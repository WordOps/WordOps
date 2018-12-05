"""Tests for Example Plugin."""

from wo.utils import test

class ExamplePluginTestCase(test.WOTestCase):
    def test_load_example_plugin(self):
        self.app.setup()
        self.app.plugin.load_plugin('example')
