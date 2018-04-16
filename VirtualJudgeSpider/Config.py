from enum import Enum

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
    """
    从原网站抓取的题目对象
    """

    class Status(Enum):
        """
        STATUS_PENDING = 0
        STATUS_RUNNING = 1
        STATUS_CRAWLING_SUCCESS = 2
        STATUS_NETWORK_ERROR = 3
        STATUS_PROBLEM_NOT_EXIST = 4
        STATUS_NO_ACCOUNT = 5
        STATUS_OJ_NOT_EXIST = 6
        STATUS_PARSE_ERROR = 7
        """
        STATUS_PENDING = 0
        STATUS_RUNNING = 1
        STATUS_CRAWLING_SUCCESS = 2
        STATUS_NETWORK_ERROR = 3
        STATUS_PROBLEM_NOT_EXIST = 4
        STATUS_NO_ACCOUNT = 5
        STATUS_OJ_NOT_EXIST = 6
        STATUS_PARSE_ERROR = 7

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


class Result(object):
    """
    从原网站抓取的返回结果对象
    """

    class Status(Enum):
        """
        STATUS_PENDING = 0
        STATUS_RUNNING = 1
        STATUS_RESULT = 2
        STATUS_NETWORK_ERROR = 3
        STATUS_RESULT_NOT_EXIST = 4
        STATUS_NO_ACCOUNT = 5
        STATUS_OJ_NOT_EXIST = 6
        STATUS_PARSE_ERROR = 7
        """
        STATUS_PENDING = 0
        STATUS_RUNNING = 1
        STATUS_RESULT = 2
        STATUS_NETWORK_ERROR = 3
        STATUS_RESULT_NOT_EXIST = 4
        STATUS_NO_ACCOUNT = 5
        STATUS_OJ_NOT_EXIST = 6
        STATUS_PARSE_ERROR = 7

    class VerdictCode(Enum):
        """
        STATUS_SUBMIT_FAILED = 0
        STATUS_RUNNING = 1
        STATUS_ACCEPT = 2
        STATUS_COMPILE_ERROR = 3
        STATUS_ERROR = 4

        """
        STATUS_RUNNING = 0
        STATUS_ACCEPTED = 1
        STATUS_COMPILE_ERROR = 2
        STATUS_RESULT_ERROR = 3
        STATUS_SUBMIT_FAILED = 4

    def __init__(self):
        self.origin_run_id = None
        self.verdict = None
        self.verdict_code = Result.VerdictCode.STATUS_RUNNING
        self.execute_time = None
        self.execute_memory = None
        self.status = None
        self.info = None
