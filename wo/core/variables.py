"""WordOps core variable module"""
import configparser
import os
import sys
from datetime import datetime
from re import match
from socket import getfqdn
from shutil import copy2

from distro import distro, linux_distribution
from sh import git


class WOVar():
    """Intialization of core variables"""

    # WordOps version
    wo_version = "3.22.0"
    # WordOps packages versions
    wo_adminer = "4.8.1"
    wo_phpmyadmin = "5.2.0"
    wo_extplorer = "2.1.15"
    wo_dashboard = "1.3"

    # Get WPCLI path
    wpcli_url = "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"
    wo_wpcli_path = '/usr/local/bin/wp'

    # Current date and time of System
    wo_date = datetime.now().strftime('%d%b%Y-%H-%M-%S')

    # WordOps core variables
    # linux distribution
    if sys.version_info <= (3, 5):
        wo_distro = linux_distribution(
            full_distribution_name=False)[0].lower()
        wo_platform_version = linux_distribution(
            full_distribution_name=False)[1].lower()
        # distro codename (bionic, xenial, stretch ...)
        wo_platform_codename = linux_distribution(
            full_distribution_name=False)[2].lower()
    else:
        wo_distro = distro.id()
        wo_platform_version = distro.version()
        # distro codename (bionic, xenial, stretch ...)
        wo_platform_codename = distro.codename()

    # Get timezone of system
    if os.path.isfile('/etc/timezone'):
        with open("/etc/timezone", mode='r', encoding='utf-8') as tzfile:
            wo_timezone = tzfile.read().replace('\n', '')
            if wo_timezone == "Etc/UTC":
                wo_timezone = "UTC"
    else:
        wo_timezone = "Europe/Amsterdam"

    # Get FQDN of system
    wo_fqdn = getfqdn()

    # WordOps default webroot path
    wo_webroot = '/var/www/'

    # WordOps default renewal  SSL certificates path
    wo_ssl_archive = '/etc/letsencrypt/renewal'

    # WordOps default live SSL certificates path
    wo_ssl_live = '/etc/letsencrypt/live'

    # PHP user
    wo_php_user = 'www-data'

    # WordOps git configuration management
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~") + '/.gitconfig')
    try:
        wo_user = config['user']['name']
        wo_email = config['user']['email']
    except Exception:
        print("WordOps (wo) require an username & and an email "
              "address to configure Git (used to save server configurations)")
        print("Your informations will ONLY be stored locally")

        wo_user = input("Enter your name: ")
        while wo_user == "":
            print("Unfortunately, this can't be left blank")
            wo_user = input("Enter your name: ")

        wo_email = input("Enter your email: ")

        while not match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$",
                        wo_email):
            print("Whoops, seems like you made a typo - "
                  "the e-mail address is invalid...")
            wo_email = input("Enter your email: ")

        git.config("--global", "user.name", "{0}".format(wo_user))
        git.config("--global", "user.email", "{0}".format(wo_email))

    if not os.path.isfile('/root/.gitconfig'):
        copy2(os.path.expanduser("~") + '/.gitconfig', '/root/.gitconfig')

    # MySQL hostname
    wo_mysql_host = ""
    config = configparser.RawConfigParser()
    if os.path.exists('/etc/mysql/conf.d/my.cnf'):
        cnfpath = "/etc/mysql/conf.d/my.cnf"
    else:
        cnfpath = os.path.expanduser("~") + "/.my.cnf"
    if [cnfpath] == config.read(cnfpath):
        try:
            wo_mysql_host = config.get('client', 'host')
        except configparser.NoOptionError:
            wo_mysql_host = "localhost"
    else:
        wo_mysql_host = "localhost"

    # WordOps stack installation variables
    # Nginx repo and packages
    if wo_distro == 'ubuntu':
        wo_nginx_repo = "ppa:wordops/nginx-wo"

    else:
        if wo_distro == 'debian':
            if wo_platform_codename == 'buster':
                wo_deb_repo = "Debian_10"
            elif wo_platform_codename == 'bullseye':
                wo_deb_repo = "Debian_11"
            elif wo_platform_codename == 'bookworm':
                wo_deb_repo = "Debian_12"
        elif wo_distro == 'raspbian':
            if wo_platform_codename == 'buster':
                wo_deb_repo = "Raspbian_10"
            elif wo_platform_codename == 'bullseye':
                wo_deb_repo = "Raspbian_11"
            elif wo_platform_codename == 'bookworm':
                wo_deb_repo = "Raspbian_12"
        # debian/raspbian nginx repository
        wo_nginx_repo = ("deb [signed-by=/usr/share/keyrings/wordops-archive-keyring.gpg] "
                         "http://download.opensuse.org"
                         f"/repositories/home:/virtubox:/WordOps/{wo_deb_repo}/ /")
        wo_nginx_key = (f"https://download.opensuse.org/repositories/home:virtubox:WordOps/{wo_deb_repo}/Release.key")

    wo_nginx = ["nginx-custom", "nginx-wo"]
    wo_nginx_key = 'FB898660'

    wo_php_versions = {
        'php74': '7.4',
        'php80': '8.0',
        'php81': '8.1',
        'php82': '8.2',
        'php83': '8.3',
        'php84': '8.4',
    }

    def generate_php_modules(version_prefix, version_number):
        wo_module = ["bcmath", "cli", "common", "curl", "fpm", "gd", "igbinary",
                     "imagick", "imap", "intl", "mbstring", "memcached", "msgpack",
                     "mysql", "opcache", "readline", "redis", "soap", "xdebug",
                     "xml", "zip"]
        php_modules = ["php{0}-{1}".format(version_number, module) for module in wo_module]

        if version_prefix == 'php74':
            php_modules.extend(["php{0}-geoip".format(version_number),
                                "php{0}-json".format(version_number)])

        return php_modules

    wo_php74 = generate_php_modules('php74', '7.4')
    wo_php80 = generate_php_modules('php80', '8.0')
    wo_php81 = generate_php_modules('php81', '8.1')
    wo_php82 = generate_php_modules('php82', '8.2')
    wo_php83 = generate_php_modules('php83', '8.3')
    wo_php84 = generate_php_modules('php84', '8.4')

    wo_php_extra = ["graphviz"]

    wo_mysql = [
        "mariadb-server", "percona-toolkit",
        "mariadb-common", "python3-mysqldb"]
    if wo_distro == 'raspbian':
        mariadb_ver = '10.3'
    else:
        mariadb_ver = '11.4'
        wo_mysql = wo_mysql + ["mariadb-backup"]

    wo_mysql_client = ["mariadb-client", "python3-mysqldb"]

    wo_fail2ban = ["fail2ban"]
    wo_clamav = ["clamav", "clamav-freshclam"]

    # APT repositories
    wo_mysql_repo = ("deb [signed-by=/etc/apt/keyrings/mariadb-keyring.pgp] "
                     "http://deb.mariadb.org/"
                     f"{mariadb_ver}/{wo_distro} {wo_platform_codename} main")
    mariadb_repo_key = "https://mariadb.org/mariadb_release_signing_key.pgp"
    if wo_distro == 'ubuntu':
        wo_php_repo = "ppa:ondrej/php"
        wo_goaccess_repo = ("ppa:alex-p/goaccess")

    else:
        wo_php_repo = (
            "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] "
            f"https://packages.sury.org/php/ {wo_platform_codename} main")
        wo_php_key = '95BD4743'
    wo_redis_key_url = "https://packages.redis.io/gpg"
    wo_redis_repo = (
        "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] "
        f"https://packages.redis.io/deb {wo_platform_codename} main")

    wo_redis = ['redis-server']

    netdata_script_url = "https://get.netdata.cloud/kickstart.sh"

    # Repo path
    wo_repo_file = "wo-repo.list"
    wo_repo_file_path = ("/etc/apt/sources.list.d/" + wo_repo_file)

    # Application dabase file path
    basedir = os.path.abspath(os.path.dirname('/var/lib/wo/'))
    wo_db_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

    def __init__(self):
        pass
