"""Tests for Example Plugin."""

from wo.utils import WOTestCase


class ExamplePluginTestCase(WOTestCase):
    def test_load_example_plugin(self):
        self.app.setup()
        self.app.plugin.load_plugin('example')
