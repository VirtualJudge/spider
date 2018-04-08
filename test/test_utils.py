import unittest

from VirtualJudgeSpider.Utils import deal_with_image_url


class TestUtils(unittest.TestCase):
    def test_deal_with_image_url(self):
        self.assertEqual(deal_with_image_url('http://acm.wust.edu.cn/image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'http://acm.wust.edu.cn/image/1121-1.png'))
        self.assertEqual(deal_with_image_url('/image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(deal_with_image_url('image/1121-1.png', 'https://prefixai.com'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(deal_with_image_url('image/1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(deal_with_image_url('/image/1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/image/1121-1.png'))
        self.assertEqual(deal_with_image_url('1121-1.png', 'https://prefixai.com/'),
                         ('1121-1.png', 'https://prefixai.com/1121-1.png'))
