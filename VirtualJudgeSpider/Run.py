from OnlineJudgeSpider.Config import Account
from OnlineJudgeSpider.Control import Controller
import csv
import random
import time
if __name__ == '__main__':
    account = Account('', '')
    #Controller.get_problem('WUST', '2095')
    #print(Controller.find_language('WUST',account))
    # Controller.check_status('HDU')
    # Controller.find_language('HDU', account)
    # Controller.is_waiting_for_judge()
    # Controller.get_result_by_rid()
    #Controller.get_result()
    code=''
    with open("/home/liwenshi/OnlineJudgeSpider/OnlineJudgeSpider/OJs/1000","r") as f:
        code=f.read()
    #print(code)
    Controller.submit_code("WUST",account,code=code,language='C++',pid='1000')
    time.sleep(2)
    Controller.get_result("WUST",account,'1000').show()
