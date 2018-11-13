from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.logging import Log
from wo.core.variables import WOVariables
from wo.core.aptget import WOAptGet
from wo.core.apt_repo import WORepo
from wo.core.services import WOService
from wo.core.fileutils import WOFileUtils
from wo.core.shellexec import WOShellExec
from wo.core.git import WOGit
from wo.core.download import WODownload
import configparser
import os


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
            (['--nginxmainline'],
                dict(help='Upgrade Nginx Mainline stack', action='store_true')),
            (['--php'],
                dict(help='Upgrade PHP stack', action='store_true')),
            (['--mysql'],
                dict(help='Upgrade MySQL stack', action='store_true')),
            (['--hhvm'],
                dict(help='Upgrade HHVM stack', action='store_true')),
            (['--wpcli'],
                dict(help='Upgrade WPCLI', action='store_true')),
            (['--redis'],
                dict(help='Upgrade Redis', action='store_true')),
            (['--php56'],
                dict(help="Upgrade to PHP5.6 from PHP5.5",
                     action='store_true')),
            (['--no-prompt'],
                dict(help="Upgrade Packages without any prompt",
                     action='store_true')),
            ]

    @expose(hide=True)
    def upgrade_php56(self):
        if WOVariables.wo_platform_distro == "ubuntu":
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

        if WOVariables.wo_platform_distro == "ubuntu":
            WORepo.remove(self, ppa="ppa:ondrej/php5")
            WORepo.add(self, ppa=WOVariables.wo_php_repo)
        else:
            WOAptGet.remove(self, ["php5-xdebug"])
            WOFileUtils.searchreplace(self, WOVariables.wo_repo_file_path,
                                      "php55", "php56")

        Log.info(self, "Updating apt-cache, please wait...")
        WOAptGet.update(self)
        Log.info(self, "Installing packages, please wait ...")
        if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
            WOAptGet.install(self, WOVariables.wo_php5_6 + WOVariables.wo_php_extra)
        else:
            WOAptGet.install(self, WOVariables.wo_php)

        if WOVariables.wo_platform_distro == "debian":
            WOShellExec.cmd_exec(self, "pecl install xdebug")

            with open("/etc/php5/mods-available/xdebug.ini",
                      encoding='utf-8', mode='a') as myfile:
                myfile.write(";zend_extension=/usr/lib/php5/20131226/"
                             "xdebug.so\n")

            WOFileUtils.create_symlink(self, ["/etc/php5/mods-available/"
                                       "xdebug.ini", "/etc/php5/fpm/conf.d"
                                                     "/20-xedbug.ini"])

        Log.info(self, "Successfully upgraded from PHP 5.5 to PHP 5.6")

    @expose(hide=True)
    def default(self):
        # All package update
        if ((not self.app.pargs.php56)):

            apt_packages = []
            packages = []

            if ((not self.app.pargs.web) and (not self.app.pargs.nginx) and
               (not self.app.pargs.php) and (not self.app.pargs.mysql) and
               (not self.app.pargs.hhvm) and (not self.app.pargs.all) and 
               (not self.app.pargs.wpcli) and (not self.app.pargs.redis) and 
               (not self.app.pargs.nginxmainline)):
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

            if self.app.pargs.nginx :
                if WOAptGet.is_installed(self, 'nginx-custom'):
                    apt_packages = apt_packages + WOVariables.wo_nginx
                else:
                    Log.info(self, "Nginx Stable is not already installed")

            if self.app.pargs.php:
                if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                    if WOAptGet.is_installed(self, 'php5-fpm'):
                        apt_packages = apt_packages + WOVariables.wo_php
                    else:
                        Log.info(self, "PHP is not installed")
                    if WOAptGet.is_installed(self, 'php7.0-fpm'):
                        apt_packages = apt_packages + WOVariables.wo_php7_0
                else:
                    if WOAptGet.is_installed(self, 'php5.6-fpm'):
                        apt_packages = apt_packages + WOVariables.wo_php5_6 + WOVariables.wo_php_extra
                    else:
                        Log.info(self, "PHP 5.6 is not installed")
                    if WOAptGet.is_installed(self, 'php7.0-fpm'):
                        apt_packages = apt_packages + WOVariables.wo_php7_0 + WOVariables.wo_php_extra
                    else:
                        Log.info(self, "PHP 7.0 is not installed")

            if self.app.pargs.hhvm:
                if WOAptGet.is_installed(self, 'hhvm'):
                    apt_packages = apt_packages + WOVariables.wo_hhvm
                else:
                    Log.info(self, "HHVM is not installed")

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
                if os.path.isfile('/usr/bin/wp'):
                    packages = packages + [["https://github.com/wp-cli/wp-cli/"
                                            "releases/download/v{0}/"
                                            "wp-cli-{0}.phar"
                                            "".format(WOVariables.wo_wp_cli),
                                            "/usr/bin/wp",
                                            "WP-CLI"]]
                else:
                    Log.info(self, "WPCLI is not installed with WordOps")

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

                    # Post Actions after package updates
                    if (set(WOVariables.wo_nginx).issubset(set(apt_packages))):
                        WOService.restart_service(self, 'nginx')
                    if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                        if set(WOVariables.wo_php).issubset(set(apt_packages)):
                            WOService.restart_service(self, 'php5-fpm')
                    else:
                        if set(WOVariables.wo_php5_6).issubset(set(apt_packages)):
                            WOService.restart_service(self, 'php5.6-fpm')
                        if set(WOVariables.wo_php7_0).issubset(set(apt_packages)):
                            WOService.restart_service(self, 'php7.0-fpm')
                    if set(WOVariables.wo_hhvm).issubset(set(apt_packages)):
                        WOService.restart_service(self, 'hhvm')
                    if set(WOVariables.wo_mysql).issubset(set(apt_packages)):
                        WOService.restart_service(self, 'mysql')
                    if set(WOVariables.wo_redis).issubset(set(apt_packages)):
                        WOService.restart_service(self, 'redis-server')

                if len(packages):
                    if self.app.pargs.wpcli:
                        WOFileUtils.remove(self,['/usr/bin/wp'])

                    Log.debug(self, "Downloading following: {0}".format(packages))
                    WODownload.download(self, packages)

                    if self.app.pargs.wpcli:
                        WOFileUtils.chmod(self, "/usr/bin/wp", 0o775)

                Log.info(self, "Successfully updated packages")

        # PHP 5.6 to 5.6
        elif (self.app.pargs.php56):
            self.upgrade_php56()
        else:
            self.app.args.print_help()
