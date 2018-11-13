from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseStack(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_stop_nginx(self):
        self.app = get_test_app(argv=['stack', 'stop', '--nginx'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_stop_php5_fpm(self):
        self.app = get_test_app(argv=['stack', 'stop', '--php'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_stop_mysql(self):
        self.app = get_test_app(argv=['stack', 'stop', '--mysql'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_stop_memcached(self):
        self.app = get_test_app(argv=['stack', 'stop', '--memcache'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_services_stop_all(self):
        self.app = get_test_app(argv=['stack', 'stop'])
        self.app.setup()
        self.app.run()
        self.app.close()
