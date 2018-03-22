import ssl
import requests
import re
from VirtualJudgeSpider import Config

ssl._create_default_https_context = ssl._create_unverified_context


class Aizu:
    def __init__(self):
        self.code_type = 'UTF-8'
        self.cookies = None
        self.headers = Config.custom_headers

    # 主页链接
    @staticmethod
    def home_page_url(self):
        url = 'http://judge.u-aizu.ac.jp/onlinejudge/'
        return url

    # 登录页面
    def login_webside(self, *args, **kwargs):
        login_page_url = 'http://judge.u-aizu.ac.jp/onlinejudge/signin.jsp'
        login_link_url = 'https://judge.u-aizu.ac.jp/session'
        res1 = requests.get(url=login_page_url, headers=self.headers, cookies=self.cookies)
        self.cookies = res1.cookies
        account = kwargs['account']
        post_data = {
            'id': account.username,
            'password': account.password
        }
        print(post_data)
        res2 = requests.options(login_link_url, headers=self.headers, cookies=self.cookies, verify=False)
        res3 = requests.post(url=login_link_url, data=post_data, headers=self.headers, cookies=self.cookies,
                             verify=False)
        print(res3.text)
        pass

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'http://acm.hdu.edu.cn/'
        try:
            website_data = requests.get(url, cookies=self.cookies, headers=self.headers)
            if re.search(r'userloginex\.php\?action=logout', website_data.text) is not None:
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
