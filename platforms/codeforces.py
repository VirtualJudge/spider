import re
import time

from bs4 import BeautifulSoup
from bs4 import element

from utils.config import Problem, Result, Account
from platforms.base import Base, BaseParser
from utils.config import HtmlTag, HttpUtil, logger
from utils.exceptions import *


class CodeforcesParser(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://codeforces.com/'
        self._script = """
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
 showProcessingMessages: true,
 messageStyle: "none",
 extensions: ["tex2jax.js"],
 jax: ["input/TeX", "output/HTML-CSS"],
 tex2jax: {
     inlineMath:  [ ["$$$", "$$$"] ],
     displayMath: [ ["$$$$$$","$$$$$$"] ],
     skipTags: ['script', 'noscript', 'style', 'textarea', 'pre','code','a']
 },
 "HTML-CSS": {
     availableFonts: ["STIX","TeX"],
     showMathMenu: false
 }
});
</script>
<script src="https://cdn.bootcss.com/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML-full" async></script>
"""

    def problem_parse(self, response, pid, url):
        problem = Problem()
        problem.remote_oj = 'Codeforces'
        problem.remote_id = pid
        problem.remote_url = url
        if response is None:
            raise SpiderNetworkError('Network Error')
        elif response.status_code == 302:
            raise SpiderNetworkError('Network Error')
        elif response.status_code != 200:
            raise SpiderNetworkError('Network Error')
        elif response.text is None:
            raise SpiderNetworkError('Network Error')
        website = response.text
        soup = BeautifulSoup(website, 'lxml')
        match_groups = soup.find('div', attrs={'class': 'title'})
        if match_groups:
            problem.title = match_groups.string
            problem.title = str(problem.title)[2:]
        match_groups = soup.find(name='div', attrs={'class': 'time-limit'})
        if match_groups:
            problem.time_limit = match_groups.contents[-1]
        match_groups = soup.find(name='div', attrs={'class': 'memory-limit'})
        if match_groups:
            problem.memory_limit = match_groups.contents[-1]
        match_groups = soup.find(name='div', attrs={'class': 'problem-statement'})
        problem.html = ''
        if match_groups and isinstance(match_groups, element.Tag):
            for child in match_groups.children:
                if isinstance(child, element.Tag) and child.get('class') and set(child['class']).intersection(
                        {'header'}):
                    pass
                elif isinstance(child, element.Tag):
                    for tag in child:
                        if isinstance(tag, element.Tag):
                            if tag.get('class') is None:
                                tag['class'] = ()
                            if tag.get('class') and set(tag['class']).intersection({'section-title'}):
                                tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                                tag['style'] = HtmlTag.TagStyle.TITLE.value
                            else:
                                tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                                tag['style'] = HtmlTag.TagStyle.CONTENT.value
                    problem.html += str(HtmlTag.update_tag(child, self._static_prefix))
                else:
                    problem.html += str(HtmlTag.update_tag(child, self._static_prefix))
        problem.html = '<html>' + problem.html + self._script + '</html>'
        return problem

    def result_parse(self, response):
        if response is None or response.status_code != 200 or response.text is None:
            raise SpiderNetworkError("Network error")
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table')
        tag = None
        if table:
            tag = table.find_all('tr')
        if tag:
            children_tag = tag[-1].find_all('td')
            if len(children_tag) > 9:
                result = Result()
                result.unique_key = children_tag[0].string
                result.verdict_info = ''
                for item in children_tag[4].stripped_strings:
                    result.verdict_info += str(item) + ' '
                result.verdict_info = result.verdict_info.strip(' ')
                result.execute_time = children_tag[5].string
                result.execute_memory = children_tag[6].string
                return result
        else:
            raise SpiderException('Parse Result Error')


class Codeforces(Base):
    def __init__(self, account: Account, *args, **kwargs):
        super().__init__(account, *args, **kwargs)
        self._req = HttpUtil(*args, **kwargs)

    # 主页链接
    @staticmethod
    def home_page_url():
        return 'https://codeforces.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if isinstance(cookies, dict):
            self._req.cookies.update(cookies)

    # 登录页面
    def login_website(self):
        if self.is_login():
            return True
        try:
            res = self._req.get('https://codeforces.com/enter?back=%2F')

            soup = BeautifulSoup(res.text, 'lxml')
            csrf_token = soup.find(attrs={'name': 'X-Csrf-Token'}).get('content')
            post_data = {
                'csrf_token': csrf_token,
                'action': 'enter',
                'ftaa': '',
                'bfaa': '',
                'handleOrEmail': self._account.username,
                'password': self._account.password,
                'remember': []
            }
            self._req.post(url='https://codeforces.com/enter', data=post_data)
        except Exception as e:
            logger.exception(e)
        return self.is_login()

    # 检查登录状态
    def is_login(self):
        res = self._req.get('https://codeforces.com')
        if res and re.search(r'logout">Logout</a>', res.text):
            return True
        return False

    def account_required(self):
        return False

    # 获取题目
    def get_problem(self, pid):
        if len(str(pid)) < 2 or str(pid)[-1].isalpha() is False or str(pid)[:-1].isnumeric() is False:
            raise SpiderException('Problem not exist')
        contest_id = str(pid)[:-1]
        problem_id = str(pid)[-1]
        p_url = f'https://codeforces.com/contest/{contest_id}/problem/{problem_id}'
        res = self._req.get(p_url)
        return CodeforcesParser().problem_parse(res, pid, p_url)

    # 提交代码
    def submit_code(self, pid, language, code):
        if not self.login_website():
            raise SpiderAccountLoginError("Login error")
        res = self._req.get('https://codeforces.com/problemset/submit')
        if res is None:
            raise SpiderNetworkError('Network error')
        soup = BeautifulSoup(res.text, 'lxml')
        csrf_token = soup.find(attrs={'name': 'X-Csrf-Token'}).get('content')
        post_data = {
            'csrf_token': csrf_token,
            'ftaa': '',
            'bfaa': '',
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemCode': pid,
            'programTypeId': language,
            'source': code,
            'tabSize': 0,
            'sourceFile': '',
        }
        submit_url = f'https://codeforces.com/problemset/submit?csrf_token={csrf_token}'
        status_list_url = 'https://codeforces.com/problemset/status?my=on'
        self._req.post(submit_url, data=post_data)
        status_res = self._req.get(status_list_url)
        website_data = status_res.text
        if website_data:
            soup = BeautifulSoup(website_data, 'lxml')
            tag = soup.find('table', attrs={'a': 'view-source'})
            if tag:
                status_url = f'https://codeforces.com{tag.get("href")}'
                while True:
                    time.sleep(1)
                    result = CodeforcesParser().result_parse(response=self._req.get(status_url))
                    if str(result.verdict_info) != 'In queue' and not str(result.verdict_info).startswith(
                            'Running on test'):
                        if str(result.verdict_info).startswith('Accepted') or str(result.verdict_info).startswith(
                                'Happy New Year!'):
                            result.verdict = Result.Verdict.ACCEPTED
                        elif str(result.verdict_info).startswith('Compilation error'):
                            result.verdict = Result.Verdict.COMPILE_ERROR
                        else:
                            result.verdict = Result.Verdict.WRONG_ANSWER
                        return result
            else:
                raise SpiderException('Parse result error')
        else:
            raise SpiderException('Parse result error')

    def find_language(self):
        if self.login_website() is False:
            return {}
        res = self._req.get('http://codeforces.com/problemset/submit')
        website_data = res.text
        languages = {}
        if website_data:
            soup = BeautifulSoup(website_data, 'lxml')
            tags = soup.find('select', attrs={'name': 'programTypeId'})
            if tags:
                for child in tags.find_all('option'):
                    languages[child.get('value')] = child.string
        return languages

    # 检查源OJ是否运行正常
    def is_working(self):
        return self._req.get('http://codeforces.com').status_code == 200
