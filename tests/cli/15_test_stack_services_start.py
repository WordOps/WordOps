from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackStart(test.WOTestCase):

    def test_wo_cli_stack_services_start_nginx(self):
        with WOTestApp(argv=['stack', 'start', '--nginx']) as app:
            app.run()

    def test_wo_cli_stack_services_start_php_fpm(self):
        with WOTestApp(argv=['stack', 'start', '--php']) as app:
            app.run()

    def test_wo_cli_stack_services_start_mysql(self):
        with WOTestApp(argv=['stack', 'start', '--mysql']) as app:
            app.run()

    def test_wo_cli_stack_services_start_all(self):
        with WOTestApp(argv=['stack', 'start']) as app:
            app.run()
