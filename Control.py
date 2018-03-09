from OJs.HDUClass import HDU


class OJBuilder:
    @staticmethod
    def build_oj(name):
        if name == 'HDU':
            return OJBuilder.build_hdu()

    @staticmethod
    def build_hdu():
        return HDU()


class Controller:
    @staticmethod
    def get_problem(oj_name, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_problem(**kwargs)

    @staticmethod
    def submit_code(oj_name, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.submit_code(**kwargs)

    @staticmethod
    def get_result(oj_name, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_result(**kwargs)

    @staticmethod
    def get_result_by_rid(oj_name, rid):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.get_result_by_rid(rid)

    @staticmethod
    def find_language(oj_name, **kwargs):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.find_language(**kwargs)

    @staticmethod
    def is_waiting_for_judge(oj_name, verdict):
        OJ = OJBuilder.build_oj(oj_name)
        return OJ.is_waiting_for_judge(verdict)
