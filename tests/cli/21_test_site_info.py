from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteInfo(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_site_info(self):
        with WOTestApp(argv=['site', 'info', 'example1.com']) as app:
            app.run()
