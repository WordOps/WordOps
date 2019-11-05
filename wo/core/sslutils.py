import csv
import os
import re

from wo.core.fileutils import WOFileUtils
from wo.core.logging import Log
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


class SSL:

    def getexpirationdays(self, domain, returnonerror=False):
        # check if exist
        if not os.path.isfile('/etc/letsencrypt/live/{0}/cert.pem'
                              .format(domain)):
            Log.error(self, 'File Not Found: '
                      '/etc/letsencrypt/live/{0}/cert.pem'
                      .format(domain), False)
            if returnonerror:
                return -1
            Log.error(self, "Check the WordOps log for more details "
                      "`tail /var/log/wo/wordops.log` and please try again...")

        current_date = WOShellExec.cmd_exec_stdout(self, "date -d \"now\" +%s")
        expiration_date = WOShellExec.cmd_exec_stdout(
            self, "date -d \""
            "$(openssl x509 -in /etc/letsencrypt/live/"
            "{0}/cert.pem -text -noout | grep \"Not After\" "
            "| cut -c 25-)\" +%s"
            .format(domain))

        days_left = int((int(expiration_date) - int(current_date)) / 86400)
        if (days_left > 0):
            return days_left
        else:
            # return "Certificate Already Expired ! Please Renew soon."
            return -1

    def getexpirationdate(self, domain):
        # check if exist
        if os.path.islink('/var/www/{0}/conf/nginx/ssl.conf'):
            split_domain = domain.split('.')
            domain = ('.').join(split_domain[1:])
        if not os.path.isfile('/etc/letsencrypt/live/{0}/cert.pem'
                              .format(domain)):
            Log.error(self, 'File Not Found: /etc/letsencrypt/'
                      'live/{0}/cert.pem'
                      .format(domain), False)
            Log.error(self, "Check the WordOps log for more details "
                      "`tail /var/log/wo/wordops.log` and please try again...")

        expiration_date = WOShellExec.cmd_exec_stdout(
            self, "date -d \"$(/usr/bin/openssl x509 -in "
            "/etc/letsencrypt/live/{0}/cert.pem -text -noout | grep "
            "\"Not After\" | cut -c 25-)\" "
            .format(domain))
        return expiration_date

    def siteurlhttps(self, domain):
        wo_site_webroot = ('/var/www/{0}'.format(domain))
        WOFileUtils.chdir(
            self, '{0}/htdocs/'.format(wo_site_webroot))
        if WOShellExec.cmd_exec(
                self, "{0} --allow-root core is-installed"
                .format(WOVar.wo_wpcli_path)):
            wo_siteurl = (
                WOShellExec.cmd_exec_stdout(
                    self, "{0} option get siteurl "
                    .format(WOVar.wo_wpcli_path) +
                    "--allow-root --quiet"))
            test_url = re.split(":", wo_siteurl)
            if not (test_url[0] == 'https'):
                Log.wait(self, "Updating site url with https")
                try:
                    WOShellExec.cmd_exec(
                        self, "{0} option update siteurl "
                        "\'https://{1}\' --allow-root"
                        .format(WOVar.wo_wpcli_path, domain))
                    WOShellExec.cmd_exec(
                        self, "{0} option update home "
                        "\'https://{1}\' --allow-root"
                        .format(WOVar.wo_wpcli_path, domain))
                    WOShellExec.cmd_exec(
                        self, "{0} search-replace \'http://{1}\'"
                        "\'https://{1}\' --skip-columns=guid "
                        "--skip-tables=wp_users"
                        .format(WOVar.wo_wpcli_path, domain))
                except Exception as e:
                    Log.debug(self, str(e))
                    Log.failed(self, "Updating site url with https")
                else:
                    Log.valide(self, "Updating site url with https")

    # check if a wildcard exist to secure a new subdomain

    def checkwildcardexist(self, wo_domain_name):

        wo_acme_exec = ("/etc/letsencrypt/acme.sh --config-home "
                        "'/etc/letsencrypt/config'")
        # export certificates list from acme.sh
        WOShellExec.cmd_exec(
            self, "{0} ".format(wo_acme_exec) +
            "--list --listraw > /var/lib/wo/cert.csv")

        # define new csv dialect
        csv.register_dialect('acmeconf', delimiter='|')
        # open file
        certfile = open('/var/lib/wo/cert.csv', mode='r', encoding='utf-8')
        reader = csv.reader(certfile, 'acmeconf')
        wo_wildcard_domain = ("*.{0}".format(wo_domain_name))
        for row in reader:
            if wo_wildcard_domain in row[2]:
                if not row[2] == "":
                    iswildcard = True
                    break
            else:
                iswildcard = False
        certfile.close()

        return iswildcard

    def setuphsts(self, wo_domain_name):
        Log.info(
            self, "Adding /var/www/{0}/conf/nginx/hsts.conf"
            .format(wo_domain_name))

        hstsconf = open("/var/www/{0}/conf/nginx/hsts.conf"
                        .format(wo_domain_name),
                        encoding='utf-8', mode='w')
        hstsconf.write("more_set_headers "
                       "\"Strict-Transport-Security: "
                       "max-age=31536000; "
                       "includeSubDomains; "
                       "preload\";")
        hstsconf.close()
        return 0

    def selfsignedcert(self, proftpd=False, backend=False):
        """issue a self-signed certificate"""

        selfs_tmp = '/var/lib/wo/tmp/selfssl'
        # create self-signed tmp directory
        if not os.path.isdir(selfs_tmp):
            WOFileUtils.mkdir(self, selfs_tmp)
        try:
            WOShellExec.cmd_exec(
                self, "openssl genrsa -out "
                "{0}/ssl.key 2048"
                .format(selfs_tmp))
            WOShellExec.cmd_exec(
                self, "openssl req -new -batch  "
                "-subj /commonName=localhost/ "
                "-key {0}/ssl.key -out {0}/ssl.csr"
                .format(selfs_tmp))

            WOFileUtils.mvfile(
                self, "{0}/ssl.key"
                .format(selfs_tmp),
                "{0}/ssl.key.org"
                .format(selfs_tmp))

            WOShellExec.cmd_exec(
                self, "openssl rsa -in "
                "{0}/ssl.key.org -out "
                "{0}/ssl.key"
                .format(selfs_tmp))

            WOShellExec.cmd_exec(
                self, "openssl x509 -req -days "
                "3652 -in {0}/ssl.csr -signkey {0}"
                "/ssl.key -out {0}/ssl.crt"
                .format(selfs_tmp))

        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(
                self, "Failed to generate HTTPS "
                "certificate for 22222", False)
        if backend:
            WOFileUtils.mvfile(
                self, "{0}/ssl.key"
                .format(selfs_tmp),
                "/var/www/22222/cert/22222.key")
            WOFileUtils.mvfile(
                self, "{0}/ssl.crt"
                .format(selfs_tmp),
                "/var/www/22222/cert/22222.crt")
        if proftpd:
            WOFileUtils.mvfile(
                self, "{0}/ssl.key"
                .format(selfs_tmp),
                "/etc/proftpd/ssl/proftpd.key")
            WOFileUtils.mvfile(
                self, "{0}/ssl.crt"
                .format(selfs_tmp),
                "/etc/proftpd/ssl/proftpd.crt")
        # remove self-signed tmp directory
        WOFileUtils.rm(self, selfs_tmp)
