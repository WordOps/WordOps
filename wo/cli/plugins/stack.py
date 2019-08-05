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
from wo.core.addswap import WOSwap
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
            (['--adminer'],
                dict(help='Install Adminer stack', action='store_true')),
            (['--fail2ban'],
                dict(help='Install Fail2ban stack', action='store_true')),
            (['--utils'],
                dict(help='Install Utils stack', action='store_true')),
            (['--redis'],
                dict(help='Install Redis', action='store_true')),
            (['--phpredisadmin'],
                dict(help='Install phpRedisAdmin', action='store_true')),
            (['--proftpd'],
                dict(help='Install ProFTPd', action='store_true')),
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
        try:
            # Default action for stack installation
            if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
                (not self.app.pargs.nginx) and (not self.app.pargs.php) and
                (not self.app.pargs.mysql) and (not self.app.pargs.wpcli) and
                (not self.app.pargs.phpmyadmin) and
                (not self.app.pargs.composer) and
                (not self.app.pargs.netdata) and
                (not self.app.pargs.dashboard) and
                (not self.app.pargs.fail2ban) and
                (not self.app.pargs.security) and
                (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
                (not self.app.pargs.redis) and (not self.app.pargs.proftpd) and
                (not self.app.pargs.phpredisadmin) and
                    (not self.app.pargs.php73)):
                self.app.pargs.web = True
                self.app.pargs.admin = True
                self.app.pargs.security = True

            if self.app.pargs.all:
                self.app.pargs.web = True
                self.app.pargs.admin = True
                self.app.pargs.php73 = True
                self.app.pargs.redis = True
                self.app.pargs.proftpd = True

            if self.app.pargs.web:
                self.app.pargs.nginx = True
                self.app.pargs.php = True
                self.app.pargs.mysql = True
                self.app.pargs.wpcli = True

            if self.app.pargs.admin:
                self.app.pargs.nginx = True
                self.app.pargs.php = True
                self.app.pargs.mysql = True
                self.app.pargs.adminer = True
                self.app.pargs.phpmyadmin = True
                self.app.pargs.composer = True
                self.app.pargs.utils = True
                self.app.pargs.netdata = True
                self.app.pargs.dashboard = True
                self.app.pargs.phpredisadmin = True

            if self.app.pargs.security:
                self.app.pargs.fail2ban = True

            # Redis
            if self.app.pargs.redis:
                if not WOAptGet.is_installed(self, 'redis-server'):
                    apt_packages = apt_packages + WOVariables.wo_redis
                    self.app.pargs.php = True
                else:
                    Log.info(self, "Redis already installed")

            # Nginx
            if self.app.pargs.nginx:
                Log.debug(self, "Setting apt_packages variable for Nginx")

                if not (WOAptGet.is_installed(self, 'nginx-custom')):
                    if not (WOAptGet.is_installed(self, 'nginx-plus') or
                            WOAptGet.is_installed(self, 'nginx')):
                        apt_packages = apt_packages + WOVariables.wo_nginx
                    else:
                        if WOAptGet.is_installed(self, 'nginx-plus'):
                            Log.info(self, "NGINX PLUS Detected ...")
                            apt = ["nginx-plus"] + WOVariables.wo_nginx
                            self.post_pref(apt, packages)
                        elif WOAptGet.is_installed(self, 'nginx'):
                            Log.info(self, "WordOps detected an already "
                                     "installed nginx package."
                                     "It may or may not have "
                                     "required modules.\n")
                            apt = ["nginx"] + WOVariables.wo_nginx
                            self.post_pref(apt, packages)
                else:
                    Log.debug(self, "Nginx Stable already installed")

            # PHP 7.2
            if self.app.pargs.php:
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
            if self.app.pargs.php73:
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
            if self.app.pargs.mysql:
                Log.debug(self, "Setting apt_packages variable for MySQL")
                if not WOShellExec.cmd_exec(self, "mysqladmin ping"):
                    apt_packages = apt_packages + WOVariables.wo_mysql
                    packages = packages + [["https://raw."
                                            "githubusercontent.com/"
                                            "major/MySQLTuner-perl"
                                            "/master/mysqltuner.pl",
                                            "/usr/bin/mysqltuner",
                                            "MySQLTuner"]]

                else:
                    Log.debug(self, "MySQL connection is already alive")
                    Log.info(self, "MySQL connection is already alive")

            # WP-CLI
            if self.app.pargs.wpcli:
                Log.debug(self, "Setting packages variable for WP-CLI")
                if not WOShellExec.cmd_exec(self, "command -v wp"):
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
            if self.app.pargs.fail2ban:
                Log.debug(self, "Setting apt_packages variable for Fail2ban")
                if not WOAptGet.is_installed(self, 'fail2ban'):
                    apt_packages = apt_packages + WOVariables.wo_fail2ban
                else:
                    Log.debug(self, "Fail2ban already installed")
                    Log.info(self, "Fail2ban already installed")

            # proftpd
            if self.app.pargs.proftpd:
                Log.debug(self, "Setting apt_packages variable for ProFTPd")
                if not WOAptGet.is_installed(self, 'proftpd-basic'):
                    apt_packages = apt_packages + ["proftpd-basic"]
                else:
                    Log.debug(self, "ProFTPd already installed")
                    Log.info(self, "ProFTPd already installed")

            # PHPMYADMIN
            if self.app.pargs.phpmyadmin:
                if not os.path.isdir('/var/www/22222/htdocs/db/pma'):
                    Log.debug(self, "Setting packages variable "
                              "for phpMyAdmin ")
                    self.app.pargs.composer = True
                    packages = packages + [["https://github.com/phpmyadmin/"
                                            "phpmyadmin/archive/STABLE.tar.gz",
                                            "/var/lib/wo/tmp/pma.tar.gz",
                                            "phpMyAdmin"]]
                else:
                    Log.debug(self, "phpMyAdmin already installed")
                    Log.info(self, "phpMyAdmin already installed")

            # Composer
            if self.app.pargs.composer:
                if not os.path.isfile('/usr/local/bin/composer'):
                    Log.debug(self, "Setting packages variable for Composer ")
                    packages = packages + [["https://getcomposer.org/"
                                            "installer",
                                            "/var/lib/wo/tmp/composer-install",
                                            "Composer"]]
                else:
                    Log.debug(self, "Composer already installed")
                    Log.info(self, "Composer already installed")

            # PHPREDISADMIN
            if self.app.pargs.phpredisadmin:
                if not os.path.isdir('/var/www/22222/htdocs/'
                                     'cache/redis/phpRedisAdmin'):
                    Log.debug(
                        self, "Setting packages variable for phpRedisAdmin")
                    self.app.pargs.composer = True
                    packages = packages + [["https://github.com/"
                                            "erikdubbelboer/"
                                            "phpRedisAdmin/archive"
                                            "/v1.11.3.tar.gz",
                                            "/var/lib/wo/tmp/pra.tar.gz",
                                            "phpRedisAdmin"]]
                else:
                    Log.debug(self, "phpRedisAdmin already installed")
                    Log.info(self, "phpRedisAdmin already installed")

            # ADMINER
            if self.app.pargs.adminer:
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

            # Netdata
            if self.app.pargs.netdata:
                Log.debug(self, "Setting packages variable for Netdata")
                if not os.path.exists('/opt/netdata'):
                    packages = packages + [['https://my-netdata.io/'
                                            'kickstart-static64.sh',
                                            '/var/lib/wo/tmp/kickstart.sh',
                                            'Netdata']]
                else:
                    Log.debug(self, "Netdata already installed")
                    Log.info(self, "Netdata already installed")

            # WordOps Dashboard
            if self.app.pargs.dashboard:
                if not os.path.isfile('/var/www/22222/htdocs/index.php'):
                    Log.debug(
                        self, "Setting packages variable for WO-Dashboard")
                    packages = packages + \
                        [["https://github.com/WordOps/"
                          "wordops-dashboard/releases/"
                          "download/v1.0/wo-dashboard.tar.gz",
                          "/var/lib/wo/tmp/wo-dashboard.tar.gz",
                          "WordOps Dashboard"],
                         ["https://github.com/soerennb/"
                          "extplorer/archive/v{0}.tar.gz"
                          .format(WOVariables.wo_extplorer),
                            "/var/lib/wo/tmp/extplorer.tar.gz",
                            "eXtplorer"]]
                else:
                    Log.debug(self, "WordOps dashboard already installed")
                    Log.info(self, "WordOps dashboard already installed")

            # UTILS
            if self.app.pargs.utils:
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
                                       ["https://gist.github.com/ck-on/4959032"
                                        "/raw/0b871b345fd6cfcd6d2be030c1f33d1"
                                        "ad6a475cb/ocp.php",
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
                                        'Anemometer']
                                       ]
        except Exception as e:
            Log.debug(self, "{0}".format(e))

        if (apt_packages) or (packages):
            Log.debug(self, "Calling pre_pref")
            pre_pref(self, apt_packages)
            if (apt_packages):
                meminfo = (os.popen('cat /proc/meminfo '
                                    '| grep MemTotal').read()).split(":")
                memsplit = re.split(" kB", meminfo[1])
                wo_mem = int(memsplit[0])
                if (wo_mem < 4000000):
                    WOSwap.add(self)
                Log.info(self, "Updating apt-cache, please wait...")
                WOAptGet.update(self)
                Log.info(self, "Installing packages, please wait...")
                WOAptGet.install(self, apt_packages)
            if (packages):
                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)
            Log.debug(self, "Calling post_pref")
            post_pref(self, apt_packages, packages)
            if 'redis-server' in apt_packages:
                # set redis.conf parameter
                # set maxmemory 10% for ram below 512MB and 20% for others
                # set maxmemory-policy allkeys-lru
                # enable systemd service
                Log.debug(self, "Enabling redis systemd service")
                WOShellExec.cmd_exec(self, "systemctl enable redis-server")
                if os.path.isfile("/etc/redis/redis.conf"):
                    wo_ram = psutil.virtual_memory().total / (1024 * 1024)
                    if wo_ram < 1024:
                        Log.debug(self, "Setting maxmemory variable to "
                                  "{0} in redis.conf"
                                  .format(int(wo_ram*1024*1024*0.1)))
                        WOFileUtils.searchreplace(self,
                                                  "/etc/redis/redis.conf",
                                                  "# maxmemory <bytes>",
                                                  "maxmemory {0}"
                                                  .format
                                                  (int(wo_ram*1024*1024*0.1)))
                        Log.debug(
                            self, "Setting maxmemory-policy variable to "
                            "allkeys-lru in redis.conf")
                        WOFileUtils.searchreplace(self,
                                                  "/etc/redis/redis.conf",
                                                  "# maxmemory-policy "
                                                  "noeviction",
                                                  "maxmemory-policy "
                                                  "allkeys-lru")
                        Log.debug(
                            self, "Setting tcp-backlog variable to "
                            "in redis.conf")
                        WOFileUtils.searchreplace(self,
                                                  "/etc/redis/redis.conf",
                                                  "tcp-backlog 511",
                                                  "tcp-backlog 32768")

                        WOService.restart_service(self, 'redis-server')
                    else:
                        Log.debug(self, "Setting maxmemory variable to {0} "
                                  "in redis.conf"
                                  .format(int(wo_ram*1024*1024*0.2)))
                        WOFileUtils.searchreplace(self,
                                                  "/etc/redis/redis.conf",
                                                  "# maxmemory <bytes>",
                                                  "maxmemory {0}"
                                                  .format
                                                  (int(wo_ram*1024*1024*0.1)))
                        Log.debug(
                            self, "Setting maxmemory-policy variable "
                            "to allkeys-lru in redis.conf")
                        WOFileUtils.searchreplace(self,
                                                  "/etc/redis/redis.conf",
                                                  "# maxmemory-policy "
                                                  "noeviction",
                                                  "maxmemory-policy "
                                                  "allkeys-lru")
                        WOService.restart_service(self, 'redis-server')

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

        if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
            (not self.app.pargs.nginx) and (not self.app.pargs.php) and
            (not self.app.pargs.php73) and (not self.app.pargs.mysql) and
            (not self.app.pargs.wpcli) and (not self.app.pargs.phpmyadmin) and
            (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
            (not self.app.pargs.composer) and (not self.app.pargs.netdata) and
            (not self.app.pargs.fail2ban) and (not self.app.pargs.proftpd) and
            (not self.app.pargs.security) and
            (not self.app.pargs.all) and (not self.app.pargs.redis) and
                (not self.app.pargs.phpredisadmin)):
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.security = True

        if self.app.pargs.all:
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.php73 = True

        if self.app.pargs.web:
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True
            self.app.pargs.wpcli = True

        if self.app.pargs.admin:
            self.app.pargs.adminer = True
            self.app.pargs.phpmyadmin = True
            self.app.pargs.composer = True
            self.app.pargs.utils = True
            self.app.pargs.netdata = True
            self.app.pargs.dashboard = True
            self.app.pargs.phpredisadmin = True

        if self.app.pargs.security:
            self.app.pargs.fail2ban = True

        # NGINX
        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Removing apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx
            else:
                Log.error(self, "Cannot Remove! Nginx Stable "
                          "version not found.")
        # PHP 7.2
        if self.app.pargs.php:
            Log.debug(self, "Removing apt_packages variable of PHP")
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php
            else:
                Log.error(self, "PHP 7.2 not found")

        # PHP7.3
        if self.app.pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php73 + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php73
            else:
                Log.error(self, "PHP 7.3 not found")

        # REDIS
        if self.app.pargs.redis:
            Log.debug(self, "Remove apt_packages variable of Redis")
            apt_packages = apt_packages + WOVariables.wo_redis

        # MariaDB
        if self.app.pargs.mysql:
            Log.debug(self, "Removing apt_packages variable of MySQL")
            apt_packages = apt_packages + WOVariables.wo_mysql
            packages = packages + ['/usr/bin/mysqltuner']

        # fail2ban
        if self.app.pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                Log.debug(self, "Remove apt_packages variable of Fail2ban")
                apt_packages = apt_packages + WOVariables.wo_fail2ban
            else:
                Log.error(self, "Fail2ban not found")

        # proftpd
        if self.app.pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                Log.debug(self, "Remove apt_packages variable for ProFTPd")
                apt_packages = apt_packages + ["proftpd-basic"]
            else:
                Log.error(self, "ProFTPd not found")

        # WPCLI
        if self.app.pargs.wpcli:
            Log.debug(self, "Removing package variable of WPCLI ")
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + ['/usr/local/bin/wp']
            else:
                Log.warn(self, "WP-CLI is not installed with WordOps")
        # PHPMYADMIN
        if self.app.pargs.phpmyadmin:
            Log.debug(self, "Removing package variable of phpMyAdmin ")
            packages = packages + ['{0}22222/htdocs/db/pma'
                                   .format(WOVariables.wo_webroot)]
        # Composer
        if self.app.pargs.composer:
            Log.debug(self, "Removing package variable of Composer ")
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + ['/usr/local/bin/composer']
            else:
                Log.warn(self, "Composer is not installed with WordOps")

        # PHPREDISADMIN
        if self.app.pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            if os.path.isdir('{0}22222/htdocs/cache/redis'
                             .format(WOVariables.wo_webroot)):
                packages = packages + ['{0}22222/htdocs/'
                                       'cache/redis/phpRedisAdmin'
                                       .format(WOVariables.wo_webroot)]
        # ADMINER
        if self.app.pargs.adminer:
            Log.debug(self, "Removing package variable of Adminer ")
            packages = packages + ['{0}22222/htdocs/db/adminer'
                                   .format(WOVariables.wo_webroot)]
        if self.app.pargs.utils:
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

        if self.app.pargs.netdata:
            Log.debug(self, "Removing Netdata")
            if os.path.isfile('/opt/netdata/usr/'
                              'libexec/netdata-uninstaller.sh'):
                packages = packages + ['/var/lib/wo/tmp/kickstart.sh']

        if self.app.pargs.dashboard:
            Log.debug(self, "Removing Wo-Dashboard")
            packages = packages + ['{0}22222/htdocs/assets/'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/index.php'
                                   .format(WOVariables.wo_webroot)]

        if (packages) or (apt_packages):
            wo_prompt = input('Are you sure you to want to'
                              ' remove from server.'
                              '\nPackage configuration will remain'
                              ' on server after this operation.\n'
                              'Any answer other than '
                              '"yes" will be stop this'
                              ' operation :  ')

            if wo_prompt == 'YES' or wo_prompt == 'yes':

                if (set(["nginx-custom"]).issubset(set(apt_packages))):
                    WOService.stop_service(self, 'nginx')

                # Netdata uninstaller
                if (set(['/var/lib/wo/tmp/'
                         'kickstart.sh']).issubset(set(packages))):
                    WOShellExec.cmd_exec(self, "bash /opt/netdata/usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")

                if (packages):
                    WOFileUtils.remove(self, packages)
                    WOAptGet.auto_remove(self)

                if (apt_packages):
                    Log.debug(self, "Removing apt_packages")
                    Log.info(self, "Removing packages, please wait...")
                    WOAptGet.remove(self, apt_packages)
                    WOAptGet.auto_remove(self)

                Log.info(self, "Successfully removed packages")

    @expose(help="Purge packages")
    def purge(self):
        """Start purging of packages"""
        apt_packages = []
        packages = []

        # Default action for stack purge
        if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
            (not self.app.pargs.nginx) and (not self.app.pargs.php) and
            (not self.app.pargs.php73) and (not self.app.pargs.mysql) and
            (not self.app.pargs.wpcli) and (not self.app.pargs.phpmyadmin) and
            (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
            (not self.app.pargs.composer) and (not self.app.pargs.netdata) and
            (not self.app.pargs.fail2ban) and (not self.app.pargs.proftpd) and
            (not self.app.pargs.security) and
            (not self.app.pargs.all) and (not self.app.pargs.redis) and
                (not self.app.pargs.phpredisadmin)):
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.security = True

        if self.app.pargs.all:
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.php73 = True

        if self.app.pargs.web:
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True
            self.app.pargs.wpcli = True

        if self.app.pargs.admin:
            self.app.pargs.adminer = True
            self.app.pargs.phpmyadmin = True
            self.app.pargs.utils = True
            self.app.pargs.composer = True
            self.app.pargs.netdata = True
            self.app.pargs.dashboard = True
            self.app.pargs.phpredisadmin = True

        if self.app.pargs.security:
            self.app.pargs.fail2ban = True
        # NGINX
        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Purge apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx
            else:
                Log.error(self, "Cannot Purge! "
                          "Nginx Stable version not found.")

        # PHP
        if self.app.pargs.php:
            Log.debug(self, "Purge apt_packages variable PHP")
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.3-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php
            else:
                Log.error(self, "Cannot Purge PHP 7.2. not found.")

        # PHP 7.3
        if self.app.pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php73 + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php73

        # fail2ban
        if self.app.pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                Log.debug(self, "Purge apt_packages variable of Fail2ban")
                apt_packages = apt_packages + WOVariables.wo_fail2ban

        # proftpd
        if self.app.pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                Log.debug(self, "Purge apt_packages variable for ProFTPd")
                apt_packages = apt_packages + ["proftpd-basic"]

        # WP-CLI
        if self.app.pargs.wpcli:
            Log.debug(self, "Purge package variable WPCLI")
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + ['/usr/local/bin/wp']
            else:
                Log.warn(self, "WP-CLI is not installed with WordOps")

        # PHPMYADMIN
        if self.app.pargs.phpmyadmin:
            packages = packages + ['{0}22222/htdocs/db/pma'.
                                   format(WOVariables.wo_webroot)]
            Log.debug(self, "Purge package variable phpMyAdmin")

        # Composer
        if self.app.pargs.composer:
            Log.debug(self, "Removing package variable of Composer ")
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + ['/usr/local/bin/composer']
            else:
                Log.warn(self, "Composer is not installed with WordOps")

        # PHPREDISADMIN
        if self.app.pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            if os.path.isdir('{0}22222/htdocs/cache/redis'
                             .format(WOVariables.wo_webroot)):
                packages = packages + ['{0}22222/htdocs/'
                                       'cache/redis/phpRedisAdmin'
                                       .format(WOVariables.wo_webroot)]
        # Adminer
        if self.app.pargs.adminer:
            Log.debug(self, "Purge  package variable Adminer")
            packages = packages + ['{0}22222/htdocs/db/adminer'
                                   .format(WOVariables.wo_webroot)]
        # utils
        if self.app.pargs.utils:
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

        if self.app.pargs.netdata:
            Log.debug(self, "Removing Netdata")
            if os.path.isfile('/opt/netdata/usr/'
                              'libexec/netdata-uninstaller.sh'):
                packages = packages + ['/var/lib/wo/tmp/kickstart.sh']

        if self.app.pargs.dashboard:
            Log.debug(self, "Removing Wo-Dashboard")
            packages = packages + ['{0}22222/htdocs/assets/'
                                   .format(WOVariables.wo_webroot),
                                   '{0}22222/htdocs/index.php'
                                   .format(WOVariables.wo_webroot)]

        if (packages) or (apt_packages):
            wo_prompt = input('Are you sure you to want to purge '
                              'from server '
                              'along with their configuration'
                              ' packages,\nAny answer other than '
                              '"yes" will be stop this '
                              'operation :')

            if wo_prompt == 'YES' or wo_prompt == 'yes':

                if (set(["nginx-custom"]).issubset(set(apt_packages))):
                    WOService.stop_service(self, 'nginx')

                # Netdata uninstaller
                if (set(['/var/lib/wo/tmp/'
                         'kickstart.sh']).issubset(set(packages))):
                    WOShellExec.cmd_exec(self, "bash /opt/netdata/usr/"
                                         "libexec/netdata-"
                                         "uninstaller.sh -y -f")

                if (set(["fail2ban"]).issubset(set(apt_packages))):
                    WOService.stop_service(self, 'fail2ban')

                if (apt_packages):
                    Log.info(self, "Purging packages, please wait...")
                    WOAptGet.remove(self, apt_packages, purge=True)
                    WOAptGet.auto_remove(self)

                if (packages):
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
