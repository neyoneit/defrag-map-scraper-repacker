import datetime
import os
from os.path import dirname
from unittest import TestCase

from bs4 import BeautifulSoup

from ws_scrape_once import find_rows


def get_page(name):
    with open(os.path.join(dirname(__file__), "test_ws_scrape", name)) as f:
        return BeautifulSoup(f.read(), "html.parser")


class WsScrapeTest(TestCase):

    page = get_page("page-0-show-50")
    rows = list(find_rows(page, 50))

    def test_len(self):
        self.assertEqual(len(self.rows), 50)

    def test_first_row_date(self):
        self.assertEqual(self.rows[0].release_date, datetime.date(2020, 12, 11))

    def test_first_row_name(self):
        self.assertEqual(self.rows[0].name, "spr-adr")

    def test_first_row_link(self):
        self.assertEqual(self.rows[0].link, "/map/spr-adr/")

    def test_first_row_pk3_file(self):
        self.assertEqual(self.rows[0].pk3_file, "spr-adr")
        self.assertEqual(self.rows[0].pk3_file_has_link, True)

    def test_first_row_size_str(self):
        self.assertEqual(self.rows[0].size_str, "2.45 MB")

    def test_first_row_mods(self):
        self.assertEqual(self.rows[0].mods, ["defrag"])

    def test_first_row_games_type(self):
        self.assertEqual(self.rows[0].game_types, ['vq3', 'cpm'])

    def test_first_row_weapons(self):
        self.assertEqual(self.rows[0].weapons, [])

    def test_first_row_items(self):
        self.assertEqual(self.rows[0].items, [])

    def test_first_row_functions(self):
        self.assertEqual(self.rows[0].functions, ['door', 'timer'])

    def test_baulo7(self):
        relevant = list(filter(lambda row: row.pk3_file == '64K_mappack', self.rows))
        self.assertEqual(len(relevant), 5)
        self.assertTrue(relevant[0].pk3_file_has_link)
        self.assertEqual(len(list(filter(lambda row: row.pk3_file_has_link, relevant))), 1)

    def test_assertions_on_tricky_page_168(self):
        self.assertEqual(len(list(find_rows(get_page('page-168-show-50'), 50))), 50)

    def test_assertions_on_tricky_page_183(self):
        self.assertEqual(len(list(find_rows(get_page('page-183-show-50'), 50))), 50)

    def test_page_1_tricky_game_type(self):
        rows = list(find_rows(get_page('page-1-show-50'), 50))
        self.assertEqual(rows[4].game_types, ['ctf', 'ffa', 'trn'])
        self.assertEqual(rows[5].game_types, ['ctf'])
