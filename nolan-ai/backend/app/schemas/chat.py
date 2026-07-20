import uuid

from pydantic import BaseModel

from app.db.models import ScriptLanguage


class ChatIn(BaseModel):
    message: str
    # Optional structured context a real frontend supplies once the user has
    # picked something from a list (e.g. clicked a topic card) rather than
    # typed a raw UUID — chat text alone can't carry Topic IDs reliably.
    topic_id: uuid.UUID | None = None
    topic_ids: list[uuid.UUID] | None = None
    rejected: dict[uuid.UUID, str] | None = None
    language: ScriptLanguage | None = None


class ChatOut(BaseModel):
    intent: str
    reply: str
    data: dict | list | None = None
