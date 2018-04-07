import re
import traceback

import requests
from bs4 import BeautifulSoup

from VirtualJudgeSpider import Config
from VirtualJudgeSpider.Config import Problem, Result
from VirtualJudgeSpider.OJs.BaseClass import Base
import bs4
from ..utils import deal_with_image_url


class ZOJ(Base):
    def __init__(self):
        self.req = requests.Session()
        self.req.headers.update(Config.custom_headers)
        self.Tag = ""
        self.problem_dir = {"description": "", "Input": "", "Output": "", "Sample Input": "",
                            "Sample Output": "", "Author:": "", "Source:": "", "Hint": ""}
        self.raw_desc = {"description": [], "Input": [], "Output": [], "Sample Input": [],
                         "Sample Output": [], "Author:": [], "Source:": [], "Hint": []}
        self.List = ["description", "Input", "Output", "Sample Input", "Sample Output", "Author:", "Source:", "Hint"]

    @staticmethod
    def home_page_url():
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        return url

    def check_login_status(self):
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        try:
            website_data = self.req.get(url)
            if re.search(r'/onlinejudge/logout.do">Logout', website_data.text) is not None:
                return True
            return False
        except:
            return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_link_url = 'http://acm.zju.edu.cn/onlinejudge/login.do'
        post_data = {'handle': kwargs['account'].get_username(), 'password': kwargs['account'].get_password()}
        try:
            self.req.post(url=login_link_url, data=post_data)
            if self.check_login_status():
                return True
            return False
        except:
            return False

    # 获取每个标签的字符串
    def parse_html(self, tag):
        if type(tag) == bs4.element.NavigableString:
            if tag.strip() in self.List:
                self.Tag = tag.strip()
                return
            if self.Tag not in ["Sample Input", "Sample Output", "Hint"]:
                self.raw_desc[self.Tag].append(self.Strip(tag.strip()))
            else:
                self.raw_desc[self.Tag].append(tag.strip())
            return
        if tag.name == 'p' or tag.name == 'br':  # 使用</p>标记换行
            self.raw_desc[self.Tag].append('</' + 'p' + '>')
        if tag.name == 'img':
            self.raw_desc[self.Tag].append(str(tag))
        elif tag.name == 'a':
            self.raw_desc[self.Tag].append(str(tag))

        for child in tag.children:
            self.parse_html(child)

    # 去掉字符串中的换行
    def Strip(self, text):
        ans = ''
        for line in text:
            if line == '\n':
                continue
            ans += line
        return ans

    def fix_all(self, descList):
        descList_temp = descList.get()
        descList = Config.DescList()
        try:
            pre = descList_temp[0]
        except:
            return None
        text = ''
        for des in descList_temp:
            if des['type'] == pre['type']:
                if pre['type'] == 0:
                    text += des['content']
                else:
                    descList.append(Config.Desc(type=des['type'], content=des['content'], file_name=des['file_name'],
                                                origin=des['origin']))
            else:
                if pre['type'] == 0:
                    pre['content'] = text.lstrip()
                    descList.append(Config.Desc(type=pre['type'], content=pre['content'], file_name=pre['file_name'],
                                                origin=pre['origin']))
                    # print(text.strip())
                    text = ''
                if des['type'] == 0:
                    text += des['content']
                else:
                    descList.append(Config.Desc(type=des['type'], content=des['content'], file_name=des['file_name'],
                                                origin=des['origin']))
                pre = des
        if des['type'] == 0:
            pre['content'] = text.lstrip()
            # print(text.strip())
            descList.append(
                Config.Desc(type=pre['type'], content=pre['content'], file_name=pre['file_name'], origin=pre['origin']))
        return descList.get()

    # 还原标准形式
    def parse_text(self, raw_descs):
        descList = Config.DescList()
        for raw_desc in raw_descs:
            if raw_desc.strip():
                match_groups = re.search(r'<img[\s\S]*src=\"([\s\S]*?)\"', raw_desc)
                if match_groups:
                    file_name, remote_path = deal_with_image_url(str(match_groups.group(1)),
                                                                 'http://acm.zju.edu.cn/onlinejudge/')
                    descList.append(
                        Config.Desc(type=Config.Desc.Type.IMG,
                                    file_name=file_name,
                                    origin=remote_path))
                else:
                    match_groups = re.search(r'<a[\s\S]*href=\"([\s\S]*)\"[\s\S]*>([\s\S]*?)<', raw_desc)
                    if match_groups:
                        remote_path = str(match_groups.group(1))
                        if remote_path.startswith('/'):
                            remote_path = 'http://acm.zju.edu.cn/onlinejudge/' + remote_path
                        else:
                            remote_path = 'http://acm.zju.edu.cn/onlinejudge/' + remote_path

                        descList.append(
                            Config.Desc(type=Config.Desc.Type.ANCHOR,
                                        content=self.replace_p(match_groups.group(2)),
                                        origin=remote_path))
                    else:
                        descList.append(Config.Desc(type=Config.Desc.Type.TEXT, content=self.replace_p(raw_desc)))
        return self.fix_all(descList)

    def replace_p(self, text):
        text = text.strip()
        text = text.replace('</p></p>', '</p>')
        text = text.replace('</p>', '\n')
        return text

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=' + str(kwargs['pid'])
        problem = Problem()
        try:
            res = self.req.get(url)
            website_data = res.text
            problem.remote_id = str(kwargs['pid'])
            problem.remote_url = url
            problem.remote_oj = 'ZOJ'
            problem.title = re.search(r'<span class="bigProblemTitle">([\s\S]*?)</span>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* Second)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* KB)', website_data).group(1)
            problem.special_judge = re.search(r'<font color="blue">Special Judge</font>',
                                              website_data) is not None  # 1005

            soup = BeautifulSoup(website_data, 'lxml')
            # print(soup)
            hrs = soup.find_all('hr')
            hr = hrs[1]
            self.Tag = "description"
            for tag in hr.next_siblings:
                if type(tag) == bs4.element.Tag and tag.name == 'center':  # 跳出遍历
                    break
                else:
                    self.parse_html(tag)  # 寻找兄弟节点的字符串

            problem.description = self.parse_text(self.raw_desc['description'])
            problem.input = self.parse_text(self.raw_desc['Input'])
            problem.output = self.parse_text(self.raw_desc['Output'])
            input_data = self.parse_text(self.raw_desc['Sample Input'])
            output_data = self.parse_text(self.raw_desc['Sample Output'])
            problem.hint = self.parse_text(self.raw_desc['Hint'])
            problem.author = self.parse_text(self.raw_desc['Author:'])
            problem.source = self.parse_text(self.raw_desc['Source:'])
            problem.sample = [
                {'input': input_data,
                 'output': output_data}]
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
            problem_url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=' + str(pid)
            res = self.req.get(problem_url)
            website_data = res.text
            problem_id = re.search('problemId=(\d*)"><font color="blue">Submit</font>', website_data).group(1)
            url = 'http://acm.zju.edu.cn/onlinejudge/submit.do?problemId=' + str(problem_id)
            post_data = {'languageId': str(language), 'problemId': str(pid), 'source': code}
            res = self.req.post(url=url, data=post_data)
            if res.status_code == 200:
                return True
            return False
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        url = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=1001'
        languages = {}
        try:
            website_data = self.req.get(url)
            soup = BeautifulSoup(website_data.text, 'lxml')
            options = soup.find('select', attrs={'name': 'languageId'}).find_all('option')
            for option in options:
                languages[option.get('value')] = option.string
        finally:
            return languages

    def get_result(self, *args, **kwargs):
        account = kwargs.get('account')
        pid = kwargs.get('pid')
        url = 'http://acm.zju.edu.cn/onlinejudge/showRuns.do?contestId=1&search=true&firstId=-1&lastId=-1&problemCode=' + str(
            pid) + '&handle=' + account.username + '&idStart=&idEnd='
        return self.get_result_by_url(url=url)

    def get_result_by_rid_and_pid(self, rid, pid):
        url = 'http://acm.zju.edu.cn/onlinejudge/showRuns.do?contestId=1&search=true&firstId=-1&lastId=-1&problemCode=&handle=&idStart=' + str(
            rid) + '&idEnd=' + str(rid)
        return self.get_result_by_url(url=url)

    def get_result_by_url(self, url):
        result = Result()
        try:
            data = self.req.get(url)
            soup = BeautifulSoup(data.text, 'lxml')
            line = soup.find('table', attrs={'class': 'list'}).find('tr', attrs={'class': 'rowOdd'}).find_all(
                'td')
            if line:
                result.origin_run_id = line[0].string
                result.verdict = line[2].get_text().strip()
                result.execute_time = line[5].string
                result.execute_memory = line[6].string
                return result
        except:
            pass
        return result

    def get_class_name(self):
        return str('ZOJ')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Queuing']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.zju.edu.cn/onlinejudge/'
        try:
            website_data = self.req.get(url)
            if re.search(r'<div class="welcome_msg">Welcome to ZOJ</div>', website_data.text):
                return True
        except:
            return False
