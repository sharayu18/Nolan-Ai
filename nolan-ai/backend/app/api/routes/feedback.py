from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.analytics_agent import AnalyticsAgentError, AnalyticsFeedbackAgent
from app.db.database import get_db
from app.schemas.feedback import FeedbackIn

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    """script-validation.html posts here on submit — logged immediately, no wait."""
    agent = AnalyticsFeedbackAgent(db)
    try:
        row = agent.ingest_feedback(payload.model_dump())
    except AnalyticsAgentError as exc:
        raise HTTPException(500, str(exc)) from exc
    return {"response_id": row.response_id, "submitted_at": row.submitted_at}
