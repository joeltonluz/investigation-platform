from abc import ABC, abstractmethod

from app.auth.models import User


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str, user: User) -> list[dict]: ...
