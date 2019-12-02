import os
import shutil

from cement.core.controller import CementBaseController, expose

from wo.cli.plugins.stack_pref import post_pref, pre_pref, pre_stack
from wo.core.aptget import WOAptGet
from wo.core.download import WODownload
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


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
                dict(help='Upgrade PHP 7.2 stack', action='store_true')),
            (['--php72'],
                dict(help='Upgrade PHP 7.2 stack', action='store_true')),
            (['--php73'],
             dict(help='Upgrade PHP 7.3 stack', action='store_true')),
            (['--php74'],
             dict(help='Upgrade PHP 7.4 stack', action='store_true')),
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
            (['--mysqltuner'],
             dict(help='Upgrade Composer', action='store_true')),
            (['--phpmyadmin'],
             dict(help='Upgrade phpMyAdmin', action='store_true')),
            (['--adminer'],
             dict(help='Upgrade Adminer', action='store_true')),
            (['--ngxblocker'],
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
        self.msg = []
        pargs = self.app.pargs
        if ((not pargs.web) and (not pargs.nginx) and
            (not pargs.php) and
            (not pargs.php72) and (not pargs.php73) and
            (not pargs.php74) and
            (not pargs.mysql) and (not pargs.ngxblocker) and
            (not pargs.all) and (not pargs.wpcli) and
            (not pargs.netdata) and (not pargs.composer) and
            (not pargs.phpmyadmin) and (not pargs.adminer) and
            (not pargs.dashboard) and (not pargs.mysqltuner) and
                (not pargs.redis)):
            pargs.web = True
            pargs.admin = True

        if pargs.php:
            pargs.php72 = True

        if pargs.all:
            pargs.web = True
            pargs.admin = True
            pargs.redis = True
            pargs.ngxblocker = True

        if pargs.web:
            pargs.nginx = True
            pargs.php72 = True
            pargs.php73 = True
            pargs.php74 = True
            pargs.mysql = True
            pargs.wpcli = True

        if pargs.admin:
            pargs.netdata = True
            pargs.composer = True
            pargs.dashboard = True
            pargs.phpmyadmin = True
            pargs.wpcli = True
            pargs.adminer = True
            pargs.mysqltuner = True

        # nginx
        if pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                apt_packages = apt_packages + WOVar.wo_nginx
            else:
                if os.path.isfile('/usr/sbin/nginx'):
                    Log.info(self, "Updating Nginx templates")
                    post_pref(self, WOVar.wo_nginx, [])
                else:
                    Log.info(self, "Nginx Stable is not already installed")

        # php 7.2
        if pargs.php72:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                apt_packages = apt_packages + WOVar.wo_php72 + \
                    WOVar.wo_php_extra

        # php 7.3
        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                apt_packages = apt_packages + WOVar.wo_php73 + \
                    WOVar.wo_php_extra

        # php 7.4
        if pargs.php74:
            if WOAptGet.is_installed(self, 'php7.4-fpm'):
                apt_packages = apt_packages + WOVar.wo_php74 + \
                    WOVar.wo_php_extra

        # mysql
        if pargs.mysql:
            if WOShellExec.cmd_exec(self, 'mysqladmin ping'):
                apt_packages = apt_packages + ['mariadb-server']

        # redis
        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                apt_packages = apt_packages + ['redis-server']

        # wp-cli
        if pargs.wpcli:
            if os.path.isfile('/usr/local/bin/wp'):
                packages = packages + [[
                    "https://github.com/wp-cli/wp-cli/"
                    "releases/download/v{0}/"
                    "wp-cli-{0}.phar".format(WOVar.wo_wp_cli),
                    "/usr/local/bin/wp",
                    "WP-CLI"]]
            else:
                Log.info(self, "WPCLI is not installed with WordOps")

        # netdata
        if pargs.netdata:
            # detect static binaries install
            if os.path.isdir('/opt/netdata'):
                packages = packages + [[
                    'https://my-netdata.io/kickstart-static64.sh',
                    '/var/lib/wo/tmp/kickstart.sh', 'Netdata']]
            # detect install from source
            elif os.path.isdir('/etc/netdata'):
                packages = packages + [[
                    'https://my-netdata.io/kickstart.sh',
                    '/var/lib/wo/tmp/kickstart.sh', 'Netdata']]
            else:
                Log.info(self, 'Netdata is not installed')

        # wordops dashboard
        if pargs.dashboard:
            if (os.path.isfile('/var/www/22222/htdocs/index.php') or
                    os.path.isfile('/var/www/22222/htdocs/index.html')):
                packages = packages + [[
                    "https://github.com/WordOps/wordops-dashboard/"
                    "releases/download/v{0}/wordops-dashboard.tar.gz"
                    .format(WOVar.wo_dashboard),
                    "/var/lib/wo/tmp/wo-dashboard.tar.gz",
                    "WordOps Dashboard"]]
            else:
                Log.info(self, 'WordOps dashboard is not installed')

        # phpmyadmin
        if pargs.phpmyadmin:
            if os.path.isdir('/var/www/22222/htdocs/db/pma'):
                packages = packages + [[
                    "https://files.phpmyadmin.net"
                    "/phpMyAdmin/{0}/phpMyAdmin-{0}-"
                    "all-languages.tar.gz"
                    .format(WOVar.wo_phpmyadmin),
                    "/var/lib/wo/tmp/pma.tar.gz",
                    "PHPMyAdmin"]]
            else:
                Log.info(self, "phpMyAdmin isn't installed")

        # adminer
        if pargs.adminer:
            if os.path.isfile("{0}22222/htdocs/db/"
                              "adminer/index.php"
                              .format(WOVar.wo_webroot)):
                Log.debug(self, "Setting packages variable for Adminer ")
                packages = packages + [[
                    "https://github.com/vrana/adminer/"
                    "releases/download/v{0}"
                    "/adminer-{0}.php"
                    .format(WOVar.wo_adminer),
                    "{0}22222/"
                    "htdocs/db/adminer/index.php"
                    .format(WOVar.wo_webroot),
                    "Adminer"],
                    ["https://raw.githubusercontent.com"
                     "/vrana/adminer/master/designs/"
                     "pepa-linha/adminer.css",
                     "{0}22222/"
                     "htdocs/db/adminer/adminer.css"
                     .format(WOVar.wo_webroot),
                     "Adminer theme"]]
            else:
                Log.debug(self, "Adminer isn't installed")
                Log.info(self, "Adminer isn't installed")

        # composer
        if pargs.composer:
            if os.path.isfile('/usr/local/bin/composer'):
                packages = packages + [[
                    "https://getcomposer.org/installer",
                    "/var/lib/wo/tmp/composer-install",
                    "Composer"]]
            else:
                Log.info(self, "Composer isn't installed")

        # mysqltuner
        if pargs.mysqltuner:
            if WOAptGet.is_exec(self, 'mysqltuner'):
                Log.debug(self, "Setting packages variable "
                          "for MySQLTuner ")
                packages = packages + [["https://raw."
                                        "githubusercontent.com/"
                                        "major/MySQLTuner-perl"
                                        "/master/mysqltuner.pl",
                                        "/usr/bin/mysqltuner",
                                        "MySQLTuner"]]

        # ngxblocker
        if pargs.ngxblocker:
            if os.path.exists('/usr/local/sbin/install-ngxblocker'):
                packages = packages + [[
                    'https://raw.githubusercontent.com/mitchellkrogza/'
                    'nginx-ultimate-bad-bot-blocker/master/update-ngxblocker',
                    '/usr/local/sbin/update-ngxblocker',
                    'ngxblocker'
                ]]
            else:
                Log.info(self, "ngxblocker is not installed")

        if ((not (apt_packages)) and (not(packages))):
            self.app.args.print_help()
        else:
            pre_stack(self)
            if (apt_packages):
                if (("php7.2-fpm" not in apt_packages) and
                        ("php7.3-fpm" not in apt_packages) and
                        ("php7.4-fpm" not in apt_packages) and
                        ("redis-server" not in apt_packages) and
                        ("nginx-custom" not in apt_packages) and
                        ("mariadb-server" not in apt_packages)):
                    pass
                else:
                    Log.info(
                        self, "Your sites may be down for few seconds if "
                        "you are upgrading Nginx, PHP-FPM, MariaDB or Redis")
                # Check prompt
                if ((not pargs.no_prompt) and (not pargs.force)):
                    start_upgrade = input("Do you want to continue:[y/N]")
                    if start_upgrade != "Y" and start_upgrade != "y":
                        Log.error(self, "Not starting package update")
                Log.wait(self, "Updating APT packages")
                # apt-get update
                WOAptGet.update(self)
                Log.valide(self, "Updating APT packages")

                # additional pre_pref
                if "nginx-custom" in apt_packages:
                    pre_pref(self, WOVar.wo_nginx)
                if "php7.2-fpm" in apt_packages:
                    WOAptGet.remove(self, ['php7.2-fpm'],
                                    auto=False, purge=True)
                if "php7.3-fpm" in apt_packages:
                    WOAptGet.remove(self, ['php7.3-fpm'],
                                    auto=False, purge=True)
                if "php7.4-fpm" in apt_packages:
                    WOAptGet.remove(self, ['php7.4-fpm'],
                                    auto=False, purge=True)
                # check if nginx upgrade is blocked
                if os.path.isfile(
                        '/etc/apt/preferences.d/nginx-block'):
                    post_pref(self, WOVar.wo_nginx, [], True)
                # upgrade packages
                WOAptGet.install(self, apt_packages)
                Log.wait(self, "Configuring APT Packages")
                post_pref(self, apt_packages, [], True)
                if "mariadb-server" in apt_packages:
                    WOShellExec.cmd_exec(self, 'mysql_upgrade')
                Log.valide(self, "Configuring APT Packages")
                # Post Actions after package updates

            if (packages):
                if WOAptGet.is_selected(self, 'WP-CLI', packages):
                    WOFileUtils.rm(self, '/usr/local/bin/wp')

                if WOAptGet.is_selected(self, 'Netdata', packages):
                    WOFileUtils.rm(self, '/var/lib/wo/tmp/kickstart.sh')

                if WOAptGet.is_selected(self, 'ngxblocker', packages):
                    WOFileUtils.rm(self, '/usr/local/sbin/update-ngxblocker')

                if WOAptGet.is_selected(self, 'WordOps Dashboard', packages):
                    if os.path.isfile('/var/www/22222/htdocs/index.php'):
                        WOFileUtils.rm(self, '/var/www/22222/htdocs/index.php')
                    if os.path.isfile('/var/www/22222/htdocs/index.html'):
                        WOFileUtils.rm(
                            self, '/var/www/22222/htdocs/index.html')

                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)

                if WOAptGet.is_selected(self, 'WP-CLI', packages):
                    WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

                if WOAptGet.is_selected(self, 'ngxblocker', packages):
                    WOFileUtils.chmod(
                        self, '/usr/local/sbin/update-ngxblocker', 0o775)
                    WOShellExec.cmd_exec(
                        self, '/usr/local/sbin/update-ngxblocker -nq')

                if WOAptGet.is_selected(self, 'MySQLTuner', packages):
                    WOFileUtils.chmod(self, "/usr/bin/mysqltuner", 0o775)
                    if os.path.exists('/usr/local/bin/mysqltuner'):
                        WOFileUtils.rm(self, '/usr/local/bin/mysqltuner')

                # Netdata
                if WOAptGet.is_selected(self, 'Netdata', packages):
                    Log.wait(self, "Upgrading Netdata")
                    # detect static binaries install
                    if os.path.isdir('/opt/netdata'):
                        if os.path.exists(
                            '/opt/netdata/usr/libexec/'
                                'netdata/netdata-updater.sh'):
                            WOShellExec.cmd_exec(
                                self, "bash /opt/netdata/usr/"
                                "libexec/netdata/netdata-"
                                "updater.sh")
                        else:
                            WOShellExec.cmd_exec(
                                self, "bash /var/lib/wo/tmp/kickstart.sh")
                    # detect install from source
                    elif os.path.isdir('/etc/netdata'):
                        if os.path.exists(
                                '/usr/libexec/netdata/netdata-updater.sh'):
                            WOShellExec.cmd_exec(
                                self,
                                'bash /usr/libexec/netdata/netdata-updater.sh')
                        else:
                            WOShellExec.cmd_exec(
                                self, "bash /var/lib/wo/tmp/kickstart.sh")
                    Log.valide(self, "Upgrading Netdata")

                if WOAptGet.is_selected(self, 'WordOps Dashboard', packages):
                    post_pref(
                        self, [], [["https://github.com/WordOps"
                                    "/wordops-dashboard/"
                                    "releases/download/v{0}/"
                                    "wordops-dashboard.tar.gz"
                                    .format(WOVar.wo_dashboard),
                                    "/var/lib/wo/tmp/wo-dashboard.tar.gz",
                                    "WordOps Dashboard"]])

                if WOAptGet.is_selected(self, 'Composer', packages):
                    Log.wait(self, "Upgrading Composer")
                    if WOShellExec.cmd_exec(
                            self, '/usr/bin/php -v'):
                        WOShellExec.cmd_exec(
                            self, "php -q /var/lib/wo"
                            "/tmp/composer-install "
                            "--install-dir=/var/lib/wo/tmp/")
                    shutil.copyfile('/var/lib/wo/tmp/composer.phar',
                                    '/usr/local/bin/composer')
                    WOFileUtils.chmod(self, "/usr/local/bin/composer", 0o775)
                    Log.valide(self, "Upgrading Composer    ")

                if WOAptGet.is_selected(self, 'PHPMyAdmin', packages):
                    Log.wait(self, "Upgrading phpMyAdmin")
                    WOExtract.extract(self, '/var/lib/wo/tmp/pma.tar.gz',
                                      '/var/lib/wo/tmp/')
                    shutil.copyfile(('{0}22222/htdocs/db/pma'
                                     '/config.inc.php'
                                     .format(WOVar.wo_webroot)),
                                    ('/var/lib/wo/tmp/phpMyAdmin-{0}'
                                     '-all-languages/config.inc.php'
                                     .format(WOVar.wo_phpmyadmin))
                                    )
                    WOFileUtils.rm(self, '{0}22222/htdocs/db/pma'
                                   .format(WOVar.wo_webroot))
                    shutil.move('/var/lib/wo/tmp/phpMyAdmin-{0}'
                                '-all-languages/'
                                .format(WOVar.wo_phpmyadmin),
                                '{0}22222/htdocs/db/pma/'
                                .format(WOVar.wo_webroot))
                    WOFileUtils.chown(self, "{0}22222/htdocs"
                                      .format(WOVar.wo_webroot),
                                      'www-data',
                                      'www-data', recursive=True)
                    Log.valide(self, "Upgrading phpMyAdmin")
                if os.path.exists('{0}22222/htdocs'.format(WOVar.wo_webroot)):
                    WOFileUtils.chown(self, "{0}22222/htdocs"
                                      .format(WOVar.wo_webroot),
                                      'www-data',
                                      'www-data', recursive=True)

            Log.info(self, "Successfully updated packages")
