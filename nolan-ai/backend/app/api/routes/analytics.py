import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.analytics_agent import AnalyticsAgentError, AnalyticsFeedbackAgent
from app.db.database import get_db
from app.db.models import TopicCategory
from app.services.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)])


@router.post("/fetch-due")
def fetch_due_reels(db: Session = Depends(get_db)):
    """Task 1-2 — normally run by the scheduler, exposed here for manual trigger/testing."""
    agent = AnalyticsFeedbackAgent(db)
    try:
        rows = agent.fetch_due_reels()
    except AnalyticsAgentError as exc:
        raise HTTPException(503, str(exc)) from exc
    return {"fetched": len(rows), "reel_ids": [r.reel_id for r in rows]}


@router.get("/digest")
def weekly_digest(db: Session = Depends(get_db)):
    agent = AnalyticsFeedbackAgent(db)
    digest = agent.weekly_digest()
    return {
        "week_of": digest.week_of,
        "posted_count": digest.posted_count,
        "best_performer": digest.best_performer,
        "flags": [f.statement + " " + f.interpretation for f in digest.flags] or ["None"],
        "pending_feedback_count": digest.pending_feedback_count,
    }


@router.get("/report")
def ad_hoc_report(
    topic_id: uuid.UUID | None = None,
    category: TopicCategory | None = None,
    since: datetime | None = None,
    db: Session = Depends(get_db),
):
    agent = AnalyticsFeedbackAgent(db)
    rows = agent.ad_hoc_report(
        topic_id=str(topic_id) if topic_id else None,
        category=category.value if category else None,
        since=since,
    )
    if not rows:
        return {"message": "Data unavailable — API may not have synced yet, or nothing matches this query."}
    return rows
