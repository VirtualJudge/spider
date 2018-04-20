import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestWUST(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('WUST').get_problem('1000', account)
        Controller('WUST').get_result(account=account, pid='1000')
