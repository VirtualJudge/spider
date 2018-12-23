import unittest

from src.config import Account
from src.core import Core


class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        POJ = Core('POJ')
        self.assertIsNotNone(POJ)
        POJ.get_result(account=account, pid='1379')
        POJ.get_problem(account=account, pid='1379')
