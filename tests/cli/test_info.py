from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseInfo(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_info_mysql(self):
        self.app = get_test_app(argv=['info', '--mysql'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_info_php(self):
        self.app = get_test_app(argv=['info', '--php'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_info_nginx(self):
        self.app = get_test_app(argv=['info', '--nginx'])
        self.app.setup()
        self.app.run()
        self.app.close()
