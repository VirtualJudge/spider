import re

from bs4 import BeautifulSoup
from bs4 import element

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base, BaseParser
from ..Utils import HttpUtil, HtmlTag


class HDUParser(BaseParser):
    def __init__(self):
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
    <script src="//cdn.bootcss.com/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>"""

    def problem_parse(self, response, pid, url):
        problem = Problem()

        problem.remote_id = pid
        problem.remote_url = url
        problem.remote_oj = 'HDU'

        if response is None:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        website_data = response.text
        status_code = response.status_code

        if status_code != 200:
            problem.status = Problem.Status.STATUS_NETWORK_ERROR
            return problem
        if re.search('No such problem', website_data):
            problem.status = Problem.Status.STATUS_PROBLEM_NOT_EXIST
            return problem
        try:
            soup = BeautifulSoup(website_data, 'lxml')
            problem.title = re.search(r'color:#1A5CC8\'>([\s\S]*?)</h1>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* MS)', website_data).group(1)
            problem.memory_limit = re.search(r'/(\d* K)', website_data).group(1)
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
            problem.status = Problem.Status.STATUS_CRAWLING_SUCCESS
        except:
            problem.status = Problem.Status.STATUS_PARSE_ERROR
        finally:
            return problem

    def result_parse(self, website_data):
        result = Result()
        try:
            soup = BeautifulSoup(website_data, 'lxml')
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
        return None


class HDU(Base):
    def __init__(self):
        self._req = HttpUtil(custom_headers=Config.custom_headers)

    @staticmethod
    def home_page_url():
        url = 'http://acm.hdu.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.hdu.edu.cn/'
        try:
            website_data = self._req.get(url)
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
            self._req.post(url=login_link_url, data=post_data,
                           params={'action': 'login'})
            if self.check_login_status():
                return True
            return False
        except:
            return False

    def get_problem(self, *args, **kwargs):
        pid = str(kwargs['pid'])
        url = 'http://acm.hdu.edu.cn/showproblem.php?pid=' + pid
        res = self._req.get(url)
        return HDUParser().problem_parse(res, pid, url)

    def submit_code(self, *args, **kwargs):
        if not self.login_webside(*args, **kwargs):
            return False
        try:
            code = kwargs.get('code')
            language = kwargs.get('language')
            pid = kwargs.get('pid')
            url = 'http://acm.hdu.edu.cn/submit.php'
            post_data = {'check': '0', 'language': language, 'problemid': pid, 'usercode': code}
            res = self._req.post(url=url, data=post_data, params={'action': 'submit'})
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
            website_data = self._req.get(url)
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
            res = self._req.get(url)
            return HDUParser().result_parse(res.text)
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
            website_data = self._req.get(url)
            if re.search(r'<H1>Welcome to HDU Online Judge System</H1>', website_data.text):
                return True
        except:
            return False
