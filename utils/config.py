import logging
import os
from enum import Enum

import requests
from bs4 import element
from requests import RequestException
import traceback

LOG_BASE = '/log' if os.getenv('VJ_ENV') == 'production' else 'log'
LOG_LEVEL = logging.WARNING if os.getenv('VJ_ENV') == 'production' else logging.INFO
SPIDER_LOG_PATH = os.path.join(LOG_BASE, 'spider.log')
try:
    os.makedirs(LOG_BASE)
except FileExistsError:
    pass
except:
    traceback.print_exc()
logger = logging.getLogger(__name__)
handler = logging.FileHandler(SPIDER_LOG_PATH) if os.getenv('VJ_ENV') == 'production' else logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

default_headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


class Account:
    def __init__(self):
        self._username = None
        self._password = None

        self._key = None

        self._cookies = None

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def cookies(self):
        return self._cookies

    @property
    def key(self):
        return self._key

    def to_json(self):
        return {
            'username': str(self._username),
            'password': str(self._password),
            'key': str(self._key),
            'cookies': str(self._cookies),
        }

    def from_json(self, data: dict):
        self._username = data['username']
        self._password = data['password']
        self._key = data['key']
        self._cookies = data['cookies']


class HttpUtil(object):
    def __init__(self, headers=None, code_type=None, cookies=None, *args, **kwargs):
        self._headers = headers
        self._request = requests.session()
        self._code_type = code_type
        self._timeout = (7, 12)
        self._response = None
        self._advanced = False
        self._proxies = None
        if kwargs.get('proxies'):
            self._proxies = {
                'http': kwargs.get('proxies'),
                'https': kwargs.get('proxies')
            }
        if self._headers:
            self._request.headers.update(self._headers)
        if cookies:
            self._request.cookies.update(cookies)

    def get(self, url, **kwargs):
        try:
            self._response = self._request.get(url, timeout=self._timeout, proxies=self._proxies, **kwargs)
            if self._code_type and self._response:
                self._response.encoding = self._code_type
            return self._response
        except RequestException as e:
            logger.exception(e)
            return None

    def post(self, url, data=None, json=None, **kwargs):
        try:
            self._response = self._request.post(url, data, json, timeout=self._timeout, proxies=self._proxies, **kwargs)
            if self._code_type and self._response:
                self._response.encoding = self._code_type
            return self._response
        except RequestException as e:
            logger.exception(e)
            return None

    @property
    def headers(self):
        return self._request.headers

    @property
    def cookies(self):
        return self._request.cookies

    @staticmethod
    def abs_url(remote_path, oj_prefix):
        """
        :param remote_path: 原本的文件路径，可能是相对路径也可能是http或https开始的路径
        :param oj_prefix: oj的static文件前缀
        :return: 文件名，原本的补全之后的路径
        """
        if not remote_path.startswith('http://') and not remote_path.startswith('https://'):
            remote_path = oj_prefix.rstrip('/') + '/' + remote_path.lstrip('/')
        file_name = str(str(remote_path).split('/')[-1])
        return file_name, remote_path


class HtmlTag(object):
    class TagDesc(Enum):
        """
        给html的tag加上相应的class
        TITLE = 'vj-title'
        CONTENT = 'vj-content'
        IMAGE = 'vj-image'
        FILE = 'vj-file'
        ANCHOR = 'vj-anchor'
        """
        TITLE = 'vj-title'
        CONTENT = 'vj-content'
        IMAGE = 'vj-image'
        FILE = 'vj-file'
        ANCHOR = 'vj-anchor'

    class TagStyle(Enum):
        """
        TITLE 和 CONTENT 需要加额外的 Style 保证网页风格一致
        """
        TITLE = 'font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB"' \
                ',"Microsoft YaHei","微软雅黑",Arial,sans-serif; font-size: 16px;font-weight: bold;color:#000000;'
        CONTENT = 'font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB",' \
                  '"Microsoft YaHei","微软雅黑",Arial,sans-serif; font-size: 16px;color:#495060;'

    @staticmethod
    def update_tag(tag, oj_prefix, update_style=None):
        """
        :param tag: 一个顶级tag，从这个tag递归遍历所有子tag，寻找需要修改url的节点
        :param oj_prefix: 原oj的静态文件前缀
        :param update_style: 不为空的话，递归修改内联style
        :return: 成功返回原tag，失败返回None
        """
        if type(tag) == element.Tag:
            for child in tag.descendants:
                if type(child) == element.Tag and update_style:
                    child['style'] = update_style
                if child.name == 'a' and child.get('href'):
                    if not child.get('class'):
                        child['class'] = ()
                    child['class'] += (HtmlTag.TagDesc.ANCHOR.value,)
                    child['target'] = ('_blank', '_parent')
                    child['href'] = HttpUtil.abs_url(child.get('href'), oj_prefix=oj_prefix)[-1]
                if child.name == 'img' and child.get('src'):
                    if not child.get('class'):
                        child['class'] = ()
                    child['class'] += (HtmlTag.TagDesc.IMAGE.value,)
                    child['src'] = HttpUtil.abs_url(child.get('src'), oj_prefix=oj_prefix)[-1]
        return tag


class Problem(object):
    """
    从原网站抓取的题目对象
    """

    def __init__(self):
        self.remote_id = None
        self.remote_oj = None
        self.remote_url = None
        self.title = None
        self.time_limit = None
        self.memory_limit = None
        self.special_judge = None
        # 这个属性是html代码，直接在网页中用iframe展示
        self.html = None
        # 这个属性代表使用的开源OJ类型，比如hustoj,qduoj等。
        self.template = None


class Result(object):
    def __init__(self):
        self.run_id = None
        self.verdict = None  # 枚举变量
        self.verdict_info = None  # 原OJ的提示信息
        self.execute_time = None
        self.execute_memory = None
        self.compile_info = None  # 编译信息，CE时可用

    def to_dict(self):
        return {
            'run_id': self.run_id,
            'verdict': self.verdict.name,
            'verdict_info': self.verdict_info,
            'execute_time': self.execute_time,
            'execute_memory': self.execute_memory,
            'compile_info': self.compile_info
        }

    class Verdict(Enum):
        PENDING = 'P'
        RUNNING = 'R'
        ACCEPTED = 'AC'
        PARTIAL_ACCEPTED = 'PA'
        PRESENTATION_ERROR = 'PE'
        TIME_LIMIT_EXCEEDED = 'TLE'
        MEMORY_LIMIT_EXCEEDED = 'MLE'
        WRONG_ANSWER = 'WA'
        RUNTIME_ERROR = 'RE'
        OUTPUT_LIMIT_EXCEEDED = 'OLE'
        COMPILE_ERROR = 'CE'
        SYSTEM_ERROR = 'SE'
