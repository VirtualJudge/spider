import unittest

from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller


class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('ZOJ').get_problem(pid='1001', account=account)
        Controller('ZOJ').get_result(account=account,pid='1039')
