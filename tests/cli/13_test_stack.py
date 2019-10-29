from wo.utils import test
from wo.cli.main import get_test_app


class CliTestCaseStack(test.WOTestCase):

    def test_wo_cli(self):
        argv = []
        with self.make_app(argv=argv) as app:
            app.run()
            self.eq(app.pargs.stack)

    def test_wo_cli_stacks_install(self):
        wo_stacks = ['nginx', 'php', 'php73', 'mysql', 'redis', 'fail2ban',
                     'clamav', 'proftpd', 'netdata',
                     'phpmyadmin',  'composer',  'dashboard', 'extplorer',
                     'adminer', 'redis', 'ufw', 'ngxblocker', 'cheat']
        for wo_stack in wo_stacks:
            argv = ['stack', 'install', '--{0}'.format(wo_stack)]
            with self.make_app(argv=argv) as app:
                app.run()
                self.eq(app.pargs.stack.install.wo_stack)