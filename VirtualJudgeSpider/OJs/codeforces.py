import re

from bs4 import BeautifulSoup
from bs4 import element

from VirtualJudgeSpider.OJs.base import Base, BaseParser
from VirtualJudgeSpider.config import custom_headers, Problem, Account
from VirtualJudgeSpider.utils import HtmlTag
from VirtualJudgeSpider.utils import HttpUtil


class CodeforcesParser(BaseParser):
    def __init__(self):
        self._static_prefix = 'http://codeforces.com/'
        self._script = """
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
 showProcessingMessages: false,
 messageStyle: "none",
 extensions: ["tex2jax.js"],
 jax: ["input/TeX", "output/HTML-CSS"],
 tex2jax: {
     inlineMath:  [ ["$$$", "$$$"] ],
     displayMath: [ ["$$","$$"] ],
     skipTags: ['script', 'noscript', 'style', 'textarea', 'pre','code','a']
 },
 "HTML-CSS": {
     availableFonts: ["STIX","TeX"],
     showMathMenu: false
 }
});
</script>
<script src="https://cdn.bootcss.com/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
"""

    def problem_parse(self, response, pid, url):
        problem = Problem()
        problem.remote_oj = 'Codeforces'
        problem.remote_id = pid
        problem.remote_url = url
        if response is None:
            problem.status = Problem.Status.STATUS_SUBMIT_FAILED
            return problem
        elif response.status_code == 302:
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        elif response.status_code != 200:
            problem.status = Problem.Status.STATUS_SUBMIT_FAILED
            return problem
        elif response.text is None:
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        website = response.text
        soup = BeautifulSoup(website, 'lxml')
        match_groups = soup.find(name='div', attrs={'class': 'time-limit'})
        if match_groups:
            problem.time_limit = match_groups.contents[-1]
        match_groups = soup.find(name='div', attrs={'class': 'memory-limit'})
        if match_groups:
            problem.memory_limit = match_groups.contents[-1]
        match_groups = soup.find(name='div', attrs={'class': 'problem-statement'})
        problem.html = ''
        if match_groups and isinstance(match_groups, element.Tag):
            print(match_groups)
            for child in match_groups.children:
                if isinstance(child, element.Tag) and child.get('class') and set(child['class']).intersection(
                        {'header'}):
                    pass
                elif isinstance(child, element.Tag):
                    for tag in child:
                        if isinstance(tag, element.Tag):
                            if tag.get('class') is None:
                                tag['class'] = ()
                            if tag.get('class') and set(tag['class']).intersection({'section-title'}):
                                tag['class'] += (HtmlTag.TagDesc.TITLE.value,)
                                tag['style'] = HtmlTag.TagStyle.TITLE.value
                            else:
                                tag['class'] += (HtmlTag.TagDesc.CONTENT.value,)
                                tag['style'] = HtmlTag.TagStyle.CONTENT.value
                    problem.html += str(HtmlTag.update_tag(child, self._static_prefix))
                else:
                    problem.html += str(HtmlTag.update_tag(child, self._static_prefix))
        problem.html = '<html>' + problem.html + self._script + '</html>'
        print(problem.html)
        return problem

    def result_parse(self, response):
        pass


class Codeforces(Base):
    def __init__(self, cookies=None):
        self._bfaa = '32782a5d13ff8f38dd0b9a2dddcff6ef'
        self._ftaa = 'rayyydfdyxlkydjl9e'
        self._req = HttpUtil(custom_headers=custom_headers)

    # 主页链接
    @staticmethod
    def home_page_url():
        return 'http://codeforces.com/'

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if type(cookies) == dict:
            self._req.cookies.update(cookies)

    def get_csrf_token(self):
        page = self._req.get(self.home_page_url())
        soup = BeautifulSoup(page.text, 'lxml')
        item = soup.find('meta', attrs={'name': 'X-Csrf-Token'})
        csrf_token = item['content']
        return csrf_token

    # 登录页面
    def login_website(self, account, *args, **kwargs):
        if account and account.cookies:
            self._req.cookies.update(account.cookies)
        if self.check_login_status():
            return True
        login_link_url = 'http://codeforces.com/enter?back=%2F'

        csrf_token = self.get_csrf_token()
        post_data = {'handleOrEmail': account.username,
                     'password': account.password,
                     'ftaa': self._ftaa,
                     'bfaa': self._bfaa,
                     'action': 'enter',
                     'csrf_token': csrf_token}
        self._req.post(url=login_link_url, data=post_data)
        return self.check_login_status()

    # 检查登录状态
    def check_login_status(self):
        res = self._req.get(self.home_page_url())
        if res and res.status_code == 200 and res.text:
            if re.search(r'logout">Logout</a>', res.text) is not None:
                return True
        return False

    # 获取题目
    def get_problem(self, pid, *args, **kwargs):

        if len(str(pid)) < 2 or str(pid)[-1].isalpha() is False or str(pid)[:-1].isnumeric() is False:
            problem = Problem()
            problem.remote_oj = Codeforces.__name__
            problem.remote_id = pid
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        p_url = 'http://codeforces.com/problemset/problem/' + str(pid)[:-1] + '/' + str(pid)[-1]
        res = self._req.get(url=p_url)
        return CodeforcesParser().problem_parse(res, pid, p_url)

    # 提交代码
    def submit_code(self, *args, **kwargs):
        if not self.login_website(*args, **kwargs):
            return False
        code = kwargs.get('code')
        language = kwargs.get('language')
        pid = kwargs.get('pid')
        url = 'http://codeforces.com/problemset/submit?csrf_token=' + self.get_csrf_token()

        post_data = {
            'csrf_token': self.get_csrf_token(),
            'ftaa': self._ftaa,
            'bfaa': self._bfaa,
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemCode': pid,
            'programTypeId': language,
            'source': code,
            'tabSize': 4
        }
        res = self._req.post(url=url, data=post_data)
        if res and res.status_code == 302:
            return True
        return False

    # 获取当然运行结果
    def get_result(self, *args, **kwargs):
        pass

    # 根据源OJ的运行id获取结构
    def get_result_by_rid_and_pid(self, rid, pid):
        pass

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        pass

    # 获取源OJ支持的语言类型
    def find_language(self, *args, **kwargs):
        if self.login_website(*args, **kwargs) is False:
            return {}
        res = self._req.get('http://codeforces.com/problemset/submit')
        languages = {}
        if res and res.text and res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            tags = soup.find('select', attrs={'name': 'programTypeId'})
            if tags:
                for child in tags.find_all('option'):
                    languages[child.get('value')] = child.string
        return languages

    # 检查源OJ是否运行正常
    def check_status(self):
        res = self._req.get(self.home_page_url())
        if res and res.status_code == 200:
            return True
        return False

    #  判断结果是否正确
    @staticmethod
    def is_accepted(verdict):
        return verdict == 'Accepted'

    # 判断是否编译错误
    @staticmethod
    def is_compile_error(verdict):
        return verdict == 'Compilation error'

    # 判断是否运行中
    @staticmethod
    def is_running(verdict):
        return str(verdict).startswith('Running on test')


if __name__ == '__main__':
    # print(Codeforces().login_website(Account('robot4test', 'robot4test')))
    # print(Codeforces().get_problem('980C').__dict__)
    account = Account('robot4test', 'robot4test')
    result = Codeforces().find_language(account=account)

"""
1 GNU G++ 5.1.0
2 Microsoft Visual C++ 2010
3 Delphi 7
4 Free Pascal 3
6 PHP 7.0.12
7 Python 2.7
8 Ruby 2.0.0p645
9 C# Mono 5
10 GNU GCC 5.1.0
12 Haskell GHC 7.8.3
13 Perl 5.20.1
14 ActiveTcl 8.5
15 Io-2008-01-07 (Win32)
17 Pike 7.8
18 Befunge
19 OCaml 4.02.1
20 Scala 2.12
22 OpenCobol 1.0
25 Factor
26 Secret_171
27 Roco
28 D DMD32 v2.074.1
31 Python 3.6
32 Go 1.8
33 Ada GNAT 4
34 JavaScript V8 4.8.0
36 Java 1.8.0_131
38 Mysterious Language
39 FALSE
40 PyPy 2.7.13 (5.9.0)
41 PyPy 3.5.3 (5.10.0)
42 GNU G++11 5.1.0
43 GNU GCC C11 5.1.0
44 Picat 0.9
45 GNU C++11 5 ZIP
46 Java 8 ZIP
47 J
48 Kotlin 1.1.3-2
49 Rust 1.21
50 GNU G++14 6.4.0
51 PascalABC.NET 2
52 Clang++17 Diagnostics
53 GNU C++17 Diagnostics (DrMemory)
54 GNU G++17 7.2.0
"""
