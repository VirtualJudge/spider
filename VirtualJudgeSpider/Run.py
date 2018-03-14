from VirtualJudgeSpider.Config import Account
from VirtualJudgeSpider.Control import Controller
if __name__ == '__main__':
    account = Account('', '')
    Controller.get_problem('POJ', '1005')
    # Controller.check_status('HDU')
    # Controller.find_language('HDU', account)
    # Controller.is_waiting_for_judge()
    # Controller.get_result_by_rid()
    # Controller.get_result()
    # Controller.submit_code()
    #with open('/home/noire/SpiderTest/1000.cpp','r') as fin:
       # Controller.submit_code('HDU',account,fin.read(),'0',1000)
