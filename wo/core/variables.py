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
    wo_version = "3.9.0"
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
    # Nginx repo and packages
    if wo_platform_codename == 'precise':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_12.04/ /")
    elif wo_platform_codename == 'trusty':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_14.04/ /")
    elif wo_platform_codename == 'xenial':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/xUbuntu_16.04/ /")
    elif wo_platform_codename == 'bionic':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                        "/rtCamp:/EasyEngine/xUbuntu_18.04/ /")
    elif wo_platform_codename == 'whwozy':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/Debian_7.0/ /")
    elif wo_platform_codename == 'jessie':
        wo_nginx_repo = ("deb http://download.opensuse.org/repositories/home:"
                         "/rtCamp:/EasyEngine/Debian_8.0/ /")


    wo_nginx = ["nginx-custom", "nginx-ee"]
    wo_nginx_key = '3050AC3CD2AE6F03'

    # PHP repo and packages
    if wo_platform_distro == 'ubuntu':
        if wo_platform_codename == 'precise':
            wo_php_repo = "ppa:ondrej/php5-5.6"
            wo_php = ["php5-fpm", "php5-curl", "php5-gd", "php5-imap",
                    "php5-mcrypt", "php5-common", "php5-readline",
                     "php5-mysql", "php5-cli", "php5-memcache", "php5-imagick",
                     "memcached", "graphviz", "php-pear"]
        elif (wo_platform_codename == 'trusty' or wo_platform_codename == 'xenial' or wo_platform_codename == 'bionic'):
            wo_php_repo = "ppa:ondrej/php"
            # PHP5.6 for those who like to live on the dangerous side
            wo_php5_6 = ["php5.6-fpm", "php5.6-curl", "php5.6-gd", "php5.6-imap",
                        "php5.6-mcrypt", "php5.6-readline", "php5.6-common", "php5.6-recode",
                        "php5.6-mysql", "php5.6-cli", "php5.6-curl", "php5.6-mbstring",
                         "php5.6-bcmath", "php5.6-mysql", "php5.6-opcache", "php5.6-zip", "php5.6-xml", "php5.6-soap"]
            # PHP7.0 going EOL soon
            wo_php7_0 = ["php7.0-fpm", "php7.0-curl", "php7.0-gd", "php7.0-imap",
                          "php7.0-mcrypt", "php7.0-readline", "php7.0-common", "php7.0-recode",
                          "php7.0-cli", "php7.0-mbstring",
                         "php7.0-bcmath", "php7.0-mysql", "php7.0-opcache", "php7.0-zip", "php7.0-xml", "php7.0-soap"]
            wo_php7_2 = ["php7.2-fpm", "php7.2-curl", "php7.2-gd", "php7.2-imap",
                          "php7.2-readline", "php7.2-common", "php7.2-recode",
                          "php7.2-cli", "php7.2-mbstring",
                         "php7.2-bcmath", "php7.2-mysql", "php7.2-opcache", "php7.2-zip", "php7.2-xml", "php7.2-soap"]
            wo_php_extra = ["php-memcached", "php-imagick", "php-memcache", "memcached",
                            "graphviz", "php-pear", "php-xdebug", "php-msgpack", "php-redis"]
    elif wo_platform_distro == 'debian':
        if wo_platform_codename == 'wheezy':
            wo_php_repo = ("deb http://packages.dotdeb.org {codename}-php56 all"
                       .format(codename=wo_platform_codename))
        else :
            wo_php_repo = ("deb http://packages.dotdeb.org {codename} all".format(codename=wo_platform_codename))

        wo_php = ["php5-fpm", "php5-curl", "php5-gd", "php5-imap",
                  "php5-mcrypt", "php5-common", "php5-readline",
                  "php5-mysqlnd", "php5-cli", "php5-memcache", "php5-imagick",
                 "memcached", "graphviz", "php-pear"]

        wo_php7_0 = ["php7.0-fpm", "php7.0-curl", "php7.0-gd", "php7.0-imap",
                  "php7.0-mcrypt", "php7.0-common", "php7.0-readline", "php7.0-redis",
                  "php7.0-mysql", "php7.0-cli", "php7.0-memcache", "php7.0-imagick",
                  "php7.0-mbstring", "php7.0-recode", "php7.0-bcmath", "php7.0-opcache", "php7.0-zip", "php7.0-xml",
                     "php7.0-soap", "php7.0-msgpack",
                 "memcached", "graphviz", "php-pear", "php7.0-xdebug"]
        wo_php_extra = []

    if wo_platform_codename == 'wheezy':
        wo_php = wo_php + ["php5-dev"]

    if wo_platform_codename == 'precise' or wo_platform_codename == 'jessie':
        wo_php = wo_php + ["php5-xdebug"]

    # MySQL repo and packages
    if wo_platform_distro == 'ubuntu':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.1/ubuntu {codename} main"
                         .format(codename=wo_platform_codename))
    elif wo_platform_distro == 'debian':
        wo_mysql_repo = ("deb [arch=amd64,i386,ppc64el] http://sfo1.mirrors.digitalocean.com/mariadb/repo/"
                         "10.1/debian {codename} main"
                         .format(codename=wo_platform_codename))

    wo_mysql = ["mariadb-server", "percona-toolkit"]

    # HHVM repo details
    # 12.04 requires boot repository
    if wo_platform_distro == 'ubuntu':
        if wo_platform_codename == "precise":
            wo_boost_repo = ("ppa:mapnik/boost")
            wo_hhvm_repo = ("deb http://dl.hhvm.com/ubuntu {codename} main"
                        .format(codename=wo_platform_codename))
        elif wo_platform_codename == "trusty":
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
        wo_redis_repo = ("deb http://packages.dotdeb.org {codename} all"
                        .format(codename=wo_platform_codename))

    if (wo_platform_codename == 'trusty' or wo_platform_codename == 'xenial' or wo_platform_codename == 'bionic'):
        wo_redis = ['redis-server', 'php-redis']
    else:
        wo_redis = ['redis-server', 'php5-redis']

    # Repo path
    wo_repo_file = "wo-repo.list"
    wo_repo_file_path = ("/etc/apt/sources.list.d/" + wo_repo_file)

    # Application dabase file path
    basedir = os.path.abspath(os.path.dirname('/var/lib/wo/'))
    wo_db_uri = 'sqlite:///' + os.path.join(basedir, 'dbase.db')

    def __init__(self):
        pass
