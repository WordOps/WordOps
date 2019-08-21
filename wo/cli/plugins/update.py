import os
import time

from cement.core import handler, hook
from cement.core.controller import CementBaseController, expose
from wo.core.download import WODownload
from wo.core.logging import Log


def wo_update_hook(app):
    pass


class WOUpdateController(CementBaseController):
    class Meta:
        label = 'wo_update'
        stacked_on = 'base'
        aliases = ['update']
        aliases_only = True
        stacked_type = 'nested'
        description = ('update WordOps to latest version')
        arguments = [
            (['--force'],
             dict(help='Force WordOps update', action='store_true')),
            (['--preserve'],
             dict(help='Preserve current Nginx configuration',
                  action='store_true')),
            (['--beta'],
             dict(help='Update WordOps to latest beta release',
                  action='store_true')),
            (['--travis'],
             dict(help='Argument used only for WordOps development',
                  action='store_true')),
        ]
        usage = "wo update [options]"

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        filename = "woupdate" + time.strftime("%Y%m%d-%H%M%S")

        if pargs.beta:
            wo_branch = "beta"
            install_args = ""
        else:
            wo_branch = "master"
            install_args = ""
        if pargs.force:
            install_args = install_args + "--force "
        if pargs.preserve:
            install_args = install_args + "--preserve "

        WODownload.download(self, [["https://raw.githubusercontent.com/"
                                    "WordOps/WordOps/{0}/install"
                                    .format(wo_branch),
                                    "/var/lib/wo/tmp/{0}".format(filename),
                                    "update script"]])

        if pargs.travis:
            try:
                Log.info(self, "updating WordOps, please wait...")
                os.system("/bin/bash install --travis "
                          "-b $TRAVIS_BRANCH --force")
            except OSError as e:
                Log.debug(self, str(e))
                Log.error(self, "WordOps update failed !")
        else:
            try:
                Log.info(self, "updating WordOps, please wait...")
                os.system("/bin/bash /var/lib/wo/tmp/{0} "
                          "-b {1} {2}".format(filename,
                                              wo_branch, install_args))
            except OSError as e:
                Log.debug(self, str(e))
                Log.error(self, "WordOps update failed !")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    handler.register(WOUpdateController)
    # register a hook (function) to run after arguments are parsed.
    hook.register('post_argument_parsing', wo_update_hook)
