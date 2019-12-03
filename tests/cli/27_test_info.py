from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseInfo(test.WOTestCase):

    def test_wo_cli_info_mysql(self):
        with WOTestApp(argv=['info', '--mysql']) as app:
            app.run()

    def test_wo_cli_info_php(self):
        with WOTestApp(argv=['info', '--php']) as app:
            app.run()

    def test_wo_cli_info_nginx(self):
        with WOTestApp(argv=['info', '--nginx']) as app:
            app.run()
