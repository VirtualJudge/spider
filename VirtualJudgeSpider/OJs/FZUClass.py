import re

from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base, BaseParser
from VirtualJudgeSpider.Utils import HtmlTag, HttpUtil

import traceback


class FZUParser(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://acm.fzu.edu.cn/'

    def problem_parse(self, response, pid, url):
        problem = Problem()

        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'FZU'

        if response is None:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        website_data = response.text
        status_code = response.status_code

        if status_code != 200:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        if re.search('No Such Problem!', website_data):
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        try:
            soup = BeautifulSoup(website_data, 'lxml')
            problem.title = re.search(r'<b> Problem [\d]* ([\s\S]*?)</b>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* mSec)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* KB)', website_data).group(1)
            problem.special_judge = re.search(r'<font color="blue">Special Judge</font>', website_data) is not None
            problem.html = ''
            for tag in soup.find('div', attrs={'class': 'problem_content'}).children:
                if tag.name == 'h2':
                    if tag.img:
                        tag.img.decompose()
                problem.html += str(HtmlTag.update_tag(tag, self._static_prefix))
            problem.html = '<body>' + problem.html + '</body>'
            problem.status = Problem.Status.STATUS_CRAWLING_SUCCESS
        except:
            problem.status = Problem.Status.STATUS_PARSE_ERROR
        finally:
            return problem

    def result_parse(self, response):
        result = Result()
        if response is None or response.status_code != 200:
            result.status = Result.Status.STATUS_NETWORK_ERROR
            return result

        try:
            website_data = response.text
            soup = BeautifulSoup(website_data, 'lxml')
            line = soup.find('tr', attrs={'onmouseover': 'hl(this);'}).find_all('td')
            if line is not None:
                result.origin_run_id = line[0].string
                result.verdict = line[2].string
                result.execute_time = line[5].string
                result.execute_memory = line[6].string
                result.status = Result.Status.STATUS_RESULT_GET
            else:
                result.status = Result.Status.STATUS_RESULT_NOT_EXIST
        except:
            result.status = Result.Status.STATUS_PARSE_ERROR
        finally:
            return result

    def result_parse_by_rid(self, response, rid):
        result = Result()
        if response is None or response.status_code != 200:
            result.status = Result.Status.STATUS_NETWORK_ERROR
            return result, False

        try:
            website_data = response.text
            soup = BeautifulSoup(website_data, 'lxml')
            lines = soup.find_all('tr', attrs={'onmouseover': 'hl(this);'})
            for line in lines:
                tag_tds = line.find_all('td')
                if len(tag_tds) == 9 and int(tag_tds[0].get_text()) == int(rid):
                    result.origin_run_id = tag_tds[0].string
                    result.verdict = tag_tds[2].string
                    result.execute_time = tag_tds[5].string
                    result.execute_memory = tag_tds[6].string
                    result.status = Result.Status.STATUS_RESULT_GET
                    return result, True
            result.status = Result.Status.STATUS_RESULT_NOT_EXIST
            return result, False
        except:
            result.status = Result.Status.STATUS_PARSE_ERROR
            return result, False


class FZU(Base):
    def __init__(self):
        self._req = HttpUtil(custom_headers=Config.custom_headers)

    @staticmethod
    def home_page_url():
        url = 'http://acm.fzu.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.fzu.edu.cn/'
        try:
            res = self._req.get(url)
            if res.status_code == 200:
                website_data = res.text
                if re.search(r'<a href="user.php', website_data):
                    return True
        except:
            pass
        return False

    def login_webside(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        try:
            login_page_url = 'http://acm.fzu.edu.cn/login.php'
            login_link_url = 'http://acm.fzu.edu.cn/login.php?act=1&dir='
            post_data = {'uname': account.username, 'upassword': account.password,
                         'submit': 'Submit'}
            self._req.get(login_page_url)
            self._req.post(login_link_url, post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        pid = str(kwargs['pid'])
        url = 'http://acm.fzu.edu.cn/problem.php?pid=' + pid
        res = self._req.get(url)
        return FZUParser().problem_parse(res, pid, url)

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            username = kwargs['account'].username
            url = 'http://acm.fzu.edu.cn/submit.php?act=5'
            Config.custom_headers['Referer'] = 'http://acm.fzu.edu.cn/submit.php?pid=' + str(pid)

            post_data = {'usr': username, 'lang': str(language), 'pid': pid, 'code': code, 'submit': 'Submit'}

            res = self._req.post(url, post_data)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return False
        url = 'http://acm.fzu.edu.cn/submit.php?'
        languages = {}
        try:
            res = self._req.get(url)
            website_data = res.text
            soup = BeautifulSoup(website_data, 'lxml')
            options = soup.find('select', attrs={'name': 'lang'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        finally:
            return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.fzu.edu.cn/log.php?pid=' + pid + '&user=' + account.username + '&language=99&state=99&submit=Go'
        return self.get_result_by_url(url=url)

    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://acm.fzu.edu.cn/log.php?pid=' + pid + '&page=1'
        page = 2
        res = self._req.get(url)
        (result, exist_rid) = FZUParser().result_parse_by_rid(res, rid)
        while not exist_rid and result.status == Result.Status.STATUS_RESULT_NOT_EXIST and page < 10:
            url = 'http://acm.fzu.edu.cn/log.php?pid=' + pid + '&page=' + str(page)
            page += 1
            res = self._req.get(url)
            (result, exist_rid) = FZUParser().result_parse_by_rid(res, rid)
        return result

    def get_result_by_url(self, url):
        print(url)
        res = self._req.get(url)
        return FZUParser().result_parse(res)

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Judging...', 'Queuing...']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.fzu.edu.cn/index.php'
        try:
            res = self._req.get(url)
            if res.status_code != 200:
                return False
            website_data = res.text
            if re.search(r'<title>Fuzhou University OnlineJudge</title>', website_data):
                return True
            return False
        except:
            return False
