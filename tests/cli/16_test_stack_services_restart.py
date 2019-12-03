from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackRestart(test.WOTestCase):

    def test_wo_cli_stack_services_restart_nginx(self):
        with WOTestApp(argv=['stack', 'restart', '--nginx']) as app:
            app.run()

    def test_wo_cli_stack_services_restart_php_fpm(self):
        with WOTestApp(argv=['stack', 'restart', '--php']) as app:
            app.run()

    def test_wo_cli_stack_services_restart_mysql(self):
        with WOTestApp(argv=['stack', 'restart', '--mysql']) as app:
            app.run()

    def test_wo_cli_stack_services_restart_all(self):
        with WOTestApp(argv=['stack', 'restart']) as app:
            app.run()
