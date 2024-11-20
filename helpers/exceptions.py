from textwrap import dedent


class MinModException(Exception):
    def __init__(self, message):
        super().__init__(dedent(message).strip())


class EmptyDedupDataFrame(MinModException):
    pass


class EmtpyGTDataFrame(MinModException):
    pass
