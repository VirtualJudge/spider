import json
import math
import random

from celery import Celery
from redis import Redis

from server_config import BROKER_URL, REDIS_USER, REDIS_PASS, REDIS_PORT, REDIS_HOST
from spider.config import Account
from spider.platforms import HDU, POJ

app = Celery('spider')
app.conf.update(
    broker_url=BROKER_URL,
    enable_utc=True,
    task_serializer='json',
)

accounts_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USER, password=REDIS_PASS, db=1)


def lock_account(platform):
    """ 锁定一个帐号
        `platform`_IDLE 存放的是可用的帐号的序号
        `platform`_RUNNING 存放的是正在使用的帐号的序号
        将这个帐号从IDLE列表中移除，然后放入到RUNNING列表中
    """
    idx = accounts_conn.brpoplpush(f'{platform}_IDLE', f'{platform}_RUNNING', timeout=5)
    return idx


def release_account(idx, platform, account=None):
    """释放这个帐号
        `platform`_IDLE 存放的是可用的帐号的序号
        `platform`_RUNNING 存放的是正在使用的帐号的序号
        将这个帐号从RUNNING列表中移除，然后放入到IDLE列表中
    """
    if account:
        accounts_conn.lset(f'{platform}', idx, account)
    accounts_conn.lrem(f'{platform}_RUNNING', 1, idx)
    accounts_conn.lpush(f'{platform}_IDLE', idx)


@app.task(name='result_problem')
def result_problem(remote_oj: str, remote_id: str, data: dict):
    print(remote_oj, remote_id, data)


@app.task(name='result_submission')
def result_submission(local_id: int, data: dict):
    print(local_id, data)


def get_oj(account: Account, remote_oj=None):
    oj = None
    if remote_oj == 'HDU':
        oj = HDU(account=account)
    elif remote_oj == 'POJ':
        oj = POJ(account=account)
    return oj


@app.task(bind=True, name="request_problem")
def request_problem(self, remote_oj: str, remote_id: str):
    """ 从请求任务队列中获取到题目请求任务，进行题目的抓取
    Args: 待定
    Returns: None
    Raises: None
    """

    idx = lock_account(remote_oj)
    if idx is None:
        raise self.retry(exc=Exception('Bind Account Error'), countdown=int(math.fabs(random.gauss(0, 5))))

    accounts_js = json.loads(accounts_conn.lindex(remote_oj, idx))
    account = Account(username=accounts_js.get('username', ''), password=accounts_js.get('password', ''),
                      cookies=accounts_js.get('cookies', ''), previous=accounts_js.get('previous', 0))
    oj = get_oj(account, remote_oj)
    if oj is None:
        print("Not support")
        return
    problem = oj.get_problem(remote_id).__dict__
    oj.account.update_previous()

    result_problem(remote_oj, remote_id, problem)
    result_problem.apply_async(
        args=[remote_oj, remote_id, problem],
        queue='results')
    release_account(idx, remote_oj, oj.account.to_str())


@app.task(bind=True, name="request_submission")
def request_submission(self, local_id: int, remote_oj: str, remote_id: str, language: str, user_code: str):
    idx = lock_account(remote_oj)
    if idx is None:
        raise self.retry(exc=Exception('Bind Account Error'), countdown=int(math.fabs(random.gauss(0, 5))))
    accounts_js = json.loads(accounts_conn.lindex(remote_oj, idx))
    account = Account(username=accounts_js.get('username', ''), password=accounts_js.get('password', ''),
                      cookies=accounts_js.get('cookies', ''), previous=accounts_js.get('previous', 0))
    oj = get_oj(account, remote_oj)
    if oj is None:
        print("Not support")
        return

    result = oj.submit_code(remote_id, language, user_code).__dict__
    oj.account.update_previous()
    result_submission(local_id, result)
    release_account(idx, remote_oj)


if __name__ == '__main__':
    code = """
#include <iostream>
using namespace std;

int main(){
    int a, b;
    while(cin >> a >> b) cout << a+b << endl;
    return 0;
}
"""
    request_problem('POJ', '1000')
    request_submission(1, 'POJ', '1000', '0', code)
