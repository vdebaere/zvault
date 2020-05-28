import argparse

import zvault.command


_COMMAND_NS_KEY = 'command'


def _build_command(args: dict) -> zvault.command.Command:
    for command in zvault.command.COMMANDS:
        if command.command_name() == args[_COMMAND_NS_KEY]:
            return command(args)
    return None


def _build_cli() -> argparse.ArgumentParser:
    _cli = argparse.ArgumentParser()
    sub_parser = _cli.add_subparsers(dest=_COMMAND_NS_KEY, required=True)
    for command in zvault.command.COMMANDS:
        command.build_command_sub_parser(sub_parser)
    return _cli


def main() -> int:
    """ zvault cli entry point.

    :return: 0 on successful execution, >0 otherwise
    """
    _build_command(vars(_build_cli().parse_args())).execute()
