import time

from VirtualJudgeSpider.config import Problem, Result, Account

supports = [
    'Aizu',
    'HDU',
    'FZU',
    'POJ',
    'WUST',
    'ZOJ',
    # 'Codeforces'
]


class OJBuilder(object):
    @staticmethod
    def build_oj(name, *args, **kwargs):
        if name:
            try:
                module_meta = __import__(f'VirtualJudgeSpider.OJs.{str(name).lower()}', globals(), locals(), [name])
                class_meta = getattr(module_meta, name)
                oj = class_meta(*args, **kwargs)
                return oj
            except ModuleNotFoundError:
                pass
        return None


class Controller(object):
    def __init__(self, oj_name):
        remote_oj = Controller.get_real_remote_oj(oj_name)
        self._oj = OJBuilder.build_oj(remote_oj)
        self._origin_name = oj_name

    def _space_and_enter_strip(self, data):
        if data:
            return str(data).strip(' ').strip('\r\n').strip(' ')

    @staticmethod
    def get_real_remote_oj(name):
        """

        :param name: oj名称，可能与数据库里面保存的名称不一致，需要通过这个函数找到数据库名称
        :return: 数据库名称，或者不存在
        """
        for oj_name in supports:
            if str(name).upper() == str(oj_name).upper():
                return oj_name
        return None

    # 获取支持的OJ列表
    @staticmethod
    def get_supports():
        return supports

    # 判断当前是否支持
    @staticmethod
    def is_support(oj_name):
        if Controller.get_real_remote_oj(oj_name):
            return True
        return False

    def get_home_page_url(self):
        if not self._oj:
            return None
        return self._oj.home_page_url()

    def get_cookies(self):
        if not self._oj:
            return None
        return self._oj.get_cookies()

    # 获取题面
    def get_problem(self, pid, account, **kwargs):
        if not self._oj:
            problem = Problem()
            problem.remote_oj = self._origin_name
            problem.remote_id = pid
            problem.status = Problem.Status.STATUS_OJ_NOT_EXIST
            return problem
        self._oj.set_cookies(account.cookies)
        problem = self._oj.get_problem(pid=pid, account=account, **kwargs)
        problem.title = self._space_and_enter_strip(problem.title)
        problem.time_limit = self._space_and_enter_strip(problem.time_limit)
        problem.memory_limit = self._space_and_enter_strip(problem.memory_limit)
        return problem

    # 提交代码
    def submit_code(self, pid, account, code, language, **kwargs):
        if not self._oj:
            return None
        self._oj.set_cookies(account.cookies)
        if self._oj.submit_code(account=account, code=code, language=language, pid=pid, **kwargs):
            time.sleep(2)
            return self.get_result(account=account, pid=pid, **kwargs)
        else:
            return Result(Result.VerdictCode.STATUS_SUBMIT_FAILED)

    # 获取结果
    def get_result(self, account, pid, **kwargs):

        if not self._oj:
            return Result(Result.VerdictCode.STATUS_SUBMIT_FAILED)
        self._oj.set_cookies(account.cookies)
        result = self._oj.get_result(account=account, pid=pid, **kwargs)
        if result is not None:
            if self._oj.is_accepted(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_ACCEPTED
            elif self._oj.is_running(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_RUNNING
            elif self._oj.is_compile_error(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_COMPILE_ERROR
            else:
                result.verdict_code = Result.VerdictCode.STATUS_RESULT_ERROR
            result.execute_time = self._space_and_enter_strip(result.execute_time)
            result.execute_memory = self._space_and_enter_strip(result.execute_memory)

            return result
        return Result(Result.VerdictCode.STATUS_SUBMIT_FAILED)

    # 通过运行id获取结果
    def get_result_by_rid_and_pid(self, rid, pid):
        if not self._oj:
            return Result(Result.VerdictCode.STATUS_SUBMIT_FAILED)

        result = self._oj.get_result_by_rid_and_pid(rid, pid)
        if result is not None:
            if self._oj.is_accepted(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_ACCEPTED
            elif self._oj.is_running(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_RUNNING
            elif self._oj.is_compile_error(result.verdict):
                result.verdict_code = Result.VerdictCode.STATUS_COMPILE_ERROR
            else:
                result.verdict_code = Result.VerdictCode.STATUS_RESULT_ERROR
            result.execute_time = self._space_and_enter_strip(result.execute_time)
            result.execute_memory = self._space_and_enter_strip(result.execute_memory)
            return result
        return Result(Result.VerdictCode.STATUS_SUBMIT_FAILED)

    # 获取源OJ语言
    def find_language(self, account, **kwargs):
        if not self._oj:
            return None
        self._oj.set_cookies(account.cookies)
        return self._oj.find_language(account=account, **kwargs)

    # 判断是否是等待判题的返回结果，例如pending,Queuing,Compiling
    def is_waiting_for_judge(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_waiting_for_judge(verdict)

    # 判断源OJ的网络连接是否良好
    def check_status(self):
        if not self._oj:
            return None
        return self._oj.check_status()

    # 判断结果是否AC
    def is_accepted(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_accepted(verdict)

    # 判断是否运行中或者排队中
    def is_running(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_running(verdict)

    # 判断是否编译错误
    def is_compile_error(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_compile_error(verdict)

    # 判断爬虫账号是否可以正常登陆
    def is_account_valid(self, account):
        if self._oj and account and self._oj.login_website(account=account):
            return True
        return False


post_code = """// 2052
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <iostream>
#include <set>
using namespace std;
int main(){
    int n;
    cin >> n;
    int a,b;
    int ans = 0;
    while(n--){
        cin >> a >> b;
        while(ans>=a) a+=b;
        ans = a;
    }
    cout << ans << endl;
    return 0;
}
"""

if __name__ == '__main__':
    account = Account('robot4test', 'robot4test')

    # start = datetime.datetime.now()
    result = Controller('codeforces').submit_code(pid='879A', account=account, code=post_code, language='50')
    # print((datetime.datetime.now() - start).seconds)
    print(result)
