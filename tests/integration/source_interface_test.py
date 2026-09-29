from unittest import TestCase

import batconf.source as source_module


class SourceInterfaceImportTests(TestCase):
    """The import statement itself is what warns, per ADR 0012."""

    def test_import_warns_and_binds_the_abc(t):
        with t.assertWarns(DeprecationWarning) as cm:
            from batconf.source import SourceInterface

        t.assertIs(SourceInterface, source_module._SourceInterface)
        t.assertEqual(
            "'SourceInterface' is deprecated and will be removed in "
            "v0.5.0; use 'SourceInterfaceP' instead.",
            str(cm.warning),
        )
