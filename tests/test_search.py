import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.dependencies import get_public_key
from app.db.models import (
    AnalyticsReport,
    CaseManagerCase,
    CaseStatus,
    EntityType,
    InvestigatorEntity,
)
from app.db.repositories.search_audit_log import SearchAuditLogRepository
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def app(session):
    application = create_app()
    application.dependency_overrides[get_db] = lambda: session
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def analytics_data(session):
    session.add_all(
        [
            AnalyticsReport(title="Q3 Report", content="quarterly earnings report"),
            AnalyticsReport(title="Q4 Report", content="something else entirely"),
        ]
    )
    session.flush()
    for r in session.query(AnalyticsReport).all():
        session.refresh(r)


@pytest.fixture
def investigator_data(session):
    session.add_all(
        [
            InvestigatorEntity(
                type=EntityType.company,
                name="ACME Corp",
                data={"sector": "tech"},
            ),
            InvestigatorEntity(
                type=EntityType.person,
                name="John Doe",
                data={"role": "employee"},
            ),
        ]
    )
    session.flush()
    for e in session.query(InvestigatorEntity).all():
        session.refresh(e)


@pytest.fixture
def case_manager_data(session):
    session.add_all(
        [
            CaseManagerCase(
                title="Case Alpha",
                assigned_to="user-123",
                status=CaseStatus.open,
            ),
            CaseManagerCase(
                title="Case Beta",
                assigned_to="other-user",
                status=CaseStatus.in_progress,
            ),
        ]
    )
    session.flush()
    for c in session.query(CaseManagerCase).all():
        session.refresh(c)


class TestSearchEndpoint:
    async def test_analytics_user_gets_only_analytics_data(
        self, app, session, rsa_keypair, token_factory, analytics_data
    ):
        _, public_key_pem = rsa_keypair
        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="user-123",
            azp="analytics-api",
            resource_access={"analytics-api": {"roles": ["search"]}},
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/search?q=quarterly",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["app"] == "analytics"
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Q3 Report"

    async def test_investigator_user_gets_only_investigator_data(
        self, app, session, rsa_keypair, token_factory, investigator_data
    ):
        _, public_key_pem = rsa_keypair
        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="user-123",
            azp="investigator-api",
            resource_access={"investigator-api": {"roles": ["search"]}},
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/search?q=ACME",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["app"] == "investigator"
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "ACME Corp"

    async def test_user_with_both_permissions_gets_aggregated_results(
        self,
        app,
        session,
        rsa_keypair,
        token_factory,
        analytics_data,
        investigator_data,
    ):
        _, public_key_pem = rsa_keypair
        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="user-123",
            azp="analytics-api",
            resource_access={
                "analytics-api": {"roles": ["search"]},
                "investigator-api": {"roles": ["search"]},
            },
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/search?q=report",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        apps = {item["app"] for item in data}
        assert "analytics" in apps
        assert "investigator" in apps

    async def test_user_without_permission_returns_403(
        self,
        app,
        session,
        rsa_keypair,
        token_factory,
    ):
        _, public_key_pem = rsa_keypair
        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="user-123",
            azp="analytics-api",
            resource_access={"analytics-api": {"roles": ["export"]}},
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/search?q=test",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 403

    async def test_search_is_recorded_in_audit_log(
        self,
        app,
        session,
        rsa_keypair,
        token_factory,
        analytics_data,
    ):
        _, public_key_pem = rsa_keypair
        app.dependency_overrides[get_public_key] = lambda: public_key_pem

        token = token_factory(
            sub="user-123",
            azp="analytics-api",
            resource_access={"analytics-api": {"roles": ["search"]}},
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/search?q=quarterly",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200

        repo = SearchAuditLogRepository(session)
        entries = repo.list()
        assert len(entries) >= 1
        match = any(
            e.user_id == "user-123" and e.app == "analytics" and "quarterly" in e.query
            for e in entries
        )
        assert match
