import abc
import argparse
import pathlib
import typing

import zvault.action as act


class Command(metaclass=abc.ABCMeta):
    _COMMAND_OPT_VAULT_PATH = 'vault_path'
    _COMMAND_OPT_GPG_KEY = 'gpg_key'
    _COMMAND_OPT_FORCE = 'force'

    _actions: typing.List[act.Action]
    _args: typing.Dict
    _name: str

    _force_parser = argparse.ArgumentParser(add_help=False)
    _force_parser.add_argument('-f', '--force', action='store_true',
                                    dest=_COMMAND_OPT_FORCE,
                                    help='force the operation')

    _path_parser = argparse.ArgumentParser(add_help=False)
    _path_parser.add_argument(_COMMAND_OPT_VAULT_PATH,
                              help='specifies the vault path relative to '
                                   'the user\'s home directory')

    _gpg_parser = argparse.ArgumentParser(add_help=False)
    _gpg_parser.add_argument('--gpg-key', '-g',
                             action='store',
                             dest=_COMMAND_OPT_GPG_KEY,
                             metavar='key_id',
                             help='specifies the gpg key used to protect '
                                  'the ZFS key or passphrase')

    @classmethod
    @abc.abstractmethod
    def build_command_sub_parser(cls, sub_parser: argparse.ArgumentParser) \
            -> None:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def command_name(cls) -> str:
        raise NotImplementedError()

    def __init__(self, args: typing.Dict):
        self._actions = []
        self._args = args

    def _add_action(self, action: act.Action):
        self._actions.append(action)

    def execute(self):
        for action in self._actions:
            action.invoke()
            if not action.result.OK:
                break
        if action.result.OK:
            return
        else:
            [a.rollback() for a in reversed(self._actions)
             if a.result is not None and a.result.OK]

    @property
    def vault_path(self) -> pathlib.Path:
        return pathlib.Path(self._args[self._COMMAND_OPT_VAULT_PATH])

    @property
    def gpg_key(self) -> str:
        return self._args[self._COMMAND_OPT_GPG_KEY]

    @property
    def force_action(self) -> bool:
        return self._args[self._COMMAND_OPT_FORCE]

    @property
    def key_file(self) -> pathlib.Path:
        raise NotImplementedError()


class CreateCommand(Command):
    _COMMAND_CREATE = 'create'
    _COMMAND_OPT_PARENT = 'parent'

    @classmethod
    def command_name(cls) -> str:
        return cls._COMMAND_CREATE

    @classmethod
    def build_command_sub_parser(cls,
                                 sub_parser: argparse.ArgumentParser) -> None:
        create_parser = sub_parser.add_parser(cls._COMMAND_CREATE,
                                              parents=[cls._path_parser,
                                                       cls._gpg_parser])
        create_parser.add_argument('--parent', '-p',
                                   action='store',
                                   dest=cls._COMMAND_OPT_PARENT,
                                   metavar='parent_dataset',
                                   help='specifies the parent dataset in which '
                                        'the vault will be created')

    def __init__(self, args: typing.Dict):
        super().__init__(args)
        self._add_action(act.CreateMountPoint(self.vault_path))
        self._add_action(act.CreateEncryptedKeyFile(self.key_file))

    @property
    def parent(self):
        return self._args[self._COMMAND_OPT_PARENT]


class DestroyCommand(Command):
    _COMMAND_DESTROY = 'destroy'

    @classmethod
    def command_name(cls) -> str:
        return cls._COMMAND_DESTROY

    @classmethod
    def build_command_sub_parser(cls,
                                 sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_parser(cls._COMMAND_DESTROY, parents=[cls._path_parser,
                                                             cls._force_parser])

    def __init__(self, args: typing.Dict):
        super().__init__(args)
        self._add_action(act.LogAction('destroy'))


class UnlockCommand(Command):
    _COMMAND_LOCK = 'lock'

    @classmethod
    def command_name(cls) -> str:
        return cls._COMMAND_UNLOCK

    @classmethod
    def build_command_sub_parser(cls,
                                 sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_parser(cls._COMMAND_UNLOCK, parents=[cls._path_parser,
                                                            cls._gpg_parser])

    def __init__(self, args: typing.Dict):
        super().__init__(args)
        self._add_action(act.LogAction('unlock'))


class LockCommand(Command):
    _COMMAND_UNLOCK = 'unlock'

    @classmethod
    def command_name(cls) -> str:
        return cls._COMMAND_LOCK

    @classmethod
    def build_command_sub_parser(cls,
                                 sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_parser(cls._COMMAND_LOCK, parents=[cls._path_parser])

    def __init__(self, args: typing.Dict):
        super().__init__(args)
        self._add_action(act.LogAction('lock'))


COMMANDS = [
    CreateCommand,
    DestroyCommand,
    LockCommand,
    UnlockCommand
]
