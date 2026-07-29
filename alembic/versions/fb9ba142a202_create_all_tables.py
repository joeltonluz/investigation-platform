"""create all tables

Revision ID: fb9ba142a202
Revises:
Create Date: 2026-07-28 22:17:50.451351

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fb9ba142a202"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    entitytype = postgresql.ENUM(
        "person",
        "company",
        "transaction",
        "document",
        name="entitytype",
    )
    casestatus = postgresql.ENUM(
        "open",
        "in_progress",
        "closed",
        name="casestatus",
    )
    entitytype.create(op.get_bind(), checkfirst=True)
    casestatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "analytics_reports",
        sa.Column(
            "id",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analytics_reports_title"), "analytics_reports", ["title"], unique=False
    )

    op.create_table(
        "case_manager_cases",
        sa.Column(
            "id",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("assigned_to", sa.String(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "open", "in_progress", "closed", name="casestatus", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_case_manager_cases_assigned_to",
        "case_manager_cases",
        ["assigned_to"],
        unique=False,
    )

    op.create_table(
        "investigator_entities",
        sa.Column(
            "id",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "type",
            postgresql.ENUM(
                "person",
                "company",
                "transaction",
                "document",
                name="entitytype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_investigator_entities_name", "investigator_entities", ["name"], unique=False
    )
    op.create_index(
        "ix_investigator_entities_type", "investigator_entities", ["type"], unique=False
    )

    op.create_table(
        "search_audit_log",
        sa.Column(
            "id",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("app", sa.String(), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_search_audit_log_app", "search_audit_log", ["app"], unique=False
    )
    op.create_index(
        "ix_search_audit_log_user_id", "search_audit_log", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_search_audit_log_user_id", table_name="search_audit_log")
    op.drop_index("ix_search_audit_log_app", table_name="search_audit_log")
    op.drop_table("search_audit_log")
    op.drop_index("ix_investigator_entities_type", table_name="investigator_entities")
    op.drop_index("ix_investigator_entities_name", table_name="investigator_entities")
    op.drop_table("investigator_entities")
    op.drop_index("ix_case_manager_cases_assigned_to", table_name="case_manager_cases")
    op.drop_table("case_manager_cases")
    op.drop_index(op.f("ix_analytics_reports_title"), table_name="analytics_reports")
    op.drop_table("analytics_reports")

    postgresql.ENUM(name="entitytype").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="casestatus").drop(op.get_bind(), checkfirst=True)
