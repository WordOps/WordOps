"""Testing utilities for WordOps"""
from cement.utils.tests import CementTestCase
from wo.cli.main import WOTestApp


class WOTestCase(CementTestCase):
    app_class = WOTestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(WOTestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(WOTestCase, self).tearDown()
