import os
from abc import ABC, abstractmethod
from os.path import basename
from typing import Optional, Union
from zipfile import ZipFile, ZipInfo

from pathvalidate import sanitize_filename
from sqlalchemy.sql import select

from settings import MAPS_OUTPUT_DIRECTORY, MINIFIED_MAPS_OUTPUT_DIRECTORY, MAPS_CUSTOM_PROCESSED
from utils import groupby_unsorted
from ws.model import MapPackAssignment, ZipLocation
from zip_cache import CachedZipFile


class ZipSplit(ABC):

    @abstractmethod
    def add(self, info: ZipInfo, in_filename: str, inzip: Union[ZipFile, CachedZipFile]) -> str:
        pass

    @abstractmethod
    def next_pk3(self, name: str):
        pass

    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, type, value, traceback):
        pass



class ZipSingleFilesSplit(ZipSplit):

    def __init__(self, dir: str):
        self._dir = dir

    def add(self, info: ZipInfo, in_filename: str, inzip: Union[ZipFile, CachedZipFile]):
        id = basename(in_filename)
        with ZipFile(os.path.join(self._dir, f"{id}.pk3"), "a") as out_zip:
            out_zip.writestr(
                zinfo_or_arcname=info,
                data=inzip.read(in_filename),
                compress_type=info.compress_type,
                compresslevel=9
            )
        return id

    def next_pk3(self, name: str):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class PerPk3Split(ZipSplit):
    _out_zip: Optional[ZipFile] = None
    _id: Optional[str] = None

    def __init__(self, dir: str):
        self._dir = dir

    def add(self, info: ZipInfo, in_filename: str, inzip: Union[ZipFile, CachedZipFile]):
        self._out_zip.writestr(
            zinfo_or_arcname=info,
            data=inzip.read(in_filename),
            compress_type=info.compress_type,
            compresslevel=9
        )
        return self._id

    def next_pk3(self, name: str):
        if self._out_zip is not None:
            self._out_zip.close()
            self._out_zip = None
        self._id = basename(name)
        self._out_zip = ZipFile(os.path.join(self._dir, self._id), "a")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self._out_zip is not None:
            self._out_zip.close()


class ZipChunksSplit(ZipSplit):
    _out_zip: Optional[ZipFile] = None

    def __init__(self, dir: str, initial_id: int, size_cap: int):
        self._dir = dir
        self._id = initial_id
        self._size_cap = size_cap
        self._size = self._size_for_file(self._filename_for_current_id())

    def add(self, info: ZipInfo, in_filename: str, inzip: Union[ZipFile, CachedZipFile]):
        if self._size + info.compress_size > self._size_cap:
            if info.compress_size > self._size_cap:
                raise Exception(f"Too large file {info}: Compressed size {info.compress_size}B is larger than the size cap {self._size_cap}B")
            self._increment_repack()
        self._ensure_out_zip()
        self._out_zip.writestr(
            zinfo_or_arcname=info,
            data=inzip.read(in_filename),
            compress_type=info.compress_type,
            compresslevel=9
        )
        self._size += info.compress_size
        return str(self._id)

    def next_pk3(self, name: str):
        # Nothing to do; We don't care
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self._out_zip is not None:
            self._out_zip.close()

    def _ensure_out_zip(self):
        if self._out_zip is None:
            self._out_zip = ZipFile(self._filename_for_current_id(), "a")

    def _increment_repack(self):
        if self._out_zip is not None:
            self._out_zip.close()
            self._out_zip = None
        self._id += 1
        self._size = self._size_for_file(self._filename_for_current_id())

    def _filename_for_current_id(self):
        return os.path.join(self._dir, get_repack_filename(self._id))

    def _size_for_file(self, file: str) -> int:
        if not os.path.exists(file):
            # It might look tempting to remove this condition and to rely on FileNotFoundError instead. However, os.stat
            # is not guaranteed to throw this exception according to the documentation. Actually, the documentation does
            # not specify the behavior when the file is not found.
            return 0
        try:
            return os.stat(file).st_size
        except FileNotFoundError:
            return 0


def get_repack_filename(id):
    return f"maps_{id}.pk3"


def get_directory_for_zip_location(zip_location: ZipLocation):
    if zip_location == ZipLocation.STANDARD:
        return MAPS_OUTPUT_DIRECTORY
    elif zip_location == ZipLocation.EXTRA_DIR:
        return MAPS_CUSTOM_PROCESSED
    else:
        raise AssertionError(f"Unknown ZipLocation: {zip_location}")


def ensure_pk3_repack(i, db_session):
    repack_filename = os.path.join(MINIFIED_MAPS_OUTPUT_DIRECTORY, get_repack_filename(i))
    if not os.path.exists(repack_filename):
        files = db_session.execute(select([MapPackAssignment]).where(MapPackAssignment.group_id == str(i))).fetchall()
        with ZipFile(os.path.join(MINIFIED_MAPS_OUTPUT_DIRECTORY, repack_filename), "w") as out_zip:
            for (zip_filename, zip_location), files in groupby_unsorted(files, lambda f: (f.zip_filename, f.zip_location)):
                ensure_safe_filename(zip_filename)
                with ZipFile(os.path.join(get_directory_for_zip_location(zip_location), zip_filename), "r") as in_zip:
                    for file in files:
                        info = in_zip.getinfo(file.bsp_filename)
                        info.filename = "maps/" + file.bsp_filename_base
                        out_zip.writestr(
                            zinfo_or_arcname=info,
                            data=in_zip.read(info.filename),
                            compress_type=info.compress_type,
                            compresslevel=9
                        )


def ensure_safe_filename(filename):
    if sanitize_filename(filename) != filename:
        raise Exception(f"Dangerous file name: {filename}")
