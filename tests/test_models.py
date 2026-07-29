"""Test model round-trips against real Postgres."""

import pytest
from sqlalchemy import text

from app.db.models import (
    AnalyticsReport,
    CaseManagerCase,
    CaseStatus,
    EntityType,
    InvestigatorEntity,
    SearchAuditLog,
)
from app.db.repositories.analytics_reports import AnalyticsReportRepository
from app.db.repositories.case_manager_cases import CaseManagerCaseRepository
from app.db.repositories.investigator_entities import (
    InvestigatorEntityRepository,
)
from app.db.repositories.search_audit_log import SearchAuditLogRepository


def test_analytics_report_round_trip(session):
    repo = AnalyticsReportRepository(session)
    report = AnalyticsReport(title="Test Report", content="Test content")
    saved = repo.add(report)
    assert saved.id is not None
    assert saved.created_at is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.title == "Test Report"


def test_investigator_entity_round_trip(session):
    repo = InvestigatorEntityRepository(session)
    entity = InvestigatorEntity(
        type=EntityType.person,
        name="John Doe",
        data={"age": 35, "city": "São Paulo"},
    )
    saved = repo.add(entity)
    assert saved.id is not None
    assert saved.created_at is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.name == "John Doe"
    assert fetched.data == {"age": 35, "city": "São Paulo"}
    assert fetched.type == EntityType.person


def test_investigator_entity_jsonb_round_trip(session):
    repo = InvestigatorEntityRepository(session)
    entity = InvestigatorEntity(
        type=EntityType.company,
        name="ACME Corp",
        data={"cnpj": "12.345.678/0001-90", "employees": 150},
    )
    saved = repo.add(entity)
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.data["cnpj"] == "12.345.678/0001-90"
    assert fetched.data["employees"] == 150


def test_investigator_entity_invalid_type_raises(session):
    with pytest.raises(Exception):
        session.execute(
            text(
                "INSERT INTO investigator_entities (type, name, data) "
                "VALUES ('invalid_type', 'Bad', '{}'::jsonb)"
            )
        )


def test_case_manager_case_round_trip(session):
    repo = CaseManagerCaseRepository(session)
    case = CaseManagerCase(
        title="Investigation #1",
        assigned_to="agent-001",
        status=CaseStatus.open,
    )
    saved = repo.add(case)
    assert saved.id is not None
    assert saved.created_at is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.title == "Investigation #1"
    assert fetched.assigned_to == "agent-001"
    assert fetched.status == CaseStatus.open


def test_search_audit_log_round_trip(session):
    repo = SearchAuditLogRepository(session)
    entry = SearchAuditLog(
        user_id="user-123",
        app="analytics",
        query="fraud report",
    )
    saved = repo.add(entry)
    assert saved.id is not None
    assert saved.timestamp is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.user_id == "user-123"
    assert fetched.app == "analytics"
    assert fetched.query == "fraud report"
