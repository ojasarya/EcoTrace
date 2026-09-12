"""Link factories to optional authenticated owners.

Revision ID: 0005_factory_owners
Revises: 0004_users
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_factory_owners"
down_revision: Union[str, None] = "0004_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("factories") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_factories_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index("ix_factories_owner_id", "factories", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_factories_owner_id", table_name="factories")
    with op.batch_alter_table("factories") as batch_op:
        batch_op.drop_constraint("fk_factories_owner_id_users", type_="foreignkey")
        batch_op.drop_column("owner_id")
