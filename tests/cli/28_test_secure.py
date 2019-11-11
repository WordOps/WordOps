from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSecure(test.WOTestCase):

    def test_wo_cli_secure_auth(self):
        with WOTestApp(argv=['secure', '--auth', 'abc', 'superpass']) as app:
            app.run()

    def test_wo_cli_secure_port(self):
        with WOTestApp(argv=['secure', '--port', '22222']) as app:
            app.run()

    def test_wo_cli_secure_ip(self):
        with WOTestApp(argv=['secure', '--ip', '172.16.0.1']) as app:
            app.run()
