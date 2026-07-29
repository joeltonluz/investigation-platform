from app.auth.models import User
from app.search.strategies.base import SearchStrategy


class SearchService:
    def search_single(
        self, strategy: SearchStrategy, query: str, user: User
    ) -> list[dict]:
        return strategy.search(query, user)

    def search_aggregated(
        self, strategies: list[tuple[str, SearchStrategy]], query: str, user: User
    ) -> list[dict]:
        results: list[dict] = []
        for app_prefix, strategy in strategies:
            app_results = strategy.search(query, user)
            results.append({"app": app_prefix, "results": app_results})
        return results
