import base64
import re

import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base


class POJ(Base):
    def __init__(self):
        self.code_type = 'utf-8'
        self.cookies = None
        self.headers = Config.custom_headers
        self.headers['Referer'] = 'http://poj.org/'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    @staticmethod
    def home_page_url(self):
        url = 'http://poj.org/'
        return url

    # 登录页面
    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://poj.org/'
        login_link_url = 'http://poj.org/login'
        post_data = {'user_id1': kwargs['account'].get_username(),
                     'password1': kwargs['account'].get_password(),
                     'B1': 'login',
                     'url': '/'}
        try:
            res1 = requests.get(url=login_page_url, data=post_data, headers=self.headers, cookies=self.cookies)
            self.cookies = res1.cookies
            res2 = requests.post(url=login_link_url, data=post_data, headers=self.headers, cookies=res1.cookies)
            if res2.status_code == 200 and self.check_login_status():
                return True
            return False
        except:
            return False

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'http://poj.org/'
        try:
            res = requests.get(url=url, headers=self.headers, cookies=self.cookies)
            website_data = res.text
            if re.search(r'action=logout&', website_data):
                return True
            return False
        except:
            return False

    # 获取题目
    def get_problem(self, *args, **kwargs):
        url = 'http://poj.org/problem?id=' + str(kwargs['pid'])
        problem = Problem()
        try:
            res = requests.get(url=url, headers=self.headers, cookies=self.cookies)
            website_data = res.text
            problem.remote_id = kwargs['pid']
            problem.remote_url = url
            problem.remote_oj = 'POJ'
            problem.title = re.search(r'ptt" lang="en-US">([\s\S]*?)</div>', website_data).group(1)
            problem.time_limit = re.search(r'(\d*MS)', website_data).group(1)
            problem.memory_limit = re.search(r'Memory Limit:</b> ([\s\S]*?)</td>', website_data).group(1)

            problem.special_judge = re.search(r'red;">Special Judge</td>', website_data) is not None
            problem.description = re.search(r'>Description</p>[\s\S]*?lang="en-US">([\s\S]*?)</div>',
                                            website_data).group(1)  #
            problem.input = re.search(r'>Input</p>[\s\S]*?lang="en-US">([\s\S]*?)</div>', website_data).group(1)
            problem.output = re.search(r'>Output</p>[\s\S]*?lang="en-US">([\s\S]*?)</div>', website_data).group(1)
            match_group = re.search(r'>Sample Input</p>([\s\S]*?)<p class', website_data)
            input_data = ''
            if match_group:
                input_data = re.search('"sio">([\s\S]*?)</pre>', match_group.group(1)).group(1)

            output_data = ''
            match_group = re.search(r'>Sample Output</p>([\s\S]*?)<p class', website_data)
            if match_group:
                output_data = re.search('"sio">([\s\S]*?)</pre>', match_group.group(1)).group(1)
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]
            # match_group = re.search(r'>Author</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data)
            # if match_group:
            #    problem.author = match_group.group(1)

            match_group = re.search(r'>Hint</p>[\s\S]*?"en-US">([\s\S]*?)</div>', website_data)
            if match_group:
                problem.hint = match_group.group(1)
            match_group = re.search(r'>Source</p>[\s\S]*?"en-US">([\s\S]*?)</div>', website_data)
            if match_group:
                problem.source = match_group.group(1)
            return problem
        except:
            pass
        return None

    # 提交代码
    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            url = 'http://poj.org/submit'
            post_data = {'problem_id': pid,
                         'language': language,
                         'source': base64.b64encode(str.encode(code)),
                         'submit': 'Submit',
                         'encoded': '1'}
            res = requests.post(url=url, data=post_data, headers=self.headers, cookies=self.cookies)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    # 获取当然运行结果
    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://poj.org/status?problem_id=' + pid + '&result=&language=&top=&user_id=' + account.username
        return self.get_result_by_url(url=url)

    # 根据源OJ的运行id获取结构
    def get_result_by_rid(self, rid):
        url = 'http://poj.org/status?problem_id=&result=&language=&top=' + rid
        return self.get_result_by_url(url=url)

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        result = Result()
        try:
            res = requests.get(url=url, headers=self.headers, cookies=self.cookies)
            soup = BeautifulSoup(res.text, 'lxml')
            line = soup.find('table', attrs={'class': 'a'}).find('tr', attrs={'align': 'center'}).find_all('td')
            if line is not None:
                result.origin_run_id = line[0].string
                result.verdict = line[3].string
                result.execute_time = line[5].string
                result.execute_memory = line[4].string
                return result
        except:
            pass
        return None

    # 获取源OJ支持的语言类型
    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://poj.org/submit'
        language = {}
        try:
            res = requests.get(url=url, headers=self.headers, cookies=self.cookies)
            soup = BeautifulSoup(res.text, 'lxml')
            options = soup.find('select', attrs={'name': 'language'}).find_all('option')
            for option in options:
                language[option.get('value')] = option.string
        finally:
            return language

    # 获取当前类名
    def get_class_name(self):
        return str('POJ')

    # 判断当前提交结果的运行状态
    def is_waiting_for_judge(self, verdict):
        if verdict == 'Queuing' or verdict == 'Compiling':
            return True
        return False

    # 检查源OJ是否运行正常
    def check_status(self):
        url = "http://poj.org/"
        res = requests.get(url, headers=self.headers, cookies=self.cookies)
        if re.search(r'color=blue>Welcome To PKU JudgeOnline</font>', res.text):
            return True
        return False
