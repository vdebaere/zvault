import abc
import gnupg
import grp
import logging
import os
import pathlib
import pwd
import secrets
import shlex
import subprocess
import typing


class Result:
    OK: bool
    exception: BaseException

    def __init__(self, exception=None):
        self.OK = exception is None
        self.exception = exception


class Action(metaclass=abc.ABCMeta):
    result: Result
    rollback_result: Result

    def __init__(self):
        self.result = None
        self.rollback_result = None

    def _pre_invoke(self, context: dict) -> None:
        pass

    @abc.abstractmethod
    def _invoke(self, context: dict) -> None:
        pass

    def invoke(self, context: dict) -> None:
        self._pre_invoke(context)
        try:
            self._invoke(context)
            self.result = Result()
        except BaseException as e:
            self.result = Result(e)

    def _pre_rollback(self, context: dict) -> None:
        pass

    @abc.abstractmethod
    def _rollback(self, context: dict) -> None:
        pass

    def rollback(self, context: dict) -> None:
        self._pre_rollback(context)
        try:
            self._rollback(context)
            self.rollback_result = Result()
        except BaseException as e:
            self.result = Result(e)


def sudo(orig_class):
    _build_command_orig = orig_class._build_command
    _build_rollback_command_orig = orig_class._build_rollback_command

    def _build_command_sudo():
        return _build_command_orig().insert(0, 'sudo')

    def _build_rollback_command_sudo():
        return _build_rollback_command_orig().insert(0, 'sudo')

    orig_class._build_command = _build_command_sudo
    orig_class._build_rollback_command = _build_rollback_command_sudo


class ShellAction(Action):

    def __init__(self):
        super().__init__()

    def _invoke(self, context: dict) -> None:
        cp = subprocess.run(self._build_invoke_command(), shell=True)
        cp.check_returncode()

    def _rollback(self, context: dict) -> None:
        cp = subprocess.run(self._build_rollback_command(), shell=True)
        cp.check_returncode()

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

    def _invoke(self, context: dict) -> None:
        self._orig_mode = self._target.stat().st_mode
        self._target.chmod(self._mode)

    def _rollback(self, context: dict) -> None:
        self._target.chmod(self._orig_mode)
        self.rollback_result = Result()


@sudo
class Chown(ShellAction):
    _target: pathlib.Path
    _orig_owner_group: (str, str)
    _owner_group: (str, str)

    def __init__(self, target: pathlib.Path, owner: str, group: str):
        super().__init__()
        self._target = target
        self._owner_group = (shlex.quote(owner), shlex.quote(group))
        self._orig_owner_group = ('', '')

    def _pre_invoke(self) -> None:
        stat_result = os.stat(self._target)
        self._orig_owner_group = (pwd.getpwuid(stat_result.st_uid)[0],
                                  grp.getgrgid(stat_result.st_gid)[0])

    def _build_invoke_command(self) -> typing.List[str]:
        return self._build_chown_command()

    def _build_rollback_command(self) -> typing.List[str]:
        return self._build_chown_command(True)

    def _build_chown_command(self, rollback=False):
        owner_group = self._orig_owner_group if rollback else self._owner_group
        return ['chown', '{}:{}'.format(*owner_group), self._target.absolute()]


class CreateMountPoint(Action):

    _target: pathlib.Path

    def __init__(self, target: pathlib.Path):
        super().__init__()
        self._target = target

    def _invoke(self, context: dict) -> None:
        self._target.mkdir(mode=0o200)
        self.result = Result()

    def _rollback(self, context: dict) -> None:
        self._target.rmdir()


class CreateEncryptedKeyFile(Action):

    _key_file: pathlib.Path
    _gpg_key_id: str

    def __init__(self, key_file: pathlib.Path, gpg_key_id: str):
        super().__init__()
        self._key_file = key_file
        self._gpg_key_id = gpg_key_id

    def _invoke(self, context: dict) -> None:
        key = secrets.token_hex(32)
        crypt_result = gnupg.GPG().encrypt(key, self._gpg_key_id)
        if not crypt_result.ok:
            raise ChildProcessError(crypt_result.status)
        with open(self._key_file, mode='w') as sink:
            sink.write(str(crypt_result))

    def _rollback(self, context: dict) -> None:
        os.remove(self._key_file)

