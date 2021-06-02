#!/usr/bin/env python3
import argparse
import asyncio
import datetime
import hashlib
import os
import shutil
import traceback
import urllib.parse
from asyncio import Semaphore
from enum import Enum
from os.path import dirname, basename
from typing import Optional, Tuple, List, Union
from zipfile import ZipFile, ZipInfo

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, select
from typing.io import TextIO

from models.common import create_current_db_engine
from scrape.scrape_utils import get
from settings import MAPS_OUTPUT_DIRECTORY, MINIFIED_MAPS_OUTPUT_DIRECTORY, MAPS_CUSTOM_INBOX, MAPS_CUSTOM_PROCESSED
from utils import groupby_unsorted, mkdirs_if_not_exists
from ws.maps_repack import ZipSplit, ZipChunksSplit, ensure_pk3_repack, ZipSingleFilesSplit, PerPk3Split
from ws.model import MapRecord, map_exists, MapPackAssignment, ZipLocation
from ws.parser import find_rows, parse_details
from zip_cache import CachedZipFile

HOST = "https://ws.q3df.org"
PAGE_SIZE = 50


def crawl_ws(session):
    db_session = session()
    try:
        max_ts = db_session.execute(select([func.max(MapRecord.release_date)])).first()[0]
        print(f"max_ts: {max_ts} ({type(max_ts)})")
        page_id = 0
        has_next = True
        last_found_ts: Optional[datetime.date] = None
        found_duplicate = False
        while has_next and (max_ts is None or last_found_ts is None or last_found_ts >= max_ts):
            print(f"last_found_ts ({last_found_ts}) >= max_ts ({max_ts})")
            print(f"page_id: {page_id+1}")
            page = get(f"{HOST}/maps/?map=&page=0{page_id}&show={PAGE_SIZE}")
            page_soup = BeautifulSoup(page, "html.parser")
            has_next = page_soup.find("a", {"rel": "next"}) is not None
            rows = find_rows(page_soup, PAGE_SIZE)
            for row in rows:
                last_found_ts = row.release_date
                record_exists = map_exists(db_session, row)
                if (not record_exists) and found_duplicate:
                    raise Exception(f"Suspicious: Record {row} does not exist, but we already have found a duplicate")
                found_duplicate = found_duplicate or record_exists
                if not record_exists:
                    db_session.execute(insert(MapRecord).values(row.to_db_record()))
            page_id += 1
        db_session.commit()
    finally:
        db_session.close()


async def download_maps(sessionmaker, http_session):
    db_session = sessionmaker()
    semaphore = Semaphore(1)

    def get_missing():
        return select(['*']).where(MapRecord.downloaded == False).where(MapRecord.pk3_file_has_link == True)

    def mark_downloaded(pk3_file):
        update_db_session = sessionmaker()
        update_db_session.execute(update(MapRecord).where(MapRecord.pk3_file == pk3_file).values(downloaded = True))
        update_db_session.commit()

    async def process_record(map_record):
        async with semaphore:
            link = f"https://ws.q3df.org/maps/downloads/{urllib.parse.quote(map_record.pk3_file, '')}.pk3"
            print(f"Starting {link}")
            if db_session.execute(get_missing().where(MapRecord.id == map_record.id)).first() is None:
                print(f"Skipping {link}")
                return

            await asyncio.sleep(1)

            out_file = os.path.join(MAPS_OUTPUT_DIRECTORY, f"{map_record.pk3_file}.pk3")

            if os.path.exists(out_file):
                mark_downloaded(map_record.pk3_file)
                print(f"Already exists: {out_file}")
                return

            res = await http_session.get(link)

            if sanitize_filename(map_record.pk3_file) != map_record.pk3_file:
                raise Exception(f"Dangerous file name: {map_record.pk3_file}")

            tmp_file = f"{out_file}.tmp"

            with open(tmp_file, "wb") as f:
                f.write(await res.read())

            if os.path.exists(out_file):
                raise Exception(f"File {out_file} already exists")
            os.rename(tmp_file, out_file)

            mark_downloaded(map_record.pk3_file)
            print(f"Finished {link}")

    result = db_session.execute(get_missing())
    for r in list(map(lambda r: asyncio.ensure_future(process_record(r)), result.fetchall())):
        try:
            await r
        except:
            print("Skipping a map download because of:")
            traceback.print_exc()


def should_include(info: ZipInfo):
    f = info.filename
    lf = f.lower()
    print(f"f: {f} {not info.is_dir()} {lf.endswith('.bsp')}")
    return (not info.is_dir()) and lf.endswith(".bsp")


def find_duplicates(zip: Union[ZipFile, CachedZipFile]) -> List[Tuple[str, List[Tuple[bytes, List[ZipInfo]]]]]:
    def get_hash(file: ZipInfo) -> bytes:
        return hashlib.sha256(zip.read(file)).digest()

    def group_by_hash(basename_infos: (str, List[ZipInfo])) -> (str, List[Tuple[bytes, List[ZipInfo]]]):
        (name, infos) = basename_infos
        hashed: List[(ZipInfo, bytes)] = list(map(lambda info: (info, get_hash(info)), infos))
        by_hash: List[(bytes, List[ZipInfo])] = [(key, list(map(lambda x: x[0], group))) for key, group in
                                                 groupby_unsorted(hashed, key=lambda x: x[1])]
        return (name, by_hash)


    included_items: List[ZipInfo] = list(filter(should_include, zip.infolist()))
    grouped_items: List[Tuple[str, List[ZipInfo]]] = [(key, list(group)) for key, group in
                                                      groupby_unsorted(included_items, lambda item: basename(item.filename.lower()))]
    duplicate_names: List[Tuple[str, List[ZipInfo]]] = list(filter(lambda x: len(x[1]) > 1, grouped_items))
    # List[(basename: str, List[(hash: bytes, files: List[ZipInfo])])]
    duplicate_names_hashed: List[Tuple[str, List[Tuple[bytes, List[ZipInfo]]]]] = list(map(group_by_hash, duplicate_names))
    duplicate_names_diverging_hashes: List[Tuple[str, List[Tuple[bytes, List[ZipInfo]]]]] = list(
        filter(lambda x: len(x[1]) > 1, duplicate_names_hashed)
    )
    return duplicate_names_diverging_hashes


class Log:
    _log_file: TextIO
    _throw_exceptions: bool

    def __init__(self, log_file: TextIO, throw_exceptions: bool) -> None:
        super().__init__()
        self._log_file = log_file
        self._throw_exceptions = throw_exceptions

    def log_exception(self, location: str, e):
        self._log_file.write(f"{datetime.datetime.now()}: Exception at {location}: {e}\n")
        self._log_file.flush()
        if self._throw_exceptions or isinstance(e, KeyboardInterrupt):
            raise

    def log_warning(self, text: str):
        self._log_file.write(f"{datetime.datetime.now()}: WARN: {text}\n")
        self._log_file.flush()


async def minify_maps(sessionmaker, repack_log: Log, zip_split: ZipSplit):
    db_session = sessionmaker()

    def get_missing():
        return select(['*']).where(MapRecord.minified == False).where(MapRecord.downloaded == True)

    def confirm_done(map_record):
        update_db_session = sessionmaker()
        update_db_session.execute(update(MapRecord).where(MapRecord.pk3_file == map_record.pk3_file).values(minified = True))
        update_db_session.commit()
        print(f"Finished minification {map_record.pk3_file}")

    def enumerate():
        # Enumerate custom files
        for file_basename in os.listdir(MAPS_CUSTOM_INBOX):
            file = os.path.join(MAPS_CUSTOM_INBOX, file_basename)
            file_after_processed = os.path.join(MAPS_CUSTOM_PROCESSED, file_basename)
            if os.path.exists(file_after_processed):
                repack_log.log_warning(f"Skipping file {file}, as file {file_after_processed} already exists.")
            else:
                with ZipFile(file, 'r') as inzip:
                    yield (file_basename, file, CachedZipFile(inzip), lambda: shutil.move(file, file_after_processed), ZipLocation.EXTRA_DIR)

        # Enumerate standard files with records in DB
        result = db_session.execute(get_missing())
        for map_record in result.fetchall():
            print(f"Starting minification {map_record.pk3_file}")
            if db_session.execute(get_missing().where(MapRecord.id == map_record.id)).first() is None:
                print(f"Skipping as already processed {map_record.pk3_file}")
                continue

            if sanitize_filename(map_record.pk3_file) != map_record.pk3_file:
                raise Exception(f"Dangerous file name: {map_record.pk3_file}")

            in_file_basename = f"{map_record.pk3_file}.pk3"
            in_file = os.path.join(MAPS_OUTPUT_DIRECTORY, in_file_basename)

            if not os.path.exists(in_file):
                print(f"Skipping because it does not exist: {in_file}")
                continue

            try:
                with ZipFile(in_file, 'r') as inzip:
                    yield (in_file_basename, in_file, CachedZipFile(inzip), lambda: confirm_done(map_record), ZipLocation.STANDARD)
            except:
                print(f"Failed: {in_file}")
                repack_log.log_exception(f"{in_file} (error when reading)", traceback.format_exc())

    with zip_split as out:
        for inzip_file_basename, inzip_filename, inzip, done_callback, zip_location in enumerate():
            has_warning = False
            out.next_pk3(inzip_file_basename)
            try:
                diverging_duplicates = find_duplicates(inzip)
                if len(diverging_duplicates) > 0:
                    repack_log.log_warning(f"{inzip_filename} (duplicates with diverging hashes): {diverging_duplicates}")
                    has_warning = True
                    mkdirs_if_not_exists(MAPS_OUTPUT_DIRECTORY, ['with-diverging-duplicates'])
                    out_name = os.path.join(MAPS_OUTPUT_DIRECTORY, 'with-diverging-duplicates', inzip_file_basename)
                    if os.path.exists(out_name):
                        raise Exception(f"File already exists: {out_name}")
                    inzip.close()
                    shutil.move(inzip_filename, out_name)
                    continue
                for info in filter(should_include, inzip.infolist()):
                    try:
                        filename_base = basename(info.filename)
                        if db_session.execute(select([func.count()]).where(MapPackAssignment.bsp_filename_base == filename_base)).first()[0] > 0:
                            repack_log.log_warning(f"{inzip_filename} / {info.filename}: duplicate")
                            has_warning = True
                        elif db_session.execute(select([func.count()]).where(MapPackAssignment.bsp_filename == info.filename)).first()[0] > 0:
                            repack_log.log_warning(f"{inzip_filename} / {info.filename}: duplicate that was not caught by bsp_filename_base == filename_base")
                            has_warning = True
                        else:
                            in_filename = info.filename
                            info.filename = "maps/" + filename_base
                            id = out.add(info=info, inzip=inzip, in_filename=in_filename)
                            db_session.execute(insert(MapPackAssignment, {
                                "zip_filename": inzip_file_basename,
                                "bsp_filename": in_filename,
                                "bsp_filename_base": filename_base,
                                "group_id": id,
                                "zip_location": zip_location,
                            }))
                            db_session.commit()
                    except BaseException:
                        repack_log.log_exception(f"{inzip_filename} / {info.filename}", traceback.format_exc())
            except BaseException:
                repack_log.log_exception(f"{inzip_filename}", traceback.format_exc())
            if (not has_warning) or (zip_location == ZipLocation.STANDARD):
                # If it has a warning and the ZIP is from the extra folder, don't move it
                done_callback()


class RepackStyle(Enum):
    large_pk3s = 'large_pk3s'
    per_pk3 = 'per_pk3'
    per_bsp = 'per_bsp'

    def __str__(self):
        return self.name


def crawl_details(db_session):
    connection = db_session()
    def get_missing():
        return select(['*']).where(MapRecord.crawling_level < MapRecord.CRAWLING_LEVEL_MAX)

    items_to_update = connection.execute(get_missing()).fetchall()
    print(f'Need to fetch details for {len(items_to_update)} items')
    for map_record in items_to_update:
        if connection.execute(get_missing().where(MapRecord.id == map_record.id)).first() is None:
            print(f"Skipping as already processed {map_record.pk3_file}")
            continue

        try:
            basic_details = parse_details(get(HOST + map_record.link))
            if basic_details.submenu_others == []:
                details = basic_details
            elif basic_details.submenu_others == [('Panorama', 1)]:
                panorama_details = parse_details(get(HOST + map_record.link + '?mapmenu=1'))
                details = basic_details.combine(panorama_details)
            else:
                raise Exception(f'Unexpected submenu: {basic_details.submenu}')
            connection.execute(
                update(MapRecord).where(MapRecord.id == map_record.id).values({
                    **details.to_db_row(),
                    "crawling_level": MapRecord.CRAWLING_LEVEL_MAX
                })
            )
            connection.commit()
            print(f"updated: {details.name or map_record.name}")
        except Exception as e:
            raise Exception(f'Processing of {map_record.link} failed') from e


async def async_main():
    parser = argparse.ArgumentParser(description=f'Indexes maps at {HOST}, downloads them and minifies (repacks) them.')
    parser.add_argument('--skip-map-download', dest='download_maps', action='store_false', default=True,
                        help='Skips map download. Useful for development rather than for production.')
    parser.add_argument('--skip-map-repack', dest='repack_maps', action='store_false', default=True,
                        help='Skips map repack. Useful for development rather than for production.')
    parser.add_argument('--repack-style', dest='repack_style', type=RepackStyle, choices=list(RepackStyle),
                        default=RepackStyle.large_pk3s,
                        help=f'Repack style. {RepackStyle.large_pk3s} will create large pk3 bundles.')
    parser.add_argument('--repack-size-cap', dest='repack_size_cap', action='store', default=1.5 * 1024 * 1024 * 1024,
                        help=f'Maximum size of repack. Effective only for --repack-style={RepackStyle.large_pk3s}')
    parser.add_argument('--reset-minified-maps', dest='reset_minified_maps', action='store_true', default=False,
                        help='Reset minified maps. This is useful when changing options like --repack-style or --repack-size-cap. Note that this does not delete the output files, so you need to delete them on your own.')
    parser.add_argument('--throw-exceptions', dest='throw_exceptions', action='store_true', default=False,
                        help='When scripts encounters an error, throw an exception rather than log it.')
    args = parser.parse_args()

    db_engine = create_current_db_engine()
    db_session = sessionmaker(bind=db_engine)

    crawl_ws(db_session)

    if args.download_maps:
        async with ClientSession() as http_session:
            await download_maps(db_session, http_session)

    if args.reset_minified_maps:
        connection = db_session()
        connection.execute(update(MapRecord).values({"minified": False}))
        connection.execute(delete(MapPackAssignment))
        connection.commit()

    if args.repack_maps:
        await repack_maps(args, db_session)

    crawl_details(db_session)


async def repack_maps(args, db_session):
    with open(os.path.join(dirname(__file__), 'ws-scrape-repack-errors.log'), 'a') as repack_log_file:
        repack_log = Log(repack_log_file, args.throw_exceptions)
        if args.repack_style == RepackStyle.large_pk3s:
            connection = db_session()
            initial_id = int(connection.execute(select([func.max(MapPackAssignment.group_id)])).first()[0] or 0)
            connection.close()
            for i in range(0, initial_id + 1):
                ensure_pk3_repack(i, connection)
            zip_split = ZipChunksSplit(dir=MINIFIED_MAPS_OUTPUT_DIRECTORY, size_cap=int(args.repack_size_cap),
                                       initial_id=initial_id)
        elif args.repack_style == RepackStyle.per_bsp:
            zip_split = ZipSingleFilesSplit(dir=MINIFIED_MAPS_OUTPUT_DIRECTORY)
        elif args.repack_style == RepackStyle.per_pk3:
            zip_split = PerPk3Split(dir=MINIFIED_MAPS_OUTPUT_DIRECTORY)
        else:
            raise AssertionError(f"Unknown repack style: {args.repack_style}")
        await minify_maps(db_session, repack_log, zip_split)


def main():
    asyncio.get_event_loop().run_until_complete(async_main())


if __name__ == "__main__":
    main()
