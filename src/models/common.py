import os
from os.path import dirname

import alembic.config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from settings import CONN_STRING

Base = declarative_base()


def create_current_db_engine():
    connection = create_engine(CONN_STRING, echo=False)
    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option('script_location', os.path.join(dirname(__file__), "..", "alembic"))
    alembic_cfg.attributes['connection'] = connection
    command.upgrade(alembic_cfg, 'head')

    return connection
