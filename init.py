import json

from redis import Redis
import yaml
from server_config import REDIS_USER, REDIS_PASS, REDIS_PORT, REDIS_HOST, ACCOUNTS_CONFIG

accounts_conn = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USER,
    password=REDIS_PASS,
    db=1)


def check(accounts):
    for key in accounts.keys():
        if not isinstance(accounts[key], list):
            return False
        for it in accounts[key]:
            if not isinstance(it, dict):
                return False
            if not it.get('username') or not it.get('password'):
                return False
    return True


def init():
    accounts_conn.flushdb()
    res = yaml.safe_load(open(ACCOUNTS_CONFIG, 'r', encoding='utf-8'))
    if check(res):
        accounts_conn.flushdb()
        for key in res.keys():
            for idx in range(len(res[key])):
                accounts_conn.rpush(key, json.dumps(res[key][idx]))
                accounts_conn.rpush(f'{key}_IDLE', idx)


if __name__ == '__main__':
    init()
