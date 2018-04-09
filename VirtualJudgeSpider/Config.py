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

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password


'''
:param title
:param origin_id
:param time_limit
:param memory_limit
:param description
:param input
:param output
:param sample
:param hint
:param author
:param source
:param origin_url
'''


class Desc(object):
    def __init__(self, **kwargs):
        if kwargs.get('type'):
            self.type = kwargs['type']
        else:
            self.type = Desc.Type.TEXT

        if kwargs.get('content'):
            self.content = kwargs['content']
        else:
            self.content = None

        if kwargs.get('file_name'):
            self.file_name = kwargs['file_name']
        else:
            self.file_name = None

        if kwargs.get('origin'):
            self.origin = kwargs['origin']
        else:
            self.origin = None

    class Type(Enum):
        TEXT = 0
        ANCHOR = 1
        PDF = 2
        IMG = 3


class DescList(object):
    def __init__(self):
        self._values = []

    @property
    def values(self):
        return self._values

    def get(self):
        return self._values

    def append(self, desc):
        if type(desc) == Desc:
            self._values.append(desc.__dict__)

    def update(self, desc, index):
        self._values[index] = desc


class Problem:
    def __init__(self):
        self.remote_id = None
        self.remote_url = None
        self.remote_oj = None
        self.title = None
        self.time_limit = None
        self.memory_limit = None
        self.description = None
        self.special_judge = None
        self.input = None
        self.output = None
        self.sample = None
        self.hint = None
        self.author = None
        self.source = None

        # 有html之后可以将description,input,output,sample,hint,author,source设为None
        # 这个属性是上面属性的html代码，直接在网页中用iframe展示
        self.html = None

    def get_dict(self):
        return self.__dict__

    def show(self):
        print(json.dumps(self.__dict__, indent=4))


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
