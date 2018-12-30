from spider.platforms.base import Base
from spider import config
from spider.utils import HttpUtil


class QDU(Base):
    def __init__(self, *args, **kwargs):
        self._headers = config.default_headers
        self._req = HttpUtil(self._headers, 'utf-8', *args, **kwargs)

    @staticmethod
    def home_page_url():
        return 'https://qduoj.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if isinstance(cookies, dict):
            self._req.cookies.update(cookies)

    def login_website(self, *args, **kwargs):
        pass

    def is_login(self, *args, **kwargs):
        pass

    def get_problem(self, *args, **kwargs):
        pass

    def submit_code(self, *args, **kwargs):
        pass

    def account_required(self):
        pass

    def get_result(self, *args, **kwargs):
        pass

    def get_result_by_rid_and_pid(self, rid, pid):
        pass

    def get_result_by_url(self, url):
        pass

    def find_language(self, *args, **kwargs):
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
