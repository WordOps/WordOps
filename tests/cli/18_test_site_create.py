from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteCreate(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_site_create_html(self):
        with WOTestApp(argv=['site', 'create', 'example1.com',
                             '--html']) as app:
            app.config.set('wo', '', True)
            app.run()

    def test_wo_cli_site_create_php(self):
        with WOTestApp(argv=['site', 'create', 'example2.com',
                             '--php']) as app:
            app.run()

    def test_wo_cli_site_create_mysql(self):
        with WOTestApp(argv=['site', 'create', 'example3.com',
                             '--mysql']) as app:
            app.run()

    def test_wo_cli_site_create_wp(self):
        with WOTestApp(argv=['site', 'create', 'example4.com',
                             '--wp']) as app:
            app.run()

    def test_wo_cli_site_create_wpsubdir(self):
        with WOTestApp(argv=['site', 'create', 'example5.com',
                             '--wpsubdir']) as app:
            app.run()

    def test_wo_cli_site_create_wpsubdomain(self):
        with WOTestApp(argv=['site', 'create', 'example6.com',
                             '--wpsubdomain']) as app:
            app.run()

    def test_wo_cli_site_create_wpfc(self):
        with WOTestApp(argv=['site', 'create', 'example8.com',
                             '--wpfc']) as app:
            app.run()

    def test_wo_cli_site_create_wpsc(self):
        with WOTestApp(argv=['site', 'create', 'example9.com',
                             '--wpsc']) as app:
            app.run()
