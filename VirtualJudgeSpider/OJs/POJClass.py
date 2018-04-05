import base64
import os
import re

import requests
import traceback
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base
from ..utils import deal_with_image_url


class POJ(Base):
    def __init__(self):
        self.code_type = 'utf-8'
        self.headers = Config.custom_headers
        self.headers['Referer'] = 'http://poj.org/'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.req = requests.Session()
        self.req.headers.update(self.headers)

    @staticmethod
    def home_page_url():
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
            self.req.get(url=login_page_url)
            res = self.req.post(url=login_link_url, data=post_data)
            if res.status_code == 200 and self.check_login_status():
                return True
            return False
        except:
            return False

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'http://poj.org/'
        try:
            res = self.req.get(url=url)
            website_data = res.text
            if re.search(r'action=logout&', website_data):
                return True
            return False
        except:
            return False

    def parse_desc(self, raw_descs):
        descList = Config.DescList()
        for raw_desc in raw_descs:
            if raw_desc.strip():
                match_groups = re.search(r'<a[\s\S]*href=\"([\s\S]*)\"[\s\S]*>([\s\S]*)</a>', raw_desc)
                if match_groups:
                    remote_path = str(match_groups.group(1))
                    if remote_path.startswith('/'):
                        remote_path = 'http://poj.org' + remote_path
                    elif not remote_path.startswith('http://') and not remote_path.startswith('https://'):
                        remote_path = 'http://poj.org/' + remote_path

                    descList.append(Config.Desc(type=Config.Desc.Type.ANCHOR, content=match_groups.group(2),
                                                origin=remote_path))
                else:
                    match_groups = re.search(r'<img([\s\S]*)src=\"([\s\S]*(gif|png|jpeg|jpg|GIF))\"', raw_desc)
                    if match_groups:
                        file_name, remote_path = deal_with_image_url(str(match_groups.group(2)),
                                                                     'http://poj.org')
                        descList.append(
                            Config.Desc(type=Config.Desc.Type.IMG,
                                        file_name=file_name,
                                        origin=remote_path))
                    else:
                        descList.append(Config.Desc(type=Config.Desc.Type.TEXT, content=raw_desc))
        print(descList.values)
        return descList.get()

    # 获取题目
    def get_problem(self, *args, **kwargs):
        url = 'http://poj.org/problem?id=' + str(kwargs['pid'])
        problem = Problem()
        try:
            res = self.req.get(url=url)
            website_data = res.text
            soup = BeautifulSoup(website_data, 'lxml')
            problem.remote_id = kwargs['pid']
            problem.remote_url = url
            problem.remote_oj = 'POJ'
            problem.title = re.search(r'ptt" lang="en-US">([\s\S]*?)</div>', website_data).group(1)
            problem.time_limit = re.search(r'(\d*MS)', website_data).group(1)
            problem.memory_limit = re.search(r'Memory Limit:</b> ([\s\S]*?)</td>', website_data).group(1)

            problem.special_judge = re.search(r'red;">Special Judge</td>', website_data) is not None

            titles = soup.find_all('p', attrs={'class': 'pst'})
            input_data = ''
            output_data = ''
            for title in titles:
                if title.string == 'Description':
                    raw_descs = []
                    for_list = title.find_next().find('span')
                    if not for_list:
                        for_list = title.find_next()
                    for child in for_list:
                        raw_descs.append(str(child))
                    problem.description = self.parse_desc(raw_descs)
                elif title.string == 'Input':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    problem.input = self.parse_desc(raw_descs)
                elif title.string == 'Output':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    problem.output = self.parse_desc(raw_descs)
                elif title.string == 'Sample Input':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    input_data = raw_descs
                elif title.string == 'Sample Output':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    output_data = raw_descs
                elif title.string == 'Hint':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    problem.hint = self.parse_desc(raw_descs)
                elif title.string == 'Source':
                    raw_descs = []
                    for child in title.find_next():
                        raw_descs.append(str(child))
                    problem.source = self.parse_desc(raw_descs)

            problem.sample = [
                {'input': input_data,
                 'output': output_data}]
            return problem
        except:
            traceback.print_exc()
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
            res = self.req.post(url=url, data=post_data)
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
    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://poj.org/status?problem_id=&result=&language=&top=' + rid
        return self.get_result_by_url(url=url)

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        result = Result()
        try:
            res = self.req.get(url=url)
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
            res = self.req.get(url=url)
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
        res = self.req.get(url)
        if re.search(r'color=blue>Welcome To PKU JudgeOnline</font>', res.text):
            return True
        return False
