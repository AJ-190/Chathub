"""added unique constraint on the email column in the users table

Revision ID: 1a3cc1aba847
Revises: 3cc13676bf84
Create Date: 2026-09-24 20:04:38.227507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a3cc1aba847'
down_revision: Union[str, Sequence[str], None] = '3cc13676bf84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_email', 'users', type_='unique')
