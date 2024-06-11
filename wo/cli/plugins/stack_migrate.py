import os
import re
from cement.core.controller import CementBaseController, expose

from wo.cli.plugins.stack_pref import post_pref, pre_pref
from wo.core.aptget import WOAptGet
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar
from wo.cli.plugins.sitedb import (getAllsites)
from wo.core.template import WOTemplate
from wo.core.domainvalidate import WODomain


class WOStackMigrateController(CementBaseController):
    class Meta:
        label = 'migrate'
        stacked_on = 'stack'
        stacked_type = 'nested'
        description = ('Migrate stack safely')
        arguments = [
            (['--mariadb'],
                dict(help="Migrate/Upgrade database to MariaDB",
                     action='store_true')),
            (['--nginx'],
                dict(help="Migrate Nginx TLS configuration to HTTP/3 QUIC",
                     action='store_true')),
            (['--force'],
                dict(help="Force Packages upgrade without any prompt",
                     action='store_true')),
            (['--ci'],
                dict(help="Argument used for testing, "
                     "do not use it on your server",
                     action='store_true')),
        ]

    @expose(hide=True)
    def migrate_mariadb(self, ci=False):

        # Backup all database
        WOMysql.backupAll(self, fulldump=True)

        # Check current MariaDB version
        if (os.path.exists('/etc/apt/sources.list.d/wo-repo.list') and
                WOFileUtils.grepcheck(self, "/etc/apt/sources.list.d/wo-repo.list", "mariadb")):
            wo_mysql_current_repo = WOFileUtils.grep(
                self, '/etc/apt/sources.list.d/wo-repo.list', 'mariadb')
            repo_path = '/etc/apt/sources.list.d/wo-repo.list'
        elif (os.path.exists('/etc/apt/sources.list.d/mariadb.list') and
              WOFileUtils.grepcheck(self, '/etc/apt/sources.list.d/mariadb.list', "mariadb")):
            wo_mysql_current_repo = WOFileUtils.grep(
                self, '/etc/apt/sources.list.d/mariadb.list', 'mariadb')
            repo_path = '/etc/apt/sources.list.d/mariadb.list'

        if wo_mysql_current_repo:
            Log.debug(self, "Looking for MariaDB version")
            pattern = r"/(\d+\.\d+)/"
            match = re.search(pattern, wo_mysql_current_repo)
            current_mysql_version = match.group(1)
            Log.debug(self, f"Current MariaDB version is {current_mysql_version}")
        else:
            Log.error(self, "MariaDB is not installed from repository yet")

        if self.app.config.has_section('mariadb'):
            mariadb_release = self.app.config.get(
                'mariadb', 'release')
            if mariadb_release < WOVar.mariadb_ver:
                mariadb_release = WOVar.mariadb_ver
        else:
            mariadb_release = WOVar.mariadb_ver
        if mariadb_release == current_mysql_version:
            Log.info(self, "You already have the latest "
                     "MariaDB version available")
            return 0

        WOFileUtils.rm(self, repo_path)
        # Add MariaDB repo
        pre_pref(self, WOVar.wo_mysql)

        # Install MariaDB

        Log.wait(self, "Updating apt-cache          ")
        WOAptGet.update(self)
        Log.valide(self, "Updating apt-cache          ")
        Log.wait(self, "Upgrading MariaDB          ")
        WOAptGet.remove(self, ["mariadb-server"])
        WOAptGet.auto_remove(self)
        WOAptGet.install(self, WOVar.wo_mysql)
        if not ci:
            WOAptGet.dist_upgrade(self)
        WOAptGet.auto_remove(self)
        WOAptGet.auto_clean(self)
        Log.valide(self, "Upgrading MariaDB          ")
        WOFileUtils.mvfile(
            self, '/etc/mysql/my.cnf', '/etc/mysql/my.cnf.old')
        WOFileUtils.create_symlink(
            self, ['/etc/mysql/mariadb.cnf', '/etc/mysql/my.cnf'])
        WOShellExec.cmd_exec(self, 'systemctl daemon-reload')
        WOShellExec.cmd_exec(self, 'systemctl enable mariadb')
        post_pref(self, WOVar.wo_mysql, [])

    @expose(hide=True)
    def migrate_nginx(self):

        # Add Nginx repo
        pre_pref(self, WOVar.wo_nginx)
        # Install Nginx
        Log.wait(self, "Updating apt-cache          ")
        WOAptGet.update(self)
        Log.valide(self, "Updating apt-cache          ")
        Log.wait(self, "Upgrading Nginx          ")
        if WOAptGet.install(self, WOVar.wo_nginx):
            Log.valide(self, "Upgrading Nginx          ")
        else:
            Log.failed(self, "Upgrading Nginx          ")
        allsites = getAllsites(self)
        for site in allsites:
            if not site:
                pass
            if os.path.exists(f'/var/www/{site.sitename}/conf/nginx/ssl.conf'):
                if not os.path.islink(f'/var/www/{site.sitename}/conf/nginx/ssl.conf'):
                    data = dict(ssl_live_path=WOVar.wo_ssl_live,
                                domain=site.sitename, quic=True)
                    WOTemplate.deploy(
                        self, f'/var/www/{site.sitename}/conf/nginx/ssl.conf',
                        'ssl.mustache', data, overwrite=True)
                else:
                    (_, wo_root_domain) = WODomain.getlevel(
                        self, site.sitename)
                    if (site.sitename != wo_root_domain and
                            os.path.exists(f'/etc/letsencrypt/shared/{wo_root_domain}.conf')):
                        data = dict(ssl_live_path=WOVar.wo_ssl_live,
                                    domain=wo_root_domain, quic=True)
                        WOTemplate.deploy(
                            self, f'/etc/letsencrypt/shared/{wo_root_domain}.conf',
                            'ssl.mustache', data, overwrite=True)
        post_pref(self, WOVar.wo_nginx, [])

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if not pargs.mariadb and not pargs.nginx:
            self.app.args.print_help()
        if pargs.mariadb:
            if WOVar.wo_distro == 'raspbian':
                Log.error(self, "MariaDB upgrade is not available on Raspbian")
            if WOVar.wo_mysql_host != "localhost":
                Log.error(
                    self, "Remote MySQL server in use, skipping local install")

            if WOMysql.mariadb_ping(self):

                Log.info(self, "If your database size is big, "
                         "migration may take some time.")
                Log.info(self, "During migration non nginx-cached parts of "
                         "your site may remain down")
                if not pargs.force:
                    start_upgrade = input("Do you want to continue:[y/N]")
                    if start_upgrade != "Y" and start_upgrade != "y":
                        Log.error(self, "Not starting package update")
                if not pargs.ci:
                    self.migrate_mariadb()
                else:
                    self.migrate_mariadb(ci=True)
            else:
                Log.error(self, "Your current MySQL is not alive or "
                          "you allready installed MariaDB")
        if pargs.nginx:
            if os.path.exists('/usr/sbin/nginx'):
                self.migrate_nginx()
            else:
                Log.error(self, "Unable to connect to MariaDB")
