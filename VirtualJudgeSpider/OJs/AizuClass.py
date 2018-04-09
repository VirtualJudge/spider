import json
import ssl
import traceback

import requests
from bs4 import BeautifulSoup
from bs4 import element

from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base, BaseParser
from VirtualJudgeSpider.Utils import HtmlTag

ssl._create_default_https_context = ssl._create_unverified_context


class AizuParser(BaseParser):

    def __init__(self):
        self._static_prefix = 'http://judge.u-aizu.ac.jp/onlinejudge/'
        self._judge_static_string = ['Compile Error', 'Wrong Answer', 'Time Limit Exceed',
                                     'Memory Limit Exceed', 'Accepted', 'Waiting',
                                     'Output Limit Exceed', 'Runtime Error', 'Presentation Error', 'Running']
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
  <script src="//cdn.bootcss.com/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>"""

    def problem_parse(self, website_data, pid, url):
        problem = Problem()
        site_data = json.loads(website_data)

        soup = BeautifulSoup(site_data.get('html'), 'lxml')

        problem.remote_id = pid
        problem.remote_oj = 'Aizu'
        problem.remote_url = url

        problem.title = str(soup.find('h1').string)
        problem.time_limit = str(site_data.get('time_limit')) + ' sec'
        problem.memory_limit = str(site_data.get('memory_limit')) + ' KB'
        problem.special_judge = False

        problem.html = ''

        for tag in soup.body:
            if type(tag) == element.Tag and tag.name in ['p', 'h2', 'pre','center']:
                if not tag.get('class'):
                    tag['class'] = ()
                if tag.name == 'h2':
                    tag['style'] = HtmlTag.TagStyle.TITLE.value
                    tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                else:
                    tag['style'] = HtmlTag.TagStyle.CONTENT.value
                    tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                problem.html += str(HtmlTag.update_tag(tag, self._static_prefix))
        problem.html += self._script
        return problem

    def result_parse(self, website_data):
        result = Result()
        try:
            site_data = json.loads(website_data)
            submission_record = site_data['submissionRecord']
            result.origin_run_id = str(submission_record['judgeId'])
            result.verdict = self._judge_static_string[int(submission_record['status'])]
            result.execute_time = str(format(float(submission_record['cpuTime']) / float(100), '.2f')) + ' s'
            result.execute_memory = str(submission_record['memory']) + ' KB'
            return result
        except:
            return None


class Aizu(Base):

    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}

        self._req = requests.session()
        self._req.headers.update(self.headers)

    # 主页链接
    @staticmethod
    def home_page_url():
        url = 'https://onlinejudge.u-aizu.ac.jp/'
        return url

    # 登录页面
    def login_webside(self, account, *args, **kwargs):
        if self.check_login_status(self, *args, **kwargs):
            return True
        login_link_url = 'https://judgeapi.u-aizu.ac.jp/session'
        post_data = {
            'id': account.username,
            'password': account.password
        }
        try:
            res = self._req.post(url=login_link_url, json=post_data)
            if res.status_code != 200:
                return False
            if self.check_login_status(self, *args, **kwargs):
                return True
            return False
        except:
            return False

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        url = 'https://judgeapi.u-aizu.ac.jp/self'
        try:
            res = self._req.get(url)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    # 获取题目
    def get_problem(self, *args, **kwargs):
        try:
            pid = kwargs['pid']
            url = 'https://judgeapi.u-aizu.ac.jp/resources/descriptions/en/' + str(pid)
            res = self._req.get(url)
            return AizuParser().problem_parse(res.text, pid, url)
        except:
            traceback.print_exc()
        return None

    # 提交代码
    def submit_code(self, *args, **kwargs):
        url = 'https://judgeapi.u-aizu.ac.jp/submissions'
        try:
            problemId = kwargs['pid']
            language = kwargs['language']
            sourceCode = kwargs['code']
            res = self._req.post(url, json.dumps(
                {'problemId': str(problemId), 'language': str(language), 'sourceCode': str(sourceCode)}))
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    # 获取当然运行结果
    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = str(kwargs.get('pid'))
        url = 'https://judgeapi.u-aizu.ac.jp/submission_records/users/' + str(account.username) + '/problems/' + pid
        res = self._req.get(url)
        if res.status_code != 200:
            return None
        recent_list = json.loads(res.text)
        url = 'https://judgeapi.u-aizu.ac.jp/verdicts/' + str(recent_list[0].get('judgeId'))
        return self.get_result_by_url(url)
        pass

    # 根据源OJ的运行id获取结构
    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'https://judgeapi.u-aizu.ac.jp/verdicts/' + str(rid)
        return self.get_result_by_url(url)
        pass

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        res = self._req.get(url)
        if res.status_code != 200:
            return None
        return AizuParser().result_parse(res.text)

    # 获取源OJ支持的语言类型
    def find_language(self, *args, **kwargs):
        return {'C': 'C', 'C++': 'C++', 'JAVA': 'JAVA', 'C++11': 'C++11', 'C++14': 'C++14', 'C#': 'C#', 'D': 'D',
                'Go': 'Go', 'Ruby': 'Ruby', 'Rust': 'Rust', 'Python': 'Python', 'Python3': 'Python3',
                'JavaScript': 'JavaScript', 'Scala': 'Scala', 'Haskell': 'Haskell', 'OCaml': 'OCaml', 'PHP': 'PHP',
                'Kotlin': 'Kotlin'}

    # 判断当前提交结果的运行状态
    def is_waiting_for_judge(self, verdict):
        if verdict in [5, 9]:
            return True
        return False

    # 检查源OJ是否运行正常
    def check_status(self):
        url = 'https://judgeapi.u-aizu.ac.jp/categories'
        try:
            res = self._req.get(url)
            if res.status_code == 200:
                return True
            return False
        except:
            return False
