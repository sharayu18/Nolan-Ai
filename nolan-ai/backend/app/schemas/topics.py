import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.models import ContentPillar, TopicCategory, TopicRejectReason, TopicSource, TopicStatus


class TopicOut(BaseModel):
    topic_id: uuid.UUID
    topic_title: str
    category: TopicCategory
    sub_area: str
    description: str
    pillar: ContentPillar | None
    source: TopicSource
    status: TopicStatus
    reason: TopicRejectReason | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RishiTopicIn(BaseModel):
    topic_title: str
    category: TopicCategory
    sub_area: str
    description: str
    pillar: ContentPillar | None = None


class RejectTopicIn(BaseModel):
    reason: TopicRejectReason
    reason_notes: str | None = None
