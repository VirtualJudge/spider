from spider.platforms.base import Base
from spider import config
from spider.utils import HttpUtil

import json
import traceback


class QDU(Base):
    def __init__(self, *args, **kwargs):
        self._headers = config.default_headers
        self._req = HttpUtil(self._headers, 'utf-8', *args, **kwargs)
        self._host = 'https://qduoj.com'

    @staticmethod
    def home_page_url():
        return 'https://qduoj.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if isinstance(cookies, dict):
            self._req.cookies.update(cookies)

    def login_website(self, account):
        if self.is_login():
            return True

        try:
            self._req.headers.update({'X-CSRFToken': self._req.cookies.get('csrftoken')})
            res = self._req.post(self._host + '/api/login', {
                'username': account.username,
                'password': account.password
            })
            print('res:', res)
            if res:
                print(res.text)
        except:
            traceback.print_exc()
        if self.is_login():
            return True
        return False

    def is_login(self):
        try:
            res = self._req.get(self._host + '/api/profile')
            if res and res.status_code == 200:
                res_dict = json.loads(res.text)
                if res_dict.get('data') and res_dict.get('error') is None:
                    return True
        except:
            pass
        return False

    def get_problem(self, pid, account=None):
        pass

    def submit_code(self, account, pid, language, code):
        pass

    def account_required(self):
        return False

    def get_result(self, account, pid):
        pass

    def get_result_by_rid_and_pid(self, rid, pid):
        pass

    def get_result_by_url(self, url):
        pass

    def find_language(self, account):
        pass

    def is_working(self):
        pass

    @staticmethod
    def is_accepted(verdict):
        pass

    @staticmethod
    def is_compile_error(verdict):
        pass

    @staticmethod
    def is_running(verdict):
        pass


if __name__ == '__main__':
    qdu = QDU()
    account = config.Account('robot4spider', 'robot4spider')
    print(qdu.login_website(account=account))
    print(qdu.is_login())
