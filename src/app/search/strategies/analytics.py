from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.db.models import AnalyticsReport
from app.search.strategies.base import SearchStrategy


class AnalyticsSearchStrategy(SearchStrategy):
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, query: str, user: User) -> list[dict]:
        stmt = select(AnalyticsReport).where(
            AnalyticsReport.content.ilike(f"%{query}%")
        )
        reports = self._session.scalars(stmt).all()
        return [
            {
                "title": r.title,
                "summary": r.content[:200],
            }
            for r in reports
        ]
