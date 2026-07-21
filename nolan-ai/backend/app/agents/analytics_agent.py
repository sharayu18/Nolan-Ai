"""Analytics & Feedback Agent — Tasks 1-10 from HANDOFF.md's full spec.

Anomaly math (Task 5) is deterministic code, not an LLM judgment call —
skip/share/completion thresholds are numbers, and getting them wrong
silently would be worse than an LLM being crisp about them. Claude is
only used for the one-line interpretation sentence (Reporting tone) and
the digest's "best performer" blurb.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.prompts.analytics_agent_prompt import (
    INDUSTRY_SHARE_RATE_FLOOR,
    ROLLING_BASELINE_WINDOW,
    SYSTEM_PROMPT,
    build_digest_summary_prompt,
    build_interpretation_prompt,
)
from app.db.models import (
    Analytics,
    ErrorSeverity,
    FeedbackResponse,
    MasterTopic,
    Script,
)
from app.services.anthropic_client import call_claude
from app.services.email_client import EmailNotConfiguredError, send_alert_email
from app.services.error_logger import log_error
from app.services.instagram_client import InstagramAuthError, instagram_client

logger = logging.getLogger(__name__)

AGENT_NAME = "Analytics & Feedback Agent"
FETCH_DELAY_HOURS = 48  # starting assumption per HANDOFF.md — revisit once live data exists


class AnalyticsAgentError(RuntimeError):
    """Critical failure — caller should stop and alert Rishi."""


@dataclass
class Flag:
    metric: str
    statement: str
    interpretation: str = ""
    reel_ref: str = ""


@dataclass
class DigestResult:
    week_of: str
    posted_count: int
    best_performer: str
    flags: list[Flag] = field(default_factory=list)
    pending_feedback_count: int = 0


class AnalyticsFeedbackAgent:
    def __init__(self, db: Session):
        self.db = db

    # -- Task 1 + 2: pull metrics for reels posted 48h+ ago, not yet fetched --
    def fetch_due_reels(self) -> list[Analytics]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=FETCH_DELAY_HOURS)
        due_scripts = self.db.execute(
            select(Script).where(
                Script.posted.is_(True),
                Script.posted_at.isnot(None),
                Script.posted_at <= cutoff,
                Script.instagram_media_id.isnot(None),
            )
        ).scalars()

        already_fetched_script_ids = {
            row.script_id
            for row in self.db.execute(select(Analytics.script_id)).scalars()
            if row is not None
        }

        results: list[Analytics] = []
        for script in due_scripts:
            if script.script_id in already_fetched_script_ids:
                continue
            try:
                results.append(self._fetch_and_store_one(script))
            except InstagramAuthError as exc:
                log_error(
                    self.db,
                    agent_name=AGENT_NAME,
                    action_name="Fetch reel metrics — Instagram auth",
                    severity=ErrorSeverity.critical,
                    details=str(exc),
                )
                raise AnalyticsAgentError(
                    "Instagram connection needs re-authorization — analytics paused until reconnected."
                ) from exc
            except httpx.HTTPError as exc:
                log_error(
                    self.db,
                    agent_name=AGENT_NAME,
                    action_name=f"Fetch reel metrics — Script {script.script_id}",
                    severity=ErrorSeverity.medium,
                    details=f"{exc} — will retry next scheduled run",
                )
                continue
        return results

    def _fetch_and_store_one(self, script: Script) -> Analytics:
        insights = instagram_client.fetch_media_insights(script.instagram_media_id)
        partial = False
        try:
            demographics = instagram_client.fetch_media_demographics(script.instagram_media_id)
        except httpx.HTTPError:
            demographics = {}
            partial = True

        views = insights.get("plays")
        reach = insights.get("reach")
        likes = insights.get("likes")
        shares = insights.get("shares")
        saves = insights.get("saved")
        comments = insights.get("comments")
        avg_watch_time = insights.get("avg_watch_time")
        total_watch_time = insights.get("video_view_total_time")

        completion_pct = None
        if avg_watch_time and script.duration_seconds:
            completion_pct = round(min(avg_watch_time / script.duration_seconds, 1.0) * 100, 2)

        skip_rate = round(100 - completion_pct, 2) if completion_pct is not None else None
        share_rate = round((shares / reach) * 100, 2) if shares is not None and reach else None
        like_rate = round((likes / reach) * 100, 2) if likes is not None and reach else None
        save_rate = round((saves / reach) * 100, 2) if saves is not None and reach else None

        row = Analytics(
            topic_id=script.topic_id,
            script_id=script.script_id,
            date_posted=script.posted_at,
            views=views,
            reach=reach,
            avg_watch_time_s=avg_watch_time,
            completion_pct=completion_pct,
            follows=None,
            likes=likes,
            shares=shares,
            saves=saves,
            comments=comments,
            skip_rate_pct=skip_rate,
            share_rate_pct=share_rate,
            like_rate_pct=like_rate,
            save_rate_pct=save_rate,
            age_breakdown=demographics.get("age") if demographics else None,
            gender_breakdown=demographics.get("gender") if demographics else None,
            country_breakdown=demographics.get("country") if demographics else None,
            partial_data=partial,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    # -- Task 3 + 4: baseline / category comparisons --------------------------
    def rolling_baseline(self) -> dict[str, float]:
        recent = list(
            self.db.execute(
                select(Analytics)
                .order_by(Analytics.date_posted.desc())
                .limit(ROLLING_BASELINE_WINDOW)
            ).scalars()
        )
        return _average_rates(recent)

    def category_baseline(self, topic: MasterTopic) -> dict[str, float]:
        rows = list(
            self.db.execute(
                select(Analytics)
                .join(MasterTopic, Analytics.topic_id == MasterTopic.topic_id)
                .where(MasterTopic.category == topic.category)
            ).scalars()
        )
        return _average_rates(rows)

    # -- Task 5: flag anomalies -----------------------------------------------
    def flag_anomalies(self) -> list[Flag]:
        recent = list(
            self.db.execute(select(Analytics).order_by(Analytics.date_posted.desc()).limit(3)).scalars()
        )
        if len(recent) < 3:
            return []
        recent = list(reversed(recent))  # oldest -> newest

        flags: list[Flag] = []

        skip_rates = [r.skip_rate_pct for r in recent if r.skip_rate_pct is not None]
        if len(skip_rates) == 3 and skip_rates[0] < skip_rates[1] < skip_rates[2]:
            statement = f"Skip rate: {skip_rates[0]}% -> {skip_rates[1]}% -> {skip_rates[2]}% over last 3 reels."
            flags.append(Flag(metric="skip_rate", statement=statement, interpretation=_interpret(
                "skip_rate", skip_rates, "Rising for 3 consecutive reels."
            )))

        share_rates = [r.share_rate_pct for r in recent[-2:] if r.share_rate_pct is not None]
        if len(share_rates) == 2 and all(rate < INDUSTRY_SHARE_RATE_FLOOR for rate in share_rates):
            statement = f"Share rate below {INDUSTRY_SHARE_RATE_FLOOR}% industry floor for 2 consecutive reels: {share_rates}."
            flags.append(Flag(metric="share_rate", statement=statement, interpretation=_interpret(
                "share_rate", share_rates, "Below industry floor for 2+ consecutive reels."
            )))

        for reel in recent:
            script = self.db.get(Script, reel.script_id) if reel.script_id else None
            if script and script.duration_seconds < 60 and reel.completion_pct is not None:
                if reel.completion_pct < 40:
                    statement = f"Completion rate {reel.completion_pct}% on a {script.duration_seconds}s script (under 60s)."
                    flags.append(Flag(
                        metric="completion_pct",
                        statement=statement,
                        interpretation=_interpret(
                            "completion_pct", [reel.completion_pct],
                            "Should be near-full completion at this length, per Reel 2 precedent.",
                        ),
                        reel_ref=str(reel.reel_id),
                    ))

        return flags

    # -- Task 6: ingest feedback ------------------------------------------------
    def ingest_feedback(self, payload: dict) -> FeedbackResponse:
        try:
            row = FeedbackResponse(**payload)
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except Exception as exc:  # noqa: BLE001
            self.db.rollback()
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name="Write script-validation.html submission to Feedback Responses",
                severity=ErrorSeverity.critical,
                details=str(exc),
            )
            raise AnalyticsAgentError("Failed to log feedback submission.") from exc

    # -- Task 7: weekly digest --------------------------------------------------
    def weekly_digest(self) -> DigestResult:
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        posted = list(
            self.db.execute(
                select(Analytics).where(Analytics.date_posted >= week_start)
            ).scalars()
        )
        pending_feedback = self.db.execute(
            select(FeedbackResponse).where(FeedbackResponse.reviewed.is_(False))
        ).scalars().all()

        best_performer = "None posted this week"
        if posted:
            best = max(posted, key=lambda r: (r.share_rate_pct or 0))
            topic = self.db.get(MasterTopic, best.topic_id)
            title = topic.topic_title if topic else str(best.topic_id)
            try:
                summary = call_claude(
                    SYSTEM_PROMPT,
                    [{"role": "user", "content": build_digest_summary_prompt(
                        week_start.date().isoformat(),
                        {"topic": title, "share_rate_pct": float(best.share_rate_pct or 0)},
                    )}],
                    context="analytics_agent.weekly_digest",
                ).text.strip()
            except Exception:  # noqa: BLE001 — digest generation failure is non-critical
                summary = f"{title} — share rate {best.share_rate_pct}%"
            best_performer = summary

        try:
            flags = self.flag_anomalies()
        except Exception as exc:  # noqa: BLE001
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name="Weekly digest — flag detection",
                severity=ErrorSeverity.medium,
                details=str(exc),
            )
            flags = []

        return DigestResult(
            week_of=week_start.date().isoformat(),
            posted_count=len(posted),
            best_performer=best_performer,
            flags=flags,
            pending_feedback_count=len(pending_feedback),
        )

    # -- Task 8: alert Rishi (chat + email) --------------------------------------
    def send_flag_alert(self, flag: Flag) -> str:
        message = f"⚠️ Pattern flagged — {flag.metric} — {datetime.now(timezone.utc).date().isoformat()}\n{flag.statement}\n{flag.interpretation}"
        if flag.reel_ref:
            message += f"\nFull data: reel {flag.reel_ref}"

        try:
            send_alert_email(subject=f"Nolan AI — flag: {flag.metric}", body=message)
        except EmailNotConfiguredError as exc:
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name="Send flag alert email",
                severity=ErrorSeverity.low,
                details=str(exc),
            )
        return message

    # -- Task 9: ad-hoc report ----------------------------------------------------
    def ad_hoc_report(
        self,
        *,
        topic_id: str | None = None,
        category: str | None = None,
        since: datetime | None = None,
    ) -> list[Analytics]:
        query = select(Analytics)
        if topic_id:
            query = query.where(Analytics.topic_id == topic_id)
        if category:
            query = query.join(MasterTopic, Analytics.topic_id == MasterTopic.topic_id).where(
                MasterTopic.category == category
            )
        if since:
            query = query.where(Analytics.date_posted >= since)
        return list(self.db.execute(query.order_by(Analytics.date_posted.desc())).scalars())


def _average_rates(rows: list[Analytics]) -> dict[str, float]:
    if not rows:
        return {}
    fields = ["skip_rate_pct", "share_rate_pct", "like_rate_pct", "save_rate_pct"]
    result = {}
    for f in fields:
        values = [float(getattr(r, f)) for r in rows if getattr(r, f) is not None]
        if values:
            result[f] = round(sum(values) / len(values), 2)
    return result


def _interpret(metric_name: str, values: list[float], context: str) -> str:
    try:
        return call_claude(
            SYSTEM_PROMPT,
            [{"role": "user", "content": build_interpretation_prompt(metric_name, values, context)}],
            context="analytics_agent._interpret",
        ).text.strip()
    except Exception:  # noqa: BLE001 — interpretation text is best-effort, not critical
        return context
