from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteList(test.WOTestCase):

    def test_wo_cli_site_list_enable(self):
        with WOTestApp(argv=['site', 'list', '--enabled']) as app:
            app.run()

    def test_wo_cli_site_list_disable(self):
        with WOTestApp(argv=['site', 'list', '--disabled']) as app:
            app.run()
