from wo.utils import test
from wo.cli.main import WOTestApp


class CliTestCaseSiteDelete(test.WOTestCase):

    def test_wo_cli(self):
        with WOTestApp as app:
            app.run()

    def test_wo_cli_site_detele(self):
        with WOTestApp(argv=['site', 'delete', 'example1.com',
                             '--no-prompt']) as app:
            app.run()

    def test_wo_cli_site_detele_all(self):
        with WOTestApp(argv=['site', 'delete', 'example2.com',
                             '--all', '--no-prompt']) as app:
            app.run()

    def test_wo_cli_site_detele_db(self):
        with WOTestApp(argv=['site', 'delete', 'example3.com',
                             '--db', '--no-prompt']) as app:
            app.run()

    def test_wo_cli_site_detele_files(self):
        with WOTestApp(argv=['site', 'delete', 'example4.com',
                             '--files', '--no-prompt']) as app:
            app.run()
