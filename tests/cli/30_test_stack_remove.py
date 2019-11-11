from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackRemove(test.WOTestCase):

    def test_wo_cli_stack_remove_admin(self):
        with WOTestApp(argv=['stack', 'remove', '--admin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_nginx(self):
        with WOTestApp(argv=['stack', 'remove', '--nginx', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_php(self):
        with WOTestApp(argv=['stack', 'remove', '--php', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_mysql(self):
        with WOTestApp(argv=['stack', 'remove', '--mysql', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_wpcli(self):
        with WOTestApp(argv=['stack', 'remove', '--wpcli', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_phpmyadmin(self):
        with WOTestApp(argv=['stack', 'remove',
                                      '--phpmyadmin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_adminer(self):
        with WOTestApp(
                argv=['stack', 'remove', '--adminer', '--force']) as app:
            app.run()

    def test_wo_cli_stack_remove_utils(self):
        with WOTestApp(argv=['stack', 'remove', '--utils', '--force']) as app:
            app.run()
