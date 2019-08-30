import os
import shutil

from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.aptget import WOAptGet
from wo.core.download import WODownload
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVariables
from wo.cli.plugins.stack_pref import pre_pref, post_pref


class WOStackUpgradeController(CementBaseController):
    class Meta:
        label = 'upgrade'
        stacked_on = 'stack'
        stacked_type = 'nested'
        exit_on_close = True
        description = ('Upgrade stack safely')
        arguments = [
            (['--all'],
                dict(help='Upgrade all stack', action='store_true')),
            (['--web'],
                dict(help='Upgrade web stack', action='store_true')),
            (['--admin'],
                dict(help='Upgrade admin tools stack', action='store_true')),
            (['--nginx'],
                dict(help='Upgrade Nginx stack', action='store_true')),
            (['--php'],
                dict(help='Upgrade PHP 7.2 stack', action='store_true')),
            (['--php73'],
             dict(help='Upgrade PHP 7.3 stack', action='store_true')),
            (['--mysql'],
                dict(help='Upgrade MySQL stack', action='store_true')),
            (['--wpcli'],
                dict(help='Upgrade WPCLI', action='store_true')),
            (['--redis'],
                dict(help='Upgrade Redis', action='store_true')),
            (['--netdata'],
                dict(help='Upgrade Netdata', action='store_true')),
            (['--dashboard'],
                dict(help='Upgrade WordOps Dashboard', action='store_true')),
            (['--composer'],
             dict(help='Upgrade Composer', action='store_true')),
            (['--phpmyadmin'],
             dict(help='Upgrade phpMyAdmin', action='store_true')),
            (['--no-prompt'],
                dict(help="Upgrade Packages without any prompt",
                     action='store_true')),
            (['--force'],
                dict(help="Force Packages upgrade without any prompt",
                     action='store_true')),
        ]

    @expose(hide=True)
    def default(self, disp_msg=False):
        # All package update
        apt_packages = []
        packages = []
        nginx_packages = []
        empty_packages = []
        self.msg = []
        pargs = self.app.pargs

        if ((not pargs.web) and (not pargs.nginx) and
            (not pargs.php) and (not pargs.php73) and
            (not pargs.mysql) and
            (not pargs.all) and (not pargs.wpcli) and
            (not pargs.netdata) and (not pargs.composer) and
            (not pargs.phpmyadmin) and (not pargs.dashboard) and
                (not pargs.redis)):
            pargs.web = True

        if pargs.all:
            pargs.web = True
            pargs.netdata = True
            pargs.composer = True
            pargs.dashboard = True
            pargs.phpmyadmin = True
            pargs.redis = True
            pargs.wpcli = True
            pargs.php73 = True

        if pargs.web:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                pargs.nginx = True
            else:
                Log.info(self, "Nginx is not already installed")
            pargs.php = True
            pargs.mysql = True
            pargs.wpcli = True

        if pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                apt_packages = apt_packages + WOVariables.wo_nginx
                nginx_packages = nginx_packages + WOVariables.wo_nginx
            else:
                Log.info(self, "Nginx Stable is not already installed")

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php
            else:
                Log.info(self, "PHP 7.2 is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                if not WOAptGet.is_installed(self, 'php7.2-fpm'):
                    apt_packages = apt_packages + WOVariables.wo_php73 + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php73
            else:
                Log.info(self, "PHP 7.3 is not installed")

        if pargs.mysql:
            if WOAptGet.is_installed(self, 'mariadb-server'):
                apt_packages = apt_packages + WOVariables.wo_mysql
            else:
                Log.info(self, "MariaDB is not installed")

        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                apt_packages = apt_packages + WOVariables.wo_redis
            else:
                Log.info(self, "Redis is not installed")

        if pargs.wpcli:
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + [["https://github.com/wp-cli/wp-cli/"
                                        "releases/download/v{0}/"
                                        "wp-cli-{0}.phar"
                                        "".format(WOVariables.wo_wp_cli),
                                        "/usr/local/bin/wp",
                                        "WP-CLI"]]
            else:
                Log.info(self, "WPCLI is not installed with WordOps")

        if pargs.netdata:
            if os.path.isdir('/opt/netdata'):
                packages = packages + [['https://my-netdata.io/'
                                        'kickstart-static64.sh',
                                        '/var/lib/wo/tmp/kickstart.sh',
                                        'Netdata']]

        if pargs.dashboard:
            if os.path.isfile('/var/www/22222/htdocs/index.php'):
                packages = packages + \
                    [["https://github.com/WordOps/wordops-dashboard/"
                      "releases/download/v{0}/wordops-dashboard.tar.gz"
                      .format(WOVariables.wo_dashboard),
                      "/var/lib/wo/tmp/wo-dashboard.tar.gz",
                      "WordOps Dashboard"]]

        if pargs.phpmyadmin:
            if os.path.isdir('/var/www/22222/htdocs/db/pma'):
                packages = packages + \
                    [["https://files.phpmyadmin.net"
                      "/phpMyAdmin/{0}/"
                      "phpMyAdmin-{0}-"
                      "all-languages"
                      ".tar.gz".format(WOVariables.wo_phpmyadmin),
                      "/var/lib/wo/tmp/pma.tar.gz",
                      "PHPMyAdmin"]]
            else:
                Log.error(self, "phpMyAdmin isn't installed")

        if pargs.composer:
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + [["https://getcomposer.org/installer",
                                        "/var/lib/wo/tmp/composer-install",
                                        "Composer"]]
            else:
                Log.error(self, "Composer isn't installed")
        if len(apt_packages) or len(packages):
            if len(apt_packages):
                Log.info(self, "Your site may be down for few seconds if "
                         "you are upgrading Nginx, PHP-FPM, MariaDB or Redis")
                # Check prompt
                if ((not pargs.no_prompt) and (not pargs.force)):
                    start_upgrade = input("Do you want to continue:[y/N]")
                    if start_upgrade != "Y" and start_upgrade != "y":
                        Log.error(self, "Not starting package update")
                Log.info(self, "Updating APT packages, please wait...")
                if set(WOVariables.wo_nginx).issubset(set(apt_packages)):
                    pre_pref(self, ["nginx-custom", "nginx-wo"])
                # apt-get update
                WOAptGet.update(self)
                if set(WOVariables.wo_php).issubset(set(apt_packages)):
                    WOAptGet.remove(self, ['php7.2-fpm'],
                                    auto=False, purge=True)
                if set(WOVariables.wo_php73).issubset(set(apt_packages)):
                    WOAptGet.remove(self, ['php7.3-fpm'],
                                    auto=False, purge=True)
                # Update packages
                WOAptGet.install(self, apt_packages)
                post_pref(self, apt_packages, empty_packages, True)
                # Post Actions after package updates

            if len(packages):
                if pargs.wpcli:
                    WOFileUtils.rm(self, '/usr/local/bin/wp')

                if pargs.netdata:
                    WOFileUtils.rm(self, '/var/lib/wo/tmp/kickstart.sh')

                if pargs.dashboard:
                    WOFileUtils.rm(self, '/var/www/22222/htdocs/index.php')

                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)

                if pargs.wpcli:
                    WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

                if pargs.netdata:
                    Log.info(self, "Upgrading Netdata, please wait...")
                    WOShellExec.cmd_exec(self, "/bin/bash /var/lib/wo/tmp/"
                                         "kickstart.sh "
                                         "--dont-wait")

                if pargs.dashboard:
                    Log.debug(self, "Extracting wo-dashboard.tar.gz "
                              "to location {0}22222/htdocs/"
                              .format(WOVariables.wo_webroot))
                    WOExtract.extract(self, '/var/lib/wo/tmp/'
                                      'wo-dashboard.tar.gz',
                                      '{0}22222/htdocs'
                                      .format(WOVariables.wo_webroot))
                    WOFileUtils.chown(self, "{0}22222/htdocs"
                                      .format(WOVariables.wo_webroot),
                                      WOVariables.wo_php_user,
                                      WOVariables.wo_php_user, recursive=True)

                if pargs.composer:
                    Log.info(self, "Upgrading Composer, please wait...")
                    WOShellExec.cmd_exec(self, "php -q /var/lib/wo"
                                         "/tmp/composer-install "
                                         "--install-dir=/var/lib/wo/tmp/")
                    shutil.copyfile('/var/lib/wo/tmp/composer.phar',
                                    '/usr/local/bin/composer')
                    WOFileUtils.chmod(self, "/usr/local/bin/composer", 0o775)

                if pargs.phpmyadmin:
                    Log.info(self, "Upgrading phpMyAdmin, please wait...")
                    WOExtract.extract(self, '/var/lib/wo/tmp/pma.tar.gz',
                                      '/var/lib/wo/tmp/')
                    shutil.copyfile(('{0}22222/htdocs/db/pma'
                                     '/config.inc.php'
                                     .format(WOVariables.wo_webroot)),
                                    ('/var/lib/wo/tmp/phpMyAdmin-{0}'
                                     '-all-languages/config.inc.php'
                                     .format(WOVariables.wo_phpmyadmin))
                                    )
                    WOFileUtils.rm(self, '{0}22222/htdocs/db/pma'
                                   .format(WOVariables.wo_webroot))
                    shutil.move('/var/lib/wo/tmp/phpMyAdmin-{0}'
                                '-all-languages/'
                                .format(WOVariables.wo_phpmyadmin),
                                '{0}22222/htdocs/db/pma/'
                                .format(WOVariables.wo_webroot))
                    WOFileUtils.chown(self, "{0}22222/htdocs"
                                      .format(WOVariables.wo_webroot),
                                      WOVariables.wo_php_user,
                                      WOVariables.wo_php_user, recursive=True)

            Log.info(self, "Successfully updated packages")
        else:
            self.app.args.print_help()
