from typing import Sequence

from sys import exit
import logging
from argparse import ArgumentParser, Namespace, Action

from .lib import hello_world, get_config_str, get_data_from_server, get_opt


log = logging.getLogger('root')


def BATCLI(ARGS: Sequence[str] | None = None):
    p = argparser()
    # Execute
    # get only the first command in args
    args = p.parse_args(args=ARGS)
    # post-processing to collect arbitrary extra arguments
    args = _parse_overrides(args)
    Commands.set_log_level(args)
    # execute function set for parsed command
    if not hasattr(Commands, args.func.__name__):  # pragma: no cover
        p.print_help()
        exit(1)
    args.func(args)
    exit(0)


def argparser():
    p = ArgumentParser(
        description='Utility for executing various bat tasks',
        usage='bat [<args>] <command>',
    )
    p.set_defaults(func=get_help(p))

    p.add_argument(
        '-v',
        '--verbose',
        help='enable INFO output',
        action='store_const',
        dest='loglevel',
        const=logging.INFO,
    )
    p.add_argument(
        '--debug',
        help='enable DEBUG output',
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
    )
    p.add_argument(
        '-c',
        '--conf',
        '--config_file',
        dest='config_file',
        default=None,
        help='specify a config file to get environment details from.'
        ' default=./config.yaml',
    )
    p.add_argument(
        '-e',
        '--env',
        '--config_environment',
        dest='config_env',
        default=None,
        help='specify the remote environment to use from the config file',
    )

    # Add a subparser to handle sub-commands
    commands = p.add_subparsers(
        dest='command',
        title='commands',
        description='for additonal details on each command use: '
        '"bat {command name} --help"',
    )
    # hello args
    hello = commands.add_parser(
        'hello',
        description='execute command hello',
        help='for details use hello --help',
    )
    hello.set_defaults(func=Commands.hello)

    print_config = commands.add_parser(
        'print-config',
        description='print the application configuration',
        help='for details use print-config --help',
    )
    print_config.set_defaults(func=Commands.print_config)
    print_config.add_argument(
        'key_values',
        nargs='*',  # Accept zero or more arguments
        action=FilterHelp,
        help='Configuration key-value pairs to print',
    )

    fetch_data = commands.add_parser(
        'fetch-data',
        description='fetch data from a remote source',
        help='for details use fetch-data --help',
    )
    fetch_data.add_argument(
        'clientid',
        default='clientA',
        choices=['clientA', 'clientB'],
    )
    fetch_data.add_argument(
        'key_values',
        nargs='*',
        action=FilterHelp,
        help='optional configuration override values',
    )
    fetch_data.set_defaults(func=Commands.get_data_from_server)

    # This example shows how to set various configuration options via the cli
    set_cli_opt = commands.add_parser(
        'cliopt',
        description='set the "opt" configuration option',
    )
    set_cli_opt.set_defaults(func=Commands.set_cli_opt)
    # Add a required positional argument to set cfg.opt
    # This adds a new value to the configuration
    set_cli_opt.add_argument('project.opt', help='Set the value of cfg.opt')
    # Add an argument flag with a default value to cfg.opt2
    # This also adds a new value to the configuration
    set_cli_opt.add_argument(
        '--opt2', dest='project.opt2', default='default opt2'
    )
    # Add an argument which overrides an existing value in the configuration
    set_cli_opt.add_argument('--opt3', dest='project.clients.clientA.key1')
    return p


def get_help(parser):
    def help(_: Namespace):
        parser.print_help()

    return help


class Commands:
    """
    These functions are called by the CLI
    Each accepts the ARGS: Namespace returned by Argparser.parse_args
    and returns a String, which will be printed to STDOUT.
    """

    @staticmethod
    def hello(_: Namespace):
        print(hello_world())

    @staticmethod
    def set_log_level(args: Namespace):
        if args.loglevel:
            log.setLevel(args.loglevel)
        else:
            log.setLevel(logging.ERROR)

    @staticmethod
    def print_config(args: Namespace):
        """
        Using this style, we can simply pass the ARGS Namespace
        from argparser to the library function.
        """
        print(args)

        print(get_config_str(cli_args=args))

    @staticmethod
    def get_data_from_server(args: Namespace):
        print(get_data_from_server(clientid=args.clientid, cli_args=args))

    @staticmethod
    def get_data_from_server_args(args: Namespace):
        """
        Using a function with a traditional signature,
        we can pull individual keys off the config and pass them to the func.
        """
        from .conf import get_config

        cfg = get_config(cli_args=args)
        # Make this subscriptable, issue #91:
        # client_cfg = cfg.client[args.clientid]
        client_cfg = getattr(cfg.clients, args.clientid)
        print(get_data_from_server(key1=client_cfg.key1, key2=client_cfg.key2))

    @staticmethod
    def set_cli_opt(args: Namespace):
        print(get_opt(cli_args=args))


def _parse_overrides(args: Namespace) -> Namespace:
    """
    Example of how to parse arbitrary key-value pairs,
    and add them to the args Namespace.

    ```
    > bat print_config project.submodule.client.key1=crash \
        project.clients.key2=override`
    project <class 'project.cfg.ProjectSchema'>:
        |- submodule <class 'project.cfg.SubmoduleConfig'>:
        |    |- client <class 'project.submodule.client.MyClient.Config'>:
        |    |    |- key1: "crash"
        |    |    |- key2: "DEFAULT VALUE"
        |- clients <class 'project.cfg.ClientsSchema'>:
        |    |- key1: "DEFAULT_VALUE"
        |    |- key2: "override"
    ```
    """
    try:
        key_values = args.key_values
    except AttributeError:
        return args

    for item in key_values:
        k, v = item.split('=')
        setattr(args, k, v)

    return args


class FilterHelp(Action):
    """
    Used when collecting arbitrary arguments from a comand
    This filters out the help command, so it behaves as expected.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        filtered_values = [v for v in values if v not in ('-h', '--help')]
        setattr(namespace, self.dest, filtered_values)
