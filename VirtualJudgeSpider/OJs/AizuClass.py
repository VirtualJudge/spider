import bs4
import re
import ssl
import requests
from http import cookiejar
from urllib import request, parse
from VirtualJudgeSpider import Config

ssl._create_default_https_context = ssl._create_unverified_context


class Aizu:
    def __init__(self):
        self.code_type = 'UTF-8'
        self.cj = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))
        self.cookies = None
        self.headers = Config.custom_headers

    # 主页链接
    @staticmethod
    def home_page_url(self):
        url = 'http://judge.u-aizu.ac.jp/onlinejudge/'
        return url

    # 登录页面
    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://judge.u-aizu.ac.jp/onlinejudge/signin.jsp'
        login_link_url = 'https://judgeapi.u-aizu.ac.jp/session'

        post_data = {'id': kwargs['account'].get_username(), 'password': kwargs['account'].get_password()}
        try:
            res1 = requests.get(login_page_url, cookies=self.cookies, headers=self.headers)
            self.cookies = res1.cookies
            res2 = requests.options(login_link_url, cookies=self.cookies, headers=self.headers)
            self.cookies = res2.cookies
            res3 = requests.post(login_link_url, data=post_data, cookies=self.cookies, headers=self.headers)
            print(res3.text)
            if self.check_login_status():
                return True
            return False
        except Exception as e:

            return False

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'http://judge.u-aizu.ac.jp/onlinejudge/'
        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers)
            website_data = response.text
            if re.search(r'<a href="user.jsp?id=" id="status">My Status</a>', website_data) is not None:
                return True
            return False
        except:
            return False


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
def get_result_by_rid(self, rid):
    pass


# 根据源OJ的url获取结果
def get_result_by_url(self, url):
    pass


# 获取源OJ支持的语言类型
def find_language(self, *args, **kwargs):
    pass


# 获取当前类名
def get_class_name(self):
    pass


# 判断当前提交结果的运行状态
def is_waiting_for_judge(self, verdict):
    pass


# 检查源OJ是否运行正常
def check_status(self):
    pass
