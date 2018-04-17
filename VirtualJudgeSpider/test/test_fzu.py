import unittest

from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller


class TestFZU(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('FZU').get_problem('1000', account)
        Controller('FZU').get_result(account=account, pid='1000')