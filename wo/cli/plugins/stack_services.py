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
        if all(value is None or value is False for value in vars(pargs).values()):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True
            pargs.netdata = True
            pargs.ufw = True

        if pargs.php:
            if self.app.config.has_section('php'):
                config_php_ver = self.app.config.get(
                    'php', 'version')
                current_php = config_php_ver.replace(".", "")
                setattr(self.app.pargs, 'php{0}'.format(current_php), True)

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            for parg_version, version in WOVar.wo_php_versions.items():
                if os.path.exists(f'{wo_system}' + f'php{version}-fpm.service'):
                    services = services + [f'php{version}-fpm']

        for parg_version, version in WOVar.wo_php_versions.items():
            if (getattr(pargs, parg_version, False) and
                    os.path.exists(f'{wo_system}' + f'php{version}-fpm.service')):
                services = services + [f'php{version}-fpm']
            else:
                Log.info(self, f"PHP{version}-FPM is not installed")

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
        if all(value is None or value is False for value in vars(pargs).values()):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True

        if pargs.php:
            if self.app.config.has_section('php'):
                config_php_ver = self.app.config.get(
                    'php', 'version')
                current_php = config_php_ver.replace(".", "")
                setattr(self.app.pargs, 'php{0}'.format(current_php), True)

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            for parg_version, version in WOVar.wo_php_versions.items():
                if os.path.exists(f'{wo_system}' + f'php{version}-fpm.service'):
                    services = services + [f'php{version}-fpm']

        for parg_version, version in WOVar.wo_php_versions.items():
            if (getattr(pargs, parg_version, False) and
                    os.path.exists(f'{wo_system}' + f'php{version}-fpm.service')):
                services = services + [f'php{version}-fpm']
            else:
                Log.info(self, f"PHP{version}-FPM is not installed")

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
        if all(value is None or value is False for value in vars(pargs).values()):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.netdata = True

        if pargs.php:
            if self.app.config.has_section('php'):
                config_php_ver = self.app.config.get(
                    'php', 'version')
                current_php = config_php_ver.replace(".", "")
                setattr(self.app.pargs, 'php{0}'.format(current_php), True)

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            for parg_version, version in WOVar.wo_php_versions.items():
                if os.path.exists(f'{wo_system}' + f'php{version}-fpm.service'):
                    services = services + [f'php{version}-fpm']

        for parg_version, version in WOVar.wo_php_versions.items():
            if (getattr(pargs, parg_version, False) and
                    os.path.exists(f'{wo_system}' + f'php{version}-fpm.service')):
                services = services + [f'php{version}-fpm']
            else:
                Log.info(self, f"PHP{version}-FPM is not installed")

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
        if all(value is None or value is False for value in vars(pargs).values()):
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
            for parg_version, version in WOVar.wo_php_versions.items():
                if os.path.exists(f'{wo_system}' + f'php{version}-fpm.service'):
                    services = services + [f'php{version}-fpm']

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
        if all(value is None or value is False for value in vars(pargs).values()):
            pargs.nginx = True
            pargs.php = True
            pargs.mysql = True
            pargs.fail2ban = True

        if pargs.php:
            if self.app.config.has_section('php'):
                config_php_ver = self.app.config.get(
                    'php', 'version')
                current_php = config_php_ver.replace(".", "")
                setattr(self.app.pargs, 'php{0}'.format(current_php), True)

        if pargs.nginx:
            if os.path.exists('{0}'.format(wo_system) + 'nginx.service'):
                services = services + ['nginx']
            else:
                Log.info(self, "Nginx is not installed")

        if pargs.php:
            for parg_version, version in WOVar.wo_php_versions.items():
                if os.path.exists(f'{wo_system}' + f'php{version}-fpm.service'):
                    services = services + [f'php{version}-fpm']

        for parg_version, version in WOVar.wo_php_versions.items():
            if (getattr(pargs, parg_version, False) and
                    os.path.exists(f'{wo_system}' + f'php{version}-fpm.service')):
                services = services + [f'php{version}-fpm']
            else:
                Log.info(self, f"PHP{version}-FPM is not installed")

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
