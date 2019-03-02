# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

### v3.X.X - [Unreleased]

#### Changed

- Updating nginx fastcgi_cache template
- Updating Nginx configuration for WordPress 5.0
- remove --experimental args

#### Added

- Add webp image support with nginx mapping
- Add PHP 7.3 support

#### Fixed

- Nginx variable $webp_suffix on fresh install

### v3.9.2 - November 30, 2018

#### Changed

- Rebranded the fork to WordOps
- Codebase cleanup
- Set PHP 7.2 as the default
- Included support for newer OS releases
- Reworked the HTTPS configuration
- Added more automated testing with Redis
- Replaced Postfix with smtp-cli
- Dropped mail services
- Dropped w3tc support