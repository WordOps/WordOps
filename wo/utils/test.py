"""Testing utilities for WordOps"""
from cement.utils import test
from wo.cli.main import WOTestApp


class WOTestCase(test.CementTestCase):
    app_class = WOTestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(WOTestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(WOTestCase, self).tearDown()
