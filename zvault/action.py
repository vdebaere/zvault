import logging


class Result:

    OK: bool

    def __init__(self, success=True):
        self.OK = success


class Action:

    result: Result
    rollback_result: Result

    def __init__(self):
        self.result = None
        self.rollback_result = None

    def invoke(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class LogAction(Action):

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def invoke(self) -> None:
        logging.info(self._message)
        self.result = Result()
