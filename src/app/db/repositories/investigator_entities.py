from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import InvestigatorEntity


class InvestigatorEntityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entity: InvestigatorEntity) -> InvestigatorEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def get(self, entity_id: str) -> InvestigatorEntity | None:
        return self._session.get(InvestigatorEntity, entity_id)

    def list_all(self) -> list[InvestigatorEntity]:
        return list(self._session.scalars(select(InvestigatorEntity)))

    def search_by_name(self, query: str) -> list[InvestigatorEntity]:
        stmt = select(InvestigatorEntity).where(
            InvestigatorEntity.name.ilike(f"%{query}%")
        )
        return list(self._session.scalars(stmt))
