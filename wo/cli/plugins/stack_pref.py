import codecs
import configparser
import os
import random
import shutil
import string
import requests
import psutil

from wo.cli.plugins.site_functions import *
from wo.cli.plugins.stack_services import WOStackStatusController
from wo.core.apt_repo import WORepo
from wo.core.aptget import WOAptGet
from wo.core.cron import WOCron
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.services import WOService
from wo.core.shellexec import CommandExecutionError, WOShellExec
from wo.core.variables import WOVariables


def pre_pref(self, apt_packages):
    """Pre settings to do before installation packages"""

    if set(WOVariables.wo_mysql).issubset(set(apt_packages)):
        # add mariadb repository excepted on raspbian and ubuntu 19.04
        if (not WOVariables.wo_distro == 'raspbian'):
            Log.info(self, "Adding repository for MySQL, please wait...")
            mysql_pref = ("Package: *\nPin: origin "
                          "sfo1.mirrors.digitalocean.com"
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
        # generate random 24 characters root password
        chars = ''.join(random.sample(string.ascii_letters, 24))
        # configure MySQL non-interactive install
        if (not WOVariables.wo_distro == 'raspbian'):
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
                Log.debug(self, "{0}".format(e))
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
                Log.debug(self, "{0}".format(e))
                Log.error("Failed to initialize MySQL package")
        else:
            Log.debug(self, "Pre-seeding MySQL")
            Log.debug(self, "echo \"mariadb-server-10.1 "
                      "mysql-server/root_password "
                      "password \" | "
                      "debconf-set-selections")
            try:
                WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.1 "
                                     "mysql-server/root_password "
                                     "password {chars}\" | "
                                     "debconf-set-selections"
                                     .format(chars=chars),
                                     log=False)
            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))
                Log.error("Failed to initialize MySQL package")

            Log.debug(self, "echo \"mariadb-server-10.1 "
                      "mysql-server/root_password_again "
                      "password \" | "
                      "debconf-set-selections")
            try:
                WOShellExec.cmd_exec(self, "echo \"mariadb-server-10.1 "
                                     "mysql-server/root_password_again "
                                     "password {chars}\" | "
                                     "debconf-set-selections"
                                     .format(chars=chars),
                                     log=False)
            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Failed to initialize MySQL package")
        # generate my.cnf root credentials
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

    # add nginx repository
    if set(WOVariables.wo_nginx).issubset(set(apt_packages)):
        Log.info(self, "Adding repository for NGINX, please wait...")
        if (WOVariables.wo_distro == 'ubuntu'):
            WORepo.add(self, ppa=WOVariables.wo_nginx_repo)
            Log.debug(self, 'Adding ppa for Nginx')
        else:
            WORepo.add(self, repo_url=WOVariables.wo_nginx_repo)
            Log.debug(self, 'Adding repository for Nginx')
            WORepo.add_key(self, WOVariables.wo_nginx_key)

    # add php repository
    if (set(WOVariables.wo_php73).issubset(set(apt_packages)) or
            set(WOVariables.wo_php).issubset(set(apt_packages))):
        Log.info(self, "Adding repository for PHP, please wait...")
        if (WOVariables.wo_distro == 'ubuntu'):
            Log.debug(self, 'Adding ppa for PHP')
            WORepo.add(self, ppa=WOVariables.wo_php_repo)
        else:
            # Add repository for php
            if (WOVariables.wo_platform_codename == 'buster'):
                php_pref = ("Package: *\nPin: origin "
                            "packages.sury.org"
                            "\nPin-Priority: 1000\n")
                with open('/etc/apt/preferences.d/'
                          'PHP.pref', 'w') as php_pref_file:
                    php_pref_file.write(php_pref)
            Log.debug(self, 'Adding repo_url of php for debian')
            WORepo.add(self, repo_url=WOVariables.wo_php_repo)
            Log.debug(self, 'Adding deb.sury GPG key')
            WORepo.add_key(self, WOVariables.wo_php_key)
    # add redis repository
    if set(WOVariables.wo_redis).issubset(set(apt_packages)):
        Log.info(self, "Adding repository for Redis, please wait...")
        if WOVariables.wo_distro == 'ubuntu':
            Log.debug(self, 'Adding ppa for redis')
            WORepo.add(self, ppa=WOVariables.wo_redis_repo)


def post_pref(self, apt_packages, packages):
    """Post activity after installation of packages"""
    if (apt_packages):
        # Nginx configuration
        if set(WOVariables.wo_nginx).issubset(set(apt_packages)):
            # Nginx main configuration
            if os.path.isfile('/etc/nginx/nginx.conf'):
                if (WOVariables.wo_distro == 'ubuntu' or
                        WOVariables.wo_platform_codename == 'buster'):
                    data = dict(tls13=True)
                else:
                    data = dict(tls13=False)
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/nginx.conf')
                wo_nginx = open('/etc/nginx/nginx.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'nginx-core.mustache', out=wo_nginx)
                wo_nginx.close()

            if not os.path.isfile('/etc/nginx/conf.d/gzip.conf'):
                data = dict()
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/gzip.conf')
                wo_nginx = open('/etc/nginx/conf.d/gzip.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'gzip.mustache', out=wo_nginx)
                wo_nginx.close()

            if not os.path.isfile('/etc/nginx/conf.d/brotli.conf.disabled'):
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/brotli.conf.disabled')
                wo_nginx = open('/etc/nginx/conf.d/brotli.conf.disabled',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'brotli.mustache', out=wo_nginx)
                wo_nginx.close()

            # Fix for white screen death with NGINX PLUS
            if not WOFileUtils.grep(self, '/etc/nginx/fastcgi_params',
                                    'SCRIPT_FILENAME'):
                with open('/etc/nginx/fastcgi_params',
                          encoding='utf-8', mode='a') as wo_nginx:
                    wo_nginx.write('fastcgi_param \tSCRIPT_FILENAME '
                                   '\t$request_filename;\n')

            if os.path.isfile('/etc/nginx/nginx.conf'):
                data = dict(php="9000", debug="9001",
                            php7="9070", debug7="9170")
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/upstream.conf')
                wo_nginx = open('/etc/nginx/conf.d/upstream.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'upstream.mustache', out=wo_nginx)
                wo_nginx.close()

                data = dict(phpconf=True if
                            WOAptGet.is_installed(self, 'php7.2-fpm')
                            else False)
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/stub_status.conf')
                wo_nginx = open('/etc/nginx/conf.d/stub_status.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'stub_status.mustache', out=wo_nginx)
                wo_nginx.close()

                data = dict()
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/webp.conf')
                wo_nginx = open('/etc/nginx/conf.d/webp.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'webp.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/cloudflare.conf')
                wo_nginx = open('/etc/nginx/conf.d/cloudflare.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'cloudflare.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/'
                          'map-wp-fastcgi-cache.conf')
                wo_nginx = open('/etc/nginx/conf.d/'
                                'map-wp-fastcgi-cache.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'map-wp.mustache',
                                out=wo_nginx)
                wo_nginx.close()

            # Setup Nginx common directory
            if not os.path.exists('/etc/nginx/common'):
                Log.debug(self, 'Creating directory'
                          '/etc/nginx/common')
                os.makedirs('/etc/nginx/common')

            if os.path.exists('/etc/nginx/common'):
                data = dict()

                # Common Configuration
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/locations-wo.conf')
                wo_nginx = open('/etc/nginx/common/locations-wo.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'locations.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/wpsubdir.conf')
                wo_nginx = open('/etc/nginx/common/wpsubdir.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wpsubdir.mustache',
                                out=wo_nginx)
                wo_nginx.close()
                data = dict(upstream="php72")
                # PHP 7.2 conf
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/php72.conf')
                wo_nginx = open('/etc/nginx/common/php72.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'php.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/redis-php72.conf')
                wo_nginx = open('/etc/nginx/common/redis-php72.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'redis.mustache',
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
                          'file /etc/nginx/common/wprocket-php72.conf')
                wo_nginx = open('/etc/nginx/common/wprocket-php72.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wprocket.mustache',
                                out=wo_nginx)
                wo_nginx.close()

            # PHP 7.3 conf
            if os.path.isdir("/etc/nginx/common"):
                data = dict(upstream="php73")

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/php73.conf')
                wo_nginx = open('/etc/nginx/common/php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'php.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/wpcommon-php73.conf')
                wo_nginx = open('/etc/nginx/common/wpcommon-php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wpcommon.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/wpfc-php73.conf')
                wo_nginx = open('/etc/nginx/common/wpfc-php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wpfc.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/wpsc-php73.conf')
                wo_nginx = open('/etc/nginx/common/wpsc-php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wpsc.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/wprocket-php73.conf')
                wo_nginx = open('/etc/nginx/common/wprocket-php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'wprocket.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/redis-php73.conf')
                wo_nginx = open('/etc/nginx/common/redis-php73.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'redis.mustache',
                                out=wo_nginx)
                wo_nginx.close()

                with open("/etc/nginx/common/release",
                          "a") as release_file:
                    release_file.write("v{0}"
                                       .format(WOVariables.wo_version))
                release_file.close()

            # Following files should not be overwrited

            if not os.path.isfile('/etc/nginx/common/acl.conf'):
                data = dict(webroot=WOVariables.wo_webroot)
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/common/acl.conf')
                wo_nginx = open('/etc/nginx/common/acl.conf',
                                encoding='utf-8', mode='w')
                self.app.render((data), 'acl.mustache',
                                out=wo_nginx)
                wo_nginx.close()
            if not os.path.isfile('/etc/nginx/conf.d/blockips.conf'):
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/blockips.conf')
                wo_nginx = open('/etc/nginx/conf.d/blockips.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'blockips.mustache', out=wo_nginx)
                wo_nginx.close()

            if not os.path.isfile('/etc/nginx/conf.d/fastcgi.conf'):
                Log.debug(self, 'Writting the nginx configuration to '
                          'file /etc/nginx/conf.d/fastcgi.conf')
                wo_nginx = open('/etc/nginx/conf.d/fastcgi.conf',
                                encoding='utf-8', mode='w')
                self.app.render(
                    (data), 'fastcgi.mustache', out=wo_nginx)
                wo_nginx.close()

            # add redis cache format if not already done
            if (os.path.isfile("/etc/nginx/nginx.conf") and
                not os.path.isfile("/etc/nginx/conf.d"
                                   "/redis.conf")):
                with open("/etc/nginx/conf.d/"
                          "redis.conf", "a") as redis_file:
                    redis_file.write("# Log format Settings\n"
                                     "log_format rt_cache_redis "
                                     "'$remote_addr "
                                     "$upstream_response_time "
                                     "$srcache_fetch_status "
                                     "[$time_local] '\n"
                                     "'$http_host \"$request\" $status"
                                     " $body_bytes_sent '\n"
                                     "'\"$http_referer\" "
                                     "\"$http_user_agent\"';\n")

                    # Nginx-Plus does not have nginx
                    # package structure like this
                    # So creating directories
            if not os.path.exists('/etc/nginx/sites-available'):
                Log.debug(self, 'Creating directory'
                          '/etc/nginx/sites-available')
                os.makedirs('/etc/nginx/sites-available')

            if not os.path.exists('/etc/nginx/sites-enabled'):
                Log.debug(self, 'Creating directory'
                          '/etc/nginx/sites-available')
                os.makedirs('/etc/nginx/sites-enabled')

                # 22222 port settings
            if not os.path.isfile("/etc/nginx/sites-available/22222"):
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
                                  for n in range(24)])
                try:
                    WOShellExec.cmd_exec(self, "printf \"WordOps:"
                                         "$(openssl passwd -crypt "
                                         "{password} 2> /dev/null)\n\""
                                         "> /etc/nginx/htpasswd-wo "
                                         "2>/dev/null"
                                         .format(password=passwd))
                except CommandExecutionError as e:
                    Log.debug(self, "{0}".format(e))
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

                if not os.path.exists('{0}22222/conf/nginx'
                                      .format(WOVariables.wo_webroot)):
                    Log.debug(self, "Creating directory "
                              "{0}22222/conf/nginx"
                              .format(WOVariables.wo_webroot))
                    os.makedirs('{0}22222/conf/nginx'
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
                        Log.debug(self, "{0}".format(e))
                        Log.error(
                            self, "Failed to generate HTTPS "
                            "certificate for 22222")

                if not os.path.isfile('{0}22222/conf/nginx/ssl.conf'
                                      .format(WOVariables.wo_webroot)):

                    with open("/var/www/22222/conf/nginx/"
                              "ssl.conf", "a") as php_file:
                        php_file.write("ssl_certificate "
                                       "/var/www/22222/cert/22222.crt;\n"
                                       "ssl_certificate_key "
                                       "/var/www/22222/cert/22222.key;\n")

                # Nginx Configation into GIT
                WOGit.add(self,
                          ["/etc/nginx"], msg="Adding Nginx into Git")
                WOService.reload_service(self, 'nginx')
                server_ip = requests.get('http://v4.wordops.eu')
                if set(["nginx"]).issubset(set(apt_packages)):
                    print("WordOps backend configuration was successful\n"
                          "You can access it on : https://{0}:22222"
                          .format(server_ip))
                    print("HTTP Auth User Name: WordOps" +
                          "\nHTTP Auth Password : {0}".format(passwd))
                    WOService.reload_service(self, 'nginx')
                else:
                    self.msg = (self.msg + ["HTTP Auth User "
                                            "Name: WordOps"] +
                                ["HTTP Auth Password : {0}"
                                 .format(passwd)])
                    self.msg = (self.msg + ["WordOps backend is available "
                                            "on https://{0}:22222 "
                                            "or https://{1}:22222"
                                            .format(server_ip.text,
                                                    WOVariables.wo_fqdn)])
            else:
                WOService.restart_service(self, 'nginx')

            # add rule for Nginx with UFW
            if WOAptGet.is_installed(self, 'ufw'):
                try:
                    WOShellExec.cmd_exec(self, "/usr/bin/ufw allow "
                                         "http")
                    WOShellExec.cmd_exec(self, "/usr/bin/ufw allow "
                                         "https")
                    WOShellExec.cmd_exec(self, "/usr/bin/ufw allow "
                                         "22222")
                except CommandExecutionError as e:
                    Log.debug(self, "{0}".format(e))
                    Log.error(self, "Unable to add UFW rule")

        # create nginx configuration for redis
        if set(WOVariables.wo_redis).issubset(set(apt_packages)):
            if os.path.isdir('/etc/nginx/common'):
                data = dict(upstream="php72")
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

        if set(WOVariables.wo_php).issubset(set(apt_packages)):
            # Create log directories
            if not os.path.exists('/var/log/php/7.2/'):
                Log.debug(self, 'Creating directory /var/log/php/7.2/')
                os.makedirs('/var/log/php/7.2/')

                # Parse etc/php/7.2/fpm/php.ini
            config = configparser.ConfigParser()
            Log.debug(self, "configuring php file "
                      "/etc/php/7.2/fpm/php.ini")
            config.read('/etc/php/7.2/fpm/php.ini')
            config['PHP']['expose_php'] = 'Off'
            config['PHP']['post_max_size'] = '100M'
            config['PHP']['upload_max_filesize'] = '100M'
            config['PHP']['max_execution_time'] = '300'
            config['PHP']['max_input_time'] = '300'
            config['PHP']['max_input_vars'] = '20000'
            config['Date']['date.timezone'] = WOVariables.wo_timezone
            config['opcache']['opcache.enable'] = '1'
            config['opcache']['opcache.interned_strings_buffer'] = '8'
            config['opcache']['opcache.max_accelerated_files'] = '10000'
            config['opcache']['opcache.memory_consumption'] = '256'
            config['opcache']['opcache.save_comments'] = '1'
            config['opcache']['opcache.revalidate_freq'] = '5'
            config['opcache']['opcache.consistency_checks'] = '0'
            config['opcache']['opcache.validate_timestamps'] = '1'
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
            config.read_file(codecs.open('/etc/php/7.2/fpm/'
                                         'pool.d/www.conf',
                                         "r", "utf8"))
            config['www']['ping.path'] = '/ping'
            config['www']['pm.status_path'] = '/status'
            config['www']['pm.max_requests'] = '1500'
            config['www']['pm.max_children'] = '50'
            config['www']['pm.start_servers'] = '10'
            config['www']['pm.min_spare_servers'] = '5'
            config['www']['pm.max_spare_servers'] = '15'
            config['www']['request_terminate_timeout'] = '300'
            config['www']['pm'] = 'ondemand'
            config['www']['chdir'] = '/'
            config['www']['prefix'] = '/var/run/php'
            config['www']['listen'] = 'php72-fpm.sock'
            config['www']['listen.mode'] = '0660'
            config['www']['listen.backlog'] = '32768'
            config['www']['catch_workers_output'] = 'yes'
            with codecs.open('/etc/php/7.2/fpm/pool.d/www.conf',
                             encoding='utf-8', mode='w') as configfile:
                Log.debug(self, "Writing PHP 7.2 configuration into "
                          "/etc/php/7.2/fpm/pool.d/www.conf")
                config.write(configfile)

            with open("/etc/php/7.2/fpm/pool.d/www.conf",
                      encoding='utf-8', mode='a') as myfile:
                myfile.write("\nphp_admin_value[open_basedir] "
                             "= \"/var/www/:/usr/share/php/:"
                             "/tmp/:/var/run/nginx-cache/:"
                             "/dev/shm:/dev/urandom\"\n")

            # Generate /etc/php/7.2/fpm/pool.d/www-two.conf
            WOFileUtils.copyfile(self, "/etc/php/7.2/fpm/pool.d/www.conf",
                                 "/etc/php/7.2/fpm/pool.d/www-two.conf")
            WOFileUtils.searchreplace(self, "/etc/php/7.2/fpm/pool.d/"
                                      "www-two.conf", "[www]", "[www-two]")
            config = configparser.ConfigParser()
            config.read('/etc/php/7.2/fpm/pool.d/www-two.conf')
            config['www-two']['listen'] = 'php72-two-fpm.sock'
            with open('/etc/php/7.2/fpm/pool.d/www-two.conf',
                      encoding='utf-8', mode='w') as confifile:
                Log.debug(self, "writting PHP7.2 configuration into "
                          "/etc/php/7.2/fpm/pool.d/www-two.conf")
                config.write(confifile)

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
            if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\'"
                                        " /etc/php/7.2/mods-available/"
                                        "xdebug.ini"):
                WOFileUtils.searchreplace(self, "/etc/php/7.2/"
                                          "mods-available/"
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
            open('{0}22222/htdocs/fpm/status/debug72'
                 .format(WOVariables.wo_webroot),
                 encoding='utf-8', mode='a').close()
            open('{0}22222/htdocs/fpm/status/php72'
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

        # PHP7.3 configuration
        if set(WOVariables.wo_php73).issubset(set(apt_packages)):
            # Create log directories
            if not os.path.exists('/var/log/php/7.3/'):
                Log.debug(self, 'Creating directory /var/log/php/7.3/')
                os.makedirs('/var/log/php/7.3/')

            # Parse etc/php/7.3/fpm/php.ini
            config = configparser.ConfigParser()
            Log.debug(self, "configuring php file /etc/php/7.3/"
                      "fpm/php.ini")
            config.read('/etc/php/7.3/fpm/php.ini')
            config['PHP']['expose_php'] = 'Off'
            config['PHP']['post_max_size'] = '100M'
            config['PHP']['upload_max_filesize'] = '100M'
            config['PHP']['max_execution_time'] = '300'
            config['PHP']['max_input_time'] = '300'
            config['PHP']['max_input_vars'] = '20000'
            config['Date']['date.timezone'] = WOVariables.wo_timezone
            config['opcache']['opcache.enable'] = '1'
            config['opcache']['opcache.interned_strings_buffer'] = '8'
            config['opcache']['opcache.max_accelerated_files'] = '10000'
            config['opcache']['opcache.memory_consumption'] = '256'
            config['opcache']['opcache.save_comments'] = '1'
            config['opcache']['opcache.revalidate_freq'] = '5'
            config['opcache']['opcache.consistency_checks'] = '0'
            config['opcache']['opcache.validate_timestamps'] = '1'
            with open('/etc/php/7.3/fpm/php.ini',
                      encoding='utf-8', mode='w') as configfile:
                Log.debug(self, "Writting php configuration into "
                          "/etc/php/7.3/fpm/php.ini")
                config.write(configfile)

            # Parse /etc/php/7.3/fpm/php-fpm.conf
            data = dict(pid="/run/php/php7.3-fpm.pid",
                            error_log="/var/log/php7.3-fpm.log",
                            include="/etc/php/7.3/fpm/pool.d/*.conf")
            Log.debug(self, "writting php 7.3 configuration into "
                      "/etc/php/7.3/fpm/php-fpm.conf")
            wo_php_fpm = open('/etc/php/7.3/fpm/php-fpm.conf',
                              encoding='utf-8', mode='w')
            self.app.render((data), 'php-fpm.mustache', out=wo_php_fpm)
            wo_php_fpm.close()

            # Parse /etc/php/7.3/fpm/pool.d/www.conf
            config = configparser.ConfigParser()
            config.read_file(codecs.open('/etc/php/7.3/fpm/'
                                         'pool.d/www.conf',
                                         "r", "utf8"))
            config['www']['ping.path'] = '/ping'
            config['www']['pm.status_path'] = '/status'
            config['www']['pm.max_requests'] = '1500'
            config['www']['pm.max_children'] = '50'
            config['www']['pm.start_servers'] = '10'
            config['www']['pm.min_spare_servers'] = '5'
            config['www']['pm.max_spare_servers'] = '15'
            config['www']['request_terminate_timeout'] = '300'
            config['www']['pm'] = 'ondemand'
            config['www']['chdir'] = '/'
            config['www']['prefix'] = '/var/run/php'
            config['www']['listen'] = 'php73-fpm.sock'
            config['www']['listen.mode'] = '0660'
            config['www']['listen.backlog'] = '32768'
            config['www']['catch_workers_output'] = 'yes'
            with codecs.open('/etc/php/7.3/fpm/pool.d/www.conf',
                             encoding='utf-8', mode='w') as configfile:
                Log.debug(self, "writting PHP 7.3 configuration into "
                          "/etc/php/7.3/fpm/pool.d/www.conf")
                config.write(configfile)

            with open("/etc/php/7.3/fpm/pool.d/www.conf",
                      encoding='utf-8', mode='a') as myfile:
                myfile.write("\nphp_admin_value[open_basedir] "
                             "= \"/var/www/:/usr/share/php/:"
                             "/tmp/:/var/run/nginx-cache/:"
                             "/dev/shm:/dev/urandom\"\n")

            # Generate /etc/php/7.3/fpm/pool.d/www-two.conf
            WOFileUtils.copyfile(self, "/etc/php/7.3/fpm/pool.d/www.conf",
                                 "/etc/php/7.3/fpm/pool.d/www-two.conf")
            WOFileUtils.searchreplace(self, "/etc/php/7.3/fpm/pool.d/"
                                      "www-two.conf", "[www]", "[www-two]")
            config = configparser.ConfigParser()
            config.read('/etc/php/7.3/fpm/pool.d/www-two.conf')
            config['www-two']['listen'] = 'php73-two-fpm.sock'
            with open('/etc/php/7.3/fpm/pool.d/www-two.conf',
                      encoding='utf-8', mode='w') as confifile:
                Log.debug(self, "writting PHP7.3 configuration into "
                          "/etc/php/7.3/fpm/pool.d/www-two.conf")
                config.write(confifile)

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
            if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\'"
                                        " /etc/php/7.3/mods-available"
                                        "/xdebug.ini"):
                WOFileUtils.searchreplace(self, "/etc/php/7.3/"
                                          "mods-available/"
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
            open('{0}22222/htdocs/fpm/status/debug73'
                 .format(WOVariables.wo_webroot),
                 encoding='utf-8', mode='a').close()
            open('{0}22222/htdocs/fpm/status/php73'
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

        # create mysql config if it doesn't exist
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
                wo_ram = psutil.virtual_memory().total / (1024 * 1024)
                wo_ram_innodb = int(wo_ram*0.3)
                wo_ram_log_buffer = int(wo_ram_innodb*0.25)
                wo_ram_log_size = int(wo_ram_log_buffer*0.5)
                # replacing default values
                Log.debug(self, "Tuning MySQL configuration")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "innodb_buffer_pool_size	= 256M",
                                          "innodb_buffer_pool_size	= {0}M"
                                          .format(wo_ram_innodb))
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "innodb_log_buffer_size	= 8M",
                                          "innodb_log_buffer_size	= {0}M"
                                          .format(wo_ram_log_buffer))
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "#innodb_log_file_size	= 50M",
                                          "innodb_log_file_size		= {0}M"
                                          .format(wo_ram_log_size))
                WOFileUtils.searchreplace(self,
                                          "/etc/mysql/my.cnf",
                                          "wait_timeout		"
                                          "= 600",
                                          "wait_timeout		"
                                          "= 120")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "skip-external-locking",
                                          "skip-external-locking\n"
                                          "skip-name-resolve = 1\n")

                # disabling mariadb binlog
                WOFileUtils.searchreplace(self,
                                          "/etc/mysql/my.cnf",
                                          "log_bin			"
                                          "= /var/log/mysql/"
                                          "mariadb-bin",
                                          "#log_bin          "
                                          "      = /var/log/"
                                          "mysql/mariadb-bin")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          'log_bin_index		'
                                          "= /var/log/mysql/"
                                          "mariadb-bin.index",
                                          "#log_bin_index "
                                          "= /var/log/mysql/"
                                          "mariadb-bin.index")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "expire_logs_days	= 10",
                                          "#expire_logs_days	"
                                          "= 10")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "max_binlog_size         "
                                          "= 100M",
                                          "#max_binlog_size         "
                                          "= 100M")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "innodb_open_files	="
                                          " 400",
                                          "innodb_open_files	="
                                          " 16000")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "innodb_io_capacity	="
                                          " 400",
                                          "innodb_io_capacity	="
                                          " 16000")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "query_cache_size		= 64M",
                                          "query_cache_size		= 0")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "#query_cache_type		= DEMAND",
                                          "query_cache_type		= 0")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "#open-files-limit	= 2000",
                                          "open-files-limit	= 10000")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "table_open_cache	= 400",
                                          "table_open_cache	= 16000")
                WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                          "max_allowed_packet	= 16M",
                                          "max_allowed_packet	= 64M")
                if (wo_ram_innodb > 1000) and (wo_ram_innodb < 64000):
                    wo_innodb_instance = int(wo_ram_innodb/1000)
                    WOFileUtils.searchreplace(self, "/etc/mysql/my.cnf",
                                              "# * Security Features",
                                              "innodb_buffer_pool_instances "
                                              "= {0}\n"
                                              .format(wo_innodb_instance) +
                                              "# * Security Features")

                WOService.stop_service(self, 'mysql')
                WOFileUtils.mvfile(self, '/var/lib/mysql/ib_logfile0',
                                   '/var/lib/mysql/ib_logfile0.bak')
                WOFileUtils.mvfile(self, '/var/lib/mysql/ib_logfile1',
                                   '/var/lib/mysql/ib_logfile1.bak')
                WOService.start_service(self, 'mysql')

            WOFileUtils.chmod(self, "/usr/bin/mysqltuner", 0o775)
            WOCron.setcron_weekly(self, 'mysqlcheck -Aos --auto-repair '
                                  '> /dev/null 2>&1',
                                  comment='MySQL optimization cronjob '
                                  'added by WordOps')
            WOGit.add(self, ["/etc/mysql"], msg="Adding MySQL into Git")

        # create fail2ban configuration files
        if set(WOVariables.wo_fail2ban).issubset(set(apt_packages)):
            if not os.path.isfile("/etc/fail2ban/jail.d/custom.conf"):
                data = dict()
                Log.debug(self, "Setting up fail2ban jails configuration")
                fail2ban_config = open('/etc/fail2ban/jail.d/custom.conf',
                                       encoding='utf-8', mode='w')
                self.app.render((data), 'fail2ban.mustache',
                                out=fail2ban_config)
                fail2ban_config.close()

                Log.debug(self, "Setting up fail2ban wp filter")
                fail2ban_config = open('/etc/fail2ban/filter.d/'
                                       'wo-wordpress.conf',
                                       encoding='utf-8', mode='w')
                self.app.render((data), 'fail2ban-wp.mustache',
                                out=fail2ban_config)
                fail2ban_config.close()

                Log.debug(self, "Setting up fail2ban wp filter")
                fail2ban_config = open('/etc/fail2ban/filter.d/'
                                       'nginx-forbidden.conf',
                                       encoding='utf-8', mode='w')
                self.app.render((data), 'fail2ban-forbidden.mustache',
                                out=fail2ban_config)
                fail2ban_config.close()
                WOGit.add(self, ["/etc/fail2ban"],
                          msg="Adding Fail2ban into Git")
                WOService.reload_service(self, 'fail2ban')

        # Proftpd configuration
        if set(["proftpd-basic"]).issubset(set(apt_packages)):
            if os.path.isfile("/etc/proftpd/proftpd.conf"):
                Log.debug(self, "Setting up Proftpd configuration")
                WOFileUtils.searchreplace(self, "/etc/proftpd/"
                                          "proftpd.conf",
                                          "# DefaultRoot",
                                          "DefaultRoot")
                WOFileUtils.searchreplace(self, "/etc/proftpd/"
                                          "proftpd.conf",
                                          "# RequireValidShell",
                                          "RequireValidShell")
                WOFileUtils.searchreplace(self, "/etc/proftpd/"
                                          "proftpd.conf",
                                          "# PassivePorts "
                                          "                 "
                                          "49152 65534",
                                          "PassivePorts "
                                          "             "
                                          "    49000 50000")
            # proftpd TLS configuration
            if not os.path.isdir("/etc/proftpd/ssl"):
                WOFileUtils.mkdir(self, "/etc/proftpd/ssl")

            try:
                WOShellExec.cmd_exec(self, "openssl genrsa -out "
                                     "/etc/proftpd/ssl/proftpd.key 2048")
                WOShellExec.cmd_exec(self, "openssl req -new -batch  "
                                     "-subj /commonName=localhost/ "
                                     "-key /etc/proftpd/ssl/proftpd.key "
                                     "-out /etc/proftpd/ssl/proftpd.csr")
                WOFileUtils.mvfile(self, "/etc/proftpd/ssl/proftpd.key",
                                   "/etc/proftpd/ssl/proftpd.key.org")
                WOShellExec.cmd_exec(self, "openssl rsa -in "
                                     "/etc/proftpd/ssl/proftpd.key.org "
                                     "-out /etc/proftpd/ssl/proftpd.key")
                WOShellExec.cmd_exec(self, "openssl x509 -req -days "
                                     "3652 -in /etc/proftpd/ssl/proftpd.csr "
                                     "-signkey /etc/proftpd/ssl/proftpd.key "
                                     " -out /etc/proftpd/ssl/proftpd.crt")
            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(
                    self, "Failed to generate SSL "
                    "certificate for Proftpd")
            WOFileUtils.chmod(self, "/etc/proftpd/ssl/proftpd.key", 0o700)
            WOFileUtils.chmod(self, "/etc/proftpd/ssl/proftpd.crt", 0o700)
            data = dict()
            Log.debug(self, 'Writting the proftpd configuration to '
                      'file /etc/proftpd/tls.conf')
            wo_proftpdconf = open('/etc/proftpd/tls.conf',
                                  encoding='utf-8', mode='w')
            self.app.render((data), 'proftpd-tls.mustache',
                                    out=wo_proftpdconf)
            wo_proftpdconf.close()
            WOFileUtils.searchreplace(self, "/etc/proftpd/"
                                      "proftpd.conf",
                                      "#Include /etc/proftpd/tls.conf",
                                      "Include /etc/proftpd/tls.conf")
            WOService.restart_service(self, 'proftpd')

            # add rule for proftpd with UFW
            if WOAptGet.is_installed(self, 'ufw'):
                try:
                    WOShellExec.cmd_exec(self, "/usr/bin/ufw allow "
                                         "49000:50000/tcp")
                except CommandExecutionError as e:
                    Log.debug(self, "{0}".format(e))
                    Log.error(self, "Unable to add UFW rule")

            if os.path.isfile("/etc/fail2ban/jail.d/custom.conf"):
                with open("/etc/fail2ban/jail.d/custom.conf",
                          encoding='utf-8', mode='a') as f2bproftpd:
                    f2bproftpd.write("\n\n[proftpd]\nenabled = true\n")
                WOService.reload_service(self, 'fail2ban')

            WOGit.add(self, ["/etc/proftpd"],
                      msg="Adding ProFTPd into Git")
            WOService.reload_service(self, 'proftpd')

    # Redis configuration
    if set(["redis-server"]).issubset(set(apt_packages)):
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

            else:
                Log.debug(self, "Setting maxmemory variable to {0} "
                          "in redis.conf"
                          .format(int(wo_ram*1024*1024*0.2)))
                WOFileUtils.searchreplace(self,
                                          "/etc/redis/redis.conf",
                                          "# maxmemory <bytes>",
                                          "maxmemory {0}"
                                          .format
                                          (int(wo_ram*1024*1024*0.2)))

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
            WOFileUtils.chown(self, '/etc/redis/redis.conf',
                              'redis', 'redis', recursive=False)
            WOService.restart_service(self, 'redis-server')

    if (packages):
        if any('/usr/local/bin/wp' == x[1] for x in packages):
            Log.debug(self, "Setting Privileges"
                      " to /usr/local/bin/wp file ")
            WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

        if any('/var/lib/wo/tmp/pma.tar.gz' == x[1]
               for x in packages):
            WOExtract.extract(
                self, '/var/lib/wo/tmp/pma.tar.gz', '/var/lib/wo/tmp/')
            Log.debug(self, 'Extracting file /var/lib/wo/tmp/pma.tar.gz to '
                      'location /var/lib/wo/tmp/')
            if not os.path.exists('{0}22222/htdocs/db'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Creating new  directory "
                          "{0}22222/htdocs/db"
                          .format(WOVariables.wo_webroot))
                os.makedirs('{0}22222/htdocs/db'
                            .format(WOVariables.wo_webroot))
            if not os.path.exists('{0}22222/htdocs/db/pma/'
                                  .format(WOVariables.wo_webroot)):
                shutil.move('/var/lib/wo/tmp/phpmyadmin-STABLE/',
                            '{0}22222/htdocs/db/pma/'
                            .format(WOVariables.wo_webroot))
                shutil.copyfile('{0}22222/htdocs/db/pma'
                                '/config.sample.inc.php'
                                .format(WOVariables.wo_webroot),
                                '{0}22222/htdocs/db/pma/config.inc.php'
                                .format(WOVariables.wo_webroot))
                Log.debug(self, 'Setting Blowfish Secret Key '
                          'FOR COOKIE AUTH to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVariables.wo_webroot))
                blowfish_key = ''.join([random.choice
                                        (string.ascii_letters +
                                         string.digits)
                                        for n in range(25)])
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma'
                                          '/config.inc.php'
                                          .format(WOVariables.wo_webroot),
                                          "$cfg[\'blowfish_secret\']"
                                          " = \'\';",
                                          "$cfg[\'blowfish_secret\']"
                                          " = \'{0}\';"
                                          .format(blowfish_key))
                Log.debug(self, 'Setting HOST Server For Mysql to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVariables.wo_webroot))
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma'
                                          '/config.inc.php'
                                          .format(WOVariables.wo_webroot),
                                          "$cfg[\'Servers\'][$i][\'host\']"
                                          " = \'localhost\';", "$cfg"
                                          "[\'Servers\'][$i][\'host\'] = \'{0}\';"
                                          .format(WOVariables.wo_mysql_host))
                Log.debug(self, 'Setting Privileges of webroot permission to  '
                          '{0}22222/htdocs/db/pma file '.format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'.format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)

        # composer install and phpmyadmin update
        if any('/var/lib/wo/tmp/composer-install' == x[1]
               for x in packages):
            Log.info(self, "Installing composer, please wait...")
            WOShellExec.cmd_exec(self, "php -q /var/lib/wo"
                                 "/tmp/composer-install "
                                 "--install-dir=/var/lib/wo/tmp/")
            shutil.copyfile('/var/lib/wo/tmp/composer.phar',
                            '/usr/local/bin/composer')
            WOFileUtils.chmod(self, "/usr/local/bin/composer", 0o775)
            Log.info(self, "Updating phpMyAdmin, please wait...")
            WOShellExec.cmd_exec(self, "/usr/local/bin/composer update "
                                 "--no-plugins --no-scripts "
                                 "-n --no-dev -d "
                                 "/var/www/22222/htdocs/db/pma/")
            WOFileUtils.chown(self, '{0}22222/htdocs/db/pma'
                              .format(WOVariables.wo_webroot),
                              WOVariables.wo_php_user,
                              WOVariables.wo_php_user,
                              recursive=True)

        # netdata install
        if any('/var/lib/wo/tmp/kickstart.sh' == x[1]
               for x in packages):
            if ((not os.path.exists('/opt/netdata')) and
                    (not os.path.exists('/etc/netdata'))):
                Log.info(self, "Installing Netdata, please wait...")
                WOShellExec.cmd_exec(self, "bash /var/lib/wo/tmp/"
                                     "kickstart.sh "
                                     "--dont-wait")
                # disable mail notifications
                WOFileUtils.searchreplace(self, "/opt/netdata/usr/"
                                          "lib/netdata/conf.d/"
                                          "health_alarm_notify.conf",
                                          'SEND_EMAIL="YES"',
                                          'SEND_EMAIL="NO"')
                # make changes persistant
                WOFileUtils.copyfile(self, "/opt/netdata/usr/"
                                     "lib/netdata/conf.d/"
                                     "health_alarm_notify.conf",
                                     "/opt/netdata/etc/netdata/"
                                     "health_alarm_notify.conf")
                # check if mysql credentials are available
                if os.path.isfile('/etc/mysql/conf.d/my.cnf'):
                    try:
                        WOMysql.execute(self,
                                        "create user "
                                        "'netdata'@'localhost';",
                                        log=False)
                        WOMysql.execute(self,
                                        "grant usage on *.* to "
                                        "'netdata'@'localhost';",
                                        log=False)
                        WOMysql.execute(self,
                                        "flush privileges;",
                                        log=False)
                    except CommandExecutionError as e:
                        Log.debug(self, "{0}".format(e))
                        Log.info(
                            self, "fail to setup mysql user for netdata")
                WOFileUtils.chown(self, '/opt/netdata',
                                  'netdata',
                                  'netdata',
                                  recursive=True)
                WOService.restart_service(self, 'netdata')

        # WordOps Dashboard
        if any('/var/lib/wo/tmp/wo-dashboard.tar.gz' == x[1]
               for x in packages):
            if not os.path.isfile('{0}22222/htdocs/index.php'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Extracting wo-dashboard.tar.gz "
                          "to location {0}22222/htdocs/"
                          .format(WOVariables.wo_webroot))
                WOExtract.extract(self, '/var/lib/wo/tmp/'
                                  'wo-dashboard.tar.gz',
                                  '{0}22222/htdocs'
                                  .format(WOVariables.wo_webroot))
                wo_wan = os.popen("/sbin/ip -4 route get 8.8.8.8 | "
                                  "grep -oP \"dev [^[:space:]]+ \" "
                                  "| cut -d ' ' -f 2").read()
                if (wo_wan != 'eth0' and wo_wan != ''):
                    WOFileUtils.searchreplace(self,
                                              "{0}22222/htdocs/index.php"
                                              .format(WOVariables.wo_webroot),
                                              "eth0",
                                              "{0}".format(wo_wan))
                    Log.debug(self, "Setting Privileges to "
                              "{0}22222/htdocs"
                              .format(WOVariables.wo_webroot))
                    WOFileUtils.chown(self, '{0}22222'
                                      .format(WOVariables.wo_webroot),
                                      WOVariables.wo_php_user,
                                      WOVariables.wo_php_user,
                                      recursive=True)

        # Extplorer FileManager
        if any('/var/lib/wo/tmp/extplorer.tar.gz' == x[1]
               for x in packages):
            if not os.path.exists('{0}22222/htdocs/files'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Extracting explorer.tar.gz "
                          "to location {0}22222/htdocs/files"
                          .format(WOVariables.wo_webroot))
                WOExtract.extract(self, '/var/lib/wo/tmp/extplorer.tar.gz',
                                  '/var/lib/wo/tmp/')
                shutil.move('/var/lib/wo/tmp/extplorer-{0}'
                            .format(WOVariables.wo_extplorer),
                            '{0}22222/htdocs/files'
                            .format(WOVariables.wo_webroot))
                Log.debug(self, "Setting Privileges to "
                          "{0}22222/htdocs/files"
                          .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)

        # webgrind
        if any('/var/lib/wo/tmp/webgrind.tar.gz' == x[1]
               for x in packages):
            Log.debug(self, "Extracting file webgrind.tar.gz to "
                      "location /var/lib/wo/tmp/ ")
            WOExtract.extract(
                self, '/var/lib/wo/tmp/webgrind.tar.gz',
                '/var/lib/wo/tmp/')
            if not os.path.exists('{0}22222/htdocs/php'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Creating directroy "
                          "{0}22222/htdocs/php"
                          .format(WOVariables.wo_webroot))
                os.makedirs('{0}22222/htdocs/php'
                            .format(WOVariables.wo_webroot))
            if not os.path.exists('{0}22222/htdocs/php/webgrind'
                                  .format(WOVariables.wo_webroot)):
                shutil.move('/var/lib/wo/tmp/webgrind-master/',
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
        # anemometer
        if any('/var/lib/wo/tmp/anemometer.tar.gz' == x[1]
               for x in packages):
            Log.debug(self, "Extracting file anemometer.tar.gz to "
                      "location /var/lib/wo/tmp/ ")
            WOExtract.extract(
                self, '/var/lib/wo/tmp/anemometer.tar.gz',
                '/var/lib/wo/tmp/')
            if not os.path.exists('{0}22222/htdocs/db/'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Creating directory")
                os.makedirs('{0}22222/htdocs/db/'
                            .format(WOVariables.wo_webroot))
            if not os.path.exists('{0}22222/htdocs/db/anemometer'
                                  .format(WOVariables.wo_webroot)):
                shutil.move('/var/lib/wo/tmp/Anemometer-master',
                            '{0}22222/htdocs/db/anemometer'
                            .format(WOVariables.wo_webroot))
                chars = ''.join(random.sample(string.ascii_letters, 8))
                try:
                    WOShellExec.cmd_exec(self, 'mysql < {0}22222/htdocs/db'
                                         '/anemometer/install.sql'
                                         .format(WOVariables.wo_webroot))
                except CommandExecutionError as e:
                    Log.debug(self, "{0}".format(e))
                    raise SiteError("Unable to import Anemometer database")

                WOMysql.execute(self, 'grant select on'
                                ' *.* to \'anemometer\''
                                '@\'{0}\' IDENTIFIED'
                                ' BY \'{1}\''.format(self.app.config.get
                                                     ('mysql',
                                                      'grant-host'),
                                                     chars))
                Log.debug(self, "grant all on slow-query-log.*"
                          " to anemometer@root_user"
                          " IDENTIFIED BY password ")
                WOMysql.execute(self, 'grant all on slow_query_log.* to'
                                '\'anemometer\'@\'{0}\' IDENTIFIED'
                                ' BY \'{1}\''.format(self.app.config.get(
                                    'mysql', 'grant-host'),
                                    chars),
                                errormsg="cannot grant priviledges",
                                log=False)

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

        # phpredisadmin
        if any('/var/lib/wo/tmp/pra.tar.gz' == x[1]
               for x in packages):
            if not os.path.exists('{0}22222/htdocs/cache/'
                                  'redis/phpRedisAdmin'
                                  .format(WOVariables.wo_webroot)):
                Log.debug(self, "Creating new directory "
                          "{0}22222/htdocs/cache/redis"
                          .format(WOVariables.wo_webroot))
                os.makedirs('{0}22222/htdocs/cache/redis/phpRedisAdmin'
                            .format(WOVariables.wo_webroot))
                WOFileUtils.chown(self, '{0}22222'
                                  .format(WOVariables.wo_webroot),
                                  WOVariables.wo_php_user,
                                  WOVariables.wo_php_user,
                                  recursive=True)
                if os.path.isfile("/usr/local/bin/composer"):
                    WOShellExec.cmd_exec(self, "sudo -u www-data -H "
                                         "composer "
                                         "create-project -n -s dev "
                                         "erik-dubbelboer/php-redis-admin "
                                         "/var/www/22222/htdocs/cache"
                                         "/redis/phpRedisAdmin ")
            Log.debug(self, 'Setting Privileges of webroot permission to  '
                      '{0}22222/htdocs/cache/file '
                      .format(WOVariables.wo_webroot))
            WOFileUtils.chown(self, '{0}22222'
                              .format(WOVariables.wo_webroot),
                              WOVariables.wo_php_user,
                              WOVariables.wo_php_user,
                              recursive=True)
