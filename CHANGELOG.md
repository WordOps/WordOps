# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## Releases

---

### v3.9.5 - [Unreleased]

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
- Theme for adminer
- Credits for tools shipped with WordOps
- Cache exception for Easy Digital Download
- Additional cache exception for Woocommerce
- MySQL monitoring with Netdata
- WordOps-dashboard on 22222
- Extplorer filemanager
- Enable OSCP Stapling with Let's Encrypt
- Compress database backup with pigz before updating sites

#### Changed

- letsencrypt stack refactored with acme.sh
- letsencrypt validation with webroot folder
- hardened nginx ssl_ecdh_curve
- Update phpredisadmin
- Increase MySQL root password size to 16 characters
- Increase MySQL users password size to 16 characters
- Nginx locations template is the same for php7.2 & 7.3
- backend SSL configuration now stored in /var/www/22222/conf/nginx/ssl.conf
- Install Netdata with static pre-built binaries instead of having to compile it from source
- Nginx updated to new stable release (1.16.0)

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