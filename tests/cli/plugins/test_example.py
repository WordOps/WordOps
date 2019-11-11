"""Tests for Example Plugin."""

from wo.utils import test
from wo.cli.main import WOTestApp


class ExamplePluginTestCase(test.WOTestCase):
    def test_load_example_plugin(self):
        with WOTestApp as app:
            app.plugin.load_plugin('example')
