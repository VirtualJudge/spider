import unittest

from spider.config import Account
from spider.core import Core


class TestFZU(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        FZU = Core('FZU')
        self.assertIsNotNone(FZU)
        FZU.get_result(account=account, pid='1039')
        FZU.get_problem(account=account, pid='1039')
