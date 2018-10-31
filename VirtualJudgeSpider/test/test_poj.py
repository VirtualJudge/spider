import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        POJ = Controller('POJ')
        POJ.get_result(account=account, pid='1379')
        POJ.get_problem(account=account, pid='1379')
