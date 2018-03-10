from OnlineJudgeSpider.Config import Account
from OnlineJudgeSpider.Control import Controller
if __name__ == '__main__':
<<<<<<< HEAD:Run.py
    account = Account('genesis244', 'herui130130')
    # Controller.get_problem('HDU', '2011').show()
    #Controller.check_status('POJ')
    #print(Controller.find_language('POJ', account))
=======
    account = Account('', '')
    Controller.get_problem('HDU', '2011').show()
    # Controller.check_status('HDU')
    # Controller.find_language('HDU', account)
>>>>>>> e21a3ca054babf22745d5a8d609f57ef32b36e65:OnlineJudgeSpider/Run.py
    # Controller.is_waiting_for_judge()
    # Controller.get_result_by_rid()
    # Controller.get_result()
    # Controller.submit_code()
    #with open('/home/noire/SpiderTest/1000.cpp','r') as fin:
       # Controller.submit_code('HDU',account,fin.read(),'0',1000)