import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestAizu(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Aizu = Controller('Aizu')
        # Aizu.get_result(account=account,pid='0001')
        Aizu.get_problem(account=account, pid='0001')
