"""Conservative Ubuntu PHP APT repository migration."""

import re
import json
import tarfile
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path


ONDREJ_HOSTS = ('ppa.launchpadcontent.net/ondrej/php',
                'ppa.launchpad.net/ondrej/php')
UPDATE_COMMAND = ['apt-get', 'update', '-qq',
                  '-o', 'APT::Update::Error-Mode=any']


class MigrationError(RuntimeError):
    pass


def _ondrej(text):
    return any(host in text for host in ONDREJ_HOSTS)


def _inspect(path):
    """Accept only files dedicated entirely to the Ondrej PHP repository."""
    content = path.read_text(encoding='utf-8')
    if not _ondrej(content):
        return False
    if path.suffix == '.list':
        active = [line.strip() for line in content.splitlines()
                  if line.strip() and not line.lstrip().startswith('#')]
        if not active or any(not line.startswith(('deb ', 'deb-src ')) or
                             not _ondrej(line) for line in active):
            raise MigrationError('Mixed or unsupported APT list: ' + str(path))
    elif path.suffix == '.sources':
        stanzas = [s for s in content.split('\n\n') if s.strip()]
        if len(stanzas) != 1:
            raise MigrationError('Mixed APT sources file: ' + str(path))
        fields = {}
        for line in stanzas[0].splitlines():
            if line and not line[0].isspace() and ':' in line:
                key, value = line.split(':', 1)
                fields[key.lower()] = value.strip()
        if (not _ondrej(fields.get('uris', '')) or
                len(fields.get('uris', '').split()) != 1 or
                fields.get('enabled', 'yes').lower() == 'no'):
            raise MigrationError('Mixed or unsupported APT source: ' + str(path))
    else:
        raise MigrationError('Unsupported source format: ' + str(path))
    return True


def _verify_sury_policy():
    """Verify that Sury PHP packages are available through APT."""
    result = subprocess.run(
        ['apt-cache', 'policy', 'php8.3-fpm'],
        capture_output=True, text=True, check=False,
    )
    return (result.returncode == 0 and
            'Version table:' in result.stdout and
            any('https://packages.sury.org/php' in line and
                line.strip().endswith('Packages')
                for line in result.stdout.splitlines()))

SURY_KEYRING_URL = (
    'https://packages.sury.org/debsuryorg-archive-keyring.deb'
)

SURY_KEY_FINGERPRINT = (
    '15058500A0235D97F5D10063B188E2B695BD4743'
)


def _verify_sury_keyring(path):
    """Verify the expected Sury signing key fingerprint."""
    if not Path(path).is_file():
        return False

    result = subprocess.run(
        ['gpg', '--batch', '--show-keys', '--with-colons', str(path)],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode:
        return False

    fingerprints = [
        line.split(':')[9].upper()
        for line in result.stdout.splitlines()
        if line.startswith('fpr:')
    ]

    return SURY_KEY_FINGERPRINT in fingerprints


def _ensure_sury_keyring(keyring):
    """Install the official Sury keyring if missing or invalid."""
    if _verify_sury_keyring(keyring):
        return

    with tempfile.TemporaryDirectory(prefix='wo-sury-keyring-') as temp:
        package = Path(temp) / 'debsuryorg-archive-keyring.deb'
        extracted = Path(temp) / 'extracted'

        try:
            urllib.request.urlretrieve(SURY_KEYRING_URL, str(package))
        except Exception as exc:
            raise MigrationError(
                'Unable to download Sury PHP keyring'
            ) from exc

        result = subprocess.run(
            ['dpkg-deb', '-x', str(package), str(extracted)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode:
            raise MigrationError(
                'Unable to extract Sury PHP keyring: ' +
                result.stderr.strip()
            )

        candidate = (
            extracted /
            'usr/share/keyrings/deb.sury.org-php.gpg'
        )

        if not _verify_sury_keyring(candidate):
            raise MigrationError(
                'Downloaded Sury PHP keyring failed fingerprint verification'
            )

        result = subprocess.run(
            ['dpkg', '-i', str(package)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode:
            raise MigrationError(
                'Unable to install Sury PHP keyring: ' +
                result.stderr.strip()
            )

        if not _verify_sury_keyring(keyring):
            raise MigrationError(
                'Sury PHP keyring verification failed after installation'
            )

def migrate_php_repository(codename, repo_dir='/etc/apt/sources.list.d',
                           keyring='/usr/share/keyrings/deb.sury.org-php.gpg',
                           backup_root='/var/lib/wo-backup/php-repo',
                           run=None, verify=None):
    """Switch an exclusive Ondrej source to Sury without upgrading packages.

    The caller must verify Ubuntu and root privileges. `run` and `verify`
    are injectable for tests. The operation refuses ambiguous source files.
    """
    if codename not in ('jammy', 'noble'):
        raise MigrationError('Unsupported Ubuntu codename: ' + str(codename))
    directory = Path(repo_dir)
    if not directory.is_dir():
        raise MigrationError('APT source directory is missing')
    expected = ('deb [signed-by=' + str(keyring) + '] '
                'https://packages.sury.org/php/ ' + codename + ' main\n')
    target = directory / 'php.list'
    if target.is_symlink():
        raise MigrationError('Refusing symlinked php.list')
    if target.exists() and target.read_text(encoding='utf-8') != expected:
        raise MigrationError('php.list exists with unexpected content')
    sources = sorted(p for p in directory.iterdir()
                     if p.is_file() and not p.is_symlink() and
                     p.suffix in ('.list', '.sources') and _inspect(p))
    if not sources:
        if target.exists():
            if not verifier_ready(verify):
                raise MigrationError(
                    'Sury repository exists but APT does not expose PHP'
                )
            return {'status': 'already-migrated', 'backup': None}

        raise MigrationError('No Ondrej PHP source found')

    # Ensure the signing key is ready before changing APT sources.
    _ensure_sury_keyring(keyring)

    backup_parent = Path(backup_root)
    backup_parent.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='migration-', dir=str(backup_parent)))
    originals = list(sources)
    if target.exists():
        originals.append(target)
    try:
        for path in originals:
            shutil.copy2(str(path), str(backup / path.name))
    except Exception as exc:
        raise MigrationError('Backup failed; no sources changed: ' +
                             str(backup)) from exc

    runner = run or (lambda cmd: subprocess.run(cmd, check=False).returncode)
    verifier = verify or _verify_sury_policy
    try:
        for path in sources:
            path.unlink()
        target.write_text(expected, encoding='utf-8')
        if runner(UPDATE_COMMAND) != 0:
            raise MigrationError('APT update failed')
        if not verifier():
            raise MigrationError('Sury PHP candidate verification failed')
        return {'status': 'migrated', 'backup': str(backup)}
    except Exception as exc:
        restore_errors = []
        try:
            if target.exists():
                target.unlink()
        except Exception as restore_exc:
            restore_errors.append(str(restore_exc))
        for path in originals:
            try:
                shutil.copy2(str(backup / path.name), str(path))
            except Exception as restore_exc:
                restore_errors.append(str(restore_exc))
        if restore_errors:
            raise MigrationError('Migration failed; FILE RESTORE INCOMPLETE; '
                                 'backup: ' + str(backup) + '; errors: ' +
                                 '; '.join(restore_errors)) from exc
        try:
            rollback_rc = runner(UPDATE_COMMAND)
        except Exception as restore_exc:
            raise MigrationError('Files restored but APT refresh failed; '
                                 'backup: ' + str(backup)) from restore_exc
        if rollback_rc != 0:
            raise MigrationError('Files restored but APT refresh failed; '
                                 'backup: ' + str(backup)) from exc
        raise MigrationError('Migration failed; files restored; backup: ' +
                             str(backup)) from exc


def verifier_ready(verify=None):
    return (verify or _verify_sury_policy)()


def _capture(command):
    result = subprocess.run(command, capture_output=True, text=True,
                            check=False)
    if result.returncode:
        raise MigrationError('Command failed: ' + ' '.join(command) +
                             '\n' + result.stderr.strip())
    return result.stdout


def _installed_php_packages():
    """Read installed packages from dpkg, not APT's available package list."""
    output = _capture(['dpkg-query', '-W',
                       '-f=${binary:Package}\t${db:Status-Abbrev}\t${Version}\n'])
    packages = {}
    for row in output.splitlines():
        fields = row.split('\t')
        if len(fields) != 3:
            continue
        name, status, version = fields
        if (status.startswith('ii') and
                re.fullmatch(r'php[0-9]+\.[0-9]+-[a-z0-9.+-]+', name)):
            packages[name] = version
    return packages


def _sury_versions(name):
    output = _capture(['apt-cache', 'madison', name])
    return [parts[1].strip() for line in output.splitlines()
            if 'https://packages.sury.org/php' in line
            for parts in [line.split('|')]
            if len(parts) >= 3]


def _upstream(version):
    # Compare upstream PHP versions, not Debian package revisions.
    value = version.split(':', 1)[-1]
    return value.split('-', 1)[0]


# Only packages built with the PHP interpreter version should have an
# identical upstream version across repositories. Extensions have their own.
PHP_CORE_SUFFIXES = frozenset((
    'cli', 'common', 'fpm', 'cgi', 'phpdbg', 'dev', 'embed', 'opcache',
))


def _plan_php_packages(installed):
    targets = []
    missing = []
    for name, old in sorted(installed.items()):
        versions = _sury_versions(name)
        if not versions:
            missing.append(name)
            continue
        chosen = versions[0]
        suffix = re.sub(r'^php[0-9]+\.[0-9]+-', '', name)
        if (suffix in PHP_CORE_SUFFIXES and
                _upstream(chosen) != _upstream(old)):
            raise MigrationError('PHP upstream version differs for ' + name +
                                 ': ' + old + ' -> ' + chosen)
        if chosen != old:
            targets.append(name + '=' + chosen)
    if missing:
        raise MigrationError('Missing Sury packages: ' + ', '.join(missing))
    return targets


def _simulate(targets):
    if not targets:
        return {'changed': 0, 'simulation': ''}
    output = _capture(['apt-get', '-s', 'install', '--allow-downgrades',
                       *targets])
    summary = re.search(r'(\d+) upgraded, (\d+) newly installed, '
                        r'(\d+) downgraded, (\d+) to remove', output)
    if not summary:
        raise MigrationError('Unable to parse APT simulation summary')
    upgraded, added, downgraded, removed = map(int, summary.groups())
    expected = dict(item.split('=', 1) for item in targets)
    operations = {}
    for line in output.splitlines():
        if line.startswith(('Remv ', 'Purg ')):
            raise MigrationError('APT simulation removes packages:\n' + output)
        if not line.startswith('Inst '):
            continue
        match = re.match(r'^Inst (\S+)(?: \[[^]]+\])? \(\s*(\S+)', line)
        if not match:
            raise MigrationError('Cannot parse APT install operation: ' + line)
        name, version = match.groups()
        if name in operations:
            raise MigrationError('Duplicate APT operation: ' + name)
        operations[name] = version
    if (added or removed or len(operations) != len(expected) or
            operations != expected or
            upgraded + downgraded != len(expected)):
        raise MigrationError('Unsafe APT transaction; inspect simulation:\n' + output)
    return {'changed': len(targets), 'simulation': output}


def _backup_php_state(backup_root, installed):
    parent = Path(backup_root)
    parent.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='packages-', dir=str(parent)))
    (backup / 'installed-before.json').write_text(
        json.dumps(installed, indent=2, sort_keys=True) + '\n',
        encoding='utf-8')
    config = Path('/etc/php')
    if config.exists():
        with tarfile.open(str(backup / 'etc-php.tar.gz'), 'w:gz') as archive:
            archive.add(str(config), arcname='etc/php', recursive=True)
    return backup


def _verify_php_fpm(installed, backup=None):
    """Check each installed PHP-FPM service, including on repeat runs."""
    versions = sorted({name.split('-')[0][3:] for name in installed
                       if re.fullmatch(r'php[0-9]+\.[0-9]+-fpm', name)})
    for version in versions:
        service = 'php' + version + '-fpm'
        if subprocess.run(['systemctl', 'is-active', '--quiet', service],
                          check=False).returncode:
            raise MigrationError(service + ' is not active; backup: ' +
                                 str(backup))
        if subprocess.run(['php-fpm' + version, '-t'],
                          check=False).returncode:
            raise MigrationError(service + ' configuration invalid; backup: ' +
                                 str(backup))


def synchronize_php_packages(backup_root='/var/lib/wo-backup/php-repo'):
    """Synchronize installed PHP packages without adding or removing packages."""
    if not _verify_sury_policy():
        raise MigrationError('Sury PHP repository is unavailable')
    installed = _installed_php_packages()
    if not installed:
        return {'status': 'no-packages', 'changed': 0, 'backup': None}
    targets = _plan_php_packages(installed)
    if not targets:
        _verify_php_fpm(installed)
        return {'status': 'already-synchronized', 'changed': 0,
                'backup': None}
    plan = _simulate(targets)
    backup = _backup_php_state(backup_root, installed)
    (backup / 'apt-simulation.txt').write_text(plan['simulation'], encoding='utf-8')
    (backup / 'targets.txt').write_text('\n'.join(targets) + '\n',
                                        encoding='utf-8')
    print(plan['simulation'], flush=True)
    print('PHP configuration backup: ' + str(backup), flush=True)
    print('Applying ' + str(len(targets)) + ' PHP package changes...', flush=True)
    # Package installation may partially complete. Never claim automatic rollback.
    result = subprocess.run(['apt-get', '-y', 'install', '--allow-downgrades',
                             *targets], check=False)
    if result.returncode:
        raise MigrationError('PHP package transaction FAILED or partially applied. '
                             'Manual recovery required. Backup: ' + str(backup))
    after = _installed_php_packages()
    expected = dict(target.split('=', 1) for target in targets)
    mismatches = [name for name, version in expected.items()
                  if after.get(name) != version]
    if mismatches or set(after) != set(installed):
        raise MigrationError('PHP package verification FAILED: ' +
                             ', '.join(mismatches) + '; backup: ' + str(backup))
    _verify_php_fpm(after, backup)
    return {'status': 'synchronized', 'changed': len(targets),
            'backup': str(backup)}


def migrate_php_stack(codename):
    """One CLI workflow: switch repository, then synchronize packages."""
    repository = migrate_php_repository(codename)
    try:
        packages = synchronize_php_packages()
    except MigrationError as exc:
        raise MigrationError('Repository status: ' + repository['status'] +
                             '; package synchronization failed: ' + str(exc)) from exc
    return {'repository': repository, 'packages': packages}
