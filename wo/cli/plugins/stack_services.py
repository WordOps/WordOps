import os

from cement.core import handler, hook
from cement.core.controller import CementBaseController, expose

from wo.core.aptget import WOAptGet
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.variables import WOVariables


class WOStackStatusController(CementBaseController):
    class Meta:
        label = 'stack_services'
        stacked_on = 'stack'
        stacked_type = 'embedded'
        exit_on_close = True
        description = 'Check the stack status'

    @expose(help="Start stack services")
    def start(self):
        """Start services"""
        services = []
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php73 or
                pargs.mysql or
                pargs.redis or
                pargs.fail2ban or
                pargs.proftpd or
                pargs.netdata):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True
            pargs.netdata = True

        if pargs.nginx:
            if (WOAptGet.is_installed(self, 'nginx-custom')):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.mysql:
            if ((WOVariables.wo_mysql_host == "localhost") or
                    (WOVariables.wo_mysql_host == "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if (os.path.isdir("/opt/netdata") or
                    os.path.isdir("/etc/netdata")):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            Log.debug(self, "Starting service: {0}".format(service))
            WOService.start_service(self, service)

    @expose(help="Stop stack services")
    def stop(self):
        """Stop services"""
        services = []
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php73 or
                pargs.mysql or
                pargs.fail2ban or
                pargs.netdata or
                pargs.proftpd or
                pargs.redis):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True

        # nginx
        if pargs.nginx:
            if (WOAptGet.is_installed(self, 'nginx-custom')):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        # php7.2
        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        # php7.3
        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        # mysql
        if pargs.mysql:
            if ((WOVariables.wo_mysql_host == "localhost") or
                    (WOVariables.wo_mysql_host == "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        # redis
        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        # fail2ban
        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if (os.path.isdir("/opt/netdata") or
                    os.path.isdir("/etc/netdata")):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            Log.debug(self, "Stopping service: {0}".format(service))
            WOService.stop_service(self, service)

    @expose(help="Restart stack services")
    def restart(self):
        """Restart services"""
        services = []
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php73 or
                pargs.mysql or
                pargs.netdata or
                pargs.proftpd or
                pargs.redis or
                pargs.fail2ban):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.netdata = True

        if pargs.nginx:
            if (WOAptGet.is_installed(self, 'nginx-custom')):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.mysql:
            if ((WOVariables.wo_mysql_host == "localhost") or
                    (WOVariables.wo_mysql_host == "127.0.0.1")):
                if ((WOAptGet.is_installed(self, 'mysql-server') or
                     WOAptGet.is_installed(self,
                                           'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server'))):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if (os.path.isdir("/opt/netdata") or
                    os.path.isdir("/etc/netdata")):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            Log.debug(self, "Restarting service: {0}".format(service))
            WOService.restart_service(self, service)

    @expose(help="Get stack status")
    def status(self):
        """Status of services"""
        services = []
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php73 or
                pargs.mysql or
                pargs.netdata or
                pargs.proftpd or
                pargs.redis or
                pargs.fail2ban):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True
            pargs.netdata = True

        if pargs.nginx:
            if (WOAptGet.is_installed(self, 'nginx-custom')):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.mysql:
            if ((WOVariables.wo_mysql_host == "localhost") or
                    (WOVariables.wo_mysql_host == "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if (os.path.isdir("/opt/netdata") or
                    os.path.isdir("/etc/netdata")):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            if WOService.get_service_status(self, service):
                Log.info(self, "{0:10}:  {1}".format(service, "Running"))

    @expose(help="Reload stack services")
    def reload(self):
        """Reload service"""
        services = []
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php73 or
                pargs.mysql or
                pargs.netdata or
                pargs.proftpd or
                pargs.redis or
                pargs.fail2ban):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True

        if pargs.nginx:
            if (WOAptGet.is_installed(self, 'nginx-custom') or
                    WOAptGet.is_installed(self, 'nginx-mainline')):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if WOAptGet.is_installed(self, 'php7.2-fpm'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php73:
            if WOAptGet.is_installed(self, 'php7.3-fpm'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.mysql:
            if ((WOVariables.wo_mysql_host == "localhost") or
                    (WOVariables.wo_mysql_host == "127.0.0.1")):
                if (WOAptGet.is_installed(self, 'mysql-server') or
                    WOAptGet.is_installed(self, 'percona-server-server-5.6') or
                        WOAptGet.is_installed(self, 'mariadb-server')):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if WOAptGet.is_installed(self, 'redis-server'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if WOAptGet.is_installed(self, 'fail2ban'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if WOAptGet.is_installed(self, 'proftpd-basic'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if (os.path.isdir("/opt/netdata") or
                    os.path.isdir("/etc/netdata")):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            Log.debug(self, "Reloading service: {0}".format(service))
            WOService.reload_service(self, service)
