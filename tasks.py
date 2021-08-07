import json
import math
import random

from celery import Celery
from redis import Redis

from server_config import BROKER_URL, REDIS_USER, REDIS_PASS, REDIS_PORT, REDIS_HOST
from utils.config import Account

from platforms.hdu import HDU
from platforms.codeforces import Codeforces

app = Celery('platforms')
app.conf.update(
    broker_url=BROKER_URL,
    enable_utc=True,
    task_serializer='json',
)

accounts_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USER, password=REDIS_PASS, db=3)


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


@app.task(name='result_problem_task')
def result_problem_task(problem_id, remote_oj, remote_id, time_limit, memory_limit, remote_url, title, spj, content):
    print(problem_id, remote_oj, remote_id, time_limit, memory_limit, remote_url, title, spj, content)


# def result_problem_task(remote_oj: str, remote_id: str, data: dict):
#     print(remote_oj, remote_id, data)


@app.task(name='result_submission')
def result_submission(local_id: int, data: dict):
    print(local_id, data)


def get_oj(account, remote_oj=None):
    oj = None
    if remote_oj == 'HDU':
        oj = HDU(account=account)
    elif remote_oj == 'Codeforces':
        oj = Codeforces(account=account)
    return oj


@app.task(bind=True, name="retrieve_problem_task")
def retrieve_problem_task(self, remote_oj: str, remote_id: str, problem_id: int):
    oj = get_oj(None, remote_oj)
    if oj is None:
        print("Not support")
        return
    problem = oj.get_problem(remote_id)

    # result_problem_task(
    #     problem_id,
    #     remote_oj,
    #     remote_id,
    #     problem.time_limit,
    #     problem.memory_limit,
    #     problem.remote_url,
    #     problem.title,
    #     problem.special_judge,
    #     {
    #         'html': problem.html,
    #         'template': problem.template,
    #     })
    result_problem_task.apply_async(
        args=[problem_id,
              remote_oj,
              remote_id,
              problem.time_limit,
              problem.memory_limit,
              problem.remote_url,
              problem.title,
              problem.special_judge,
              {
                  'html': problem.html,
                  'template': problem.template,
              }],
        queue='results')


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

    result = oj.submit_code(remote_id, language, user_code).to_dict()
    oj.account.update_previous()
    result_submission(local_id, result)
    result_submission.apply_async(
        args=[local_id, result],
        queue='results')
    release_account(idx, remote_oj)


@app.task(bind=True, name='sync_problem_list')
def sync_problem_list(self, remote_oj: str, local_id_list: list[str]):
    oj = get_oj(None, remote_oj)
    remote_id_list = oj.get_problem_list()
    id_set = set(local_id_list)
    candidate_update_id_list = [it for it in remote_id_list if it not in id_set]
    for item in candidate_update_id_list:
        retrieve_problem_task.apply_async(
            args=['HDU', item, None],
            queue='requests'
        )


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
    # accounts_conn.set('PROBLEM_PAUSE', 0)
    # retrieve_problem_task('HDU', '1000', None)
    # retrieve_problem_task('Codeforces', '1A', None)
    # request_submission(1, 'HDU', '1000', '0', code)
    print(sync_problem_list("HDU", []))
    print(sync_problem_list("Codeforces", []))
