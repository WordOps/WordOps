import os

from cement.core.controller import CementBaseController, expose
from wo.cli.plugins.site_functions import (
    detSitePar, check_domain_exists, site_package_check,
    pre_run_checks, setupdomain, SiteError,
    doCleanupAction, setupdatabase, setupwordpress, setwebrootpermissions,
    display_cache_settings, copyWildcardCert)
from wo.cli.plugins.sitedb import (deleteSiteInfo, getAllsites,
                                   getSiteInfo, updateSiteInfo)
from wo.core.acme import WOAcme
from wo.core.domainvalidate import WODomain
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.nginxhashbucket import hashbucket
from wo.core.services import WOService
from wo.core.sslutils import SSL
from wo.core.variables import WOVar


class WOSiteBackupController(CementBaseController):
    class Meta:
        label = 'backup'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = ('this commands allow you to backup your sites')
        arguments = [
            (['site_name'],
                dict(help='domain name for the site to be cloned.',
                     nargs='?')),
            (['--db'],
                dict(help="backup only site database", action='store_true')),
            (['--files'],
                dict(help="backup only site files", action='store_true')),
            (['--all'],
                dict(help="backup all sites", action='store_true')),
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        # self.app.render((data), 'default.mustache')
        # Check domain name validation
        data = dict()
        sites = getAllsites(self)

        if not pargs.site_name and not pargs.all:
            try:
                while not pargs.site_name:
                    # preprocessing before finalize site name
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, "Unable to input site name, Please try again!")

        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        (wo_domain_type, wo_root_domain) = WODomain.getlevel(
            self, wo_domain)
        if not wo_domain.strip():
            Log.error(self, "Invalid domain name, "
                      "Provide valid domain name")

        wo_site_webroot = WOVar.wo_webroot + wo_domain

        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} already exists".format(wo_domain))
        elif os.path.isfile('/etc/nginx/sites-available/{0}'
                            .format(wo_domain)):
            Log.error(self, "Nginx configuration /etc/nginx/sites-available/"
                      "{0} already exists".format(wo_domain))


        try:
            try:
                # setup NGINX configuration, and webroot
                setupdomain(self, data)

                # Fix Nginx Hashbucket size error
                hashbucket(self)
            except SiteError as e:
                # call cleanup actions on failure
                Log.info(self, Log.FAIL +
                         "There was a serious error encountered...")
                Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                doCleanupAction(self, domain=wo_domain,
                                webroot=data['webroot'])
                Log.debug(self, str(e))
                Log.error(self, "Check the log for details: "
                          "`tail /var/log/wo/wordops.log` "
                          "and please try again")

            if 'proxy' in data.keys() and data['proxy']:
                addNewSite(self, wo_domain, stype, cache, wo_site_webroot)
                # Service Nginx Reload
                if not WOService.reload_service(self, 'nginx'):
                    Log.info(self, Log.FAIL +
                             "There was a serious error encountered...")
                    Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                    doCleanupAction(self, domain=wo_domain)
                    deleteSiteInfo(self, wo_domain)
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
                    Log.error(self, "Check the log for details: "
                              "`tail /var/log/wo/wordops.log` "
                              "and please try again")
                if wo_auth and len(wo_auth):
                    for msg in wo_auth:
                        Log.info(self, Log.ENDC + msg, log=False)
                Log.info(self, "Successfully created site"
                         " http://{0}".format(wo_domain))
                return

            if data['php72']:
                php_version = "7.2"
            elif data['php74']:
                php_version = "7.4"
            else:
                php_version = "7.3"

            addNewSite(self, wo_domain, stype, cache, wo_site_webroot,
                       php_version=php_version)

            # Setup database for MySQL site
            if 'wo_db_name' in data.keys() and not data['wp']:
                try:
                    data = setupdatabase(self, data)
                    # Add database information for site into database
                    updateSiteInfo(self, wo_domain, db_name=data['wo_db_name'],
                                   db_user=data['wo_db_user'],
                                   db_password=data['wo_db_pass'],
                                   db_host=data['wo_db_host'])
                except SiteError as e:
                    # call cleanup actions on failure
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL +
                             "There was a serious error encountered...")
                    Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                    doCleanupAction(self, domain=wo_domain,
                                    webroot=data['webroot'],
                                    dbname=data['wo_db_name'],
                                    dbuser=data['wo_db_user'],
                                    dbhost=data['wo_db_host'])
                    deleteSiteInfo(self, wo_domain)
                    Log.error(self, "Check the log for details: "
                              "`tail /var/log/wo/wordops.log` "
                              "and please try again")

                try:
                    wodbconfig = open("{0}/wo-config.php"
                                      .format(wo_site_webroot),
                                      encoding='utf-8', mode='w')
                    wodbconfig.write("<?php \ndefine('DB_NAME', '{0}');"
                                     "\ndefine('DB_USER', '{1}'); "
                                     "\ndefine('DB_PASSWORD', '{2}');"
                                     "\ndefine('DB_HOST', '{3}');\n?>"
                                     .format(data['wo_db_name'],
                                             data['wo_db_user'],
                                             data['wo_db_pass'],
                                             data['wo_db_host']))
                    wodbconfig.close()
                    stype = 'mysql'
                except IOError as e:
                    Log.debug(self, str(e))
                    Log.debug(self, "Error occured while generating "
                              "wo-config.php")
                    Log.info(self, Log.FAIL +
                             "There was a serious error encountered...")
                    Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                    doCleanupAction(self, domain=wo_domain,
                                    webroot=data['webroot'],
                                    dbname=data['wo_db_name'],
                                    dbuser=data['wo_db_user'],
                                    dbhost=data['wo_db_host'])
                    deleteSiteInfo(self, wo_domain)
                    Log.error(self, "Check the log for details: "
                              "`tail /var/log/wo/wordops.log` "
                              "and please try again")

            # Setup WordPress if Wordpress site
            if data['wp']:
                vhostonly = bool(pargs.vhostonly)
                try:
                    wo_wp_creds = setupwordpress(self, data, vhostonly)
                    # Add database information for site into database
                    updateSiteInfo(self, wo_domain,
                                   db_name=data['wo_db_name'],
                                   db_user=data['wo_db_user'],
                                   db_password=data['wo_db_pass'],
                                   db_host=data['wo_db_host'])
                except SiteError as e:
                    # call cleanup actions on failure
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL +
                             "There was a serious error encountered...")
                    Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                    doCleanupAction(self, domain=wo_domain,
                                    webroot=data['webroot'],
                                    dbname=data['wo_db_name'],
                                    dbuser=data['wo_db_user'],
                                    dbhost=data['wo_mysql_grant_host'])
                    deleteSiteInfo(self, wo_domain)
                    Log.error(self, "Check the log for details: "
                              "`tail /var/log/wo/wordops.log` "
                              "and please try again")

            # Service Nginx Reload call cleanup if failed to reload nginx
            if not WOService.reload_service(self, 'nginx'):
                Log.info(self, Log.FAIL +
                         "There was a serious error encountered...")
                Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                doCleanupAction(self, domain=wo_domain,
                                webroot=data['webroot'])
                if 'wo_db_name' in data.keys():
                    doCleanupAction(self, domain=wo_domain,
                                    dbname=data['wo_db_name'],
                                    dbuser=data['wo_db_user'],
                                    dbhost=data['wo_mysql_grant_host'])
                deleteSiteInfo(self, wo_domain)
                Log.info(self, Log.FAIL + "service nginx reload failed."
                         " check issues with `nginx -t` command.")
                Log.error(self, "Check the log for details: "
                          "`tail /var/log/wo/wordops.log` "
                          "and please try again")

            WOGit.add(self, ["/etc/nginx"],
                      msg="{0} created with {1} {2}"
                      .format(wo_www_domain, stype, cache))
            # Setup Permissions for webroot
            try:
                setwebrootpermissions(self, data['webroot'])
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL +
                         "There was a serious error encountered...")
                Log.info(self, Log.FAIL + "Cleaning up afterwards...")
                doCleanupAction(self, domain=wo_domain,
                                webroot=data['webroot'])
                if 'wo_db_name' in data.keys():
                    print("Inside db cleanup")
                    doCleanupAction(self, domain=wo_domain,
                                    dbname=data['wo_db_name'],
                                    dbuser=data['wo_db_user'],
                                    dbhost=data['wo_mysql_grant_host'])
                deleteSiteInfo(self, wo_domain)
                Log.error(self, "Check the log for details: "
                          "`tail /var/log/wo/wordops.log` and "
                          "please try again")

            if wo_auth and len(wo_auth):
                for msg in wo_auth:
                    Log.info(self, Log.ENDC + msg, log=False)

            if data['wp'] and (not pargs.vhostonly):
                Log.info(self, Log.ENDC + "WordPress admin user :"
                         " {0}".format(wo_wp_creds['wp_user']), log=False)
                Log.info(self, Log.ENDC + "WordPress admin password : {0}"
                         .format(wo_wp_creds['wp_pass']), log=False)

                display_cache_settings(self, data)

            Log.info(self, "Successfully created site"
                     " http://{0}".format(wo_domain))
        except SiteError:
            Log.error(self, "Check the log for details: "
                      "`tail /var/log/wo/wordops.log` and please try again")

        if pargs.letsencrypt:
            acme_domains = []
            data['letsencrypt'] = True
            letsencrypt = True
            Log.debug(self, "Going to issue Let's Encrypt certificate")
            acmedata = dict(
                acme_domains, dns=False, acme_dns='dns_cf',
                dnsalias=False, acme_alias='', keylength='')
            if self.app.config.has_section('letsencrypt'):
                acmedata['keylength'] = self.app.config.get(
                    'letsencrypt', 'keylength')
            else:
                acmedata['keylength'] = 'ec-384'
            if pargs.dns:
                Log.debug(self, "DNS validation enabled")
                acmedata['dns'] = True
                if not pargs.dns == 'dns_cf':
                    Log.debug(self, "DNS API : {0}".format(pargs.dns))
                    acmedata['acme_dns'] = pargs.dns
            if pargs.dnsalias:
                Log.debug(self, "DNS Alias enabled")
                acmedata['dnsalias'] = True
                acmedata['acme_alias'] = pargs.dnsalias

            # detect subdomain and set subdomain variable
            if pargs.letsencrypt == "subdomain":
                Log.warn(
                    self, 'Flag --letsencrypt=subdomain is '
                    'deprecated and not required anymore.')
                acme_subdomain = True
                acme_wildcard = False
            elif pargs.letsencrypt == "wildcard":
                acme_wildcard = True
                acme_subdomain = False
                acmedata['dns'] = True
            else:
                if ((wo_domain_type == 'subdomain')):
                    Log.debug(self, "Domain type = {0}"
                              .format(wo_domain_type))
                    acme_subdomain = True
                else:
                    acme_subdomain = False
                    acme_wildcard = False

            if acme_subdomain is True:
                Log.info(self, "Certificate type : subdomain")
                acme_domains = acme_domains + ['{0}'.format(wo_domain)]
            elif acme_wildcard is True:
                Log.info(self, "Certificate type : wildcard")
                acme_domains = acme_domains + ['{0}'.format(wo_domain),
                                               '*.{0}'.format(wo_domain)]
            else:
                Log.info(self, "Certificate type : domain")
                acme_domains = acme_domains + ['{0}'.format(wo_domain),
                                               'www.{0}'.format(wo_domain)]

            if WOAcme.cert_check(self, wo_domain):
                SSL.archivedcertificatehandle(self, wo_domain, acme_domains)
            else:
                if acme_subdomain is True:
                    # check if a wildcard cert for the root domain exist
                    Log.debug(self, "checkWildcardExist on *.{0}"
                              .format(wo_root_domain))
                    if SSL.checkwildcardexist(self, wo_root_domain):
                        Log.info(self, "Using existing Wildcard SSL "
                                 "certificate from {0} to secure {1}"
                                 .format(wo_root_domain, wo_domain))
                        Log.debug(self, "symlink wildcard "
                                  "cert between {0} & {1}"
                                  .format(wo_domain, wo_root_domain))
                        # copy the cert from the root domain
                        copyWildcardCert(self, wo_domain, wo_root_domain)
                    else:
                        # check DNS records before issuing cert
                        if not acmedata['dns'] is True:
                            if not pargs.force:
                                if not WOAcme.check_dns(self, acme_domains):
                                    Log.error(self,
                                              "Aborting SSL "
                                              "certificate issuance")
                        Log.debug(self, "Setup Cert with acme.sh for {0}"
                                  .format(wo_domain))
                        if WOAcme.setupletsencrypt(
                                self, acme_domains, acmedata):
                            WOAcme.deploycert(self, wo_domain)
                else:
                    if not acmedata['dns'] is True:
                        if not pargs.force:
                            if not WOAcme.check_dns(self, acme_domains):
                                Log.error(self,
                                          "Aborting SSL certificate issuance")
                    if WOAcme.setupletsencrypt(
                            self, acme_domains, acmedata):
                        WOAcme.deploycert(self, wo_domain)

                if pargs.hsts:
                    SSL.setuphsts(self, wo_domain)

                SSL.httpsredirect(self, wo_domain, acme_domains, True)
                SSL.siteurlhttps(self, wo_domain)
                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
                Log.info(self, "Congratulations! Successfully Configured "
                         "SSL on https://{0}".format(wo_domain))

                # Add nginx conf folder into GIT
                WOGit.add(self, ["{0}/conf/nginx".format(wo_site_webroot)],
                          msg="Adding letsencrypts config of site: {0}"
                          .format(wo_domain))
                updateSiteInfo(self, wo_domain, ssl=letsencrypt)
