from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteEnable(test.WOTestCase):

    def test_wo_cli_site_enable(self):
        with WOTestApp(argv=['site', 'enable', 'html.com']) as app:
            app.run()
