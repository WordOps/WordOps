from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackStatus(test.WOTestCase):

    def test_wo_cli_stack_services_status_nginx(self):
        with WOTestApp(argv=['stack', 'status', '--nginx']) as app:
            app.run()

    def test_wo_cli_stack_services_status_php_fpm(self):
        with WOTestApp(argv=['stack', 'status', '--php']) as app:
            app.run()

    def test_wo_cli_stack_services_status_mysql(self):
        with WOTestApp(argv=['stack', 'status', '--mysql']) as app:
            app.run()

    def test_wo_cli_stack_services_status_all(self):
        with WOTestApp(argv=['stack', 'status']) as app:
            app.run()
