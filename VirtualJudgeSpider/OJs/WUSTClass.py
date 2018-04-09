import re
import traceback

from bs4 import BeautifulSoup
from bs4 import element

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base, BaseParser
from VirtualJudgeSpider.Utils import HttpUtil, HtmlTag


class WUSTParser(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://acm.wust.edu.cn/'

    def problem_parse(self, website_data, pid, url):
        problem = Problem()
        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'WUST'

        problem.title = re.search(r': ([\s\S]*?)</h2>', website_data).group(1)
        problem.time_limit = re.search(r'(\d* Sec)', website_data).group(1)
        problem.memory_limit = re.search(r'(\d* MB)', website_data).group(1)
        problem.special_judge = re.search(r'class=red>Special Judge</span>', website_data) is not None

        soup = BeautifulSoup(website_data, 'lxml')

        problem.html = ''
        for tag in soup.find('div', attrs={'class': 'rich_text'}).children:
            if type(tag) == element.Tag:
                if tag.name in ['h2', 'div']:
                    if not tag.get('class'):
                        tag['class'] = ()
                    if tag.name == 'h2':
                        tag['style'] = HtmlTag.TagStyle.TITLE.value
                        tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                        problem.html += str(
                            HtmlTag.update_tag(tag, self._static_prefix, update_style=HtmlTag.TagStyle.TITLE.value))

                    else:
                        tag['style'] = HtmlTag.TagStyle.CONTENT.value
                        tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                        problem.html += str(
                            HtmlTag.update_tag(tag, self._static_prefix, update_style=HtmlTag.TagStyle.CONTENT.value))
        problem.html = '<body>' + problem.html + '</body>'
        return problem

    def result_parse(self, website_data):
        result = Result()
        soup = BeautifulSoup(website_data, 'lxml')
        line = soup.find('table', attrs={'id': 'result-tab'}).find('tr', attrs={'class': 'evenrow'}).find_all('td')
        if line:
            result.origin_run_id = line[0].string
            result.verdict = line[4].string
            result.execute_time = line[6].string
            result.execute_memory = line[5].string
            return result
        return result


class WUST(Base):
    def __init__(self):
        self._req = HttpUtil(Config.custom_headers, 'utf-8')

    @staticmethod
    def home_page_url():
        url = 'http://acm.wust.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.wust.edu.cn/'
        try:
            res = self._req.get(url)
            website_data = res.text
            if re.search(r'<a href="logout.php">Logout</a>', website_data) is not None:
                return True
        except:
            return False

    def login_webside(self, account, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://acm.wust.edu.cn/loginpage.php'
        login_link_url = 'http://acm.wust.edu.cn/login.php'

        post_data = {'user_id': account.username,
                     'password': account.password,
                     'submit': 'Submit'}
        try:
            self._req.get(login_page_url)
            self._req.post(login_link_url, post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        pid = str(kwargs['pid'])
        url = 'http://acm.wust.edu.cn/problem.php?id=' + pid + '&soj=0'
        try:
            res = self._req.get(url)
            return WUSTParser().problem_parse(res.text, pid, url)
        except:
            traceback.print_exc()
            return None

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            link_page_url = 'http://acm.wust.edu.cn/submitpage.php?id=' + str(pid) + '&soj=0'
            link_post_url = 'http://acm.wust.edu.cn/submit.php?'
            #    self._req.headers.update({'Referer': link_page_url})
            res = self._req.get(link_page_url)
            if res.status_code != 200:
                return False
            soup = BeautifulSoup(res.text, 'lxml')
            submitkey = soup.find('input', attrs={'name': 'submitkey'})['value']
            post_data = {'id': str(pid), 'soj': '0', 'language': language, 'source': code, 'submitkey': str(submitkey)}
            res = self._req.post(url=link_post_url, data=post_data)
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
            res = self._req.get(url)
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

    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        try:
            res = self._req.get(url)
            return WUSTParser().result_parse(res.text)
        except:
            return None

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Pending', 'Pending Rejudge', 'Compiling', 'Running & Judging']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.wust.edu.cn/'
        try:
            res = self._req.get(url)
            if re.search(r'<a href="index.php">WUST Online Judge</a>', res.text):
                return True
        except:
            return False
