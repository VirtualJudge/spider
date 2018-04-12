import unittest

from VirtualJudgeSpider.Config import Result


class TestResult(unittest.TestCase):
    def test_result(self):
        result = Result()
        result.execute_memory = '128 MB'
        result.execute_time = '1000 MS'
        result.origin_run_id = '1'
        result.verdict = 'Accepted'
        self.assertDictEqual(result.__dict__, {'execute_memory': '128 MB',
                                               'execute_time': '1000 MS',
                                               'origin_run_id': '1',
                                               'status': None,
                                               'verdict': 'Accepted'})
