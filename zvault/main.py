import argparse


class Application():

    _cli: argparse.ArgumentParser

    def __init__(self):
        self._cli = None
        self._init_cli()

    def _init_cli(self) -> None:
        self._cli = argparse.ArgumentParser()
        sub_parser = self._cli.add_subparsers(dest='action', required=True)

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

        create_parser = sub_parser.add_parser('create',
                                              parents=[path_parser, gpg_parser])
        create_parser.add_argument('--parent', '-p',
                                   action='store',
                                   dest='parent',
                                   metavar='parent_dataset',
                                   help='specifies the parent dataset in which '
                                        'the vault will be created')

        destroy_parser = sub_parser.add_parser('destroy', parents=[path_parser])
        destroy_parser.add_argument('-f', '--force',
                                    action='store_true',
                                    dest='force',
                                    help='force the removal of the vault, even '
                                         'when files are in use')

        sub_parser.add_parser('unlock', parents=[path_parser, gpg_parser])

        sub_parser.add_parser('lock', parents=[path_parser])

    def run(self) -> int:
        try:
            self._cli.parse_args()
        except:
            return 1
        return 0


def main() -> int:
    """ zvault cli entry point.

    :return: 0 on successful execution, >0 otherwise
    """
    return Application().run()
