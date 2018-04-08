import re
import traceback
import os
import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base
from ..Utils import deal_with_image_url


class HDU(Base):
    def __init__(self):
        self.req = requests.Session()
        self.req.headers.update(Config.custom_headers)

    @staticmethod
    def home_page_url():
        url = 'http://acm.hdu.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.hdu.edu.cn/'
        try:
            website_data = self.req.get(url)
            if re.search(r'userloginex\.php\?action=logout', website_data.text) is not None:
                return True
            return False
        except:
            return False

    def login_webside(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        login_link_url = 'http://acm.hdu.edu.cn/userloginex.php'
        post_data = {'username': account.get_username(),
                     'userpass': account.get_password(),
                     'login': 'Sign In'
                     }
        try:
            self.req.post(url=login_link_url, data=post_data,
                          params={'action': 'login'})
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def parse_desc(self, raw_descs):
        descList = Config.DescList()
        for raw_desc in raw_descs.split('<br>'):
            if raw_desc.strip(''):
                match_groups = re.search(r'<img([\s\S]*)src=([\s\S]*(gif|png|jpeg|jpg|GIF))', raw_desc)
                if match_groups:
                    file_name, remote_path = deal_with_image_url(str(match_groups.group(2)), 'http://acm.hdu.edu.cn/')

                    descList.append(
                        Config.Desc(type=Config.Desc.Type.IMG,
                                    file_name=file_name,
                                    origin=remote_path))
                else:
                    descList.append(Config.Desc(type=Config.Desc.Type.TEXT, content=raw_desc))
        return descList.get()

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.hdu.edu.cn/showproblem.php?pid=' + str(kwargs['pid'])
        problem = Problem()
        try:
            res = self.req.get(url)
            website_data = res.text
            problem.remote_id = str(kwargs['pid'])
            problem.remote_url = url
            problem.remote_oj = 'HDU'
            problem.title = re.search(r'color:#1A5CC8\'>([\s\S]*?)</h1>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* MS)', website_data).group(1)
            problem.memory_limit = re.search(r'/(\d* K)', website_data).group(1)

            problem.special_judge = re.search(r'color=red>Special Judge</font>', website_data) is not None

            # description
            match_groups = re.search(r'>Problem Description</div>[\s\S]*?panel_content>([\s\S]*?)</div>',
                                     website_data)
            if match_groups:
                problem.description = self.parse_desc(match_groups.group(1))
            # input
            match_groups = re.search(r'>Input</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data)
            if match_groups:
                problem.input = self.parse_desc(match_groups.group(1))

            # output

            match_groups = re.search(r'>Output</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data)
            if match_groups:
                problem.output = self.parse_desc(match_groups.group(1))

            # input data
            match_groups = re.search(r'>Sample Input</div>[\s\S]*?panel_content>([\s\S]*?)</div', website_data)
            input_data = ''
            if match_groups:
                input_data = re.search(r'(<pre><div[\s\S]*?>)?([\s\S]*)', match_groups.group(1)).group(2)

            # output data
            output_data = ''
            match_groups = re.search(r'>Sample Output</div>[\s\S]*?panel_content>([\s\S]*?)</div', website_data)
            if match_groups:
                output_data = re.search(r'(<pre><div[\s\S]*?>)?([\s\S]*)', match_groups.group(1)).group(2)
                if re.search('<div', output_data):
                    output_data = re.search(r'([\s\S]*?)<div', output_data).group(1)
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]

            # author
            match_groups = re.search(r'>Author</div>[\s\S]*?panel_content>([\s\S]*?)</div>', website_data)
            if match_groups:
                problem.author = match_groups.group(1)

            # hint
            match_groups = re.search(r'<i>Hint</i>[\s\S]*?/div>[\s]*([\s\S]+?)</div>', website_data)
            if match_groups:
                problem.hint = self.parse_desc(match_groups.group(1))
        except:
            traceback.print_exc()
            return None
        return problem

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            url = 'http://acm.hdu.edu.cn/submit.php'
            post_data = {'check': '0', 'language': language, 'problemid': pid, 'usercode': code}
            res = self.req.post(url=url, data=post_data, params={'action': 'submit'})
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://acm.hdu.edu.cn/submit.php'
        languages = {}
        try:
            website_data = self.req.get(url)
            soup = BeautifulSoup(website_data.text, 'lxml')
            options = soup.find('select', attrs={'name': 'language'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        finally:
            return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.hdu.edu.cn/status.php?first=&pid=' + pid + '&user=' + account.username + '&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        result = Result()
        try:
            data = self.req.get(url)
            soup = BeautifulSoup(data.text, 'lxml')
            line = soup.find('table', attrs={'class': 'table_text'}).find('tr', attrs={'align': 'center'}).find_all(
                'td')
            if line:
                result.origin_run_id = line[0].string
                result.verdict = line[2].string
                result.execute_time = line[4].string
                result.execute_memory = line[5].string
                return result
        except:
            pass
        return result

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Queuing', 'Compiling', 'Running']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.hdu.edu.cn/'
        try:
            website_data = self.req.get(url)
            if re.search(r'<H1>Welcome to HDU Online Judge System</H1>', website_data.text):
                return True
        except:
            return False
