from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVariables
import os


def check_fqdn(self, wo_host):
    """FQDN check with WordOps, for mail server hostname must be FQDN"""
    # wo_host=os.popen("hostname -f | tr -d '\n'").read()
    if '.' in wo_host:
        WOVariables.wo_fqdn = wo_host
        with open('/etc/hostname', encoding='utf-8', mode='w') as hostfile:
            hostfile.write(wo_host)

        WOShellExec.cmd_exec(self, "sed -i \"1i\\127.0.0.1 {0}\" /etc/hosts"
                                   .format(wo_host))
        if WOVariables.wo_platform_distro == 'debian':
            WOShellExec.cmd_exec(self, "/etc/init.d/hostname.sh start")
        else:
            WOShellExec.cmd_exec(self, "service hostname restart")

    else:
        wo_host = input("Enter hostname [fqdn]:")
        check_fqdn(self, wo_host)
