"""WordOps Swap Creation"""
import os

import psutil

from wo.core.aptget import WOAptGet
from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec


class WOSwap():
    """Manage Swap"""

    def __init__():
        """Initialize """
        pass

    def add(self):
        """Swap addition with WordOps"""
        # Get System RAM and SWAP details
        wo_ram = psutil.virtual_memory().total / (1024 * 1024)
        wo_swap = psutil.swap_memory().total / (1024 * 1024)
        if wo_ram < 512:
            if wo_swap < 1000:
                Log.info(self, "Adding SWAP file, please wait...")

                # Install dphys-swapfile
                WOAptGet.update(self)
                WOAptGet.install(self, ["dphys-swapfile"])
                # Stop service
                WOShellExec.cmd_exec(self, "service dphys-swapfile stop")
                # Remove Default swap created
                WOShellExec.cmd_exec(self, "/sbin/dphys-swapfile uninstall")

                # Modify Swap configuration
                if os.path.isfile("/etc/dphys-swapfile"):
                    WOFileUtils.searchreplace(self, "/etc/dphys-swapfile",
                                              "#CONF_SWAPFILE=/var/swap",
                                              "CONF_SWAPFILE=/wo-swapfile")
                    WOFileUtils.searchreplace(self, "/etc/dphys-swapfile",
                                              "#CONF_MAXSWAP=2048",
                                              "CONF_MAXSWAP=1024")
                    WOFileUtils.searchreplace(self, "/etc/dphys-swapfile",
                                              "#CONF_SWAPSIZE=",
                                              "CONF_SWAPSIZE=1024")
                else:
                    with open("/etc/dphys-swapfile", 'w') as conffile:
                        conffile.write("CONF_SWAPFILE=/wo-swapfile\n"
                                       "CONF_SWAPSIZE=1024\n"
                                       "CONF_MAXSWAP=1024\n")
                # Create swap file
                WOShellExec.cmd_exec(self, "service dphys-swapfile start")
