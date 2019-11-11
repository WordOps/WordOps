from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteUpdate(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_site_update_html(self):
        with WOTestApp(argv=['site', 'update', 'example2.com',
                             '--html']) as app:
            app.run()

    def test_wo_cli_site_update_php(self):
        with WOTestApp(argv=['site', 'update', 'example1.com',
                             '--php']) as app:
            app.run()

    def test_wo_cli_site_update_mysql(self):
        with WOTestApp(argv=['site', 'update', 'example1.com',
                             '--html']) as app:
            app.run()

    def test_wo_cli_site_update_wp(self):
        with WOTestApp(argv=['site', 'update', 'example5.com',
                             '--wp']) as app:
            app.run()

    def test_wo_cli_site_update_wpsubdir(self):
        with WOTestApp(argv=['site', 'update', 'example4.com',
                             '--wpsubdir']) as app:
            app.run()

    def test_wo_cli_site_update_wpsubdomain(self):
        with WOTestApp(argv=['site', 'update', 'example7.com',
                             '--wpsubdomain']) as app:
            app.run()

    def test_wo_cli_site_update_wpfc(self):
        with WOTestApp(argv=['site', 'update', 'example9.com',
                             '--wpfc']) as app:
            app.run()

    def test_wo_cli_site_update_wpsc(self):
        with WOTestApp(argv=['site', 'update', 'example6.com',
                             '--wpsc']) as app:
            app.run()
