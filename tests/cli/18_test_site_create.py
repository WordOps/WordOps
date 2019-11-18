from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteCreate(test.WOTestCase):

    def test_wo_cli_site_create_html(self):
        with WOTestApp(argv=['site', 'create', 'html.com',
                             '--html']) as app:
            app.config.set('wo', '', True)
            app.run()

    def test_wo_cli_site_create_php(self):
        with WOTestApp(argv=['site', 'create', 'php.com',
                             '--php']) as app:
            app.run()

    def test_wo_cli_site_create_mysql(self):
        with WOTestApp(argv=['site', 'create', 'mysql.com',
                             '--mysql']) as app:
            app.run()

    def test_wo_cli_site_create_wp(self):
        with WOTestApp(argv=['site', 'create', 'wp.com',
                             '--wp']) as app:
            app.run()

    def test_wo_cli_site_create_wpsubdir(self):
        with WOTestApp(argv=['site', 'create', 'wpsubdir.com',
                             '--wpsubdir']) as app:
            app.run()

    def test_wo_cli_site_create_wpsubdomain(self):
        with WOTestApp(argv=['site', 'create', 'wpsubdomain.com',
                             '--wpsubdomain']) as app:
            app.run()

    def test_wo_cli_site_create_wpfc(self):
        with WOTestApp(argv=['site', 'create', 'wpfc.com',
                             '--wpfc']) as app:
            app.run()

    def test_wo_cli_site_create_wpsc(self):
        with WOTestApp(argv=['site', 'create', 'wpsc.com',
                             '--wpsc']) as app:
            app.run()

    def test_wo_cli_site_create_wpce(self):
        with WOTestApp(argv=['site', 'create', 'wpce.com',
                             '--wpce']) as app:
            app.run()

    def test_wo_cli_site_create_wprocket(self):
        with WOTestApp(argv=['site', 'create', 'wprocket.com',
                             '--wprocket']) as app:
            app.run()
