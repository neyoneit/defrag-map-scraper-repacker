from typing import Dict
from zipfile import ZipFile


class CachedZipFile:
    _cache: Dict[str, bytes]

    def __init__(self, zf: ZipFile):
        self._zf = zf
        self._cache =  dict()

    def read(self, name, pwd=None):
        if pwd is None:
            out = self._cache.get(name)
            if out is not None:
                return out
            else:
                out = self._zf.read(name, pwd)
                self._cache[name] = out
                return out
        else:
            return self._zf.read(name, pwd)

    def infolist(self):
        return self._zf.infolist()

    def close(self):
        return self._zf.close()
