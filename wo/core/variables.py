"""WordOps core variable module"""
import platform
import socket
import configparser
import os
import sys
import psutil
import datetime


class WOVariables():
    """Intialization of core variables"""

    # WordOps version
    wo_version = "3.9.5"
    # WordOps packages versions
    wo_wp_cli = "2.1.0"
    wo_adminer = "4.7.1"

    # Get WPCLI path
    wo_wpcli_path = os.popen('command -v wp | tr "\n" " "').read()
    if wo_wpcli_path == '':
        wo_wpcli_path = '/usr/local/bin/wp '

    # Current date and time of System
    wo_date = datetime.datetime.now().strftime('%d%b%Y%H%M%S')

    # WordOps core variables
    wo_platform_distro = platform.linux_distribution()[0].lower()
    wo_platform_version = platform.linux_distribution()[1]
    wo_platform_codename = os.popen("lsb_release -sc | tr -d \'\\n\'").read()

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

    # PHP user
    wo_php_user = 'www-data'

    # Get git user name and EMail
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~")+'/.gitconfig')
    try:
        wo_user = config['user']['name']
        wo_email = config['user']['email']
    except Exception as e:
        wo_user = input("Enter your name: ")
        wo_email = input("Enter your email: ")
        os.system("git config --global user.name {0}".format(wo_user))
        os.system("git config --global user.email {0}".format(wo_email))

    # Get System RAM and SWAP details
    wo_ram = psutil.virtual_memory().total / (1024 * 1024)
    wo_swap = psutil.swap_memory().total / (1024 * 1024)

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
        except configparser.NoOptionError as e:
            wo_mysql_host = "localhost"
    else:
        wo_mysql_host = "localhost"

    # WordOps stack installation variables
    # Nginx repo and packages
    if wo_platform_codename == 'trusty':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_14.04/ /")
    elif wo_platform_codename == 'xenial':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_16.04/ /")
    elif wo_platform_codename == 'bionic':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_18.04/ /")
    elif wo_platform_codename == 'jessie':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/Debian_8.0/ /")
    elif wo_platform_codename == 'stretch':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/Debian_8.0/ /")

    wo_nginx = ["nginx-custom", "nginx-ee"]
    wo_nginx_key = '3050AC3CD2AE6F03'

    # PHP repo and packages
    if wo_platform_distro == 'ubuntu':
        if (wo_platform_codename == 'trusty' or wo_platform_codename == 'xenial' or wo_platform_codename == 'bionic'):
            wo_php_repo = "ppa:ondrej/php"
            wo_php = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                      "php7.2-readline", "php7.2-common", "php7.2-recode",
                      "php7.2-cli", "php7.2-mbstring",
                      "php7.2-bcmath", "php7.2-mysql", "php7.2-opcache", "php7.2-zip", "php7.2-xml", "php7.2-soap"]
            wo_php73 = ["php7.3-fpm", "php7.3-curl", "php7.3-gd", "php7.3-imap",
                        "php7.3-readline", "php7.3-common", "php7.3-recode",
                        "php7.3-cli", "php7.3-mbstring",
                        "php7.3-bcmath", "php7.3-mysql", "php7.3-opcache", "php7.3-zip", "php7.3-xml", "php7.3-soap"]
            wo_php_extra = ["php-memcached", "php-imagick",
                            "graphviz", "php-xdebug", "php-msgpack", "php-redis"]
    elif wo_platform_distro == 'debian':
        wo_php_repo = (
            "deb https://packages.sury.org/php/ {codename} main".format(codename=wo_platform_codename))
        wo_php = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                  "php7.2-common", "php7.2-readline", "php-redis",
                  "php7.2-mysql", "php7.2-cli", "php-imagick",
                  "php7.2-mbstring", "php7.2-recode", "php7.2-bcmath", "php7.2-opcache", "php7.2-zip", "php7.2-xml",
                  "php7.2-soap", "php-msgpack",
                  "graphviz", "php-pear", "php-xdebug"]
        wo_php73 = ["php7.3-fpm", "php7.3-curl", "php7.3-gd", "php7.3-imap",
                    "php7.3-common", "php7.3-readline", "php-redis",
                    "php7.3-mysql", "php7.3-cli", "php-imagick",
                    "php7.3-mbstring", "php7.3-recode", "php7.3-bcmath", "php7.3-opcache", "php7.3-zip", "php7.3-xml",
                    "php7.3-soap", "php-msgpack",
                    "graphviz", "php-pear", "php-xdebug"]
        wo_php_extra = []

    # MySQL repo and packages
    if wo_platform_distro == 'ubuntu':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.3/ubuntu {codename} main"
                         .format(codename=wo_platform_codename))
    elif wo_platform_distro == 'debian':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.3/debian {codename} main"
                         .format(codename=wo_platform_codename))

    wo_mysql = ["mariadb-server", "percona-toolkit"]

    # HHVM repo details
    if wo_platform_distro == 'ubuntu':
        if wo_platform_codename == "trusty" or wo_platform_codename == "xenial" or wo_platform_codename == "bionic":
            wo_hhvm_repo = ("deb http://dl.hhvm.com/ubuntu {codename} main"
                            .format(codename=wo_platform_codename))
    else:
        wo_hhvm_repo = ("deb http://dl.hhvm.com/debian {codename} main"
                        .format(codename=wo_platform_codename))

    wo_hhvm = ["hhvm"]

    # Redis repo details
    if wo_platform_distro == 'ubuntu':
        wo_redis_repo = ("ppa:chris-lea/redis-server")

    else:
        wo_redis_repo = ("deb https://packages.sury.org/php/ {codename} all"
                         .format(codename=wo_platform_codename))

    if (wo_platform_codename == 'trusty' or wo_platform_codename == 'xenial' or wo_platform_codename == 'bionic' or wo_platform_distro == 'debian'):
        wo_redis = ['redis-server', 'php-redis']

    # Repo path
    wo_repo_file = "wo-repo.list"
    wo_repo_file_path = ("/etc/apt/sources.list.d/" + wo_repo_file)

    # Application dabase file path
    basedir = os.path.abspath(os.path.dirname('/var/lib/wo/'))
    wo_db_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

    def __init__(self):
        pass
