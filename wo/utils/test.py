"""Testing utilities for WordOps"""
from wo.cli.main import WOTestApp
from cement.utils.test import *


class WOTestCase(CementTestCase):
    app_class = WOTestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(WOTestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(WOTestCase, self).tearDown()
