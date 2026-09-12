"""Add persisted roadmap action tracking.

Revision ID: 0003_roadmap_actions
Revises: 0002_interventions
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_roadmap_actions"
down_revision: Union[str, None] = "0002_interventions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roadmap_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("factory_id", sa.Integer(), nullable=False),
        sa.Column("calculation_id", sa.Integer(), nullable=False),
        sa.Column("intervention_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="planned"),
        sa.Column("planned_start_date", sa.Date(), nullable=True),
        sa.Column("owner", sa.String(length=150), nullable=True),
        sa.Column("actual_cost", sa.Numeric(18, 2), nullable=True),
        sa.Column("actual_reduction_kg_co2e", sa.Numeric(18, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["factory_id"], ["factories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["calculation_id"], ["emission_calculations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["intervention_id"], ["interventions.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_roadmap_actions_factory_id", "roadmap_actions", ["factory_id"])
    op.create_index("ix_roadmap_actions_calculation_id", "roadmap_actions", ["calculation_id"])
    op.create_index("ix_roadmap_actions_intervention_id", "roadmap_actions", ["intervention_id"])


def downgrade() -> None:
    op.drop_index("ix_roadmap_actions_intervention_id", table_name="roadmap_actions")
    op.drop_index("ix_roadmap_actions_calculation_id", table_name="roadmap_actions")
    op.drop_index("ix_roadmap_actions_factory_id", table_name="roadmap_actions")
    op.drop_table("roadmap_actions")
