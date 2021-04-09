import datetime
import urllib.parse
from os.path import basename
from typing import Optional

from bs4 import BeautifulSoup, Tag, NavigableString

from ws.model import MapTableRow


def parse_date(d):
    [y, m, d] = map(int, d.split('-'))
    return datetime.date(y, m, d)


def remove_extension(s: str):
    pos = s.rindex('.')
    return s[0:pos]


def parse_img_alt(img: Tag):
    return img.attrs['alt']


def parse_img(img: Tag):
    src: str = img.attrs['src']
    return remove_extension(basename(src))


def find_rows(page_soup: BeautifulSoup, page_size: int):
    maps_table = page_soup.find("table", {"id": "maps_table"})
    trs = maps_table.find_all("tr")[1:]
    assert len(trs) <= page_size

    for tr in trs:
        yield parse_row(tr)


def parse_game_type(a: Tag):
    text = a.text.strip()
    if text == "":
        return a.find("img").attrs["alt"]
    else:
        return text


def parse_row(tr: Tag):
    tds = tr.find_all('td')
    release_cell: Tag = tds[0]
    map_details_cell: Tag = tds[1]
    pk3_file_cell: Tag = tds[2]
    size_cell: Tag = tds[3]
    mod_cell: Tag = tds[4]
    game_types_cell: Tag = tds[5]
    weapons_cell: Tag = tds[6]
    items_cell: Tag = tds[7]
    functions_cell: Tag = tds[8]
    map_link_tag: Tag = map_details_cell.find("a")
    map_link = map_link_tag.attrs['href']
    map_name = map_details_cell.text.strip()
    pk3_file = pk3_file_cell.text.strip()
    pk3_file_link_tag: Optional[Tag] = pk3_file_cell.find("a")
    use_pk3_file_link_tag = pk3_file_link_tag is not None and pk3_file_link_tag.text.strip() == pk3_file
    pk3_file_link: Optional[str] = pk3_file_link_tag.attrs['href'] if use_pk3_file_link_tag else None
    if pk3_file_link is not None:
        expected_link = f"/maps/downloads/{urllib.parse.quote(pk3_file, '')}.pk3"
        if pk3_file_link != expected_link:
            raise AssertionError(f"pk3_file_link ({pk3_file_link}) != expected_link ({expected_link}) in {tr}")
    size_cell_last: NavigableString = (size_cell.contents[-1])
    size_str = size_cell_last.strip()
    # Does not always hold: assert (pk3_file_link is None) == (size_str == "")
    mods = list(map(parse_img, mod_cell.find_all("img")))

    return MapTableRow(
        release_date=parse_date(release_cell.text),
        name=map_name,
        link=map_link,
        pk3_file=pk3_file,
        pk3_file_has_link=pk3_file_link is not None,
        size_str=size_str,
        functions=list(map(parse_img, functions_cell.find_all("img"))),
        items=list(map(parse_img_alt, items_cell.find_all("img"))),
        weapons=list(map(parse_img_alt, weapons_cell.find_all("img"))),
        mods=mods,
        game_types=list(map(parse_game_type, game_types_cell.find_all("a"))),
    )
