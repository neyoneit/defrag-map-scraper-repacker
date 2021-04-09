"""initial structure

Revision ID: 67ddbf216d81
Revises: 
Create Date: 2020-12-23 00:17:38.557739

"""
# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import sessionmaker

revision = '67ddbf216d81'
down_revision = None
branch_labels = None
depends_on = None

Session = sessionmaker()


def create_ws_map_record():
    op.create_table(
        'ws_map_record',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('release_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('link', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('pk3_file', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('pk3_file_has_link', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('size_str', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('mods_rq3', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_rally', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_mm', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_wfa', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_defrag', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_jbpow', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_rocket_arena', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_threewave', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_bfp', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_fba', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_urbanterror', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_dom', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_truecombat', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_proball', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_tre', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_pka', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_navyseals', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_sid', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_cpma', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_freestyle', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_jailbreak', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_team_arena', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_wq3', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_q3fortress', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('mods_wop', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_shooterpg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_door', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_tele', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_timer', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_shootergl', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_shooterrl', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_water', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_moving', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_fog', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_button', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_push', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_slime', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_break', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_sound', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_slick', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('functions_lava', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_kami', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_sa', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_guard', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_ga', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_flight', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_largeh', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_doubler', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_smallh', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_mega', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_ra', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_regen', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_haste', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_enviro', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_medkit', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_ptele', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_quad', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_invu', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_invis', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_health', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_ammoregen', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_scout', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('items_ya', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_sg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_rg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_bfg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_hook', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_pml', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_ng', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_gl', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_cg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_ga', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_pg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_lg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_mg', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('weapons_rl', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_lmst', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ffa', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ftl', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_harv', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_cctf', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ol', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ut_ctf', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_vq3', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ctf', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_dom', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ctfs', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_sp', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_lms', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_trn', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_mission', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_1f', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_rctf', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ts', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_cah', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_cpm', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_ut_team', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_bomb', sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column('game_types_tdm', sa.Boolean(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='PK__ws_map_r__3213E83F468D835F')
    )


def upgrade():
    create_ws_map_record()

    # ### end Alembic commands ###


def downgrade():
    op.drop_table('ws_map_record')
    # ### end Alembic commands ###
