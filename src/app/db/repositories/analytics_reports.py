from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalyticsReport


class AnalyticsReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, report: AnalyticsReport) -> AnalyticsReport:
        self._session.add(report)
        self._session.flush()
        return report

    def get(self, report_id: str) -> AnalyticsReport | None:
        return self._session.get(AnalyticsReport, report_id)

    def list_all(self) -> list[AnalyticsReport]:
        return list(self._session.scalars(select(AnalyticsReport)))

    def search_by_content(self, query: str) -> list[AnalyticsReport]:
        stmt = select(AnalyticsReport).where(
            AnalyticsReport.content.ilike(f"%{query}%")
        )
        return list(self._session.scalars(stmt))
