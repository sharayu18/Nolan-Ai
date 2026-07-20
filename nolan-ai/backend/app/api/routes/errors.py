from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ErrorManagement

router = APIRouter(prefix="/errors", tags=["errors"])


@router.get("")
def list_errors(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        select(ErrorManagement).order_by(ErrorManagement.occurred_at.desc()).limit(limit)
    ).scalars()
    return list(rows)
