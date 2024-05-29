"""Clean Plugin for WordOps."""

import os
import requests

from cement.core.controller import CementBaseController, expose

from wo.core.aptget import WOAptGet
from wo.core.logging import Log
from wo.core.services import WOService
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


def wo_clean_hook(app):
    pass


class WOCleanController(CementBaseController):
    class Meta:
        label = 'clean'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = (
            'Clean NGINX FastCGI cache, Opcache, Redis Cache')
        arguments = [
            (['--all'],
                dict(help='Clean all cache', action='store_true')),
            (['--fastcgi'],
                dict(help='Clean FastCGI cache', action='store_true')),
            (['--opcache'],
                dict(help='Clean OpCache', action='store_true')),
            (['--redis'],
                dict(help='Clean Redis Cache', action='store_true')),
        ]
        usage = "wo clean [options]"

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if ((not pargs.all) and (not pargs.fastcgi) and
                (not pargs.opcache) and (not pargs.redis)):
            self.clean_fastcgi()
        if pargs.all:
            self.clean_fastcgi()
            self.clean_opcache()
            self.clean_redis()
        if pargs.fastcgi:
            self.clean_fastcgi()
        if pargs.opcache:
            self.clean_opcache()
        if pargs.redis:
            self.clean_redis()

    @expose(hide=True)
    def clean_redis(self):
        """This function clears Redis cache"""
        if (WOAptGet.is_installed(self, "redis-server")):
            Log.info(self, "Cleaning Redis cache")
            WOShellExec.cmd_exec(self, "redis-cli flushall")
        else:
            Log.info(self, "Redis is not installed")

    @expose(hide=True)
    def clean_fastcgi(self):
        if (os.path.isdir("/var/run/nginx-cache") and
           os.path.exists('/usr/sbin/nginx')):
            Log.info(self, "Cleaning NGINX FastCGI cache")
            WOShellExec.cmd_exec(self, "rm -rf /var/run/nginx-cache/*")
            WOService.restart_service(self, 'nginx')
        else:
            Log.error(self, "Unable to clean FastCGI cache", False)

    @expose(hide=True)
    def clean_opcache(self):
        opcache_dir = '/var/www/22222/htdocs/cache/opcache/'
        if (os.path.exists('/usr/sbin/nginx') and
                os.path.exists(
                    '/var/www/22222/htdocs/cache/opcache')):
            try:
                Log.info(self, "Cleaning opcache")
                wo_php_version = list(WOVar.wo_php_versions.keys())
                for wo_php in wo_php_version:
                    if os.path.exists('{0}{1}.php'.format(opcache_dir, wo_php)):
                        requests.get(
                            "http://127.0.0.1/cache/opcache/{0}.php".format(wo_php))

            except requests.HTTPError as e:
                Log.debug(self, "{0}".format(e))
                Log.debug(self, "Unable hit url, "
                          " http://127.0.0.1/cache/opcache/"
                          "phpXX.php,"
                          " please check you have admin tools installed")
                Log.debug(self, "please check you have admin tools installed,"
                          " or install them with `wo stack install --admin`")
                Log.error(self, "Unable to clean opcache", False)


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOCleanController)
    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_clean_hook)
