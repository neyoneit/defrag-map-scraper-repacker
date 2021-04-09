from decimal import Decimal
from unittest import TestCase

from utils import time_to_decimal


class TestTimeToDecimal(TestCase):

    def test_time_without_minutes(self):
        self.assertEqual(time_to_decimal("1:234"), Decimal("1.234"))


    def test_time_with_minutes(self):
        self.assertEqual(time_to_decimal("1:1:234"), Decimal("61.234"))
        self.assertEqual(time_to_decimal("2:1:234"), Decimal("121.234"))
