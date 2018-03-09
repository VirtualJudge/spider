import json
import uuid
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
    def __init__(self, username, password, uid):
        self.username = username
        self.password = password
        self.uid = uid
        self.status = False

    def get_uid(self):
        return self.uid

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_status(self):
        return self.status


class Accounts:
    def __init__(self):
        self.accounts = {'HDU': [], 'POJ': []}
        with open(ACCOUNTS_FILE, 'r') as fin:
            text = fin.read()
            accounts_json = json.loads(text)
            for account_json in accounts_json:
                self.accounts[account_json['name']].append(
                    Account(account_json['username'], account_json['password'], uuid.uuid1()))

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
        with request.urlopen(url) as fin:
            data = fin.read()
            return data.decode(codec)


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
    def __init__(self):
        self.origin_id = None
        self.origin_url = None

        self.title = None
        self.time_limit = None
        self.memory_limit = None
        self.description = None
        self.input = None
        self.output = None
        self.sample = None
        self.hint = None
        self.author = None
        self.source = None

    def show(self):
        print(self.origin_id)
        print(self.origin_url)
        print(self.title)
        print(self.time_limit)
        print(self.memory_limit)
        print(self.description)
        print(self.input)
        print(self.output)
        print(self.sample)
        print(self.hint)
        print(self.author)
        print(self.source)


class Result:
    def __init__(self):
        self.origin_run_id = None
        self.verdict = None
        self.execute_time = None
        self.execute_memory = None

    def show(self):
        print(self.origin_run_id)
        print(self.verdict)
        print(self.execute_time)
        print(self.execute_memory)
