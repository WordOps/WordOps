import configparser
import os

from cement.core.controller import CementBaseController, expose

from wo.core.apt_repo import WORepo
from wo.core.aptget import WOAptGet
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


class WOStackMigrateController(CementBaseController):
    class Meta:
        label = 'migrate'
        stacked_on = 'stack'
        stacked_type = 'nested'
        description = ('Migrate stack safely')
        arguments = [
            (['--mariadb'],
                dict(help="Migrate database to MariaDB",
                     action='store_true')),
        ]

    @expose(hide=True)
    def migrate_mariadb(self):
        # Backup all database
        WOMysql.backupAll(self)

        if not WOVar.wo_distro == 'raspbian':
            if (not WOVar.wo_platform_codename == 'jessie'):
                wo_mysql = ["mariadb-server", "percona-toolkit",
                            "python3-mysqldb", "mariadb-backup"]
            else:
                wo_mysql = ["mariadb-server", "percona-toolkit",
                            "python3-mysql.connector"]
        else:
            wo_mysql = ["mariadb-server", "percona-toolkit",
                        "python3-mysqldb"]

        # Add MariaDB repo
        Log.info(self, "Adding repository for MariaDB, please wait...")

        mysql_pref = ("Package: *\nPin: origin sfo1.mirrors.digitalocean.com"
                      "\nPin-Priority: 1000\n")
        with open('/etc/apt/preferences.d/'
                  'MariaDB.pref', 'w') as mysql_pref_file:
            mysql_pref_file.write(mysql_pref)

        WORepo.add(self, repo_url=WOVar.wo_mysql_repo)
        Log.debug(self, 'Adding key for {0}'
                  .format(WOVar.wo_mysql_repo))
        WORepo.add_key(self, '0xcbcb082a1bb943db',
                       keyserver="keyserver.ubuntu.com")

        config = configparser.ConfigParser()
        if os.path.exists('/etc/mysql/conf.d/my.cnf'):
            config.read('/etc/mysql/conf.d/my.cnf')
        else:
            config.read(os.path.expanduser("~")+'/.my.cnf')

        try:
            chars = config['client']['password']
        except Exception as e:
            Log.error(self, "Error: process exited with error %s"
                            % e)

        Log.debug(self, "Pre-seeding MariaDB")
        Log.debug(self, "echo \"mariadb-server-10.3 "
                        "mysql-server/root_password "
                        "password \" | "
                        "debconf-set-selections")
        WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.3 "
                                   "mysql-server/root_password "
                                   "password {chars}\" | "
                                   "debconf-set-selections"
                                   .format(chars=chars),
                                   log=False)
        Log.debug(self, "echo \"mariadb-server-10.3 "
                        "mysql-server/root_password_again "
                        "password \" | "
                        "debconf-set-selections")
        WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.3 "
                                   "mysql-server/root_password_again "
                                   "password {chars}\" | "
                                   "debconf-set-selections"
                                   .format(chars=chars),
                                   log=False)

        # Install MariaDB
        apt_packages = wo_mysql

        Log.info(self, "Updating apt-cache, hang on...")
        WOAptGet.update(self)
        Log.info(self, "Installing MariaDB, hang on...")
        WOAptGet.remove(self, ["mysql-common", "libmysqlclient18"])
        WOAptGet.auto_remove(self)
        WOAptGet.install(self, apt_packages)

    @expose(hide=True)
    def default(self):
        if ((not self.app.pargs.mariadb)):
            self.app.args.print_help()
        if self.app.pargs.mariadb:
            if WOVar.wo_mysql_host != "localhost":
                Log.error(
                    self, "Remote MySQL server in use, skipping local install")

            if (WOShellExec.cmd_exec(self, "mysqladmin ping") and
                    (not WOAptGet.is_installed(self, 'mariadb-server'))):

                Log.info(self, "If your database size is big, "
                         "migration may take some time.")
                Log.info(self, "During migration non nginx-cached parts of "
                         "your site may remain down")
                start_migrate = input("Type \"mariadb\" to continue:")
                if start_migrate != "mariadb":
                    Log.error(self, "Not starting migration")
                self.migrate_mariadb()
            else:
                Log.error(self, "Your current MySQL is not alive or "
                          "you allready installed MariaDB")
