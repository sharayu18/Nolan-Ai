"""Search Engine Agent — Tasks 1-8 from search-agent-prompt.md.

Rotation (Task 1), sub-area search (Task 2), the criteria filter (Task 3),
ranking (Task 4), top-15 selection with Completed/Rejected exclusion
(Task 5), sharing (Task 6) and outcome writes (Task 7) are all here.
Error handling (Task 8) routes through app.services.error_logger.
"""
from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

import anthropic
from app.agents.prompts.search_agent_prompt import (
    CATEGORY_METADATA,
    CATEGORY_ROTATION_ORDER,
    MAX_SEARCHES_PER_RUN,
    SYSTEM_PROMPT,
    TOPICS_PER_RUN,
    build_criteria_filter_prompt,
    build_ranking_prompt,
    build_search_task_prompt,
)
from app.db.models import (
    CriteriaFilterRule,
    ErrorSeverity,
    MasterTopic,
    TopicCategory,
    TopicSource,
    TopicStatus,
)
from app.services.anthropic_client import call_claude
from app.services.error_logger import log_error

logger = logging.getLogger(__name__)

AGENT_NAME = "Search Engine Agent"


class SearchAgentError(RuntimeError):
    """Critical failure — caller should stop and alert Rishi."""


class SearchEngineAgent:
    def __init__(self, db: Session):
        self.db = db

    # -- Task 1: rotation --------------------------------------------------
    def determine_next_rotation(self) -> tuple[TopicCategory, str]:
        last_agent_topic = self.db.execute(
            select(MasterTopic)
            .where(MasterTopic.source == TopicSource.agent)
            .order_by(MasterTopic.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

        if last_agent_topic is None:
            category = CATEGORY_ROTATION_ORDER[0]
            sub_area = CATEGORY_METADATA[category]["sub_area_rotation"][0]
            return category, sub_area

        last_category = last_agent_topic.category
        last_sub_area = last_agent_topic.sub_area
        rotation = CATEGORY_METADATA[last_category]["sub_area_rotation"]

        try:
            idx = rotation.index(last_sub_area)
        except ValueError:
            idx = -1  # unknown sub-area on record -> restart this category's rotation

        if idx + 1 < len(rotation):
            return last_category, rotation[idx + 1]

        # sub-area rotation exhausted -> advance to next category
        cat_idx = CATEGORY_ROTATION_ORDER.index(last_category)
        next_category = CATEGORY_ROTATION_ORDER[(cat_idx + 1) % len(CATEGORY_ROTATION_ORDER)]
        next_sub_area = CATEGORY_METADATA[next_category]["sub_area_rotation"][0]
        return next_category, next_sub_area

    # -- Task 2: search ------------------------------------------------------
    def search_subarea(self, category: TopicCategory, sub_area: str) -> list[dict]:
        prompt = build_search_task_prompt(category, sub_area)
        try:
            response = call_claude(
                SYSTEM_PROMPT,
                [{"role": "user", "content": prompt}],
                use_web_search=True,
                max_web_searches=MAX_SEARCHES_PER_RUN,
            )
        except anthropic.APIError as exc:
            raise SearchAgentError(f"Search returns zero results — API call failed: {exc}") from exc

        topics = _parse_json_array(response.text)
        if not topics:
            raise SearchAgentError(f"Search returned zero results for {category.value}/{sub_area}")
        return topics

    # -- Task 3: criteria filter ---------------------------------------------
    def apply_criteria_filter(self, topics: list[dict]) -> list[dict]:
        rules = [
            r.rule_text
            for r in self.db.execute(
                select(CriteriaFilterRule).where(CriteriaFilterRule.is_active.is_(True))
            ).scalars()
        ]
        if not rules:
            return topics  # no rules configured -> nothing to filter against

        prompt = build_criteria_filter_prompt(rules, topics)
        response = call_claude(SYSTEM_PROMPT, [{"role": "user", "content": prompt}])
        verdicts = {v["topic_title"]: v["passes"] for v in _parse_json_array(response.text)}

        return [t for t in topics if verdicts.get(t["topic_title"], False)]

    # -- Task 4: rank ---------------------------------------------------------
    def rank_topics(self, category: TopicCategory, sub_area: str, topics: list[dict]) -> list[dict]:
        ranking = CATEGORY_METADATA[category]["ranking"]
        if ranking is not None:
            # Categories 1-2: explicit sub-area priority order — but within a
            # single run all topics share one sub-area, so fall through to
            # the order Claude produced them in (already sub-area-scoped).
            return topics

        prompt = build_ranking_prompt(category, sub_area, topics)
        response = call_claude(SYSTEM_PROMPT, [{"role": "user", "content": prompt}])
        order = _parse_json_array(response.text)
        by_title = {t["topic_title"]: t for t in topics}
        ranked = [by_title[title] for title in order if title in by_title]
        # append anything Claude dropped from its ranking, preserving original order
        ranked += [t for t in topics if t["topic_title"] not in {r["topic_title"] for r in ranked}]
        return ranked

    # -- Task 5: select top 15, excluding Completed/Rejected -----------------
    def select_top(self, topics: list[dict]) -> list[dict]:
        existing_titles = {
            t.lower()
            for t in self.db.execute(
                select(MasterTopic.topic_title).where(
                    MasterTopic.status.in_([TopicStatus.completed, TopicStatus.rejected])
                )
            ).scalars()
        }
        available = [t for t in topics if t["topic_title"].lower() not in existing_titles]
        return available[:TOPICS_PER_RUN]

    # -- Full weekly run (Monday 10am cron, Tasks 1-5 + write) ---------------
    def run_weekly_search(self) -> list[MasterTopic]:
        category, sub_area = self.determine_next_rotation()
        try:
            raw_topics = self.search_subarea(category, sub_area)
            passing = self.apply_criteria_filter(raw_topics)
            ranked = self.rank_topics(category, sub_area, passing)
            selected = self.select_top(ranked)
        except SearchAgentError as exc:
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name=f"Weekly search run — {category.value}/{sub_area}",
                severity=ErrorSeverity.critical,
                details=str(exc),
            )
            raise

        if len(selected) < TOPICS_PER_RUN:
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name=f"Weekly search run — {category.value}/{sub_area}",
                severity=ErrorSeverity.low,
                details=f"Only {len(selected)} of {TOPICS_PER_RUN} topics passed/available.",
            )

        rows = []
        for topic in selected:
            row = MasterTopic(
                topic_title=topic["topic_title"],
                category=category,
                sub_area=sub_area,
                description=topic.get("description", ""),
                pillar=topic.get("pillar"),
                source=TopicSource.agent,
                status=TopicStatus.pending_to_pick,
            )
            self.db.add(row)
            rows.append(row)

        try:
            self.db.commit()
        except Exception as exc:  # noqa: BLE001 — write failure is a critical, stop-and-alert case
            self.db.rollback()
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name="Write new topics to Master Topics",
                severity=ErrorSeverity.critical,
                details=str(exc),
            )
            raise SearchAgentError(
                "I ran into an issue. Please check Error Management or try again shortly."
            ) from exc

        for row in rows:
            self.db.refresh(row)
        return rows

    # -- Task 6: "share this week's topics" (on-demand, no re-search) --------
    def share_this_weeks_topics(self) -> list[MasterTopic]:
        return list(
            self.db.execute(
                select(MasterTopic)
                .where(MasterTopic.status == TopicStatus.pending_to_pick)
                .order_by(MasterTopic.created_at.desc())
            ).scalars()
        )

    # -- Task 7: record Rishi's picks/rejections ------------------------------
    def record_outcomes(
        self,
        picked_ids: list[str] | None = None,
        rejected: dict[str, str] | None = None,  # topic_id -> reason
    ) -> None:
        picked_ids = picked_ids or []
        rejected = rejected or {}

        try:
            for topic_id in picked_ids:
                topic = self.db.get(MasterTopic, topic_id)
                if topic:
                    topic.status = TopicStatus.picked

            for topic_id, reason in rejected.items():
                topic = self.db.get(MasterTopic, topic_id)
                if topic:
                    topic.status = TopicStatus.rejected
                    topic.reason = reason

            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            self.db.rollback()
            log_error(
                self.db,
                agent_name=AGENT_NAME,
                action_name="Write Rishi's picks/rejections to Master Topics",
                severity=ErrorSeverity.critical,
                details=str(exc),
            )
            raise SearchAgentError(
                "I ran into an issue. Please check Error Management or try again shortly."
            ) from exc


def _parse_json_array(text: str) -> list[dict]:
    text = text.strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
