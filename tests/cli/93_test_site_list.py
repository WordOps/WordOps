from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseSite(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_site_list_enable(self):
        self.app = get_test_app(argv=['site', 'list', '--enabled'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_site_list_disable(self):
        self.app = get_test_app(argv=['site', 'list', '--disabled'])
        self.app.setup()
        self.app.run()
        self.app.close()
