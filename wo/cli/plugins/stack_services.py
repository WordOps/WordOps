from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.services import WOService
from wo.core.logging import Log
from wo.core.variables import WOVariables
from wo.core.aptget import WOAptGet


class WOStackStatusController(CementBaseController):
    class Meta:
        label = 'stack_services'
        stacked_on = 'stack'
        stacked_type = 'embedded'
        description = 'Check the stack status'
        arguments = [
            (['--memcached'],
                dict(help='start/stop/restart memcached', action='store_true')),
        ]

    @expose(help="Start stack services")
    def start(self):
        """Start services"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php73
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcached
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self, 'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.mysql:
            if ((WOVariables.wo_mysql_host is "localhost") or
                    (WOVariables.wo_mysql_host is "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if self.app.pargs.hhvm:
            if WOAptGet.is_installed(self, 'hhvm'):
                services = services + ['hhvm']
            else:
                Log.info(self, "HHVM is not installed")
        if self.app.pargs.memcached:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcached is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            Log.debug(self, "Starting service: {0}".format(service))
            WOService.start_service(self, service)

    @expose(help="Stop stack services")
    def stop(self):
        """Stop services"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php73
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcached
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self, 'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.mysql:
            if ((WOVariables.wo_mysql_host is "localhost") or
                    (WOVariables.wo_mysql_host is "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if self.app.pargs.hhvm:
            if WOAptGet.is_installed(self, 'hhvm'):
                services = services + ['hhvm']
            else:
                Log.info(self, "HHVM is not installed")
        if self.app.pargs.memcached:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcached is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            Log.debug(self, "Stopping service: {0}".format(service))
            WOService.stop_service(self, service)

    @expose(help="Restart stack services")
    def restart(self):
        """Restart services"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php73
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcached
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self, 'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.mysql:
            if ((WOVariables.wo_mysql_host is "localhost") or
                    (WOVariables.wo_mysql_host is "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if self.app.pargs.hhvm:
            if WOAptGet.is_installed(self, 'hhvm'):
                services = services + ['hhvm']
            else:
                Log.info(self, "HHVM is not installed")
        if self.app.pargs.memcached:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcached is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            Log.debug(self, "Restarting service: {0}".format(service))
            WOService.restart_service(self, service)

    @expose(help="Get stack status")
    def status(self):
        """Status of services"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php73
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcached
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True
            self.app.pargs.hhvm = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self, 'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.mysql:
            if ((WOVariables.wo_mysql_host is "localhost") or
                    (WOVariables.wo_mysql_host is "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if self.app.pargs.hhvm:
            if WOAptGet.is_installed(self, 'hhvm'):
                services = services + ['hhvm']
            else:
                Log.info(self, "HHVM is not installed")
        if self.app.pargs.memcached:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcached is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            if WOService.get_service_status(self, service):
                Log.info(self, "{0:10}:  {1}".format(service, "Running"))

    @expose(help="Reload stack services")
    def reload(self):
        """Reload service"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php73
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcached
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self, 'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
             else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if self.app.pargs.mysql:
            if ((WOVariables.wo_mysql_host is "localhost") or
                    (WOVariables.wo_mysql_host is "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if self.app.pargs.hhvm:
            Log.info(self, "HHVM does not support to reload")

        if self.app.pargs.memcached:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcached is not installed")

        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            Log.debug(self, "Reloading service: {0}".format(service))
            WOService.reload_service(self, service)
