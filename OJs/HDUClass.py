from OJs.BaseClass import Base
from urllib import request, parse
from bs4 import BeautifulSoup
import re
from http import cookiejar
from Config import Problem, Spider, Result
import Config

class HDU(Base):
    def __init__(self):

        self.code_type = 'gb2312'
        self.cj = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))

    def check_login_status(self):
        url = 'http://acm.hdu.edu.cn/'

        with self.opener.open(url) as fin:
            website_data = fin.read().decode(self.code_type)
            if re.search(r'userloginex\.php\?action=logout', website_data) is not None:
                return True
        return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        assert kwargs['account'] is not None, "没有提供账号"
        login_page_url = 'http://acm.hdu.edu.cn/'
        login_link_url = 'http://acm.hdu.edu.cn/userloginex.php?action=login&cid=0&notice=0'

        post_data = parse.urlencode(
            {'username': kwargs['account'].get_username(), 'userpass': kwargs['account'].get_password()})

        self.opener.open(login_page_url)
        req = request.Request(url=login_link_url, data=post_data.encode(self.code_type), headers=Config.custom_headers)
        self.opener.open(req)
        if self.check_login_status():
            return True
        else:
            return False

    def get_problem(self, *args, **kwargs):
        assert kwargs['pid'] is not None, "没有给题目编号'id'"
        url = 'http://acm.hdu.edu.cn/showproblem.php?pid=' + str(kwargs['pid'])
        website_data = Spider.get_data(url, self.code_type)
        problem = Problem()
        problem.origin_id = kwargs['pid']
        problem.origin_url = url

        problem.title = re.search(r'color:#1A5CC8\'>([\s\S]*?)</h1>', website_data).group(1)
        problem.time_limit = re.search(r'(\d* MS)', website_data).group(1)
        problem.memory_limit = re.search(r'/(\d* K)', website_data).group(1)
        problem.description = re.search(r'>Problem Description</div>[\s\S]*?panel_content>([\s\S]*?)</div>',
                                        website_data).group(1)
        problem.input = re.search(r'>Input</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data).group(1)
        problem.output = re.search(r'>Output</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data).group(1)
        problem.sample = [
            {'input': re.search(r'>Sample Input</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data).group(1),
             'output': re.search(r'>Sample Output</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data).group(1)}]
        problem.author = re.search(r'>Author</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data).group(1)

        return problem

    def submit_code(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return False
        assert kwargs['code'] is not None
        assert kwargs['language'] is not None
        assert kwargs['pid'] is not None
        code = kwargs['code']
        language = kwargs['language']
        pid = kwargs['pid']
        url = 'http://acm.hdu.edu.cn/submit.php?action=submit'
        post_data = parse.urlencode({'check': '0', 'language': language, 'problemid': pid, 'usercode': code})
        req = request.Request(url=url, data=post_data.encode(self.code_type), headers=Config.custom_headers)
        response = self.opener.open(req)
        response.read().decode(self.code_type)
        return True

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://acm.hdu.edu.cn/submit.php'
        languages = {}
        with self.opener.open(url) as fin:
            data = fin.read().decode(self.code_type)
            soup = BeautifulSoup(data, 'lxml')
            options = soup.find('select', attrs={'name': 'language'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.hdu.edu.cn/status.php?first=&pid=' + pid + '&user=' + account.username + '&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_rid(self, rid):
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        result = Result()
        with request.urlopen(url) as fin:
            data = fin.read().decode(self.code_type)
            soup = BeautifulSoup(data, 'lxml')
            line = soup.find('table', attrs={'class': 'table_text'}).find('tr', attrs={'align': 'center'}).find_all(
                'td')
            if line is not None:
                result.origin_run_id = line[0].string
                result.verdict = line[2].string
                result.execute_time = line[4].string
                result.execute_memory = line[5].string
        return result

    def get_class_name(self):
        return str('HDU')

    def is_waiting_for_judge(self, verdict):
        if verdict == 'Queuing' or verdict == 'Compiling':
            return True
        return False
