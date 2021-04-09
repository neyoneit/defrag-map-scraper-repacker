"""empty message

Revision ID: 940e4f657388
Revises: 5cc0a8972334
Create Date: 2021-02-21 01:39:39.927118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '940e4f657388'
down_revision = '4bfa2709ad6e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ws_map_pack_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('zip_filename', sa.String(length=256), nullable=False),
    sa.Column('bsp_filename', sa.String(length=256), nullable=False),
    sa.Column('group_id', sa.String(256), nullable=False),
    sa.Column('bsp_filename_base', sa.String(length=256), nullable=False),
    sa.Column('zip_location', sa.Enum('standard', 'extra_dir', name='ziplocation'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('bsp_filename')
    )
    op.create_index('ws_map_pack_assignment_group_id', 'ws_map_pack_assignment', ['group_id'], unique=False)
    op.execute("UPDATE ws_map_record SET minified=0")

def downgrade():
    op.drop_index('ws_map_pack_assignment_group_id', table_name='ws_map_pack_assignment')
    op.drop_table('ws_map_pack_assignment')
