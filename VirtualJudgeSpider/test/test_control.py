import unittest

from VirtualJudgeSpider.Control import OJBuilder
from VirtualJudgeSpider.OJs.hdu import HDU


class TestOJBuilder(unittest.TestCase):
    def test_build_oj(self):
        self.assertEqual(type(OJBuilder.build_oj('HDU')), HDU)
        self.assertIsNone(OJBuilder.build_oj('WUSTOJ'))
