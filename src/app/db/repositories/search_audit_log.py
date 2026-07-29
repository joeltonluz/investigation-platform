from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SearchAuditLog


class SearchAuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: SearchAuditLog) -> SearchAuditLog:
        self._session.add(entry)
        self._session.flush()
        return entry

    def get(self, entry_id: str) -> SearchAuditLog | None:
        return self._session.get(SearchAuditLog, entry_id)

    def list(self) -> list[SearchAuditLog]:
        return list(self._session.scalars(select(SearchAuditLog)))
