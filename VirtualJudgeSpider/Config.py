from enum import Enum
import json

custom_headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


class Account:
    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password


class Problem(object):
    class Status(Enum):
        STATUS_CRAWLING_SUCCESS = 0
        STATUS_NETWORK_ERROR = 1
        STATUS_PROBLEM_NOT_EXIST = 2
        STATUS_PARSE_ERROR = 3

    def __init__(self):
        self.remote_id = None
        self.status = None
        self.remote_oj = None

        self.remote_url = None

        self.title = None
        self.time_limit = None
        self.memory_limit = None
        self.special_judge = None

        # 这个属性是html代码，直接在网页中用iframe展示
        self.html = None

    def get_dict(self):
        return self.__dict__

    def show(self):
        print(self.__dict__)


class Result:
    def __init__(self):
        self.origin_run_id = None
        self.verdict = None
        self.execute_time = None
        self.execute_memory = None

    def get_dict(self):
        return self.__dict__

    def show(self):
        print(json.dumps(self.__dict__, indent=4))
