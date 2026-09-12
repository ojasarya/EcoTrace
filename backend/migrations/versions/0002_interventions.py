"""Add the circular intervention catalog.

Revision ID: 0002_interventions
Revises: 0001_initial_schema
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_interventions"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interventions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("target_source", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("estimated_cost", sa.Numeric(18, 2), nullable=False),
        sa.Column("estimated_reduction_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("feasibility", sa.String(length=30), nullable=False),
        sa.Column("urgency", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_interventions_category", "interventions", ["category"])
    op.create_index("ix_interventions_target_source", "interventions", ["target_source"])


def downgrade() -> None:
    op.drop_index("ix_interventions_target_source", table_name="interventions")
    op.drop_index("ix_interventions_category", table_name="interventions")
    op.drop_table("interventions")
