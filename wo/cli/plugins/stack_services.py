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
            (['--memcache'],
                dict(help='start/stop/restart memcache', action='store_true')),
            ]

    @expose(help="Start stack services")
    def start(self):
        """Start services"""
        services = []
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php7
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcache
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self,'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                if WOAptGet.is_installed(self, 'php5-fpm'):
                    services = services + ['php5-fpm']
                else:
                    Log.info(self, "PHP5-FPM is not installed")
            else:
                if WOAptGet.is_installed(self, 'php5.6-fpm'):
                    services = services + ['php5.6-fpm']
                else:
                    Log.info(self, "PHP5.6-FPM is not installed")

                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")

        if self.app.pargs.php7:
            if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")
            else:
                Log.info(self, "Your platform does not support PHP 7")

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
        if self.app.pargs.memcache:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcache is not installed")

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
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php7
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcache
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self,'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                if WOAptGet.is_installed(self, 'php5-fpm'):
                    services = services + ['php5-fpm']
                else:
                    Log.info(self, "PHP5-FPM is not installed")
            else:
                if WOAptGet.is_installed(self, 'php5.6-fpm'):
                    services = services + ['php5.6-fpm']
                else:
                    Log.info(self, "PHP5.6-FPM is not installed")

                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")

        if self.app.pargs.php7:
            if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")
            else:
                Log.info(self, "Your platform does not support PHP 7")

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
        if self.app.pargs.memcache:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcache is not installed")

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
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php7
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcache
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self,'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                if WOAptGet.is_installed(self, 'php5-fpm'):
                    services = services + ['php5-fpm']
                else:
                    Log.info(self, "PHP5-FPM is not installed")
            else:
                if WOAptGet.is_installed(self, 'php5.6-fpm'):
                    services = services + ['php5.6-fpm']
                else:
                    Log.info(self, "PHP5.6-FPM is not installed")

                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")

        if self.app.pargs.php7:
            if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")
            else:
                Log.info(self, "Your platform does not support PHP 7")


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
        if self.app.pargs.memcache:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcache is not installed")

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
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php7
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcache
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True
            self.app.pargs.hhvm = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self,'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                if WOAptGet.is_installed(self, 'php5-fpm'):
                    services = services + ['php5-fpm']
                else:
                    Log.info(self, "PHP5-FPM is not installed")
            else:
                if WOAptGet.is_installed(self, 'php5.6-fpm'):
                    services = services + ['php5.6-fpm']
                else:
                    Log.info(self, "PHP5.6-FPM is not installed")

                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")

        if self.app.pargs.php7:
            if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")
            else:
                Log.info(self, "Your platform does not support PHP 7")

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
        if self.app.pargs.memcache:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcache is not installed")

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
        if not (self.app.pargs.nginx or self.app.pargs.php or self.app.pargs.php7
                or self.app.pargs.mysql or self.app.pargs.hhvm or self.app.pargs.memcache 
                or self.app.pargs.redis):
            self.app.pargs.nginx = True
            self.app.pargs.php = True
            self.app.pargs.mysql = True

        if self.app.pargs.nginx:
            if WOAptGet.is_installed(self, 'nginx-custom') or WOAptGet.is_installed(self,'nginx-mainline'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if self.app.pargs.php:
            if (WOVariables.wo_platform_distro == 'debian' or WOVariables.wo_platform_codename == 'precise'):
                if WOAptGet.is_installed(self, 'php5-fpm'):
                    services = services + ['php5-fpm']
                else:
                    Log.info(self, "PHP5-FPM is not installed")
            else:
                if WOAptGet.is_installed(self, 'php5.6-fpm'):
                    services = services + ['php5.6-fpm']
                else:
                    Log.info(self, "PHP5.6-FPM is not installed")

                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")

        if self.app.pargs.php7:
            if (WOVariables.wo_platform_codename == 'trusty' or WOVariables.wo_platform_codename == 'xenial' or WOVariables.wo_platform_codename == 'bionic'):
                if WOAptGet.is_installed(self, 'php7.0-fpm'):
                    services = services + ['php7.0-fpm']
                else:
                    Log.info(self, "PHP7.0-FPM is not installed")
            else:
                Log.info(self, "Your platform does not support PHP 7")

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

        if self.app.pargs.memcache:
            if WOAptGet.is_installed(self, 'memcached'):
                services = services + ['memcached']
            else:
                Log.info(self, "Memcache is not installed")
                
        if self.app.pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        for service in services:
            Log.debug(self, "Reloading service: {0}".format(service))
            WOService.reload_service(self, service)
