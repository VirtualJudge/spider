import unittest

from spider.src.config import Account
from spider.src.core import Core


class TestAizu(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Aizu = Core('Aizu')
        self.assertIsNotNone(Aizu)
        # Aizu.get_result(account=account,pid='0001')
        Aizu.get_problem(account=account, pid='0001')
