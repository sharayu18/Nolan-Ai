import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.models import ScriptComplexity, ScriptLanguage


class GenerateScriptIn(BaseModel):
    topic_id: uuid.UUID
    language: ScriptLanguage


class ScriptOut(BaseModel):
    script_id: uuid.UUID
    topic_id: uuid.UUID
    topic_title: str
    language: ScriptLanguage
    complexity: ScriptComplexity
    duration_seconds: int
    audio_script: str
    video_script: str
    hook_1: str
    hook_2: str
    hook_3: str
    caption_1: str
    caption_2: str
    caption_3: str
    hashtags: str
    text_overlay_start: str
    text_overlay_mid: str
    audio_suggestion: str
    posted: bool
    date_generated: datetime

    model_config = {"from_attributes": True}


class MarkPostedIn(BaseModel):
    instagram_media_id: str
    posted_at: datetime | None = None
