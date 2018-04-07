import json
import ssl
import traceback

import requests

from VirtualJudgeSpider.Config import Problem
from VirtualJudgeSpider.OJs.BaseClass import Base

ssl._create_default_https_context = ssl._create_unverified_context


class Aizu(Base):
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}

        self.req = requests.session()
        self.req.headers.update(self.headers)

    # 主页链接
    @staticmethod
    def home_page_url():
        url = 'https://onlinejudge.u-aizu.ac.jp/'
        return url

    # 登录页面
    def login_webside(self, *args, **kwargs):
        if self.check_login_status(self, *args, **kwargs):
            return True
        login_link_url = 'https://judgeapi.u-aizu.ac.jp/session'
        account = kwargs['account']
        post_data = {
            'id': account.username,
            'password': account.password
        }
        try:
            res = self.req.post(url=login_link_url, data=json.dumps(post_data))
            if res.status_code != 200:
                return False
            if self.check_login_status(self, *args, **kwargs):
                return True
            return False
        except:
            return False

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'https://judgeapi.u-aizu.ac.jp/self'
        try:
            res = self.req.get(url)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    # 获取题目
    def get_problem(self, *args, **kwargs):
        problem = Problem()
        try:
            pid = kwargs['pid']
            url = 'https://judgeapi.u-aizu.ac.jp/resources/descriptions/en/' + str(pid)
            res = self.req.get(url)
            js = json.loads(res.text)
            print(json.dumps(js, indent=4))
            problem.time_limit = str(js.time_limit) + ' sec'
            problem.memory_limit = str(js.memory_limit) + ' KB'
            problem.description = js.html
            return problem
        except:
            traceback.print_exc()
        return None

    # 提交代码
    def submit_code(self, *args, **kwargs):
        url = 'https://judgeapi.u-aizu.ac.jp/submissions'
        try:
            problemId = kwargs['pid']
            language = kwargs['language']
            sourceCode = kwargs['code']
            res = self.req.post(url, json.dumps(
                {'problemId': str(problemId), 'language': str(language), 'sourceCode': str(sourceCode)}))
            if res.status_code == 200:
                return True
            return False
        except:
            return False

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
        return {'C': 'C', 'C++': 'C++', 'JAVA': 'JAVA', 'C++11': 'C++11', 'C++14': 'C++14', 'C#': 'C#', 'D': 'D',
                'Go': 'Go', 'Ruby': 'Ruby', 'Rust': 'Rust', 'Python': 'Python', 'Python3': 'Python3',
                'JavaScript': 'JavaScript', 'Scala': 'Scala', 'Haskell': 'Haskell', 'OCaml': 'OCaml', 'PHP': 'PHP',
                'Kotlin': 'Kotlin'}

    # 获取当前类名
    def get_class_name(self):
        return str('Aizu')

    # 判断当前提交结果的运行状态
    def is_waiting_for_judge(self, verdict):
        if verdict in [5, 9]:
            return True
        return False

    # 检查源OJ是否运行正常
    def check_status(self):
        url = 'https://judgeapi.u-aizu.ac.jp/categories'
        try:
            res = self.req.get(url)
            if res.status_code == 200:
                return True
            return False
        except:
            return False
