"""Maintenance Plugin for WordOps"""

from cement.core.controller import CementBaseController, expose

from wo.core.aptget import WOAptGet
from wo.core.logging import Log


def wo_maintenance_hook(app):
    pass


class WOMaintenanceController(CementBaseController):
    class Meta:
        label = 'maintenance'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = ('update server packages to latest version')
        usage = "wo maintenance"

    @expose(hide=True)
    def default(self):

        try:
            Log.info(self, "updating apt-cache, please wait...")
            WOAptGet.update(self)
            Log.info(self, "updating packages, please wait...")
            WOAptGet.dist_upgrade(self)
            Log.info(self, "cleaning-up packages, please wait...")
            WOAptGet.auto_remove(self)
            WOAptGet.auto_clean(self)
        except OSError as e:
            Log.debug(self, str(e))
            Log.error(self, "Package updates failed !")
        except Exception as e:
            Log.debug(self, str(e))
            Log.error(self, "Packages updates failed !")


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOMaintenanceController)
    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_maintenance_hook)
