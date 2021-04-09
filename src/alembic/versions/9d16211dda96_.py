"""empty message

Revision ID: 9d16211dda96
Revises: 7b72cdc960dd
Create Date: 2021-02-16 17:35:01.343475

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy.sql import ClauseElement, False_

revision = '9d16211dda96'
down_revision = '67ddbf216d81'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ws_map_record', sa.Column('downloaded', sa.Boolean(), nullable=False, server_default=False_()))


def downgrade():
    op.drop_column('ws_map_record', 'downloaded')
