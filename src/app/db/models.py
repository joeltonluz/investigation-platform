import enum
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntityType(enum.Enum):
    person = "person"
    company = "company"
    transaction = "transaction"
    document = "document"


class CaseStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class AnalyticsReport(Base):
    __tablename__ = "analytics_reports"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class InvestigatorEntity(Base):
    __tablename__ = "investigator_entities"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, create_constraint=False, create_type=False),
    )
    name: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_investigator_entities_type", "type"),
        Index("ix_investigator_entities_name", "name"),
    )


class CaseManagerCase(Base):
    __tablename__ = "case_manager_cases"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    title: Mapped[str] = mapped_column(String)
    assigned_to: Mapped[str] = mapped_column(String)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, create_constraint=False, create_type=False),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_case_manager_cases_assigned_to", "assigned_to"),)


class SearchAuditLog(Base):
    __tablename__ = "search_audit_log"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[str] = mapped_column(String)
    app: Mapped[str] = mapped_column(String)
    query: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_search_audit_log_user_id", "user_id"),
        Index("ix_search_audit_log_app", "app"),
    )
