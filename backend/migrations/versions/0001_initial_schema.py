"""Create the initial factory activity and emissions schema.

Revision ID: 0001_initial_schema
Revises:
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "factories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("industry_type", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("production_unit", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "emission_factors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=150), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("kg_co2e_per_unit", sa.Numeric(18, 8), nullable=False),
        sa.Column("geography", sa.String(length=100), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("category", "source", "unit", "version", name="uq_emission_factor_identity"),
    )
    op.create_index("ix_emission_factors_category", "emission_factors", ["category"])
    op.create_table(
        "reporting_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("factory_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("production_quantity", sa.Float(), nullable=False),
        sa.Column("production_unit", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["factory_id"], ["factories.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_reporting_periods_factory_id", "reporting_periods", ["factory_id"])

    activity_tables = [
        ("production_activities", [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reporting_period_id", sa.Integer(), nullable=False),
            sa.Column("process_name", sa.String(length=150), nullable=False),
            sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
            sa.Column("unit", sa.String(length=50), nullable=False),
        ]),
        ("energy_usage", [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reporting_period_id", sa.Integer(), nullable=False),
            sa.Column("source", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
            sa.Column("unit", sa.String(length=50), nullable=False),
            sa.Column("renewable_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        ]),
        ("material_usage", [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reporting_period_id", sa.Integer(), nullable=False),
            sa.Column("material_name", sa.String(length=150), nullable=False),
            sa.Column("material_type", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
            sa.Column("unit", sa.String(length=50), nullable=False),
            sa.Column("recycled_content_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        ]),
        ("waste_records", [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reporting_period_id", sa.Integer(), nullable=False),
            sa.Column("waste_type", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
            sa.Column("unit", sa.String(length=50), nullable=False),
            sa.Column("disposal_method", sa.String(length=100), nullable=False),
            sa.Column("recycled_quantity", sa.Numeric(18, 6), nullable=False, server_default="0"),
        ]),
        ("transportation_activities", [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reporting_period_id", sa.Integer(), nullable=False),
            sa.Column("mode", sa.String(length=100), nullable=False),
            sa.Column("direction", sa.String(length=50), nullable=False),
            sa.Column("distance", sa.Numeric(18, 6), nullable=False),
            sa.Column("distance_unit", sa.String(length=50), nullable=False),
            sa.Column("load_quantity", sa.Numeric(18, 6), nullable=False),
            sa.Column("load_unit", sa.String(length=50), nullable=False),
        ]),
    ]
    for table_name, columns in activity_tables:
        op.create_table(
            table_name,
            *columns,
            sa.ForeignKeyConstraint(
                ["reporting_period_id"],
                ["reporting_periods.id"],
                ondelete="CASCADE",
            ),
        )
        op.create_index(
            f"ix_{table_name}_reporting_period_id",
            table_name,
            ["reporting_period_id"],
        )

    op.create_table(
        "emission_calculations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reporting_period_id", sa.Integer(), nullable=False),
        sa.Column("total_kg_co2e", sa.Numeric(18, 6), nullable=False),
        sa.Column("calculation_version", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["reporting_period_id"],
            ["reporting_periods.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_emission_calculations_reporting_period_id",
        "emission_calculations",
        ["reporting_period_id"],
    )
    op.create_table(
        "emission_breakdowns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("calculation_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=150), nullable=False),
        sa.Column("activity_quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("activity_unit", sa.String(length=50), nullable=False),
        sa.Column("applied_factor", sa.Numeric(18, 8), nullable=False),
        sa.Column("kg_co2e", sa.Numeric(18, 6), nullable=False),
        sa.Column("percentage_of_total", sa.Numeric(7, 4), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["calculation_id"],
            ["emission_calculations.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_emission_breakdowns_calculation_id",
        "emission_breakdowns",
        ["calculation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_emission_breakdowns_calculation_id", table_name="emission_breakdowns")
    op.drop_table("emission_breakdowns")
    op.drop_index("ix_emission_calculations_reporting_period_id", table_name="emission_calculations")
    op.drop_table("emission_calculations")
    for table_name in reversed([
        "transportation_activities",
        "waste_records",
        "material_usage",
        "energy_usage",
        "production_activities",
    ]):
        op.drop_index(f"ix_{table_name}_reporting_period_id", table_name=table_name)
        op.drop_table(table_name)
    op.drop_index("ix_reporting_periods_factory_id", table_name="reporting_periods")
    op.drop_table("reporting_periods")
    op.drop_index("ix_emission_factors_category", table_name="emission_factors")
    op.drop_table("emission_factors")
    op.drop_table("factories")
