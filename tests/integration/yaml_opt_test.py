from unittest import TestCase, skipIf

from batconf.sources.tests.yaml_test import (
    EXAMPLE_CONFIG_DICT,
    EXAMPLE_CONFIG_YAML,
    EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
    EXAMPLE_CONFIG_WITHOUT_ENV_DICT,
)

_PYYAML_INSTALLED = True
try:
    import yaml
except ImportError:
    _PYYAML_INSTALLED = False


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class SourcesYamlUnittestStaticValuesTests(TestCase):
    '''If pyyaml is installed,
    use it to validate that our assumptions
    about how yaml strings will be converted to dictionaries
    '''
    def test_EXAMPLE_CONFIG_DICT(t):
        loaded_dict = yaml.load(
            EXAMPLE_CONFIG_YAML,
            Loader=yaml.BaseLoader
        )
        t.assertDictEqual(EXAMPLE_CONFIG_DICT, loaded_dict)

    def test_EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS(t):
        loaded_envless_dict = yaml.load(
            EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
            Loader=yaml.BaseLoader,
        )
        t.assertDictEqual(
            EXAMPLE_CONFIG_WITHOUT_ENV_DICT,
            loaded_envless_dict
        )


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class SourcesFileUnittestStaticValuesTests(TestCase):
    def test_EXAMPLE_CONFIG_DICT(t):
        loaded_dict = yaml.load(
            EXAMPLE_CONFIG_YAML,
            Loader=yaml.BaseLoader
        )
        t.assertDictEqual(EXAMPLE_CONFIG_DICT, loaded_dict)

    def test_EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS(t):
        loaded_envless_dict = yaml.load(
            EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
            Loader=yaml.BaseLoader,
        )
        t.assertDictEqual(
            EXAMPLE_CONFIG_WITHOUT_ENV_DICT,
            loaded_envless_dict
        )
