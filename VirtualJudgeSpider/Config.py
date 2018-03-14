import json
from urllib import request

ACCOUNTS_FILE = '/Users/prefixai/static_files/accounts.json'

custom_headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}


class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.status = False

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_status(self):
        return self.status


class Accounts:
    def __init__(self):
        self.accounts = {'HDU': [], 'POJ': [],'WUST': []}
        with open(ACCOUNTS_FILE, 'r') as fin:
            text = fin.read()
            accounts_json = json.loads(text)
            for account_json in accounts_json:
                self.accounts[account_json['name']].append(
                    Account(account_json['username'], account_json['password']))

    def rent_account(self, oj_name):
        for account in self.accounts[oj_name]:
            if not account.status:
                account.status = True
                return account

    def return_account(self, oj_name, uuid):
        for account in self.accounts[oj_name]:
            if account.uid == uuid:
                account.status = False
                break


class Spider:
    @staticmethod
    def get_data(url, codec):
        try:
            with request.urlopen(url) as fin:
                data = fin.read()
                return data.decode(codec)
        except:
            return None


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


class Problem:
    PROBLEM_NOT_FOUND = None

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

    def get_dict(self):
        ret_dict = {'remote_id': self.remote_id,
                    'remote_oj': self.remote_oj,
                    'remote_url': self.remote_url,
                    'title': self.title,
                    'time_limit': self.time_limit,
                    'memory_limit': self.memory_limit,
                    'description': self.description,
                    'special_judge': self.special_judge,
                    'input': self.input,
                    'output': self.output,
                    'sample': self.sample,
                    'hint': self.hint,
                    'author': self.author,
                    'source': self.source}
        return ret_dict

    def show(self):
        print('remote_id', self.remote_id)
        print('remote_oj', self.remote_oj)
        print('remote_url', self.remote_url)
        print('title', self.title)
        print('time_limit', self.time_limit)
        print('memory_limit', self.memory_limit)
        print('description', self.description)
        print('special_judge', self.special_judge)
        print('input', self.input)
        print('output', self.output)
        print('sample', self.sample)
        print('hint', self.hint)
        print('author', self.author)
        print('source', self.source)


class Result:
    def __init__(self):
        self.origin_run_id = None
        self.verdict = None
        self.execute_time = None
        self.execute_memory = None

    def get_dict(self):
        ret_dict = {'origin_run_id': self.origin_run_id,
                    'verdict': self.verdict,
                    'execute_time': self.execute_time,
                    'execute_memory': self.execute_memory}
        pass

    def show(self):
        print(self.origin_run_id)
        print(self.verdict)
        print(self.execute_time)
        print(self.execute_memory)
