import uuid

from pydantic import BaseModel

from app.db.models import (
    FeedbackQ1,
    FeedbackQ2,
    FeedbackQ3,
    FeedbackQ4,
    FeedbackQ5,
    FeedbackQ6,
    FeedbackQ7,
)


class FeedbackIn(BaseModel):
    topic_id: uuid.UUID | None = None
    script_id: uuid.UUID | None = None
    q1_sounds_like_rishi: FeedbackQ1 | None = None
    q2_formality: FeedbackQ2 | None = None
    q3_hinglish_ratio: FeedbackQ3 | None = None
    q4_length: FeedbackQ4 | None = None
    q5_format: FeedbackQ5 | None = None
    q6_camera: FeedbackQ6 | None = None
    camera_notes: str | None = None
    q7_supporting_outputs: FeedbackQ7 | None = None
    extra_notes: str | None = None
