import re

import requests

from VirtualJudgeSpider import config
from VirtualJudgeSpider.OJs.base import Base
from VirtualJudgeSpider.config import Problem


class hihoCoder(Base):
    def __init__(self):
        self.req = requests.session()
        self.headers = config.custom_headers

    # 主页链接
    @staticmethod
    def home_page_url():
        url = 'https://hihocoder.com/'
        return url

    # 登录页面
    def login_website(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'https://hihocoder.com/login'
        login_link_url = 'https://hihocoder.com/api/User/login.json'
        self.req.get(login_page_url)
        post_data = {'email': kwargs['account'].get_username(), 'passwd': kwargs['account'].get_password()}
        res = self.req.post(login_link_url, post_data)
        if res is None or res.status_code != 200:
            return False
        if self.check_login_status():
            return True
        return False

    # 检查登录状态
    def check_login_status(self):
        url = 'https://hihocoder.com'
        res = self.req.get(url=url)
        if res is None:
            return False
        website_data = res.text
        if re.search(r'api.logout\(\);', website_data):
            return True
        return False

    # 获取题目
    def get_problem(self, pid, *args, **kwargs):
        url = 'https://hihocoder.com/problemset/problem/' + str(kwargs['pid'])
        problem = Problem()
        if not self.login_website(*args, **kwargs):
            return None
        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'hihoCoder'

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

    def is_compile_error(verdict):
        pass

    def is_accepted(verdict):
        pass

    def is_running(verdict):
        pass
