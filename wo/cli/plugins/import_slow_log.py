from cement.core.controller import CementBaseController, expose

from wo.core.logging import Log


def wo_import_slow_log_hook(app):
    pass


class WOImportslowlogController(CementBaseController):
    class Meta:
        label = 'import_slow_log'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Import MySQL slow log to Anemometer database'
        usage = "wo import-slow-log"

    @expose(hide=True)
    def default(self):
        Log.info(self, "This command is deprecated."
                 " You can use this command instead, " +
                 Log.ENDC + Log.BOLD + "\n`wo debug --import-slow-log`" +
                 Log.ENDC)


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOImportslowlogController)

    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_import_slow_log_hook)
