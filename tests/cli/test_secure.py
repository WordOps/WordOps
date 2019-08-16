from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseSecure(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_secure_auth(self):
        self.app = get_test_app(argv=['secure', '--auth', 'abc', 'superpass'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_secure_port(self):
        self.app = get_test_app(argv=['secure', '--port', '22222'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_secure_ip(self):
        self.app = get_test_app(argv=['secure', '--ip', '172.16.0.1'])
        self.app.setup()
        self.app.run()
        self.app.close()
