from unittest import TestCase
from unittest.mock import patch

from dataclasses import dataclass
from os import path

from batconf.manager import Configuration, SourceList
from batconf.sources.ini import IniConfig
from batconf.sources.env import EnvConfig


# === Configuration Schema === #
@dataclass
class Level2ConfigA:
    value: str = 'level 2 config A value'


@dataclass
class Level2ConfigB:
    value: str = 'level 2 config B value'


@dataclass
class Level1ConfigA:
    l2a: Level2ConfigA
    l2b: Level2ConfigB
    value: str = 'level 1 config A value'


@dataclass
class Level1ConfigB:
    l2a: Level2ConfigA
    l2b: Level2ConfigB
    value: str = 'level 1 config B value'


@dataclass
class SubSection:
    doc: str
    key1: str
    schema_default: str = 'subsection default from schema'


@dataclass
class RootConfigSchema:
    l1a: Level1ConfigA
    l1b: Level1ConfigB
    subsection: SubSection
    nodefault: str
    value: str = 'root config value'


class FreeFormConfigTreeTests(TestCase):
    def setUp(t) -> None:
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_freeform_config_tree(t) -> None:
        # Example Configuration,
        # with no external sources,
        # the schema its self provides all default values
        cfg = Configuration(
            source_list=SourceList([]),
            config_class=RootConfigSchema,
            path='root',
        )

        t.assertIsInstance(cfg, Configuration)
        t.assertEqual(cfg.value, 'root config value')
        t.assertIsInstance(cfg.l1a, Configuration)
        t.assertEqual(cfg.l1a.value, 'level 1 config A value')
        t.assertIsInstance(cfg.l1a.l2a, Configuration)
        t.assertEqual(cfg.l1a.l2a.value, 'level 2 config A value')
        t.assertIsInstance(cfg.l1a.l2b, Configuration)
        t.assertEqual(cfg.l1a.l2b.value, 'level 2 config B value')

        t.assertEqual(cfg.l1b.value, 'level 1 config B value')
        t.assertEqual(cfg.l1b.l2a.value, 'level 2 config A value')
        t.assertEqual(cfg.l1b.l2b.value, 'level 2 config B value')

        with t.assertRaises(AttributeError):
            _ = cfg.nodefault

    def test_environments_config(t) -> None:
        config_file_name = path.join(t.this_dir, 'data', 'envs.config.ini')

        config_source = IniConfig(
            file_path=config_file_name, file_format='environments'
        )
        t.assertEqual(config_source.get('doc'), 'our testing environment')
        t.assertIsNone(config_source.get('project'))

        source_list = SourceList([config_source])
        t.assertEqual(source_list.get('doc'), 'our testing environment')

        cfg = Configuration(
            source_list=source_list,
            config_class=RootConfigSchema,
            # path='project',  # default = 'configuration_test'
        )

        # A Configuration's _path is used to lookup values from config sources
        t.assertEqual(cfg._path, 'configuration_test')
        # sources with an 'environments' format do not have access to the full
        # config file tree,
        # their entry-point is the specified environment itself
        # In this test, cfg.doc accesses `[test.configuration_test] / doc`
        # from the file
        t.assertEqual(cfg.doc, 'configuration_test.py options')
        # values defined in the RootConfig schema are also accessible
        t.assertEqual(cfg.value, 'root config value')

        # while a config source can look up any values in its tree
        t.assertEqual(
            source_list.get('configuration_test.notinschema.doc'),
            'file section not included in the config schema',
        )
        # sub-sections must be declared in the schema
        # for a Configuration to access them
        with t.assertRaises(AttributeError):
            _ = cfg.notinschema
        with t.assertRaises(AttributeError):
            _ = cfg.notinschema.doc
        # but it can access values which are not in the schema
        t.assertEqual(
            cfg.subsection.opt_not_in_schema,
            'an option from the file, but not in the schema',
        )
        # and values which are set as defaults in the schema,
        # but are not in any source
        t.assertEqual(
            cfg.subsection.schema_default, 'subsection default from schema'
        )

        # === Accessing SubConfigs === #
        # Getting a submodule from a Configuration
        # returns another Configuration
        subsection = cfg.subsection
        t.assertIsInstance(subsection, Configuration)
        # which has an expanded _path
        t.assertEqual(subsection._path, 'configuration_test.subsection')
        # so it can be used to shorten access to options
        t.assertIs(cfg.subsection.doc, subsection.doc)

        t.assertEqual(
            cfg.subsection.opt0,
            'envs.config.ini/test.configuration_test.subsection: opt0',
        )

    def test_sections_config(t) -> None:
        config_file_name = path.join(t.this_dir, 'data', 'sections.config.ini')
        config_source = IniConfig(
            file_path=config_file_name, file_format='sections'
        )
        source_list = SourceList([config_source])

        @dataclass
        class SubSection0Schema:
            value0: str
            opt2: str
            opt3: str = 'opt3 default'

        @dataclass
        class ConfigTestSchema:
            sub0: SubSection0Schema
            opt1: str = 'Configuration: opt1 default'

        cfg = Configuration(
            source_list=source_list,
            config_class=ConfigTestSchema,
            # path='project-name',  # default: 'configuration_test'
        )

        # NOTE: presently, section-based configs still require a parent section
        # which should be set to your project's name,
        # but defaults to the module name
        t.assertEqual(
            cfg.opt1,
            'sections.config.ini :: configuration_test :: opt1',
        )
        t.assertEqual(
            cfg.sub0.doc,
            'sections.config.ini :: configuration_test.sub0 :: doc',
        )
        # sections not defined in the schema are inaccessible
        with t.assertRaises(AttributeError):
            _ = cfg.noschema
        # options not defined in the schema can be accessed
        t.assertEqual(
            cfg.optnoschema,
            'sections.config.ini :: configuration_test :: '
            'option not in schema',
        )

    def test_flat_config_values(t) -> None:
        # Get the absolute path to the test flat.config.ini file
        example_dir = path.dirname(path.realpath(__file__))
        config_file_name = path.join(example_dir, 'data', 'flat.config.ini')

        config_source = IniConfig(
            file_path=config_file_name, file_format='flat'
        )
        source_list = SourceList([config_source])

        # Schemas for flat configurations should not contain nested Schemas
        @dataclass
        class FlatConfigSchema:
            opt2: str
            opt3: str = 'opt3 default'

        cfg = Configuration(
            source_list=source_list,
            config_class=FlatConfigSchema,
            # path='application',  # path does not affect flat files
        )

        # options not defined in the schema are accessible
        t.assertEqual(cfg.opt1, 'flat file option 1')
        # options with no assigned values raise an error
        with t.assertRaises(AttributeError):
            t.assertEqual(cfg.opt2, 'sir not appearing in this film')
        # the schema may provide default values
        t.assertEqual(cfg.opt3, 'opt3 default')

    @patch.dict(
        'batconf.sources.env.os.environ',
        {
            'ROOT_VALUE': 'ENVIRONMENT root config value',
            'ROOT_L1A_VALUE': 'ENVIRONMENT level 1 config A value',
        },
    )
    def test_sub_configs_respect_environment_variables(t) -> None:
        """REF: github #2
        """
        cfg = Configuration(
            source_list=SourceList([EnvConfig()]),
            config_class=RootConfigSchema,
            path='root',
        )

        t.assertEqual(cfg.value, 'ENVIRONMENT root config value')
        t.assertIsInstance(cfg.l1a, Configuration)
        t.assertEqual(cfg.l1a.value, 'ENVIRONMENT level 1 config A value')
        sub_config = cfg.l1a
        t.assertEqual(sub_config.value, 'ENVIRONMENT level 1 config A value')
