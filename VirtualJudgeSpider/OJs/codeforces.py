import os
import re

from bs4 import BeautifulSoup
from bs4 import element
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from VirtualJudgeSpider.OJs.base import Base, BaseParser
from VirtualJudgeSpider.config import custom_headers, Problem, Result
from VirtualJudgeSpider.utils import HtmlTag
from VirtualJudgeSpider.utils import HttpUtil


def get_env(key, value=''):
    return os.environ.get(key, value)


class CodeforcesParser(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://codeforces.com/'
        self._script = """
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
 showProcessingMessages: false,
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
<script src="https://cdn.bootcss.com/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
"""

    def problem_parse(self, response, pid, url):
        problem = Problem()
        problem.remote_oj = 'Codeforces'
        problem.remote_id = pid
        problem.remote_url = url
        if response is None:
            problem.status = Problem.Status.STATUS_SUBMIT_FAILED
            return problem
        elif response.status_code == 302:
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        elif response.status_code != 200:
            problem.status = Problem.Status.STATUS_SUBMIT_FAILED
            return problem
        elif response.text is None:
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
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
            print(match_groups)
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
        problem.status = Problem.Status.STATUS_CRAWLING_SUCCESS
        return problem

    def result_parse(self, response):
        if response is None or response.status_code != 200 or response.text is None:
            result = Result()
            result.status = Result.Status.STATUS_SUBMIT_FAILED
            return result
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table')
        tag = None
        if table:
            tag = table.find_all('tr')
        if tag:
            children_tag = tag[-1].find_all('td')
            if len(children_tag) > 9:
                result = Result()
                result.origin_run_id = children_tag[0].string
                result.verdict = children_tag[4].span.string
                result.execute_time = children_tag[5].string
                result.execute_memory = children_tag[6].string
                return result
        result = Result()
        result.status = Result.Status.STATUS_SUBMIT_FAILED
        return result


class Codeforces(Base):
    def __init__(self):
        self._bfaa = ''
        self._ftaa = ''
        self._csrf_token = ''
        self._remote = 'http://' + str(get_env('PHANTOMJS_HOST', '127.0.0.1')) + ':' + str(
            get_env('PHANTOMJS_PORT', '8910'))
        driver = webdriver.Remote(command_executor=self._remote, desired_capabilities=DesiredCapabilities.PHANTOMJS)
        driver.get('http://codeforces.com/enter')
        self._bfaa = driver.execute_script('return _bfaa')
        self._ftaa = driver.execute_script('return _ftaa')
        self._csrf_token = driver.find_element_by_name('csrf_token').get_attribute('value')
        cookies = {item['name']: item['value'] for item in driver.get_cookies()}
        self._req = HttpUtil(custom_headers=custom_headers, cookies=cookies)
        driver.quit()

    # 主页链接
    @staticmethod
    def home_page_url():
        return 'http://codeforces.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if type(cookies) == dict:
            self._req.cookies.update(cookies)

    def get_csrf_token(self):
        res = self._req.get(self.home_page_url())
        if res is None or res.status_code != 200 or res.text is None:
            return ''
        soup = BeautifulSoup(res.text, 'lxml')
        item = soup.find('meta', attrs={'name': 'X-Csrf-Token'})
        csrf_token = item.get('content')
        return csrf_token

    # 登录页面
    def login_website(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        login_link_url = 'http://codeforces.com/enter?back=%2F'

        csrf_token = self._csrf_token
        post_data = {'handleOrEmail': account.username,
                     'password': account.password,
                     'ftaa': self._ftaa,
                     'bfaa': self._bfaa,
                     'action': 'enter',
                     'remember': 'on',
                     '_tta': 871,
                     'csrf_token': csrf_token}
        print(post_data)
        self._req.post(url=login_link_url, data=post_data)
        return self.check_login_status()

    # 检查登录状态
    def check_login_status(self):
        res = self._req.get(self.home_page_url())
        if res and res.status_code == 200 and res.text:
            if re.search(r'logout">Logout</a>', res.text) is not None:
                return True
        return False

    # 获取题目
    def get_problem(self, pid, *args, **kwargs):

        if len(str(pid)) < 2 or str(pid)[-1].isalpha() is False or str(pid)[:-1].isnumeric() is False:
            problem = Problem()
            problem.remote_oj = Codeforces.__name__
            problem.remote_id = pid
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        p_url = 'http://codeforces.com/problemset/problem/' + str(pid)[:-1] + '/' + str(pid)[-1]
        res = self._req.get(url=p_url)
        return CodeforcesParser().problem_parse(res, pid, p_url)

    # 提交代码
    def submit_code(self, *args, **kwargs):
        if not self.login_website(*args, **kwargs):
            return False
        code = kwargs.get('code')
        language = kwargs.get('language')
        pid = kwargs.get('pid')
        url = 'http://codeforces.com/problemset/submit?csrf_token=' + self.get_csrf_token()

        post_data = {
            'csrf_token': self.get_csrf_token(),
            'ftaa': self._ftaa,
            'bfaa': self._bfaa,
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemCode': pid,
            'programTypeId': language,
            'source': code,
            'tabSize': 4
        }
        res = self._req.post(url=url, data=post_data)
        if res and res.status_code == 302:
            return True
        return False

    # 获取当然运行结果
    def get_result(self, account, pid, *args, **kwargs):
        if self.login_website(account, *args, **kwargs) is False:
            result = Result()
            result.status = Result.Status.STATUS_SUBMIT_FAILED
            return result

        request_url = 'http://codeforces.com/problemset/status?friends=on'
        res = self._req.get(request_url)
        if res and res.status_code == 200:
            website_data = res.text
            soup = BeautifulSoup(website_data, 'lxml')
            tag = soup.find('table', attrs={'class': 'status-frame-datatable'})
            if tag:
                list_tr = tag.find_all('tr')
                for tr in list_tr:
                    if isinstance(tr, element.Tag) and tr.get('data-submission-id'):
                        return self.get_result_by_url(
                            'http://codeforces.com/contest/' + pid[:-1] + '/submission/' + tr.get('data-submission-id'))

    # 根据源OJ的运行id获取结构
    def get_result_by_rid_and_pid(self, rid, pid):
        return self.get_result_by_url('http://codeforces.com/contest/' + str(pid)[:-1] + '/submission/' + str(rid))

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        res = self._req.get(url=url)
        return CodeforcesParser().result_parse(response=res)

    # 获取源OJ支持的语言类型
    def find_language(self, account, *args, **kwargs):
        if self.login_website(account, *args, **kwargs) is False:
            print('login failed')
            return {}
        print('login success')
        res = self._req.get('http://codeforces.com/problemset/submit')
        languages = {}
        if res and res.text and res.status_code == 200:
            print('res accepted')
            soup = BeautifulSoup(res.text, 'lxml')
            tags = soup.find('select', attrs={'name': 'programTypeId'})
            if tags:
                for child in tags.find_all('option'):
                    languages[child.get('value')] = child.string
        return languages

    # 检查源OJ是否运行正常
    def check_status(self):
        res = self._req.get(self.home_page_url())
        if res and res.status_code == 200:
            return True
        return False

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
        return str(verdict).startswith('Running on test') or verdict == 'In queue'
