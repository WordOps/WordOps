# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## Releases

---

### v3.9.6 - [Unreleased]

### v3.9.5.2 - 2019-06-17

#### Added

- Non-interactive install/upgrade
- Argument `--force` with the command `wo update`
- Argument `-s|--silent` to perform non interactive installation

#### Changed

- robots.txt location block moved from locations-wo.conf to wpcommon.php

#### Fixed

- WP_CACHE_KEY_SALT set twice with wpredis
- WordOps version check when using `wo update`
- robots.txt file download if not created

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
- "--letsencrypt=subdomain" option
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