import os

from cement.core.controller import CementBaseController, expose
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.variables import WOVar
from wo.core.fileutils import WOFileUtils


class WOStackStatusController(CementBaseController):
    class Meta:
        label = 'stack_services'
        stacked_on = 'stack'
        stacked_type = 'embedded'
        description = 'Check the stack status'

    @expose(help="Start stack services")
    def start(self):
        """Start services"""
        services = []
        wo_system = "/lib/systemd/system/"
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php72 or
                pargs.php73 or
                pargs.php74 or
                pargs.php80 or
                pargs.php81 or
                pargs.php82 or
                pargs.mysql or
                pargs.redis or
                pargs.fail2ban or
                pargs.proftpd or
                pargs.netdata or
                pargs.ufw):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True
            pargs.netdata = True
            pargs.ufw = True

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.php72:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

        if pargs.php73:
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php74:
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php80:
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")

        if pargs.php81:
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")

        if pargs.php82:
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.mysql:
            if ((WOVar.wo_mysql_host == "localhost") or
                    (WOVar.wo_mysql_host == "127.0.0.1")):
                if os.path.exists('/lib/systemd/system/mariadb.service'):
                    services = services + ['mariadb']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if os.path.exists('{0}'.format(wo_system) +
                              'redis-server.service'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if os.path.exists('{0}'.format(wo_system) + 'fail2ban.service'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if os.path.exists('/etc/init.d/proftpd'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if os.path.exists('{0}'.format(wo_system) + 'netdata.service'):
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
        wo_system = "/lib/systemd/system/"
        pargs = self.app.pargs
        if not (pargs.nginx or
                pargs.php or pargs.php72 or pargs.php73 or pargs.php74 or
                pargs.php80 or pargs.php81 or pargs.php82 or
                pargs.mysql or
                pargs.fail2ban or
                pargs.netdata or
                pargs.proftpd or
                pargs.redis):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php72:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

        if pargs.php73:
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php74:
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php80:
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")

        if pargs.php81:
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")

        if pargs.php82:
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.mysql:
            if ((WOVar.wo_mysql_host == "localhost") or
                    (WOVar.wo_mysql_host == "127.0.0.1")):
                if os.path.exists('/lib/systemd/system/mariadb.service'):
                    services = services + ['mariadb']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if os.path.exists('{0}'.format(wo_system) +
                              'redis-server.service'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if os.path.exists('{0}'.format(wo_system) + 'fail2ban.service'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if os.path.exists('/etc/init.d/proftpd'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if os.path.exists('{0}'.format(wo_system) + 'netdata.service'):
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
        wo_system = "/lib/systemd/system/"
        pargs = self.app.pargs
        if not (pargs.nginx or
                pargs.php or pargs.php72 or pargs.php73 or pargs.php74 or
                pargs.php80 or pargs.php81 or pargs.php82 or
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
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.php72:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

        if pargs.php73:
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php74:
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php80:
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")

        if pargs.php81:
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")

        if pargs.php82:
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.mysql:
            if ((WOVar.wo_mysql_host == "localhost") or
                    (WOVar.wo_mysql_host == "127.0.0.1")):
                if os.path.exists('/lib/systemd/system/mariadb.service'):
                    services = services + ['mariadb']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if os.path.exists('{0}'.format(wo_system) +
                              'redis-server.service'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if os.path.exists('{0}'.format(wo_system) + 'fail2ban.service'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if os.path.exists('/etc/init.d/proftpd'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if os.path.exists('{0}'.format(wo_system) + 'netdata.service'):
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
        wo_system = "/lib/systemd/system/"
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php72 or
                pargs.php73 or
                pargs.php74 or
                pargs.php80 or
                pargs.php81 or
                pargs.php82 or
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
            pargs.ufw = True

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.php72:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

        if pargs.php73:
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php74:
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php80:
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")

        if pargs.php81:
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")

        if pargs.php82:
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.mysql:
            if ((WOVar.wo_mysql_host == "localhost") or
                    (WOVar.wo_mysql_host == "127.0.0.1")):
                if os.path.exists('/lib/systemd/system/mariadb.service'):
                    services = services + ['mariadb']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if os.path.exists('{0}'.format(wo_system) +
                              'redis-server.service'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if os.path.exists('{0}'.format(wo_system) + 'fail2ban.service'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if os.path.exists('/etc/init.d/proftpd'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if os.path.exists('{0}'.format(wo_system) + 'netdata.service'):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        # UFW
        if pargs.ufw:
            if os.path.exists('/usr/sbin/ufw'):
                if WOFileUtils.grepcheck(
                        self, '/etc/ufw/ufw.conf', 'ENABLED=yes'):
                    Log.info(self, "UFW Firewall is enabled")
                else:
                    Log.info(self, "UFW Firewall is disabled")
            else:
                Log.info(self, "UFW is not installed")

        for service in services:
            if WOService.get_service_status(self, service):
                Log.info(self, "{0:10}:  {1}".format(service, "Running"))

    @expose(help="Reload stack services")
    def reload(self):
        """Reload service"""
        services = []
        wo_system = "/lib/systemd/system/"
        pargs = self.app.pargs
        if not (pargs.nginx or pargs.php or
                pargs.php72 or pargs.php73 or pargs.php74 or
                pargs.php80 or pargs.php81 or pargs.php82 or
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
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.php72:
            if os.path.exists('{0}'.format(wo_system) + 'php7.2-fpm.service'):
                services = services + ['php7.2-fpm']
            else:
                Log.info(self, "PHP7.2-FPM is not installed")

        if pargs.php73:
            if os.path.exists('{0}'.format(wo_system) + 'php7.3-fpm.service'):
                services = services + ['php7.3-fpm']
            else:
                Log.info(self, "PHP7.3-FPM is not installed")

        if pargs.php74:
            if os.path.exists('{0}'.format(wo_system) + 'php7.4-fpm.service'):
                services = services + ['php7.4-fpm']
            else:
                Log.info(self, "PHP7.4-FPM is not installed")

        if pargs.php80:
            if os.path.exists('{0}'.format(wo_system) + 'php8.0-fpm.service'):
                services = services + ['php8.0-fpm']
            else:
                Log.info(self, "PHP8.0-FPM is not installed")

        if pargs.php81:
            if os.path.exists('{0}'.format(wo_system) + 'php8.1-fpm.service'):
                services = services + ['php8.1-fpm']
            else:
                Log.info(self, "PHP8.1-FPM is not installed")

        if pargs.php82:
            if os.path.exists('{0}'.format(wo_system) + 'php8.2-fpm.service'):
                services = services + ['php8.2-fpm']
            else:
                Log.info(self, "PHP8.2-FPM is not installed")

        if pargs.mysql:
            if ((WOVar.wo_mysql_host == "localhost") or
                    (WOVar.wo_mysql_host == "127.0.0.1")):
                if os.path.exists('/lib/systemd/system/mariadb.service'):
                    services = services + ['mysql']
                else:
                    Log.info(self, "MySQL is not installed")
            else:
                Log.warn(self, "Remote MySQL found, "
                         "Unable to check MySQL service status")

        if pargs.redis:
            if os.path.exists('{0}'.format(wo_system) +
                              'redis-server.service'):
                services = services + ['redis-server']
            else:
                Log.info(self, "Redis server is not installed")

        if pargs.fail2ban:
            if os.path.exists('{0}'.format(wo_system) + 'fail2ban.service'):
                services = services + ['fail2ban']
            else:
                Log.info(self, "fail2ban is not installed")

        # proftpd
        if pargs.proftpd:
            if os.path.exists('/etc/init.d/proftpd'):
                services = services + ['proftpd']
            else:
                Log.info(self, "ProFTPd is not installed")

        # netdata
        if pargs.netdata:
            if os.path.exists('{0}'.format(wo_system) + 'netdata.service'):
                services = services + ['netdata']
            else:
                Log.info(self, "Netdata is not installed")

        for service in services:
            Log.debug(self, "Reloading service: {0}".format(service))
            WOService.reload_service(self, service)
