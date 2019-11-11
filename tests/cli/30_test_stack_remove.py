from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStack(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_stack_remove_web(self):
        with WOTestApp(argv=['stack', 'remove', '--web', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_admin(self):
        with WOTestApp(argv=['stack', 'remove', '--admin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_nginx(self):
        with WOTestApp(argv=['stack', 'remove', '--nginx', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_php(self):
        with WOTestApp(argv=['stack', 'remove', '--php', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_mysql(self):
        with WOTestApp(argv=['stack', 'remove', '--mysql', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_wpcli(self):
        with WOTestApp(argv=['stack', 'remove', '--wpcli', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_phpmyadmin(self):
        with WOTestApp(argv=['stack', 'remove',
                                      '--phpmyadmin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_adminer(self):
        with WOTestApp(
                argv=['stack', 'remove', '--adminer', '--force']) as app:
            app.run()

    def test_wo_cli_stack_install_utils(self):
        with WOTestApp(argv=['stack', 'remove', '--utils', '--force']) as app:
            app.run()
