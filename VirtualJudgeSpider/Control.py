from VirtualJudgeSpider.OJs.HDUClass import HDU
from VirtualJudgeSpider.OJs.POJClass import POJ
from VirtualJudgeSpider.OJs.WUSTClass import WUST
from VirtualJudgeSpider.OJs.AizuClass import Aizu

supports = ['HDU', 'WUST', 'POJ', 'Aizu']


class Config:
    custom_headers = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }


class OJBuilder:
    @staticmethod
    def build_oj(name):
        if name == 'HDU':
            return OJBuilder.build_hdu()
        if name == 'POJ':
            return OJBuilder.build_poj()
        if name == 'WUST':
            return OJBuilder.build_wust()
        if name == 'Aizu':
            return OJBuilder.build_aizu()

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
    def build_aizu():
        return Aizu()


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
