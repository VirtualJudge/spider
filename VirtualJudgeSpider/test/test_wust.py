import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestWUST(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        WUST=Controller('WUST')
        WUST.get_result(account=account,pid='1039')
        WUST.get_problem(account=account,pid='1039')