# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

### v3.9.3 - [Unreleased]

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

- Nginx variable $webp_suffix on fresh install
- wo update command
- Fix php services management 
- Fix WP-CLI install


### v3.9.2 - November 30, 2018

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