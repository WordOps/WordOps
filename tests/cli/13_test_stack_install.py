from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackInstall(test.WOTestCase):

    def test_wo_cli_stack_install_nginx(self):
        with WOTestApp(argv=['stack', 'install', '--nginx']) as app:
            app.run()

    def test_wo_cli_stack_install_php(self):
        with WOTestApp(argv=['stack', 'install', '--php']) as app:
            app.run()

    def test_wo_cli_stack_install_php73(self):
        with WOTestApp(argv=['stack', 'install', '--php73']) as app:
            app.run()

    def test_wo_cli_stack_install_mysql(self):
        with WOTestApp(argv=['stack', 'install', '--mysql']) as app:
            app.run()

    def test_wo_cli_stack_install_wpcli(self):
        with WOTestApp(argv=['stack', 'install', '--wpcli']) as app:
            app.run()

    def test_wo_cli_stack_install_phpmyadmin(self):
        with WOTestApp(argv=['stack', 'install', '--phpmyadmin']) as app:
            app.run()

    def test_wo_cli_stack_install_adminer(self):
        with WOTestApp(argv=['stack', 'install', '--adminer']) as app:
            app.run()

    def test_wo_cli_stack_install_utils(self):
        with WOTestApp(argv=['stack', 'install', '--utils']) as app:
            app.run()
