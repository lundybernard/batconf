# Postpones evaluation of type hints for compatibility
from __future__ import annotations
from functools import cached_property
from typing import Any

from pathlib import Path

from .file import (
    file_config_repr,
    missing_file_handlers as _missing_file_handlers,
)
from .types import (
    ConfigFileFormats,
    FileSourceP,
    MissingFileOption as _MissingFileOption,
)


EmptyYamlDict: dict[None, None] = dict()


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
            empty_fallback=EmptyYamlDict,
        )

    @cached_property
    def _data(self) -> dict:
        if self._raw_data is EmptyYamlDict:
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
            if raw is not EmptyYamlDict:
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
            return None
        return None if isinstance(conf, dict) else conf

    def keys(self):
        return self._data.keys()

    def __str__(self) -> str:
        return f'Yaml File: {repr(self)}'

    __repr__ = file_config_repr


# === Yaml File Loader === #


def _load_yaml(
    file_path: Path,
    when_missing: _MissingFileOption,
    empty_fallback: Any,
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
    'PyYAML is required to use YamlSource. '
    'Please install it using `pip install pyyaml`. '
    'Or as an optional extra using `pip install batconf[yaml]`.'
)
