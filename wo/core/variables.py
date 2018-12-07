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
    wo_version = "3.9.5.0"
    # WordOps packages versions
    wo_wp_cli = "2.0.1"
    wo_adminer = "4.6.3"

    # Get WPCLI path
    wo_wpcli_path = os.popen('which wp | tr "\n" " "').read()
    if wo_wpcli_path == '':
        wo_wpcli_path = '/usr/bin/wp '

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
    # OpenResty repo and packages
    if wo_platform_codename == 'trusty':
        wo_nginx_repo = ("deb http://openresty.org/package/ubuntu "
                         "trusty openresty")
    elif wo_platform_codename == 'xenial':
        wo_nginx_repo = ("deb http://openresty.org/package/ubuntu "
                         "xenial openresty")
    elif wo_platform_codename == 'bionic':
        wo_nginx_repo = ("deb http://openresty.org/package/ubuntu "
                        "bionic openresty")
    elif wo_platform_codename == 'jessie':
        wo_nginx_repo = ("deb http://openresty.org/package/debian "
                         "jessie openresty")
    elif wo_platform_codename == 'stretch':
        wo_nginx_repo = ("deb http://openresty.org/package/debian "
                         "stretch openresty")

    wo_nginx = ["openresty"]
    wo_nginx_key = 'D5EDEB74'

    # PHP repo and packages
    if wo_platform_distro == 'ubuntu':
        if (wo_platform_codename == 'trusty' or wo_platform_codename == 'xenial' or wo_platform_codename == 'bionic'):
            wo_php_repo = "ppa:ondrej/php"
            wo_php = ["php7.2-fpm", "php-sodium", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                          "php7.2-readline", "php7.2-common", "php7.2-recode",
                          "php7.2-cli", "php7.2-mbstring",
                         "php7.2-bcmath", "php7.2-mysql", "php7.2-opcache", "php7.2-zip", "php7.2-xml", "php7.2-soap"]
            wo_php72 = ["php7.2-fpm", "php-sodium", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                          "php7.2-readline", "php7.2-common", "php7.2-recode",
                          "php7.2-cli", "php7.2-mbstring",
                         "php7.2-bcmath", "php7.2-mysql", "php7.2-opcache", "php7.2-zip", "php7.2-xml", "php7.2-soap"]
            wo_php_extra = ["php-memcached", "php-imagick", "php-memcache", "memcached",
                            "graphviz", "php-pear", "php-xdebug", "php-msgpack", "php-redis"]
    elif wo_platform_distro == 'debian':
        wo_php_repo = ("deb https://packages.sury.org/php/ {codename} main".format(codename=wo_platform_codename))
        wo_php = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                  "php-sodium", "php7.2-common", "php7.2-readline", "php7.2-redis",
                  "php7.2-mysql", "php7.2-cli", "php7.2-memcache", "php7.2-imagick",
                  "php7.2-mbstring", "php7.2-recode", "php7.2-bcmath", "php7.2-opcache", "php7.2-zip", "php7.2-xml",
                     "php7.2-soap", "php7.2-msgpack",
                 "memcached", "graphviz", "php-pear", "php7.2-xdebug"]
        wo_php72 = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                  "php-sodium", "php7.2-common", "php7.2-readline", "php7.2-redis",
                  "php7.2-mysql", "php7.2-cli", "php7.2-memcache", "php7.2-imagick",
                  "php7.2-mbstring", "php7.2-recode", "php7.2-bcmath", "php7.2-opcache", "php7.2-zip", "php7.2-xml",
                     "php7.2-soap", "php7.2-msgpack",
                 "memcached", "graphviz", "php-pear", "php7.2-xdebug"]
        wo_php_extra = []

    # MySQL repo and packages
    if wo_platform_distro == 'ubuntu':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://ams2.mirrors.digitalocean.com/mariadb/repo/"
                         "10.1/ubuntu {codename} main"
                         .format(codename=wo_platform_codename))
    elif wo_platform_distro == 'debian':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://ams2.mirrors.digitalocean.com/mariadb/repo/"
                         "10.1/debian {codename} main"
                         .format(codename=wo_platform_codename))

    wo_mysql = ["mariadb-server", "percona-toolkit"]

    # OpenSMTPd repo and packages
    wo_smtp_repo = ""
    wo_smtp = ["opensmtpd"]

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
        wo_redis = ['redis-server', 'php7.2-redis']

    # Repo path
    wo_repo_file = "wo-repo.list"
    wo_repo_file_path = ("/etc/apt/sources.list.d/" + wo_repo_file)

    # Application dabase file path
    basedir = os.path.abspath(os.path.dirname('/var/lib/wo/'))
    wo_db_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

    def __init__(self):
        pass
