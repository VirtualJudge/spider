from VirtualJudgeSpider.OJs.base import Base, BaseParser

from VirtualJudgeSpider.utils import HttpUtil


class CodeforcesParser(BaseParser):
    def problem_parse(self, response, pid, url):
        pass

    def result_parse(self, response):
        pass


class Codeforces(Base):
    def __init__(self, cookies=None):
        self._headers = {'Content-Type': 'application/json'}

        self._req = HttpUtil(custom_headers=self._headers)

    # 主页链接
    @staticmethod
    def home_page_url():
        return 'http://codeforces.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if type(cookies) == dict:
            self._req.cookies.update(cookies)

    # 登录页面
    def login_website(self,account, *args, **kwargs):
        pass

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        pass

    # 获取题目
    def get_problem(self, *args, **kwargs):
        pass

    # 提交代码
    def submit_code(self, *args, **kwargs):
        pass

    # 获取当然运行结果
    def get_result(self, *args, **kwargs):
        pass

    # 根据源OJ的运行id获取结构
    def get_result_by_rid_and_pid(self, rid, pid):
        pass

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        pass

    # 获取源OJ支持的语言类型
    def find_language(self, *args, **kwargs):
        pass

    # 检查源OJ是否运行正常
    def check_status(self):
        pass

    #  判断结果是否正确
    @staticmethod
    def is_accepted(verdict):
        return verdict == 'Accepted'

    # 判断是否编译错误
    @staticmethod
    def is_compile_error(verdict):
        return verdict == 'Compilation error'

    # 判断是否运行中
    @staticmethod
    def is_running(verdict):
        return str(verdict).startswith('running on test')
