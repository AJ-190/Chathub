"""added unique constraint on the phone column in the users table

Revision ID: 3cc13676bf84
Revises: 08e6fafbd1d4
Create Date: 2026-09-08 17:39:12.432176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3cc13676bf84'
down_revision: Union[str, Sequence[str], None] = '08e6fafbd1d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_users_phone', 'users', ['phone'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_phone', 'users', type_='unique')
