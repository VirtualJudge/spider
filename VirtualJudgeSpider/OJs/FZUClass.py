import re
from http import cookiejar
from urllib import request, parse

from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Spider, Result
from VirtualJudgeSpider.OJs.BaseClass import Base


class FZU(Base):
    def __init__(self):
        self.code_type = 'utf-8'
        self.cj = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))

    @staticmethod
    def home_page_url(self):
        url = 'http://acm.fzu.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.fzu.edu.cn/'
        try:
            with self.opener.open(url) as fin:
                website_data = fin.read().decode(self.code_type)
                if re.search(r'<a href="user.php', website_data) is not None:
                    return True
        except:
            return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://acm.fzu.edu.cn/login.php'
        login_link_url = 'http://acm.fzu.edu.cn/login.php?act=1&dir='
        post_data = parse.urlencode(
            {'uname': kwargs['account'].get_username(), 'upassword': kwargs['account'].get_password(),
             'submit': 'Submit'})
        try:
            self.opener.open(login_page_url)
            req = request.Request(url=login_link_url, data=post_data.encode(self.code_type),
                                  headers=Config.custom_headers, )
            self.opener.open(req)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.fzu.edu.cn/problem.php?pid=' + str(kwargs['pid'])
        problem = Problem()
        try:
            website_data = Spider.get_data(url, self.code_type)
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
            if len(data) > 1:
                input_data = data[0].get_text()
                output_data = data[1].get_text()
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]

            h2s = soup.find_all('h2')
            for h2 in h2s[-2:]:
                if (h2.get_text().strip() == 'Hint'):
                    problem.hint = h2.next_sibling

                if (h2.get_text().strip() == 'Source'):
                    problem.source = h2.next_sibling


        except Exception as e:
            # print(e)
            return Problem.PROBLEM_NOT_FOUND
        return problem

    def submit_code(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            username = kwargs['account'].get_username()
            url = 'http://acm.fzu.edu.cn/submit.php?act=5'
            Config.custom_headers['Referer'] = 'http://acm.fzu.edu.cn/submit.php?pid=' + str(pid)
            languages = self.find_language()
            # 语言字典键值反转
            languages = {value: key for key, value in languages.items()}
            # 字典键值映射
            language = languages[language]
            post_data = parse.urlencode(
                {'usr': username, 'lang': str(language), 'pid': pid, 'code': code, 'submit': 'Submit'})
            req = request.Request(url=url, data=post_data.encode(self.code_type), headers=Config.custom_headers)
            response = self.opener.open(req)
            response.read().decode(self.code_type)
            return True
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return False
        url = 'http://acm.fzu.edu.cn/submit.php?'
        languages = {}
        try:
            with self.opener.open(url) as fin:
                data = fin.read().decode(self.code_type)
                soup = BeautifulSoup(data, 'lxml')
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
            with request.urlopen(url) as fin:
                data = fin.read().decode(self.code_type)
                soup = BeautifulSoup(data, 'lxml')
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
        return result

    def get_class_name(self):
        return str('FZU')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Judging...', 'Queuing...']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.fzu.edu.cn/index.php'
        try:
            with request.urlopen(url, timeout=5) as fin:
                data = fin.read().decode(self.code_type)
                if re.search(r'<title>Fuzhou University OnlineJudge</title>', data):
                    return True
            return False
        except:
            return False
