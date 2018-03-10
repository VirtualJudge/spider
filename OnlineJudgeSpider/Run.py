from OnlineJudgeSpider.Config import Account
from OnlineJudgeSpider.Control import Controller
if __name__ == '__main__':
    account = Account('', '')
    Controller.get_problem('HDU', '2011').show()
    # Controller.check_status('HDU')
    # Controller.find_language('HDU', account)
    # Controller.is_waiting_for_judge()
    # Controller.get_result_by_rid()
    # Controller.get_result()
    # Controller.submit_code()
    #with open('/home/noire/SpiderTest/1000.cpp','r') as fin:
       # Controller.submit_code('HDU',account,fin.read(),'0',1000)
