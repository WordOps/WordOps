import configparser
import os
import random
import shutil
import string

import psutil
from wo.core.apt_repo import WORepo
from wo.core.aptget import WOAptGet
from wo.core.cron import WOCron
from wo.core.extract import WOExtract
from wo.core.fileutils import WOFileUtils
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.mysql import WOMysql
from wo.core.nginxhashbucket import hashbucket
from wo.core.services import WOService
from wo.core.shellexec import CommandExecutionError, WOShellExec
from wo.core.sslutils import SSL
from wo.core.template import WOTemplate
from wo.core.variables import WOVar
from wo.core.stackconf import WOConf
from wo.core.download import WODownload
from wo.core.checkfqdn import WOFqdn


def pre_pref(self, apt_packages):
    """Pre settings to do before installation packages"""

    if ("mariadb-server" in apt_packages or "mariadb-client" in apt_packages):
        # add mariadb repository excepted on raspbian and ubuntu 19.04
        if not (WOVar.wo_distro == 'raspbian'):
            Log.info(self, "Adding repository for MySQL, please wait...")
            mysql_pref = (
                "Package: *\nPin: origin  deb.mariadb.org"
                "\nPin-Priority: 1000\n")
            with open('/etc/apt/preferences.d/'
                      'MariaDB.pref', 'w') as mysql_pref_file:
                mysql_pref_file.write(mysql_pref)
            if self.app.config.has_section('mariadb'):
                mariadb_ver = self.app.config.get(
                    'mariadb', 'release')
                wo_mysql_repo_conf = ("deb [signed-by=/etc/apt/keyrings/mariadb-keyring.pgp] "
                                      "http://deb.mariadb.org/"
                                      f"{mariadb_ver}/{WOVar.wo_distro} {WOVar.wo_platform_codename} main")
            else:
                wo_mysql_repo_conf = WOVar.wo_mysql_repo
            # APT repositories
            WORepo.add(self, repo_url=wo_mysql_repo_conf, repo_name="mariadb")
    if ("mariadb-server" in apt_packages and
            not os.path.exists('/etc/mysql/conf.d/my.cnf')):
        # generate random 24 characters root password
        chars = ''.join(random.sample(string.ascii_letters, 24))
        # generate my.cnf root credentials
        mysql_config = """
            [client]
            user = root
            password = {chars}
            socket = /run/mysqld/mysqld.sock
            """.format(chars=chars)
        config = configparser.ConfigParser()
        config.read_string(mysql_config)
        Log.debug(self, 'Writting configuration into MySQL file')
        conf_path = "/etc/mysql/conf.d/my.cnf.tmp"
        os.makedirs(os.path.dirname(conf_path), exist_ok=True)
        with os.fdopen(os.open(conf_path, os.O_WRONLY | os.O_CREAT, 0o600), 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    # add nginx repository
    if set(WOVar.wo_nginx).issubset(set(apt_packages)):
        if (WOVar.wo_distro == 'ubuntu'):
            Log.info(self, "Adding repository for NGINX, please wait...")
            WORepo.add(self, ppa=WOVar.wo_nginx_repo)
            Log.debug(self, 'Adding ppa for Nginx')
        else:
            if not os.path.exists('/etc/apt/sources.list.d/wordops.list'):
                Log.info(self, "Adding repository for NGINX, please wait...")
                Log.debug(self, 'Adding repository for Nginx')
                WORepo.add(self, repo_url=WOVar.wo_nginx_repo, repo_name="wordops")

    # add php repository
    if (('php7.3-fpm' in apt_packages) or
            ('php7.2-fpm' in apt_packages) or
            ('php7.4-fpm' in apt_packages) or
            ('php8.0-fpm' in apt_packages) or
            ('php8.1-fpm' in apt_packages) or
            ('php8.2-fpm' in apt_packages) or
            ('php8.3-fpm' in apt_packages) or
            ('php8.4-fpm' in apt_packages)):
        if (WOVar.wo_distro == 'ubuntu'):
            Log.debug(self, 'Adding ppa for PHP')
            Log.info(self, "Adding repository for PHP, please wait...")
            WORepo.add(self, ppa=WOVar.wo_php_repo)
        else:
            # Add repository for php
            if (WOVar.wo_platform_codename == 'buster'):
                php_pref = ("Package: *\nPin: origin "
                            "packages.sury.org"
                            "\nPin-Priority: 1000\n")
                with open(
                    '/etc/apt/preferences.d/'
                        'PHP.pref', mode='w',
                        encoding='utf-8') as php_pref_file:
                    php_pref_file.write(php_pref)
            if not os.path.exists('/etc/apt/sources.list.d/php.list'):
                Log.debug(self, 'Adding repo_url of php for debian')
                Log.info(self, "Adding repository for PHP, please wait...")
                WORepo.add(self, repo_url=WOVar.wo_php_repo, repo_name="php")

    # add redis repository
    if set(WOVar.wo_redis).issubset(set(apt_packages)):
        if not os.path.exists('/etc/apt/sources.list.d/redis.list'):
            WORepo.add(self, repo_url=WOVar.wo_redis_repo, repo_name="redis")


def post_pref(self, apt_packages, packages, upgrade=False):
    """Post activity after installation of packages"""
    if (apt_packages):
        # Nginx configuration
        if set(WOVar.wo_nginx).issubset(set(apt_packages)):
            Log.wait(self, "Configuring Nginx")
            # Nginx main configuration
            ngxcnf = '/etc/nginx/conf.d'
            ngxcom = '/etc/nginx/common'
            ngxroot = '/var/www/'
            WOGit.add(self, ["/etc/nginx"], msg="Adding Nginx into Git")
            data = dict(tls13=True, release=WOVar.wo_version)
            WOTemplate.deploy(self,
                              '/etc/nginx/nginx.conf',
                              'nginx-core.mustache', data, overwrite=True)

            if not os.path.isfile('{0}/gzip.conf.disabled'.format(ngxcnf)):
                data = dict(release=WOVar.wo_version)
                WOTemplate.deploy(self, '{0}/gzip.conf'.format(ngxcnf),
                                  'gzip.mustache', data)

            if not os.path.isfile('{0}/brotli.conf'.format(ngxcnf)):
                WOTemplate.deploy(self,
                                  '{0}/brotli.conf.disabled'
                                  .format(ngxcnf),
                                  'brotli.mustache', data)

            WOTemplate.deploy(self, '{0}/tweaks.conf'.format(ngxcnf),
                              'tweaks.mustache', data)

            # Fix for white screen death with NGINX PLUS
            if not WOFileUtils.grep(self, '/etc/nginx/fastcgi_params',
                                    'SCRIPT_FILENAME'):
                with open('/etc/nginx/fastcgi_params',
                          encoding='utf-8', mode='a') as wo_nginx:
                    wo_nginx.write('fastcgi_param \tSCRIPT_FILENAME '
                                   '\t$request_filename;\n')
            if not WOFileUtils.grep(self, '/etc/nginx/fastcgi_params',
                                    'HTTP_HOST'):
                WOFileUtils.textappend(self, '/etc/nginx/fastcgi_params',
                                       '# Fix for HTTP/3 QUIC HTTP_HOST\n'
                                       'fastcgi_param\tHTTP_HOST\t$host;\n')
            if not WOFileUtils.grep(self, '/etc/nginx/proxy_params',
                                    'X-Forwarded-Host'):
                WOFileUtils.textappend(self, '/etc/nginx/proxy_params',
                                       'proxy_set_header X-Forwarded-Host $host;\n')
            if not WOFileUtils.grep(self, '/etc/nginx/proxy_params',
                                    'X-Forwarded-Port'):
                WOFileUtils.textappend(self, '/etc/nginx/proxy_params',
                                       'proxy_set_header X-Forwarded-Port $server_port;\n')
            try:
                data = dict(php="9000", debug="9001",
                            php7="9070", debug7="9170",
                            release=WOVar.wo_version)
                WOTemplate.deploy(
                    self, '{0}/upstream.conf'.format(ngxcnf),
                    'upstream.mustache', data, overwrite=True)

                data = dict(phpconf=(
                    bool(WOAptGet.is_installed(self, 'php7.2-fpm'))),
                    release=WOVar.wo_version)
                WOTemplate.deploy(
                    self, '{0}/stub_status.conf'.format(ngxcnf),
                    'stub_status.mustache', data)
                data = dict(release=WOVar.wo_version)
                WOTemplate.deploy(
                    self, '{0}/webp.conf'.format(ngxcnf),
                    'webp.mustache', data, overwrite=False)
                WOTemplate.deploy(
                    self, '{0}/avif.conf'.format(ngxcnf),
                    'avif.mustache', data, overwrite=False)
                WOTemplate.deploy(
                    self,
                    '{0}/map-wp-fastcgi-cache.conf'.format(ngxcnf),
                    'map-wp.mustache', data)
            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))

            # Setup Nginx common directory
            if not os.path.exists('{0}'.format(ngxcom)):
                Log.debug(self, 'Creating directory'
                          '/etc/nginx/common')
                os.makedirs('/etc/nginx/common')

            try:
                data = dict(release=WOVar.wo_version)

                # Common Configuration
                WOTemplate.deploy(self,
                                  '{0}/locations-wo.conf'
                                  .format(ngxcom),
                                  'locations.mustache', data)
                # traffic advice file
                WOTemplate.deploy(self,
                                  '/var/www/html/'
                                  '.well-known/traffic-advice',
                                  'traffic-advice.mustache', data)

                WOTemplate.deploy(self,
                                  '{0}/wpsubdir.conf'
                                  .format(ngxcom),
                                  'wpsubdir.mustache', data)

                for wo_php in WOVar.wo_php_versions:
                    data = dict(upstream="{0}".format(wo_php),
                                release=WOVar.wo_version)
                    WOConf.nginxcommon(self)

            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))

            with open("/etc/nginx/common/release",
                      "w", encoding='utf-8') as release_file:
                release_file.write("v{0}"
                                   .format(WOVar.wo_version))
            release_file.close()

            # Following files should not be overwrited

            data = dict(webroot=ngxroot, release=WOVar.wo_version)
            WOTemplate.deploy(self,
                              '{0}/acl.conf'
                              .format(ngxcom),
                              'acl.mustache', data, overwrite=False)
            WOTemplate.deploy(self,
                              '{0}/blockips.conf'
                              .format(ngxcnf),
                              'blockips.mustache', data, overwrite=False)
            WOTemplate.deploy(self,
                              '{0}/fastcgi.conf'
                              .format(ngxcnf),
                              'fastcgi.mustache', data, overwrite=True)

            # add redis cache format if not already done
            if (os.path.isfile("/etc/nginx/nginx.conf") and
                not os.path.isfile("/etc/nginx/conf.d"
                                   "/redis.conf")):
                with open("/etc/nginx/conf.d/"
                          "redis.conf", "a") as redis_file:
                    redis_file.write(
                        "# Log format Settings\n"
                        "log_format rt_cache_redis "
                        "'$remote_addr "
                        "$upstream_response_time "
                        "$srcache_fetch_status "
                        "[$time_local] '\n"
                        "'$host \"$request\" $status"
                        " $body_bytes_sent '\n"
                        "'\"$http_referer\" "
                        "\"$http_user_agent\"';\n")

            if not os.path.exists('/etc/nginx/bots.d'):
                WOFileUtils.textwrite(
                    self, '/etc/nginx/conf.d/variables-hash.conf',
                    'variables_hash_max_size 4096;\n'
                    'variables_hash_bucket_size 4096;')

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
            if os.path.exists('/etc/nginx/sites-available/22222'):
                Log.debug(self, "looking for the current backend port")
                for line in open('/etc/nginx/sites-available/22222',
                                 encoding='utf-8'):
                    if 'listen' in line:
                        listen_line = line.strip()
                        break
                port = (listen_line).split(' ')
                current_backend_port = (port[1]).strip()
            else:
                current_backend_port = '22222'

            if 'current_backend_port' not in locals():
                current_backend_port = '22222'

            data = dict(webroot=ngxroot,
                        release=WOVar.wo_version, port=current_backend_port)
            WOTemplate.deploy(
                self,
                '/etc/nginx/sites-available/22222',
                '22222.mustache', data, overwrite=True)

            passwd = ''.join([random.choice
                              (string.ascii_letters + string.digits)
                              for n in range(24)])
            if not os.path.isfile('/etc/nginx/htpasswd-wo'):
                try:
                    WOShellExec.cmd_exec(
                        self, "printf \"WordOps:"
                        "$(openssl passwd -apr1 "
                        "{password} 2> /dev/null)\n\""
                        "> /etc/nginx/htpasswd-wo "
                        "2>/dev/null"
                        .format(password=passwd))
                except CommandExecutionError as e:
                    Log.debug(self, "{0}".format(e))
                    Log.error(self, "Failed to save HTTP Auth")
            if not os.path.islink('/etc/nginx/sites-enabled/22222'):
                # Create Symbolic link for 22222
                WOFileUtils.create_symlink(
                    self, ['/etc/nginx/'
                           'sites-available/'
                           '22222',
                           '/etc/nginx/'
                           'sites-enabled/'
                           '22222'])
            # Create log and cert folder and softlinks
            if not os.path.exists('{0}22222/logs'
                                  .format(ngxroot)):
                Log.debug(self, "Creating directory "
                          "{0}22222/logs "
                          .format(ngxroot))
                os.makedirs('{0}22222/logs'
                            .format(ngxroot))

            if not os.path.exists('{0}22222/cert'
                                  .format(ngxroot)):
                Log.debug(self, "Creating directory "
                          "{0}22222/cert"
                          .format(ngxroot))
                os.makedirs('{0}22222/cert'
                            .format(ngxroot))

            if not os.path.isdir('{0}22222/conf/nginx'
                                 .format(ngxroot)):
                Log.debug(self, "Creating directory "
                          "{0}22222/conf/nginx"
                          .format(ngxroot))
                os.makedirs('{0}22222/conf/nginx'
                            .format(ngxroot))

                WOFileUtils.create_symlink(
                    self,
                    ['/var/log/nginx/'
                     '22222.access.log',
                     '{0}22222/'
                     'logs/access.log'
                     .format(ngxroot)]
                )

                WOFileUtils.create_symlink(
                    self,
                    ['/var/log/nginx/'
                     '22222.error.log',
                     '{0}22222/'
                     'logs/error.log'
                     .format(ngxroot)]
                )
            if (not os.path.isfile('{0}22222/cert/22222.key'
                                   .format(ngxroot))):
                SSL.selfsignedcert(self, proftpd=False, backend=True)

            if not os.path.exists('{0}22222/conf/nginx/ssl.conf'
                                  .format(ngxroot)):
                with open("/var/www/22222/conf/nginx/"
                          "ssl.conf", "w") as php_file:
                    php_file.write("ssl_certificate "
                                   "/var/www/22222/cert/22222.crt;\n"
                                   "ssl_certificate_key "
                                   "/var/www/22222/cert/22222.key;\n"
                                   "ssl_stapling off;\n")

                server_ip = WOFqdn.get_server_ip(self)
                if server_ip is None:
                    server_ip = WOVar.wo_fqdn

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
                    self.msg = (self.msg + [f'WordOps backend is available on https://{server_ip}:22222 '
                                            f'or https://{WOVar.wo_fqdn}:22222'])

            data = dict(release=WOVar.wo_version)
            WOTemplate.deploy(self, '/opt/cf-update.sh',
                              'cf-update.mustache',
                              data, overwrite=True)
            WOFileUtils.chmod(self, "/opt/cf-update.sh", 0o775)
            Log.debug(self, 'Creating Cloudflare.conf')
            WOShellExec.cmd_exec(self, '/opt/cf-update.sh')
            WOCron.setcron_weekly(self, '/opt/cf-update.sh '
                                  '> /dev/null 2>&1',
                                  comment='Cloudflare IP refresh cronjob '
                                  'added by WordOps')

            # Nginx Configation into GIT
            if not WOService.restart_service(self, 'nginx'):
                try:
                    hashbucket(self)
                    WOService.restart_service(self, 'nginx')
                except Exception:
                    Log.warn(
                        self, "increasing nginx server_names_hash_bucket_size "
                        "do not fix the issue")
                    Log.info(self, "Rolling back to previous configuration")
                    WOGit.rollback(self, ["/etc/nginx"])
                    if not WOService.restart_service(self, 'nginx'):
                        Log.error(
                            self, "There is an error in Nginx configuration.\n"
                            "Use the command nginx -t to identify "
                            "the cause of this issue", False)
            else:
                Log.valide(self, "Configuring Nginx")
                WOGit.add(self, ["/etc/nginx"], msg="Adding Nginx into Git")
                if not os.path.isdir('/etc/systemd/system/nginx.service.d'):
                    WOFileUtils.mkdir(self,
                                      '/etc/systemd/system/nginx.service.d')
                if not os.path.isdir(
                        '/etc/systemd/system/nginx.service.d/limits.conf'):
                    with open(
                        '/etc/systemd/system/nginx.service.d/limits.conf',
                            encoding='utf-8', mode='w') as ngx_limit:
                        ngx_limit.write('[Service]\nLimitNOFILE=500000')
                    WOShellExec.cmd_exec(self, 'systemctl daemon-reload')
                    WOService.restart_service(self, 'nginx')

        # php conf
        php_list = []
        for version in list(WOVar.wo_php_versions.values()):
            package_name = 'php' + version + '-fpm'
            if package_name in apt_packages:
                php_list.append([version])

        for php_version in php_list:
            WOGit.add(self, ["/etc/php"], msg="Adding PHP into Git")
            Log.wait(self, "Configuring php{0}-fpm".format(php_version[0]))
            ngxroot = '/var/www/'

            # Create log directories
            if not os.path.exists('/var/log/php/{0}/'.format(php_version[0])):
                Log.debug(
                    self, 'Creating directory /var/log/php/{0}/'
                    .format(php_version[0]))
                os.makedirs('/var/log/php/{0}/'.format(php_version[0]))

            if not os.path.isfile(
                    '/etc/php/{0}/fpm/php.ini.orig'.format(php_version[0])):
                WOFileUtils.copyfile(self,
                                     '/etc/php/{0}/fpm/php.ini'.format(
                                         php_version[0]),
                                     '/etc/php/{0}/fpm/php.ini.orig'
                                     .format(php_version[0]))

            # Parse etc/php/x.x/fpm/php.ini
            config = configparser.ConfigParser()
            Log.debug(self, "configuring php file "
                      "/etc/php/{0}/fpm/php.ini".format(php_version[0]))
            config.read('/etc/php/{0}/fpm/php.ini.orig'.format(php_version[0]))
            config['PHP']['expose_php'] = 'Off'
            config['PHP']['post_max_size'] = '100M'
            config['PHP']['upload_max_filesize'] = '100M'
            config['PHP']['max_execution_time'] = '300'
            config['PHP']['max_input_time'] = '300'
            config['PHP']['max_input_vars'] = '20000'
            config['Date']['date.timezone'] = WOVar.wo_timezone
            config['opcache']['opcache.enable'] = '1'
            config['opcache']['opcache.interned_strings_buffer'] = '8'
            config['opcache']['opcache.max_accelerated_files'] = '10000'
            config['opcache']['opcache.memory_consumption'] = '256'
            config['opcache']['opcache.save_comments'] = '1'
            config['opcache']['opcache.revalidate_freq'] = '5'
            config['opcache']['opcache.consistency_checks'] = '0'
            config['opcache']['opcache.validate_timestamps'] = '1'
            with open('/etc/php/{0}/fpm/php.ini'.format(php_version[0]),
                      encoding='utf-8', mode='w') as configfile:
                Log.debug(self, "Writting php configuration into "
                          "/etc/php/{0}/fpm/php.ini".format(php_version[0]))
                config.write(configfile)

            # Render php-fpm pool template for phpx.x
            data = dict(pid="/run/php/php{0}-fpm.pid".format(php_version[0]),
                        error_log="/var/log/php{0}-fpm.log".format(
                            php_version[0]),
                        include="/etc/php/{0}/fpm/pool.d/*.conf"
                        .format(php_version[0]))
            WOTemplate.deploy(
                self, '/etc/php/{0}/fpm/php-fpm.conf'.format(php_version[0]),
                'php-fpm.mustache', data)
            php_short = php_version[0].replace(".", "")
            data = dict(pool='www-php{0}'.format(php_short),
                        listen='php{0}-fpm.sock'.format(php_short),
                        user='www-data',
                        group='www-data', listenuser='root',
                        listengroup='www-data', openbasedir=True)
            WOTemplate.deploy(self, '/etc/php/{0}/fpm/pool.d/www.conf'
                              .format(php_version[0]),
                              'php-pool.mustache', data)
            data = dict(pool='www-two-php{0}'.format(php_short),
                        listen='php{0}-two-fpm.sock'.format(php_short),
                        user='www-data',
                        group='www-data', listenuser='root',
                        listengroup='www-data', openbasedir=True)
            WOTemplate.deploy(self,
                              '/etc/php/{0}/fpm/pool.d/www-two.conf'.format(
                                  php_version[0]),
                              'php-pool.mustache', data)

            # Generate /etc/php/x.x/fpm/pool.d/debug.conf
            WOFileUtils.copyfile(self,
                                 "/etc/php/{0}/fpm/pool.d/www.conf".format(
                                     php_version[0]),
                                 "/etc/php/{0}/fpm/pool.d/debug.conf"
                                 .format(php_version[0]))
            WOFileUtils.searchreplace(self,
                                      "/etc/php/{0}/fpm/pool.d/"
                                      "debug.conf".format(php_version[0]),
                                      "[www-php{0}]".format(php_short),
                                      "[debug]")
            config = configparser.ConfigParser()
            config.read(
                '/etc/php/{0}/fpm/pool.d/debug.conf'.format(php_version[0]))
            config['debug']['listen'] = '127.0.0.1:91{0}'.format(php_short)
            config['debug']['rlimit_core'] = 'unlimited'
            config['debug']['slowlog'] = '/var/log/php/{0}/slow.log'.format(
                php_version[0])
            config['debug']['request_slowlog_timeout'] = '10s'
            with open('/etc/php/{0}/fpm/pool.d/debug.conf'
                      .format(php_version[0]),
                      encoding='utf-8', mode='w') as confifile:
                Log.debug(self,
                          "writting PHP configuration into "
                          "/etc/php/{0}/fpm/pool.d/debug.conf"
                          .format(php_version[0]))
                config.write(confifile)

            with open("/etc/php/{0}/fpm/pool.d/debug.conf"
                      .format(php_version[0]),
                      encoding='utf-8', mode='a') as myfile:
                myfile.write("php_admin_value[xdebug.profiler_output_dir] "
                             "= /tmp/ \nphp_admin_value[xdebug.profiler_"
                             "output_name] = cachegrind.out.%p-%H-%R "
                             "\nphp_admin_flag[xdebug.profiler_enable"
                             "_trigger] = on \nphp_admin_flag[xdebug."
                             "profiler_enable] = off\n")

            # Disable xdebug
            if not WOShellExec.cmd_exec(self, "grep -q \';zend_extension\'"
                                        " /etc/php/{0}/mods-available/"
                                        "xdebug.ini".format(php_version[0])):
                WOFileUtils.searchreplace(self, "/etc/php/{0}/"
                                          "mods-available/"
                                          "xdebug.ini".format(php_version[0]),
                                          "zend_extension",
                                          ";zend_extension")

            # PHP and Debug pull configuration
            if not os.path.exists('{0}22222/htdocs/fpm/status/'
                                  .format(ngxroot)):
                Log.debug(self, 'Creating directory '
                          '{0}22222/htdocs/fpm/status/ '
                          .format(ngxroot))
                os.makedirs('{0}22222/htdocs/fpm/status/'
                            .format(ngxroot))
                open('{0}22222/htdocs/fpm/status/debug{1}'
                     .format(ngxroot, php_short),
                     encoding='utf-8', mode='a').close()
                open('{0}22222/htdocs/fpm/status/php{1}'
                     .format(ngxroot, php_short),
                     encoding='utf-8', mode='a').close()

            # Write info.php
            if not os.path.exists('{0}22222/htdocs/php/'
                                  .format(ngxroot)):
                Log.debug(self, 'Creating directory '
                          '{0}22222/htdocs/php/ '
                          .format(ngxroot))
                os.makedirs('{0}22222/htdocs/php'
                            .format(ngxroot))

                with open("{0}22222/htdocs/php/info.php"
                          .format(ngxroot),
                          encoding='utf-8', mode='w') as myfile:
                    myfile.write("<?php\nphpinfo();\n?>")

            # write opcache clean for phpxx
            if not os.path.exists('{0}22222/htdocs/cache/opcache'
                                  .format(ngxroot)):
                os.makedirs('{0}22222/htdocs/cache/opcache'
                            .format(ngxroot))
            WOFileUtils.textwrite(
                self, '{0}22222/htdocs/cache/opcache/php{1}.php'
                .format(ngxroot, php_short),
                '<?php opcache_reset(); ?>')

            WOFileUtils.chown(self, "{0}22222/htdocs"
                              .format(ngxroot),
                              'www-data',
                              'www-data', recursive=True)

            # enable imagick php extension
            WOShellExec.cmd_exec(self, 'phpenmod -v ALL imagick')

            # check service restart or rollback configuration
            if not WOService.restart_service(self,
                                             'php{0}-fpm'
                                             .format(php_version[0])):
                WOGit.rollback(self, ["/etc/php"], msg="Rollback PHP")
            else:
                Log.valide(
                    self, "Configuring php{0}-fpm".format(php_version[0]))
                WOGit.add(self, ["/etc/php"], msg="Adding PHP into Git")

            if os.path.exists('/etc/nginx/conf.d/upstream.conf'):
                if not WOFileUtils.grepcheck(
                        self, '/etc/nginx/conf.d/upstream.conf',
                        'php{0}'.format(php_short)):
                    data = dict(php="9000", debug="9001",
                                php7="9070", debug7="9170",
                                php8="9080", debug8="9180",
                                release=WOVar.wo_version)
                    WOTemplate.deploy(
                        self, '/etc/nginx/conf.d/upstream.conf',
                        'upstream.mustache', data, True)
                    WOConf.nginxcommon(self)

        # create mysql config if it doesn't exist
        if "mariadb-server" in apt_packages:
            WOGit.add(self, ["/etc/mysql"], msg="Adding MySQL into Git")
            if not os.path.exists("/etc/mysql/my.cnf"):
                config = ("[mysqld]\nwait_timeout = 30\n"
                          "interactive_timeout=60\nperformance_schema = 0"
                          "\nquery_cache_type = 1")
                config_file = open("/etc/mysql/my.cnf",
                                   encoding='utf-8', mode='w')
                config_file.write(config)
                config_file.close()
            else:
                # make sure root account have all privileges
                if os.path.exists('/etc/mysql/conf.d/my.cnf.tmp'):
                    try:
                        config = configparser.ConfigParser()
                        config.read('/etc/mysql/conf.d/my.cnf.tmp')
                        chars = config['client']['password']
                        WOShellExec.cmd_exec(
                            self,
                            'mysql -e "SET PASSWORD = '
                            'PASSWORD(\'{0}\'); flush privileges;"'
                            .format(chars), log=False)
                        WOFileUtils.mvfile(
                            self, '/etc/mysql/conf.d/my.cnf.tmp',
                            '/etc/mysql/conf.d/my.cnf')
                    except CommandExecutionError:
                        Log.error(self, "Unable to set MySQL password")
                    WOGit.add(self, ["/etc/mysql"],
                              msg="Adding MySQL into Git")
                elif os.path.exists('/etc/mysql/conf.d/my.cnf'):
                    if ((WOAptGet.is_installed(
                        self,
                        'mariadb-server-{0}'.format(WOVar.mariadb_ver))) and
                            not (WOFileUtils.grepcheck(
                                self, '/etc/mysql/conf.d/my.cnf', 'socket'))):
                        try:
                            config = configparser.ConfigParser()
                            config.read('/etc/mysql/conf.d/my.cnf')
                            chars = config['client']['password']
                            WOShellExec.cmd_exec(
                                self,
                                'mysql -e "ALTER USER root@localhost '
                                'IDENTIFIED VIA unix_socket OR '
                                'mysql_native_password; '
                                'SET PASSWORD = PASSWORD(\'{0}\'); '
                                'flush privileges;"'.format(chars), log=False)
                            WOFileUtils.textappend(
                                self, '/etc/mysql/conf.d/my.cnf',
                                'socket = /run/mysqld/mysqld.sock')
                        except CommandExecutionError:
                            Log.error(self, "Unable to set MySQL password")
                        WOGit.add(self, ["/etc/mysql"],
                                  msg="Adding MySQL into Git")

                Log.wait(self, "Tuning MariaDB configuration")
                if not os.path.isfile("/etc/mysql/my.cnf.default-pkg"):
                    WOFileUtils.copyfile(self, "/etc/mysql/my.cnf",
                                         "/etc/mysql/my.cnf.default-pkg")
                wo_ram = psutil.virtual_memory().total / (1024 * 1024)
                # set InnoDB variable depending on the RAM available
                wo_ram_innodb = int(wo_ram * 0.3)
                wo_ram_log_buffer = int(wo_ram_innodb * 0.25)
                wo_ram_log_size = int(wo_ram_log_buffer * 0.5)
                if (wo_ram < 2000):
                    wo_innodb_instance = int(1)
                    tmp_table_size = int(32)
                elif (wo_ram > 2000) and (wo_ram < 64000):
                    wo_innodb_instance = int(wo_ram / 1000)
                    tmp_table_size = int(128)
                elif (wo_ram > 64000):
                    wo_innodb_instance = int(64)
                    tmp_table_size = int(256)
                mariadbconf = bool(not os.path.exists(
                    '/etc/mysql/mariadb.conf.d/50-server.cnf'))
                data = dict(
                    tmp_table_size=tmp_table_size, inno_log=wo_ram_log_size,
                    inno_buffer=wo_ram_innodb,
                    inno_log_buffer=wo_ram_log_buffer,
                    innodb_instances=wo_innodb_instance,
                    newmariadb=mariadbconf, release=WOVar.wo_version)
                if os.path.exists('/etc/mysql/mariadb.conf.d/50-server.cnf'):
                    WOTemplate.deploy(
                        self, '/etc/mysql/mariadb.conf.d/50-server.cnf',
                        'my.mustache', data)
                else:
                    WOTemplate.deploy(
                        self, '/etc/mysql/my.cnf', 'my.mustache', data)
                # replacing default values
                Log.debug(self, "Tuning MySQL configuration")
                if os.path.isdir('/etc/systemd/system/mariadb.service.d'):
                    if not os.path.isfile(
                            '/etc/systemd/system/'
                            'mariadb.service.d/limits.conf'):
                        WOFileUtils.textwrite(
                            self,
                            '/etc/systemd/system/'
                            'mariadb.service.d/limits.conf',
                            '[Service]\nLimitNOFILE=500000')
                        WOShellExec.cmd_exec(self, 'systemctl daemon-reload')
                Log.valide(self, "Tuning MySQL configuration")
                # set innodb_buffer_pool_instances depending
                # on the amount of RAM

                WOService.restart_service(self, 'mariadb')

                # WOFileUtils.mvfile(self, '/var/lib/mysql/ib_logfile0',
                #                    '/var/lib/mysql/ib_logfile0.bak')
                # WOFileUtils.mvfile(self, '/var/lib/mysql/ib_logfile1',
                #                    '/var/lib/mysql/ib_logfile1.bak')

            WOCron.setcron_weekly(self, 'mysqlcheck -Aos --auto-repair '
                                  '> /dev/null 2>&1',
                                  comment='MySQL optimization cronjob '
                                  'added by WordOps')
            WOGit.add(self, ["/etc/mysql"], msg="Adding MySQL into Git")

        # create fail2ban configuration files
        if "fail2ban" in apt_packages:
            WOService.restart_service(self, 'fail2ban')
            if os.path.exists('/etc/fail2ban'):
                WOGit.add(self, ["/etc/fail2ban"],
                          msg="Adding Fail2ban into Git")
                Log.wait(self, "Configuring Fail2Ban")
                nginxf2b = bool(os.path.exists('/var/log/nginx'))
                data = dict(release=WOVar.wo_version, nginx=nginxf2b)
                WOTemplate.deploy(
                    self,
                    '/etc/fail2ban/jail.d/custom.conf',
                    'fail2ban.mustache',
                    data, overwrite=True)
                WOTemplate.deploy(
                    self,
                    '/etc/fail2ban/filter.d/wo-wordpress.conf',
                    'fail2ban-wp.mustache',
                    data, overwrite=False)
                WOTemplate.deploy(
                    self,
                    '/etc/fail2ban/filter.d/nginx-forbidden.conf',
                    'fail2ban-forbidden.mustache',
                    data, overwrite=False)

                if not WOShellExec.cmd_exec(self, 'fail2ban-client reload'):
                    WOGit.rollback(
                        self, ['/etc/fail2ban'], msg="Rollback f2b config")
                    WOService.restart_service(self, 'fail2ban')
                else:
                    Log.valide(self, "Configuring Fail2Ban")
                    WOGit.add(self, ["/etc/fail2ban"],
                              msg="Adding Fail2ban into Git")

        # Proftpd configuration
        if "proftpd-basic" in apt_packages:
            WOGit.add(self, ["/etc/proftpd"],
                      msg="Adding ProFTPd into Git")
            if os.path.isfile("/etc/proftpd/proftpd.conf"):
                Log.debug(self, "Setting up Proftpd configuration")
                data = dict()
                WOTemplate.deploy(self,
                                  '/etc/proftpd/proftpd.conf',
                                  'proftpd.mustache', data)
            # proftpd TLS configuration
            if not os.path.isdir("/etc/proftpd/ssl"):
                WOFileUtils.mkdir(self, "/etc/proftpd/ssl")
                SSL.selfsignedcert(self, proftpd=True, backend=False)
            WOFileUtils.chmod(self, "/etc/proftpd/ssl/proftpd.key", 0o700)
            WOFileUtils.chmod(self, "/etc/proftpd/ssl/proftpd.crt", 0o700)
            data = dict()
            WOTemplate.deploy(self, '/etc/proftpd/tls.conf',
                              'proftpd-tls.mustache', data)
            WOService.restart_service(self, 'proftpd')

            if os.path.isfile('/etc/ufw/ufw.conf'):
                # add rule for proftpd with UFW
                if WOFileUtils.grepcheck(
                        self, '/etc/ufw/ufw.conf', 'ENABLED=yes'):
                    try:
                        WOShellExec.cmd_exec(
                            self, "ufw limit 21")
                        WOShellExec.cmd_exec(
                            self, "ufw allow 49000:50000/tcp")
                        WOShellExec.cmd_exec(
                            self, "ufw reload")
                    except Exception as e:
                        Log.debug(self, "{0}".format(e))
                        Log.error(self, "Unable to add UFW rules")

            if ((os.path.exists("/etc/fail2ban/jail.d/custom.conf")) and
                (not WOFileUtils.grepcheck(
                    self, "/etc/fail2ban/jail.d/custom.conf",
                    "proftpd"))):
                with open("/etc/fail2ban/jail.d/custom.conf",
                          encoding='utf-8', mode='a') as f2bproftpd:
                    f2bproftpd.write("\n\n[proftpd]\nenabled = true\n")
                WOService.reload_service(self, 'fail2ban')

            if not WOService.reload_service(self, 'proftpd'):
                WOGit.rollback(self, ["/etc/proftpd"],
                               msg="Rollback ProFTPd")
            else:
                WOGit.add(self, ["/etc/proftpd"],
                          msg="Adding ProFTPd into Git")

        # Sendmail configuration
        if "sendmail" in apt_packages:
            if (os.path.exists("/usr/bin/yes") and
                    os.path.exists("/usr/sbin/sendmailconfig")):
                Log.wait(self, "Configuring Sendmail")
                if WOShellExec.cmd_exec(self, "yes 'y' | sendmailconfig"):
                    Log.valide(self, "Configuring Sendmail")
                else:
                    Log.failed(self, "Configuring Sendmail")

        if "ufw" in apt_packages:
            # check if ufw is already enabled
            if not WOFileUtils.grep(self,
                                    '/etc/ufw/ufw.conf', 'ENABLED=yes'):
                Log.wait(self, "Configuring UFW")
                # check if ufw script is already created
                if not os.path.isfile("/opt/ufw.sh"):
                    data = dict()
                    WOTemplate.deploy(self, '/opt/ufw.sh',
                                      'ufw.mustache',
                                      data, overwrite=False)
                    WOFileUtils.chmod(self, "/opt/ufw.sh", 0o700)
                # setup ufw rules
                WOShellExec.cmd_exec(self, "bash /opt/ufw.sh")
                Log.valide(self, "Configuring UFW")
            else:
                Log.info(self, "UFW is already installed and enabled")

        # Redis configuration
        if "redis-server" in apt_packages:
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
                        redis_file.write(
                            "# Log format Settings\n"
                            "log_format rt_cache_redis '$remote_addr "
                            "$upstream_response_time $srcache_fetch_status "
                            "[$time_local] '\n '$host \"$request\" "
                            "$status $body_bytes_sent '\n'\"$http_referer\" "
                            "\"$http_user_agent\"';\n")
            # set redis.conf parameter
            # set maxmemory 10% for ram below 512MB and 20% for others
            # set maxmemory-policy allkeys-lru
            # enable systemd service
            WOGit.add(self, ["/etc/redis"],
                      msg="Adding Redis into Git")
            Log.debug(self, "Enabling redis systemd service")
            WOShellExec.cmd_exec(self, "systemctl enable redis-server")
            if (os.path.isfile("/etc/redis/redis.conf") and
                    (not WOFileUtils.grep(self, "/etc/redis/redis.conf",
                                          "WordOps"))):
                Log.wait(self, "Tuning Redis configuration")
                with open("/etc/redis/redis.conf",
                          "a") as redis_file:
                    redis_file.write("\n# WordOps v3.9.9\n")
                wo_ram = psutil.virtual_memory().total / (1024 * 1024)
                if wo_ram < 1024:
                    Log.debug(self, "Setting maxmemory variable to "
                              "{0} in redis.conf"
                              .format(int(wo_ram * 1024 * 1024 * 0.1)))
                    WOFileUtils.searchreplace(
                        self,
                        "/etc/redis/redis.conf",
                        "# maxmemory <bytes>",
                        "maxmemory {0}"
                        .format
                        (int(wo_ram * 1024 * 1024 * 0.1)))

                else:
                    Log.debug(self, "Setting maxmemory variable to {0} "
                              "in redis.conf"
                              .format(int(wo_ram * 1024 * 1024 * 0.2)))
                    WOFileUtils.searchreplace(
                        self,
                        "/etc/redis/redis.conf",
                        "# maxmemory <bytes>",
                        "maxmemory {0}"
                        .format
                        (int(wo_ram * 1024 * 1024 * 0.2)))

                Log.debug(
                    self, "Setting maxmemory-policy variable to "
                    "allkeys-lru in redis.conf")
                WOFileUtils.searchreplace(
                    self, "/etc/redis/redis.conf",
                    "# maxmemory-policy noeviction",
                    "maxmemory-policy allkeys-lru")
                Log.debug(
                    self, "Setting tcp-backlog variable to "
                    "in redis.conf")
                WOFileUtils.searchreplace(self,
                                          "/etc/redis/redis.conf",
                                          "tcp-backlog 511",
                                          "tcp-backlog 32768")
                WOFileUtils.chown(self, '/etc/redis/redis.conf',
                                  'redis', 'redis', recursive=False)
                Log.valide(self, "Tuning Redis configuration")
            if not WOService.restart_service(self, 'redis-server'):
                WOGit.rollback(self, ["/etc/redis"], msg="Rollback Redis")
            else:
                WOGit.add(self, ["/etc/redis"], msg="Adding Redis into Git")

        # ClamAV configuration
        if set(WOVar.wo_clamav).issubset(set(apt_packages)):
            Log.debug(self, "Setting up freshclam cronjob")
            if not os.path.isfile("/opt/freshclam.sh"):
                data = dict()
                WOTemplate.deploy(self, '/opt/freshclam.sh',
                                  'freshclam.mustache',
                                  data, overwrite=False)
                WOFileUtils.chmod(self, "/opt/freshclam.sh", 0o775)
                WOCron.setcron_weekly(self, '/opt/freshclam.sh '
                                      '> /dev/null 2>&1',
                                      comment='ClamAV freshclam cronjob '
                                      'added by WordOps')

        # nanorc
        if 'nano' in apt_packages:
            Log.debug(self, 'Setting up nanorc')
            WOGit.clone(self, 'https://github.com/scopatz/nanorc.git',
                        '/usr/share/nano-syntax-highlighting')
            if os.path.exists('/etc/nanorc'):
                Log.debug(
                    self, 'including nano syntax highlighting to /etc/nanorc')
                if not WOFileUtils.grepcheck(self, '/etc/nanorc',
                                             'nano-syntax-highlighting'):
                    WOFileUtils.textappend(
                        self, '/etc/nanorc', 'include /usr/share/'
                        'nano-syntax-highlighting/*.nanorc')

    if (packages):
        # WP-CLI
        if any('/usr/local/bin/wp' == x[1] for x in packages):
            Log.debug(self, "Setting Privileges"
                      " to /usr/local/bin/wp file ")
            WOFileUtils.chmod(self, "/usr/local/bin/wp", 0o775)

        # PHPMyAdmin
        if any('/var/lib/wo/tmp/pma.tar.gz' == x[1]
               for x in packages):
            wo_phpmyadmin = WODownload.pma_release(self)
            WOExtract.extract(
                self, '/var/lib/wo/tmp/pma.tar.gz', '/var/lib/wo/tmp/')
            Log.debug(self, 'Extracting file /var/lib/wo/tmp/pma.tar.gz to '
                      'location /var/lib/wo/tmp/')
            if not os.path.exists('{0}22222/htdocs/db'
                                  .format(WOVar.wo_webroot)):
                Log.debug(self, "Creating new  directory "
                          "{0}22222/htdocs/db"
                          .format(WOVar.wo_webroot))
                os.makedirs('{0}22222/htdocs/db'
                            .format(WOVar.wo_webroot))
            if not os.path.exists('{0}22222/htdocs/db/pma/'
                                  .format(WOVar.wo_webroot)):
                shutil.move('/var/lib/wo/tmp/phpMyAdmin-{0}'
                            '-all-languages/'
                            .format(wo_phpmyadmin),
                            '{0}22222/htdocs/db/pma/'
                            .format(WOVar.wo_webroot))
                shutil.copyfile('{0}22222/htdocs/db/pma'
                                '/config.sample.inc.php'
                                .format(WOVar.wo_webroot),
                                '{0}22222/htdocs/db/pma/config.inc.php'
                                .format(WOVar.wo_webroot))
                Log.debug(self, 'Setting Blowfish Secret Key '
                          'FOR COOKIE AUTH to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVar.wo_webroot))
                blowfish_key = ''.join([random.choice
                                        (string.ascii_letters +
                                         string.digits)
                                        for n in range(32)])
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma'
                                          '/config.inc.php'
                                          .format(WOVar.wo_webroot),
                                          "$cfg[\'blowfish_secret\']"
                                          " = \'\';",
                                          "$cfg[\'blowfish_secret\']"
                                          " = \'{0}\';"
                                          .format(blowfish_key))
                Log.debug(self, 'Setting HOST Server For Mysql to  '
                          '{0}22222/htdocs/db/pma/config.inc.php file '
                          .format(WOVar.wo_webroot))
                WOFileUtils.searchreplace(self,
                                          '{0}22222/htdocs/db/pma'
                                          '/config.inc.php'
                                          .format(WOVar.wo_webroot),
                                          "$cfg[\'Servers\'][$i][\'host\']"
                                          " = \'localhost\';", "$cfg"
                                          "[\'Servers\'][$i][\'host\'] "
                                          "= \'{0}\';"
                                          .format(WOVar.wo_mysql_host))
                Log.debug(self, 'Setting Privileges of webroot permission to  '
                          '{0}22222/htdocs/db/pma file '
                          .format(WOVar.wo_webroot))
                WOFileUtils.chown(self, '{0}22222/htdocs'
                                  .format(WOVar.wo_webroot),
                                  'www-data',
                                  'www-data',
                                  recursive=True)

        # composer install and phpmyadmin update
        if any('/var/lib/wo/tmp/composer-install' == x[1]
               for x in packages):
            Log.wait(self, "Installing composer")
            WOShellExec.cmd_exec(self, "php -q /var/lib/wo"
                                 "/tmp/composer-install "
                                 "--install-dir=/var/lib/wo/tmp/")
            shutil.copyfile('/var/lib/wo/tmp/composer.phar',
                            '/usr/local/bin/composer')
            WOFileUtils.chmod(self, "/usr/local/bin/composer", 0o775)
            Log.valide(self, "Installing composer")
            if ((os.path.isdir("/var/www/22222/htdocs/db/pma")) and
                    (not os.path.isfile('/var/www/22222/htdocs/db/'
                                        'pma/composer.lock'))):
                Log.wait(self, "Updating phpMyAdmin")
                WOShellExec.cmd_exec(
                    self, "/usr/local/bin/composer update "
                    "--no-plugins --no-scripts -n --no-dev -d "
                    "/var/www/22222/htdocs/db/pma/")
                WOFileUtils.chown(
                    self, '{0}22222/htdocs/db/pma'
                    .format(WOVar.wo_webroot),
                    'www-data',
                    'www-data',
                    recursive=True)
                Log.valide(self, "Updating phpMyAdmin")
            if not os.path.exists('{0}22222/htdocs/cache/'
                                  'redis/phpRedisAdmin'
                                  .format(WOVar.wo_webroot)):
                Log.debug(self, "Creating new directory "
                          "{0}22222/htdocs/cache/redis"
                          .format(WOVar.wo_webroot))
                os.makedirs('{0}22222/htdocs/cache/redis/phpRedisAdmin'
                            .format(WOVar.wo_webroot))
            if not os.path.isfile('/var/www/22222/htdocs/cache/redis/'
                                  'phpRedisAdmin/composer.lock'):
                WOShellExec.cmd_exec(
                    self, "/usr/local/bin/composer "
                    "create-project --no-plugins --no-scripts -n -s dev "
                    "erik-dubbelboer/php-redis-admin "
                    "/var/www/22222/htdocs/cache/redis/phpRedisAdmin")
            WOFileUtils.chown(self, '{0}22222/htdocs'
                              .format(WOVar.wo_webroot),
                              'www-data',
                              'www-data',
                              recursive=True)

        # MySQLtuner
        if any('/usr/bin/mysqltuner' == x[1]
               for x in packages):
            Log.debug(self, "CHMOD MySQLTuner in /usr/bin/mysqltuner")
            WOFileUtils.chmod(self, "/usr/bin/mysqltuner", 0o775)

        # cheat.sh
        if any('/usr/local/bin/cht.sh' == x[1]
               for x in packages):
            Log.debug(self, "CHMOD cht.sh in /usr/local/bin/cht.sh")
            WOFileUtils.chmod(self, "/usr/local/bin/cht.sh", 0o775)
            if WOFileUtils.grepcheck(self, '/etc/bash_completion.d/cht.sh',
                                     'cht_complete cht.sh'):
                WOFileUtils.searchreplace(
                    self, '/etc/bash_completion.d/cht.sh',
                    '_cht_complete cht.sh',
                    '_cht_complete cheat')
            if not os.path.islink('/usr/local/bin/cheat'):
                WOFileUtils.create_symlink(
                    self, ['/usr/local/bin/cht.sh', '/usr/local/bin/cheat'])

        # netdata install
        if any('/var/lib/wo/tmp/kickstart.sh' == x[1]
               for x in packages):
            Log.wait(self, "Installing Netdata")
            WOShellExec.cmd_exec(
                self, "bash /var/lib/wo/tmp/kickstart.sh "
                "--dont-wait --stable-channel",
                errormsg='', log=False)
            Log.valide(self, "Installing Netdata")

            # disable mail notifications
            if os.path.exists('/usr/lib/netdata/conf.d/health_alarm_notify.conf'):
                WOFileUtils.searchreplace(
                    self, "/usr/lib/netdata/conf.d/health_alarm_notify.conf",
                    'SEND_EMAIL="YES"',
                    'SEND_EMAIL="NO"')

            if os.path.exists('/etc/netdata/orig/health_alarm_notify.conf'):
                WOFileUtils.searchreplace(
                    self, "/etc/netdata/orig/health_alarm_notify.conf",
                    'SEND_EMAIL="YES"',
                    'SEND_EMAIL="NO"')
            if self.app.config.has_section('mysql'):
                wo_grant_host = self.app.config.get('mysql', 'grant-host')
            else:
                wo_grant_host = 'localhost'
            # check if mysql credentials are available
            if (WOMysql.mariadb_ping(self)
                    and wo_grant_host == 'localhost'):
                try:
                    WOMysql.execute(
                        self,
                        "DELETE FROM mysql.user WHERE User = 'netdata';",
                        log=False)
                    WOMysql.execute(
                        self,
                        "create user 'netdata'@'127.0.0.1';",
                        log=False)
                    WOMysql.execute(
                        self,
                        "grant usage on *.* to 'netdata'@'127.0.0.1';",
                        log=False)
                    WOMysql.execute(
                        self, "flush privileges;",
                        log=False)
                except Exception as e:
                    Log.debug(self, "{0}".format(e))
                    Log.info(
                        self, "fail to setup mysql user for netdata")
            WOService.restart_service(self, 'netdata')

        # WordOps Dashboard
        if any('/var/lib/wo/tmp/wo-dashboard.tar.gz' == x[1]
               for x in packages):
            Log.debug(self, "Extracting wo-dashboard.tar.gz "
                      "to location {0}22222/htdocs/"
                      .format(WOVar.wo_webroot))
            WOExtract.extract(self, '/var/lib/wo/tmp/'
                              'wo-dashboard.tar.gz',
                              '{0}22222/htdocs'
                              .format(WOVar.wo_webroot))
            wo_wan = os.popen("/sbin/ip -4 route get 8.8.8.8 | "
                              "grep -oP \"dev [^[:space:]]+ \" "
                              "| cut -d ' ' -f 2").read()
            if (wo_wan != 'eth0' and wo_wan != ''):
                WOFileUtils.searchreplace(self,
                                          "{0}22222/htdocs/index.html"
                                          .format(WOVar.wo_webroot),
                                          "eth0",
                                          "{0}".format(wo_wan))
                Log.debug(self, "Setting Privileges to "
                          "{0}22222/htdocs"
                          .format(WOVar.wo_webroot))
                WOFileUtils.chown(self, '{0}22222/htdocs'
                                  .format(WOVar.wo_webroot),
                                  'www-data',
                                  'www-data',
                                  recursive=True)

        # Extplorer FileManager
        if any('/var/lib/wo/tmp/extplorer.tar.gz' == x[1]
               for x in packages):
            Log.debug(self, "Extracting extplorer.tar.gz "
                      "to location {0}22222/htdocs/files"
                      .format(WOVar.wo_webroot))
            WOExtract.extract(self, '/var/lib/wo/tmp/extplorer.tar.gz',
                              '/var/lib/wo/tmp/')
            shutil.move('/var/lib/wo/tmp/extplorer-{0}'
                        .format(WOVar.wo_extplorer),
                        '{0}22222/htdocs/files'
                        .format(WOVar.wo_webroot))
            Log.debug(self, "Setting Privileges to "
                      "{0}22222/htdocs/files"
                      .format(WOVar.wo_webroot))
            WOFileUtils.chown(self, '{0}22222/htdocs'
                              .format(WOVar.wo_webroot),
                              'www-data',
                              'www-data',
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
                                  .format(WOVar.wo_webroot)):
                Log.debug(self, "Creating directroy "
                          "{0}22222/htdocs/php"
                          .format(WOVar.wo_webroot))
                os.makedirs('{0}22222/htdocs/php'
                            .format(WOVar.wo_webroot))
            if not os.path.exists('{0}22222/htdocs/php/webgrind'
                                  .format(WOVar.wo_webroot)):
                shutil.move('/var/lib/wo/tmp/webgrind-master/',
                            '{0}22222/htdocs/php/webgrind'
                            .format(WOVar.wo_webroot))

            WOFileUtils.searchreplace(
                self, "{0}22222/htdocs/php/webgrind/"
                "config.php"
                .format(WOVar.wo_webroot),
                "/usr/local/bin/dot", "/usr/bin/dot")
            WOFileUtils.searchreplace(
                self, "{0}22222/htdocs/php/webgrind/"
                "config.php"
                .format(WOVar.wo_webroot),
                "Europe/Copenhagen",
                WOVar.wo_timezone)

            WOFileUtils.searchreplace(
                self, "{0}22222/htdocs/php/webgrind/"
                "config.php"
                .format(WOVar.wo_webroot),
                "90", "100")

            Log.debug(self, "Setting Privileges of webroot permission to "
                      "{0}22222/htdocs/php/webgrind/ file "
                      .format(WOVar.wo_webroot))
            WOFileUtils.chown(self, '{0}22222/htdocs'
                              .format(WOVar.wo_webroot),
                              'www-data',
                              'www-data',
                              recursive=True)

        # pt-query-advisor
        if any('/usr/bin/pt-query-advisor' == x[1]
               for x in packages):
            WOFileUtils.chmod(self, "/usr/bin/pt-query-advisor", 0o775)

        # ngxblocker
        if any('/usr/local/sbin/install-ngxblocker' == x[1]
               for x in packages):
            # remove duplicate directives
            if os.path.exists('/etc/nginx/conf.d/variables-hash.conf'):
                WOFileUtils.rm(self, '/etc/nginx/conf.d/variables-hash.conf')
            WOFileUtils.chmod(
                self, "/usr/local/sbin/install-ngxblocker", 0o700)
            WOShellExec.cmd_exec(self, '/usr/local/sbin/install-ngxblocker -x')
            WOFileUtils.chmod(
                self, "/usr/local/sbin/update-ngxblocker", 0o700)
            if not WOService.restart_service(self, 'nginx'):
                Log.error(self, 'ngxblocker install failed')


def pre_stack(self):
    """Inital server configuration and tweak"""
    # remove old sysctl tweak
    if os.path.isfile('/etc/sysctl.d/60-ubuntu-nginx-web-server.conf'):
        WOFileUtils.rm(
            self, '/etc/sysctl.d/60-ubuntu-nginx-web-server.conf')
    # check if version.txt exist
    if os.path.exists('/var/lib/wo/version.txt'):
        with open('/var/lib/wo/version.txt',
                  mode='r', encoding='utf-8') as wo_ver:
            # check version written in version.txt
            wo_check = bool(wo_ver.read().strip() ==
                            '{0}'.format(WOVar.wo_version))
    else:
        wo_check = False
    if wo_check is False:
        # wo sysctl tweaks
        # check system type
        wo_arch = bool((os.uname()[4]) == 'x86_64')
        if os.path.isfile('/proc/1/environ'):
            # detect lxc containers
            wo_lxc = WOFileUtils.grepcheck(
                self, '/proc/1/environ', 'container=lxc')
            # detect wsl
            wo_wsl = WOFileUtils.grepcheck(
                self, '/proc/1/environ', 'wsl')
        else:
            wo_wsl = True
            wo_lxc = True

        if (wo_lxc is not True) and (wo_wsl is not True) and (wo_arch is True):
            data = dict()
            WOTemplate.deploy(
                self, '/etc/sysctl.d/60-wo-tweaks.conf',
                'sysctl.mustache', data, True)
            # use tcp_bbr congestion algorithm only on new kernels
            if (WOVar.wo_platform_codename == 'focal' or
                WOVar.wo_platform_codename == 'buster' or
                WOVar.wo_platform_codename == 'jammy' or
                    WOVar.wo_platform_codename == 'bullseye' or
                    WOVar.wo_platform_codename == 'bookworm'):
                try:
                    WOShellExec.cmd_exec(
                        self, 'modprobe tcp_bbr')
                    with open(
                        "/etc/modules-load.d/bbr.conf",
                            encoding='utf-8', mode='w') as bbr_file:
                        bbr_file.write('tcp_bbr')
                    with open(
                        "/etc/sysctl.d/60-wo-tweaks.conf",
                            encoding='utf-8', mode='a') as sysctl_file:
                        sysctl_file.write(
                            '\nnet.ipv4.tcp_congestion_control = bbr'
                            '\nnet.ipv4.tcp_notsent_lowat = 16384')
                except OSError as e:
                    Log.debug(self, str(e))
                    Log.warn(self, "failed to tweak sysctl")
            else:
                try:
                    WOShellExec.cmd_exec(
                        self, 'modprobe tcp_htcp')
                    with open(
                        "/etc/modules-load.d/htcp.conf",
                            encoding='utf-8', mode='w') as bbr_file:
                        bbr_file.write('tcp_htcp')
                    with open(
                        "/etc/sysctl.d/60-wo-tweaks.conf",
                            encoding='utf-8', mode='a') as sysctl_file:
                        sysctl_file.write(
                            '\nnet.ipv4.tcp_congestion_control = htcp')
                except OSError as e:
                    Log.debug(self, str(e))
                    Log.warn(self, "failed to tweak sysctl")

            # apply sysctl tweaks
            WOShellExec.cmd_exec(
                self, 'sysctl -eq -p /etc/sysctl.d/60-wo-tweaks.conf')

        # sysctl tweak service
        data = dict()
        if not os.path.isfile('/opt/wo-kernel.sh'):
            WOTemplate.deploy(self, '/opt/wo-kernel.sh',
                              'wo-kernel-script.mustache', data)
        WOFileUtils.chmod(self, '/opt/wo-kernel.sh', 0o700)
        if not os.path.isfile('/lib/systemd/system/wo-kernel.service'):
            WOTemplate.deploy(
                self, '/lib/systemd/system/wo-kernel.service',
                'wo-kernel-service.mustache', data)
            WOShellExec.cmd_exec(self, 'systemctl enable wo-kernel.service')
            WOService.start_service(self, 'wo-kernel')
        # open_files_limit tweak
        if not WOFileUtils.grepcheck(self,
                                     '/etc/security/limits.conf', '500000'):
            with open("/etc/security/limits.conf",
                      encoding='utf-8', mode='a') as limit_file:
                limit_file.write(
                    '*         hard    nofile      500000\n'
                    '*         soft    nofile      500000\n'
                    'root      hard    nofile      500000\n'
                    'root      soft    nofile      500000\n')
        # custom motd-news
        data = dict()
        # check if update-motd.d directory exist
        if os.path.isdir('/etc/update-motd.d/'):
            # render custom motd template
            WOTemplate.deploy(
                self, '/etc/update-motd.d/98-wo-update',
                'wo-update.mustache', data)
            WOFileUtils.chmod(
                self, "/etc/update-motd.d/98-wo-update", 0o755)
        with open('/var/lib/wo/version.txt',
                  mode='w', encoding='utf-8') as wo_ver:
            wo_ver.write('{0}'.format(WOVar.wo_version))
