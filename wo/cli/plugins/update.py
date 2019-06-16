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
        stacked_type = 'nested'
        description = ('update WordOps to latest version')
        arguments = [
            (['--force'],
             dict(help='Force WordOps update', action='store_true')),
        ]
        usage = "wo update [options]"

    @expose(hide=True)
    def default(self):
        filename = "woupdate" + time.strftime("%Y%m%d-%H%M%S")
        WODownload.download(self, [["https://raw.githubusercontent.com/"
                                    "WordOps/WordOps/master/install",
                                    "/tmp/{0}".format(filename),
                                    "update script"]])
        if self.app.pargs.force:
            try:
                Log.info(self, "updating WordOps, please wait...")
                os.system("bash /tmp/{0} --force".format(filename))
            except OSError as e:
                Log.debug(self, str(e))
                Log.error(self, "WordOps update failed !")
        else:
            try:
                Log.info(self, "updating WordOps, please wait...")
                os.system("bash /tmp/{0}".format(filename))
            except OSError as e:
                Log.debug(self, str(e))
                Log.error(self, "WordOps update failed !")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    handler.register(WOUpdateController)
    # register a hook (function) to run after arguments are parsed.
    hook.register('post_argument_parsing', wo_update_hook)
