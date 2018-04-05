import re

import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base


class FZU(Base):
    def __init__(self):
        self.req = requests.session()
        self.header = Config.custom_headers
        self.req.headers.update(self.header)

    @staticmethod
    def home_page_url():
        url = 'http://acm.fzu.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.fzu.edu.cn/'
        try:
            res = self.req.get(url)
            if res.status_code == 200:
                website_data = res.text
                if re.search(r'<a href="user.php', website_data):
                    return True
        except:
            pass
        return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        try:
            login_page_url = 'http://acm.fzu.edu.cn/login.php'
            login_link_url = 'http://acm.fzu.edu.cn/login.php?act=1&dir='
            post_data = {'uname': kwargs['account'].get_username(), 'upassword': kwargs['account'].get_password(),
                         'submit': 'Submit'}
            self.req.get(login_page_url)
            self.req.post(login_link_url, post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.fzu.edu.cn/problem.php?pid=' + str(kwargs['pid'])
        problem = Problem()
        try:
            res = self.req.get(url)
            if res.status_code != 200:
                return None
            website_data = res.text
            soup = BeautifulSoup(website_data, 'lxml')
            problem.remote_id = kwargs['pid']
            problem.remote_url = url
            problem.remote_oj = 'FZU'
            problem.title = re.search(r'<b> Problem [\d]* ([\s\S]*?)</b>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* mSec)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* KB)', website_data).group(1)
            problem.special_judge = re.search(r'<font color="blue">Special Judge</font>', website_data) is not None
            pro_desc = soup.find_all(attrs={"class": 'pro_desc'})
            problem.description = pro_desc[0].get_text()
            if len(pro_desc) >= 2:
                problem.input = pro_desc[1].get_text()
            if len(pro_desc) >= 3:
                problem.output = pro_desc[2].get_text()
            data = soup.find_all(attrs={"class": 'data'})
            input_data = ''
            output_data = ''
            if len(data) > 1:
                input_data = data[0].get_text()
                output_data = data[1].get_text()
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]

            h2s = soup.find_all('h2')
            for h2 in h2s[-2:]:
                if h2.get_text().strip() == 'Hint':
                    problem.hint = h2.next_sibling

                if h2.get_text().strip() == 'Source':
                    problem.source = h2.next_sibling

        except:
            return None
        return problem

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            username = kwargs['account'].get_username()
            url = 'http://acm.fzu.edu.cn/submit.php?act=5'
            Config.custom_headers['Referer'] = 'http://acm.fzu.edu.cn/submit.php?pid=' + str(pid)

            post_data = {'usr': username, 'lang': str(language), 'pid': pid, 'code': code, 'submit': 'Submit'}
            res = self.req.post(url, post_data)
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
            res = self.req.get(url)
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
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        result = Result()
        try:
            res = self.req.get(url)
            website_data = res.text
            soup = BeautifulSoup(website_data, 'lxml')
            line = soup.find('table').find('tr', attrs={'onmouseover': 'hl(this);'}).find_all(
                'td')
            if line is not None:
                result.origin_run_id = line[0].string
                result.verdict = line[2].string
                result.execute_time = line[5].string
                result.execute_memory = line[6].string
                return result
        except:
            pass
        return None

    def get_class_name(self):
        return str('FZU')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Judging...', 'Queuing...']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.fzu.edu.cn/index.php'
        try:
            res = self.req.get(url)
            if res.status_code != 200:
                return False
            website_data = res.text
            if re.search(r'<title>Fuzhou University OnlineJudge</title>', website_data):
                return True
            return False
        except:
            return False
