import unittest

from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller


class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('WUST').get_problem('1000', account)
        Controller('WUST').get_result(account=account, pid='1000')