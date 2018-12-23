import unittest

from spider.src.config import Account
from spider.src.core import Core


class TestWUST(unittest.TestCase):
    def test_get_problem(self):
        account = Account('robot4test', 'robot4test')
        WUST = Core('WUST')
        self.assertIsNotNone(WUST)
        problem = WUST.get_problem(account=account, pid='1039')
        self.assertIsNotNone(problem)

    def test_get_problem_with_proxies(self):
        account = Account('robot4test', 'robot4test')
        WUST = Core('WUST')
        self.assertIsNotNone(WUST)
        problem = WUST.get_problem(account=account, pid='1039')
        print(problem.__dict__)
        self.assertIsNotNone(problem)

        WUST = Core('WUST', proxies='socks5://127.0.0.1:1086')
        self.assertIsNotNone(WUST)
        problem = WUST.get_problem(account=account, pid='1039')
        print(problem.__dict__)
        self.assertIsNotNone(problem)
