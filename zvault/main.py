import argparse

import zvault.command


_COMMAND_CREATE = 'create'
_COMMAND_DESTROY = 'destroy'
_COMMAND_LOCK = 'lock'
_COMMAND_UNLOCK = 'unlock'

_COMMAND_CLASSES = {
    _COMMAND_CREATE: zvault.command.CreateCommand,
    _COMMAND_DESTROY: zvault.command.DestroyCommand,
    _COMMAND_LOCK: zvault.command.LockCommand,
    _COMMAND_UNLOCK: zvault.command.UnlockCommand
}
_COMMAND_NS_KEY = 'command'


def _build_command(args: dict) -> zvault.command.Command:
    return _COMMAND_CLASSES[args[_COMMAND_NS_KEY]]()


def _build_cli() -> argparse.ArgumentParser:
    _cli = argparse.ArgumentParser()
    sub_parser = _cli.add_subparsers(dest=_COMMAND_NS_KEY, required=True)

    path_parser = argparse.ArgumentParser(add_help=False)
    path_parser.add_argument('vault_path',
                             help='specifies the vault path relative to '
                                  'the user\'s home directory')

    gpg_parser = argparse.ArgumentParser(add_help=False)
    gpg_parser.add_argument('--gpg-key', '-g',
                            action='store',
                            dest='gpg_key',
                            metavar='key_id',
                            help='specifies the gpg key used to protect '
                                 'the ZFS key or passphrase')

    create_parser = sub_parser.add_parser(_COMMAND_CREATE,
                                          parents=[path_parser, gpg_parser])
    create_parser.add_argument('--parent', '-p',
                               action='store',
                               dest='parent',
                               metavar='parent_dataset',
                               help='specifies the parent dataset in which '
                                    'the vault will be created')

    destroy_parser = sub_parser.add_parser(_COMMAND_DESTROY,
                                           parents=[path_parser])
    destroy_parser.add_argument('-f', '--force',
                                action='store_true',
                                dest='force',
                                help='force the removal of the vault, even '
                                     'when files are in use')

    sub_parser.add_parser(_COMMAND_UNLOCK, parents=[path_parser, gpg_parser])

    sub_parser.add_parser(_COMMAND_LOCK, parents=[path_parser])

    return _cli


def main() -> int:
    """ zvault cli entry point.

    :return: 0 on successful execution, >0 otherwise
    """
    _build_command(vars(_build_cli().parse_args())).execute()
