import base64
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from spider import config
from spider.platforms.base import Base, BaseParser
from spider.config import Problem, Result
from spider.utils import HttpUtil, HtmlTag
from spider.exceptions import *
from spider.config import Account
import time


class POJParser(BaseParser):
    def __init__(self, *args, **kwargs):
        self._static_prefix = 'http://poj.org/'

    def problem_parse(self, response, pid, url):
        problem = Problem()

        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'POJ'
        if response is None:
            raise SpiderNetworkError("")
        website_data = response.text
        status_code = response.status_code
        if status_code != 200:
            raise SpiderNetworkError("")
        if re.search('Can not find problem', website_data):
            raise SpiderNetworkError("")
        soup = BeautifulSoup(website_data, 'lxml')

        match_groups = re.search(r'ptt" lang="en-US">([\s\S]*?)</div>', website_data)
        if match_groups:
            problem.title = match_groups.group(1)
        match_groups = re.search(r'(\d*MS)', website_data)
        if match_groups:
            problem.time_limit = match_groups.group(1)
        match_groups = re.search(r'Memory Limit:</b> ([\s\S]*?)</td>', website_data)
        if match_groups:
            problem.memory_limit = match_groups.group(1)
        problem.special_judge = re.search(r'red;">Special Judge</td>', website_data) is not None
        problem.html = ''
        for tag in soup.find('div', attrs={'class': 'ptt'}).next_siblings:
            if type(tag) == Tag and set(tag.get('class')).intersection({'ptx', 'pst', 'sio'}):
                if set(tag['class']).intersection({'pst', }):
                    tag['style'] = HtmlTag.TagStyle.TITLE.value

                    tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                else:
                    tag['style'] = HtmlTag.TagStyle.CONTENT.value
                    tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                problem.html += str(HtmlTag.update_tag(tag, self._static_prefix))
        return problem

    def result_parse(self, response):
        result = Result()
        if response is None or response.status_code != 200:
            raise SpiderNetworkError("")
        soup = BeautifulSoup(response.text, 'lxml')
        line = soup.find('table', attrs={'class': 'a'}).find('tr', attrs={'align': 'center'}).find_all('td')
        if line is None:
            raise SpiderProblemParseError("Parse Error")
        result.unique_key = line[0].string
        result.verdict_info = line[3].string
        result.execute_time = line[5].string
        result.execute_memory = line[4].string
        return result


class POJ(Base):
    def __init__(self, account: Account, *args, **kwargs):
        super().__init__(account, *args, **kwargs)
        self.code_type = 'utf-8'
        self._headers = config.default_headers
        self._headers['Referer'] = 'http://poj.org/'
        self._headers['Content-Type'] = 'application/x-www-form-urlencoded'

        self._req = HttpUtil(headers=self._headers, code_type=self.code_type, *args, **kwargs)
        if self.account.cookies:
            self._req.cookies.update(self.account.cookies)

    # 登录页面
    def login_website(self):
        if self.is_login():
            return True
        login_page_url = 'http://poj.org/'
        login_link_url = 'http://poj.org/login'
        post_data = {'user_id1': self.account.username,
                     'password1': self.account.password,
                     'B1': 'login',
                     'url': '/'}
        self._req.get(url=login_page_url)
        self._req.post(url=login_link_url, data=post_data)
        return self.is_login()

    # 检查登录状态
    def is_login(self):
        url = 'http://poj.org/'
        res = self._req.get(url=url)
        if res and re.search(r'action=logout&', res.text):
            self.account.set_cookies(self._req.cookies.get_dict())
            return True
        return False

    # 获取题目
    def get_problem(self, pid):
        url = f'http://poj.org/problem?id={pid}'
        res = self._req.get(url=url)
        return POJParser().problem_parse(res, pid, url)

    # 提交代码
    def submit_code(self, pid, language, code):
        if not self.login_website():
            raise SpiderAccountLoginError()
        url = 'http://poj.org/submit'
        if type(code) is str:
            code = bytes(code, encoding='utf-8')
        post_data = {'problem_id': pid,
                     'language': language,
                     'source': base64.b64encode(code),
                     'submit': 'Submit',
                     'encoded': '1'}
        self._req.post(url=url, data=post_data)
        while True:
            time.sleep(1)
            status_url = f'http://poj.org/status?problem_id={pid}&result=&language=&top=&user_id={self.account.username}'
            result = POJParser().result_parse(self._req.get(status_url))
            if str(result.verdict_info) not in ['Queuing', 'Compiling', 'Waiting', 'Running & Judging']:
                break
        if str(result.verdict_info) == 'Accepted':
            result.verdict = Result.Verdict.VERDICT_AC
        elif str(result.verdict_info) == 'Compile Error':
            result.verdict = Result.Verdict.VERDICT_CE
        else:
            result.verdict = Result.Verdict.VERDICT_WA
        result.execute_time = str(result.execute_time).strip()
        result.execute_memory = str(result.execute_memory).strip()
        return result

    # 检查源OJ是否运行正常
    def is_working(self):
        url = "http://poj.org/"
        res = self._req.get(url)
        if res and re.search(r'color=blue>Welcome To PKU JudgeOnline</font>', res.text):
            return True
        return False
