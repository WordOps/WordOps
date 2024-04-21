import requests

from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


class WOFqdn:
    """IP and FQDN tools for WordOps"""

    def check_fqdn(self, wo_host):
        """FQDN check with WordOps, for mail server hostname must be FQDN"""
        # wo_host=os.popen("hostname -f | tr -d '\n'").read()
        if '.' in wo_host:
            WOVar.wo_fqdn = wo_host
            with open('/etc/hostname', encoding='utf-8', mode='w') as hostfile:
                hostfile.write(wo_host)

            WOShellExec.cmd_exec(self, "sed -i \"1i\\127.0.0.1 {0}\" /etc/hosts"
                                 .format(wo_host))
            if WOVar.wo_distro == 'debian':
                WOShellExec.cmd_exec(self, "/etc/init.d/hostname.sh start")
            else:
                WOShellExec.cmd_exec(self, "service hostname restart")

        else:
            wo_host = input("Enter hostname [fqdn]:")
            WOFqdn.check_fqdn(self, wo_host)

    def check_fqdn_ip(self):
        """Check if server hostname resolved server IP"""
        try:
            x = requests.get('http://v4.wordops.eu')
            ip = (x.text).strip()

            wo_fqdn = WOVar.wo_fqdn
            y = requests.get('http://v4.wordops.eu/dns/{0}/'.format(wo_fqdn))
            ip_fqdn = (y.text).strip()

            return bool(ip == ip_fqdn)
        except requests.exceptions.RequestException as e:
            print("Error occurred during request:", e)
            return False

    def get_server_ip(self):
        """Get the server externet IP"""
        try:
            x = requests.get('http://v4.wordops.eu')
            ip = (x.text).strip()

            return ip
        except requests.exceptions.RequestException as e:
            print("Error occurred during request:", e)
            return None

    def get_domain_ip(self, wo_domain):
        """Get the server externet IP"""
        try:
            y = requests.get('http://v4.wordops.eu/dns/{0}/'.format(wo_domain))
            domain_ip = (y.text).strip()

            return domain_ip
        except requests.exceptions.RequestException as e:
            print("Error occurred during request:", e)
            return None
