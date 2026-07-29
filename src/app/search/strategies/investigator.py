from app.auth.models import User
from app.db.repositories.investigator_entities import (
    InvestigatorEntityRepository,
)
from app.search.strategies.base import SearchStrategy


class InvestigatorSearchStrategy(SearchStrategy):
    def __init__(self, repo: InvestigatorEntityRepository) -> None:
        self._repo = repo

    def search(self, query: str, user: User) -> list[dict]:
        entities = self._repo.search_by_name(query)
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
