import unittest

from spider.config import Account
from spider.core import Core


class TestHDU(unittest.TestCase):
    def test_hdu(self):
        oj = Core('HDU')
        account = Account('robot4test', 'robot4test')
        code = """
        #include <iostream>

        int main(){
            std::cout << "Hello World!" << std::endl;
            return 0;
        }
                """
        self.assertIsNotNone(oj)
        oj.get_problem(account=account, pid='1001')
        self.assertTrue(oj.is_account_valid(account))
        self.assertIsNotNone(oj.get_home_page_url())
        self.assertIsNotNone(oj.get_cookies())
        self.assertFalse(oj.account_required())
        self.assertIsNotNone(oj.submit_code(pid=1001, account=account, language='C++', code=code))
        self.assertIsNotNone(oj.get_result(account=account, pid=1001))
        self.assertIsNotNone(oj.find_language(account))
        self.assertTrue(oj.is_working())
