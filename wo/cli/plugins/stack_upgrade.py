import os
import shutil

from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.apt_repo import WORepo
from wo.core.aptget import WOAptGet
from wo.core.download import WODownload
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVariables
from wo.cli.plugins.stack_pref import post_pref


class WOStackUpgradeController(CementBaseController):
    class Meta:
        label = 'upgrade'
        stacked_on = 'stack'
        stacked_type = 'nested'
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
                dict(help='Upgrade PHP stack', action='store_true')),
            (['--mysql'],
                dict(help='Upgrade MySQL stack', action='store_true')),
            (['--wpcli'],
                dict(help='Upgrade WPCLI', action='store_true')),
            (['--redis'],
                dict(help='Upgrade Redis', action='store_true')),
            (['--netdata'],
                dict(help='Upgrade Netdata', action='store_true')),
            (['--composer'],
             dict(help='Upgrade Composer', action='store_true')),
            (['--phpmyadmin'],
             dict(help='Upgrade phpMyAdmin', action='store_true')),
            (['--no-prompt'],
                dict(help="Upgrade Packages without any prompt",
                     action='store_true')),
        ]

    @expose(hide=True)
    def upgrade_php56(self):
        if WOVariables.wo_distro == "ubuntu":
            if os.path.isfile("/etc/apt/sources.list.d/ondrej-php5-5_6-{0}."
                              "list".format(WOVariables.wo_platform_codename)):
                Log.error(self, "Unable to find PHP 5.5")
        else:
            if not(os.path.isfile(WOVariables.wo_repo_file_path) and
                   WOFileUtils.grep(self, WOVariables.wo_repo_file_path,
                                    "php55")):
                Log.error(self, "Unable to find PHP 5.5")

        Log.info(self, "During PHP update process non nginx-cached"
                 " parts of your site may remain down.")

        # Check prompt
        if (not self.app.pargs.no_prompt):
            start_upgrade = input("Do you want to continue:[y/N]")
            if start_upgrade != "Y" and start_upgrade != "y":
                Log.error(self, "Not starting PHP package update")

        if WOVariables.wo_distro == "ubuntu":
            WORepo.remove(self, ppa="ppa:ondrej/php5")
            WORepo.add(self, ppa=WOVariables.wo_php_repo)

        Log.info(self, "Updating apt-cache, please wait...")
        WOAptGet.update(self)
        Log.info(self, "Installing packages, please wait ...")
        WOAptGet.install(self, WOVariables.wo_php +
                         WOVariables.wo_php_extra)

    @expose(hide=True)
    def default(self):
        # All package update
        apt_packages = []
        packages = []
        empty_packages = []

        if ((not self.app.pargs.web) and (not self.app.pargs.nginx) and
            (not self.app.pargs.php) and (not self.app.pargs.mysql) and
            (not self.app.pargs.all) and (not self.app.pargs.wpcli) and
            (not self.app.pargs.netdata) and (not self.app.pargs.composer) and
            (not self.app.pargs.phpmyadmin) and
                (not self.app.pargs.redis)):
            self.app.pargs.web = True

        if self.app.pargs.all:
            self.app.pargs.web = True

        if self.app.pargs.web:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                self.app.pargs.nginx = True
            else:
                Log.info(self, "Nginx is not already installed")
            self.app.pargs.php = True
            self.app.pargs.mysql = True
            self.app.pargs.wpcli = True
            self.app.pargs.netdata = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                apt_packages = apt_packages + WOVariables.wo_nginx
            else:
                Log.info(self, "Nginx Stable is not already installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                    apt_packages = apt_packages + WOVariables.wo_php + \
                        WOVariables.wo_php_extra
                else:
                    apt_packages = apt_packages + WOVariables.wo_php
            else:
                Log.info(self, "PHP 7.2 is not installed")

        if self.app.pargs.mysql:
            if WOAptGet.is_installed(self, 'mariadb-server'):
                apt_packages = apt_packages + WOVariables.wo_mysql
            else:
                Log.info(self, "MariaDB is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                apt_packages = apt_packages + WOVariables.wo_redis
            else:
                Log.info(self, "Redis is not installed")

        if self.app.pargs.wpcli:
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + [["https://github.com/wp-cli/wp-cli/"
                                        "releases/download/v{0}/"
                                        "wp-cli-{0}.phar"
                                        "".format(WOVariables.wo_wp_cli),
                                        "/usr/local/bin/wp",
                                        "WP-CLI"]]
            else:
                Log.info(self, "WPCLI is not installed with WordOps")

        if self.app.pargs.netdata:
            if os.path.isdir('/opt/netdata'):
                packages = packages + [['https://my-netdata.io/'
                                        'kickstart-static64.sh',
                                        '/var/lib/wo/tmp/kickstart.sh',
                                        'Netdata']]
        if self.app.pargs.phpmyadmin:
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

        if self.app.pargs.composer:
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + [["https://getcomposer.org/installer",
                                        "/var/lib/wo/tmp/composer-install",
                                        "Composer"]]
            else:
                Log.error(self, "Composer isn't installed")

        if len(packages) or len(apt_packages):

            Log.info(self, "During package update process non nginx-cached"
                     " parts of your site may remain down")
            # Check prompt
            if (not self.app.pargs.no_prompt):
                start_upgrade = input("Do you want to continue:[y/N]")
                if start_upgrade != "Y" and start_upgrade != "y":
                    Log.error(self, "Not starting package update")

            Log.info(self, "Updating packages, please wait...")
            if len(apt_packages):
                # apt-get update
                WOAptGet.update(self)
                # Update packages
                WOAptGet.install(self, apt_packages)
                if set(WOVariables.wo_php).issubset(set(apt_packages)):
                    WOFileUtils.rm(self, "/etc/php/7.2/fpm/pool.d/www.conf")
                    WOFileUtils.rm(self, "/etc/php/7.2/fpm/"
                                   "pool.d/www-two.conf")
                post_pref(self, apt_packages, empty_packages)
                # Post Actions after package updates
                if (set(WOVariables.wo_nginx).issubset(set(apt_packages))):
                    WOService.restart_service(self, 'nginx')
                if set(WOVariables.wo_php).issubset(set(apt_packages)):
                    WOService.restart_service(self, 'php7.2-fpm')
                if set(WOVariables.wo_mysql).issubset(set(apt_packages)):
                    WOService.restart_service(self, 'mysql')
                if set(WOVariables.wo_redis).issubset(set(apt_packages)):
                    WOService.restart_service(self, 'redis-server')

            if len(packages):
                if self.app.pargs.wpcli:
                    WOFileUtils.remove(self, ['/usr/local/bin/wp'])

                if self.app.pargs.netdata:
                    WOFileUtils.remove(self, ['/var/lib/wo/tmp/kickstart.sh'])

                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)

                if self.app.pargs.wpcli:
                    WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

                if self.app.pargs.netdata:
                    Log.info(self, "Upgrading Netdata, please wait...")
                    WOShellExec.cmd_exec(self, "/bin/bash /var/lib/wo/tmp/"
                                         "kickstart.sh "
                                         "--dont-wait")

                if self.app.pargs.composer:
                    Log.info(self, "Upgrading Composer, please wait...")
                    WOShellExec.cmd_exec(self, "php -q /var/lib/wo"
                                         "/tmp/composer-install "
                                         "--install-dir=/var/lib/wo/tmp/")
                    shutil.copyfile('/var/lib/wo/tmp/composer.phar',
                                    '/usr/local/bin/composer')
                    WOFileUtils.chmod(self, "/usr/local/bin/composer", 0o775)

                if self.app.pargs.phpmyadmin:
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

            Log.info(self, "Successfully updated packages")
        else:
            self.app.args.print_help()
