import logging
import os
import pathlib
import subprocess
import typing


class Result:

    OK: bool
    exception: BaseException

    def __init__(self, success=True, exception=None):
        self.OK = success
        self.exception = exception


class Action:

    result: Result
    rollback_result: Result

    def __init__(self):
        self.result = None
        self.rollback_result = None

    def _pre_invoke(self, context: dict) -> None:
        pass

    def invoke(self, context: dict) -> None:
        pass

    def _pre_rollback(self, context: dict) -> None:
        pass

    def rollback(self, context: dict) -> None:
        pass


def pkexec(orig_class):

    _build_command_orig = orig_class._build_command
    _build_rollback_command_orig = orig_class._build_rollback_command

    def _build_command_pkexec():
        return _build_command_orig().insert(0, 'pkexec')

    def _build_rollback_command_pkexec():
        return _build_rollback_command_orig().insert(0, 'pkexec')

    orig_class._build_command = _build_command_pkexec
    orig_class._build_rollback_command = _build_rollback_command_pkexec


class ShellAction(Action):

    def __init__(self):
        super().__init__()

    def invoke(self, context: dict) -> None:
        self._pre_invoke()
        cp = subprocess.run(self._build_command(), shell=True)
        try:
            cp.check_returncode()
            self.result = Result()
        except subprocess.CalledProcessError as e:
            self.result = Result(False, e)

    def _build_invoke_command(self) -> typing.List[str]:
        return []

    def _build_rollback_command(self) -> typing.List[str]:
        return []


class LogAction(Action):

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def invoke(self, context: dict) -> None:
        logging.info(self._message)
        self.result = Result()


class Chmod(Action):

    _target: pathlib.Path
    _mode: int
    _orig_mode: int

    def __init__(self, target: pathlib.Path, mode: int):
        super().__init__()
        self._target = target
        self._mode = mode
        self._orig_mode = 0

    def invoke(self, context: dict) -> None:
        try:
            self._orig_mode = os.stat(self._target).st_mode
            self._target.chmod(self._mode)
            self.result = Result()
        except (FileNotFoundError, PermissionError) as e:
            self.result = Result(False, e)

    def rollback(self, context: dict) -> None:
        try:
            self._target.chmod(self._orig_mode)
            self.rollback_result = Result()
        except (FileNotFoundError, PermissionError) as e:
            self.rollback_result = Result(False, e)
