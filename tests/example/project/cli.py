from typing import Sequence, Optional as Opt

from sys import exit
import logging
from argparse import ArgumentParser, Namespace, REMAINDER

from .lib import hello_world, get_config_str, get_data_from_server


log = logging.getLogger('root')


def BATCLI(ARGS: Opt[Sequence[str]] = None):
    p = argparser()
    # Execute
    # get only the first command in args
    args = p.parse_args(args=ARGS)
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
        nargs=REMAINDER,  # Accept zero or more arguments
        help='Configuration key-value pairs to print',
    )

    fetch_data = commands.add_parser(
        'fetch-data',
        description='fetch data from a remote source',
        help='for details use fetch-data --help',
    )
    fetch_data.set_defaults(func=Commands.get_data_from_server)

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
        """
        Using a function with a traditional signature,
        we can pull individual keys off the config and pass them to the func.
        """
        from .conf import get_config

        # Get the global configuration object, providing the CLI Args
        # so that args from the cli can overwrite other config settings.
        cfg = get_config(cli_args=args)

        # Select the subsection of the config that we need
        client_cfg = cfg.submodule.sub

        print(get_data_from_server(key1=client_cfg.key1, key2=client_cfg.key2))


def _parse_overrides(args: Namespace) -> Namespace:
    """
    Example of how to parse arbitrary key-value pairs,
    and add them to the args Namespace.

    ex:
    ```
    > bat print_config key1=crash key2=override`
    Root <class 'project.ProjectConfig'>:
        |- submodule <class 'project.submodule.SubmoduleConfig'>:
        |    |- sub <class 'project.submodule.sub.MyClient.Config'>:
        |    |    |- key1: "crash"
        |    |    |- key2: "override"
    ```

    Notes: without a NestedNamespace, the key value will overwrite every
    option where the final key in its path matches.
    project.key1, project.thing1.key1, project.thing2.key1, etc.
    would all be set to "crash"

    We need to update the example to demonstrate usage of a NestedNamespace
    such that the keys to be overwritten require a full path.
    ex:
        ```
    > bat print_config project.submodule.sub.MyClient.key1=crash key2=override`
    Root <class 'project.ProjectConfig'>:
        |- submodule <class 'project.submodule.SubmoduleConfig'>:
        |    |- sub <class 'project.submodule.sub.MyClient.Config'>:
        |    |    |- key1: "crash"
        |    |    |- key2: "DEFAULT VALUE"
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
