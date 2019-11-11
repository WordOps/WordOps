from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackStop(test.WOTestCase):

    def test_wo_cli_stack_services_stop_nginx(self):
        with WOTestApp(argv=['stack', 'stop', '--nginx']) as app:
            app.run()

    def test_wo_cli_stack_services_stop_php_fpm(self):
        with WOTestApp(argv=['stack', 'stop', '--php']) as app:
            app.run()

    def test_wo_cli_stack_services_stop_mysql(self):
        with WOTestApp(argv=['stack', 'stop', '--mysql']) as app:
            app.run()

    def test_wo_cli_stack_services_stop_all(self):
        with WOTestApp(argv=['stack', 'stop']) as app:
            app.run()
