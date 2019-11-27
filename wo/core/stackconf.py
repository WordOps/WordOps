import os
import configparser

from wo.core.logging import Log
from wo.core.template import WOTemplate
from wo.core.variables import WOVar
from wo.core.fileutils import WOFileUtils


class WOConf():
    """wo stack configuration utilities"""
    def __init__():
        pass

    def nginxcommon(self):
        """nginx common configuration deployment"""
        wo_php_version = ["php72", "php73", "php74"]
        ngxcom = '/etc/nginx/common'
        for wo_php in wo_php_version:
            Log.debug(self, 'deploying templates for {0}'.format(wo_php))
            data = dict(upstream="{0}".format(wo_php),
                        release=WOVar.wo_version)
            WOTemplate.deploy(self,
                              '{0}/{1}.conf'
                              .format(ngxcom, wo_php),
                              'php.mustache', data)

            WOTemplate.deploy(
                self, '{0}/redis-{1}.conf'.format(ngxcom, wo_php),
                'redis.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpcommon-{1}.conf'.format(ngxcom, wo_php),
                'wpcommon.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpfc-{1}.conf'.format(ngxcom, wo_php),
                'wpfc.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpsc-{1}.conf'.format(ngxcom, wo_php),
                'wpsc.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wprocket-{1}.conf'.format(ngxcom, wo_php),
                'wprocket.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpce-{1}.conf'.format(ngxcom, wo_php),
                'wpce.mustache', data)

    def phpconf(self, php_version):
        """Deploy configuration for php-fpm"""
        ngxroot = '/var/www/'
        php_number = (php_version.split('.'))[1]
        # Create log directories
        if not os.path.exists('/var/log/php/{0}/'.format(php_version)):
            Log.debug(
                self, 'Creating directory /var/log/php/{0}/'
                .format(php_version))
            os.makedirs('/var/log/php/{0}/'.format(php_version))

        if not os.path.isfile('/etc/php/{0}/fpm/php.ini.orig'
                              .format(php_version)):
            WOFileUtils.copyfile(self, '/etc/php/{0}/fpm/php.ini'
                                 .format(php_version),
                                 '/etc/php/{0}/fpm/php.ini.orig'
                                 .format(php_version))

            # Parse etc/php/7.x/fpm/php.ini
            config = configparser.ConfigParser()
            Log.debug(self, "configuring php file /etc/php/{0}/"
                      .format(php_version) +
                      "fpm/php.ini")
            config.read('/etc/php/{0}/fpm/php.ini.orig'.format(php_version))
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
            with open('/etc/php/{0}/fpm/php.ini'.format(php_version),
                      encoding='utf-8', mode='w') as configfile:
                Log.debug(self, "Writting php configuration into "
                          "/etc/php/{0}/fpm/php.ini".format(php_version))
                config.write(configfile)

            # Render php-fpm pool template for php7.x
            data = dict(pid="/run/php/php{0}-fpm.pid".format(php_version),
                        error_log="/var/log/php{0}-fpm.log".format(
                            php_version),
                        include="/etc/php/{0}/fpm/pool.d/*.conf"
                        .format(php_version))
            WOTemplate.deploy(
                self, '/etc/php/{0}/fpm/php-fpm.conf'.format(php_version),
                'php-fpm.mustache', data)

            data = dict(pool='www-php7{0}'.format(php_number),
                        listen='php7{0}-fpm.sock'.format(php_number),
                        user='www-data',
                        group='www-data', listenuser='root',
                        listengroup='www-data', openbasedir=True)
            WOTemplate.deploy(
                self, '/etc/php/{0}/fpm/pool.d/www.conf'.format(php_version),
                'php-pool.mustache', data)
            data = dict(pool='www-two-php7{0}'.format(php_number),
                        listen='php7{0}-two-fpm.sock'.format(php_number),
                        user='www-data',
                        group='www-data', listenuser='root',
                        listengroup='www-data', openbasedir=True)
            WOTemplate.deploy(
                self, '/etc/php/{0}/fpm/pool.d/www-two.conf'
                .format(php_version),
                'php-pool.mustache', data)

            # Generate /etc/php/7.x/fpm/pool.d/debug.conf
            WOFileUtils.copyfile(self, "/etc/php/{0}/fpm/pool.d/www.conf"
                                 .format(php_version),
                                 "/etc/php/{0}/fpm/pool.d/debug.conf"
                                 .format(php_version))
            WOFileUtils.searchreplace(self, "/etc/php/{0}/fpm/pool.d/"
                                      .format(php_version) +
                                      "debug.conf", "[www-php7{0}]"
                                      .format(php_number), "[debug]")
            config = configparser.ConfigParser()
            config.read(
                '/etc/php/{0}/fpm/pool.d/debug.conf'.format(php_version))
            config['debug']['listen'] = '127.0.0.1:917{0}'.format(php_number)
            config['debug']['rlimit_core'] = 'unlimited'
            config['debug']['slowlog'] = ('/var/log/php/{0}/slow.log'
                                          .format(php_version))
            config['debug']['request_slowlog_timeout'] = '10s'
            with open('/etc/php/{0}/fpm/pool.d/debug.conf'.format(php_version),
                      encoding='utf-8', mode='w') as confifile:
                Log.debug(self, "writting PHP {0} configuration into "
                          .format(php_version) +
                          "/etc/php/{0}/fpm/pool.d/debug.conf"
                          .format(php_version))
                config.write(confifile)

            with open("/etc/php/{0}/fpm/pool.d/debug.conf".format(php_version),
                      encoding='utf-8', mode='a') as myfile:
                myfile.write(
                    "php_admin_value[xdebug.profiler_output_dir] "
                    "= /tmp/ \nphp_admin_value[xdebug.profiler_"
                    "output_name] = cachegrind.out.%p-%H-%R "
                    "\nphp_admin_flag[xdebug.profiler_enable"
                    "_trigger] = on \nphp_admin_flag[xdebug."
                    "profiler_enable] = off\n")

            # Disable xdebug
            if not WOFileUtils.grepcheck(
                self, '/etc/php/{0}/mods-available/xdebug.ini'
                .format(php_version),
                    ';zend_extension'):
                WOFileUtils.searchreplace(
                    self, "/etc/php/{0}/mods-available/".format(php_version) +
                    "xdebug.ini",
                    "zend_extension", ";zend_extension")

            # PHP and Debug pull configuration
            if not os.path.exists('{0}22222/htdocs/fpm/status/'
                                  .format(ngxroot)):
                Log.debug(self, 'Creating directory '
                          '{0}22222/htdocs/fpm/status/ '
                          .format(ngxroot))
                os.makedirs('{0}22222/htdocs/fpm/status/'
                            .format(ngxroot))
            open('{0}22222/htdocs/fpm/status/debug7{1}'
                 .format(ngxroot, php_number),
                 encoding='utf-8', mode='a').close()
            open('{0}22222/htdocs/fpm/status/php7{1}'
                 .format(ngxroot, php_number),
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

            WOFileUtils.chown(self, "{0}22222/htdocs"
                              .format(ngxroot),
                              'www-data',
                              'www-data', recursive=True)
