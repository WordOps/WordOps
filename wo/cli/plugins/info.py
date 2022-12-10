"""WOInfo Plugin for WordOps"""

import configparser
import os

from cement.core.controller import CementBaseController, expose
from pynginxconfig import NginxConfig

from wo.core.aptget import WOAptGet
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec


def wo_info_hook(app):
    pass


class WOInfoController(CementBaseController):
    class Meta:
        label = 'info'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = ('Display configuration information related to Nginx,'
                       ' PHP and MySQL')
        arguments = [
            (['--mysql'],
                dict(help='Get MySQL configuration information',
                     action='store_true')),
            (['--php'],
                dict(help='Get PHP 7.2 configuration information',
                     action='store_true')),
            (['--php73'],
                dict(help='Get PHP 7.3 configuration information',
                     action='store_true')),
            (['--php74'],
                dict(help='Get PHP 7.4 configuration information',
                     action='store_true')),
            (['--php80'],
                dict(help='Get PHP 8.0 configuration information',
                     action='store_true')),
            (['--php81'],
                dict(help='Get PHP 8.1 configuration information',
                     action='store_true')),
            (['--php82'],
                dict(help='Get PHP 8.2 configuration information',
                     action='store_true')),
            (['--nginx'],
                dict(help='Get Nginx configuration information',
                     action='store_true')),
        ]
        usage = "wo info [options]"

    @expose(hide=True)
    def info_nginx(self):
        """Display Nginx information"""
        version = os.popen("/usr/sbin/nginx -v 2>&1 | "
                           "awk -F '/' '{print $2}' | "
                           "awk -F ' ' '{print $1}' | tr '\n' ' '").read()
        allow = os.popen("grep ^allow /etc/nginx/common/acl.conf | "
                         "cut -d' ' -f2 | cut -d';' -f1 | tr '\n' ' '").read()
        nc = NginxConfig()
        nc.loadf('/etc/nginx/nginx.conf')
        user = nc.get('user')[1]
        worker_processes = nc.get('worker_processes')[1]
        worker_connections = nc.get([('events',), 'worker_connections'])[1]
        keepalive_timeout = nc.get([('http',), 'keepalive_timeout'])[1]
        fastcgi_read_timeout = nc.get([('http',),
                                       'fastcgi_read_timeout'])[1]
        client_max_body_size = nc.get([('http',),
                                       'client_max_body_size'])[1]
        data = dict(version=version, allow=allow, user=user,
                    worker_processes=worker_processes,
                    keepalive_timeout=keepalive_timeout,
                    worker_connections=worker_connections,
                    fastcgi_read_timeout=fastcgi_read_timeout,
                    client_max_body_size=client_max_body_size)
        self.app.render((data), 'info_nginx.mustache')

    @expose(hide=True)
    def info_php(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php7.2 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/{0}/fpm/php.ini'.format("php/7.2"))
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/7.2/fpm/pool.d/www.conf'):
            config.read('/etc/php/7.2/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php72'):
            wconfig = config['www-php72']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (
                wconfig['php_admin_flag[xdebug.profiler_enable'
                        '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/{0}/fpm/pool.d/debug.conf'.format("php/7.2"))
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_php73(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php7.3 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/php/7.3/fpm/php.ini')
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/7.3/fpm/pool.d/www.conf'):
            config.read('/etc/php/7.3/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php73'):
            wconfig = config['www-php73']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (wconfig
                          ['php_admin_flag[xdebug.profiler_enable'
                           '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/php/7.3/fpm/pool.d/debug.conf')
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_php74(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php7.4 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/php/7.4/fpm/php.ini')
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/7.4/fpm/pool.d/www.conf'):
            config.read('/etc/php/7.4/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php74'):
            wconfig = config['www-php74']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (wconfig
                          ['php_admin_flag[xdebug.profiler_enable'
                           '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/php/7.4/fpm/pool.d/debug.conf')
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_php80(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php8.0 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/php/8.0/fpm/php.ini')
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/8.0/fpm/pool.d/www.conf'):
            config.read('/etc/php/8.0/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php80'):
            wconfig = config['www-php80']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (wconfig
                          ['php_admin_flag[xdebug.profiler_enable'
                           '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/php/8.0/fpm/pool.d/debug.conf')
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_php81(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php8.1 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/php/8.1/fpm/php.ini')
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/8.1/fpm/pool.d/www.conf'):
            config.read('/etc/php/8.1/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php81'):
            wconfig = config['www-php81']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (wconfig
                          ['php_admin_flag[xdebug.profiler_enable'
                           '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/php/8.1/fpm/pool.d/debug.conf')
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_php82(self):
        """Display PHP information"""
        version = os.popen("/usr/bin/php8.2 -v 2>/dev/null | "
                           "head -n1 | cut -d' ' -f2 |"
                           " cut -d'+' -f1 | tr -d '\n'").read
        config = configparser.ConfigParser()
        config.read('/etc/php/8.2/fpm/php.ini')
        expose_php = config['PHP']['expose_php']
        memory_limit = config['PHP']['memory_limit']
        post_max_size = config['PHP']['post_max_size']
        upload_max_filesize = config['PHP']['upload_max_filesize']
        max_execution_time = config['PHP']['max_execution_time']

        if os.path.exists('/etc/php/8.2/fpm/pool.d/www.conf'):
            config.read('/etc/php/8.2/fpm/pool.d/www.conf')
        else:
            Log.error(self, 'php-fpm pool config not found')
        if config.has_section('www'):
            wconfig = config['www']
        elif config.has_section('www-php82'):
            wconfig = config['www-php82']
        else:
            Log.error(self, 'Unable to parse configuration')
        www_listen = wconfig['listen']
        www_ping_path = wconfig['ping.path']
        www_pm_status_path = wconfig['pm.status_path']
        www_pm = wconfig['pm']
        www_pm_max_requests = wconfig['pm.max_requests']
        www_pm_max_children = wconfig['pm.max_children']
        www_pm_start_servers = wconfig['pm.start_servers']
        www_pm_min_spare_servers = wconfig['pm.min_spare_servers']
        www_pm_max_spare_servers = wconfig['pm.max_spare_servers']
        www_request_terminate_time = (wconfig
                                      ['request_terminate_timeout'])
        try:
            www_xdebug = (wconfig
                          ['php_admin_flag[xdebug.profiler_enable'
                           '_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            www_xdebug = 'off'

        config.read('/etc/php/8.2/fpm/pool.d/debug.conf')
        debug_listen = config['debug']['listen']
        debug_ping_path = config['debug']['ping.path']
        debug_pm_status_path = config['debug']['pm.status_path']
        debug_pm = config['debug']['pm']
        debug_pm_max_requests = config['debug']['pm.max_requests']
        debug_pm_max_children = config['debug']['pm.max_children']
        debug_pm_start_servers = config['debug']['pm.start_servers']
        debug_pm_min_spare_servers = config['debug']['pm.min_spare_servers']
        debug_pm_max_spare_servers = config['debug']['pm.max_spare_servers']
        debug_request_terminate = (config['debug']
                                         ['request_terminate_timeout'])
        try:
            debug_xdebug = (config['debug']['php_admin_flag[xdebug.profiler_'
                                            'enable_trigger]'])
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            debug_xdebug = 'off'

        data = dict(version=version, expose_php=expose_php,
                    memory_limit=memory_limit, post_max_size=post_max_size,
                    upload_max_filesize=upload_max_filesize,
                    max_execution_time=max_execution_time,
                    www_listen=www_listen, www_ping_path=www_ping_path,
                    www_pm_status_path=www_pm_status_path, www_pm=www_pm,
                    www_pm_max_requests=www_pm_max_requests,
                    www_pm_max_children=www_pm_max_children,
                    www_pm_start_servers=www_pm_start_servers,
                    www_pm_min_spare_servers=www_pm_min_spare_servers,
                    www_pm_max_spare_servers=www_pm_max_spare_servers,
                    www_request_terminate_timeout=www_request_terminate_time,
                    www_xdebug_profiler_enable_trigger=www_xdebug,
                    debug_listen=debug_listen, debug_ping_path=debug_ping_path,
                    debug_pm_status_path=debug_pm_status_path,
                    debug_pm=debug_pm,
                    debug_pm_max_requests=debug_pm_max_requests,
                    debug_pm_max_children=debug_pm_max_children,
                    debug_pm_start_servers=debug_pm_start_servers,
                    debug_pm_min_spare_servers=debug_pm_min_spare_servers,
                    debug_pm_max_spare_servers=debug_pm_max_spare_servers,
                    debug_request_terminate_timeout=debug_request_terminate,
                    debug_xdebug_profiler_enable_trigger=debug_xdebug)
        self.app.render((data), 'info_php.mustache')

    @expose(hide=True)
    def info_mysql(self):
        """Display MySQL information"""
        version = os.popen("/usr/bin/mysql -V | awk '{print($5)}' | "
                           "cut -d ',' "
                           "-f1 | tr -d '\n'").read()
        host = "localhost"
        port = os.popen("/usr/bin/mysql -e \"show variables\" | "
                        "/bin/grep ^port | awk "
                        "'{print($2)}' | tr -d '\n'").read()
        wait_timeout = os.popen("/usr/bin/mysql -e \"show variables\" | grep "
                                "^wait_timeout | awk '{print($2)}' | "
                                "tr -d '\n'").read()
        interactive_timeout = os.popen("/usr/bin/mysql -e "
                                       "\"show variables\" | grep "
                                       "^interactive_timeout | awk "
                                       "'{print($2)}' | tr -d '\n'").read()
        max_used_connections = os.popen("/usr/bin/mysql -e "
                                        "\"show global status\" | "
                                        "grep Max_used_connections | awk "
                                        "'{print($2)}' | tr -d '\n'").read()
        datadir = os.popen("/usr/bin/mysql -e \"show variables\" | "
                           "/bin/grep datadir | awk"
                           " '{print($2)}' | tr -d '\n'").read()
        socket = os.popen("/usr/bin/mysql -e \"show variables\" | "
                          "/bin/grep \"^socket\" | "
                          "awk '{print($2)}' | tr -d '\n'").read()
        data = dict(version=version, host=host, port=port,
                    wait_timeout=wait_timeout,
                    interactive_timeout=interactive_timeout,
                    max_used_connections=max_used_connections,
                    datadir=datadir, socket=socket)
        self.app.render((data), 'info_mysql.mustache')

    @expose(hide=True)
    def default(self):
        """default function for info"""
        pargs = self.app.pargs
        if (not pargs.nginx and not pargs.php and
                not pargs.mysql and not pargs.php73 and
                not pargs.php74 and not pargs.php80 and
                not pargs.php81 and not pargs.php82):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                pargs.php73 = True
            if WOAptGet.is_installed(self, 'php7.4-fpm'):
                pargs.php74 = True
            if WOAptGet.is_installed(self, 'php8.0-fpm'):
                pargs.php80 = True
            if WOAptGet.is_installed(self, 'php8.1-fpm'):
                pargs.php81 = True
            if WOAptGet.is_installed(self, 'php8.2-fpm'):
                pargs.php82 = True

        if pargs.nginx:
            if ((not WOAptGet.is_installed(self, 'nginx-custom')) and
                    (not os.path.exists('/usr/bin/nginx'))):
                Log.info(self, "Nginx is not installed")
            else:
                self.info_nginx()

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                self.info_php()
            else:
                Log.info(self, "PHP 7.2 is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                self.info_php73()
            else:
                Log.info(self, "PHP 7.3 is not installed")

        if pargs.php74:
            if WOAptGet.is_installed(self, 'php7.4-fpm'):
                self.info_php74()
            else:
                Log.info(self, "PHP 7.4 is not installed")

        if pargs.php80:
            if WOAptGet.is_installed(self, 'php8.0-fpm'):
                self.info_php80()
            else:
                Log.info(self, "PHP 8.0 is not installed")

        if pargs.php81:
            if WOAptGet.is_installed(self, 'php8.1-fpm'):
                self.info_php81()
            else:
                Log.info(self, "PHP 8.1 is not installed")

        if pargs.php82:
            if WOAptGet.is_installed(self, 'php8.2-fpm'):
                self.info_php82()
            else:
                Log.info(self, "PHP 8.2 is not installed")

        if pargs.mysql:
            if WOShellExec.cmd_exec(self, "/usr/bin/mysqladmin ping"):
                self.info_mysql()
            else:
                Log.info(self, "MySQL is not installed")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOInfoController)

    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_info_hook)
