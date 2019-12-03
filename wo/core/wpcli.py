"""WordPress utilities for WordOps"""
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


class WOWp:
    """WordPress utilities for WordOps"""

    def wpcli(self, command):
        """WP-CLI wrapper"""
        try:
            WOShellExec.cmd_exec(
                self, '{0} --allow-root '.format(WOVar.wo_wpcli_path) +
                '{0}'.format(command))
        except Exception:
            Log.error(self, "WP-CLI command failed")
