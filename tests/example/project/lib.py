"""
This example library module,
which demonstrates use of batconf's Configuration manager.

A few notes:
* This example assumes that your UI code (CLI, GUI, Rest API, etc.),
  will rely on batconf exclusively for configuration options.
  * Note how the CLI in cli.py passes cli_args to get_config.
    A similar approach can be used for other UIs.
  * This approach keeps config access usage in the library,
    so does not get scattered throughout your codebase.
  * While this is a useful pattern, it is not required by batconf.
    You are free to use the Configuration manager as best suits your project.
"""

from typing import Callable
from functools import wraps
from argparse import Namespace

from .conf import get_config, Configuration, CONFIG_FILE_NAME
from .submodule.client import MyClient


def configurable(func: Callable) -> Callable:
    """
    configurable is a decorator for library functions.
    It modifies the functon signature to accept parameters
    needed for the get_config function.
    """

    @wraps(func)
    def wrapper(
        cli_args: Namespace | None = None,
        config_file_name: str = CONFIG_FILE_NAME,
        config_env: str | None = None,
        **kwargs,
    ):
        # Fetch the configuration using get_config
        cfg = get_config(
            cli_args=cli_args,
            config_file_name=config_file_name,
            config_env=config_env,
        )
        # Pass the configuration as the first argument to the wrapped function
        return func(cfg=cfg, **kwargs)

    return wrapper


def hello_world() -> str:
    return 'Hello World!'


@configurable
def get_config_str(cfg: Configuration) -> str:
    return str(cfg)


@configurable
def get_data_from_server(clientid: str, cfg: Configuration) -> str:
    """Get data from the specified client"""
    # get the configuration for the specified clientid from your configuration
    my_client_config = getattr(cfg.clients, clientid)

    client = MyClient.from_config(my_client_config)
    return client.fetch_data()


@configurable
def get_opt(cfg: Configuration) -> str:
    return (
        f'cfg.opt was set to `{cfg.opt}`\n'
        f'cfg.opt2 was set to `{cfg.opt2}`\n'
        f'cfg.clients.ClientA.key1 was set to `{cfg.clients.clientA.key1}`'
    )
