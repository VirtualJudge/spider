import unittest

from spider.config import Account
from spider.core import Core


class TestZOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        ZOJ = Core('ZOJ')
        self.assertIsNotNone(ZOJ)
        ZOJ.get_result(account=account, pid='1039')
        ZOJ.get_problem(account=account, pid='1039')
