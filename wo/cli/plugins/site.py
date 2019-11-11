import glob
import json
import os
import subprocess

from cement.core.controller import CementBaseController, expose
from wo.cli.plugins.site_functions import *
from wo.cli.plugins.sitedb import (addNewSite, deleteSiteInfo, getAllsites,
                                   getSiteInfo, updateSiteInfo)
from wo.core.acme import WOAcme
from wo.core.domainvalidate import WODomain
from wo.core.fileutils import WOFileUtils
from wo.core.git import WOGit
from wo.core.logging import Log
from wo.core.nginxhashbucket import hashbucket
from wo.core.services import WOService
from wo.core.shellexec import WOShellExec
from wo.core.sslutils import SSL
from wo.core.variables import WOVar


def wo_site_hook(app):
    from wo.core.database import init_db
    import wo.cli.plugins.models
    init_db(app)


class WOSiteController(CementBaseController):
    class Meta:
        label = 'site'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = ('Performs website specific operations')
        arguments = [
            (['site_name'],
                dict(help='Website name', nargs='?')),
        ]
        usage = "wo site (command) <site_name> [options]"

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @expose(help="Enable site example.com")
    def enable(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'could not input site name')

        pargs.site_name = pargs.site_name.strip()
        # validate domain name
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)

        # check if site exists
        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))
        if os.path.isfile('/etc/nginx/sites-available/{0}'
                          .format(wo_domain)):
            Log.info(self, "Enable domain {0:10} \t".format(wo_domain), end='')
            WOFileUtils.create_symlink(self,
                                       ['/etc/nginx/sites-available/{0}'
                                        .format(wo_domain),
                                        '/etc/nginx/sites-enabled/{0}'
                                        .format(wo_domain)])
            WOGit.add(self, ["/etc/nginx"],
                      msg="Enabled {0} "
                      .format(wo_domain))
            updateSiteInfo(self, wo_domain, enabled=True)
            Log.info(self, "[" + Log.ENDC + "OK" + Log.OKBLUE + "]")
            if not WOService.reload_service(self, 'nginx'):
                Log.error(self, "service nginx reload failed. "
                          "check issues with `nginx -t` command")
        else:
            Log.error(self, 'nginx configuration file does not exist')

    @expose(help="Disable site example.com")
    def disable(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())

            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'could not input site name')
        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        # check if site exists
        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))

        if os.path.isfile('/etc/nginx/sites-available/{0}'
                          .format(wo_domain)):
            Log.info(self, "Disable domain {0:10} \t"
                     .format(wo_domain), end='')
            if not os.path.isfile('/etc/nginx/sites-enabled/{0}'
                                  .format(wo_domain)):
                Log.debug(self, "Site {0} already disabled".format(wo_domain))
                Log.info(self, "[" + Log.FAIL + "Failed" + Log.OKBLUE + "]")
            else:
                WOFileUtils.remove_symlink(self,
                                           '/etc/nginx/sites-enabled/{0}'
                                           .format(wo_domain))
                WOGit.add(self, ["/etc/nginx"],
                          msg="Disabled {0} "
                          .format(wo_domain))
                updateSiteInfo(self, wo_domain, enabled=False)
                Log.info(self, "[" + Log.ENDC + "OK" + Log.OKBLUE + "]")
                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
        else:
            Log.error(self, "nginx configuration file does not exist")

    @expose(help="Get example.com information")
    def info(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'could not input site name')
        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        (wo_domain_type, wo_root_domain) = WODomain.getlevel(
            self, wo_domain)
        wo_db_name = ''
        wo_db_user = ''
        wo_db_pass = ''

        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))
        if os.path.isfile('/etc/nginx/sites-available/{0}'
                          .format(wo_domain)):
            siteinfo = getSiteInfo(self, wo_domain)
            sitetype = siteinfo.site_type
            cachetype = siteinfo.cache_type
            wo_site_webroot = siteinfo.site_path
            access_log = (wo_site_webroot + '/logs/access.log')
            error_log = (wo_site_webroot + '/logs/error.log')
            wo_db_name = siteinfo.db_name
            wo_db_user = siteinfo.db_user
            wo_db_pass = siteinfo.db_password
            wo_db_host = siteinfo.db_host

            php_version = siteinfo.php_version

            ssl = ("enabled" if siteinfo.is_ssl else "disabled")
            if (ssl == "enabled"):
                sslprovider = "Lets Encrypt"
                if os.path.islink("{0}/conf/nginx/ssl.conf"
                                  .format(wo_site_webroot)):
                    sslexpiry = str(
                        SSL.getexpirationdays(self, wo_root_domain))
                else:
                    sslexpiry = str(SSL.getexpirationdays(self, wo_domain))
            else:
                sslprovider = ''
                sslexpiry = ''
            data = dict(domain=wo_domain, webroot=wo_site_webroot,
                        accesslog=access_log, errorlog=error_log,
                        dbname=wo_db_name, dbuser=wo_db_user,
                        php_version=php_version,
                        dbpass=wo_db_pass,
                        ssl=ssl, sslprovider=sslprovider, sslexpiry=sslexpiry,
                        type=sitetype + " " + cachetype + " ({0})"
                        .format("enabled" if siteinfo.is_enabled else
                                "disabled"))
            self.app.render((data), 'siteinfo.mustache')
        else:
            Log.error(self, "nginx configuration file does not exist")

    @expose(help="Monitor example.com logs")
    def log(self):
        pargs = self.app.pargs
        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        wo_site_webroot = getSiteInfo(self, wo_domain).site_path

        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))
        logfiles = glob.glob(wo_site_webroot + '/logs/*.log')
        if logfiles:
            logwatch(self, logfiles)

    @expose(help="Display Nginx configuration of example.com")
    def show(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'could not input site name')
        # TODO Write code for wo site edit command here
        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)

        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))

        if os.path.isfile('/etc/nginx/sites-available/{0}'
                          .format(wo_domain)):
            Log.info(self, "Display NGINX configuration for {0}"
                     .format(wo_domain))
            f = open('/etc/nginx/sites-available/{0}'.format(wo_domain),
                     encoding='utf-8', mode='r')
            text = f.read()
            Log.info(self, Log.ENDC + text)
            f.close()
        else:
            Log.error(self, "nginx configuration file does not exists")

    @expose(help="Change directory to site webroot")
    def cd(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'Unable to read input, please try again')

        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)

        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))

        wo_site_webroot = getSiteInfo(self, wo_domain).site_path
        WOFileUtils.chdir(self, wo_site_webroot)

        try:
            subprocess.call(['/bin/bash'])
        except OSError as e:
            Log.debug(self, "{0}{1}".format(e.errno, e.strerror))
            Log.error(self, "unable to change directory")


class WOSiteEditController(CementBaseController):
    class Meta:
        label = 'edit'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = ('Edit Nginx configuration of site')
        arguments = [
            (['site_name'],
                dict(help='domain name for the site',
                     nargs='?')),
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'Unable to read input, Please try again')

        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))

        wo_site_webroot = WOVar.wo_webroot + wo_domain

        if os.path.isfile('/etc/nginx/sites-available/{0}'
                          .format(wo_domain)):
            try:
                WOShellExec.invoke_editor(self, '/etc/nginx/sites-availa'
                                          'ble/{0}'.format(wo_domain))
            except CommandExecutionError as e:
                Log.debug(self, str(e))
                Log.error(self, "Failed invoke editor")
            if (WOGit.checkfilestatus(self, "/etc/nginx",
                                      '/etc/nginx/sites-available/{0}'
                                      .format(wo_domain))):
                WOGit.add(self, ["/etc/nginx"], msg="Edit website: {0}"
                          .format(wo_domain))
                # Reload NGINX
                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
        else:
            Log.error(self, "nginx configuration file does not exists")


class WOSiteCreateController(CementBaseController):
    class Meta:
        label = 'create'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = ('this commands set up configuration and installs '
                       'required files as options are provided')
        arguments = [
            (['site_name'],
                dict(help='domain name for the site to be created.',
                     nargs='?')),
            (['--html'],
                dict(help="create html site", action='store_true')),
            (['--php'],
             dict(help="create php 7.2 site", action='store_true')),
            (['--php72'],
                dict(help="create php 7.2 site", action='store_true')),
            (['--php73'],
                dict(help="create php 7.3 site", action='store_true')),
            (['--mysql'],
                dict(help="create mysql site", action='store_true')),
            (['--wp'],
                dict(help="create WordPress single site",
                     action='store_true')),
            (['--wpsubdir'],
                dict(help="create WordPress multisite with subdirectory setup",
                     action='store_true')),
            (['--wpsubdomain'],
                dict(help="create WordPress multisite with subdomain setup",
                     action='store_true')),
            (['--wpfc'],
                dict(help="create WordPress single/multi site with "
                     "Nginx fastcgi_cache",
                     action='store_true')),
            (['--wpsc'],
                dict(help="create WordPress single/multi site with wpsc cache",
                     action='store_true')),
            (['--wprocket'],
             dict(help="create WordPress single/multi site with WP-Rocket",
                  action='store_true')),
            (['--wpce'],
             dict(help="create WordPress single/multi site with Cache-Enabler",
                  action='store_true')),
            (['--wpredis'],
                dict(help="create WordPress single/multi site "
                     "with redis cache",
                     action='store_true')),
            (['-le', '--letsencrypt'],
                dict(help="configure letsencrypt ssl for the site",
                     action='store' or 'store_const',
                     choices=('on', 'subdomain', 'wildcard'),
                     const='on', nargs='?')),
            (['--force'],
                dict(help="force Let's Encrypt certificate issuance",
                     action='store_true')),
            (['--dns'],
                dict(help="choose dns provider api for letsencrypt",
                     action='store' or 'store_const',
                     const='dns_cf', nargs='?')),
            (['--dnsalias'],
                dict(help="set domain used for acme dns alias validation",
                     action='store', nargs='?')),
            (['--hsts'],
                dict(help="enable HSTS for site secured with letsencrypt",
                     action='store_true')),
            (['--ngxblocker'],
                dict(help="enable HSTS for site secured with letsencrypt",
                     action='store_true')),
            (['--user'],
                dict(help="provide user for WordPress site")),
            (['--email'],
                dict(help="provide email address for WordPress site")),
            (['--pass'],
                dict(help="provide password for WordPress user",
                     dest='wppass')),
            (['--proxy'],
                dict(help="create proxy for site", nargs='+')),
            (['--vhostonly'], dict(help="only create vhost and database "
                                   "without installing WordPress",
                                   action='store_true')),
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if pargs.php72:
            pargs.php = True
        # self.app.render((data), 'default.mustache')
        # Check domain name validation
        data = dict()
        host, port = None, None
        try:
            stype, cache = detSitePar(vars(pargs))
        except RuntimeError as e:
            Log.debug(self, str(e))
            Log.error(self, "Please provide valid options to creating site")

        if stype is None and pargs.proxy:
            stype, cache = 'proxy', ''
            proxyinfo = pargs.proxy[0].strip()
            if not proxyinfo:
                Log.error(self, "Please provide proxy server host information")
            proxyinfo = proxyinfo.split(':')
            host = proxyinfo[0].strip()
            port = '80' if len(proxyinfo) < 2 else proxyinfo[1].strip()
        elif stype is None and not pargs.proxy:
            stype, cache = 'html', 'basic'
        elif stype and pargs.proxy:
            Log.error(self, "proxy should not be used with other site types")

        if not pargs.site_name:
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

        if check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} already exists".format(wo_domain))
        elif os.path.isfile('/etc/nginx/sites-available/{0}'
                            .format(wo_domain)):
            Log.error(self, "Nginx configuration /etc/nginx/sites-available/"
                      "{0} already exists".format(wo_domain))

        if stype == 'proxy':
            data = dict(site_name=wo_domain, www_domain=wo_www_domain,
                        static=True, basic=False, php73=False, wp=False,
                        wpfc=False, wpsc=False, wprocket=False, wpce=False,
                        multisite=False,
                        wpsubdir=False, webroot=wo_site_webroot)
            data['proxy'] = True
            data['host'] = host
            data['port'] = port
            data['basic'] = True

        if pargs.php73:
            data = dict(site_name=wo_domain, www_domain=wo_www_domain,
                        static=False, basic=False, php73=True, wp=False,
                        wpfc=False, wpsc=False, wprocket=False, wpce=False,
                        multisite=False,
                        wpsubdir=False, webroot=wo_site_webroot)
            data['basic'] = True

        if stype in ['html', 'php']:
            data = dict(site_name=wo_domain, www_domain=wo_www_domain,
                        static=True, basic=False, php73=False, wp=False,
                        wpfc=False, wpsc=False, wprocket=False, wpce=False,
                        multisite=False,
                        wpsubdir=False, webroot=wo_site_webroot)

            if stype == 'php':
                data['static'] = False
                data['basic'] = True

        elif stype in ['mysql', 'wp', 'wpsubdir', 'wpsubdomain']:

            data = dict(site_name=wo_domain, www_domain=wo_www_domain,
                        static=False, basic=True, wp=False, wpfc=False,
                        wpsc=False, wpredis=False, wprocket=False, wpce=False,
                        multisite=False,
                        wpsubdir=False, webroot=wo_site_webroot,
                        wo_db_name='', wo_db_user='', wo_db_pass='',
                        wo_db_host='')

            if stype in ['wp', 'wpsubdir', 'wpsubdomain']:
                data['wp'] = True
                data['basic'] = False
                data[cache] = True
                data['wp-user'] = pargs.user
                data['wp-email'] = pargs.email
                data['wp-pass'] = pargs.wppass
                if stype in ['wpsubdir', 'wpsubdomain']:
                    data['multisite'] = True
                    if stype == 'wpsubdir':
                        data['wpsubdir'] = True
        else:
            pass

        if data and pargs.php73:
            data['php73'] = True
        elif data:
            data['php73'] = False

        if ((not pargs.wpfc) and (not pargs.wpsc) and
            (not pargs.wprocket) and
            (not pargs.wpce) and
                (not pargs.wpredis)):
            data['basic'] = True

        if (cache == 'wpredis'):
            cache = 'wpredis'
            data['wpredis'] = True
            data['basic'] = False
            pargs.wpredis = True

        # Check rerequired packages are installed or not
        wo_auth = site_package_check(self, stype)

        try:
            pre_run_checks(self)
        except SiteError as e:
            Log.debug(self, str(e))
            Log.error(self, "NGINX configuration check failed.")

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

            if data['php73']:
                php_version = "7.3"
                php73 = 1
            else:
                php_version = "7.2"
                php73 = 0

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
            if WOAcme.cert_check(self, wo_domain):
                archivedCertificateHandle(self, wo_domain)
            else:
                Log.debug(self, "Going to issue Let's Encrypt certificate")
                acmedata = dict(acme_domains, dns=False, acme_dns='dns_cf',
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

                httpsRedirect(self, wo_domain, True, acme_wildcard)
                SSL.siteurlhttps(self, wo_domain)
                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
                Log.info(self, "Congratulations! Successfully Configured "
                         "SSl for Site "
                         " https://{0}".format(wo_domain))

                # Add nginx conf folder into GIT
                WOGit.add(self, ["{0}/conf/nginx".format(wo_site_webroot)],
                          msg="Adding letsencrypts config of site: {0}"
                          .format(wo_domain))
                updateSiteInfo(self, wo_domain, ssl=letsencrypt)


class WOSiteUpdateController(CementBaseController):
    class Meta:
        label = 'update'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = ('This command updates websites configuration to '
                       'another as per the options are provided')
        arguments = [
            (['site_name'],
                dict(help='domain name for the site to be updated',
                     nargs='?')),
            (['--password'],
                dict(help="update to password for wordpress site user",
                     action='store_true')),
            (['--html'],
                dict(help="update to html site", action='store_true')),
            (['--php72'],
                dict(help="update to php site", action='store_true')),
            (['--php'],
             dict(help="update to php site", action='store_true')),
            (['--php73'],
                dict(help="update to php73 site",
                     action='store' or 'store_const',
                     choices=('on', 'off'), const='on', nargs='?')),
            (['--mysql'],
                dict(help="update to mysql site", action='store_true')),
            (['--wp'],
                dict(help="update to wordpress single site",
                     action='store_true')),
            (['--wpsubdir'],
                dict(help="update to wpsubdir site", action='store_true')),
            (['--wpsubdomain'],
                dict(help="update to  wpsubdomain site", action='store_true')),
            (['--wpfc'],
                dict(help="update to wpfc cache", action='store_true')),
            (['--wpsc'],
                dict(help="update to wpsc cache", action='store_true')),
            (['--wprocket'],
                dict(help="update to WP-Rocket cache", action='store_true')),
            (['--wpce'],
                dict(help="update to Cache-Enabler cache",
                     action='store_true')),
            (['--wpredis'],
                dict(help="update to redis cache", action='store_true')),
            (['-le', '--letsencrypt'],
                dict(help="configure letsencrypt ssl for the site",
                     action='store' or 'store_const',
                     choices=('on', 'off', 'renew', 'subdomain',
                              'wildcard', 'clean', 'purge'),
                     const='on', nargs='?')),
            (['--force'],
                dict(help="force LetsEncrypt certificate issuance/renewal",
                     action='store_true')),
            (['--dns'],
                dict(help="choose dns provider api for letsencrypt",
                     action='store' or 'store_const',
                     const='dns_cf', nargs='?')),
            (['--dnsalias'],
                dict(help="set domain used for acme dns alias validation",
                     action='store', nargs='?')),
            (['--hsts'],
                dict(help="configure hsts for the site",
                     action='store' or 'store_const',
                     choices=('on', 'off'),
                     const='on', nargs='?')),
            (['--ngxblocker'],
                dict(help="enable Ultimate Nginx bad bot blocker",
                     action='store' or 'store_const',
                     choices=('on', 'off'),
                     const='on', nargs='?')),
            (['--proxy'],
                dict(help="update to proxy site", nargs='+')),
            (['--all'],
                dict(help="update all sites", action='store_true')),
        ]

    @expose(help="Update site type or cache")
    def default(self):
        pargs = self.app.pargs

        if pargs.php72:
            pargs.php = True

        if pargs.all:
            if pargs.site_name:
                Log.error(self, "`--all` option cannot be used with site name"
                          " provided")
            if pargs.html:
                Log.error(self, "No site can be updated to html")

            if not (pargs.php or pargs.php73 or
                    pargs.mysql or pargs.wp or pargs.wpsubdir or
                    pargs.wpsubdomain or pargs.wpfc or pargs.wpsc or
                    pargs.wprocket or pargs.wpce or
                    pargs.wpredis or pargs.letsencrypt or pargs.hsts or
                    pargs.dns or pargs.force):
                Log.error(self, "Please provide options to update sites.")

        if pargs.all:
            if pargs.site_name:
                Log.error(self, "`--all` option cannot be used with site name"
                          " provided")

            sites = getAllsites(self)
            if not sites:
                pass
            else:
                for site in sites:
                    pargs.site_name = site.sitename
                    Log.info(self, Log.ENDC + Log.BOLD + "Updating site {0},"
                             " please wait..."
                             .format(pargs.site_name))
                    self.doupdatesite(pargs)
                    print("\n")
        else:
            self.doupdatesite(pargs)

    def doupdatesite(self, pargs):
        pargs = self.app.pargs
        letsencrypt = False
        php73 = None

        data = dict()
        try:
            stype, cache = detSitePar(vars(pargs))
        except RuntimeError as e:
            Log.debug(self, str(e))
            Log.error(self, "Please provide valid options combination for"
                      " site update")

        if stype is None and pargs.proxy:
            stype, cache = 'proxy', ''
            proxyinfo = pargs.proxy[0].strip()
            if not proxyinfo:
                Log.error(self, "Please provide proxy server host information")
            proxyinfo = proxyinfo.split(':')
            host = proxyinfo[0].strip()
            port = '80' if len(proxyinfo) < 2 else proxyinfo[1].strip()
        elif stype is None and not (pargs.proxy or pargs.letsencrypt):
            stype, cache = 'html', 'basic'
        elif stype and pargs.proxy:
            Log.error(self, "--proxy can not be used with other site types")

        if not pargs.site_name:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ').strip())
            except IOError:
                Log.error(self, 'Unable to input site name, Please try again!')

        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        (wo_domain_type, wo_root_domain) = WODomain.getlevel(
            self, wo_domain)
        wo_site_webroot = WOVar.wo_webroot + wo_domain
        check_site = getSiteInfo(self, wo_domain)

        if check_site is None:
            Log.error(self, " Site {0} does not exist.".format(wo_domain))
        else:
            oldsitetype = check_site.site_type
            oldcachetype = check_site.cache_type
            check_ssl = check_site.is_ssl
            check_php_version = check_site.php_version

            old_php73 = bool(check_php_version == "7.3")

        if (pargs.password and not (pargs.html or
                                    pargs.php or pargs.php73 or pargs.mysql or
                                    pargs.wp or pargs.wpfc or pargs.wpsc or
                                    pargs.wprocket or pargs.wpce or
                                    pargs.wpsubdir or pargs.wpsubdomain or
                                    pargs.hsts or pargs.ngxblocker)):
            try:
                updatewpuserpassword(self, wo_domain, wo_site_webroot)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, "\nPassword Unchanged.")
            return 0

        if (pargs.hsts and not (pargs.html or
                                pargs.php or pargs.php73 or pargs.mysql or
                                pargs.wp or pargs.wpfc or pargs.wpsc or
                                pargs.wprocket or pargs.wpce or
                                pargs.wpsubdir or pargs.wpsubdomain or
                                pargs.ngxblocker)):
            if pargs.hsts == "on":
                try:
                    SSL.setuphsts(self, wo_domain)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, "\nHSTS not enabled.")
            elif pargs.hsts == "off":
                if os.path.isfile(
                    '/var/www/{0}/conf/nginx/hsts.conf'
                        .format(wo_domain)):
                    WOFileUtils.mvfile(self, '/var/www/{0}/conf/'
                                       'nginx/hsts.conf'
                                       .format(wo_domain),
                                       '/var/www/{0}/conf/'
                                       'nginx/hsts.conf.disabled'
                                       .format(wo_domain))
                else:
                    Log.error(self, "HSTS isn't enabled")
                    # Service Nginx Reload
            if not WOService.reload_service(self, 'nginx'):
                Log.error(self, "service nginx reload failed. "
                          "check issues with `nginx -t` command")
            return 0

        if (pargs.ngxblocker and not (pargs.html or
                                      pargs.php or pargs.php73 or
                                      pargs.mysql or
                                      pargs.wp or pargs.wpfc or pargs.wpsc or
                                      pargs.wprocket or pargs.wpce or
                                      pargs.wpsubdir or pargs.wpsubdomain or
                                      pargs.hsts)):
            if pargs.ngxblocker == "on":
                if os.path.isdir('/etc/nginx/bots.d'):
                    try:
                        setupngxblocker(self, wo_domain)
                    except SiteError as e:
                        Log.debug(self, str(e))
                        Log.info(self, "\nngxblocker not enabled.")
                else:
                    Log.error(self, 'ngxblocker stack is not installed')
            elif pargs.ngxblocker == "off":
                try:
                    setupngxblocker(self, wo_domain, False)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, "\nngxblocker not enabled.")

            # Service Nginx Reload
            if not WOService.reload_service(self, 'nginx'):
                Log.error(self, "service nginx reload failed. "
                          "check issues with `nginx -t` command")
            return 0
        #
        if (pargs.letsencrypt == 'renew' and
            not (pargs.html or
                 pargs.php or pargs.php73 or pargs.mysql or
                 pargs.wp or pargs.wpfc or pargs.wpsc or
                 pargs.wprocket or pargs.wpce or
                 pargs.wpsubdir or pargs.wpsubdomain or
                 pargs.ngxblocker or pargs.hsts)):

            if WOAcme.cert_check(self, wo_domain):
                if not pargs.force:
                    if (SSL.getexpirationdays(self, wo_domain) > 30):
                        Log.error(
                            self, "Your cert will expire in more "
                            "than 30 days ( " +
                                  str(SSL.getexpirationdays(self, wo_domain)) +
                                  " days).\nAdd \'--force\' to force to renew")
                Log.wait(self, "Renewing SSL certificate")
                if WOAcme.renew(self, wo_domain):
                    Log.valide(self, "Renewing SSL certificate")
            else:
                Log.error(self, "Certificate doesn't exist")
            return 0

        if ((stype == 'php' and
             oldsitetype not in ['html', 'proxy', 'php73']) or
            (stype == 'mysql' and oldsitetype not in ['html', 'php',
                                                      'proxy', 'php73']) or
            (stype == 'wp' and oldsitetype not in ['html', 'php', 'mysql',
                                                   'proxy', 'wp', 'php73']) or
            (stype == 'wpsubdir' and oldsitetype in ['wpsubdomain']) or
            (stype == 'wpsubdomain' and oldsitetype in ['wpsubdir']) or
            (stype == oldsitetype and cache == oldcachetype) and not
                pargs.php73):
            Log.info(self, Log.FAIL + "can not update {0} {1} to {2} {3}".
                     format(oldsitetype, oldcachetype, stype, cache))
            return 1

        if stype == 'proxy':
            data['site_name'] = wo_domain
            data['www_domain'] = wo_www_domain
            data['proxy'] = True
            data['host'] = host
            data['port'] = port
            data['webroot'] = wo_site_webroot
            data['currsitetype'] = oldsitetype
            data['currcachetype'] = oldcachetype

        if stype == 'php':
            data = dict(
                site_name=wo_domain, www_domain=wo_www_domain,
                static=False, basic=True, wp=False, wpfc=False,
                wpsc=False, wpredis=False, wprocket=False, wpce=False,
                multisite=False, wpsubdir=False, webroot=wo_site_webroot,
                currsitetype=oldsitetype, currcachetype=oldcachetype)

        elif stype in ['mysql', 'wp', 'wpsubdir', 'wpsubdomain']:

            data = dict(
                site_name=wo_domain, www_domain=wo_www_domain,
                static=False, basic=True, wp=False, wpfc=False,
                wpsc=False, wpredis=False, wprocket=False, wpce=False,
                multisite=False, wpsubdir=False, webroot=wo_site_webroot,
                wo_db_name='', wo_db_user='', wo_db_pass='',
                wo_db_host='',
                currsitetype=oldsitetype, currcachetype=oldcachetype)

            if stype in ['wp', 'wpsubdir', 'wpsubdomain']:
                data['wp'] = True
                data['basic'] = False
                data[cache] = True
                if stype in ['wpsubdir', 'wpsubdomain']:
                    data['multisite'] = True
                    if stype == 'wpsubdir':
                        data['wpsubdir'] = True

        if pargs.php73:
            if not data:
                data = dict(
                    site_name=wo_domain,
                    www_domain=wo_www_domain,
                    currsitetype=oldsitetype,
                    currcachetype=oldcachetype,
                    webroot=wo_site_webroot)
                stype = oldsitetype
                cache = oldcachetype
                if oldsitetype == 'html' or oldsitetype == 'proxy':
                    data['static'] = False
                    data['wp'] = False
                    data['multisite'] = False
                    data['wpsubdir'] = False
                elif oldsitetype == 'php' or oldsitetype == 'mysql':
                    data['static'] = False
                    data['wp'] = False
                    data['multisite'] = False
                    data['wpsubdir'] = False
                elif oldsitetype == 'wp':
                    data['static'] = False
                    data['wp'] = True
                    data['multisite'] = False
                    data['wpsubdir'] = False
                elif oldsitetype == 'wpsubdir':
                    data['static'] = False
                    data['wp'] = True
                    data['multisite'] = True
                    data['wpsubdir'] = True
                elif oldsitetype == 'wpsubdomain':
                    data['static'] = False
                    data['wp'] = True
                    data['multisite'] = True
                    data['wpsubdir'] = False

                if oldcachetype == 'basic':
                    data['basic'] = True
                    data['wpfc'] = False
                    data['wpsc'] = False
                    data['wpredis'] = False
                    data['wprocket'] = False
                    data['wpce'] = False
                elif oldcachetype == 'wpfc':
                    data['basic'] = False
                    data['wpfc'] = True
                    data['wpsc'] = False
                    data['wpredis'] = False
                    data['wprocket'] = False
                    data['wpce'] = False
                elif oldcachetype == 'wpsc':
                    data['basic'] = False
                    data['wpfc'] = False
                    data['wpsc'] = True
                    data['wpredis'] = False
                    data['wprocket'] = False
                    data['wpce'] = False
                elif oldcachetype == 'wpredis':
                    data['basic'] = False
                    data['wpfc'] = False
                    data['wpsc'] = False
                    data['wpredis'] = True
                    data['wprocket'] = False
                    data['wpce'] = False
                elif oldcachetype == 'wprocket':
                    data['basic'] = False
                    data['wpfc'] = False
                    data['wpsc'] = False
                    data['wpredis'] = False
                    data['wprocket'] = True
                    data['wpce'] = False
                elif oldcachetype == 'wpce':
                    data['basic'] = False
                    data['wpfc'] = False
                    data['wpsc'] = False
                    data['wpredis'] = False
                    data['wprocket'] = False
                    data['wpce'] = True

            if pargs.php73 == 'on':
                data['php73'] = True
                php73 = True
                check_php_version = '7.3'
            elif pargs.php73 == 'off':
                data['php73'] = False
                php73 = False
                check_php_version = '7.2'

        if pargs.php73:
            if php73 is old_php73:
                if php73 is False:
                    Log.info(self, "PHP 7.3 is already disabled for given "
                             "site")
                elif php73 is True:
                    Log.info(self, "PHP 7.3 is already enabled for given "
                             "site")
                pargs.php73 = False

        if pargs.letsencrypt:
            acme_domains = []
            acmedata = dict(acme_domains, dns=False, acme_dns='dns_cf',
                            dnsalias=False, acme_alias='', keylength='')
            acmedata['keylength'] = self.app.config.get('letsencrypt',
                                                        'keylength')
            if pargs.letsencrypt == 'on':
                data['letsencrypt'] = True
                letsencrypt = True
                acme_subdomain = bool(wo_domain_type == 'subdomain')
                acme_wildcard = False
            elif pargs.letsencrypt == 'subdomain':
                data['letsencrypt'] = True
                letsencrypt = True
                acme_subdomain = True
                acme_wildcard = False
            elif pargs.letsencrypt == 'wildcard':
                data['letsencrypt'] = True
                letsencrypt = True
                acme_wildcard = True
                acme_subdomain = False
                acmedata['dns'] = True
            elif pargs.letsencrypt == 'off':
                data['letsencrypt'] = False
                letsencrypt = False
                acme_subdomain = False
                acme_wildcard = False
            elif pargs.letsencrypt == 'clean':
                data['letsencrypt'] = False
                letsencrypt = False
                acme_subdomain = False
                acme_wildcard = False
            elif pargs.letsencrypt == 'purge':
                data['letsencrypt'] = False
                letsencrypt = False
                acme_subdomain = False
                acme_wildcard = False
            else:
                data['letsencrypt'] = False
                letsencrypt = False
                acme_subdomain = False
                acme_wildcard = False

            if not (acme_subdomain is True):
                if letsencrypt is check_ssl:
                    if letsencrypt is False:
                        Log.error(self, "SSL is not configured for given "
                                  "site")
                    elif letsencrypt is True:
                        Log.error(self, "SSL is already configured for given "
                                  "site")
                    pargs.letsencrypt = False

        if pargs.all and pargs.letsencrypt == "off":
            if letsencrypt is check_ssl:
                if letsencrypt is False:
                    Log.error(self, "HTTPS is not configured for given "
                              "site", False)
                    return 0

        if data and (not pargs.php73):
            data['php73'] = bool(old_php73 is True)
            php73 = bool(old_php73 is True)

        data['php73'] = bool(pargs.php73 == "on")
        php73 = bool(pargs.php73 == "on")

        if pargs.wpredis and data['currcachetype'] != 'wpredis':
            data['wpredis'] = True
            data['basic'] = False
            cache = 'wpredis'

        if pargs.wprocket and data['currcachetype'] != 'wprocket':
            data['wprocket'] = True
            data['basic'] = False
            cache = 'wprocket'

        if pargs.wpce and data['currcachetype'] != 'wpce':
            data['wpce'] = True
            data['basic'] = False
            cache = 'wpce'

        if (php73 is old_php73) and (stype == oldsitetype and
                                     cache == oldcachetype):
            return 1

        if pargs.hsts:
            data['hsts'] = bool(pargs.hsts == "on")

        if pargs.ngxblocker:
            ngxblocker = bool(pargs.ngxblocker == 'on')

        if not data:
            Log.error(self, "Cannot update {0}, Invalid Options"
                      .format(wo_domain))

        wo_auth = site_package_check(self, stype)
        data['wo_db_name'] = check_site.db_name
        data['wo_db_user'] = check_site.db_user
        data['wo_db_pass'] = check_site.db_password
        data['wo_db_host'] = check_site.db_host

        if not (pargs.letsencrypt or pargs.hsts or pargs.ngxblocker):
            try:
                pre_run_checks(self)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.error(self, "NGINX configuration check failed.")

            try:
                sitebackup(self, data)
            except Exception as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

            # setup NGINX configuration, and webroot
            try:
                setupdomain(self, data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details:"
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        if 'proxy' in data.keys() and data['proxy']:
            updateSiteInfo(self, wo_domain, stype=stype, cache=cache,
                           ssl=(bool(check_site.is_ssl)))
            Log.info(self, "Successfully updated site"
                     " http://{0}".format(wo_domain))
            return 0

        if pargs.letsencrypt:
            if data['letsencrypt'] is True:
                if WOAcme.cert_check(self, wo_domain):
                    archivedCertificateHandle(self, wo_domain)
                else:
                    # DNS API configuration
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
                    # Set list of domains to secure
                    if acme_subdomain is True:
                        Log.info(self, "Certificate type : subdomain")
                        acme_domains = acme_domains + ['{0}'.format(wo_domain)]
                    elif acme_wildcard is True:
                        Log.info(self, "Certificate type : wildcard")
                        acme_domains = \
                            acme_domains + ['{0}'.format(wo_domain),
                                            '*.{0}'.format(wo_domain)]
                    else:
                        Log.info(self, "Certificate type : domain")
                        acme_domains = \
                            acme_domains + ['{0}'.format(wo_domain),
                                            'www.{0}'.format(wo_domain)]

                    if not os.path.isfile("{0}/conf/nginx/ssl.conf.disabled"):
                        if acme_subdomain:
                            Log.debug(self, "checkWildcardExist on *.{0}"
                                      .format(wo_root_domain))
                            if SSL.checkwildcardexist(self, wo_root_domain):
                                Log.info(
                                    self, "Using existing Wildcard SSL "
                                    "certificate from {0} to secure {1}"
                                    .format(wo_root_domain, wo_domain))
                                Log.debug(
                                    self, "symlink wildcard "
                                    "cert between {0} & {1}"
                                    .format(wo_domain, wo_root_domain))
                                # copy the cert from the root domain
                                copyWildcardCert(self, wo_domain,
                                                 wo_root_domain)
                            else:
                                # check DNS records before issuing cert
                                if not acmedata['dns'] is True:
                                    if not pargs.force:
                                        if not WOAcme.check_dns(self,
                                                                acme_domains):
                                            Log.error(
                                                self,
                                                "Aborting SSL certificate "
                                                "issuance")
                            Log.debug(self, "Setup Cert with acme.sh for {0}"
                                      .format(wo_domain))
                            if WOAcme.setupletsencrypt(
                                    self, acme_domains, acmedata):
                                WOAcme.deploycert(self, wo_domain)
                            else:
                                Log.error(self, "Unable to issue certificate")
                        else:
                            # check DNS records before issuing cert
                            if not acmedata['dns'] is True:
                                if not pargs.force:
                                    if not WOAcme.check_dns(self,
                                                            acme_domains):
                                        Log.error(
                                            self,
                                            "Aborting SSL "
                                            "certificate issuance")
                            if WOAcme.setupletsencrypt(
                                    self, acme_domains, acmedata):
                                WOAcme.deploycert(self, wo_domain)
                            else:
                                Log.error(self, "Unable to issue certificate")
                    else:
                        WOFileUtils.mvfile(
                            self, "{0}/conf/nginx/ssl.conf.disabled"
                            .format(wo_site_webroot),
                            '{0}/conf/nginx/ssl.conf'
                            .format(wo_site_webroot))
                        WOFileUtils.mvfile(
                            self, "/etc/nginx/conf.d/"
                            "force-ssl-{0}.conf.disabled"
                            .format(wo_domain),
                            '/etc/nginx/conf.d/force-ssl-{0}.conf'
                            .format(wo_domain))

                    httpsRedirect(self, wo_domain, True, acme_wildcard)
                    SSL.siteurlhttps(self, wo_domain)

                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
                Log.info(self, "Congratulations! Successfully "
                         "Configured SSL for Site "
                         " https://{0}".format(wo_domain))
                if (SSL.getexpirationdays(self, wo_domain) > 0):
                    Log.info(self, "Your cert will expire within " +
                             str(SSL.getexpirationdays(self, wo_domain)) +
                             " days.")
                else:
                    Log.warn(
                        self, "Your cert already EXPIRED ! "
                        ".PLEASE renew soon . ")

            elif data['letsencrypt'] is False:
                if pargs.letsencrypt == "off":
                    if os.path.islink("{0}/conf/nginx/ssl.conf"
                                      .format(wo_site_webroot)):
                        WOFileUtils.remove_symlink(self,
                                                   "{0}/conf/nginx/ssl.conf"
                                                   .format(wo_site_webroot))
                    elif os.path.isfile("{0}/conf/nginx/ssl.conf"
                                        .format(wo_site_webroot)):
                        Log.info(self, 'Setting Nginx configuration')
                        WOFileUtils.mvfile(self, "{0}/conf/nginx/ssl.conf"
                                           .format(wo_site_webroot),
                                           '{0}/conf/nginx/ssl.conf.disabled'
                                           .format(wo_site_webroot))
                        httpsRedirect(self, wo_domain, False)
                        if os.path.isfile("{0}/conf/nginx/hsts.conf"
                                          .format(wo_site_webroot)):
                            WOFileUtils.mvfile(self, "{0}/conf/nginx/hsts.conf"
                                               .format(wo_site_webroot),
                                               '{0}/conf/nginx/'
                                               'hsts.conf.disabled'
                                               .format(wo_site_webroot))
                        # find all broken symlinks
                        sympath = "/var/www"
                        WOFileUtils.findBrokenSymlink(self, sympath)

                elif (pargs.letsencrypt == "clean" or
                      pargs.letsencrypt == "purge"):
                    WOAcme.removeconf(self, wo_domain)
                    # find all broken symlinks
                    sympath = "/var/www"
                    WOFileUtils.findBrokenSymlink(self, sympath)
                if not WOService.reload_service(self, 'nginx'):
                    Log.error(self, "service nginx reload failed. "
                              "check issues with `nginx -t` command")
                    # Log.info(self,"Removing Cron Job set for cert
                    # auto-renewal") WOCron.remove_cron(self,'wo site
                    # update {0} --le=renew --min_expiry_limit 30
                    # 2> \/dev\/null'.format(wo_domain))
                    Log.info(self, "Successfully Disabled SSl for Site "
                             " http://{0}".format(wo_domain))

            # Add nginx conf folder into GIT
            WOGit.add(self, ["{0}/conf/nginx".format(wo_site_webroot)],
                      msg="Adding letsencrypts config of site: {0}"
                      .format(wo_domain))
            updateSiteInfo(self, wo_domain, ssl=letsencrypt)
            return 0

        if pargs.hsts:
            if data['hsts'] is True:
                if os.path.isfile(("{0}/conf/nginx/ssl.conf")
                                  .format(wo_site_webroot)):
                    if not os.path.isfile("{0}/conf/nginx/hsts.conf"
                                          .format(wo_site_webroot)):
                        SSL.setuphsts(self, wo_domain)
                    else:
                        Log.error(self, "HSTS is already configured for given "
                                        "site")
                    if not WOService.reload_service(self, 'nginx'):
                        Log.error(self, "service nginx reload failed. "
                                  "check issues with `nginx -t` command")
                else:
                    Log.error(self, "HTTPS is not configured for given "
                              "site")

            elif data['hsts'] is False:
                if os.path.isfile(("{0}/conf/nginx/hsts.conf")
                                  .format(wo_site_webroot)):
                    WOFileUtils.mvfile(self, "{0}/conf/nginx/hsts.conf"
                                       .format(wo_site_webroot),
                                       '{0}/conf/nginx/hsts.conf.disabled'
                                       .format(wo_site_webroot))
                    if not WOService.reload_service(self, 'nginx'):
                        Log.error(self, "service nginx reload failed. "
                                  "check issues with `nginx -t` command")
                else:
                    Log.error(self, "HSTS is not configured for given "
                              "site")
        if pargs.ngxblocker:
            if ngxblocker is True:
                setupngxblocker(self, wo_domain)
            elif ngxblocker is False:
                if os.path.isfile("{0}/conf/nginx/ngxblocker.conf"
                                  .format(wo_site_webroot)):
                    WOFileUtils.mvfile(
                        self,
                        "{0}/conf/nginx/ngxblocker.conf"
                        .format(wo_site_webroot),
                        "{0}/conf/nginx/ngxblocker.conf.disabled"
                        .format(wo_site_webroot))
            # Service Nginx Reload
            if not WOService.reload_service(self, 'nginx'):
                Log.error(self, "service nginx reload failed. "
                          "check issues with `nginx -t` command")

        if stype == oldsitetype and cache == oldcachetype:

            # Service Nginx Reload
            if not WOService.reload_service(self, 'nginx'):
                Log.error(self, "service nginx reload failed. "
                          "check issues with `nginx -t` command")

            updateSiteInfo(self, wo_domain, stype=stype, cache=cache,
                           ssl=(bool(check_site.is_ssl)),
                           php_version=check_php_version)

            Log.info(self, "Successfully updated site"
                     " http://{0}".format(wo_domain))
            return 0

        # if data['wo_db_name'] and not data['wp']:
        if 'wo_db_name' in data.keys() and not data['wp']:
            try:
                data = setupdatabase(self, data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details:"
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1
            try:
                wodbconfig = open("{0}/wo-config.php".format(wo_site_webroot),
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
            except IOError as e:
                Log.debug(self, str(e))
                Log.debug(self, "creating wo-config.php failed.")
                Log.info(self, Log.FAIL + "Update site failed. "
                         "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        # Setup WordPress if old sites are html/php/mysql sites
        if data['wp'] and oldsitetype in ['html', 'proxy', 'php',
                                          'mysql', 'php73']:
            try:
                wo_wp_creds = setupwordpress(self, data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        # Uninstall unnecessary plugins
        if oldsitetype in ['wp', 'wpsubdir', 'wpsubdomain']:
            # Setup WordPress Network if update option is multisite
            # and oldsite is WordPress single site
            if data['multisite'] and oldsitetype == 'wp':
                try:
                    setupwordpressnetwork(self, data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update site failed. "
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

            if ((oldcachetype in ['wpsc', 'basic', 'wpredis', 'wprocket',
                                  'wpce'] and
                 (data['wpfc'])) or (oldsitetype == 'wp' and
                                     data['multisite'] and data['wpfc'])):
                try:
                    plugin_data_object = {
                        "log_level": "INFO",
                        "log_filesize": 5,
                        "enable_purge": 1,
                        "enable_map": "0",
                        "enable_log": 0,
                        "enable_stamp": 1,
                        "purge_homepage_on_new": 1,
                        "purge_homepage_on_edit": 1,
                        "purge_homepage_on_del": 1,
                        "purge_archive_on_new": 1,
                        "purge_archive_on_edit": 0,
                        "purge_archive_on_del": 0,
                        "purge_archive_on_new_comment": 0,
                        "purge_archive_on_deleted_comment": 0,
                        "purge_page_on_mod": 1,
                        "purge_page_on_new_comment": 1,
                        "purge_page_on_deleted_comment": 1,
                        "cache_method": "enable_fastcgi",
                        "purge_method": "get_request",
                        "redis_hostname": "127.0.0.1",
                                          "redis_port": "6379",
                                          "redis_prefix": "nginx-cache:"}
                    plugin_data = json.dumps(plugin_data_object)
                    setupwp_plugin(self, 'nginx-helper',
                                   'rt_wp_nginx_helper_options',
                                   plugin_data, data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update nginx-helper "
                             "settings failed. "
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

            elif ((oldcachetype in ['wpsc', 'basic', 'wpfc',
                                    'wprocket', 'wpce'] and
                   (data['wpredis'])) or (oldsitetype == 'wp' and
                                          data['multisite'] and
                                          data['wpredis'])):
                try:
                    plugin_data_object = {
                        "log_level": "INFO",
                        "log_filesize": 5,
                        "enable_purge": 1,
                        "enable_map": "0",
                        "enable_log": 0,
                        "enable_stamp": 1,
                        "purge_homepage_on_new": 1,
                        "purge_homepage_on_edit": 1,
                        "purge_homepage_on_del": 1,
                        "purge_archive_on_new": 1,
                        "purge_archive_on_edit": 0,
                        "purge_archive_on_del": 0,
                        "purge_archive_on_new_comment": 0,
                        "purge_archive_on_deleted_comment": 0,
                        "purge_page_on_mod": 1,
                        "purge_page_on_new_comment": 1,
                        "purge_page_on_deleted_comment": 1,
                        "cache_method": "enable_redis",
                        "purge_method": "get_request",
                        "redis_hostname": "127.0.0.1",
                                          "redis_port": "6379",
                                          "redis_prefix": "nginx-cache:"}
                    plugin_data = json.dumps(plugin_data_object)
                    setupwp_plugin(self, 'nginx-helper',
                                   'rt_wp_nginx_helper_options',
                                   plugin_data, data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update nginx-helper "
                             "settings failed. "
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1
            else:
                try:
                    # disable nginx-helper
                    plugin_data_object = {
                        "log_level": "INFO",
                        "log_filesize": 5,
                        "enable_purge": 0,
                        "enable_map": 0,
                        "enable_log": 0,
                        "enable_stamp": 0,
                        "purge_homepage_on_new": 1,
                        "purge_homepage_on_edit": 1,
                        "purge_homepage_on_del": 1,
                        "purge_archive_on_new": 1,
                        "purge_archive_on_edit": 0,
                        "purge_archive_on_del": 0,
                        "purge_archive_on_new_comment": 0,
                        "purge_archive_on_deleted_comment": 0,
                        "purge_page_on_mod": 1,
                        "purge_page_on_new_comment": 1,
                        "purge_page_on_deleted_comment": 1,
                        "cache_method": "enable_redis",
                        "purge_method": "get_request",
                        "redis_hostname": "127.0.0.1",
                                          "redis_port": "6379",
                                          "redis_prefix": "nginx-cache:"}
                    plugin_data = json.dumps(plugin_data_object)
                    setupwp_plugin(
                        self, 'nginx-helper',
                        'rt_wp_nginx_helper_options', plugin_data, data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update nginx-helper "
                             "settings failed. "
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

            if ((oldcachetype in ['wpsc', 'basic',
                                  'wpfc', 'wprocket', 'wpredis'] and
                 (data['wpce'])) or (oldsitetype == 'wp' and
                                     data['multisite'] and
                                     data['wpce'])):
                try:
                    installwp_plugin(self, 'cache-enabler', data)
                    # setup cache-enabler
                    plugin_data_object = {
                        "expires": 24,
                        "new_post": 1,
                        "new_comment": 0,
                        "webp": 0,
                        "clear_on_upgrade": 1,
                        "compress": 0,
                        "excl_ids": "",
                        "excl_regexp": "",
                        "excl_cookies": "",
                        "incl_attributes": "",
                        "minify_html": 1}
                    plugin_data = json.dumps(plugin_data_object)
                    setupwp_plugin(self, 'cache-enabler',
                                   'cache-enabler', plugin_data, data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update cache-enabler "
                             "settings failed. "
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

            if oldcachetype == 'wpsc' and not data['wpsc']:
                try:
                    uninstallwp_plugin(self, 'wp-super-cache', data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update site failed."
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

            if oldcachetype == 'wpredis' and not data['wpredis']:
                try:
                    uninstallwp_plugin(self, 'redis-cache', data)
                except SiteError as e:
                    Log.debug(self, str(e))
                    Log.info(self, Log.FAIL + "Update site failed."
                             "Check the log for details:"
                             " `tail /var/log/wo/wordops.log` "
                             "and please try again")
                    return 1

        if oldcachetype != 'wpsc' and data['wpsc']:
            try:
                installwp_plugin(self, 'wp-super-cache', data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        if oldcachetype == 'wprocket' and not data['wprocket']:
            try:
                uninstallwp_plugin(self, 'wp-rocket', data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        if oldcachetype == 'wpce' and not data['wpce']:
            try:
                uninstallwp_plugin(self, 'cache-enabler', data)
            except SiteError as e:
                Log.debug(self, str(e))
                Log.info(self, Log.FAIL + "Update site failed."
                         "Check the log for details: "
                         "`tail /var/log/wo/wordops.log` and please try again")
                return 1

        # Service Nginx Reload
        if not WOService.reload_service(self, 'nginx'):
            Log.error(self, "service nginx reload failed. "
                      "check issues with `nginx -t` command")

        WOGit.add(self, ["/etc/nginx"],
                  msg="{0} updated with {1} {2}"
                  .format(wo_www_domain, stype, cache))
        # Setup Permissions for webroot
        try:
            setwebrootpermissions(self, data['webroot'])
        except SiteError as e:
            Log.debug(self, str(e))
            Log.info(self, Log.FAIL + "Update site failed."
                     "Check the log for details: "
                     "`tail /var/log/wo/wordops.log` and please try again")
            return 1

        if wo_auth and len(wo_auth):
            for msg in wo_auth:
                Log.info(self, Log.ENDC + msg)

        display_cache_settings(self, data)
        if data['wp'] and oldsitetype in ['html', 'php', 'mysql']:
            Log.info(self, "\n\n" + Log.ENDC + "WordPress admin user :"
                     " {0}".format(wo_wp_creds['wp_user']))
            Log.info(self, Log.ENDC + "WordPress admin password : {0}"
                     .format(wo_wp_creds['wp_pass']) + "\n\n")
        if oldsitetype in ['html', 'php'] and stype != 'php':
            updateSiteInfo(self, wo_domain, stype=stype, cache=cache,
                           db_name=data['wo_db_name'],
                           db_user=data['wo_db_user'],
                           db_password=data['wo_db_pass'],
                           db_host=data['wo_db_host'],
                           ssl=True if check_site.is_ssl else False,
                           php_version=check_php_version)
        else:
            updateSiteInfo(self, wo_domain, stype=stype, cache=cache,
                           ssl=True if check_site.is_ssl else False,
                           php_version=check_php_version)
        Log.info(self, "Successfully updated site"
                 " http://{0}".format(wo_domain))
        return 0


class WOSiteDeleteController(CementBaseController):
    class Meta:
        label = 'delete'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = 'delete an existing website'
        arguments = [
            (['site_name'],
                dict(help='domain name to be deleted', nargs='?')),
            (['--no-prompt'],
                dict(help="doesnt ask permission for delete",
                     action='store_true')),
            (['-f', '--force'],
                dict(help="forcefully delete site and configuration",
                     action='store_true')),
            (['--all'],
                dict(help="delete files & db", action='store_true')),
            (['--db'],
                dict(help="delete db only", action='store_true')),
            (['--files'],
                dict(help="delete webroot only", action='store_true')),
        ]

    @expose(help="Delete website configuration and files")
    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        if not pargs.site_name and not pargs.all:
            try:
                while not pargs.site_name:
                    pargs.site_name = (input('Enter site name : ')
                                       .strip())
            except IOError as e:
                Log.debug(self, str(e))
                Log.error(self, 'could not input site name')

        pargs.site_name = pargs.site_name.strip()
        wo_domain = WODomain.validate(self, pargs.site_name)
        wo_www_domain = "www.{0}".format(wo_domain)
        wo_db_name = ''
        wo_prompt = ''
        wo_nginx_prompt = ''
        mark_db_delete_prompt = False
        mark_webroot_delete_prompt = False
        mark_db_deleted = False
        mark_webroot_deleted = False
        if not check_domain_exists(self, wo_domain):
            Log.error(self, "site {0} does not exist".format(wo_domain))

        if ((not pargs.db) and (not pargs.files) and
                (not pargs.all)):
            pargs.all = True

        if pargs.force:
            pargs.no_prompt = True

        # Gather information from wo-db for wo_domain
        check_site = getSiteInfo(self, wo_domain)
        wo_site_type = check_site.site_type
        wo_site_webroot = check_site.site_path
        if wo_site_webroot == 'deleted':
            mark_webroot_deleted = True
        if wo_site_type in ['mysql', 'wp', 'wpsubdir', 'wpsubdomain']:
            wo_db_name = check_site.db_name
            wo_db_user = check_site.db_user
            if self.app.config.has_section('mysql'):
                wo_mysql_grant_host = self.app.config.get('mysql', 'grant-host')
            else:
                wo_mysql_grant_host = 'localhost'
            if wo_db_name == 'deleted':
                mark_db_deleted = True
            if pargs.all:
                pargs.db = True
                pargs.files = True
        else:
            if pargs.all:
                mark_db_deleted = True
                pargs.files = True

        # Delete website database
        if pargs.db:
            if wo_db_name != 'deleted' and wo_db_name != '':
                if not pargs.no_prompt:
                    wo_db_prompt = input('Are you sure, you want to delete'
                                         ' database [y/N]: ')
                else:
                    wo_db_prompt = 'Y'
                    mark_db_delete_prompt = True

                if wo_db_prompt == 'Y' or wo_db_prompt == 'y':
                    mark_db_delete_prompt = True
                    Log.info(self, "Deleting Database, {0}, user {1}"
                             .format(wo_db_name, wo_db_user))
                    deleteDB(self, wo_db_name, wo_db_user,
                             wo_mysql_grant_host, False)
                    updateSiteInfo(self, wo_domain,
                                   db_name='deleted',
                                   db_user='deleted',
                                   db_password='deleted')
                    mark_db_deleted = True
                    Log.info(self, "Deleted Database successfully.")
            else:
                mark_db_deleted = True
                Log.info(self, "Does not seems to have database for this site."
                         )

        # Delete webroot
        if pargs.files:
            if wo_site_webroot != 'deleted':
                if not pargs.no_prompt:
                    wo_web_prompt = input('Are you sure, you want to delete '
                                          'webroot [y/N]: ')
                else:
                    wo_web_prompt = 'Y'
                    mark_webroot_delete_prompt = True

                if wo_web_prompt == 'Y' or wo_web_prompt == 'y':
                    mark_webroot_delete_prompt = True
                    Log.info(self, "Deleting Webroot, {0}"
                             .format(wo_site_webroot))
                    deleteWebRoot(self, wo_site_webroot)
                    updateSiteInfo(self, wo_domain, webroot='deleted')
                    mark_webroot_deleted = True
                    Log.info(self, "Deleted webroot successfully")
            else:
                mark_webroot_deleted = True
                Log.info(self, "Webroot seems to be already deleted")

        if not pargs.force:
            if (mark_webroot_deleted and mark_db_deleted):
                # TODO Delete nginx conf
                removeNginxConf(self, wo_domain)
                deleteSiteInfo(self, wo_domain)
                Log.info(self, "Deleted site {0}".format(wo_domain))
                # else:
                # Log.error(self, " site {0} does
                # not exists".format(wo_domain))
        else:
            if (mark_db_delete_prompt or mark_webroot_delete_prompt or
                    (mark_webroot_deleted and mark_db_deleted)):
                # TODO Delete nginx conf
                removeNginxConf(self, wo_domain)
                deleteSiteInfo(self, wo_domain)
                Log.info(self, "Deleted site {0}".format(wo_domain))


class WOSiteListController(CementBaseController):
    class Meta:
        label = 'list'
        stacked_on = 'site'
        stacked_type = 'nested'
        description = 'List websites'
        arguments = [
            (['--enabled'],
                dict(help='List enabled websites', action='store_true')),
            (['--disabled'],
                dict(help="List disabled websites", action='store_true')),
        ]

    @expose(help="Lists websites")
    def default(self):
        pargs = self.app.pargs
        sites = getAllsites(self)
        if not sites:
            pass

        if pargs.enabled:
            for site in sites:
                if site.is_enabled:
                    Log.info(self, "{0}".format(site.sitename))
        elif pargs.disabled:
            for site in sites:
                if not site.is_enabled:
                    Log.info(self, "{0}".format(site.sitename))
        else:
            for site in sites:
                Log.info(self, "{0}".format(site.sitename))


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOSiteController)
    app.handler.register(WOSiteCreateController)
    app.handler.register(WOSiteUpdateController)
    app.handler.register(WOSiteDeleteController)
    app.handler.register(WOSiteListController)
    app.handler.register(WOSiteEditController)
    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_site_hook)
