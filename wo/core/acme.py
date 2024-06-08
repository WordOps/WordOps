import csv
import os

from wo.core.fileutils import WOFileUtils
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec, CommandExecutionError
from wo.core.variables import WOVar
from wo.core.template import WOTemplate
from wo.core.checkfqdn import WOFqdn


class WOAcme:
    """Acme.sh utilities for WordOps"""

    wo_acme_exec = ("/etc/letsencrypt/acme.sh --config-home "
                    "'/etc/letsencrypt/config'")

    def check_acme(self):
        """
        Check if acme.sh is properly installed,
        and install it if required
        """
        if not os.path.exists('/etc/letsencrypt/acme.sh'):
            if os.path.exists('/opt/acme.sh'):
                WOFileUtils.rm(self, '/opt/acme.sh')
            WOGit.clone(
                self, 'https://github.com/Neilpang/acme.sh.git',
                '/opt/acme.sh', branch='master')
            WOFileUtils.mkdir(self, '/etc/letsencrypt/config')
            WOFileUtils.mkdir(self, '/etc/letsencrypt/renewal')
            WOFileUtils.mkdir(self, '/etc/letsencrypt/live')
            try:
                WOFileUtils.chdir(self, '/opt/acme.sh')
                WOShellExec.cmd_exec(
                    self, './acme.sh --install --home /etc/letsencrypt'
                    '--config-home /etc/letsencrypt/config'
                    '--cert-home /etc/letsencrypt/renewal'
                )
                WOShellExec.cmd_exec(
                    self, "{0} --upgrade --auto-upgrade"
                    .format(WOAcme.wo_acme_exec)
                )
            except CommandExecutionError as e:
                Log.debug(self, str(e))
                Log.error(self, "acme.sh installation failed")
        if not os.path.exists('/etc/letsencrypt/acme.sh'):
            Log.error(self, 'acme.sh ')

    def export_cert(self):
        """Export acme.sh csv certificate list"""
        # check acme.sh is installed
        WOAcme.check_acme(self)
        acme_list = WOShellExec.cmd_exec_stdout(
            self, "{0} ".format(WOAcme.wo_acme_exec) +
            "--list --listraw", log=False)
        if acme_list:
            WOFileUtils.textwrite(self, '/var/lib/wo/cert.csv', acme_list)
            WOFileUtils.chmod(self, '/var/lib/wo/cert.csv', 0o600)
        else:
            Log.error(self, "Unable to export certs list")

    def setupletsencrypt(self, acme_domains, acmedata):
        """Issue SSL certificates with acme.sh"""
        # check acme.sh is installed
        WOAcme.check_acme(self)
        # define variables
        all_domains = '\' -d \''.join(acme_domains)
        wo_acme_dns = acmedata['acme_dns']
        keylenght = acmedata['keylength']
        if acmedata['dns'] is True:
            acme_mode = "--dns {0}".format(wo_acme_dns)
            validation_mode = "DNS mode with {0}".format(wo_acme_dns)
            if acmedata['dnsalias'] is True:
                acme_mode = acme_mode + \
                    " --challenge-alias {0}".format(acmedata['acme_alias'])
        else:
            acme_mode = "-w /var/www/html"
            validation_mode = "Webroot challenge"
            Log.debug(self, "Validation : Webroot mode")
            if not os.path.isdir('/var/www/html/.well-known/acme-challenge'):
                WOFileUtils.mkdir(
                    self, '/var/www/html/.well-known/acme-challenge')
            WOFileUtils.chown(
                self, '/var/www/html/.well-known', 'www-data', 'www-data',
                recursive=True)
            WOFileUtils.chmod(self, '/var/www/html/.well-known', 0o750,
                              recursive=True)

        Log.info(self, "Validation mode : {0}".format(validation_mode))
        Log.wait(self, "Issuing SSL cert with acme.sh")
        if not WOShellExec.cmd_exec(
                self, "{0} ".format(WOAcme.wo_acme_exec) +
                "--issue -d '{0}' {1} -k {2} -f"
                .format(all_domains, acme_mode, keylenght), log=False):
            Log.failed(self, "Issuing SSL cert with acme.sh")
            if acmedata['dns'] is True:
                Log.error(
                    self, "Please make sure you properly "
                    "set your DNS API credentials for acme.sh\n"
                    "If you are using sudo, use \"sudo -E wo\"")
                return False
            else:
                Log.error(
                    self, "Your domain is properly configured "
                    "but acme.sh was unable to issue certificate.\n"
                    "You can find more informations in "
                    "/var/log/wo/wordops.log")
                return False
        else:
            Log.valide(self, "Issuing SSL cert with acme.sh")
            return True

    def deploycert(self, wo_domain_name):
        """Deploy Let's Encrypt certificates with acme.sh"""
        # check acme.sh is installed
        WOAcme.check_acme(self)
        if not os.path.isfile('/etc/letsencrypt/renewal/{0}_ecc/fullchain.cer'
                              .format(wo_domain_name)):
            Log.error(self, 'Certificate not found. Deployment canceled')

        Log.debug(self, "Cert deployment for domain: {0}"
                  .format(wo_domain_name))

        try:
            Log.wait(self, "Deploying SSL cert")
            if WOShellExec.cmd_exec(
                self, "mkdir -p {0}/{1} && {2} --install-cert -d {1} --ecc "
                "--cert-file {0}/{1}/cert.pem --key-file {0}/{1}/key.pem "
                "--fullchain-file {0}/{1}/fullchain.pem "
                "--ca-file {0}/{1}/ca.pem --reloadcmd \"nginx -t && "
                "service nginx restart\" "
                .format(WOVar.wo_ssl_live,
                        wo_domain_name, WOAcme.wo_acme_exec)):
                Log.valide(self, "Deploying SSL cert")
            else:
                Log.failed(self, "Deploying SSL cert")
                Log.error(self, "Unable to deploy certificate")

            if os.path.isdir('/var/www/{0}/conf/nginx'
                             .format(wo_domain_name)):

                data = dict(ssl_live_path=WOVar.wo_ssl_live,
                            domain=wo_domain_name, quic=True)
                WOTemplate.deploy(self,
                                  '/var/www/{0}/conf/nginx/ssl.conf'
                                  .format(wo_domain_name),
                                  'ssl.mustache', data, overwrite=False)

            if not WOFileUtils.grep(self, '/var/www/22222/conf/nginx/ssl.conf',
                                    '/etc/letsencrypt'):
                Log.info(self, "Securing WordOps backend with current cert")
                data = dict(ssl_live_path=WOVar.wo_ssl_live,
                            domain=wo_domain_name, quic=False)
                WOTemplate.deploy(self,
                                  '/var/www/22222/conf/nginx/ssl.conf',
                                  'ssl.mustache', data, overwrite=True)

            WOGit.add(self, ["/etc/letsencrypt"],
                      msg="Adding letsencrypt folder")

        except IOError as e:
            Log.debug(self, str(e))
            Log.debug(self, "Error occured while generating "
                      "ssl.conf")
        return 0

    def renew(self, domain):
        """Renew letsencrypt certificate with acme.sh"""
        # check acme.sh is installed
        WOAcme.check_acme(self)
        try:
            WOShellExec.cmd_exec(
                self, "{0} ".format(WOAcme.wo_acme_exec) +
                "--renew -d {0} --ecc --force".format(domain), log=False)
        except CommandExecutionError as e:
            Log.debug(self, str(e))
            Log.error(self, 'Unable to renew certificate')
        return True

    def check_dns(self, acme_domains):
        """Check if a list of domains point to the server IP"""
        server_ip = WOFqdn.get_server_ip(self)
        for domain in acme_domains:
            domain_ip = WOFqdn.get_domain_ip(self, domain)

            if (not domain_ip == server_ip):
                Log.warn(
                    self, "{0}".format(domain) +
                    " point to the IP {0}".format(domain_ip) +
                    " but your server IP is {0}.".format(server_ip) +
                    "\nUse the flag --force to bypass this check.")
                Log.error(
                    self, "You have to set the "
                    "proper DNS record for your domain", False)
                return False
        Log.debug(self, "DNS record are properly set")
        return True

    def cert_check(self, wo_domain_name):
        """Check certificate existance with acme.sh and return Boolean"""
        WOAcme.export_cert(self)
        # set variable acme_cert
        acme_cert = False
        # define new csv dialect
        csv.register_dialect('acmeconf', delimiter='|')
        # open file
        certfile = open('/var/lib/wo/cert.csv',
                        mode='r', encoding='utf-8')
        reader = csv.reader(certfile, 'acmeconf')
        for row in reader:
            # check if domain exist
            if wo_domain_name == row[0]:
                # check if cert expiration exist
                if not row[3] == '':
                    acme_cert = True
        certfile.close()
        if acme_cert is True:
            if os.path.exists(
                '/etc/letsencrypt/live/{0}/fullchain.pem'
                    .format(wo_domain_name)):
                return True
        return False

    def removeconf(self, domain):
        sslconf = ("/var/www/{0}/conf/nginx/ssl.conf"
                   .format(domain))
        sslforce = ("/etc/nginx/conf.d/force-ssl-{0}.conf"
                    .format(domain))
        acmedir = [
            '{0}'.format(sslforce), '{0}'.format(sslconf),
            '{0}/{1}_ecc'.format(WOVar.wo_ssl_archive, domain),
            '{0}.disabled'.format(sslconf), '{0}.disabled'
            .format(sslforce), '{0}/{1}'
            .format(WOVar.wo_ssl_live, domain),
            '/etc/letsencrypt/shared/{0}.conf'.format(domain)]
        wo_domain = domain
        # check acme.sh is installed
        WOAcme.check_acme(self)
        if WOAcme.cert_check(self, wo_domain):
            Log.info(self, "Removing Acme configuration")
            Log.debug(self, "Removing Acme configuration")
            try:
                WOShellExec.cmd_exec(
                    self, "{0} ".format(WOAcme.wo_acme_exec) +
                    "--remove -d {0} --ecc".format(domain))
            except CommandExecutionError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Cert removal failed")
            # remove all files and directories
            for dir in acmedir:
                if os.path.exists('{0}'.format(dir)):
                    WOFileUtils.rm(self, '{0}'.format(dir))

        else:
            if os.path.islink("{0}".format(sslconf)):
                WOFileUtils.remove_symlink(self, "{0}".format(sslconf))
                WOFileUtils.rm(self, '{0}'.format(sslforce))

        if WOFileUtils.grepcheck(self, '/var/www/22222/conf/nginx/ssl.conf',
                                 '{0}'.format(domain)):
            Log.info(
                self, "Setting back default certificate for WordOps backend")
            with open("/var/www/22222/conf/nginx/"
                      "ssl.conf", "w") as ssl_conf_file:
                ssl_conf_file.write("ssl_certificate "
                                    "/var/www/22222/cert/22222.crt;\n"
                                    "ssl_certificate_key "
                                    "/var/www/22222/cert/22222.key;\n"
                                    "ssl_stapling off;\n")
