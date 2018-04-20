import unittest

from VirtualJudgeSpider.config import Account
from VirtualJudgeSpider.control import Controller


class TestFZU(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        FZU = Controller('FZU')
        FZU.get_result(account=account, pid='1039')
        FZU.get_problem(account=account, pid='1039')
