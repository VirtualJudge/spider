from VirtualJudgeSpider.OJs.FZUClass import FZU
from VirtualJudgeSpider.OJs.HDUClass import HDU
from VirtualJudgeSpider.OJs.POJClass import POJ
from VirtualJudgeSpider.OJs.WUSTClass import WUST

supports = ['HDU', 'POJ', 'WUST', 'FZU']


class OJBuilder:
    @staticmethod
    def build_oj(name):
        if name == 'HDU':
            return OJBuilder.build_hdu()
        if name == 'POJ':
            return OJBuilder.build_poj()
        if name == 'WUST':
            return OJBuilder.build_wust()
        if name == 'FZU':
            return OJBuilder.build_fzu()

    @staticmethod
    def build_hdu():
        return HDU()

    @staticmethod
    def build_poj():
        return POJ()

    @staticmethod
    def build_wust():
        return WUST()

    @staticmethod
    def build_fzu():
        return FZU()


class Controller:
    # 获取支持的OJ列表
    @staticmethod
    def get_supports():
        return supports

    # 判断当前是否支持
    @staticmethod
    def is_support(oj_name):
        if oj_name in supports:
            return True
        return False

    # 获取题面
    @staticmethod
    def get_problem(oj_name, pid, **kwargs):
        oj = OJBuilder.build_oj(oj_name)
        return oj.get_problem(pid=pid, **kwargs)

    # 提交代码
    @staticmethod
    def submit_code(oj_name, account, code, language, pid, **kwargs):
        oj = OJBuilder.build_oj(oj_name)
        return oj.submit_code(account=account, code=code, language=language, pid=pid, **kwargs)

    # 获取结果
    @staticmethod
    def get_result(oj_name, account, pid, **kwargs):
        oj = OJBuilder.build_oj(oj_name)
        return oj.get_result(account=account, pid=pid, **kwargs)

    # 通过运行id获取结果
    @staticmethod
    def get_result_by_rid(oj_name, rid):
        oj = OJBuilder.build_oj(oj_name)
        return oj.get_result_by_rid(rid)

    # 获取源OJ语言
    @staticmethod
    def find_language(oj_name, account, **kwargs):
        oj = OJBuilder.build_oj(oj_name)
        return oj.find_language(account=account, **kwargs)

    # 判断是否是等待判题的返回结果，例如pending,Queuing,Compiling
    @staticmethod
    def is_waiting_for_judge(oj_name, verdict):
        oj = OJBuilder.build_oj(oj_name)
        return oj.is_waiting_for_judge(verdict)

    # 判断源OJ的网络连接是否良好
    @staticmethod
    def check_status(oj_name):
        oj = OJBuilder.build_oj(oj_name)
        return oj.check_status()
