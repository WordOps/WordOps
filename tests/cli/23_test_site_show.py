from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteShow(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_show_edit(self):
        with WOTestApp(argv=['site', 'show', 'example1.com']) as app:
            app.run()
