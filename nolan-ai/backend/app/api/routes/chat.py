"""Chat entry point — dispatches free text to whichever agent's Trigger
Conditions match, mirroring the phrase-triggered design in the original
agent prompt docs (e.g. Rishi typing "Generate script for Topic ID X").

Raw UUID Topic/Script IDs are unwieldy to type in chat, so the frontend
is expected to pass structured `topic_id` / `topic_ids` / `rejected`
alongside the message once the user has picked something from a list
(e.g. clicking a topic card) — see ChatIn's docstring-equivalent comment
in schemas/chat.py. Matching is keyword-based, same literal style as the
source docs' trigger phrases, not a general-purpose NLU layer.
"""
import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.analytics_agent import AnalyticsAgentError, AnalyticsFeedbackAgent
from app.agents.script_agent import ScriptAgentError, ScriptGenerationAgent
from app.agents.search_agent import SearchAgentError, SearchEngineAgent
from app.db.database import get_db
from app.db.models import MasterTopic, ScriptLanguage
from app.schemas.chat import ChatIn, ChatOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])

_SHARE_TOPICS_RE = re.compile(r"share.*this week|this week.*topics", re.I)
_GENERATE_SCRIPT_RE = re.compile(r"generate script|script banao", re.I)
_CHANNEL_STATUS_RE = re.compile(r"how is my channel|channel doing", re.I)
_REEL_PERFORMANCE_RE = re.compile(r"performance|how (did|is).*(reel|doing)", re.I)
_OLD_DATA_RE = re.compile(r"old (data|topics)|past topics", re.I)


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    message = payload.message.strip()

    if payload.topic_ids or payload.rejected:
        agent = SearchEngineAgent(db)
        try:
            agent.record_outcomes(
                picked_ids=[str(t) for t in (payload.topic_ids or [])],
                rejected={str(k): v for k, v in (payload.rejected or {}).items()},
            )
        except SearchAgentError as exc:
            return ChatOut(intent="record_outcomes", reply=str(exc))
        return ChatOut(intent="record_outcomes", reply="Got it — Master Topics updated.")

    if _SHARE_TOPICS_RE.search(message):
        agent = SearchEngineAgent(db)
        topics = agent.share_this_weeks_topics()
        if not topics:
            return ChatOut(intent="share_topics", reply="No pending topics right now.", data=[])
        lines = [
            f"ID: {t.topic_id}\nTopic: {t.topic_title}\nCategory: {t.category.value} — {t.sub_area}\nDescription: {t.description}"
            for t in topics
        ]
        return ChatOut(
            intent="share_topics",
            reply="\n\n".join(lines),
            data=[{"topic_id": str(t.topic_id), "topic_title": t.topic_title} for t in topics],
        )

    if _GENERATE_SCRIPT_RE.search(message):
        if not payload.topic_id:
            return ChatOut(
                intent="generate_script",
                reply="I don't have this topic on record — please confirm the Topic ID or paste the topic name and description.",
            )
        topic = db.get(MasterTopic, payload.topic_id)
        if not topic:
            return ChatOut(
                intent="generate_script",
                reply="I don't have this topic on record — please confirm the Topic ID or paste the topic name and description.",
            )
        script_agent = ScriptGenerationAgent(db)
        try:
            script = script_agent.generate(topic, payload.language or ScriptLanguage.hinglish)
        except ScriptAgentError as exc:
            return ChatOut(intent="generate_script", reply=str(exc))
        return ChatOut(
            intent="generate_script",
            reply=f"Script ready — {script.duration_seconds}s, {script.complexity.value}.",
            data={"script_id": str(script.script_id)},
        )

    if _CHANNEL_STATUS_RE.search(message):
        analytics_agent = AnalyticsFeedbackAgent(db)
        digest = analytics_agent.weekly_digest()
        reply = (
            f"Week of {digest.week_of} — {digest.posted_count} reels posted.\n"
            f"Best performer: {digest.best_performer}\n"
            f"Flags: {', '.join(f.statement for f in digest.flags) or 'None'}\n"
            f"Pending feedback: {digest.pending_feedback_count}"
        )
        return ChatOut(intent="channel_status", reply=reply)

    if _REEL_PERFORMANCE_RE.search(message):
        if not payload.topic_id:
            return ChatOut(
                intent="reel_performance",
                reply="Which reel? Please pass its Topic ID.",
            )
        analytics_agent = AnalyticsFeedbackAgent(db)
        try:
            rows = analytics_agent.ad_hoc_report(topic_id=str(payload.topic_id))
        except AnalyticsAgentError as exc:
            return ChatOut(intent="reel_performance", reply=str(exc))
        if not rows:
            return ChatOut(
                intent="reel_performance",
                reply=f"Data unavailable for {payload.topic_id} — API may not have synced yet.",
            )
        r = rows[0]
        reply = (
            f"Views: {r.views} | Reach: {r.reach} | Completion: {r.completion_pct}% | "
            f"Skip: {r.skip_rate_pct}% | Share: {r.share_rate_pct}% | Save: {r.save_rate_pct}%"
        )
        return ChatOut(intent="reel_performance", reply=reply)

    if _OLD_DATA_RE.search(message):
        return ChatOut(
            intent="old_data",
            reply="Please refer to Master Topics — filter by Status to find what you need.",
        )

    return ChatOut(
        intent="unknown",
        reply="I don't have enough data to act on that. Try: \"share this week's topics\", "
        "\"generate script for Topic ID [X]\", or \"how is my channel doing\".",
    )
