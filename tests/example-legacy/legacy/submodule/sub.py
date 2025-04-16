from dataclasses import dataclass


KEY2_DEFAULT = 'DEFAULT VALUE'


class MyClient:
    """Example class that utilizes batconf

    Attributes
    ----------
    Config : dataclasses.DataClass
        Define a dataclass with the configuration keys your class requires.

        We chose the builtin dataclass for this purpose
        to avoid requiring a dependency on batconf in submodules.

        The Config class can be a class attribute,
        or stand-alone class in the module.
    """

    # Define a dataclass with the configuration keys your class requires
    # We chose dataclass for this to avoid requiring a dependency on batconf
    @dataclass
    class Config:
        key1: str
        key2: str = KEY2_DEFAULT

    @classmethod
    def from_config(cls, config: Config) -> 'MyClient':
        return cls(config.key1, config.key2)

    def __init__(self, key1: str, key2: str = KEY2_DEFAULT):
        self.key1 = key1
        self.key2 = key2

    def fetch_data(self):
        return f'MyClient data: {self.key1=}, {self.key2=}'
