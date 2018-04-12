import unittest

from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller


class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('POJ').get_problem('1000', account)
