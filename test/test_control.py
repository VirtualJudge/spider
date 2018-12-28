import unittest

from spider.platforms.hdu import HDU
from spider.core import Core, OJBuilder


class TestOJBuilder(unittest.TestCase):
    def test_build_oj(self):
        self.assertEqual(type(OJBuilder.build_oj('HDU')), HDU)
        self.assertIsNone(OJBuilder.build_oj('THISOJISNONE'))

    def test_all_support(self):
        for item in Core.get_supports():
            try:
                self.assertTrue(Core(item).is_working(), msg=f'{item} error')
            except Exception as e:
                print(e)
