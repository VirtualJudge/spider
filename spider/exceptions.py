class SpiderException(Exception):
    pass


class SpiderNetworkError(SpiderException):
    pass


class SpiderProblemParseError(SpiderException):
    pass


class SpiderAccountLoginError(SpiderException):
    pass
