from enum import Enum
from datetime import datetime
import json

default_headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


class Account:
    def __init__(self, username, password, cookies=None, previous=None):
        self._username = username
        self._password = password
        self._cookies = cookies
        self._previous = previous

    def to_str(self):
        return json.dumps({
            'username': self._username,
            'password': self._password,
            'cookies': self._cookies,
            'previous': self._previous
        })

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
    def previous_utc(self):
        return self._previous

    def set_cookies(self, cookies):
        if type(cookies) != dict:
            raise TypeError(f'set_cookies() required {type(dict)} type, but we got {type(cookies)}')
        self._cookies = cookies

    def update_previous(self):
        self._previous = int(datetime.utcnow().timestamp())


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

    class Verdict(Enum):
        VERDICT_AC = 'AC'  # Accepted
        VERDICT_CE = 'CE'  # Compilation Error
        VERDICT_WA = 'WA'  # Wrong Answer
        VERDICT_MLE = 'MLE'  # Memory Limit Exceed
        VERDICT_TLE = 'TLE'  # Time Limit Exceed
        VERDICT_SE = 'SE'  # System Error
        VERDICT_IQ = 'IQ'  # In Queue
