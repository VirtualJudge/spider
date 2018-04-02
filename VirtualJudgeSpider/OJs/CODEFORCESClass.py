import re
import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base

class CODEFORCES(Base):
    def __init__(self):
        self.req = requests.Session()
        self.req.headers.update(Config.custom_headers)

    @staticmethod
    def home_page_url(self):
        url = 'http://codeforces.com/'
        return url

    def get_csrf_token(self):
        page = self.req.get(self.home_page_url(self))
        soup = BeautifulSoup(page.text, 'lxml')
        item = soup.find('meta', attrs={'name': 'X-Csrf-Token'})
        csrf_token = item['content']
        return csrf_token

    def check_login_status(self):
        url = self.home_page_url(self)
        try:
            website_data = self.req.get(url)
            if re.search(r'logout">Logout</a>', website_data.text) is not None:
                return True
            return False
        except:
            return False

    def login_website(self,  *args, **kwargs):
        if self.check_login_status():
            return True
        login_link_url = 'http://codeforces.com/enter?back=%2Fcontest%2F349%2Fsubmission%2F36519973'

        csrf_token = self.get_csrf_token()
        post_data = {'handle': kwargs['account'].get_username(), 'password': kwargs['account'].get_password(),
                     'action': 'enter', 'csrf_token': csrf_token}
        try:
            res = self.req.post(url=login_link_url, data=post_data,
                                params={'back': '/'})
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        pid = kwargs.get('pid')
        url = 'http://codeforces.com/problemset/problem/' + pid[:-1] + '/' + pid[-1:]
        problem = Problem()
        try:
            website_data = self.req.get(url)
            problem.remote_id = kwargs.get('pid')
            problem.remote_url = url
            problem.remote_oj = 'CODEFORCES'
            problem.title = re.search(r'class="title">([\s\S]*?)</div>',
                                      website_data.text).group(1)
            temp_result = re.search(r'time-limit"><div class="property-title">([\s\S]*?)</div>([\s\S]*?)</div>',
                                    website_data.text)
            problem.time_limit = temp_result.group(1) + ': ' + temp_result.group(2)
            temp_result = re.search(r'class="memory-limit"><div class="property-title">([\s\S]*?)</div>([\s\S]*?)</div>',
                                    website_data.text)
            problem.memory_limit = temp_result.group(1) + ': ' + temp_result.group(2)
            problem.special_judge = None
            problem.description = re.search(r'class="property-title">' 
                                            '([\s\S]*?)</div>([\s\S]*?)</div>'
                                            '([\s\S]*?)<div>([\s\S]*?)</div>', website_data.text).group(4)
            problem.input = re.search(r'class="section-title">Input</div>([\s\S]*?)</div>', website_data.text).group(1)
            problem.output = re.search(r'class="section-title">Output</div>([\s\S]*?)</div>', website_data.text).group(1)

            input_data = ''
            soup = BeautifulSoup(website_data.text, 'lxml')
            lines = soup.find_all('div', attrs={'class': 'input'})
            if lines:
                for line in lines:
                    input_data += str(line.find('pre')) + '\n'

            output_data = ''
            lines = soup.find_all('div', attrs={'class': 'output'})
            if lines:
                for line in lines:
                    output_data += str(line.find('pre')) + '\n'

            problem.sample = [
                {'input': input_data,
                 'output': output_data}]

            temp_result = re.search(r'div class="note">([\s\S]*?)</div>([\s\S]*?)</div>', website_data.text).group(2)
            problem.hint = temp_result

        except:
            return None

    def find_language(self, *args, **kwargs):
        url = 'http://codeforces.com/problemset/submit'
        language = {}

        try:
            res = self.req.get(url=url)
            soup = BeautifulSoup(res.text, 'lxml')
            options = soup.find('select', attrs={'name': 'programTypeId'}).find_all('option')
            for option in options:
                language[option.get('value')] = option.string
        finally:
            return language


    def submit_code(self, *args, **kwargs):
        if not self.login_website(*args, **kwargs):
            return False
        try:
            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            #contestId = pid[:-1]
            #problemIndex = pid[-1:]
            csrf_token = self.get_csrf_token()
            url = 'http://codeforces.com/problemset/submit'
            post_data = {'csrf_token': csrf_token, 'action': 'submitSolutionFormSubmitted',
                         'submittedProblemCode': pid,
                         'programTypeId': language, 'source': code}

            res = self.req.post(url=url, data=post_data)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    def get_result_by_rid(self, rid):
        pass

    def get_result_by_url(self, url):
        result = Result()
        try:
            data = self.req.get(url)
            data = BeautifulSoup(data.text, 'lxml')
            line = data.find_all('td', attrs={})
            if line:
                result.origin_run_id = line[0].get_text().strip().replace('\n', '')
                result.verdict = line[4].get_text().strip().replace('\n', '')
                result.execute_time = line[5].get_text().strip().replace('\n', '')
                result.execute_memory = line[6].get_text().strip().replace('\n', '')
                return result
        except:
            pass
        return result

    def get_result(self, *args, **kwargs):
        pid = kwargs.get('pid')
        rid = kwargs.get('rid')
        url = 'http://codeforces.com/contest/' + pid[:-1] + '/submission/' + rid
        self.get_result_by_url(url=url)

    def get_class_name(self):
        return str('CODEFORCES')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Queuing', 'Compiling', 'Runing']:
            return True
        return False

    def check_status(self):
        url = 'http://codeforces.com/'
        try:
            website_data = self.req.get(url)
            if re.search(r'led">&rarr; Pay attention', website_data.text):
                return True
        except:
            return False


if __name__ == '__main__':
    oj = CODEFORCES()
    oj.get_result(pid='754A', rid='36867638')


