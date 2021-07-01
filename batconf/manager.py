from dataclasses import dataclass, fields, is_dataclass

from .source import SourceList


class Configuration:
    '''
    Input: an application config in dictionary form

    Configuration Hierarchy:
    1. Command line arguments
        any argument passed in via command line superseeds all other configs
        this must be passed to the Configuration object by the cli parser
    2. Environment Variables
        Any environment variable with the format BAT_SECTION_SUBSECTION_KEY
        will override the value of configuration.section.subsection.key
    3. Config File
        User defined config file,
        a default file in the current working directory may be set
        the config file may be specified as a cli arg
        the config file path may be set to the BAT_CONFIG_FILE ENV variable
    4. Default Values
        default values may be set in the config specification
    '''

    def __init__(
        self,
        source_list: SourceList,
        config_class: dataclass,
    ):
        self._config_sources = source_list
        self._config_class = config_class

        for f in fields(self._config_class):
            if is_dataclass(f.type):
                setattr(self, f.name, Configuration(
                    source_list=source_list,
                    config_class=f.type,
                ))

    def __getattr__(self, name):
        return self._get_config_opt(name, self._mod_)

    def _get_config_opt(self, key, path=None):
        if value := self._config_sources.get(key, path=path):
            return value

        raise AttributeError(
            'required configuration value not found.\n'
            f' please provide {key}'
            ' as a commandline argument\n'
            f' or add {self._config_class.__module__}.{key}'
            ' to your config file\n'
            f' or add {self._mod_.replace(".", "_").upper()}_{key.upper()}'
            ' to your Environment'
        )

    @property
    def _mod_(self):
        return self._config_class.__module__
