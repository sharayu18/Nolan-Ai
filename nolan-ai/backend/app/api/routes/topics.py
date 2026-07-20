import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import MasterTopic, TopicSource, TopicStatus
from app.schemas.topics import RejectTopicIn, RishiTopicIn, TopicOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/topics", tags=["topics"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[TopicOut])
def list_topics(status: TopicStatus | None = None, db: Session = Depends(get_db)):
    query = select(MasterTopic).order_by(MasterTopic.created_at.desc())
    if status:
        query = query.where(MasterTopic.status == status)
    return list(db.execute(query).scalars())


@router.post("", response_model=TopicOut)
def add_rishi_topic(payload: RishiTopicIn, db: Session = Depends(get_db)):
    """Rishi's own idea — added directly, no criteria filter applied."""
    topic = MasterTopic(
        **payload.model_dump(),
        source=TopicSource.rishi,
        status=TopicStatus.pending_to_pick,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.post("/{topic_id}/pick", response_model=TopicOut)
def pick_topic(topic_id: uuid.UUID, db: Session = Depends(get_db)):
    topic = db.get(MasterTopic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    topic.status = TopicStatus.picked
    db.commit()
    db.refresh(topic)
    return topic


@router.post("/{topic_id}/reject", response_model=TopicOut)
def reject_topic(topic_id: uuid.UUID, payload: RejectTopicIn, db: Session = Depends(get_db)):
    topic = db.get(MasterTopic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    topic.status = TopicStatus.rejected
    topic.reason = payload.reason
    topic.reason_notes = payload.reason_notes
    db.commit()
    db.refresh(topic)
    return topic
