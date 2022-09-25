from cement.core.controller import CementBaseController, expose

from wo.cli.plugins.stack_pref import post_pref, pre_pref
from wo.core.aptget import WOAptGet
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar
from wo.core.apt_repo import WORepo


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

        # Remove previous MariaDB repository
        wo_mysql_old_repo = (
            "deb [arch=amd64,ppc64el] "
            "http://mariadb.mirrors.ovh.net/MariaDB/repo/"
            "10.3/{distro} {codename} main"
            .format(distro=WOVar.wo_distro,
                    codename=WOVar.wo_platform_codename))
        if WOFileUtils.grepcheck(
                self, '/etc/apt/sources.list.d/wo-repo.list',
                wo_mysql_old_repo):
            WORepo.remove(self, repo_url=wo_mysql_old_repo)
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
    def default(self):
        pargs = self.app.pargs
        if not pargs.mariadb:
            self.app.args.print_help()
        if pargs.mariadb:
            if WOVar.wo_distro == 'raspbian':
                Log.error(self, "MariaDB upgrade is not available on Raspbian")
            if WOVar.wo_mysql_host != "localhost":
                Log.error(
                    self, "Remote MySQL server in use, skipping local install")

            if WOShellExec.cmd_exec(self, "mysqladmin ping"):

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
