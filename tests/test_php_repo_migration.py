
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from wo.core.php_repo_migration import (
    MigrationError,
    _ensure_sury_keyring,
    _verify_sury_keyring,
    _verify_sury_policy,
    migrate_php_repository,
)


class PhpMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.root = Path(self.tmp.name)
        self.sources = self.root / 'sources'
        self.sources.mkdir()

        self.keyring = self.root / 'sury.gpg'
        self.keyring.write_text('test')

        self.backups = self.root / 'backups'
        self.ondrej = self.sources / 'ondrej-ubuntu-php-noble.sources'

        self.original = (
            'Types: deb\n'
            'URIs: https://ppa.launchpadcontent.net/ondrej/php/ubuntu/\n'
            'Suites: noble\n'
            'Components: main\n'
            'Signed-By: -----BEGIN PGP PUBLIC KEY BLOCK-----\n'
            ' .\n'
            ' ABC\n'
            ' -----END PGP PUBLIC KEY BLOCK-----\n'
        )

        self.ondrej.write_text(self.original)

    def migrate(self, run=None, verify=None):
        with patch(
            'wo.core.php_repo_migration._ensure_sury_keyring'
        ):
            return migrate_php_repository(
                'noble',
                self.sources,
                self.keyring,
                self.backups,
                run=run if run is not None else lambda cmd: 0,
                verify=verify if verify is not None else lambda: True,
            )

    def test_success(self):
        commands = []

        result = self.migrate(
            lambda cmd: commands.append(cmd) or 0
        )

        self.assertEqual(result['status'], 'migrated')
        self.assertFalse(self.ondrej.exists())
        self.assertIn(
            'packages.sury.org/php/',
            (self.sources / 'php.list').read_text(),
        )
        self.assertEqual(len(commands), 1)
        self.assertEqual(
            (Path(result['backup']) / self.ondrej.name).read_text(),
            self.original,
        )

    def test_rollback(self):
        commands = []

        def fail_first(cmd):
            commands.append(cmd)
            return 1 if len(commands) == 1 else 0

        with self.assertRaises(MigrationError):
            self.migrate(fail_first)

        self.assertEqual(self.ondrej.read_text(), self.original)
        self.assertFalse((self.sources / 'php.list').exists())
        self.assertEqual(len(commands), 2)

    def test_verification_failure_rolls_back(self):
        commands = []

        with self.assertRaisesRegex(MigrationError, 'files restored'):
            self.migrate(
                lambda cmd: commands.append(cmd) or 0,
                verify=lambda: False,
            )

        self.assertEqual(len(commands), 2)
        self.assertEqual(self.ondrej.read_text(), self.original)
        self.assertFalse((self.sources / 'php.list').exists())

    def test_rollback_refresh_failure_reported(self):
        with self.assertRaisesRegex(
            MigrationError,
            'APT refresh failed',
        ):
            self.migrate(lambda cmd: 1)

        self.assertEqual(self.ondrej.read_text(), self.original)

    def test_reject_mixed_sources(self):
        self.ondrej.write_text(
            self.original +
            '\nTypes: deb\n'
            'URIs: https://example.org/other\n'
            'Suites: noble\n'
        )

        with self.assertRaises(MigrationError):
            self.migrate()

        self.assertFalse((self.sources / 'php.list').exists())

    def test_reject_existing_php_list(self):
        (self.sources / 'php.list').write_text(
            'deb https://example.org noble main\n'
        )

        with self.assertRaises(MigrationError):
            self.migrate()

        self.assertTrue(self.ondrej.exists())

    def test_existing_php_list_restored(self):
        target = self.sources / 'php.list'

        original = (
            'deb [signed-by=' + str(self.keyring) + '] '
            'https://packages.sury.org/php/ noble main\n'
        )

        target.write_text(original)

        with self.assertRaises(MigrationError):
            self.migrate(lambda cmd: 1)

        self.assertEqual(target.read_text(), original)
        self.assertEqual(self.ondrej.read_text(), self.original)

    def test_reject_focal(self):
        with self.assertRaises(MigrationError):
            migrate_php_repository(
                'focal',
                self.sources,
                self.keyring,
                self.backups,
                run=lambda cmd: 0,
            )

    def test_idempotent(self):
        self.migrate()
        self.assertEqual(
            self.migrate()['status'],
            'already-migrated',
        )

    def test_sury_candidate_installed(self):
        policy = """php8.3-fpm:
  Installed: 8.3.36-1
  Candidate: 8.3.36-1
  Version table:
 *** 8.3.36-1 500
        500 https://packages.sury.org/php noble/main amd64 Packages
        100 /var/lib/dpkg/status
"""

        with patch(
            'wo.core.php_repo_migration.subprocess.run',
            return_value=CompletedProcess([], 0, policy, ''),
        ):
            self.assertTrue(_verify_sury_policy())

    def test_ondrej_candidate_rejected(self):
        policy = """php8.3-fpm:
  Installed: 8.3.36-1
  Candidate: 8.3.36-1
  Version table:
 *** 8.3.36-1 500
        500 https://ppa.launchpadcontent.net/ondrej/php/ubuntu noble/main amd64 Packages
        100 /var/lib/dpkg/status
"""

        with patch(
            'wo.core.php_repo_migration.subprocess.run',
            return_value=CompletedProcess([], 0, policy, ''),
        ):
            self.assertFalse(_verify_sury_policy())

    def test_sury_available_with_different_installed_candidate(self):
        policy = """php8.3-fpm:
    Installed: 8.3.36-1+ubuntu24.04.1+deb.sury.org+1
    Candidate: 8.3.36-1+ubuntu24.04.1+deb.sury.org+1
    Version table:
    *** 8.3.36-1+ubuntu24.04.1+deb.sury.org+1 100
            100 /var/lib/dpkg/status
        8.3.36-1+0~20261021.88+ubuntu24.04~1.gbp250f7c 500
            500 https://packages.sury.org/php noble/main amd64 Packages
    """

        with patch(
            'wo.core.php_repo_migration.subprocess.run',
            return_value=CompletedProcess([], 0, policy, ''),
        ):
            self.assertTrue(_verify_sury_policy())


class SuryKeyringTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.root = Path(self.tmp.name)
        self.keyring = self.root / 'sury.gpg'

    def test_valid_keyring(self):
        self.keyring.write_bytes(b'fake-keyring')

        fingerprint = (
            '15058500A0235D97F5D10063B188E2B695BD4743'
        )

        output = (
            'pub:-:4096:1:12345678:0:0::::::\n'
            'fpr:::::::::' + fingerprint + ':\n'
        )

        with patch(
            'wo.core.php_repo_migration.subprocess.run',
            return_value=CompletedProcess([], 0, output, ''),
        ):
            self.assertTrue(_verify_sury_keyring(self.keyring))

    def test_missing_keyring(self):
        self.assertFalse(_verify_sury_keyring(self.keyring))

    def test_invalid_fingerprint(self):
        self.keyring.write_bytes(b'fake-keyring')

        output = (
            'pub:-:4096:1:12345678:0:0::::::\n'
            'fpr:::::::::AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:\n'
        )

        with patch(
            'wo.core.php_repo_migration.subprocess.run',
            return_value=CompletedProcess([], 0, output, ''),
        ):
            self.assertFalse(_verify_sury_keyring(self.keyring))

    def test_existing_valid_key_skips_download(self):
        with patch(
            'wo.core.php_repo_migration._verify_sury_keyring',
            return_value=True,
        ), patch(
            'wo.core.php_repo_migration.urllib.request.urlretrieve'
        ) as download:
            _ensure_sury_keyring(self.keyring)

        download.assert_not_called()

    def test_download_failure(self):
        with patch(
            'wo.core.php_repo_migration._verify_sury_keyring',
            return_value=False,
        ), patch(
            'wo.core.php_repo_migration.urllib.request.urlretrieve',
            side_effect=OSError('Network unavailable'),
        ):
            with self.assertRaisesRegex(
                MigrationError,
                'Unable to download',
            ):
                _ensure_sury_keyring(self.keyring)

    def test_invalid_downloaded_key_rejected(self):
        def fake_run(command, **kwargs):
            if command[:2] == ['dpkg-deb', '-x']:
                return CompletedProcess(command, 0, '', '')
            return CompletedProcess(command, 0, '', '')

        with patch(
            'wo.core.php_repo_migration._verify_sury_keyring',
            return_value=False,
        ), patch(
            'wo.core.php_repo_migration.urllib.request.urlretrieve'
        ), patch(
            'wo.core.php_repo_migration.subprocess.run',
            side_effect=fake_run,
        ):
            with self.assertRaisesRegex(
                MigrationError,
                'fingerprint verification',
            ):
                _ensure_sury_keyring(self.keyring)


if __name__ == '__main__':
    unittest.main()
