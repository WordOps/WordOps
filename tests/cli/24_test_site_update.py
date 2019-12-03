from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteUpdate(test.WOTestCase):

    def test_wo_cli_site_update_html(self):
        with WOTestApp(argv=['site', 'update', 'php.com',
                             '--html']) as app:
            app.run()

    def test_wo_cli_site_update_php(self):
        with WOTestApp(argv=['site', 'update', 'html.com',
                             '--php']) as app:
            app.run()

    def test_wo_cli_site_update_mysql(self):
        with WOTestApp(argv=['site', 'update', 'mysql.com',
                             '--html']) as app:
            app.run()

    def test_wo_cli_site_update_wp(self):
        with WOTestApp(argv=['site', 'update', 'mysql.com',
                             '--wp']) as app:
            app.run()

    def test_wo_cli_site_update_wpsubdir(self):
        with WOTestApp(argv=['site', 'update', 'wp.com',
                             '--wpsubdir']) as app:
            app.run()

    def test_wo_cli_site_update_wpsubdomain(self):
        with WOTestApp(argv=['site', 'update', 'wpsubdir.com',
                             '--wpsubdomain']) as app:
            app.run()

    def test_wo_cli_site_update_wpfc(self):
        with WOTestApp(argv=['site', 'update', 'wpsc.com',
                             '--wpfc']) as app:
            app.run()

    def test_wo_cli_site_update_wpsc(self):
        with WOTestApp(argv=['site', 'update', 'wpfc.com',
                             '--wpsc']) as app:
            app.run()
