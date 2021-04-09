"""empty message

Revision ID: 4bfa2709ad6e
Revises: 9d16211dda96
Create Date: 2021-02-19 14:53:51.996892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import False_

revision = '4bfa2709ad6e'
down_revision = '9d16211dda96'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ws_map_record', sa.Column('minified', sa.Boolean(), nullable=True, server_default=False_()))


def downgrade():
    op.drop_column('ws_map_record', 'minified')
