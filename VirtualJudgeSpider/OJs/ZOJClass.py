import re

from bs4 import BeautifulSoup
from bs4 import element

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base, BaseParser
from VirtualJudgeSpider.Utils import HtmlTag, HttpUtil


class ZOJParaer(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://acm.zju.edu.cn/onlinejudge/'
        self._script = """<style>
* {
    font-family: Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif; 
    font-size: 14px;
}
</style>"""

    def problem_parse(self, response, pid, url):
        problem = Problem()

        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'ZOJ'

        if not response:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        website_data = response.text
        status_code = response.status_code

        if status_code != 200:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        if re.search('No such problem', website_data):
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem

        try:
            soup = BeautifulSoup(website_data, 'lxml')
            problem.title = soup.find('span', attrs={'class': 'bigProblemTitle'})
            problem.time_limit = re.search(r'(\d* Second)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* KB)', website_data).group(1)
            problem.special_judge = re.search(r'<font color="blue">Special Judge</font>',
                                              website_data) is not None
            problem.html = ''
            problem.html += self._script
            raw_html = soup.find('div', attrs={'id': 'content_body'})
            for tag in raw_html.children:
                if type(tag) == element.NavigableString:
                    problem.html += str(tag)
                if type(tag) == element.Tag and tag.name not in ['center', 'hr']:
                    if tag.name == 'a' and tag.get('href') == '/onlinejudge/faq.do#sample':
                        continue
                    if tag.name == 'h2':
                        tag['style'] = HtmlTag.TagStyle.TITLE.value
                    elif tag.name == 'p' and tag.b and tag.b.string in ['Input', 'Output', 'Sample Input',
                                                                        'Sample Output']:
                        tag.b['style'] = HtmlTag.TagStyle.TITLE.value
                    else:
                        tag['style'] = HtmlTag.TagStyle.CONTENT.value
                    problem.html += str(HtmlTag.update_tag(tag, self._static_prefix))
            problem.status = Problem.Status.STATUS_CRAWLING_SUCCESS
        except:
            problem.status = Problem.Status.STATUS_PARSE_ERROR
        finally:
            return problem

    def result_parse(self, website_data):
        result = Result()
        soup = BeautifulSoup(website_data, 'lxml')
        line = soup.find('table', attrs={'class': 'list'}).find('tr', attrs={'class': 'rowOdd'}).find_all(
            'td')
        if line:
            result.origin_run_id = line[0].string
            result.verdict = line[2].get_text().strip()
            result.execute_time = line[5].string
            result.execute_memory = line[6].string
            return result
        return None


class ZOJ(Base):
    def __init__(self):
        self._req = HttpUtil(custom_headers=Config.custom_headers)

    @staticmethod
    def home_page_url():
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        return url

    def check_login_status(self):
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        try:
            res = self._req.get(url)
            if re.search(r'/onlinejudge/logout.do">Logout', res.text) is not None:
                return True
            return False
        except:
            return False

    def login_webside(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        login_link_url = 'http://acm.zju.edu.cn/onlinejudge/login.do'
        post_data = {'handle': account.username, 'password': account.password}
        try:
            self._req.post(url=login_link_url, data=post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        pid = str(kwargs['pid'])
        url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=' + pid
        res = self._req.get(url)
        return ZOJParaer().problem_parse(res, pid, url)

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            problem_url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=' + str(pid)
            res = self._req.get(problem_url)
            website_data = res.text
            problem_id = re.search('problemId=(\d*)"><font color="blue">Submit</font>', website_data).group(1)
            url = 'http://acm.zju.edu.cn/onlinejudge/submit.do?problemId=' + str(problem_id)
            post_data = {'languageId': str(language), 'problemId': str(pid), 'source': code}
            res = self._req.post(url=url, data=post_data)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=1001'
        languages = {}
        try:
            res = self._req.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            options = soup.find('select', attrs={'name': 'languageId'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        finally:
            return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.zju.edu.cn/onlinejudge/showRuns.do?contestId=1&search=true&firstId=-1&lastId=-1&problemCode=' + str(
            pid) + '&handle=' + account.username + '&idStart=&idEnd='
        return self.get_result_by_url(url=url)

    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://acm.zju.edu.cn/onlinejudge/showRuns.do?contestId=1&search=true&fi' \
              'rstId=-1&lastId=-1&problemCode=&handle=&idStart=' + str(rid) + '&idEnd=' + str(rid)
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        try:
            res = self._req.get(url)
            return ZOJParaer().result_parse(res.text)
        except:
            return None

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Queuing']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        try:
            website_data = self._req.get(url)
            if re.search(r'<div class="welcome_msg">Welcome to ZOJ</div>', website_data.text):
                return True
        except:
            return False
