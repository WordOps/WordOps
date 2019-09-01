"""Stack Plugin for WordOps"""

from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook

import codecs
import configparser
import os
import pwd
import random
import shutil
import string
import re
import requests

import psutil

# from pynginxconfig import NginxConfig
from wo.cli.plugins.site_functions import *
from wo.cli.plugins.sitedb import *
from wo.cli.plugins.stack_migrate import WOStackMigrateController
from wo.cli.plugins.stack_services import WOStackStatusController
from wo.cli.plugins.stack_upgrade import WOStackUpgradeController
from wo.cli.plugins.stack_pref import pre_pref, post_pref
from wo.core.apt_repo import WORepo
from wo.core.aptget import WOAptGet
from wo.core.cron import WOCron
from wo.core.download import WODownload
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.services import WOService
from wo.core.shellexec import CommandExecutionError, WOShellExec
from wo.core.variables import WOVariables
from wo.core.template import WOTemplate


def wo_stack_hook(app):
    pass


class WOStackController(CementBaseController):
    class Meta:
        label = 'stack'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Stack command manages stack operations'
        arguments = [
            (['--all'],
                dict(help='Install all stacks at once', action='store_true')),
            (['--web'],
                dict(help='Install web stack', action='store_true')),
            (['--admin'],
                dict(help='Install admin tools stack', action='store_true')),
            (['--security'],
             dict(help='Install security tools stack', action='store_true')),
            (['--nginx'],
                dict(help='Install Nginx stack', action='store_true')),
            (['--php'],
                dict(help='Install PHP 7.2 stack', action='store_true')),
            (['--php73'],
                dict(help='Install PHP 7.3 stack', action='store_true')),
            (['--mysql'],
                dict(help='Install MySQL stack', action='store_true')),
            (['--mysqlclient'],
                dict(help='Install MySQL client for remote MySQL server',
                     action='store_true')),
            (['--mysqltuner'],
                dict(help='Install MySQLTuner stack', action='store_true')),
            (['--wpcli'],
                dict(help='Install WPCLI stack', action='store_true')),
            (['--phpmyadmin'],
                dict(help='Install PHPMyAdmin stack', action='store_true')),
            (['--composer'],
                dict(help='Install Composer stack', action='store_true')),
            (['--netdata'],
                dict(help='Install Netdata monitoring suite',
                     action='store_true')),
            (['--dashboard'],
                dict(help='Install WordOps dashboard', action='store_true')),
            (['--extplorer'],
                dict(help='Install eXtplorer file manager',
                     action='store_true')),
            (['--adminer'],
                dict(help='Install Adminer stack', action='store_true')),
            (['--fail2ban'],
                dict(help='Install Fail2ban stack', action='store_true')),
            (['--clamav'],
                dict(help='Install ClamAV stack', action='store_true')),
            (['--sendmail'],
                dict(help='Install Sendmail stack', action='store_true')),
            (['--utils'],
                dict(help='Install Utils stack', action='store_true')),
            (['--redis'],
                dict(help='Install Redis', action='store_true')),
            (['--phpredisadmin'],
                dict(help='Install phpRedisAdmin', action='store_true')),
            (['--proftpd'],
                dict(help='Install ProFTPd', action='store_true')),
            (['--force'],
                dict(help='Force install/remove/purge without prompt',
                     action='store_true')),
        ]
        usage = "wo stack (command) [options]"

    @expose(hide=True)
    def default(self):
        """default action of wo stack command"""
        self.app.args.print_help()

    @expose(help="Install packages")
    def install(self, packages=[], apt_packages=[], disp_msg=True):
        """Start installation of packages"""
        self.msg = []
        empty_packages = []
        wo_webroot = "/var/www/"
        pargs = self.app.pargs
        try:
            # Default action for stack installation
            if ((not pargs.web) and (not pargs.admin) and
                (not pargs.nginx) and (not pargs.php) and
                (not pargs.mysql) and (not pargs.wpcli) and
                (not pargs.phpmyadmin) and (not pargs.composer) and
                (not pargs.netdata) and (not pargs.dashboard) and
                (not pargs.fail2ban) and (not pargs.security) and
                (not pargs.mysqlclient) and (not pargs.mysqltuner) and
                (not pargs.adminer) and (not pargs.utils) and
                (not pargs.redis) and (not pargs.proftpd) and
                (not pargs.extplorer) and (not pargs.clamav) and
                (not pargs.phpredisadmin) and (not pargs.sendmail) and
                    (not pargs.php73)):
                pargs.web = True
                pargs.admin = True
                pargs.fail2ban = True

            if pargs.all:
                pargs.web = True
                pargs.admin = True
                pargs.php73 = True
                pargs.redis = True
                pargs.proftpd = True
                pargs.security = True

            if pargs.web:
                pargs.nginx = True
                pargs.php = True
                pargs.mysql = True
                pargs.wpcli = True
                pargs.sendmail = True

            if pargs.admin:
                pargs.web = True
                pargs.adminer = True
                pargs.phpmyadmin = True
                pargs.composer = True
                pargs.utils = True
                pargs.netdata = True
                pargs.dashboard = True
                pargs.phpredisadmin = True
                pargs.extplorer = True

            if pargs.security:
                pargs.fail2ban = True
                pargs.clamav = True

            # Nginx
            if pargs.nginx:
                Log.debug(self, "Setting apt_packages variable for Nginx")

                if not (WOAptGet.is_installed(self, 'nginx-custom')):
                    if not (WOAptGet.is_installed(self, 'nginx-plus') or
                            WOAptGet.is_installed(self, 'nginx')):
                        apt_packages = apt_packages + WOVariables.wo_nginx
                    else:
                        if WOAptGet.is_installed(self, 'nginx-plus'):
                            Log.info(self, "NGINX PLUS Detected ...")
                            apt = ["nginx-plus"] + WOVariables.wo_nginx
                            self.post_pref(apt, empty_packages)
                        elif WOAptGet.is_installed(self, 'nginx'):
                            Log.info(self, "WordOps detected an already "
                                     "installed nginx package."
                                     "It may or may not have "
                                     "required modules.\n")
                            apt = ["nginx"] + WOVariables.wo_nginx
                            self.post_pref(apt, empty_packages)
                else:
                    Log.debug(self, "Nginx Stable already installed")

            # Redis
            if pargs.redis:
                pargs.php = True
                if not WOAptGet.is_installed(self, 'redis-server'):
                    apt_packages = apt_packages + WOVariables.wo_redis

                else:
                    Log.info(self, "Redis already installed")

            # PHP 7.2
            if pargs.php:
                Log.debug(self, "Setting apt_packages variable for PHP 7.2")
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    if not (WOAptGet.is_installed(self, 'php7.3-fpm')):
                        apt_packages = apt_packages + WOVariables.wo_php + \
                            WOVariables.wo_php_extra
                    else:
                        apt_packages = apt_packages + WOVariables.wo_php
                else:
                    Log.debug(self, "PHP 7.2 already installed")
                    Log.info(self, "PHP 7.2 already installed")

            # PHP 7.3
            if pargs.php73:
                Log.debug(self, "Setting apt_packages variable for PHP 7.3")
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                    if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                        apt_packages = apt_packages + WOVariables.wo_php + \
                            WOVariables.wo_php73 + WOVariables.wo_php_extra
                    else:
                        apt_packages = apt_packages + WOVariables.wo_php73
                else:
                    Log.debug(self, "PHP 7.3 already installed")
                    Log.info(self, "PHP 7.3 already installed")

            # MariaDB 10.3
            if pargs.mysql:
                pargs.mysqltuner = True
                Log.debug(self, "Setting apt_packages variable for MySQL")
                if not WOShellExec.cmd_exec(self, "mysqladmin ping"):
                    apt_packages = apt_packages + WOVariables.wo_mysql
                else:
                    Log.debug(self, "MySQL already installed and alive")
                    Log.info(self, "MySQL already installed and alive")

            # mysqlclient
            if pargs.mysqlclient:
                Log.debug(self, "Setting apt_packages variable "
                          "for MySQL Client")
                if not WOShellExec.cmd_exec(self, "mysqladmin ping"):
                    apt_packages = apt_packages + WOVariables.wo_mysql_client
                else:
                    Log.debug(self, "MySQL already installed and alive")
                    Log.info(self, "MySQL already installed and alive")

            # WP-CLI
            if pargs.wpcli:
                Log.debug(self, "Setting packages variable for WP-CLI")
                if ((not os.path.isfile("/usr/local/bin/wp")) and
                        (not os.path.isfile("/usr/bin/wp"))):
                    packages = packages + [["https://github.com/wp-cli/wp-cli/"
                                            "releases/download/v{0}/"
                                            "wp-cli-{0}.phar"
                                            "".format(WOVariables.wo_wp_cli),
                                            "/usr/local/bin/wp",
                                            "WP-CLI"]]
                else:
                    Log.debug(self, "WP-CLI is already installed")
                    Log.info(self, "WP-CLI is already installed")

            # fail2ban
            if pargs.fail2ban:
                Log.debug(self, "Setting apt_packages variable for Fail2ban")
                if not WOAptGet.is_installed(self, 'fail2ban'):
                    apt_packages = apt_packages + WOVariables.wo_fail2ban
                else:
                    Log.debug(self, "Fail2ban already installed")
                    Log.info(self, "Fail2ban already installed")

            # ClamAV
            if pargs.clamav:
                Log.debug(self, "Setting apt_packages variable for ClamAV")
                if not WOAptGet.is_installed(self, 'clamav'):
                    apt_packages = apt_packages + WOVariables.wo_clamav
                else:
                    Log.debug(self, "ClamAV already installed")
                    Log.info(self, "ClamAV already installed")

            # sendmail
            if pargs.sendmail:
                Log.debug(self, "Setting apt_packages variable for Sendmail")
                if not WOAptGet.is_installed(self, 'sendmail'):
                    apt_packages = apt_packages + ["sendmail"]
                else:
                    Log.debug(self, "Sendmail already installed")
                    Log.info(self, "Sendmail already installed")

            # proftpd
            if pargs.proftpd:
                Log.debug(self, "Setting apt_packages variable for ProFTPd")
                if not WOAptGet.is_installed(self, 'proftpd-basic'):
                    apt_packages = apt_packages + ["proftpd-basic"]
                else:
                    Log.debug(self, "ProFTPd already installed")
                    Log.info(self, "ProFTPd already installed")

            # PHPMYADMIN
            if pargs.phpmyadmin:
                pargs.composer = True
                if not os.path.isdir('/var/www/22222/htdocs/db/pma'):
                    Log.debug(self, "Setting packages variable "
                              "for phpMyAdmin ")
                    packages = packages + [["https://github.com/phpmyadmin/"
                                            "phpmyadmin/archive/STABLE.tar.gz",
                                            "/var/lib/wo/tmp/pma.tar.gz",
                                            "phpMyAdmin"]]
                else:
                    Log.debug(self, "phpMyAdmin already installed")
                    Log.info(self, "phpMyAdmin already installed")

                    # PHPREDISADMIN
            if pargs.phpredisadmin:
                pargs.composer = True
                if not os.path.isdir('/var/www/22222/htdocs/'
                                     'cache/redis/phpRedisAdmin'):
                    Log.debug(
                        self, "Setting packages variable for phpRedisAdmin")
                    packages = packages + [["https://github.com/"
                                            "erikdubbelboer/"
                                            "phpRedisAdmin/archive"
                                            "/v1.11.3.tar.gz",
                                            "/var/lib/wo/tmp/pra.tar.gz",
                                            "phpRedisAdmin"]]
                else:
                    Log.debug(self, "phpRedisAdmin already installed")
                    Log.info(self, "phpRedisAdmin already installed")

            # Composer
            if pargs.composer:
                if ((not WOAptGet.is_installed(self, 'php7.2-fpm')) and
                        (not WOAptGet.is_installed(self, 'php7.3-fpm'))):
                    pargs.php = True
                if not os.path.isfile('/usr/local/bin/composer'):
                    Log.debug(self, "Setting packages variable for Composer ")
                    packages = packages + [["https://getcomposer.org/"
                                            "installer",
                                            "/var/lib/wo/tmp/composer-install",
                                            "Composer"]]
                else:
                    Log.debug(self, "Composer already installed")
                    Log.info(self, "Composer already installed")

            # ADMINER
            if pargs.adminer:
                if not os.path.isfile("{0}22222/htdocs/db/"
                                      "adminer/index.php"
                                      .format(wo_webroot)):
                    Log.debug(self, "Setting packages variable for Adminer ")
                    packages = packages + [["https://github.com/vrana/adminer/"
                                            "releases/download/v{0}"
                                            "/adminer-{0}.php"
                                            .format(WOVariables.wo_adminer),
                                            "{0}22222/"
                                            "htdocs/db/adminer/index.php"
                                            .format(WOVariables.wo_webroot),
                                            "Adminer"],
                                           ["https://raw.githubusercontent.com"
                                            "/vrana/adminer/master/designs/"
                                            "pepa-linha/adminer.css",
                                            "{0}22222/"
                                            "htdocs/db/adminer/adminer.css"
                                            .format(WOVariables.wo_webroot),
                                            "Adminer theme"]]
                else:
                    Log.debug(self, "Adminer already installed")
                    Log.info(self, "Adminer already installed")

            # mysqltuner
            if pargs.mysqltuner:
                if not os.path.isfile("/usr/bin/mysqltuner"):
                    Log.debug(self, "Setting packages variable "
                              "for MySQLTuner ")
                    packages = packages + [["https://raw."
                                            "githubusercontent.com/"
                                            "major/MySQLTuner-perl"
                                            "/master/mysqltuner.pl",
                                            "/usr/bin/mysqltuner",
                                            "MySQLTuner"]]
                else:
                    Log.debug(self, "MySQLtuner already installed")
                    Log.info(self, "MySQLtuner already installed")

            # Netdata
            if pargs.netdata:
                if (not os.path.isdir('/opt/netdata') and not
                        os.path.isdir("/etc/netdata")):
                    Log.debug(
                        self, "Setting packages variable for Netdata")
                    if WOVariables.wo_distro == 'raspbian':
                        packages = packages + [['https://my-netdata.io/'
                                                'kickstart.sh',
                                                '/var/lib/wo/tmp/kickstart.sh',
                                                'Netdata']]
                    else:
                        packages = packages + [['https://my-netdata.io/'
                                                'kickstart-static64.sh',
                                                '/var/lib/wo/tmp/kickstart.sh',
                                                'Netdata']]
                else:
                    Log.debug(self, "Netdata already installed")
                    Log.info(self, "Netdata already installed")

            # WordOps Dashboard
            if pargs.dashboard:
                if not os.path.isfile('/var/www/22222/htdocs/index.php'):
                    Log.debug(self,
                              "Setting packages variable for WO-Dashboard")
                    packages = \
                        packages + [["https://github.com/WordOps"
                                     "/wordops-dashboard/"
                                     "releases/download/v{0}/"
                                     "wordops-dashboard.tar.gz"
                                     .format(WOVariables.wo_dashboard),
                                     "/var/lib/wo/tmp/wo-dashboard.tar.gz",
                                     "WordOps Dashboard"]]
                else:
                    Log.debug(self, "WordOps dashboard already installed")
                    Log.info(self, "WordOps dashboard already installed")

            # eXtplorer
            if pargs.extplorer:
                if not os.path.isdir('/var/www/22222/htdocs/files'):
                    Log.debug(self, "Setting packages variable for eXtplorer")
                    packages = packages + \
                        [["https://github.com/soerennb/"
                          "extplorer/archive/v{0}.tar.gz"
                          .format(WOVariables.wo_extplorer),
                          "/var/lib/wo/tmp/extplorer.tar.gz",
                          "eXtplorer"]]
                else:
                    Log.debug(self, "eXtplorer is already installed")
                    Log.info(self, "eXtplorer is already installed")

            # UTILS
            if pargs.utils:
                Log.debug(self, "Setting packages variable for utils")
                packages = packages + [["https://raw.githubusercontent.com"
                                        "/rtCamp/eeadmin/master/cache/nginx/"
                                        "clean.php",
                                        "{0}22222/htdocs/cache/"
                                        "nginx/clean.php"
                                        .format(WOVariables.wo_webroot),
                                        "clean.php"],
                                       ["https://raw.github.com/rlerdorf/"
                                        "opcache-status/master/opcache.php",
                                        "{0}22222/htdocs/cache/"
                                        "opcache/opcache.php"
                                        .format(WOVariables.wo_webroot),
                                        "opcache.php"],
                                       ["https://raw.github.com/amnuts/"
                                        "opcache-gui/master/index.php",
                                        "{0}22222/htdocs/"
                                        "cache/opcache/opgui.php"
                                        .format(WOVariables.wo_webroot),
                                        "Opgui"],
                                       ["https://raw.githubusercontent.com/"
                                        "mlazarov/ocp/master/ocp.php",
                                        "{0}22222/htdocs/cache/"
                                        "opcache/ocp.php"
                                        .format(WOVariables.wo_webroot),
                                        "OCP.php"],
                                       ["https://github.com/jokkedk/webgrind/"
                                        "archive/master.tar.gz",
                                        '/var/lib/wo/tmp/webgrind.tar.gz',
                                        'Webgrind'],
                                       ["https://www.percona.com/"
                                        "get/pt-query-digest",
                                        "/usr/bin/pt-query-advisor",
                                        "pt-query-advisor"],
                                       ["https://github.com/box/Anemometer/"
                                        "archive/master.tar.gz",
                                        '/var/lib/wo/tmp/anemometer.tar.gz',
                                        'Anemometer']]

        except Exception as e:
            Log.debug(self, "{0}".format(e))

        if (apt_packages) or (packages):
            if (apt_packages):
                Log.debug(self, "Calling pre_pref")
                pre_pref(self, apt_packages)
                # meminfo = (os.popen('/bin/cat /proc/meminfo '
                #                    '| grep MemTotal').read()).split(":")
                # memsplit = re.split(" kB", meminfo[1])
                # wo_mem = int(memsplit[0])
                # if (wo_mem < 4000000):
                #    WOSwap.add(self)
                Log.info(self, "Updating apt-cache, please wait...")
                WOAptGet.update(self)
                Log.info(self, "Installing packages, please wait...")
                WOAptGet.install(self, apt_packages)
                post_pref(self, apt_packages, empty_packages)
            if (packages):
                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)
                Log.debug(self, "Calling post_pref")
                post_pref(self, empty_packages, packages)

            if disp_msg:
                if (self.msg):
                    for msg in self.msg:
                        Log.info(self, Log.ENDC + msg)
                Log.info(self, "Successfully installed packages")
            else:
                return self.msg

    @expose(help="Remove packages")
    def remove(self):
        """Start removal of packages"""
        apt_packages = []
        packages = []
        pargs = self.app.pargs
        if ((not pargs.web) and (not pargs.admin) and
            (not pargs.nginx) and (not pargs.php) and
            (not pargs.mysql) and (not pargs.wpcli) and
            (not pargs.phpmyadmin) and (not pargs.composer) and
                (not pargs.netdata) and (not pargs.dashboard) and
                (not pargs.fail2ban) and (not pargs.security) and
                (not pargs.mysqlclient) and (not pargs.mysqltuner) and
                (not pargs.adminer) and (not pargs.utils) and
                (not pargs.redis) and (not pargs.proftpd) and
                (not pargs.extplorer) and (not pargs.clamav) and
                (not pargs.phpredisadmin) and (not pargs.sendmail) and
                (not pargs.php73)):
            pargs.web = True
            pargs.admin = True
            pargs.security = True

        if pargs.all:
            pargs.web = True
            pargs.admin = True
            pargs.php73 = True
            pargs.fail2ban = True
            pargs.proftpd = True
            pargs.utils = True
            pargs.redis = True
            packages = packages + ['/var/www/22222/htdocs/*']

        if pargs.web:
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.wpcli = True
            pargs.sendmail = True

        if pargs.admin:
            pargs.composer = True
            pargs.utils = True
            pargs.netdata = True
            pargs.mysqltuner = True

        if pargs.security:
            pargs.fail2ban = True
            pargs.clamav = True

        # NGINX
        if pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Removing apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx

        # PHP 7.2
        if pargs.php:
            Log.debug(self, "Removing apt_packages variable of PHP")
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php

        # PHP7.3
        if pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php73 + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php73

        # REDIS
        if pargs.redis:
            Log.debug(self, "Remove apt_packages variable of Redis")
            apt_packages = apt_packages + WOVariables.wo_redis

        # MariaDB
        if pargs.mysql:
            Log.debug(self, "Removing apt_packages variable of MySQL")
            apt_packages = apt_packages + WOVariables.wo_mysql

        # mysqlclient
        if pargs.mysqlclient:
            Log.debug(self, "Removing apt_packages variable "
                      "for MySQL Client")
            if WOShellExec.cmd_exec(self, "mysqladmin ping"):
                apt_packages = apt_packages + WOVariables.wo_mysql_client

        # fail2ban
        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                Log.debug(self, "Remove apt_packages variable of Fail2ban")
                apt_packages = apt_packages + WOVariables.wo_fail2ban

        # ClamAV
        if pargs.clamav:
            Log.debug(self, "Setting apt_packages variable for ClamAV")
            if WOAptGet.is_installed(self, 'clamav'):
                apt_packages = apt_packages + WOVariables.wo_clamav

        # sendmail
        if pargs.sendmail:
            Log.debug(self, "Setting apt_packages variable for Sendmail")
            if WOAptGet.is_installed(self, 'sendmail'):
                apt_packages = apt_packages + ["sendmail"]

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                Log.debug(self, "Remove apt_packages variable for ProFTPd")
                apt_packages = apt_packages + ["proftpd-basic"]

        # WPCLI
        if pargs.wpcli:
            Log.debug(self, "Removing package variable of WPCLI ")
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + ['/usr/local/bin/wp']

        # PHPMYADMIN
        if pargs.phpmyadmin:
            Log.debug(self, "Removing package of phpMyAdmin ")
            packages = packages + ['{0}22222/htdocs/db/pma'
                                   .format(WOVariables.wo_webroot)]
        # Composer
        if pargs.composer:
            Log.debug(self, "Removing package of Composer ")
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + ['/usr/local/bin/composer']

        if pargs.mysqltuner:
            Log.debug(self, "Removing packages for MySQLTuner ")
            packages = packages + ['/usr/bin/mysqltuner']

        # PHPREDISADMIN
        if pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            if os.path.isdir('{0}22222/htdocs/cache/redis'
                             .format(WOVariables.wo_webroot)):
                packages = packages + ['{0}22222/htdocs/'
                                       'cache/redis'
                                       .format(WOVariables.wo_webroot)]
        # ADMINER
        if pargs.adminer:
            Log.debug(self, "Removing package variable of Adminer ")
            packages = packages + ['{0}22222/htdocs/db/adminer'
                                   .format(WOVariables.wo_webroot)]
        if pargs.utils:
            Log.debug(self, "Removing package variable of utils ")
            packages = packages + ['{0}22222/htdocs/php/webgrind/'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/cache/opcache'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/cache/nginx/'
                                   'clean.php'.format(WOVariables.wo_webroot),
                                   '/usr/bin/pt-query-advisor',
                                   '{0}22222/htdocs/db/anemometer'
                                   .format(WOVariables.wo_webroot)]

        if pargs.netdata:
            Log.debug(self, "Removing Netdata")
            if os.path.isfile('/opt/netdata/usr/'
                              'libexec/netdata-uninstaller.sh'):
                packages = packages + ['/var/lib/wo/tmp/kickstart.sh']

        if pargs.dashboard:
            Log.debug(self, "Removing Wo-Dashboard")
            packages = packages + ['{0}22222/htdocs/assets'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/index.php'
                                   .format(WOVariables.wo_webroot)]

        if (packages) or (apt_packages):
            if (not pargs.force):
                start_remove = input('Are you sure you to want to'
                                     ' remove from server.'
                                     '\nPackage configuration will remain'
                                     ' on server after this operation.\n'
                                     'Remove stacks [y/N]?')
                if start_remove != "Y" and start_remove != "y":
                    Log.error(self, "Not starting stack removal")

            if (set(["nginx-custom"]).issubset(set(apt_packages))):
                WOService.stop_service(self, 'nginx')

            # Netdata uninstaller
            if (set(['/var/lib/wo/tmp/'
                     'kickstart.sh']).issubset(set(packages))):
                if WOVariables.wo_distro == 'Raspbian':
                    WOShellExec.cmd_exec(self, "bash /usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")
                else:
                    WOShellExec.cmd_exec(self, "bash /opt/netdata/usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")

            if (packages):
                Log.info(self, "Removing packages, please wait...")
                WOFileUtils.remove(self, packages)

            if (apt_packages):
                Log.debug(self, "Removing apt_packages")
                Log.info(self, "Removing apt packages, please wait...")
                WOAptGet.remove(self, apt_packages)
                WOAptGet.auto_remove(self)

            Log.info(self, "Successfully removed packages")

    @expose(help="Purge packages")
    def purge(self):
        """Start purging of packages"""
        apt_packages = []
        packages = []
        pargs = self.app.pargs
        # Default action for stack purge
        if ((not pargs.web) and (not pargs.admin) and
            (not pargs.nginx) and (not pargs.php) and
            (not pargs.mysql) and (not pargs.wpcli) and
            (not pargs.phpmyadmin) and (not pargs.composer) and
                (not pargs.netdata) and (not pargs.dashboard) and
                (not pargs.fail2ban) and (not pargs.security) and
                (not pargs.mysqlclient) and (not pargs.mysqltuner) and
                (not pargs.adminer) and (not pargs.utils) and
                (not pargs.redis) and (not pargs.proftpd) and
                (not pargs.extplorer) and (not pargs.clamav) and
                (not pargs.phpredisadmin) and (not pargs.sendmail) and
                (not pargs.php73)):
            pargs.web = True
            pargs.admin = True
            pargs.security = True

        if pargs.all:
            pargs.web = True
            pargs.admin = True
            pargs.php73 = True
            pargs.fail2ban = True
            pargs.proftpd = True
            pargs.utils = True
            pargs.redis = True
            packages = packages + ['/var/www/22222/htdocs/*']

        if pargs.web:
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.wpcli = True
            pargs.sendmail = True

        if pargs.admin:
            pargs.utils = True
            pargs.composer = True
            pargs.netdata = True
            pargs.mysqltuner = True

        if pargs.security:
            pargs.fail2ban = True
            pargs.clamav = True

        # NGINX
        if pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Purge apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx

        # PHP
        if pargs.php:
            Log.debug(self, "Purge apt_packages variable PHP")
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.3-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php

        # PHP 7.3
        if pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php73 + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php73

        # REDIS
        if pargs.redis:
            Log.debug(self, "Remove apt_packages variable of Redis")
            apt_packages = apt_packages + WOVariables.wo_redis

        # MariaDB
        if pargs.mysql:
            Log.debug(self, "Removing apt_packages variable of MySQL")
            apt_packages = apt_packages + WOVariables.wo_mysql

        # mysqlclient
        if pargs.mysqlclient:
            Log.debug(self, "Removing apt_packages variable "
                      "for MySQL Client")
            if WOShellExec.cmd_exec(self, "mysqladmin ping"):
                apt_packages = apt_packages + WOVariables.wo_mysql_client

        # fail2ban
        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                Log.debug(self, "Remove apt_packages variable of Fail2ban")
                apt_packages = apt_packages + WOVariables.wo_fail2ban

        # ClamAV
        if pargs.clamav:
            Log.debug(self, "Setting apt_packages variable for ClamAV")
            if WOAptGet.is_installed(self, 'clamav'):
                apt_packages = apt_packages + WOVariables.wo_clamav

        # sendmail
        if pargs.sendmail:
            Log.debug(self, "Setting apt_packages variable for Sendmail")
            if WOAptGet.is_installed(self, 'sendmail'):
                apt_packages = apt_packages + ["sendmail"]

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                Log.debug(self, "Purge apt_packages variable for ProFTPd")
                apt_packages = apt_packages + ["proftpd-basic"]

        # WP-CLI
        if pargs.wpcli:
            Log.debug(self, "Purge package variable WPCLI")
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + ['/usr/local/bin/wp']

        # PHPMYADMIN
        if pargs.phpmyadmin:
            packages = packages + ['{0}22222/htdocs/db/pma'.
                                   format(WOVariables.wo_webroot)]
            Log.debug(self, "Purge package variable phpMyAdmin")

        # Composer
        if pargs.composer:
            Log.debug(self, "Removing package variable of Composer ")
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + ['/usr/local/bin/composer']

        if pargs.mysqltuner:
            Log.debug(self, "Removing packages for MySQLTuner ")
            packages = packages + ['/usr/bin/mysqltuner']

        # PHPREDISADMIN
        if pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            if os.path.isdir('{0}22222/htdocs/cache/redis'
                             .format(WOVariables.wo_webroot)):
                packages = packages + ['{0}22222/htdocs/'
                                       'cache/redis'
                                       .format(WOVariables.wo_webroot)]
        # Adminer
        if pargs.adminer:
            Log.debug(self, "Purge  package variable Adminer")
            packages = packages + ['{0}22222/htdocs/db/adminer'
                                   .format(WOVariables.wo_webroot)]
        # utils
        if pargs.utils:
            Log.debug(self, "Purge package variable utils")
            packages = packages + ['{0}22222/htdocs/php/webgrind/'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/cache/opcache'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/cache/nginx/'
                                   'clean.php'.format(WOVariables.wo_webroot),
                                   '/usr/bin/pt-query-advisor',
                                   '{0}22222/htdocs/db/anemometer'
                                   .format(WOVariables.wo_webroot)
                                   ]

        if pargs.netdata:
            Log.debug(self, "Removing Netdata")
            if os.path.isfile('/opt/netdata/usr/'
                              'libexec/netdata-uninstaller.sh'):
                packages = packages + ['/var/lib/wo/tmp/kickstart.sh']

        if pargs.dashboard:
            Log.debug(self, "Removing Wo-Dashboard")
            packages = packages + ['{0}22222/htdocs/assets/'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/index.php'
                                   .format(WOVariables.wo_webroot)]

        if (packages) or (apt_packages):
            if (not pargs.force):
                start_purge = input('Are you sure you to want to'
                                    ' purge stacks from this server ?'
                                    '\nPackage configuration and data '
                                    'will not remain'
                                    ' on this server after this operation.\n'
                                    'Purge stacks [y/N]')
                if start_purge != "Y" and start_purge != "y":
                    Log.error(self, "Not starting stack purge")

            if (set(["nginx-custom"]).issubset(set(apt_packages))):
                WOService.stop_service(self, 'nginx')

            if (set(["fail2ban"]).issubset(set(apt_packages))):
                WOService.stop_service(self, 'fail2ban')

            # Netdata uninstaller
            if (set(['/var/lib/wo/tmp/'
                     'kickstart.sh']).issubset(set(packages))):
                if WOVariables.wo_distro == 'Raspbian':
                    WOShellExec.cmd_exec(self, "bash /usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")
                else:
                    WOShellExec.cmd_exec(self, "bash /opt/netdata/usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")

            if (apt_packages):
                Log.info(self, "Purging apt packages, please wait...")
                WOAptGet.remove(self, apt_packages, purge=True)
                WOAptGet.auto_remove(self)

            if (packages):
                Log.info(self, "Purging packages, please wait...")
                WOFileUtils.remove(self, packages)
                WOAptGet.auto_remove(self)

            Log.info(self, "Successfully purged packages")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    handler.register(WOStackController)
    handler.register(WOStackStatusController)
    handler.register(WOStackMigrateController)
    handler.register(WOStackUpgradeController)

    # register a hook (function) to run after arguments are parsed.
    hook.register('post_argument_parsing', wo_stack_hook)
