from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseClean(test.WOTestCase):

    def test_wo_cli_clean(self):
        with WOTestApp(argv=['clean']) as app:
            app.run()

    def test_wo_cli_clean_fastcgi(self):
        with WOTestApp(argv=['clean', '--fastcgi']) as app:
            app.run()

    def test_wo_cli_clean_all(self):
        with WOTestApp(argv=['clean', '--all']) as app:
            app.run()

    def test_wo_cli_clean_opcache(self):
        with WOTestApp(argv=['clean', '--opcache']) as app:
            app.run()

    def test_wo_cli_clean_redis(self):
        with WOTestApp(argv=['clean', '--redis']) as app:
            app.run()
