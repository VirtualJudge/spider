class Base:
    # 登录页面
    def login_webside(self, *args, **kwargs):
        pass

    # 检查登录状态
    def check_login_status(self, *args, **kwargs):
        pass

    # 获取题目
    def get_problem(self, *args, **kwargs):
        pass

    # 提交代码
    def submit_code(self, *args, **kwargs):
        pass

    # 获取当然运行结果
    def get_result(self, *args, **kwargs):
        pass

    # 根据源OJ的运行id获取结构
    def get_result_by_rid(self, rid):
        pass

    # 根据源OJ的url获取结果
    def get_result_by_url(self, url):
        pass

    # 获取源OJ支持的语言类型
    def find_language(self, *args, **kwargs):
        pass

    # 获取当前类名
    def get_class_name(self):
        pass

    # 判断当前提交结果的运行状态
    def is_waiting_for_judge(self, verdict):
        pass

    # 检查源OJ是否运行正常
    def check_status(self):
        pass
