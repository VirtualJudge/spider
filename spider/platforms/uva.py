from spider.platforms.base import Base


class UVA(Base):
    def __init__(self):
        pass

    @staticmethod
    def home_page_url():
        super().home_page_url()

    def get_cookies(self):
        super().get_cookies()

    def set_cookies(self, cookies):
        super().set_cookies(cookies)

    def login_website(self, *args, **kwargs):
        super().login_website(*args, **kwargs)

    def is_login(self, *args, **kwargs):
        super().is_login(*args, **kwargs)

    def get_problem(self, *args, **kwargs):
        pid = kwargs.get('pid')
        url = f'https://uva.onlinejudge.org/external/{pid[0:len(pid - 2)]}/{pid}.pdf'

    def submit_code(self, *args, **kwargs):
        super().submit_code(*args, **kwargs)

    def account_required(self):
        return False

    def get_result(self, *args, **kwargs):
        super().get_result(*args, **kwargs)

    def get_result_by_rid_and_pid(self, rid, pid):
        super().get_result_by_rid_and_pid(rid, pid)

    def get_result_by_url(self, url):
        super().get_result_by_url(url)

    def find_language(self, *args, **kwargs):
        super().find_language(*args, **kwargs)

    def is_working(self):
        super().is_working()

    @staticmethod
    def is_accepted(verdict):
        super().is_accepted(verdict)

    @staticmethod
    def is_compile_error(verdict):
        super().is_compile_error(verdict)

    @staticmethod
    def is_running(verdict):
        super().is_running(verdict)
