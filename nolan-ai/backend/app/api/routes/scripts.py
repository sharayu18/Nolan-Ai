import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.script_agent import ScriptAgentError, ScriptGenerationAgent
from app.db.database import get_db
from app.db.models import MasterTopic, Script
from app.schemas.scripts import GenerateScriptIn, MarkPostedIn, ScriptOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/scripts", tags=["scripts"], dependencies=[Depends(get_current_user)])


@router.post("/generate", response_model=ScriptOut)
def generate_script(payload: GenerateScriptIn, db: Session = Depends(get_db)):
    topic = db.get(MasterTopic, payload.topic_id)
    if not topic:
        raise HTTPException(
            404,
            "I don't have this topic on record — please confirm the Topic ID "
            "or paste the topic name and description.",
        )

    agent = ScriptGenerationAgent(db)
    try:
        return agent.generate(topic, payload.language)
    except ScriptAgentError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/{script_id}", response_model=ScriptOut)
def get_script(script_id: uuid.UUID, db: Session = Depends(get_db)):
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(404, "Script not found")
    return script


@router.post("/{script_id}/posted", response_model=ScriptOut)
def mark_posted(script_id: uuid.UUID, payload: MarkPostedIn, db: Session = Depends(get_db)):
    """Marks a script Posted — starts the Analytics Agent's 48h fetch clock."""
    script = db.get(Script, script_id)
    if not script:
        raise HTTPException(404, "Script not found")
    script.posted = True
    script.posted_at = payload.posted_at or datetime.now(timezone.utc)
    script.instagram_media_id = payload.instagram_media_id
    db.commit()
    db.refresh(script)
    return script
