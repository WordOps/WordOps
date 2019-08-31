"""WordOps core variable module"""
import distro
import socket
import configparser
import os
import datetime


class WOVariables():
    """Intialization of core variables"""

    # WordOps version
    wo_version = "3.9.8.7"
    # WordOps packages versions
    wo_wp_cli = "2.2.0"
    wo_adminer = "4.7.2"
    wo_phpmyadmin = "4.9.0.1"
    wo_extplorer = "2.1.13"
    wo_dashboard = "1.1"

    # Get WPCLI path
    wo_wpcli_path = '/usr/local/bin/wp'

    # Current date and time of System
    wo_date = datetime.datetime.now().strftime('%d%b%Y-%H-%M-%S')

    # WordOps core variables
    wo_distro = distro.linux_distribution(
        full_distribution_name=False)[0].lower()
    wo_platform_version = distro.linux_distribution(
        full_distribution_name=False)[1].lower()
    wo_platform_codename = distro.linux_distribution(
        full_distribution_name=False)[2].lower()

    # Get timezone of system
    if os.path.isfile('/etc/timezone'):
        with open("/etc/timezone", "r") as tzfile:
            wo_timezone = tzfile.read().replace('\n', '')
            if wo_timezone == "Etc/UTC":
                wo_timezone = "UTC"
    else:
        wo_timezone = "Europe/Amsterdam"

    # Get FQDN of system
    wo_fqdn = socket.getfqdn()

    # WordOps default webroot path
    wo_webroot = '/var/www/'

    # WordOps default renewal  SSL certificates path
    wo_ssl_archive = '/etc/letsencrypt/renewal'

    # WordOps default live SSL certificates path
    wo_ssl_live = '/etc/letsencrypt/live'

    # PHP user
    wo_php_user = 'www-data'

    # Get git user name and EMail
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~")+'/.gitconfig')
    try:
        wo_user = config['user']['name']
        wo_email = config['user']['email']
    except Exception:
        wo_user = input("Enter your name: ")
        wo_email = input("Enter your email: ")
        os.system("/usr/bin/git config --global user.name {0}".format(wo_user))
        os.system(
            "/usr/bin/git config --global user.email {0}".format(wo_email))

    # MySQL hostname
    wo_mysql_host = ""
    config = configparser.RawConfigParser()
    if os.path.exists('/etc/mysql/conf.d/my.cnf'):
        cnfpath = "/etc/mysql/conf.d/my.cnf"
    else:
        cnfpath = os.path.expanduser("~")+"/.my.cnf"
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
            if wo_platform_codename == 'jessie':
                wo_deb_repo = "Debian_8.0"
            elif wo_platform_codename == 'stretch':
                wo_deb_repo = "Debian_9.0"
            elif wo_platform_codename == 'buster':
                wo_deb_repo = "Debian_10"
        elif wo_distro == 'raspbian':
            if wo_platform_codename == 'stretch':
                wo_deb_repo = "Raspbian_9.0"
            elif wo_platform_codename == 'buster':
                wo_deb_repo = "Raspbian_10"
        # debian/raspbian nginx repository
        wo_nginx_repo = ("deb http://download.opensuse.org"
                         "/repositories/home:"
                         "/virtubox:/WordOps/{0}/ /"
                         .format(wo_deb_repo))

    wo_nginx = ["nginx-custom", "nginx-wo"]
    wo_nginx_key = '188C9FB063F0247A'

    # PHP repo and packages
    if wo_distro == 'ubuntu':
        wo_php_repo = "ppa:ondrej/php"
    else:
        wo_php_repo = (
            "deb https://packages.sury.org/php/ {codename} main"
            .format(codename=wo_platform_codename))
        wo_php_key = 'AC0E47584A7A714D'

    wo_php = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
              "php7.2-readline", "php7.2-common", "php7.2-recode",
              "php7.2-cli", "php7.2-mbstring", "php7.2-intl",
              "php7.2-bcmath", "php7.2-mysql", "php7.2-opcache",
              "php7.2-zip", "php7.2-xml", "php7.2-soap"]
    wo_php73 = ["php7.3-fpm", "php7.3-curl", "php7.3-gd", "php7.3-imap",
                "php7.3-readline", "php7.3-common", "php7.3-recode",
                "php7.3-cli", "php7.3-mbstring", "php7.3-intl",
                "php7.3-bcmath", "php7.3-mysql", "php7.3-opcache",
                "php7.3-zip", "php7.3-xml", "php7.3-soap"]
    wo_php_extra = ["php-memcached", "php-imagick",
                    "graphviz", "php-xdebug", "php-msgpack", "php-redis"]

    # MySQL repo and packages
    if wo_distro == 'ubuntu':
        wo_mysql_repo = ("deb [arch=amd64,ppc64el] "
                         "http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.3/ubuntu {codename} main"
                         .format(codename=wo_platform_codename))
    else:
        wo_mysql_repo = ("deb [arch=amd64,ppc64el] "
                         "http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.3/debian {codename} main"
                         .format(codename=wo_platform_codename))

    if wo_distro == 'raspbian':
        wo_mysql = ["mariadb-server", "percona-toolkit",
                    "python3-mysqldb"]
    elif wo_platform_codename == 'jessie':
        wo_mysql = ["mariadb-server", "percona-toolkit",
                    "python3-mysql.connector"]
    else:
        wo_mysql = ["mariadb-server", "percona-toolkit",
                    "python3-mysqldb", "mariadb-backup"]

    if wo_platform_codename == 'jessie':
        wo_mysql_client = ["mariadb-client", "python3-mysqldb"]
    else:
        wo_mysql_client = ["mariadb-client", "python3-mysql.connector"]

    wo_fail2ban = ["fail2ban"]
    wo_clamav = ["clamav", "clamav-freshclam"]

    # Redis repo details
    if wo_distro == 'ubuntu':
        wo_redis_repo = ("ppa:chris-lea/redis-server")

    else:
        wo_redis_repo = ("deb https://packages.sury.org/php/ {codename} all"
                         .format(codename=wo_platform_codename))

    wo_redis = ['redis-server', 'php-redis']

    # Repo path
    wo_repo_file = "wo-repo.list"
    wo_repo_file_path = ("/etc/apt/sources.list.d/" + wo_repo_file)

    # Application dabase file path
    basedir = os.path.abspath(os.path.dirname('/var/lib/wo/'))
    wo_db_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

    def __init__(self):
        pass
