import unittest

from VirtualJudgeSpider.Control import Controller
from VirtualJudgeSpider.Config import Account
import os
import json

class TestPOJ(unittest.TestCase):
    def test_get_problem(self):
        Controller('POJ').get_problem('1000',)