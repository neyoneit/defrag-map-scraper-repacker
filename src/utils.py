import itertools
import os
import random
from decimal import Decimal
from typing import TypeVar, Iterable, Callable, Iterator, Tuple, Set


def mkdirs_if_not_exists(basedir, subdir):
    dir = basedir
    for component in subdir:
        dir = os.path.join(dir, component)
        mkdir_if_not_exists(dir)


def mkdir_if_not_exists(dir):
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass


def shuffled(l):
    l2 = list(l)  # normalize and clone
    random.shuffle(l2)
    return l2


def time_to_decimal(time: str) -> Decimal:
    time_parts = time.split(":", 2)
    if len(time_parts) == 2:
        [s, ms] = time_parts
        m = "0"
    elif len(time_parts) == 3:
        [m, s, ms] = time_parts
    else:
        raise ValueError(f"Bad time: {time}")
    return Decimal(m)*Decimal(60) + Decimal(f"{s}.{ms}")


T = TypeVar("T")
U = TypeVar("U")


def groupby_unsorted(items: Iterable[T], key: Callable[[T], U]) -> Iterator[Tuple[U, T]]:
    return itertools.groupby(sorted(items, key=key), key=key)


def read_policylist(filename) -> Set[str]:
    if os.path.exists(filename):
        with open(filename) as f:
            return set(map(lambda s: s.strip(), f.readlines()))
    else:
        return set()