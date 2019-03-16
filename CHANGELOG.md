# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## Releases

---

### v3.9.5 - [Unreleased]

### Changed

- "--letsencrypt=subdomain" option

#### Fixed

- PHP 7.3 extras when php 7.2 isn't installed
- acme.sh installation

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