"""Add columns for map details

Revision ID: 3d8f7ebd33ed
Revises: 940e4f657388
Create Date: 2021-05-26 15:23:13.633635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d8f7ebd33ed'
down_revision = '940e4f657388'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ws_map_record', sa.Column('author', sa.String(length=512), nullable=True))
    op.add_column('ws_map_record', sa.Column('crawling_level', sa.Integer(), server_default=sa.text('0'), nullable=True))
    op.add_column('ws_map_record', sa.Column('downloads', sa.Integer(), nullable=True))
    op.add_column('ws_map_record', sa.Column('downloads_checked', sa.DateTime(), nullable=True))
    op.add_column('ws_map_record', sa.Column('map_details_topview_url', sa.String(length=512), nullable=True))
    op.add_column('ws_map_record', sa.Column('map_details_panorama_url', sa.String(length=512), nullable=True))
    op.add_column('ws_map_record', sa.Column('map_thumbnail_url', sa.String(length=512), nullable=True))
    op.add_column('ws_map_record', sa.Column('md5', sa.String(length=32), nullable=True))
    op.create_index(op.f('ix_ws_map_record_crawling_level'), 'ws_map_record', ['crawling_level'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ws_map_record_crawling_level'), table_name='ws_map_record')
    op.drop_column('ws_map_record', 'md5')
    op.drop_column('ws_map_record', 'map_thumbnail_url')
    op.drop_column('ws_map_record', 'map_details_panorama_url')
    op.drop_column('ws_map_record', 'map_details_topview_url')
    op.drop_column('ws_map_record', 'downloads_checked')
    op.drop_column('ws_map_record', 'downloads')
    op.drop_column('ws_map_record', 'crawling_level')
    op.drop_column('ws_map_record', 'author')
