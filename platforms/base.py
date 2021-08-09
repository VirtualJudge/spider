from functools import wraps
from utils.config import Account


class SpiderException(Exception):
    pass


class BaseParser(object):
    pass


class Base(object):
    def __init__(self, account, *args, **kwargs):
        self._account = account

    @property
    def account(self):
        return self._account

    def check_network(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_working():
                raise SpiderException("Network Error")
            return func(*args, **kwargs)

        return wrapper

    def check_login(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_login():
                self.login_website()
            return func(*args, **kwargs)

        return wrapper

    def login_website(self):
        pass

    def is_login(self):
        pass

    def is_working(self):
        pass

    def submit_code(self, *args, **kwargs):
        pass

    def list_problem(self, *args, **kwargs):
        pass

    def retrieve_problem(self, *args, **kwargs):
        pass

    def get_problem_list(self):
        pass

    def retrieve_language(self, *args, **kwargs):
        pass
