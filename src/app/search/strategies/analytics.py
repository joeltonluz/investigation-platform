from app.auth.models import User
from app.db.repositories.analytics_reports import AnalyticsReportRepository
from app.search.strategies.base import SearchStrategy


class AnalyticsSearchStrategy(SearchStrategy):
    def __init__(self, repo: AnalyticsReportRepository) -> None:
        self._repo = repo

    def search(self, query: str, user: User) -> list[dict]:
        reports = self._repo.search_by_content(query)
        return [
            {
                "title": r.title,
                "summary": r.content[:200],
            }
            for r in reports
        ]
