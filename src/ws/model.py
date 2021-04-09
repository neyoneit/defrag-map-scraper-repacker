import datetime
import itertools
import urllib.parse
from enum import Enum
from typing import NamedTuple, List

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Date, UniqueConstraint, Boolean, select, func, Index

from models.common import Base


class MapTableRow(NamedTuple):
    release_date: datetime.date
    name: str
    link: str
    pk3_file: str
    pk3_file_has_link: bool
    size_str: str
    functions: List[str]
    items: List[str]
    weapons: List[str]
    mods: List[str]
    game_types: List[str]

    EXPANSION = {
        # Exported from https://ws.q3df.org/legend/#lg-weapon using script like this:
        # Array.from(document.querySelectorAll('#lg-item+ul img')).map((x) => x.src).join("\n")
        "mods": {"defrag", "freestyle", "wfa", "urbanterror", "q3fortress", "threewave", "navyseals", "team_arena",
                 "rocket_arena", "rally", "truecombat", "rq3", "tre", "fba", "jailbreak", "proball", "dom", "wop",
                 "jbpow", "bfp", "wq3", "mm", "cpma", "sid", "pka"},
        "functions": {"door", "button", "tele", "push", "moving", "shootergl", "shooterpg", "shooterrl", "slick",
                      "water", "fog", "slime", "lava", "break", "sound", "timer"},
        "items": {
            # Array.from(document.querySelectorAll('#lg-item+ul img')).map((x) => x.alt).join("\n")
            "ra", "ya", "sa", "enviro", "flight", "haste", "health", "largeh", "mega", "smallh", "invis", "quad",
            "regen", "medkit", "ptele", "ammoregen", "scout", "doubler", "guard", "kami", "invu", "ga",
        },
        "weapons": {
            # Array.from(document.querySelectorAll('#lg-weapon+ul img')).map((x) => x.alt).join("\n")
            "ga", "mg", "sg", "gl", "rl", "lg", "rg", "pg", "bfg", "hook", "cg", "ng", "pml",
        },
        "game_types": {
            # manually added
            'vq3', 'cpm',
            # Array.from(document.querySelectorAll('#lg-gametype+ul img')).map((x) => x.alt).join("\n")
            "ctf", "sp", "ffa", "tdm", "trn", "1f", "ol", "harv", "cctf", "ctfs", "dom", "lms", "lmst", "mission",
            "rctf", "ts", "ftl", "cah", "bomb", "ut_ctf", "ut_team",
        }
    }

    def to_db_record(self):
        return {
            "release_date": self.release_date,
            "name": self.name,
            "link": self.link,
            "pk3_file": self.pk3_file,
            "pk3_file_has_link": self.pk3_file_has_link,
            "size_str": self.size_str,
            **self._expand("functions", self.functions),
            **self._expand("items", self.items),
            **self._expand("weapons", self.weapons),
            **self._expand("mods", self.mods),
            **self._expand("game_types", self.game_types),
        }

    def _expand(self, name: str, data: List[str]):
        return dict(self._expand_gen(name, data))

    @staticmethod
    def _expand_gen(name, data: List[str]):
        known = MapTableRow.EXPANSION[name]
        data_set = set(data)
        unknown = data_set - known
        if len(unknown) > 0:
            raise ValueError(f"Unknown {name}: {unknown}")
        for variant in known:
            yield (f"{name}_{variant}", variant in data_set)


def expanded_columns(name: str):
    for variant in MapTableRow.EXPANSION[name]:
        yield Column(f"{name}_{variant}", Boolean)


def all_expanded_columns():
    return list(itertools.chain.from_iterable(map(expanded_columns, MapTableRow.EXPANSION)))


class MapRecord(Base):
    __table__ = Table(
        'ws_map_record', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('release_date', Date),
        Column('name', String(50)),
        Column('link', String(100)),
        Column('pk3_file', String(50)),
        Column('pk3_file_has_link', Boolean),
        Column('size_str', String(50)),
        Column('downloaded', Boolean, nullable=False, default=False),
        Column('minified', Boolean, nullable=False, default=False),
        *all_expanded_columns(),
        UniqueConstraint('link', 'pk3_file', name='unique_name')
    )


class ZipLocation(Enum):
    STANDARD = 'standard'
    EXTRA_DIR = 'extra_dir'


class MapPackAssignment(Base):
    __table__ = Table(
        'ws_map_pack_assignment', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('zip_filename', String(256), nullable=False),
        Column('bsp_filename', String(256), nullable=False, unique=True),
        Column('bsp_filename_base', String(256), nullable=False, unique=True),
        Column('group_id', String(256), nullable=False),
        Column('zip_location', sqlalchemy.Enum(ZipLocation, values_callable=lambda obj: [e.value for e in obj])),
        Index("ws_map_pack_assignment_group_id", 'group_id', unique=False)
    )


def map_exists(db_session, row):
    res = db_session.execute(
        select([func.count()])
        .where(MapRecord.link == row.link)
        .where(MapRecord.pk3_file == row.pk3_file)
        .limit(1)
    ).first()[0]
    return res == 1


def get_map_info(db_session, map_id: str):
    return db_session.execute(
        select(['*'])
        .where(MapRecord.link == f"/map/{urllib.parse.quote(map_id, '')}/")
    ).first()
