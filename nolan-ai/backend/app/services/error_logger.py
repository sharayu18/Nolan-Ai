"""Writes to the Error Management table.

Every agent's Error Handling section in the design docs specifies the
same log format: {ID} | {Action Name} | {Date Time} | {Error Details}.
The ID and Date Time are the row's own primary key / occurred_at —
callers only need to supply agent_name, action_name, severity, details.
"""
from sqlalchemy.orm import Session

from app.db.models import ErrorManagement, ErrorSeverity


def log_error(
    db: Session,
    *,
    agent_name: str,
    action_name: str,
    severity: ErrorSeverity,
    details: str,
) -> ErrorManagement:
    row = ErrorManagement(
        agent_name=agent_name,
        action_name=action_name,
        severity=severity,
        error_details=details,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
