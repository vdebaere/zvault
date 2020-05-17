import pathlib
import typing

import zvault.action
import zvault.main


class Command:

    _actions: typing.List[zvault.action.Action]
    _args: typing.Dict

    def __init__(self, args):
        self._actions = []
        self._args = args

    def _add_action(self, action: zvault.action.Action):
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


class CreateCommand(Command):

    def __init__(self):
        super().__init__()
        mpath = pathlib.Path(super()._args[zvault.main.COMMAND_OPT_VAULT_PATH])
        self._add_action(zvault.action.CreateMountPoint(mpath))


class DestroyCommand(Command):

    def __init__(self):
        super().__init__()
        self._add_action(zvault.action.LogAction('destroy'))


class UnlockCommand(Command):

    def __init__(self):
        super().__init__()
        self._add_action(zvault.action.LogAction('unlock'))


class LockCommand(Command):

    def __init__(self):
        super().__init__()
        self._add_action(zvault.action.LogAction('lock'))
