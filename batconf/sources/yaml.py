# Postpones evaluation of type hints for compatibility
from __future__ import annotations
from functools import cached_property
from typing import Any

from logging import getLogger

from pathlib import Path

from .file import (
    ConfigFileFormats,
    file_config_repr,
    missing_file_handlers as _missing_file_handlers,
)
from .types import FileSourceP, MissingFileOption as _MissingFileOption
from ..source import SourceInterface
from ._compat import make_deprecated_getattr


log = getLogger(__name__)

EmptyYamlConfig: dict[None, None] = dict()


class YamlSource(FileSourceP):
    """Configuration source backed by a YAML file.

    Parameters
    ----------
    file_path : str
        Path to the YAML configuration file.
    file_format : {'environments', 'sections', 'flat'}, default='environments'
        YAML file layout. ``'environments'`` expects a ``batconf`` mapping
        with a ``default_env`` key and per-environment top-level mappings;
        ``'sections'`` uses top-level keys as config namespaces; ``'flat'``
        reads all keys from the top level.
    config_env : str or None, default=read from file
        Active configuration environment. When not provided, the value of
        ``batconf.default_env`` in the YAML file is used.
    missing_file_option : {'warn', 'ignore', 'error'}, default='warn'
        Behaviour when the specified file is missing.

    Examples
    --------
    >>> src = YamlSource(file_path='config.yaml', config_env='dev')
    """

    def __init__(
        self,
        file_path: str,
        file_format: ConfigFileFormats = 'environments',
        config_env: str | None = None,
        missing_file_option: _MissingFileOption = 'warn',
    ):
        self._missing_file_option = missing_file_option
        self._file_format = file_format
        self._config_file_path = Path(file_path)
        self._config_env = config_env

    @cached_property
    def _raw_data(self) -> dict:
        return _load_yaml(
            file_path=self._config_file_path,
            when_missing=self._missing_file_option,
            empty_fallback=EmptyYamlConfig,
        )

    @cached_property
    def _data(self) -> dict:
        if self._raw_data is EmptyYamlConfig:
            return self._raw_data
        if self._file_format == 'environments':
            try:
                return self._raw_data[self._config_env]
            except KeyError as err:
                raise ValueError(
                    f'Config Environment "{self._config_env}" '
                    f'not found in {self._config_file_path}'
                ) from err
        return self._raw_data

    # TODO: Fix type-hints when the next version of MyPy is released
    @property
    def _config_env(self):  # -> str | None:
        if self._file_format != 'environments':
            return None
        if self.__config_env is None:
            raw = self._raw_data
            if raw is not EmptyYamlConfig:
                self.__config_env = raw['batconf']['default_env']
        return self.__config_env

    @_config_env.setter
    def _config_env(self, env):  # str | None
        if self._file_format != 'environments':
            self.__config_env = None  # type: ignore[assignment]
            return
        self.__config_env = env

    def get(self, key: str, path: str | None = None) -> str | None:
        parts = path.split('.') + key.split('.') if path else key.split('.')
        conf: Any = self._data
        try:
            for k in parts:
                conf = conf.get(k)
        except AttributeError:
            log.warning(f'Config path {".".join(parts)} does not exist')
            return None
        return None if isinstance(conf, dict) else conf

    def keys(self):
        return self._data.keys()

    def __str__(self) -> str:
        return f'Yaml File: {repr(self)}'

    __repr__ = file_config_repr


class YamlConfig(SourceInterface):
    """
    Configuration source backed by a YAML file.

    By default, the YAML file is interpreted as an environment-based
    configuration, where top-level keys define environments and
    ``config_env`` selects the active one.

    Parameters
    ----------
    config_file_name : str
        Path to the YAML configuration file.
    config_env : str or None, default=None
        Name of the active configuration environment. When
        ``config_env`` is not provided, the ``default`` environment
        defined in the YAML file is used.
    enable_config_environments : bool, default=True
        Whether the YAML file should be interpreted as an
        environment-based configuration.
    missing_file_option : {'warn', 'ignore', 'error'}, default='warn'
        Behavior when the specified config file is missing.

    Notes
    -----
    When environment-based configuration is enabled, the YAML file is
    expected to contain a top-level ``default`` key identifying the
    default environment, along with top-level mappings for each
    environment.
    """

    __data: Any

    def __init__(
        self,
        config_file_name: str,
        config_env: str | None = None,
        enable_config_environments: bool = True,
        missing_file_option: _MissingFileOption = 'warn',
    ):
        self._missing_file_option = missing_file_option
        self._config_file_path = get_file_path(
            file_name=config_file_name,
            when_missing=missing_file_option,
        )
        self._config_env = config_env

        self._enable_config_environments = enable_config_environments

        self._data = _load_yaml(
            file_path=self._config_file_path,
            when_missing=self._missing_file_option,
        )

    @property
    def _data(self) -> Any:
        return self.__data

    @_data.setter
    def _data(self, config: dict):
        if self._enable_config_environments:
            if not self._config_env:
                self._config_env = config['default']
            self.__data = config[self._config_env]
        else:
            self.__data = config

    @property
    def _file_format(self) -> str:
        if self._enable_config_environments:
            return 'environments'
        return 'sections'

    def __getitem__(self, key: str) -> SourceInterface | str:
        path = key.split('.')
        conf = self._data
        for k in path:
            conf = conf[k]
        return conf

    def __str__(self) -> str:
        return f'Yaml File: {repr(self)}'

    __repr__ = file_config_repr

    def keys(self) -> list[str]:
        return self._data.keys()

    def get(self, key: str, module: str | None = None) -> str | None:
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = key.split('.')

        conf = self._data
        for k in path:
            if not (conf := conf.get(k)):
                return conf
        return conf


_YamlConfig = YamlConfig
del YamlConfig

__getattr__ = make_deprecated_getattr(
    deprecated={'YamlConfig': 'YamlSource'},
    module_globals=globals(),
    module_name=__name__,
    targets={'YamlConfig': '_YamlConfig'},
)


_missing_config_warning = 'Config File not found'


# === OS File Checker === #


def get_file_path(
    file_name: str, when_missing: _MissingFileOption = 'warn'
) -> Path:
    path = Path(file_name)

    if path.is_file():
        return path

    relpath = path.resolve()
    if relpath.is_file():
        return relpath

    if when_missing == 'warn':
        log.warning(_missing_config_warning)
    elif when_missing == 'error':
        raise FileNotFoundError(
            f'Could not find Yaml Config file'
            f' Using absolute path: {path}'
            f' or relative path: {relpath}.'
        )

    return path


# === Yaml File Loader === #

# TODO: replace when we implement YamlSource
_empty_yaml_config: dict = {'default': 'none', 'none': {}}


def _load_yaml(
    file_path: Path,
    when_missing: _MissingFileOption,
    empty_fallback: Any = _empty_yaml_config,
) -> dict:
    return _missing_file_handlers[when_missing](
        loader_fn=_load_yaml_file,
        file_path=file_path,
        empty_fallback=empty_fallback,
    )


def _load_yaml_file(file_path: Path) -> dict:
    try:
        import yaml
    except ImportError as e:
        raise ImportError(_YAML_IMPORT_ERROR_MSG) from e

    with open(file_path) as env_file:
        return yaml.load(env_file, Loader=yaml.BaseLoader)


_YAML_IMPORT_ERROR_MSG = (
    'PyYAML is required to use YamlConfig. '
    'Please install it using `pip install pyyaml`.'
    'Or as an optional extra using `pip install batconf[yaml]`.'
)
