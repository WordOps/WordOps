"""Stack Plugin for WordOps"""

from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.cli.plugins.site_functions import *
from wo.core.variables import WOVariables
from wo.core.aptget import WOAptGet
from wo.core.download import WODownload
from wo.core.shellexec import WOShellExec, CommandExecutionError
from wo.core.fileutils import WOFileUtils
from wo.core.apt_repo import WORepo
from wo.core.extract import WOExtract
from wo.core.mysql import WOMysql
from wo.core.addswap import WOSwap
from wo.core.git import WOGit
from wo.core.checkfqdn import check_fqdn
from pynginxconfig import NginxConfig
from wo.core.services import WOService
from wo.core.variables import WOVariables
import random
import string
import configparser
import time
import shutil
import os
import pwd
import grp
import codecs
import platform
from wo.cli.plugins.stack_services import WOStackStatusController
from wo.cli.plugins.stack_migrate import WOStackMigrateController
from wo.cli.plugins.stack_upgrade import WOStackUpgradeController
from wo.core.logging import Log
from wo.cli.plugins.sitedb import *


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
            (['--adminer'],
                dict(help='Install Adminer stack', action='store_true')),
            (['--utils'],
                dict(help='Install Utils stack', action='store_true')),
            (['--redis'],
                dict(help='Install Redis', action='store_true')),
            (['--phpredisadmin'],
                dict(help='Install phpRedisAdmin', action='store_true')),
        ]
        usage = "wo stack (command) [options]"

    @expose(hide=True)
    def default(self):
        """default action of wo stack command"""
        self.app.args.print_help()

    @expose(hide=True)
    def pre_pref(self, apt_packages):
        """Pre settings to do before installation packages"""

        if set(WOVariables.wo_mysql).issubset(set(apt_packages)):
            Log.info(self, "Adding repository for MySQL, please wait...")
            mysql_pref = ("Package: *\nPin: origin sfo1.mirrors.digitalocean.com"
                          "\nPin-Priority: 1000\n")
            with open('/etc/apt/preferences.d/'
                      'MariaDB.pref', 'w') as mysql_pref_file:
                mysql_pref_file.write(mysql_pref)
            WORepo.add(self, repo_url=WOVariables.wo_mysql_repo)
            Log.debug(self, 'Adding key for {0}'
                      .format(WOVariables.wo_mysql_repo))
            WORepo.add_key(self, '0xcbcb082a1bb943db',
                           keyserver="keyserver.ubuntu.com")
            WORepo.add_key(self, '0xF1656F24C74CD1D8',
                           keyserver="keyserver.ubuntu.com")
            chars = ''.join(random.sample(string.ascii_letters, 8))
            Log.debug(self, "Pre-seeding MySQL")
            Log.debug(self, "echo \"mariadb-server-10.3 "
                      "mysql-server/root_password "
                      "password \" | "
                      "debconf-set-selections")
            try:
                WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.3 "
                                     "mysql-server/root_password "
                                     "password {chars}\" | "
                                     "debconf-set-selections"
                                     .format(chars=chars),
                                     log=False)
            except CommandExecutionError as e:
                Log.error("Failed to initialize MySQL package")

            Log.debug(self, "echo \"mariadb-server-10.3 "
                      "mysql-server/root_password_again "
                      "password \" | "
                      "debconf-set-selections")
            try:
                WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.3 "
                                     "mysql-server/root_password_again "
                                     "password {chars}\" | "
                                     "debconf-set-selections"
                                     .format(chars=chars),
                                     log=False)
            except CommandExecutionError as e:
                Log.error("Failed to initialize MySQL package")

            mysql_config = """
            [client]
            user = root
            password = {chars}
            """.format(chars=chars)
            config = configparser.ConfigParser()
            config.read_string(mysql_config)
            Log.debug(self, 'Writting configuration into MySQL file')
            conf_path = "/etc/mysql/conf.d/my.cnf"
            os.makedirs(os.path.dirname(conf_path), exist_ok=True)
            with open(conf_path, encoding='utf-8',
                      mode='w') as configfile:
                config.write(configfile)
            Log.debug(self, 'Setting my.cnf permission')
            WOFileUtils.chmod(self, "/etc/mysql/conf.d/my.cnf", 0o600)

        if set(WOVariables.wo_nginx).issubset(set(apt_packages)):
            Log.info(self, "Adding repository for NGINX, please wait...")
            WORepo.add(self, repo_url=WOVariables.wo_nginx_repo)
            Log.debug(self, 'Adding repository for Nginx')
            WORepo.add_key(self, WOVariables.wo_nginx_key)

        if (WOVariables.wo_platform_distro == 'ubuntu'):
            if (set(WOVariables.wo_php73).issubset(set(apt_packages)) or
                    set(WOVariables.wo_php).issubset(set(apt_packages))):
                Log.info(self, "Adding repository for PHP, please wait...")
                Log.debug(self, 'Adding ppa for PHP')
                WORepo.add(self, ppa=WOVariables.wo_php_repo)
        else:
            if (set(WOVariables.wo_php73).issubset(set(apt_packages)) or
                    set(WOVariables.wo_php).issubset(set(apt_packages))):
                Log.info(self, "Adding repository for PHP, please wait...")
                # Add repository for php
                Log.debug(self, 'Adding repo_url of php for debian')
                WORepo.add(self, repo_url=WOVariables.wo_php_repo)
                Log.debug(self, 'Adding deb.sury GPG key')
                WORepo.add_key(self, WOVariables.wo_php_key)

        if set(WOVariables.wo_redis).issubset(set(apt_packages)):
            Log.info(self, "Adding repository for Redis, please wait...")
            if WOVariables.wo_platform_distro == 'debian':
                Log.debug(self, 'Adding repo_url of redis for debian')
                WORepo.add(self, repo_url=WOVariables.wo_redis_repo)
                Log.debug(self, 'Adding Deb.sury GPG key')
                WORepo.add_key(self, 'AC0E47584A7A714D')
            else:
                Log.debug(self, 'Adding ppa for redis')
                WORepo.add(self, ppa=WOVariables.wo_redis_repo)

    @expose(hide=True)
    def post_pref(self, apt_packages, packages):
        """Post activity after installation of packages"""
        if len(apt_packages):

            if set(WOVariables.wo_nginx).issubset(set(apt_packages)):
                if set(["nginx"]).issubset(set(apt_packages)):
                    # Fix for white screen death with NGINX PLUS
                    if not WOFileUtils.grep(self, '/etc/nginx/fastcgi_params',
                                            'SCRIPT_FILENAME'):
                        with open('/etc/nginx/fastcgi_params',
                                  encoding='utf-8', mode='a') as wo_nginx:
                            wo_nginx.write('fastcgi_param \tSCRIPT_FILENAME '
                                           '\t$request_filename;\n')

                if not (os.path.isfile('/etc/nginx/common/wpfc-php72.conf')):
                    # Change WordOpsVersion in nginx.conf file
                    WOFileUtils.searchreplace(self, "/etc/nginx/nginx.conf",
                                              "# add_header",
                                              "add_header")

                    WOFileUtils.searchreplace(self, "/etc/nginx/nginx.conf",
                                              "\"WordOps\"",
                                              "\"WordOps v{0}\""
                                              .format(WOVariables.wo_version))
                    data = dict()
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/conf.d/blockips.conf')
                    wo_nginx = open('/etc/nginx/conf.d/blockips.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'blockips.mustache', out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/conf.d/fastcgi.conf')
                    wo_nginx = open('/etc/nginx/conf.d/fastcgi.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'fastcgi.mustache', out=wo_nginx)
                    wo_nginx.close()

                    data = dict(php="9000", debug="9001",
                                php7="9070", debug7="9170",
                                php7conf=True
                                if WOAptGet.is_installed(self, 'php7.0-fpm')
                                else False)
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/conf.d/upstream.conf')
                    wo_nginx = open('/etc/nginx/conf.d/upstream.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'upstream.mustache', out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/conf.d/map-wp.conf')
                    wo_nginx = open('/etc/nginx/conf.d/map-wp.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'map-wp.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    if not (os.path.isfile('/etc/nginx/conf.d/webp.conf')):
                        Log.debug(self, 'Writting the nginx configuration to '
                                        'file /etc/nginx/conf.d/webp.conf')
                        wo_nginx = open('/etc/nginx/conf.d/webp.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'webp.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                    # Setup Nginx common directory
                    if not os.path.exists('/etc/nginx/common'):
                        Log.debug(self, 'Creating directory'
                                  '/etc/nginx/common')
                        os.makedirs('/etc/nginx/common')

                    data = dict(webroot=WOVariables.wo_webroot)
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/acl.conf')
                    wo_nginx = open('/etc/nginx/common/acl.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'acl.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/locations-php72.conf')
                    wo_nginx = open('/etc/nginx/common/locations-php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'locations.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/php72.conf')
                    wo_nginx = open('/etc/nginx/common/php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'php.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpcommon-php72.conf')
                    wo_nginx = open('/etc/nginx/common/wpcommon-php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpcommon.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpfc-php72.conf')
                    wo_nginx = open('/etc/nginx/common/wpfc-php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpfc.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpsc-php72.conf')
                    wo_nginx = open('/etc/nginx/common/wpsc-php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpsc.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpsubdir.conf')
                    wo_nginx = open('/etc/nginx/common/wpsubdir.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpsubdir.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    # php7 conf
                    if not os.path.isfile("/etc/nginx/common/php73.conf"):
                        # data = dict()
                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/locations-php73.conf')
                        wo_nginx = open('/etc/nginx/common/locations-php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'locations-php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/php73.conf')
                        wo_nginx = open('/etc/nginx/common/php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/wpcommon-php73.conf')
                        wo_nginx = open('/etc/nginx/common/wpcommon-php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'wpcommon-php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/wpfc-php73.conf')
                        wo_nginx = open('/etc/nginx/common/wpfc-php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'wpfc-php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/wpsc-php73.conf')
                        wo_nginx = open('/etc/nginx/common/wpsc-php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'wpsc-php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/redis-php73.conf')
                        wo_nginx = open('/etc/nginx/common/redis-php73.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'redis-php7.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                    # Nginx-Plus does not have nginx
                    # package structure like this
                    # So creating directories
                    if (set(["nginx-plus"]).issubset(set(apt_packages)) or
                            set(["nginx"]).issubset(set(apt_packages))):
                        Log.info(self,
                                 "Installing WordOpsConfigurations for" "NGINX")
                        if not os.path.exists('/etc/nginx/sites-available'):
                            Log.debug(self, 'Creating directory'
                                      '/etc/nginx/sites-available')
                            os.makedirs('/etc/nginx/sites-available')

                        if not os.path.exists('/etc/nginx/sites-enabled'):
                            Log.debug(self, 'Creating directory'
                                      '/etc/nginx/sites-available')
                            os.makedirs('/etc/nginx/sites-enabled')

                    # 22222 port settings
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/sites-available/'
                              '22222')
                    wo_nginx = open('/etc/nginx/sites-available/22222',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), '22222.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    passwd = ''.join([random.choice
                                      (string.ascii_letters + string.digits)
                                      for n in range(6)])
                    try:
                        WOShellExec.cmd_exec(self, "printf \"WordOps:"
                                             "$(openssl passwd -crypt "
                                             "{password} 2> /dev/null)\n\""
                                             "> /etc/nginx/htpasswd-wo "
                                             "2>/dev/null"
                                             .format(password=passwd))
                    except CommandExecutionError as e:
                        Log.error(self, "Failed to save HTTP Auth")

                    # Create Symbolic link for 22222
                    WOFileUtils.create_symlink(self, ['/etc/nginx/'
                                                      'sites-available/'
                                                      '22222',
                                                      '/etc/nginx/'
                                                      'sites-enabled/'
                                                      '22222'])
                    # Create log and cert folder and softlinks
                    if not os.path.exists('{0}22222/logs'
                                          .format(WOVariables.wo_webroot)):
                        Log.debug(self, "Creating directory "
                                  "{0}22222/logs "
                                  .format(WOVariables.wo_webroot))
                        os.makedirs('{0}22222/logs'
                                    .format(WOVariables.wo_webroot))

                    if not os.path.exists('{0}22222/cert'
                                          .format(WOVariables.wo_webroot)):
                        Log.debug(self, "Creating directory "
                                  "{0}22222/cert"
                                  .format(WOVariables.wo_webroot))
                        os.makedirs('{0}22222/cert'
                                    .format(WOVariables.wo_webroot))

                    WOFileUtils.create_symlink(self, ['/var/log/nginx/'
                                                      '22222.access.log',
                                                      '{0}22222/'
                                                      'logs/access.log'
                                                      .format(WOVariables.wo_webroot)]
                                               )

                    WOFileUtils.create_symlink(self, ['/var/log/nginx/'
                                                      '22222.error.log',
                                                      '{0}22222/'
                                                      'logs/error.log'
                                                      .format(WOVariables.wo_webroot)]
                                               )

                    try:
                        WOShellExec.cmd_exec(self, "openssl genrsa -out "
                                             "{0}22222/cert/22222.key 2048"
                                             .format(WOVariables.wo_webroot))
                        WOShellExec.cmd_exec(self, "openssl req -new -batch  "
                                             "-subj /commonName=localhost/ "
                                             "-key {0}22222/cert/22222.key "
                                             "-out {0}22222/cert/"
                                             "22222.csr"
                                             .format(WOVariables.wo_webroot))

                        WOFileUtils.mvfile(self, "{0}22222/cert/22222.key"
                                           .format(WOVariables.wo_webroot),
                                           "{0}22222/cert/"
                                           "22222.key.org"
                                           .format(WOVariables.wo_webroot))

                        WOShellExec.cmd_exec(self, "openssl rsa -in "
                                             "{0}22222/cert/"
                                             "22222.key.org -out "
                                             "{0}22222/cert/22222.key"
                                             .format(WOVariables.wo_webroot))

                        WOShellExec.cmd_exec(self, "openssl x509 -req -days "
                                             "3652 -in {0}22222/cert/"
                                             "22222.csr -signkey {0}"
                                             "22222/cert/22222.key -out "
                                             "{0}22222/cert/22222.crt"
                                             .format(WOVariables.wo_webroot))

                    except CommandExecutionError as e:
                        Log.error(
                            self, "Failed to generate HTTPS certificate for 22222")

                    # Nginx Configation into GIT
                    WOGit.add(self,
                              ["/etc/nginx"], msg="Adding Nginx into Git")
                    WOService.reload_service(self, 'nginx')
                    if (set(["nginx-plus"]).issubset(set(apt_packages)) or
                            set(["nginx"]).issubset(set(apt_packages))):
                        WOShellExec.cmd_exec(self, "sed -i -e 's/^user/#user/'"
                                             " -e '/^#user/a user"
                                             "\ www-data\;'"
                                             " /etc/nginx/nginx.conf")
                        if not WOShellExec.cmd_exec(self, "cat /etc/nginx/"
                                                    "nginx.conf | grep -q "
                                                    "'/etc/nginx/sites-enabled'"):
                            WOShellExec.cmd_exec(self, "sed -i '/\/etc\/"
                                                 "nginx\/conf\.d\/\*"
                                                 "\.conf/a \    include"
                                                 "\ \/etc\/nginx\/sites-enabled"
                                                 "\/*;' /etc/nginx/nginx.conf")

                        # WordOpsconfig for NGINX plus
                        data['version'] = WOVariables.wo_version
                        Log.debug(self, 'Writting for nginx plus configuration'
                                  ' to file /etc/nginx/conf.d/wo-plus.conf')
                        wo_nginx = open('/etc/nginx/conf.d/wo-plus.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'wo-plus.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                        print("HTTP Auth User Name: WordOps"
                              + "\nHTTP Auth Password : {0}".format(passwd))
                        WOService.reload_service(self, 'nginx')
                    else:
                        self.msg = (self.msg + ["HTTP Auth User Name: WordOps"]
                                    + ["HTTP Auth Password : {0}".format(passwd)])
                else:
                    WOService.restart_service(self, 'nginx')

                if WOAptGet.is_installed(self, 'redis-server'):
                    if (os.path.isfile("/etc/nginx/nginx.conf") and
                            not os.path.isfile("/etc/nginx/common/redis-php72.conf")):

                        data = dict()
                        Log.debug(self, 'Writting the nginx configuration to '
                                  'file /etc/nginx/common/redis-php72.conf')
                        wo_nginx = open('/etc/nginx/common/redis-php72.conf',
                                        encoding='utf-8', mode='w')
                        self.app.render((data), 'redis.mustache',
                                        out=wo_nginx)
                        wo_nginx.close()

                    if (WOVariables.wo_platform_distro == 'ubuntu'):
                        if (os.path.isfile("/etc/nginx/nginx.conf") and
                                not os.path.isfile("/etc/nginx/common/redis-php73.conf")):
                            data = dict()
                            Log.debug(self, 'Writting the nginx configuration to '
                                      'file /etc/nginx/common/redis-php73.conf')
                            wo_nginx = open('/etc/nginx/common/redis-php73.conf',
                                            encoding='utf-8', mode='w')
                            self.app.render((data), 'redis-php7.mustache',
                                            out=wo_nginx)
                            wo_nginx.close()

                    if os.path.isfile("/etc/nginx/conf.d/upstream.conf"):
                        if not WOFileUtils.grep(self, "/etc/nginx/conf.d/"
                                                "upstream.conf",
                                                "redis"):
                            with open("/etc/nginx/conf.d/upstream.conf",
                                      "a") as redis_file:
                                redis_file.write("upstream redis {\n"
                                                 "    server 127.0.0.1:6379;\n"
                                                 "    keepalive 10;\n}\n")

                    if (os.path.isfile("/etc/nginx/nginx.conf") and
                            not os.path.isfile("/etc/nginx/conf.d/redis.conf")):
                        with open("/etc/nginx/conf.d/redis.conf", "a") as redis_file:
                            redis_file.write("# Log format Settings\n"
                                             "log_format rt_cache_redis '$remote_addr $upstream_response_time $srcache_fetch_status [$time_local] '\n"
                                             "'$http_host \"$request\" $status $body_bytes_sent '\n"
                                             "'\"$http_referer\" \"$http_user_agent\"';\n")
            # setup nginx common folder for php7
            if self.app.pargs.php73:
                if (os.path.isdir("/etc/nginx/common") and
                        not os.path.isfile("/etc/nginx/common/php73.conf")):
                    data = dict()
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/locations-php73.conf')
                    wo_nginx = open('/etc/nginx/common/locations-php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'locations-php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/php73.conf')
                    wo_nginx = open('/etc/nginx/common/php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpcommon-php73.conf')
                    wo_nginx = open('/etc/nginx/common/wpcommon-php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpcommon-php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpfc-php73.conf')
                    wo_nginx = open('/etc/nginx/common/wpfc-php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpfc-php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/wpsc-php73.conf')
                    wo_nginx = open('/etc/nginx/common/wpsc-php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'wpsc-php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                if (os.path.isdir("/etc/nginx/common") and
                        not os.path.isfile("/etc/nginx/common/redis-php73.conf")):
                    data = dict()
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/redis-php73.conf')
                    wo_nginx = open('/etc/nginx/common/redis-php73.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'redis-php7.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                if os.path.isfile("/etc/nginx/conf.d/upstream.conf"):
                    if not WOFileUtils.grep(self, "/etc/nginx/conf.d/upstream.conf",
                                            "php73"):
                        with open("/etc/nginx/conf.d/upstream.conf", "a") as php_file:
                            php_file.write("upstream php73 {\nserver unix:/var/run/php/php73-fpm.sock;\n}\n"
                                           "upstream debug73 {\nserver 127.0.0.1:9173;\n}\n")

            if set(WOVariables.wo_redis).issubset(set(apt_packages)):
                if (os.path.isfile("/etc/nginx/nginx.conf") and
                        not os.path.isfile("/etc/nginx/common/redis-php72.conf")):

                    data = dict()
                    Log.debug(self, 'Writting the nginx configuration to '
                              'file /etc/nginx/common/redis-php72.conf')
                    wo_nginx = open('/etc/nginx/common/redis-php72.conf',
                                    encoding='utf-8', mode='w')
                    self.app.render((data), 'redis.mustache',
                                    out=wo_nginx)
                    wo_nginx.close()

                if os.path.isfile("/etc/nginx/conf.d/upstream.conf"):
                    if not WOFileUtils.grep(self, "/etc/nginx/conf.d/"
                                            "upstream.conf",
                                            "redis"):
                        with open("/etc/nginx/conf.d/upstream.conf",
                                  "a") as redis_file:
                            redis_file.write("upstream redis {\n"
                                             "    server 127.0.0.1:6379;\n"
                                             "    keepalive 10;\n}\n")

                if os.path.isfile("/etc/nginx/nginx.conf"):
                    if not os.path.isfile("/etc/nginx/conf.d/redis.conf"):
                        with open("/etc/nginx/conf.d/redis.conf",
                                  "a") as redis_file:
                            redis_file.write("# Log format Settings\n"
                                             "log_format rt_cache_redis "
                                             "'$remote_addr "
                                             "$upstream_response_time "
                                             "$srcache_fetch_status "
                                             "[$time_local]"
                                             " '\n '$http_host"
                                             " \"$request\" "
                                             "$status $body_bytes_sent '\n"
                                             "'\"$http_referer\" "
                                             "\"$http_user_agent\"';\n")

            if (WOVariables.wo_platform_distro == 'ubuntu'):
                # Create log directories
                if not os.path.exists('/var/log/php/7.2/'):
                    Log.debug(self, 'Creating directory /var/log/php/7.2/')
                    os.makedirs('/var/log/php/7.2/')

                # Parse etc/php/7.2/fpm/php.ini
                config = configparser.ConfigParser()
                Log.debug(self, "configuring php file /etc/php/7.2/fpm/php.ini")
                config.read('/etc/php/7.2/fpm/php.ini')
                config['PHP']['expose_php'] = 'Off'
                config['PHP']['post_max_size'] = '100M'
                config['PHP']['upload_max_filesize'] = '100M'
                config['PHP']['max_execution_time'] = '300'
                config['PHP']['date.timezone'] = WOVariables.wo_timezone
                with open('/etc/php/7.2/fpm/php.ini',
                          encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "Writting php configuration into "
                              "/etc/php/7.2/fpm/php.ini")
                    config.write(configfile)

                # Parse /etc/php/7.2/fpm/php-fpm.conf
                data = dict(pid="/run/php/php7.2-fpm.pid",
                            error_log="/var/log/php/7.2/fpm.log",
                            include="/etc/php/7.2/fpm/pool.d/*.conf")
                Log.debug(self, "writting php7.2 configuration into "
                          "/etc/php/7.2/fpm/php-fpm.conf")
                wo_php_fpm = open('/etc/php/7.2/fpm/php-fpm.conf',
                                  encoding='utf-8', mode='w')
                self.app.render((data), 'php-fpm.mustache', out=wo_php_fpm)
                wo_php_fpm.close()

                # Parse /etc/php/7.2/fpm/pool.d/www.conf
                config = configparser.ConfigParser()
                config.read_file(codecs.open('/etc/php/7.2/fpm/pool.d/www.conf',
                                             "r", "utf8"))
                config['www']['ping.path'] = '/ping'
                config['www']['pm.status_path'] = '/status'
                config['www']['pm.max_requests'] = '100'
                config['www']['pm.max_children'] = '25'
                config['www']['pm.start_servers'] = '5'
                config['www']['pm.min_spare_servers'] = '2'
                config['www']['pm.max_spare_servers'] = '5'
                config['www']['request_terminate_timeout'] = '100'
                config['www']['pm'] = 'ondemand'
                config['www']['chdir'] = '/'
                config['www']['prefix'] = '/var/run/php'
                config['www']['listen'] = 'php72-fpm.sock'
                config['www']['listen.backlog'] = '32768'
                with codecs.open('/etc/php/7.2/fpm/pool.d/www.conf',
                                 encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "Writing PHP 7.2 configuration into "
                              "/etc/php/7.2/fpm/pool.d/www.conf")
                    config.write(configfile)

                # Generate /etc/php/7.2/fpm/pool.d/debug.conf
                WOFileUtils.copyfile(self, "/etc/php/7.2/fpm/pool.d/www.conf",
                                     "/etc/php/7.2/fpm/pool.d/debug.conf")
                WOFileUtils.searchreplace(self, "/etc/php/7.2/fpm/pool.d/"
                                          "debug.conf", "[www]", "[debug]")
                config = configparser.ConfigParser()
                config.read('/etc/php/7.2/fpm/pool.d/debug.conf')
                config['debug']['listen'] = '127.0.0.1:9172'
                config['debug']['rlimit_core'] = 'unlimited'
                config['debug']['slowlog'] = '/var/log/php/7.2/slow.log'
                config['debug']['request_slowlog_timeout'] = '10s'
                with open('/etc/php/7.2/fpm/pool.d/debug.conf',
                          encoding='utf-8', mode='w') as confifile:
                    Log.debug(self, "writting PHP7.2 configuration into "
                              "/etc/php/7.2/fpm/pool.d/debug.conf")
                    config.write(confifile)

                with open("/etc/php/7.2/fpm/pool.d/debug.conf",
                          encoding='utf-8', mode='a') as myfile:
                    myfile.write("php_admin_value[xdebug.profiler_output_dir] "
                                 "= /tmp/ \nphp_admin_value[xdebug.profiler_"
                                 "output_name] = cachegrind.out.%p-%H-%R "
                                 "\nphp_admin_flag[xdebug.profiler_enable"
                                 "_trigger] = on \nphp_admin_flag[xdebug."
                                 "profiler_enable] = off\n")

                # Disable xdebug
                if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\' /etc/php/7.2/mods-available/xdebug.ini"):
                    WOFileUtils.searchreplace(self, "/etc/php/7.2/mods-available/"
                                              "xdebug.ini",
                                              "zend_extension",
                                              ";zend_extension")

                # PHP and Debug pull configuration
                if not os.path.exists('{0}22222/htdocs/fpm/status/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/fpm/status/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/fpm/status/'
                                .format(WOVariables.wo_webroot))
                open('{0}22222/htdocs/fpm/status/debug'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()
                open('{0}22222/htdocs/fpm/status/php'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()

                # Write info.php
                if not os.path.exists('{0}22222/htdocs/php/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/php/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/php'
                                .format(WOVariables.wo_webroot))

                with open("{0}22222/htdocs/php/info.php"
                          .format(WOVariables.wo_webroot),
                          encoding='utf-8', mode='w') as myfile:
                    myfile.write("<?php\nphpinfo();\n?>")

                WOFileUtils.chown(self, "{0}22222"
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user, recursive=True)

                WOGit.add(self, ["/etc/php"], msg="Adding PHP into Git")
                WOService.restart_service(self, 'php7.2-fpm')

            # PHP7.3 configuration for debian
            if (WOVariables.wo_platform_distro == 'debian' and
                    set(WOVariables.wo_php73).issubset(set(apt_packages))):
                # Create log directories
                if not os.path.exists('/var/log/php/7.3/'):
                    Log.debug(self, 'Creating directory /var/log/php/7.3/')
                    os.makedirs('/var/log/php/7.3/')

                # Parse etc/php/7.3/fpm/php.ini
                config = configparser.ConfigParser()
                Log.debug(self, "configuring php file /etc/php/7.3/fpm/php.ini")
                config.read('/etc/php/7.3/fpm/php.ini')
                config['PHP']['expose_php'] = 'Off'
                config['PHP']['post_max_size'] = '100M'
                config['PHP']['upload_max_filesize'] = '100M'
                config['PHP']['max_execution_time'] = '300'
                config['PHP']['date.timezone'] = WOVariables.wo_timezone
                with open('/etc/php/7.3/fpm/php.ini',
                          encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "Writting php configuration into "
                              "/etc/php/7.3/fpm/php.ini")
                    config.write(configfile)

                # Parse /etc/php/7.3/fpm/php-fpm.conf
                data = dict(pid="/run/php/php7.3-fpm.pid", error_log="/var/log/php7.3-fpm.log",
                            include="/etc/php/7.3/fpm/pool.d/*.conf")
                Log.debug(self, "writting php 7.3 configuration into "
                          "/etc/php/7.3/fpm/php-fpm.conf")
                wo_php_fpm = open('/etc/php/7.3/fpm/php-fpm.conf',
                                  encoding='utf-8', mode='w')
                self.app.render((data), 'php-fpm.mustache', out=wo_php_fpm)
                wo_php_fpm.close()

                # Parse /etc/php/7.3/fpm/pool.d/www.conf
                config = configparser.ConfigParser()
                config.read_file(codecs.open('/etc/php/7.3/fpm/pool.d/www.conf',
                                             "r", "utf8"))
                config['www']['ping.path'] = '/ping'
                config['www']['pm.status_path'] = '/status'
                config['www']['pm.max_requests'] = '500'
                config['www']['pm.max_children'] = '100'
                config['www']['pm.start_servers'] = '20'
                config['www']['pm.min_spare_servers'] = '10'
                config['www']['pm.max_spare_servers'] = '30'
                config['www']['request_terminate_timeout'] = '300'
                config['www']['pm'] = 'ondemand'
                config['www']['chdir'] = '/'
                config['www']['prefix'] = '/var/run/php'
                config['www']['listen'] = 'php73-fpm.sock'
                config['www']['listen.backlog'] = '32768'
                with codecs.open('/etc/php/7.3/fpm/pool.d/www.conf',
                                 encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "writting PHP 7.3 configuration into "
                              "/etc/php/7.3/fpm/pool.d/www.conf")
                    config.write(configfile)

                # Generate /etc/php/7.3/fpm/pool.d/debug.conf
                WOFileUtils.copyfile(self, "/etc/php/7.3/fpm/pool.d/www.conf",
                                     "/etc/php/7.3/fpm/pool.d/debug.conf")
                WOFileUtils.searchreplace(self, "/etc/php/7.3/fpm/pool.d/"
                                          "debug.conf", "[www]", "[debug]")
                config = configparser.ConfigParser()
                config.read('/etc/php/7.3/fpm/pool.d/debug.conf')
                config['debug']['listen'] = '127.0.0.1:9173'
                config['debug']['rlimit_core'] = 'unlimited'
                config['debug']['slowlog'] = '/var/log/php/7.3/slow.log'
                config['debug']['request_slowlog_timeout'] = '10s'
                with open('/etc/php/7.3/fpm/pool.d/debug.conf',
                          encoding='utf-8', mode='w') as confifile:
                    Log.debug(self, "writting PHP 7.3 configuration into "
                              "/etc/php/7.3/fpm/pool.d/debug.conf")
                    config.write(confifile)

                with open("/etc/php/7.3/fpm/pool.d/debug.conf",
                          encoding='utf-8', mode='a') as myfile:
                    myfile.write("php_admin_value[xdebug.profiler_output_dir] "
                                 "= /tmp/ \nphp_admin_value[xdebug.profiler_"
                                 "output_name] = cachegrind.out.%p-%H-%R "
                                 "\nphp_admin_flag[xdebug.profiler_enable"
                                 "_trigger] = on \nphp_admin_flag[xdebug."
                                 "profiler_enable] = off\n")

                # Disable xdebug
                if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\' /etc/php/7.3/mods-available/xdebug.ini"):
                    WOFileUtils.searchreplace(self, "/etc/php/7.3/mods-available/"
                                              "xdebug.ini",
                                              "zend_extension",
                                              ";zend_extension")

                # PHP and Debug pull configuration
                if not os.path.exists('{0}22222/htdocs/fpm/status/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/fpm/status/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/fpm/status/'
                                .format(WOVariables.wo_webroot))
                open('{0}22222/htdocs/fpm/status/debug'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()
                open('{0}22222/htdocs/fpm/status/php'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()

                # Write info.php
                if not os.path.exists('{0}22222/htdocs/php/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/php/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/php'
                                .format(WOVariables.wo_webroot))

                with open("{0}22222/htdocs/php/info.php"
                          .format(WOVariables.wo_webroot),
                          encoding='utf-8', mode='w') as myfile:
                    myfile.write("<?php\nphpinfo();\n?>")

                WOFileUtils.chown(self, "{0}22222"
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user, recursive=True)

                WOGit.add(self, ["/etc/php"], msg="Adding PHP into Git")
                WOService.restart_service(self, 'php7.3-fpm')

            # preconfiguration for php7.3
            if (WOVariables.wo_platform_distro == 'ubuntu' and
                    set(WOVariables.wo_php73).issubset(set(apt_packages))):
                # Create log directories
                if not os.path.exists('/var/log/php/7.3/'):
                    Log.debug(self, 'Creating directory /var/log/php/7.3/')
                    os.makedirs('/var/log/php/7.3/')

                # Parse etc/php/7.2/fpm/php.ini
                config = configparser.ConfigParser()
                Log.debug(self, "configuring php file /etc/php/7.3/fpm/php.ini")
                config.read('/etc/php/7.3/fpm/php.ini')
                config['PHP']['expose_php'] = 'Off'
                config['PHP']['post_max_size'] = '64M'
                config['PHP']['upload_max_filesize'] = '64M'
                config['PHP']['max_execution_time'] = '300'
                config['PHP']['date.timezone'] = WOVariables.wo_timezone
                with open('/etc/php/7.3/fpm/php.ini',
                          encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "Writting php configuration into "
                              "/etc/php/7.3/fpm/php.ini")
                    config.write(configfile)

                # Parse /etc/php/7.2/fpm/php-fpm.conf
                data = dict(pid="/run/php/php7.3-fpm.pid", error_log="/var/log/php/7.3/fpm.log",
                            include="/etc/php/7.3/fpm/pool.d/*.conf")
                Log.debug(self, "writting php 7.3 configuration into "
                          "/etc/php/7.3/fpm/php-fpm.conf")
                wo_php_fpm = open('/etc/php/7.3/fpm/php-fpm.conf',
                                  encoding='utf-8', mode='w')
                self.app.render((data), 'php-fpm.mustache', out=wo_php_fpm)
                wo_php_fpm.close()

                # Parse /etc/php/7.3/fpm/pool.d/www.conf
                config = configparser.ConfigParser()
                config.read_file(codecs.open('/etc/php/7.3/fpm/pool.d/www.conf',
                                             "r", "utf8"))
                config['www']['ping.path'] = '/ping'
                config['www']['pm.status_path'] = '/status'
                config['www']['pm.max_requests'] = '100'
                config['www']['pm.max_children'] = '25'
                config['www']['pm.start_servers'] = '5'
                config['www']['pm.min_spare_servers'] = '2'
                config['www']['pm.max_spare_servers'] = '5'
                config['www']['request_terminate_timeout'] = '100'
                config['www']['pm'] = 'ondemand'
                config['www']['chdir'] = '/'
                config['www']['prefix'] = '/var/run/php'
                config['www']['listen'] = 'php73-fpm.sock'
                config['www']['listen.backlog'] = '32768'
                with codecs.open('/etc/php/7.3/fpm/pool.d/www.conf',
                                 encoding='utf-8', mode='w') as configfile:
                    Log.debug(self, "writting PHP 7.3 configuration into "
                              "/etc/php/7.3/fpm/pool.d/www.conf")
                    config.write(configfile)

                # Generate /etc/php/7.3/fpm/pool.d/debug.conf
                WOFileUtils.copyfile(self, "/etc/php/7.3/fpm/pool.d/www.conf",
                                     "/etc/php/7.3/fpm/pool.d/debug.conf")
                WOFileUtils.searchreplace(self, "/etc/php/7.3/fpm/pool.d/"
                                          "debug.conf", "[www]", "[debug]")
                config = configparser.ConfigParser()
                config.read('/etc/php/7.3/fpm/pool.d/debug.conf')
                config['debug']['listen'] = '127.0.0.1:9173'
                config['debug']['rlimit_core'] = 'unlimited'
                config['debug']['slowlog'] = '/var/log/php/7.3/slow.log'
                config['debug']['request_slowlog_timeout'] = '10s'
                with open('/etc/php/7.3/fpm/pool.d/debug.conf',
                          encoding='utf-8', mode='w') as confifile:
                    Log.debug(self, "writting PHP 7.3 configuration into "
                              "/etc/php/7.3/fpm/pool.d/debug.conf")
                    config.write(confifile)

                with open("/etc/php/7.3/fpm/pool.d/debug.conf",
                          encoding='utf-8', mode='a') as myfile:
                    myfile.write("php_admin_value[xdebug.profiler_output_dir] "
                                 "= /tmp/ \nphp_admin_value[xdebug.profiler_"
                                 "output_name] = cachegrind.out.%p-%H-%R "
                                 "\nphp_admin_flag[xdebug.profiler_enable"
                                 "_trigger] = on \nphp_admin_flag[xdebug."
                                 "profiler_enable] = off\n")

                # Disable xdebug
                if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\' /etc/php/7.3/mods-available/xdebug.ini"):
                    WOFileUtils.searchreplace(self, "/etc/php/7.3/mods-available/"
                                              "xdebug.ini",
                                              "zend_extension",
                                              ";zend_extension")

                # PHP and Debug pull configuration
                if not os.path.exists('{0}22222/htdocs/fpm/status/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/fpm/status/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/fpm/status/'
                                .format(WOVariables.wo_webroot))
                open('{0}22222/htdocs/fpm/status/debug'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()
                open('{0}22222/htdocs/fpm/status/php'
                     .format(WOVariables.wo_webroot),
                     encoding='utf-8', mode='a').close()

                # Write info.php
                if not os.path.exists('{0}22222/htdocs/php/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, 'Creating directory '
                              '{0}22222/htdocs/php/ '
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/php'
                                .format(WOVariables.wo_webroot))

                with open("{0}22222/htdocs/php/info.php"
                          .format(WOVariables.wo_webroot),
                          encoding='utf-8', mode='w') as myfile:
                    myfile.write("<?php\nphpinfo();\n?>")

                WOFileUtils.chown(self, "{0}22222"
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user, recursive=True)

                WOGit.add(self, ["/etc/php"], msg="Adding PHP into Git")
                WOService.restart_service(self, 'php7.3-fpm')

            if set(WOVariables.wo_mysql).issubset(set(apt_packages)):
                if not os.path.isfile("/etc/mysql/my.cnf"):
                    config = ("[mysqld]\nwait_timeout = 30\n"
                              "interactive_timeout=60\nperformance_schema = 0"
                              "\nquery_cache_type = 1")
                    config_file = open("/etc/mysql/my.cnf",
                                       encoding='utf-8', mode='w')
                    config_file.write(config)
                    config_file.close()
                else:
                    try:
                        WOShellExec.cmd_exec(self, "sed -i \"/#max_conn"
                                             "ections/a wait_timeout = 30 \\n"
                                             "interactive_timeout = 60 \\n"
                                             "performance_schema = 0\\n"
                                             "query_cache_type = 1 \" "
                                             "/etc/mysql/my.cnf")
                    except CommandExecutionError as e:
                        Log.error(self, "Unable to update MySQL file")

                WOFileUtils.chmod(self, "/usr/bin/mysqltuner", 0o775)

                WOGit.add(self, ["/etc/mysql"], msg="Adding MySQL into Git")
                WOService.reload_service(self, 'mysql')

        if len(packages):
            if any('/usr/local/bin/wp' == x[1] for x in packages):
                Log.debug(self, "Setting Privileges to /usr/local/bin/wp file ")
                WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

            if any('/tmp/pma.tar.gz' == x[1]
                    for x in packages):
                WOExtract.extract(self, '/tmp/pma.tar.gz', '/tmp/')
                Log.debug(self, 'Extracting file /tmp/pma.tar.gz to '
                          'location /tmp/')
                if not os.path.exists('{0}22222/htdocs/db'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, "Creating new  directory "
                              "{0}22222/htdocs/db"
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/db'
                                .format(WOVariables.wo_webroot))
                shutil.move('/tmp/phpmyadmin-STABLE/',
                            '{0}22222/htdocs/db/pma/'
                            .format(WOVariables.wo_webroot))
                shutil.copyfile('{0}22222/htdocs/db/pma/config.sample.inc.php'
                                .format(WOVariables.wo_webroot),
                                '{0}22222/htdocs/db/pma/config.inc.php'
                                .format(WOVariables.wo_webroot))
                Log.debug(self, 'Setting Blowfish Secret Key FOR COOKIE AUTH to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVariables.wo_webroot))
                blowfish_key = ''.join([random.choice
                                        (string.ascii_letters + string.digits)
                                        for n in range(25)])
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma/config.inc.php'
                                          .format(WOVariables.wo_webroot),
                                          "$cfg[\'blowfish_secret\'] = \'\';", "$cfg[\'blowfish_secret\'] = \'{0}\';"
                                          .format(blowfish_key))
                Log.debug(self, 'Setting HOST Server For Mysql to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVariables.wo_webroot))
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma/config.inc.php'
                                          .format(WOVariables.wo_webroot),
                                          "$cfg[\'Servers\'][$i][\'host\'] = \'localhost\';", "$cfg[\'Servers\'][$i][\'host\'] = \'{0}\';"
                                          .format(WOVariables.wo_mysql_host))
                Log.debug(self, 'Setting Privileges of webroot permission to  '
                          '{0}22222/htdocs/db/pma file '
                          .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)
            if any('/tmp/memcached.tar.gz' == x[1]
                    for x in packages):
                Log.debug(self, "Extracting memcached.tar.gz to location"
                          " {0}22222/htdocs/cache/memcached "
                          .format(WOVariables.wo_webroot))
                WOExtract.extract(self, '/tmp/memcached.tar.gz',
                                  '{0}22222/htdocs/cache/memcached'
                                  .format(WOVariables.wo_webroot))
                Log.debug(self, "Setting Privileges to "
                          "{0}22222/htdocs/cache/memcached file"
                          .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)

            if any('/tmp/webgrind.tar.gz' == x[1]
                    for x in packages):
                Log.debug(self, "Extracting file webgrind.tar.gz to "
                          "location /tmp/ ")
                WOExtract.extract(self, '/tmp/webgrind.tar.gz', '/tmp/')
                if not os.path.exists('{0}22222/htdocs/php'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, "Creating directroy "
                              "{0}22222/htdocs/php"
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/php'
                                .format(WOVariables.wo_webroot))
                shutil.move('/tmp/webgrind-master/',
                            '{0}22222/htdocs/php/webgrind'
                            .format(WOVariables.wo_webroot))

                WOFileUtils.searchreplace(self, "{0}22222/htdocs/php/webgrind/"
                                          "config.php"
                                          .format(WOVariables.wo_webroot),
                                          "/usr/local/bin/dot", "/usr/bin/dot")
                WOFileUtils.searchreplace(self, "{0}22222/htdocs/php/webgrind/"
                                          "config.php"
                                          .format(WOVariables.wo_webroot),
                                          "Europe/Copenhagen",
                                          WOVariables.wo_timezone)

                WOFileUtils.searchreplace(self, "{0}22222/htdocs/php/webgrind/"
                                          "config.php"
                                          .format(WOVariables.wo_webroot),
                                          "90", "100")

                Log.debug(self, "Setting Privileges of webroot permission to "
                          "{0}22222/htdocs/php/webgrind/ file "
                          .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)

            if any('/tmp/anemometer.tar.gz' == x[1]
                    for x in packages):
                Log.debug(self, "Extracting file anemometer.tar.gz to "
                          "location /tmp/ ")
                WOExtract.extract(self, '/tmp/anemometer.tar.gz', '/tmp/')
                if not os.path.exists('{0}22222/htdocs/db/'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, "Creating directory")
                    os.makedirs('{0}22222/htdocs/db/'
                                .format(WOVariables.wo_webroot))
                shutil.move('/tmp/Anemometer-master',
                            '{0}22222/htdocs/db/anemometer'
                            .format(WOVariables.wo_webroot))
                chars = ''.join(random.sample(string.ascii_letters, 8))
                try:
                    WOShellExec.cmd_exec(self, 'mysql < {0}22222/htdocs/db'
                                         '/anemometer/install.sql'
                                         .format(WOVariables.wo_webroot))
                except CommandExecutionError as e:
                    raise SiteError("Unable to import Anemometer database")

                WOMysql.execute(self, 'grant select on *.* to \'anemometer\''
                                '@\'{0}\' IDENTIFIED'
                                ' BY \'{1}\''.format(self.app.config.get('mysql',
                                                                         'grant-host'), chars))
                Log.debug(self, "grant all on slow-query-log.*"
                          " to anemometer@root_user IDENTIFIED BY password ")
                WOMysql.execute(self, 'grant all on slow_query_log.* to'
                                '\'anemometer\'@\'{0}\' IDENTIFIED'
                                ' BY \'{1}\''.format(self.app.config.get(
                                                     'mysql', 'grant-host'),
                                                     chars),
                                errormsg="cannot grant priviledges", log=False)

                # Custom Anemometer configuration
                Log.debug(self, "configration Anemometer")
                data = dict(host=WOVariables.wo_mysql_host, port='3306',
                            user='anemometer', password=chars)
                wo_anemometer = open('{0}22222/htdocs/db/anemometer'
                                     '/conf/config.inc.php'
                                     .format(WOVariables.wo_webroot),
                                     encoding='utf-8', mode='w')
                self.app.render((data), 'anemometer.mustache',
                                out=wo_anemometer)
                wo_anemometer.close()

            if any('/usr/bin/pt-query-advisor' == x[1]
                    for x in packages):
                WOFileUtils.chmod(self, "/usr/bin/pt-query-advisor", 0o775)

            if any('/tmp/pra.tar.gz' == x[1]
                    for x in packages):
                Log.debug(self, 'Extracting file /tmp/pra.tar.gz to '
                          'loaction /tmp/')
                WOExtract.extract(self, '/tmp/pra.tar.gz', '/tmp/')
                if not os.path.exists('{0}22222/htdocs/cache/redis'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, "Creating new directory "
                              "{0}22222/htdocs/cache/redis"
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/htdocs/cache/redis'
                                .format(WOVariables.wo_webroot))
                shutil.move('/tmp/phpRedisAdmin-master/',
                            '{0}22222/htdocs/cache/redis/phpRedisAdmin'
                            .format(WOVariables.wo_webroot))

                Log.debug(self, 'Extracting file /tmp/predis.tar.gz to '
                          'loaction /tmp/')
                WOExtract.extract(self, '/tmp/predis.tar.gz', '/tmp/')
                shutil.move('/tmp/predis-1.0.1/',
                            '{0}22222/htdocs/cache/redis/phpRedisAdmin/vendor'
                            .format(WOVariables.wo_webroot))

                Log.debug(self, 'Setting Privileges of webroot permission to  '
                          '{0}22222/htdocs/cache/ file '
                          .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)

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
                (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
                (not self.app.pargs.redis) and
                (not self.app.pargs.phpredisadmin) and
                    (not self.app.pargs.php73)):
                self.app.pargs.web = True
                self.app.pargs.admin = True

            if self.app.pargs.all:
                self.app.pargs.web = True
                self.app.pargs.admin = True

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
                self.app.pargs.utils = True

            if self.app.pargs.redis:
                if not WOAptGet.is_installed(self, 'redis-server'):
                    apt_packages = apt_packages + WOVariables.wo_redis
                    self.app.pargs.php = True
                else:
                    Log.info(self, "Redis already installed")

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
                            Log.info(self, "WordOps detected an already installed nginx package."
                                     "It may or may not have required modules.\n")
                            apt = ["nginx"] + WOVariables.wo_nginx
                            self.post_pref(apt, packages)
                else:
                    Log.debug(self, "Nginx Stable already installed")

            # PHP 7.2
            if self.app.pargs.php:
                Log.debug(self, "Setting apt_packages variable for PHP 7.2")
                if not (WOAptGet.is_installed(self, 'php7.2-fpm')):
                    apt_packages = apt_packages + WOVariables.wo_php + WOVariables.wo_php_extra
                else:
                    Log.debug(self, "PHP 7.2 already installed")
                    Log.info(self, "PHP 7.2 already installed")

            # PHP 7.3
            if self.app.pargs.php73:
                Log.debug(self, "Setting apt_packages variable for PHP 7.3")
                if not WOAptGet.is_installed(self, 'php7.3-fpm'):
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

            # PHPMYADMIN
            if self.app.pargs.phpmyadmin:
                Log.debug(self, "Setting packages varible for phpMyAdmin ")
                packages = packages + [["https://github.com/phpmyadmin/"
                                        "phpmyadmin/archive/STABLE.tar.gz",
                                        "/tmp/pma.tar.gz", "phpMyAdmin"]]
            # PHPREDISADMIN
            if self.app.pargs.phpredisadmin:
                Log.debug(self, "Setting packages varible for phpRedisAdmin")
                packages = packages + [["https://github.com/ErikDubbelboer/"
                                        "phpRedisAdmin/archive/master.tar.gz",
                                        "/tmp/pra.tar.gz", "phpRedisAdmin"],
                                       ["https://github.com/nrk/predis/"
                                        "archive/v1.1.1.tar.gz",
                                        "/tmp/predis.tar.gz", "Predis"]]
            # ADMINER
            if self.app.pargs.adminer:
                Log.debug(self, "Setting packages variable for Adminer ")
                packages = packages + [["https://www.adminer.org/static/download/"
                                        "{0}/adminer-{0}.php"
                                        "".format(WOVariables.wo_adminer),
                                        "{0}22222/"
                                        "htdocs/db/adminer/index.php"
                                        .format(WOVariables.wo_webroot),
                                        "Adminer"]]
            # UTILS
            if self.app.pargs.utils:
                Log.debug(self, "Setting packages variable for utils")
                packages = packages + [["https://github.com/elijaa/"
                                        "phpmemcachedadmin/archive/"
                                        "1.3.0.tar.gz",
                                        '/tmp/memcached.tar.gz',
                                        'phpMemcachedAdmin'],
                                       ["https://raw.githubusercontent.com"
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
                                        '/tmp/webgrind.tar.gz', 'Webgrind'],
                                       ["http://bazaar.launchpad.net/~"
                                        "percona-toolkit-dev/percona-toolkit/"
                                        "2.1/download/head:/ptquerydigest-"
                                        "20110624220137-or26tn4"
                                        "expb9ul2a-16/pt-query-digest",
                                        "/usr/bin/pt-query-advisor",
                                        "pt-query-advisor"],
                                       ["https://github.com/box/Anemometer/"
                                        "archive/master.tar.gz",
                                        '/tmp/anemometer.tar.gz', 'Anemometer']
                                       ]
        except Exception as e:
            pass

        if len(apt_packages) or len(packages):
            Log.debug(self, "Calling pre_pref")
            self.pre_pref(apt_packages)
            if len(apt_packages):
                WOSwap.add(self)
                Log.info(self, "Updating apt-cache, please wait...")
                WOAptGet.update(self)
                Log.info(self, "Installing packages, please wait...")
                WOAptGet.install(self, apt_packages)
            if len(packages):
                Log.debug(self, "Downloading following: {0}".format(packages))
                WODownload.download(self, packages)
            Log.debug(self, "Calling post_pref")
            self.post_pref(apt_packages, packages)
            if 'redis-server' in apt_packages:
                # set redis.conf parameter
                # set maxmemory 10% for ram below 512MB and 20% for others
                # set maxmemory-policy allkeys-lru
                if os.path.isfile("/etc/redis/redis.conf"):
                    if WOVariables.wo_ram < 512:
                        Log.debug(self, "Setting maxmemory variable to {0} in redis.conf"
                                  .format(int(WOVariables.wo_ram*1024*1024*0.1)))
                        WOShellExec.cmd_exec(self, "sed -i 's/# maxmemory <bytes>/maxmemory {0}/' /etc/redis/redis.conf"
                                             .format(int(WOVariables.wo_ram*1024*1024*0.1)))
                        Log.debug(
                            self, "Setting maxmemory-policy variable to allkeys-lru in redis.conf")
                        WOShellExec.cmd_exec(self, "sed -i 's/# maxmemory-policy.*/maxmemory-policy allkeys-lru/' "
                                                   "/etc/redis/redis.conf")
                        WOService.restart_service(self, 'redis-server')
                    else:
                        Log.debug(self, "Setting maxmemory variable to {0} in redis.conf"
                                  .format(int(WOVariables.wo_ram*1024*1024*0.2)))
                        WOShellExec.cmd_exec(self, "sed -i 's/# maxmemory <bytes>/maxmemory {0}/' /etc/redis/redis.conf"
                                             .format(int(WOVariables.wo_ram*1024*1024*0.2)))
                        Log.debug(
                            self, "Setting maxmemory-policy variable to allkeys-lru in redis.conf")
                        WOShellExec.cmd_exec(self, "sed -i 's/# maxmemory-policy.*/maxmemory-policy allkeys-lru/' "
                                                   "/etc/redis/redis.conf")
                        WOService.restart_service(self, 'redis-server')
            if disp_msg:
                if len(self.msg):
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
            (not self.app.pargs.all) and (not self.app.pargs.redis) and
                (not self.app.pargs.phpredisadmin)):
            self.app.pargs.web = True
            self.app.pargs.admin = True

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
        # NGINX
        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Removing apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx
            else:
                Log.error(self, "Cannot Remove! Nginx Stable version not found.")
        # PHP 7.2
        if self.app.pargs.php:
            Log.debug(self, "Removing apt_packages variable of PHP")
            if not WOAptGet.is_installed(self, 'php7.2-fpm'):
                apt_packages = apt_packages + WOVariables.wo_php + WOVariables.wo_php_extra

        # PHP7.3
        if self.app.pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                apt_packages = apt_packages + WOVariables.wo_php73

        # REDIS
        if self.app.pargs.redis:
            Log.debug(self, "Remove apt_packages variable of Redis")
            apt_packages = apt_packages + WOVariables.wo_redis

        # MariaDB
        if self.app.pargs.mysql:
            Log.debug(self, "Removing apt_packages variable of MySQL")
            apt_packages = apt_packages + WOVariables.wo_mysql
            packages = packages + ['/usr/bin/mysqltuner']
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
        # PHPREDISADMIN
        if self.app.pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            packages = packages + ['{0}22222/htdocs/cache/redis/phpRedisAdmin'
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
                                   '{0}22222/htdocs/cache/memcached'
                                   .format(WOVariables.wo_webroot),
                                   '/usr/bin/pt-query-advisor',
                                   '{0}22222/htdocs/db/anemometer'
                                   .format(WOVariables.wo_webroot)]

        if len(packages) or len(apt_packages):
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

                if len(packages):
                    WOFileUtils.remove(self, packages)
                    WOAptGet.auto_remove(self)

                if len(apt_packages):
                    Log.debug(self, "Removing apt_packages")
                    Log.info(self, "Removing packages, please wait...")
                    WOAptGet.remove(self, apt_packages)
                    WOAptGet.auto_remove(self)

                Log.info(self, "Successfully removed packages")

                # Added for Ondrej Repo missing package Fix
                if self.app.pargs.php:
                    if WOAptGet.is_installed(self, 'php7.2-fpm'):
                        Log.info(self, "PHP7.2-fpm found on system.")
                        Log.info(
                            self, "Verifying and installing missing packages,")
                        WOShellExec.cmd_exec(
                            self, "apt-get install -y php-memcached php-igbinary")

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
            (not self.app.pargs.all) and (not self.app.pargs.redis) and
                (not self.app.pargs.phpredisadmin)):
            self.app.pargs.web = True
            self.app.pargs.admin = True

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

        # NGINX
        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom'):
                Log.debug(self, "Purge apt_packages variable of Nginx")
                apt_packages = apt_packages + WOVariables.wo_nginx
            else:
                Log.error(self, "Cannot Purge! Nginx Stable version not found.")

        # PHP
        if self.app.pargs.php:
            Log.debug(self, "Purge apt_packages variable PHP")
            if not WOAptGet.is_installed(self, 'php7.2-fpm'):
                apt_packages = apt_packages + WOVariables.wo_php + WOVariables.wo_php_extra
            else:
                Log.error(self, "Cannot Purge PHP 7.2. not found.")

        # PHP 7.3
        if self.app.pargs.php73:
            Log.debug(self, "Removing apt_packages variable of PHP 7.3")
            if not WOAptGet.is_installed(self, 'php7.3-fpm'):
                apt_packages = apt_packages + WOVariables.wo_php73
            else:
                Log.error(self, "Cannot Purge PHP 7.3. not found.")
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

        # PHPREDISADMIN
        if self.app.pargs.phpredisadmin:
            Log.debug(self, "Removing package variable of phpRedisAdmin ")
            packages = packages + ['{0}22222/htdocs/cache/redis/phpRedisAdmin'
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
                                   '{0}22222/htdocs/cache/memcached'
                                   .format(WOVariables.wo_webroot),
                                   '/usr/bin/pt-query-advisor',
                                   '{0}22222/htdocs/db/anemometer'
                                   .format(WOVariables.wo_webroot)
                                   ]

        if len(packages) or len(apt_packages):
            wo_prompt = input('Are you sure you to want to purge '
                              'from server '
                              'along with their configuration'
                              ' packages,\nAny answer other than '
                              '"yes" will be stop this '
                              'operation :')

            if wo_prompt == 'YES' or wo_prompt == 'yes':

                if (set(["nginx-custom"]).issubset(set(apt_packages))):
                    WOService.stop_service(self, 'nginx')

                if len(apt_packages):
                    Log.info(self, "Purging packages, please wait...")
                    WOAptGet.remove(self, apt_packages, purge=True)
                    WOAptGet.auto_remove(self)

                if len(packages):
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
