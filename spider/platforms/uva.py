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

    def login_website(self, account):
        pass

    def is_login(self):
        pass

    def get_problem(self, pid, account=None):
        url = f'https://uva.onlinejudge.org/external/{pid[0:len(pid - 2)]}/{pid}.pdf'
        pass

    def submit_code(self, account, pid, language, code):
        pass

    def account_required(self):
        return False

    def get_result(self, account, pid):
        pass

    def get_result_by_rid_and_pid(self, rid, pid):
        super().get_result_by_rid_and_pid(rid, pid)

    def get_result_by_url(self, url):
        super().get_result_by_url(url)

    def find_language(self, account):
        pass

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
