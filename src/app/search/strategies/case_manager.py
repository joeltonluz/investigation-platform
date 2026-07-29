from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.db.models import CaseManagerCase
from app.search.strategies.base import SearchStrategy


class CaseManagerSearchStrategy(SearchStrategy):
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, query: str, user: User) -> list[dict]:
        stmt = select(CaseManagerCase).where(
            CaseManagerCase.assigned_to == user.user_id
        )
        cases = self._session.scalars(stmt).all()
        return [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status.value,
            }
            for c in cases
        ]
