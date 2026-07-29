from app.auth.models import User
from app.db.repositories.case_manager_cases import (
    CaseManagerCaseRepository,
)
from app.search.strategies.base import SearchStrategy


class CaseManagerSearchStrategy(SearchStrategy):
    def __init__(self, repo: CaseManagerCaseRepository) -> None:
        self._repo = repo

    def search(self, query: str, user: User) -> list[dict]:
        cases = self._repo.list_assigned_to(user.user_id)
        return [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status.value,
            }
            for c in cases
        ]
