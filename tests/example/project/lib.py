"""
This example library module,
demonstrates use of batconf's Configuration manager.

Notes
-----
- Conf.py provides a Global CFG object
- The application UI (CLI, GUI, Rest API, etc.) is responsible for updating
  the global Configuration, using insert_source as needed.
- While this is a useful pattern, it is not required by batconf.
  You are free to use the Configuration manager as best suits your project.
  get_config() can be used directly without the need for a Global CFG.
"""

from .conf import CFG
from .submodule.client import MyClient


def hello_world() -> str:
    return 'Hello World!'


def get_config_str() -> str:
    return str(CFG)


def get_data_from_server_config(clientid: str) -> str:
    """Fetch data using a client defined in the global configuration.

    This function looks up the named client in ``CFG.clients`` and uses that
    configuration to construct a client instance.

    Parameters
    ----------
    clientid : str
        Client identifier from the global configuration.

    Returns
    -------
    str
        Data retrieved from the server.
    """
    # get the configuration for the specified clientid from your configuration
    my_client_config = CFG.clients[clientid]
    return MyClient.from_config(my_client_config).fetch_data()


def get_data_from_server(
    key1: str,
    key2: str,
) -> str:
    """Fetch data using explicit client credentials.

    This function bypasses the global configuration and creates the client
    directly from the provided credentials.

    Parameters
    ----------
    key1 : str
        First client credential.
    key2 : str
        Second client credential.

    Returns
    -------
    str
        Data retrieved from the server.
    """
    client = MyClient(key1=key1, key2=key2)
    return client.fetch_data()


def get_opt() -> str:
    return (
        f'cfg.opt was set to `{CFG.opt}`\n'
        f'cfg.opt2 was set to `{CFG.opt2}`\n'
        f'cfg.clients.ClientA.key1 was set to `{CFG.clients.clientA.key1}`'
    )
