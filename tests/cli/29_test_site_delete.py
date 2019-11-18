from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteDelete(test.WOTestCase):

    def test_wo_cli_site_detele(self):
        with WOTestApp(argv=['site', 'delete', 'html.com',
                             '--force']) as app:
            app.run()

    def test_wo_cli_site_detele_all(self):
        with WOTestApp(argv=['site', 'delete', 'wp.com',
                             '--all', '--force']) as app:
            app.run()

    def test_wo_cli_site_detele_db(self):
        with WOTestApp(argv=['site', 'delete', 'mysql.com',
                             '--db', '--force']) as app:
            app.run()

    def test_wo_cli_site_detele_files(self):
        with WOTestApp(argv=['site', 'delete', 'php.com',
                             '--files', '--force']) as app:
            app.run()
