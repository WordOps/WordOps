from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteInfo(test.WOTestCase):

    def test_wo_cli_site_info(self):
        with WOTestApp(argv=['site', 'info', 'html.com']) as app:
            app.run()
