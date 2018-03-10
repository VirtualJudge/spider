from OJs.HDUClass import HDU
from OJs.POJClass import POJ

class OJBuilder:
    @staticmethod
    def build_oj(name):
        if name == 'HDU':
            return OJBuilder.build_hdu()
        if name == 'POJ':
            return OJBuilder.build_poj()

    @staticmethod
    def build_hdu():
        return HDU()
    @staticmethod
    def build_poj():
        return POJ()


class Controller:
    # 获取题面
    @staticmethod
    def get_problem(oj_name, pid, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_problem(pid=pid, **kwargs)

    # 提交代码
    @staticmethod
    def submit_code(oj_name, account, code, language, pid, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.submit_code(account=account, code=code, language=language, pid=pid, **kwargs)

    # 获取结果
    @staticmethod
    def get_result(oj_name, account, pid, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_result(account=account, pid=pid, **kwargs)

    # 通过运行id获取结果
    @staticmethod
    def get_result_by_rid(oj_name, rid):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_result_by_rid(rid)

    # 获取源OJ语言
    @staticmethod
    def find_language(oj_name, account, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.find_language(account=account, **kwargs)

    # 判断是否是等待判题的返回结果，例如pending,Queuing,Compiling
    @staticmethod
    def is_waiting_for_judge(oj_name, verdict):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.is_waiting_for_judge(verdict)

    # 判断源OJ的网络连接是否良好
    @staticmethod
    def check_status(oj_name):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.check_status()
