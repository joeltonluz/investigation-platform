from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.permissions import CLIENT_TO_APP
from app.db.repositories.analytics_reports import AnalyticsReportRepository
from app.db.repositories.case_manager_cases import CaseManagerCaseRepository
from app.db.repositories.investigator_entities import (
    InvestigatorEntityRepository,
)
from app.db.session import get_db
from app.search.service import SearchService
from app.search.strategies.analytics import AnalyticsSearchStrategy
from app.search.strategies.case_manager import CaseManagerSearchStrategy
from app.search.strategies.investigator import InvestigatorSearchStrategy

router = APIRouter(tags=["search"])

APP_STRATEGIES = {
    "analytics": AnalyticsSearchStrategy,
    "investigator": InvestigatorSearchStrategy,
    "case-manager": CaseManagerSearchStrategy,
}


def _make_strategy(app_prefix: str, db: Session):
    cls = APP_STRATEGIES[app_prefix]
    repo_map = {
        "analytics": AnalyticsReportRepository(db),
        "investigator": InvestigatorEntityRepository(db),
        "case-manager": CaseManagerCaseRepository(db),
    }
    return cls(repo_map[app_prefix])


def _get_search_apps(user: User) -> list[str]:
    return [app for app in APP_STRATEGIES if f"{app}:search" in user.permissions]


@router.get("/api/v1/search")
async def search(
    q: str = Query(min_length=1),
    mode: str = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if mode == "aggregated":
        apps = _get_search_apps(user)
        if not apps:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        service = SearchService()
        strategies = [(app, _make_strategy(app, db)) for app in apps]
        results = service.search_aggregated(strategies, q, user)
        audit = AuditService(db)
        for app_prefix, _ in strategies:
            audit.record_search(user_id=user.user_id, app=app_prefix, query=q)
        return results

    origin_app = CLIENT_TO_APP.get(user.app_client_id)
    if origin_app is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if f"{origin_app}:search" not in user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    service = SearchService()
    strategy = _make_strategy(origin_app, db)
    results = service.search_single(strategy, q, user)
    AuditService(db).record_search(user_id=user.user_id, app=origin_app, query=q)
    return {"app": origin_app, "results": results}
