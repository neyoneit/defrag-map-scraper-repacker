import datetime
import re
import urllib.parse
from os.path import basename
from typing import Optional, NamedTuple, List, Tuple

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

def one(xs: list):
    if len(xs) != 1:
        raise Exception(f"Bad list: {xs}")
    [x] = xs
    return x


def remove_prefix_strict(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    else:
        raise Exception('Missing prefix in '+text)


def need_at_most_one(a, b):
    if a is not None:
        if b is not None:
            raise Exception()
        else:
            return a
    else:
        return b


def optional_max(a, b):
    if (a is not None) and (b is not None):
        return max(a, b)
    if (a is None) and (b is None):
        return None
    raise Exception(f'Inconsistent max: {a} vs. {b}')

class MapDetails(NamedTuple):
    name: str
    author: Optional[str]
    downloads: Optional[str]
    map_thumbnail_url: str
    map_details_panorama_url: Optional[str]
    map_details_topview_url: Optional[str]
    md5: str
    submenu: List[Tuple[str, int]]
    submenu_position: Optional[int]

    @property
    def submenu_others(self):
        return list(filter(lambda x: x[1] != self.submenu_position, self.submenu))

    def combine(self, other):
        def need_same(a, b):
            if a != b:
                raise Exception(f'{a} != {b}')
            return a
        return MapDetails(
            author=need_same(self.author, other.author),
            name=need_same(self.name, other.name),
            map_thumbnail_url=need_same(self.map_thumbnail_url, other.map_thumbnail_url),
            md5=need_same(self.md5, other.md5),
            submenu=need_same(self.submenu, other.submenu),
            submenu_position=None,
            downloads=optional_max(self.downloads, other.downloads),
            map_details_topview_url=need_at_most_one(self.map_details_topview_url, other.map_details_topview_url),
            map_details_panorama_url=need_at_most_one(self.map_details_panorama_url, other.map_details_panorama_url),
        )

    def to_db_row(self):
        return {
            "author": self.author,
            "downloads": self.downloads,
            "map_thumbnail_url": self.map_thumbnail_url,
            "map_details_panorama_url": self.map_details_panorama_url,
            "map_details_topview_url": self.map_details_topview_url,
            "md5": self.md5,
            **({"name": self.name} if self.name else {})
        }


SUBMENU_LINK_RE = re.compile("""^/map/[^/]+/\?mapmenu=([0-9]+)$""")


def parse_submenu(li: Tag) -> Tuple[str, bool, int]:
    a = li.find('a')
    match = SUBMENU_LINK_RE.match(a.attrs['href'])
    if match is None:
        raise Exception(f"Bad link: {a}")
    return (a.text, a.attrs.get('class') == ['text-decoration_none'], int(match.group(1)))


def parse_details(details_str: str) -> MapDetails:
    details_soup = BeautifulSoup(details_str, "html.parser")
    details_table = details_soup.find('table', {"id": "mapdetails_data_table"})

    Res = NamedTuple('Res', [('tr', Tag), ('td', Tag)])

    def parse_tr(tr: Tag):
        [name, value] = tr.find_all('td')
        return (name.text, Res(tr, value))

    trs = dict(map(parse_tr, details_table.find_all('tr')))
    unknown_keys = trs.keys() - {'Author', 'Downloads', 'Mapname', 'Filename', 'Release date', 'File size', 'Game type',
                                 'Items', 'Functions', 'Bots', 'Pk3 file', 'Checksum', 'Weapons', 'Modification',
                                 'Defrag style', 'Defrag demos', 'Defrag physics', 'Defrag online records',
                                 'Difficult level', 'Map dependencies', 'Rating', 'Category'}
    if len(unknown_keys) > 0:
        raise Exception(f"Unknown key(s): {unknown_keys}")
    author_row = trs['Author']
    author_class = author_row.tr.attrs.get('class')
    if author_class is None:
        author = author_row.td.text
    elif author_class == ['map_column_none']:
        author = None
    else:
        raise Exception(f"Bad author: {author_row}")

    panorama_container = details_soup.find('div', {'id': 'panorama_container'})
    mapdetails_sub_container = details_soup.find('div', {"id": "mapdetails_sub_container"})
    topview_img_elem = mapdetails_sub_container.find('img', {"title": "Topview"})
    topview_img = topview_img_elem.attrs['src'] if topview_img_elem is not None else None
    submenu_list = details_soup.find('ul', {"id": "mapdetails_submenu_list"})
    submenu = list(map(parse_submenu, submenu_list.find_all('li'))) if submenu_list is not None else []

    return MapDetails(
        name=trs['Mapname'].td.text if 'Mapname' in trs else None,
        author=author,
        downloads=int(trs['Downloads'].td.text.replace(',', '')) if 'Downloads' in trs else None,
        map_thumbnail_url=details_soup.find('img', {'id': 'mapdetails_levelshot'}).attrs['src'],
        map_details_panorama_url=panorama_container.attrs['data-image'] if panorama_container is not None else None,
        map_details_topview_url=topview_img,
        md5=remove_prefix_strict(trs['Checksum'].td.text.strip(), 'MD5: '),
        submenu=list(map(lambda s: (s[0], s[2]), submenu)),
        submenu_position = one(list(filter(lambda x: x[1], submenu)))[2] if len(submenu) > 0 else None,
    )
