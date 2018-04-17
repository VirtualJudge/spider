import unittest

from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller


class TestAizu(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        Controller('Aizu').get_problem('0001', account)
        
