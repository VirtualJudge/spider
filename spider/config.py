from enum import Enum

default_headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


class Account:
    def __init__(self, username, password, cookies=None):
        self._username = username
        self._password = password
        self._cookies = cookies

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def cookies(self):
        return self._cookies

    def set_cookies(self, cookies):
        if type(cookies) != dict:
            raise TypeError(f'set_cookies() required {type(dict)} type, but we got {type(cookies)}')
        self._cookies = cookies


class Problem(object):
    """
    从原网站抓取的题目对象
    """

    class Status(Enum):
        STATUS_PENDING = 'Pending'
        STATUS_RUNNING = 'Running'
        STATUS_CRAWLING_SUCCESS = 'Success'
        STATUS_PROBLEM_NOT_EXIST = 'Problem Not Exist'
        STATUS_NO_ACCOUNT = 'No Account'
        STATUS_OJ_NOT_EXIST = 'Platform Not Exist'
        STATUS_PARSE_ERROR = 'Parse Error'
        STATUS_SUBMIT_FAILED = 'Submit Failed'

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
        STATUS_PENDING = 'Pending'
        STATUS_RUNNING = 'Running'
        STATUS_RESULT = 'Success'
        STATUS_SUBMIT_FAILED = 'Submit Failed'
        STATUS_RESULT_NOT_EXIST = 'Not Exist'
        STATUS_NO_ACCOUNT = 'No Account'
        STATUS_OJ_NOT_EXIST = 'Platform Not Exist'
        STATUS_PARSE_ERROR = 'Parse Error'
        STATUS_IN_QUEUE = 'In Queue'

    class VerdictCode(Enum):
        VERDICT_RUNNING = 'Running'
        VERDICT_ACCEPTED = 'Accepted'
        VERDICT_COMPILE_ERROR = 'Compile Error'
        VERDICT_RESULT_ERROR = 'Result Error'
        VERDICT_SUBMIT_FAILED = 'Submit Failed'

    def __init__(self, verdict_code=VerdictCode.VERDICT_RUNNING):
        self.origin_run_id = None
        self.verdict = None
        self.verdict_code = verdict_code
        self.execute_time = None
        self.execute_memory = None
        self.status = None
        self.info = None
