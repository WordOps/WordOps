from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteDisable(test.WOTestCase):

    def test_wo_cli_site_disable(self):
        with WOTestApp(argv=['site', 'disable', 'html.com']) as app:
            app.run()
