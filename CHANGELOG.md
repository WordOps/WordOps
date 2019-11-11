# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## Releases

### v3.9.x - [Unreleased]

### v3.10.3 - 2019-11-11

#### Added

- [ACME] Display warning about sudo usage when issuing certificate with DNS API validation (require `sudo -E`)

#### Changed

- [ACME] Resolve domain IP over HTTPS with Cloudflare DNS Resolver
- [CORE] Cement Framework updated to v2.10.2
- [SITE] database name = 0 to 16 characters from the site name + 4 randomly generated character
- [SITE] database user = 0 to 12 characters from the site name + 4 randomy generated character
- [STACK] Improve sysctl tweak deployment

#### Fixed

- [SITE] https redirection missing on subdomains sites
- Issues with digitalocean mariadb repository
- Cement Framework output handler issues
- [CLEAN] check if Nginx is installed before purging fastcgi or opcache

### v3.10.2 - 2019-11-06

#### Added

- [STACK] nanorc syntax highlighting for nano editor : `--nanorc`

#### Changed

- `wo stack remove/purge` without argument print help instead of removing main stacks

#### Fixed

- Import rtCamp:EasyEngine GPG key to avoid issues with previous nginx repository
- Unable to issue certificate for a domain if a subdomain certificate exist
- Incorrect WP-CLI path site_url_https function
- `wo stack upgrade --ngxblocker` not working properly

### v3.10.1 - 2019-10-30

#### Fixed

- WordOps install/upgrade from PyPi

### v3.10.0 - 2019-10-30

#### Added

- WordOps is now installed inside a wheel with pip (easier, cleaner and safer) from PyPi
- Redis 5.0.6 package backported to Debian 8/9/10
- Custom motd to display a message if a new WordOps release is available
- Run `mysql_upgrade` during MySQL upgrade with `wo stack upgrade` to perform migration if needed
- `wo stack upgrade --ngxblocker` to update ngxblocker blocklist

#### Changed

- Sysctl tweaks are applied during stack install and removed from install script
- Nginx & MariaDB systemd tweaks are removed from install script and applied during stacks install/upgrade
- Initial creation of .gitconfig is displayed the first time you run the command `wo`
- Added `/var/lib/php/sessions/` to open_basedir to allow php sessions storage
- WordOps now check if a repository already exist before trying to adding it again.
- Improved SSL certificate error messages by displaying domain IP and server IP
- Version check before updating WordOps with `wo update` is now directly handled by `wo`
- Refactored WordOps download function with python3-requests
- MySQL backup path changed to `/var/lib/wo-backup/mysql`
- Do not check anymore if stack are installed with apt in `wo service` but only if there is a systemd service
- Refactored `--letsencrypt=renew`. Require the flag `--force` if certificate expiration is more than 45 days
- Improve netdata stack upgrade with install from source detection and updater fallback

#### Fixed

- Incorrect PHP-FPM log path is `wo log`
- force-ssl.conf not removed after removing a site
- `wo clean --opcache` not working with invalid SSL certificate
- `wo stack install --cheat` wasn't working properly previously
- `wo info` failure depending on php-fpm pool name. ConfigParser will now detect the section name.


### v3.9.9.4 -  2019-10-18

#### Changed

- [STACK] New Nginx package built with libbrotli-dev for all linux distro supported by WordOps

#### Fixed

- GPG keys error with previous EasyEngine Nginx repository
- Issue with `--ngxblocker` stack removal/purge
- Install/Update issues with python3 setup.py
- WordOps deploying SSL certificate even if acme.sh failed

### v3.9.9.3 -  2019-10-15

#### Added

- [STACK] Add Nginx TLS 1.3 0-RTT configuration

#### Changed

- [STACK] New Nginx package built with OpenSSL_1.1.1d and the latest ngx_brotli module

#### Fixed

- `wo stack upgrade` when using nginx-ee
- `wo secure --auth`
- `wo secure --sshport` not working with default ssh config
- Issues after APT repositories informations changed
- `www` was added to WordPress site url with subdomains [Issue #178](https://github.com/WordOps/WordOps/issues/178)
- Issuing certificate with acme.sh for sub.sub-domains not working

### v3.9.9.2 - 2019-10-04

#### Added

- [STACK] Nginx server_names_hash_bucket_size automated fix
- [STACK] Nginx configuration rollback in case of failure after `wo stack upgrade --nginx`
- [STACK] Nginx ultimate bad bots blocker with `wo stack install --ngxblocker`
- [STACK] Added support for custom Nginx compiled from source
- [STACK] Rollback configuration with Git in case of failure during service reload/restart
- [SITE] Enable or disable Nginx ultimate bad bots blocker with `wo site update site.tld --ngxblocker/--ngxblocker=off`

#### Changed

- [CORE] Query acme.sh database directly to check if a certificate exist
- [SITE] `--letsencrypt=renew` is deprecated because not it's not required with acme.sh

#### Fixed

- [SITE] Issues with root_domain variable with `wo site update`
- [SECURE] Wrong sftp-server path in sshd_config
- [SITE] Git error when using flag `--vhostonly`
- [SITE] Wrong plugin name displayed when installing Cache-Enabler

### v3.9.9.1 - 2019-09-26

#### Added

- [SECURE] Allow new ssh port with UFW when running `wo secure --sshport`
- [STACK] Additional Nginx directives to prevent access to log files or backup from web browser
- [CORE] apt-mirror-updater to select the fastest debian/ubuntu mirror with automatic switching between mirrors if the current mirror is being updated
- [SITE] add `--force` to force Let's Encrypt certificate issuance even if DNS check fail
- [STACK] check if another mta is installed before installing sendmail
- [SECURE] `--allowpassword` to allow password when using `--ssh` with `wo secure`

#### Changed

- [SECURE] Improved sshd_config template according to Mozilla Infosec guidelines
- [STACK] Always add stack configuration into Git before making changes to make rollback easier
- [STACK] Render php-fpm pools configuration from template
- [STACK] Adminer updated to v4.7.3

#### Fixed

- [STACK] UFW setup after removing all stacks with `wo stack purge --all`
- [CONFIG] Invalid CORS header
- [STACK] PHP-FPM stack upgrade failure due to pool configuration

### v3.9.9 - 2019-09-24

#### Added

- [STACK]  UFW now available as a stack with flag `--ufw`
- [SECURE] `wo secure --ssh` to harden ssh security
- [SECURE] `wo secure --sshport` to change ssh port
- [SITE] check domain DNS records before issuing a new certificate without DNS API
- [STACK] Acme challenge with DNS Alias mode `--dnsalias=aliasdomain.tld` [acme.sh wiki](https://github.com/Neilpang/acme.sh/wiki/DNS-alias-mode)

#### Changed

- [APP] WordOps dashboard updated to v1.2, shipped as a html file, it can be used without PHP stack
- [STACK] Refactor Let's Encrypt with acme.sh
- [STACK] Log error improved with acme.sh depending on the acme challenge (DNS API or Webroot)
- [INSTALL] Removed UFW setup from install script
- [APP] phpMyAdmin updated to v4.9.1
- [STACK] Commit possible Nginx configuration changes into Git before and after performing tasks (in `wo secure` for example)
- [CORE] Update deprecated handlers and hooks registration

#### Fixed

- [STACK] `wo stack purge --all` failure if mysql isn't installed
- [INSTALL] Fix EEv3 files cleanup
- [SECURE] Incorrect variable usage in `wo secure --port`
- [INSTALL] Fix backup_ee function in install script

### v3.9.8.12 - 2019-09-20

#### Changed

- [APP] WP-CLI updated to v2.3.0
- [CORE] Improved SSL certificates management from previous letsencrypt or certbot install
- [CORE] Use a separate python file for gitconfig during installation to redirect setup.py output into logs
- [CORE] updated cement to v2.8.2
- [CORE] removed old `--experimental flag`
- [CORE] Improve and simplify install script

#### Fixed

- htpasswd protection when migrating from EasyEngine v3 [Issue #152](https://github.com/WordOps/WordOps/issues/152)
- acme.sh install when migration from EasyEngine v3 [Issue #153](https://github.com/WordOps/WordOps/issues/153)

### v3.9.8.11 - 2019-09-06

#### Changed

- Improved general logs display
- UFW configuration is only applied during initial installation if UFW is disabled

#### Fixed

- Redis-server configuration and start
- Nginx upgrade with `wo stack upgrade`

### v3.9.8.10 - 2019-09-04

#### Changed

- Improve Let's Encrypt certificate issuance logging informations
- MariaDB configuration & optimization is now rendered from a template (can be protected against overwriting with .custom)

#### Fixed

- Fix cheat.sh install [PR #139](https://github.com/WordOps/WordOps/pull/139)
- sslutils error when trying to display SSL certificate expiration
- Fix cheat.sh symbolic link check before creation
- subdomain detection with complex suffixes like com.br
- Fix mariadb install/upgrade when running mariadb-10.1
- Fix mariadb install/upgrade on raspbian and debian 8
- Fix mariadb tuning wrong pool_instance calculation

### v3.9.8.9 - 2019-09-03

#### Added

- Rate limiter on wp-cron.php and xmlrpc.php
- mime.types template to handle missing extension ttf
- try_files directive for favicon
- additional settings for fail2ban
- asynchronous installer to decrease install/update duration

#### Fixed

- Several typo or syntax errors
- `wo  site` errors due to broken symlinks for access.log or error.log
- `wo clean` error due to unused memcached flag
- MySQL database and user variables overwrited in `wo site`

### v3.9.8.8 - 2019-09-02

#### Added

- Sendmail stack to send WordPress welcome email properly
- Backup all MySQL databases before removing/purging MySQL stack

#### Changed

- do not terminate stack install process on errors
- WordOps internal log rotation limit increased to 1MB

#### Fixed

- ufw rules for proftpd not applied
- phpredisadmin install
- netdata configuration
- extplorer installation
- add LANG='en_US.UTF-8' in install script
- Read public_suffix list with utf8 encoding. Issue [#128](https://github.com/WordOps/WordOps/issues/128)
- Netdata uninstall script path. PR [#135](https://github.com/WordOps/WordOps/pull/135)
- SSL Certificates expiration for subdomains

### v3.9.8.7 - 2019-08-31

#### Changed

- WordPress default permalinks structure from `/%year%/%monthnum%/%day%/%postname%/` -> `/%postname%/`

#### Fixed

- Error with `wo stack upgrade --nginx`
- Install/update script version check
- clamAV stack install

### v3.9.8.6 - 2019-08-30

#### Added

- Subdomains are automatically secured with an existant Wildcard LetsEncrypt SSL certificate.
(If a wildcard certificate exist, WordOps will use this certificate for subdomains instead of issuing new certificates)
- MySQL & Redis stack to `wo stack remove/purge`

#### Changed

- Date format in backup name : /backup/30Aug2019035932 -> /backup/30Aug2019-03-59-32
- Cleanup and update bash_completion
- cheat.sh is installed with WordOps install script, not as a stack because it wasn't downloaded at all by WordOps (unknown reason yet)

#### Fixed

- cache-enabler plugin not installed and configured with `wo site update site.tld --wpce`
- possible issue with domain variable in `--letsencrypt=wildcard`
- python3-mysqldb not available on Debian 8 (Jessie)
- Fix mysql variable skip-name-resolved
- Fix typo in redis tuning directives

### v3.9.8.5 - 2019-08-30

#### Changed

- updated OpCache Control Panel to v0.2.0

#### Fixed

- Fix Netdata install on Raspbian 9/10
- `wo stack remove/purge` confirmation
- Nginx error after removing a SSL certificate used to secure WordOps backend
- `wo stack install --all`
- ProFTPd fail2ban rules set twice if removed and reinstalled
- `wo site update`

### v3.9.8.4 - 2019-08-28

#### Added

- cht.sh stack : linux online cheatsheet. Usage : `cheat <command>`. Example for tar : `cheat tar`
- ClamAV anti-virus with weekly cronjob to update signatures database
- Internal function to add daily cronjobs
- Additional comment to detect previous configuration tuning (MariaDB & Redis)
- Domain/Subdomain detection based on public domain suffixes list for letsencrypt
- Increase Nginx & MariaDB systemd open_files limits
- Cronjob to update Cloudflare IPs list
- mariadb-backup to perform full and non-blocking databases backup (installation only. Backup feature will be available soon)
- Nginx configuration check before performing start/reload/restart (If configuration check fail, WordOps will not reload/restart Nginx anymore)
- Nginx mapping to proxy web-socket connections

#### Changed

- eXplorer filemanager isn't installed with WordOps dashboard anymore, and a flag `--extplorer` is available. But it's still installed when running the command `wo stack install`
- Template rendering function now check for a .custom file before overwriting a configuration by default.
- flag `--letsencrypt=subdomain` is not required anymore, you can use `--letsencrypt` or `-le`
- Simplifiy and decrease duration of `apt-key` GPG keys import

#### Fixed

- typo error in `wo site update` : [PR #126](https://github.com/WordOps/WordOps/pull/126)

### v3.9.8.3 - 2019-08-21

#### Changed

- Nginx package OpenSSL configuration improvements (TLS v1.3 now available on all operating systems supported by WordOps)
- remove user prompt for confirmation with `wo update`
- Nginx stack will not be upgraded with `wo update` anymore. This can be done at anytime with `wo upgrade --nginx`
- Databases name and user are now semi-randomly generated (0-8 letters from the domain + 8 random caracters)

#### Fixed

- `wo upgrade` output
- Database name or database user length

### v3.9.8.2 - 2019-08-20

#### Added

- Additional cache expection for Easy Digital Downloads [PR #120](https://github.com/WordOps/WordOps/pull/120)
- Additional settings to support mobile with WP-Rocket
- Add the ability to block nginx configuration overwriting by adding a file .custom. Example with /etc/nginx/conf.d/webp.conf -> `touch /etc/nginx/conf.d/webp.conf.custom`
- If there is a custom file, WordOps will write the configuration in a file named fileconf.conf.orig to let users implement possible changes
- UFW minimal configuration during install. Can be disabled with the flag `-w`, `--wufw` or `--without-ufw`. Example : `wget -qO wo wops.cc && sudo bash wo -w`

#### Fixed

- WordOps internal database creation on servers running with custom setup

### v3.9.8.1 - 2019-08-18

#### Added

- WordOps backend is automatically secured by the first Let's Encrypt SSL certificate issued

#### Changed

- Extra Nginx directives moved from nginx.conf to conf.d/tweaks.conf

#### Fixed

- MySQLTuner installation
- `wo stack remove/purge --all`
- variable substitution in install script
- `wo stack upgrade --phpmyadmin/--dashboard`
- phpmyadmin blowfish_secret key length
- Cement App not exiting on close in case of error

### v3.9.8 - 2019-08-16

#### Added

- Allow web browser caching for json and webmanifest files
- nginx-core.mustache template used to render nginx.conf during stack setup
- APT Packages configuration step with `wo stack upgrade` to apply new configurations
- Cloudflare restore real_ip configuration
- WP-Rocket plugin support with the flag `--wprocket`
- Cache-Enabler plugin support with the flag `--wpce`
- Install unattended-upgrade and enable automated security updates
- Enable time synchronization with ntp
- Additional cache exception for woocommerce

#### Changed

- Do not force Nginx upgrade if a custom Nginx package compiled with nginx-ee is detected
- Gzip enabled again by default with configuration in /etc/nginx/conf.d/gzip.conf
- Brotli configuration moved in /etc/nginx/conf.d/brotli.conf.disabled (disabled by default)
- Moving package configuration in a new plugin stack_pref.py
- Cleanup templates by removing all doublons (with/without php7) and replacing them with variables
- Updated Nginx to v1.16.1 in response to HTTP/2 vulnerabilites discovered
- Disable temporary adding swap feature (not working)
- `wo stack upgrade --nginx` is now able to apply new configurations during `wo update`, it highly reduce upgrade duration

#### Fixed

- Error in HSTS header syntax

### v3.9.7.2 - 2019-08-12

#### Fixed

- redis.conf permissions additional fix

### v3.9.7.1 - 2019-08-09

#### Changed

- Set WordOps backend password length from 16 to 24
- Upgrade framework cement to 2.6.0
- Upgrade PyMySQL to 0.9.3
- Upgrade Psutil to 5.6.3

#### Fixed

- Missing import in `wo sync`
- redis.conf incorrect permissions

### v3.9.7 - 2019-08-02

#### Added

- MySQL configuration tuning
- Cronjob to optimize MySQL databases weekly
- WO-kernel systemd service to automatically apply kernel tweaks on server startup
- Proftpd stack now secured with TLS
- New Nginx package built with Brotli from operating system libraries
- Brotli configuration with only well compressible MIME types
- WordPress site url automatically updated to `https://domain.tld` when using `-le/--letsencrypt` flag
- More informations during certificate issuance about validation mode selected
- `--php72` as alternative for `--php`
- Automated removal of the deprecated variable `ssl on;` in previous Nginx ssl.conf
- Project Contributing guidelines
- Project Code of conduct

#### Changed

- `wo maintenance` refactored
- Improved debug log
- Updated Nginx configuration process to not overwrite files with custom data (htpasswd-wo, acl.conf etc..)
- Adminer updated to v4.7.2
- eXtplorer updated to v2.1.13
- Removed WordOps version from the Nginx header X-Powered-By to avoid possible security issues
- Several code quality improvements to speed up WordOps execution
- Few adjustements on PHP-FPM configuration (max_input_time,opcache.consistency_checks)
- Added /dev/urandom & /dev/shm to open_basedir in PHP-FPM configuration

#### Fixed

- Kernel tweaks were not applied without server reboot
- Fail2ban standalone install
- `wo stack purge --all` error due to PHP7.3 check
- Nginx helper configuration during plugin install for Nginx fastcgi_cache and redis-cache
- phpRedisAdmin stack installation
- Fixed Travis CI build on pull requests
- Nginx `server_names_hash_bucket_size` variable error after WordOps upgrade

### v3.9.6.2 - 2019-07-24

#### Changed

- Improve `wo update` process duration
- Improve package install/upgrade/remove process

#### Fixed

- phpMyAdmin archive download link archive
- Arguments `--letsencrypt=clean/purge`
- Incorrect directory removal during stack upgrade

### v3.9.6.1 - 2019-07-23

#### Fixed

- Typo in  `--letsencrypt=subdomain`
- phpMyAdmin upgrade archive extraction
- Error in the command `wo update`. Please `wo update --beta` as workaround

### v3.9.6 - 2019-07-20

#### Added

- New Nginx package on Ubuntu with Cloudflare HTTP/2 HPACK and Dynamic TLS records
- phpMyAdmin upgrade with `wo stack upgrade --phpmyadmin`
- Wildcard SSL Certificates support with DNS validation
- Let's Encrypt DNS API support (Cloudflare, DigitalOcean, etc ..) on domain, subdomain, and wildcard
- Flag `--letsencrypt=clean` to purge a previous SSL configuration
- Support for Debian 10 buster (testing - not ready for production)
- Fail2ban with custom jails to secure WordPress & SSH
- Variable `keylength` in /etc/wo/wo.conf to define letsencrypt certificate keylenght
- ProFTPd stack with UFW & Fail2ban configurationz
- Beta branch and command `wo update --beta` for beta releases
- Extra directives in wp-config.php (limit posts revisions, set max_memory, enable auto-update for minor-releases)

#### Fixed

- Nginx was not reloaded after enabling HSTS
- Netdata, Composer & Fail2Ban stack remove and purge
- WordPress not installed by `wo site update` with basic php73 sites

### v3.9.5.4 - 2019-07-13

#### Added

- New Nginx package on Ubuntu with TLS v1.3 support (OpenSSL 1.1.1c)
- Netdata upgrade with `wo stack upgrade --netdata`
- Netdata stack remove/purge

#### Changed

- phpRedisAdmin is now installed with the stack `--admin`
- Remove memcached - not required anymore

#### Fixed

- phpRedisAdmin installation
- Duplicated locations /robots.txt after upgrade to v3.9.5.3
- Let's Encrypt stack `wo site update --letsencrypt/--letsencrypt=off`
- pt-query-advisor dead link
- Netdata persistant configuration

### v3.9.5.3 - 2019-06-18

#### Added

- Argument `--preserve` with the command `wo update` to keep current Nginx configuration

#### Fixed

- Nginx upgrade failure when running wo update

### v3.9.5.2 - 2019-06-17

#### Added

- Non-interactive install/upgrade
- Argument `--force` with the command `wo update`
- Argument `-s|--silent` to perform non interactive installation

#### Changed

- robots.txt location block moved from locations-wo.conf to wpcommon(-php7).php

#### Fixed

- WP_CACHE_KEY_SALT set twice with wpredis
- WordOps version check when using `wo update`
- robots.txt file download if not created
- PHP-FPM socket path in stub_status.conf : PR [#82](https://github.com/WordOps/WordOps/pull/82)

### v3.9.5.1 - 2019-05-10

#### Fixed

- Adminer download link

### v3.9.5 - 2019-05-02

#### Added

- IPv6 support with HTTPS
- Brotli support in Nginx
- Let's Encrypt support with --proxy
- Install script handle migration from EEv3
- load-balancing on unix socket for php-fpm
- stub_status vhost for metrics
- `--letsencrypt=subdomain` option
- opcache optimization for php-fpm
- EasyEngine configuration backup before migration
- EasyEngine configuration cleanup after migration
- WordOps configuration backup before upgrade
- Previous acme.sh certs migration
- "wo maintenance" command to perform server package update & cleanup
- Support for Netdata on backend : https://server.hostname:22222/netdata/
- New Stacks : composer and netdata
- additional argument for letsencrypt : --hsts
- Clean Theme for adminer
- Credits for tools shipped with WordOps
- Cache exception for Easy Digital Download
- Additional cache exceptions for Woocommerce
- MySQL monitoring with Netdata
- WordOps-dashboard on 22222, can be installed with `wo stack install`
- Extplorer filemanager in WordOps backend
- Enable OSCP Stapling with Let's Encrypt
- Compress database backup with pigz (faster than gzip) before updating sites
- Support for Ubuntu 19.04 (disco) - few php extensions missing
- Support for Raspbian 9 (stretch) - tested on Raspberry Pi 3b+
- backup letsencrypt certificate before upgrade
- directives emergency_restart_threshold & emergency_restart_interval to restart php-fpm in case of failure
- EasyEngine cronjob removal during install
- Kernel tweaks via systctl.conf
- open_basedir on php-fpm process to forbid access with php outside of /var/www & /run/nginx-cache

#### Changed

- letsencrypt stack refactored with acme.sh
- letsencrypt validation with webroot folder
- hardened nginx ssl_ecdh_curve
- Update phpredisadmin
- Increase MySQL root password size to 24 characters
- Increase MySQL users password size to 24 characters
- Nginx locations template is the same for php7.2 & 7.3
- backend SSL configuration now stored in /var/www/22222/conf/nginx/ssl.conf
- Install Netdata with static pre-built binaries instead of having to compile it from source
- Nginx updated to new stable release (1.16.0)
- New packages (phpmyadmin, adminer, composer) are not download in /tmp anymore

#### Fixed

- PHP 7.3 extras when php 7.2 isn't installed
- acme.sh installation
- acme.sh alias with config home variable
- deb.sury.org repository gpg key
- Nginx upgrade from previous WordOps release
- Force new Nginx templates during update
- Error message about missing my.cnf file during upgrade
- PHP 7.2 & PHP 7.3 pool configuration during upgrade
- WordOps backup directory creation before upgrade
- EasyEngine database sync during migration
- fix command "wo info"
- phpmyadmin install with composer
- command "wo clean --memcached"
- phpredisadmin setup
- --hsts flag with basic html site
- hsts flag on site not secure with letsencrypt
- fix import of previous acme.sh certificate
- fix proxy webroot folder creation

### v3.9.4 - 2019-03-15

#### Added

- Nginx module nginx_vts
- Migration script from nginx-ee to nginx-wo
- Support for Debian 9 (testing)
- New Nginx build v1.14.2

#### Changed

- Update WP-CLI version to 2.1.0
- Update Adminer to 4.6.2
- Update predis to v1.1.1
- Refactored nginx.conf
- Removed HHVM Stack
- Removed old linux distro checks
- Replace wo-acme-sh by acme.sh

#### Fixed

- Outdated Nginx ssl_ciphers suite
- Debian 9 nginx build

### v3.9.3 - 2019-03-07

#### Changed

- Updated Nginx fastcgi_cache templates
- Updated Nginx redis_cache templates
- Updated Nginx wp-super-cache templates
- Updated Nginx configuration for WordPress 5.0
- remove --experimental args
- MariaDB version bumped to 10.3
- Refactored Changelog
- Updated WO manual
- Updated WO bash_completion
- Refactored README.md

#### Added

- Add WebP image support with Nginx mapping
- Add PHP 7.3 support
- WordPress $skip_cache variable mapping

#### Fixed

- Nginx variable $webp_suffix on fresh install ([#21](https://github.com/WordOps/WordOps/issues/21))
- wo update command ([#7](https://github.com/WordOps/WordOps/issues/7))
- Fix php services management ([#12](https://github.com/WordOps/WordOps/issues/12))
- Fix WP-CLI install

### v3.9.2 - 2018-11-30

#### Changed

- Re-branded the fork to WordOps
- Codebase cleanup
- Set PHP 7.2 as the default
- Included support for newer OS releases
- Reworked the HTTPS configuration
- Added more automated testing with Redis
- Replaced Postfix with smtp-cli
- Dropped mail services
- Dropped w3tc support