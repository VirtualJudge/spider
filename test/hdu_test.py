import unittest

from VirtualJudgeSpider.OJs.HDUClass import HDU


class TestHDU(unittest.TestCase):
    def test_homeurl(self):
        self.assertEqual(HDU.home_page_url(), 'http://acm.hdu.edu.cn/')

    def test_classname(self):
        hdu = HDU()
        self.assertEqual(hdu.get_class_name(), 'HDU')
