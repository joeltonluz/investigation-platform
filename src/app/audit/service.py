from sqlalchemy.orm import Session

from app.db.models import SearchAuditLog
from app.db.repositories.search_audit_log import SearchAuditLogRepository


class AuditService:
    def __init__(self, session: Session) -> None:
        self._repo = SearchAuditLogRepository(session)

    def record_search(self, user_id: str, app: str, query: str) -> SearchAuditLog:
        entry = SearchAuditLog(user_id=user_id, app=app, query=query)
        return self._repo.add(entry)
