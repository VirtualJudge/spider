import re

import bs4
import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base


class WUST(Base):
    def __init__(self):
        self.code_type = 'UTF-8'
        self.headers = Config.custom_headers
        self.req = requests.Session()
        self.req.headers.update(self.headers)

    @staticmethod
    def home_page_url(self):
        url = 'http://acm.wust.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.wust.edu.cn/index.php'
        try:
            res = self.req.get(url)
            website_data = res.text
            if re.search(r'<a href="logout.php">Logout</a>', website_data) is not None:
                return True
        except:
            return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://acm.wust.edu.cn/loginpage.php'
        login_link_url = 'http://acm.wust.edu.cn/login.php'

        post_data = {'user_id': kwargs['account'].get_username(), 'password': kwargs['account'].get_password(),
                     'submit': 'Submit'}
        try:
            self.req.get(login_page_url)
            self.req.post(login_link_url, post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def find_texts(self, tag):
        ans = ''
        if type(tag) is bs4.element.NavigableString:
            return tag
        elif tag.children is not None and tag.name != 'style':
            for child in tag.children:
                ans = ans + self.find_texts(child)
        return ans

    def parse_html(self, model, soup, website_data):
        # -------------------------------------------------------------------------------------------------------
        ans = ''
        if model == 'Sample Input':
            model = soup.find('span', attrs={'id': 'sample_input'})
            if model is not None:
                for child in model.children:
                    ans = ans + self.find_texts(child)
            return ans.strip()

        taken = "<h2>" + model + "</h2>"
        match_group = re.search(re.compile(taken), website_data)
        if match_group is None:
            return ans
        model = soup.find('h2', text=model).next_siblings
        for tag in model:
            if tag.name == 'div':
                model = tag
                break
        # print(model)
        try:
            for child in model.children:
                ans = ans + self.find_texts(child)
                # print(model)
        except Exception as e:
            print(e)
        return ans.strip()
        # ---------------------------------------------------------------------------------------------------------

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.wust.edu.cn/problem.php?id=' + str(kwargs['pid']) + '&soj=0'
        problem = Problem()
        try:
            res = self.req.get(url)
            website_data = res.text
            problem.remote_id = kwargs['pid']
            problem.remote_url = url
            problem.remote_oj = 'WUST'
            problem.title = re.search(r': ([\s\S]*?)</h2>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* Sec)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* MB)', website_data).group(1)
            problem.special_judge = re.search(r'class=red>Special Judge</span>', website_data) is not None
            soup = BeautifulSoup(website_data, 'lxml')
            # case:problem.picture=self.parse_html("img", soup, website_data)
            problem.description = self.parse_html("Description", soup, website_data)
            problem.input = self.parse_html("Input", soup, website_data)
            problem.output = self.parse_html("Output", soup, website_data)
            input_data = self.parse_html("Sample Input", soup, website_data)
            output_data = self.parse_html("Sample Output", soup, website_data)
            problem.hint = self.parse_html("HINT", soup, website_data)
            problem.author = self.parse_html("Author", soup, website_data)
            problem.source = self.parse_html("Source", soup, website_data)
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]
        except:
            return None
        return problem

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            print('Login Failed')
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            link_page_url = 'http://acm.wust.edu.cn/submitpage.php?id=' + str(pid) + '&soj=0'
            link_post_url = 'http://acm.wust.edu.cn/submit.php?'
            self.req.headers.update({'Referer': link_page_url})
            res = self.req.get(link_page_url)
            soup = BeautifulSoup(res.text, 'lxml')
            submitkey = soup.find('input', attrs={'name': 'submitkey'})['value']
            post_data = {'id': str(pid), 'soj': '0', 'language': language, 'source': code, 'submitkey': str(submitkey)}
            res = self.req.post(url=link_post_url, data=post_data)
            if res.status_code != 200:
                return False
            return True
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://acm.wust.edu.cn/submitpage.php?id=1000&soj=0'
        languages = {}
        try:
            res = self.req.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            options = soup.find('select', attrs={'name': 'language'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        finally:
            return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.wust.edu.cn/status.php?soj=-1&problem_id=' + pid + '&user_id=' + account.username + '&language=-1&jresult=-1'

        return self.get_result_by_url(url=url)

    def get_result_by_rid(self, rid):
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        result = Result()
        try:
            res = self.req.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            line = soup.find('table', attrs={'id': 'result-tab'}).find('tr', attrs={'class': 'evenrow'}).find_all(
                'td')
            if line is not None:
                result.origin_run_id = line[0].string
                result.verdict = line[4].string
                result.execute_time = line[6].string
                result.execute_memory = line[5].string
                return result
        except:
            pass
        return None

    def get_class_name(self):
        return str('WUST')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Pending', 'Pending Rejudge', 'Compiling', 'Running & Judging']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.wust.edu.cn/'
        try:
            res = self.req.get(url)
            if re.search(r'<a href="index.php">WUST Online Judge</a>', res.text):
                return True
        except:
            return False
