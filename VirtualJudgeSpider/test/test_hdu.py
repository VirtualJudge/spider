import unittest

from VirtualJudgeSpider.OJs.hdu import HDU
from VirtualJudgeSpider.control import Controller
from VirtualJudgeSpider.config import Account


class TestHDU(unittest.TestCase):
    def test_homeurl(self):
        self.assertEqual(Controller('HDU').get_home_page_url(), 'http://acm.hdu.edu.cn/')

    def test_get_problem(self):
        hdu = Controller('HDU')
        account = Account('robot4test', 'robot4test')
        self.assertIsNotNone(hdu)
        hdu.get_problem(account=account, pid='1001')

    def test_classname(self):
        hdu = HDU()
        self.assertEqual(hdu.__class__.__name__, 'HDU')
