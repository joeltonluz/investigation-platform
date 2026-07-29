from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.db.models import InvestigatorEntity
from app.search.strategies.base import SearchStrategy


class InvestigatorSearchStrategy(SearchStrategy):
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, query: str, user: User) -> list[dict]:
        stmt = select(InvestigatorEntity).where(
            InvestigatorEntity.name.ilike(f"%{query}%")
        )
        entities = self._session.scalars(stmt).all()
        return [
            {
                "id": e.id,
                "type": e.type.value,
                "name": e.name,
                "data": e.data,
                "created_at": e.created_at.isoformat(),
            }
            for e in entities
        ]
