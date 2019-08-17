from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseStack(test.WOTestCase):

    def test_wo_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_web(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--web', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_admin(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--admin', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_nginx(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--nginx', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_php(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--php', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_mysql(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--mysql', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_wpcli(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--wpcli', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_phpmyadmin(self):
        self.app = get_test_app(
            argv=['stack', 'purge', '--phpmyadmin', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_adminer(self):
        self.app = get_test_app(
            argv=['stack', 'purge', '--adminer', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

    def test_wo_cli_stack_purge_utils(self):
        self.app = get_test_app(argv=['stack', 'purge',
                                      '--utils', '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()
