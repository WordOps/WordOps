from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseStack(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_restart_nginx(self):
        self.app = get_test_app(argv=['stack', 'restart', '--nginx'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_restart_php5_fpm(self):
        self.app = get_test_app(argv=['stack', 'restart', '--php'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_restart_mysql(self):
        self.app = get_test_app(argv=['stack', 'restart', '--mysql'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_restart_memcached(self):
        self.app = get_test_app(argv=['stack', 'restart', '--memcache'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_restart_all(self):
        self.app = get_test_app(argv=['stack', 'restart'])
        self.app.setup()
        self.app.run()
        self.app.close()
