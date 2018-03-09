from Control import Controller
from OJs import *
from Config import Accounts

accounts = Accounts()

if __name__ == '__main__':
    account = accounts.rent_account('HDU')

    Controller.get_problem('HDU', pid='1026')
    with open('/Users/prefixai/static_files/1000.cpp', 'r') as f:
        data = f.read().encode('utf-8')
        Controller.submit_code('HDU', account=account, code=data, language='0', pid='1000')
    print(Controller.find_language('HDU', account=account))

    result = Controller.get_result('HDU', account=account, pid='1000')
    while Controller.is_waiting_for_judge('HDU', result.verdict):
        result = Controller.get_result_by_rid('HDU', result.origin_run_id)
    result.show()
    accounts.return_account('HDU', account.get_uid())
