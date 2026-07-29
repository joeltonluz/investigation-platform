from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CaseManagerCase


class CaseManagerCaseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, case: CaseManagerCase) -> CaseManagerCase:
        self._session.add(case)
        self._session.flush()
        return case

    def get(self, case_id: str) -> CaseManagerCase | None:
        return self._session.get(CaseManagerCase, case_id)

    def list(self) -> list[CaseManagerCase]:
        return list(self._session.scalars(select(CaseManagerCase)))
