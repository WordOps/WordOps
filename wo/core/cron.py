from wo.core.logging import Log
from wo.core.shellexec import WOShellExec


"""
Set CRON on LINUX system.
"""


class WOCron():
    def setcron_weekly(self, cmd, comment='Cron set by WordOps', user='root',
                       min=0, hour=12):
        if not WOShellExec.cmd_exec(self, "crontab -l "
                                    "| grep -q \'{0}\'".format(cmd)):

            WOShellExec.cmd_exec(self, "/bin/bash -c \"crontab -l "
                                 "2> /dev/null | {{ cat; echo -e"
                                 " \\\""
                                 "\\n0 0 * * 0 "
                                 "{0}".format(cmd) +
                                 " # {0}".format(comment) +
                                 "\\\"; } | crontab -\"")
            Log.debug(self, "Cron set")

    def setcron_daily(self, cmd, comment='Cron set by WordOps', user='root',
                      min=0, hour=12):
        if not WOShellExec.cmd_exec(self, "crontab -l "
                                    "| grep -q \'{0}\'".format(cmd)):

            WOShellExec.cmd_exec(self, "/bin/bash -c \"crontab -l "
                                 "2> /dev/null | {{ cat; echo -e"
                                 " \\\""
                                 "\\n@daily"
                                 "{0}".format(cmd) +
                                 " # {0}".format(comment) +
                                 "\\\"; } | crontab -\"")
            Log.debug(self, "Cron set")

    def remove_cron(self, cmd):
        if WOShellExec.cmd_exec(self, "crontab -l "
                                "| grep -q \'{0}\'".format(cmd)):
            if not WOShellExec.cmd_exec(self, "/bin/bash -c "
                                        "\"crontab "
                                        "-l | sed '/{0}/d'"
                                        "| crontab -\""
                                        .format(cmd)):
                Log.error(self, "Failed to remove crontab entry", False)
        else:
            Log.debug(self, "Cron not found")
