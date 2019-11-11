from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseDebug(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_debug_stop(self):
        with WOTestApp(argv=['debug', '--stop']) as app:
            app.run()

    def test_wo_cli_debug_start(self):
        with WOTestApp(argv=['debug', '--start']) as app:
            app.run()

    def test_wo_cli_debug_php(self):
        with WOTestApp(argv=['debug', '--php']) as app:
            app.run()

    def test_wo_cli_debug_nginx(self):
        with WOTestApp(argv=['debug', '--nginx']) as app:
            app.run()

    def test_wo_cli_debug_rewrite(self):
        with WOTestApp(argv=['debug', '--rewrite']) as app:
            app.run()

    def test_wo_cli_debug_fpm(self):
        with WOTestApp(argv=['debug', '--fpm']) as app:
            app.run()

    def test_wo_cli_debug_mysql(self):
        with WOTestApp(argv=['debug', '--mysql']) as app:
            app.run()

    def test_wo_cli_debug_import_slow_log_interval(self):
        with WOTestApp(argv=['debug', '--mysql',
                                      '--import-slow-log-interval']) as app:
            app.run()

    def test_wo_cli_debug_site_name_mysql(self):
        with WOTestApp(argv=['debug', 'example3.com', '--mysql']) as app:
            app.run()

    def test_wo_cli_debug_site_name_wp(self):
        with WOTestApp(argv=['debug', 'example4.com', '--wp']) as app:
            app.run()

    def test_wo_cli_debug_site_name_nginx(self):
        with WOTestApp(argv=['debug', 'example4.com', '--nginx']) as app:
            app.run()

    def test_wo_cli_debug_site_name_start(self):
        with WOTestApp(argv=['debug', 'example1.com', '--start']) as app:
            app.run()

    def test_wo_cli_debug_site_name_stop(self):
        with WOTestApp(argv=['debug', 'example1.com', '--stop']) as app:
            app.run()

    def test_wo_cli_debug_site_name_rewrite(self):
        with WOTestApp(argv=['debug', 'example1.com', '--rewrite']) as app:
            app.run()
