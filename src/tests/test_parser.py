import datetime
import os
from os.path import dirname
from unittest import TestCase

from ws.parser import parse_details


def get_page(name):
    with open(os.path.join(dirname(__file__), "test_parser", name)) as f:
        return parse_details(f.read())


class WsScrapeTest(TestCase):

    def test_kakawki_scptnuo(self):
        page = get_page('kakawki-scptnuo')
        self.assertIsNone(page.author)
        self.assertEqual(page.downloads, 84)
        self.assertEqual(page.map_thumbnail_url, '/images/levelshots/512x384/kakawki-scptnuo.jpg')
        self.assertIsNone(page.map_details_panorama_url)
        self.assertIsNone(page.map_details_topview_url)
        self.assertEqual(page.md5, '0c9d584b27671bec4c70384624eda263')
        self.assertEqual(page.submenu, [])
        self.assertIsNone(page.submenu_position)
        self.assertEqual(page.submenu_others, [])

    def test_dm_13v2(self):
        page = get_page('dm_13v2')
        self.assertEqual(page.author, "DM_")
        self.assertEqual(page.downloads, 87)
        self.assertEqual(page.map_thumbnail_url, '/images/levelshots/512x384/dm_13v2.jpg')
        self.assertIsNone(page.map_details_panorama_url)
        self.assertIsNone(page.map_details_topview_url)
        self.assertEqual(page.md5, '6202d0df8433555d9fd174f0f00250ea')
        self.assertEqual(page.submenu, [])
        self.assertIsNone(page.submenu_position)
        self.assertEqual(page.submenu_others, [])

    def test_mcjump(self):
        page = get_page('mcjump')
        self.assertEqual(page.author, "KittenIgnition")
        self.assertEqual(page.downloads, 231)
        self.assertEqual(page.map_thumbnail_url, '/images/levelshots/512x384/mcjump.jpg')
        self.assertIsNone(page.map_details_panorama_url)
        self.assertEqual(page.map_details_topview_url, '/images/topviews/512x384/mcjump.jpg')
        self.assertEqual(page.md5, 'c74e8e4b8dde73bcb1fb8183ee41f069')
        self.assertEqual(page.submenu, [])
        self.assertIsNone(page.submenu_position)
        self.assertEqual(page.submenu_others, [])

    def test_q3dm2(self):
        page = get_page('q3dm2')
        self.assertEqual(page.author, 'Id Software, Inc.')
        self.assertIsNone(page.downloads)
        self.assertEqual(page.map_thumbnail_url, '/images/levelshots/512x384/q3dm2.jpg')
        self.assertIsNone(page.map_details_panorama_url)
        self.assertEqual(page.map_details_topview_url, '/images/topviews/512x384/q3dm2.jpg')
        self.assertEqual(page.md5, '1197ca3df1e65f3c380f8abc10ca43bf')
        self.assertEqual(page.submenu, [('Topview', 0), ('Panorama', 1)])
        self.assertEqual(page.submenu_position, 0)
        self.assertEqual(page.submenu_others, [('Panorama', 1)])

    def test_q3dm2_panorama(self):
        page = get_page('q3dm2-panorama')
        self.assertEqual(page.author, 'Id Software, Inc.')
        self.assertIsNone(page.downloads)
        self.assertEqual(page.map_thumbnail_url, '/images/levelshots/512x384/q3dm2.jpg')
        self.assertEqual(page.map_details_panorama_url, '/images/panoramas/q3dm2.jpg')
        self.assertIsNone(page.map_details_topview_url)
        self.assertEqual(page.md5, '1197ca3df1e65f3c380f8abc10ca43bf')
        self.assertEqual(page.submenu, [('Topview', 0), ('Panorama', 1)])
        self.assertEqual(page.submenu_position, 1)
        self.assertEqual(page.submenu_others, [('Topview', 0)])
