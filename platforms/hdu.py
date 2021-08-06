import re
import time

from bs4 import BeautifulSoup
from bs4 import element

from platforms.base import Base, BaseParser
from utils import config
from utils.config import Problem, Result, HttpUtil, HtmlTag
from utils.exceptions import *


class HDUParser(BaseParser):
    def __init__(self, *args, **kwargs):
        self._static_prefix = 'http://acm.hdu.edu.cn/'
        self._script = """<script type="text/x-mathjax-config">
     MathJax.Hub.Config({
      showProcessingMessages: false,
      messageStyle: "none",
      extensions: ["tex2jax.js"],
      jax: ["input/TeX", "output/HTML-CSS"],
      tex2jax: {
          inlineMath:  [ ["$", "$"] ],
          displayMath: [ ["$$","$$"] ],
          skipTags: ['script', 'noscript', 'style', 'textarea', 'pre','code','a']
      },
      "HTML-CSS": {
          availableFonts: ["STIX","TeX"],
          showMathMenu: false
      }
     });
    </script>
    <script src="https://cdn.bootcss.com/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>"""

    def problem_parse(self, response, pid, url):
        problem = Problem()

        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'HDU'

        if response is None:
            raise SpiderNetworkError("Empty Response")

        website_data = response.text
        status_code = response.status_code

        if status_code != 200:
            raise SpiderNetworkError("")
        if re.search('No such problem', website_data):
            raise SpiderProblemParseError("No such problem")
        soup = BeautifulSoup(website_data, 'lxml')

        match_groups = re.search(r'color:#1A5CC8\'>([\s\S]*?)</h1>', website_data)
        if match_groups:
            problem.title = match_groups.group(1)
        match_groups = re.search(r'(\d* MS)', website_data)
        if match_groups:
            problem.time_limit = match_groups.group(1)
        match_groups = re.search(r'/(\d* K)', website_data)
        if match_groups:
            problem.memory_limit = match_groups.group(1)
        problem.special_judge = re.search(r'color=red>Special Judge</font>', website_data) is not None

        problem.html = ''
        for tag in soup.find('h1').parent.children:
            if type(tag) == element.Tag and tag.get('class') and set(tag['class']).intersection({'panel_title',
                                                                                                 'panel_content',
                                                                                                 'panel_bottom'}):
                if set(tag['class']).intersection({'panel_title', }):
                    tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                    tag['style'] = HtmlTag.TagStyle.TITLE.value
                else:
                    tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                    tag['style'] = HtmlTag.TagStyle.CONTENT.value
                problem.html += str(HtmlTag.update_tag(tag, self._static_prefix))
        problem.html += self._script
        return problem

    @staticmethod
    def result_parse(response):
        result = Result()
        if response is None or response.status_code != 200:
            raise SpiderNetworkError("Network error")
        website_data = response.text
        soup = BeautifulSoup(website_data, 'lxml')
        line = soup.find('table', attrs={'class': 'table_text'}).find('tr', attrs={'align': 'center'}).find_all('td')
        if line is None:
            raise SpiderProblemParseError("Parse Error")
        result.unique_key = line[0].string
        result.verdict_info = line[2].get_text()
        result.execute_time = line[4].string
        result.execute_memory = line[5].string
        return result

    @staticmethod
    def problem_list_parse(response):
        ret = []
        if response.status_code != 200 or response.text == None:
            return ret
        soup = BeautifulSoup(response.text, 'lxml')
        raw_problems = str(soup.find('table', 'table_text').find('script').string).split(';')
        for item in raw_problems:
            if item.startswith('p('):
                ret.append(item.split(',')[1])
        return ret


class HDU(Base):
    def __init__(self, account, *args, **kwargs):
        super().__init__(account, *args, **kwargs)
        self._code_type = 'gb18030'
        self._req = HttpUtil(headers=config.default_headers, code_type=self._code_type,
                             *args, **kwargs)
        if self._account and self.account.cookies:
            self._req.cookies.update(self.account.cookies)

    def is_login(self):
        url = 'http://acm.hdu.edu.cn/'
        res = self._req.get(url)
        if res and re.search(r'userloginex\.php\?action=logout', res.text) is not None:
            self.account.set_cookies(self._req.cookies.get_dict())
            return True
        return False

    def login_website(self):
        if self.is_login():
            return True
        login_link_url = 'http://acm.hdu.edu.cn/userloginex.php'
        post_data = {'username': self._account.username,
                     'userpass': self._account.password,
                     'login': 'Sign In'
                     }
        self._req.post(url=login_link_url, data=post_data,
                       params={'action': 'login'})
        return self.is_login()

    def get_problem(self, pid):
        url = 'http://acm.hdu.edu.cn/showproblem.php?pid=' + pid
        res = self._req.get(url)
        return HDUParser().problem_parse(res, pid, url)

    def submit_code(self, pid, language, code):
        if not self.login_website():
            raise SpiderAccountLoginError("Login error")
        submit_url = 'http://acm.hdu.edu.cn/submit.php'
        post_data = {'check': '0', 'language': language, 'problemid': pid, 'usercode': code}
        self._req.post(url=submit_url, data=post_data, params={'action': 'submit'})

        while True:
            time.sleep(1)
            status_url = f'http://acm.hdu.edu.cn/status.php?first=&pid=${pid}&user={self.account.username}&lang=0&status=0'
            result = HDUParser().result_parse(self._req.get(status_url))
            if str(result.verdict_info) not in ['Queuing', 'Compiling', 'Running']:
                break
        if str(result.verdict_info) == 'Accepted':
            result.verdict = Result.Verdict.ACCEPTED
        elif str(result.verdict_info) == 'Compilation Error':
            result.verdict = Result.Verdict.COMPILE_ERROR
        elif str(result.verdict_info) == 'Time Limit Exceeded':
            result.verdict = Result.Verdict.TIME_LIMIT_EXCEEDED
        elif str(result.verdict_info).startswith('Runtime Error'):
            result.verdict = Result.Verdict.RUNTIME_ERROR
        elif str(result.verdict_info).startswith('Presentation Error'):
            result.verdict = Result.Verdict.PRESENTATION_ERROR
        elif str(result.verdict_info).startswith('Output Limit Exceeded'):
            result.verdict = Result.Verdict.OUTPUT_LIMIT_EXCEEDED
        elif str(result.verdict_info).startswith('Memory Limit Exceeded'):
            result.verdict = Result.Verdict.MEMORY_LIMIT_EXCEEDED
        else:
            result.verdict = Result.Verdict.WRONG_ANSWER
        result.execute_time = str(result.execute_time).strip()
        result.execute_memory = str(result.execute_memory).strip()
        return result

    def is_working(self):
        url = 'http://acm.hdu.edu.cn/'
        res = self._req.get(url)
        if res and re.search(r'<H1>Welcome to HDU Online Judge System</H1>', res.text):
            return True
        return False

    def get_problem_list(self):
        """
        获得当前平台所有题目的编号
        """
        page_idx = 1
        all_problem_ids = []
        while True:
            page_url = f'https://acm.hdu.edu.cn/listproblem.php?vol={page_idx}'
            cur_page = HDUParser.problem_list_parse(self._req.get(page_url))
            if len(cur_page) > 0:
                all_problem_ids += cur_page
            else:
                break
            page_idx += 1
        return all_problem_ids


if __name__ == '__main__':
    oj = HDU(None)
    oj.get_problem_list()
