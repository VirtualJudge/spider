PENDING = 'P'
RUNNING = 'R'
ACCEPTED = 'AC'
PARTIAL_ACCEPTED = 'PA'
PRESENTATION_ERROR = 'PE'
TIME_LIMIT_EXCEEDED = 'TLE'
MEMORY_LIMIT_EXCEEDED = 'MLE'
WRONG_ANSWER = 'WA'
RUNTIME_ERROR = 'RE'
OUTPUT_LIMIT_EXCEEDED = 'OLE'
COMPILE_ERROR = 'CE'
SYSTEM_ERROR = 'SE'


class Account:
    def __init__(self):
        self._username = None
        self._password = None

        self._key = None

        self._cookies = None

    def to_json(self):
        return {
            'username': str(self._username),
            'password': str(self._password),
            'key': str(self._key),
            'cookies': str(self._cookies),
        }

    def from_json(self, data: dict):
        self._username = data['username']
        self._password = data['password']
        self._key = data['key']
        self._cookies = data['cookies']
