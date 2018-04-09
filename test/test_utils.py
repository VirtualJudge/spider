import unittest

from VirtualJudgeSpider.Utils import HttpUtil


class TestUtils(unittest.TestCase):
    def test_deal_with_image_url(self):
        self.assertEqual(HttpUtil.abs_url('http://acm.wust.edu.cn/image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'http://acm.wust.edu.cn/image/1121-1.png'))
        self.assertEqual(HttpUtil.abs_url('/image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(HttpUtil.abs_url('image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(HttpUtil.abs_url('image/1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(HttpUtil.abs_url('/image/1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(HttpUtil.abs_url('1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/1121-1.png'))
