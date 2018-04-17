import unittest

from VirtualJudgeSpider.OJs.hdu import HDU
from VirtualJudgeSpider.control import Controller


class TestHDU(unittest.TestCase):
    def test_homeurl(self):
        self.assertEqual(Controller('HDU').get_home_page_url(), 'http://acm.hdu.edu.cn/')

    def test_classname(self):
        hdu = HDU()
        self.assertEqual(hdu.__class__.__name__, 'HDU')
