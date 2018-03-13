import re
from http import cookiejar
from urllib import request, parse

from bs4 import BeautifulSoup
import bs4

from OnlineJudgeSpider import Config
from OnlineJudgeSpider.Config import Problem, Spider, Result
from OnlineJudgeSpider.OJs.BaseClass import Base


class WUST(Base):
    def __init__(self):
        self.code_type = 'UTF-8'
        self.cj = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))
        self.headers = Config.custom_headers;
        self.headers['Connection'] = 'keep-alive'
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        self.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        self.headers[
            'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'

    @staticmethod
    def home_page_url(self):
        url = 'http://acm.wust.edu.cn/'
        return url

    def check_login_status(self):
        url = 'http://acm.wust.edu.cn/index.php'
        try:
            with self.opener.open(url) as fin:
                website_data = fin.read().decode(self.code_type)

                if re.search(r'<a href="logout.php">Logout</a>', website_data) is not None:
                    return True
        except:
            return False

    def login_webside(self, *args, **kwargs):
        if self.check_login_status():
            return True
        login_page_url = 'http://acm.wust.edu.cn/loginpage.php'
        login_link_url = 'http://acm.wust.edu.cn/login.php'

        post_data = parse.urlencode(
            {'user_id': kwargs['account'].get_username(), 'password': kwargs['account'].get_password(),
             'submit': 'Submit'})
        try:
            self.opener.open(login_page_url)
            req = request.Request(url=login_link_url, data=post_data.encode(self.code_type),
                                  headers=self.headers)
            response = self.opener.open(req)

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

    def get_problem(self, *args, **kwargs):
        url = 'http://acm.wust.edu.cn/problem.php?id=' + str(kwargs['pid']) + '&soj=0'
        problem = Problem()
        try:
            website_data = Spider.get_data(url, self.code_type)

            problem.remote_id = kwargs['pid']
            problem.remote_url = url
            problem.remote_oj = 'WUST'
            problem.title = re.search(r': ([\s\S]*?)</h2>', website_data).group(1)
            problem.time_limit = re.search(r'(\d* Sec)', website_data).group(1)
            problem.memory_limit = re.search(r'(\d* MB)', website_data).group(1)
            problem.special_judge = re.search(r'class=red>Special Judge</span>', website_data) is not None

            soup = BeautifulSoup(website_data, 'lxml')
            texts = soup.find_all(attrs={'class': 'text'})
            #-------------------------------------------------------------------------------------------------------
            description = soup.find('h2', text='Description').next_siblings
            for tag in description:
                if tag.name == 'div':
                    description = tag
                    break
            # print(description)
            ans = ''
            try:
                for child in description.children:
                    ans = ans + self.find_texts(child)
                    # print(child)
            except Exception as e:
                print(e)
            problem.description = ans.strip()
            #print(problem.description)
            #---------------------------------------------------------------------------------------------------------
            problem.input = texts[1].get_text()
            problem.output = texts[2].get_text()

            input_data = ''
            match_group = re.search(
                r"class=sampledata id='sample_input'>([\s\S]*?)</span></pre></div><br><h2>Sample Output", website_data)
            if match_group:
                input_data = match_group.group(1)

            output_data = ''
            match_group = re.search(r"<div><pre class=text><span class=sampledata>([\S\s]*?)</span></pre></div><br>",
                                    website_data)
            if match_group:
                output_data = match_group.group(1)

            problem.sample = [
                {'input': input_data,
                 'output': output_data}]
            #-----------------------------------------------------------------------------------------------------
            match_group = re.search(r'HINT</h2>[\s\S]*?<div class=text><p>([\s\S]*?)</p></p>', website_data)
            if match_group:
                hint = soup.find('h2', text='HINT').next_siblings
                for tag in hint:
                    if tag.name=='div':
                        hint=tag
                        break
                #print(hint)
                ans = ''
                try:
                    for child in hint.children:
                        ans = ans + self.find_texts(child)
                        #print(child)
                except Exception as e:
                    print(e)
                problem.hint = ans.strip()
                #print(problem.hint)
            #-------------------------------------------------------------------------------------------------------
            match_group = re.search(r'Author</h2>[\s\S]*?<div class=text><p>([\s\S]*?)</p></div>', website_data)
            if match_group:
                problem.author = match_group.group(1)

            match_group = re.search(r'Source</h2>[\s\S]*?<div class=text>([\s\S]*?)</div>', website_data)
            if match_group:
                source = soup.find('h2', text='Source').next_siblings
                for tag in source:
                    if tag.name == 'div':
                        source = tag
                        break
                # print(source)
                ans = ''
                try:
                    for child in source.children:
                        ans = ans + self.find_texts(child)
                        # print(child)
                except Exception as e:
                    print(e)
                problem.source = ans.strip()

        finally:
            return problem

    def submit_code(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return False
        try:

            code = kwargs['code']
            language = kwargs['language']
            pid = kwargs['pid']
            link_page_url = 'http://acm.wust.edu.cn/submitpage.php?id=' + str(pid) + '&soj=0'
            link_post_url = 'http://acm.wust.edu.cn/submit.php?'
            self.headers['Referer'] = link_page_url
            submitkey = ''

            with self.opener.open(link_page_url) as response:
                soup = BeautifulSoup(response, 'lxml')
                submitkey = soup.find('input', attrs={'name': 'submitkey'})['value']
                # 获取提交的语言信息
                languages = self.find_language(soup=soup)
                # 语言字典键值反转
                languages = {value: key for key, value in languages.items()}
                # 字典键值映射
                language = languages[language]
            post_data = parse.urlencode(
                {'id': str(pid), 'soj': '0', 'language': language, 'source': code, 'submitkey': str(submitkey)})
            req = request.Request(url=link_post_url, data=post_data.encode(self.code_type), headers=self.headers)
            response = self.opener.open(req)
            return True
        except:
            return False

    def find_language(self, *args, **kwargs):
        if self.login_webside(*args, **kwargs) is False:
            return None
        soup = kwargs['soup']
        languages = {}
        try:
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

    '''
    def get_result_by_rid(self, rid):
        url = 'http://acm.hdu.edu.cn/status.php?first=' + rid + '&pid=&user=&lang=0&status=0'
        return self.get_result_by_url(url=url)
    '''

    def get_result_by_url(self, url):
        result = Result()
        try:
            with request.urlopen(url) as fin:
                data = fin.read().decode(self.code_type)
                soup = BeautifulSoup(data, 'lxml')
                line = soup.find('table', attrs={'id': 'result-tab'}).find('tr', attrs={'class': 'evenrow'}).find_all(
                    'td')
                if line is not None:
                    result.origin_run_id = line[0].string
                    result.verdict = line[4].string
                    result.execute_time = line[6].string
                    result.execute_memory = line[5].string
        finally:
            return result

    def get_class_name(self):
        return str('WUST')

    def is_waiting_for_judge(self, verdict):
        if verdict in ['Pending', 'Pending Rejudge', 'Compiling', 'Running & Judging']:
            return True
        return False

    def check_status(self):
        url = 'http://acm.wust.edu.cn/'
        try:
            with request.urlopen(url, timeout=5) as fin:
                data = fin.read().decode(self.code_type)
                if re.search(r'<a href="index.php">WUST Online Judge</a>', data):
                    return True
        except:
            return False
