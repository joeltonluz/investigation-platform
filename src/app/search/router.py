from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.auth.dependencies import get_current_user
from app.auth.models import User
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


def _get_user_search_apps(user: User) -> list[str]:
    apps: list[str] = []
    for app_prefix in APP_STRATEGIES:
        if f"{app_prefix}:search" in user.permissions:
            apps.append(app_prefix)
    return apps


@router.get("/api/v1/search")
async def search(
    q: str = Query(min_length=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_apps = _get_user_search_apps(user)

    if not user_apps:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    service = SearchService()
    audit = AuditService(db)

    if len(user_apps) == 1:
        app_prefix = user_apps[0]
        strategy = APP_STRATEGIES[app_prefix](db)
        results = service.search_single(strategy, q, user)
        audit.record_search(user_id=user.user_id, app=app_prefix, query=q)
        return {"app": app_prefix, "results": results}

    strategies = [
        (app_prefix, APP_STRATEGIES[app_prefix](db)) for app_prefix in user_apps
    ]
    results = service.search_aggregated(strategies, q, user)
    for app_prefix, _ in strategies:
        audit.record_search(user_id=user.user_id, app=app_prefix, query=q)
    return results
