import unittest

from spider.core import OJBuilder
from spider.platforms.hdu import HDU


class TestOJBuilder(unittest.TestCase):
    def test_build_oj(self):
        self.assertEqual(type(OJBuilder.build_oj('HDU')), HDU)
        self.assertIsNone(OJBuilder.build_oj('THISOJISNONE'))
