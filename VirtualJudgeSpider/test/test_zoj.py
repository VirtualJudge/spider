import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestZOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        ZOJ=Controller('ZOJ')
        ZOJ.get_result(account=account,pid='1039')
        ZOJ.get_problem(account=account,pid='1039')

