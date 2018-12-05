from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from wo.core.download import WODownload
from wo.core.logging import Log
import time
import os


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
        usage = "wo update"

    @expose(hide=True)
    def default(self):
        filename = "woupdate" + time.strftime("%Y%m%d-%H%M%S")
        WODownload.download(self, [["https://wrdps.nl/woup",
                                    "/tmp/{0}".format(filename),
                                    "update script"]])
        try:
            Log.info(self, "updating WordOps, please wait...")
            os.system("bash /tmp/{0}".format(filename))
        except OSError as e:
            Log.debug(self, str(e))
            Log.error(self, "WordOps update failed !")
        except Exception as e:
            Log.debug(self, str(e))
            Log.error(self, "WordOps update failed !")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    handler.register(WOUpdateController)
    # register a hook (function) to run after arguments are parsed.
    hook.register('post_argument_parsing', wo_update_hook)
