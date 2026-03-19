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

from typing import overload

from .conf import CFG
from .submodule.client import MyClient


def hello_world() -> str:
    return 'Hello World!'


def get_config_str() -> str:
    return str(CFG)


@overload
def get_data_from_server(clientid: str) -> str:
    """Fetch data for a configured client.

    Parameters
    ----------
    clientid : str
        Client identifier from configuration.

    Returns
    -------
    str
        Data returned by the selected client.
    """
    pass


@overload
def get_data_from_server(*, key1: str, key2: str) -> str:
    """
    Get data using explicit client credentials.

    Parameters
    ----------
    key1 : str
        First client credential.
    key2 : str
        Second client credential.

    Returns
    -------
    str
        Retrieved data.
    """
    pass


def get_data_from_server(
    clientid: str | None = None,
    key1: str | None = None,
    key2: str | None = None,
) -> str:
    """Get data for a client.

    Parameters
    ----------
    clientid : str, optional
        Client identifier.
    key1 : str, optional
        First client credential.
    key2 : str, optional
        Second client credential.

    Returns
    -------
    str
        Retrieved data.
    """
    # get the configuration for the specified clientid from your configuration
    if clientid:
        my_client_config = getattr(CFG.clients, clientid)
        return MyClient.from_config(my_client_config).fetch_data()

    client = MyClient(key1=key1, key2=key2)
    return client.fetch_data()


def get_opt() -> str:
    return (
        f'cfg.opt was set to `{CFG.opt}`\n'
        f'cfg.opt2 was set to `{CFG.opt2}`\n'
        f'cfg.clients.ClientA.key1 was set to `{CFG.clients.clientA.key1}`'
    )
