import unittest

from spider.config import Result


class TestResult(unittest.TestCase):
    def test_result(self):
        result = Result()
        result.execute_memory = '128 MB'
        result.execute_time = '1000 MS'
        result.unique_key = '1'
        result.verdict = Result.Verdict.VERDICT_RUNNING
        result.verdict_info = 'Accepted'
        print(result.__dict__)
        self.assertDictEqual(result.__dict__, {'execute_memory': '128 MB',
                                               'execute_time': '1000 MS',
                                               'unique_key': '1',
                                               'status': None,
                                               'compile_info': None,
                                               'verdict_info': 'Accepted',
                                               'verdict': Result.Verdict.VERDICT_RUNNING})
