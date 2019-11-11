from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseStackPurge(test.WOTestCase):

    def test_wo_cli_stack_purge_web(self):
        with WOTestApp(
                argv=['stack', 'purge', '--web', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_admin(self):
        with WOTestApp(
                argv=['stack', 'purge', '--admin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_nginx(self):
        with WOTestApp(
                argv=['stack', 'purge', '--nginx', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_php(self):
        with WOTestApp(argv=['stack', 'purge',
                                      '--php', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_mysql(self):
        with WOTestApp(argv=['stack', 'purge',
                                      '--mysql', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_wpcli(self):
        with WOTestApp(argv=['stack', 'purge',
                                      '--wpcli', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_phpmyadmin(self):
        with WOTestApp(
                argv=['stack', 'purge', '--phpmyadmin', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_adminer(self):
        with WOTestApp(
                argv=['stack', 'purge', '--adminer', '--force']) as app:
            app.run()

    def test_wo_cli_stack_purge_utils(self):
        with WOTestApp(argv=['stack', 'purge',
                                      '--utils', '--force']) as app:
            app.run()
