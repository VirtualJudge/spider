import unittest

from spider.src.platforms import HDU
from spider.src.core import Core
from spider.src.config import Account


class TestHDU(unittest.TestCase):
    def test_homeurl(self):
        self.assertEqual(Core('HDU').get_home_page_url(), 'http://acm.hdu.edu.cn/')

    def test_get_problem(self):
        hdu = Core('HDU')
        account = Account('robot4test', 'robot4test')
        self.assertIsNotNone(hdu)
        hdu.get_problem(account=account, pid='1001')

    def test_classname(self):
        hdu = HDU()
        self.assertEqual(hdu.__class__.__name__, 'HDU')
