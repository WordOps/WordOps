<p align="center"><img src="https://raw.githubusercontent.com/WordOps/WordOps/master/logo.png" width="400" alt="Wordops" /><a href="https://wordops.net">

  <br>
</p>

<h2 align="center">An essential toolset that eases WordPress site and server administration</h2>

<p align="center">
<img src="https://docs.wordops.net/images/wordops-intro.gif" width="800" alt="WordOps" />
</p>

<p align="center">
<a href="https://github.com/WordOps/WordOps/actions" target="_blank"><img src="https://github.com/WordOps/WordOps/workflows/CI/badge.svg?branch=master" alt="CI"></a>
<img src="https://img.shields.io/github/license/wordops/wordops.svg?cacheSeconds=86400" alt="MIT">
<img src="https://img.shields.io/github/last-commit/wordops/wordops.svg?cacheSeconds=86400" alt="Commits">
<img alt="GitHub release" src="https://img.shields.io/github/release/WordOps/WordOps.svg">
<br><a href="https://pypi.org/project/wordops/" target="_blank"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/wordops.svg?cacheSeconds=86400"></a>
<a href="https://twitter.com/WordOps_" target="_blank"><img src="https://img.shields.io/badge/twitter-%40WordOps__-blue.svg?style=flat&logo=twitter&cacheSeconds=86400" alt="Badge Twitter" /></a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#usage">Usage</a> •
  <a href="https://github.com/WordOps/WordOps/projects">RoadMap</a> •
  <a href="https://github.com/WordOps/WordOps/blob/master/CHANGELOG.md">Changelog</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>
<p align="center">
<a href="https://wordops.net" target="_blank"> WordOps.net</a> •
<a href="https://docs.wordops.net" target="_blank">Documentation</a> •
<a href="https://community.wordops.net" target="_blank">Community Forum</a> •
<a href="https://demo.wordops.eu" target="_blank">Dashboard demo</a>
</p>

---

## Key Features

-   **Easy to install** : One step automated installer with migration from EasyEngine v3 support
-   **Fast deployment** : Fast and automated WordPress, Nginx, PHP, MySQL & Redis installation
-   **Custom Nginx build** : Nginx 1.26.1 - TLS v1.3 HTTP/3 QUIC & Brotli support
-   **Up-to-date** : PHP 7.4, 8.0, 8.1, 8.2 & 8.3 - MariaDB 11.4 LTS & Redis 7.0
-   **Secured** : Hardened WordPress security with strict Nginx location directives
-   **Powerful** : Optimized Nginx configurations with multiple cache backends support
-   **SSL** : Domain, Subdomain & Wildcard Let's Encrypt SSL certificates with DNS API support
-   **Modern** : Strong ciphers_suite, modern TLS protocols and HSTS support (Grade A+ on [ssllabs](https://www.ssllabs.com/ssltest/analyze.html?d=demo.wordops.eu&latest))
-   **Monitoring** : Live Nginx vhost traffic with ngx_vts_module and server monitoring with Netdata
-   **User Friendly** : WordOps dashboard with server status/monitoring and tools ([demo](https://demo.wordops.eu))
-   **Release cycle** : WordOps stable releases are published in June and December.

---

## Requirements

### Operating System

#### Recommended

-   Ubuntu 24.04 LTS (Noble)
-   Ubuntu 22.04 LTS (Jammy)
-   Ubuntu 20.04 LTS (Focal)

#### Also compatible

-   Debian 10 (Buster)
-   Debian 11 (Bullseye)
-   Debian 12 (Bookworm)

#### For testing purpose only

-   Raspbian 10 (Buster)
-   Raspbian 11 (Bullseye)

## Getting Started

```bash
wget -qO wo wops.cc && sudo bash wo      # Install WordOps
sudo wo site create example.com --wp     # Install required packages & setup WordPress on example.com
```

Detailed Getting Started guide with additional installation methods can be found in [the documentation](https://docs.wordops.net/getting-started/installation-guide/).

## Usage

### Standard WordPress sites

```bash
wo site create example.com --wp                # install wordpress with [Current supported PHP release](https://endoflife.date/php) without any page caching
wo site create example.com --wp  --php83       # install wordpress with PHP 8.3  without any page caching
wo site create example.com --wpfc              # install wordpress + nginx fastcgi_cache
wo site create example.com --wpredis           # install wordpress + nginx redis_cache
wo site create example.com --wprocket          # install wordpress with WP-Rocket plugin
wo site create example.com --wpce              # install wordpress with Cache-enabler plugin
wo site create example.com --wpsc              # install wordpress with wp-super-cache plugin
```

### WordPress multisite with subdirectory

```bash
wo site create example.com --wpsubdir            # install wpmu-subdirectory without any page caching
wo site create example.com --wpsubdir --wpsc     # install wpmu-subdirectory with wp-super-cache plugin
wo site create example.com --wpsubdir --wpfc     # install wpmu-subdirectory + nginx fastcgi_cache
wo site create example.com --wpsubdir --wpredis  # install wpmu-subdirectory + nginx redis_cache
wo site create example.com --wpsubdir --wprocket # install wpmu-subdirectory + WP-Rocket plugin
wo site create example.com --wpsubdir --wpce     # install wpmu-subdirectory + Cache-Enabler plugin
```

### WordPress multisite with subdomain

```bash
wo site create example.com --wpsubdomain            # install wpmu-subdomain without any page caching
wo site create example.com --wpsubdomain --wpsc     # install wpmu-subdomain with wp-super-cache plugin
wo site create example.com --wpsubdomain --wpfc     # install wpmu-subdomain + nginx fastcgi_cache
wo site create example.com --wpsubdomain --wpredis  # install wpmu-subdomain + nginx redis_cache
wo site create example.com --wpsubdomain --wprocket # install wpmu-subdomain + WP-Rocket plugin
wo site create example.com --wpsubdomain --wpce     # install wpmu-subdomain + Cache-Enabler plugin
```

### Non-WordPress sites

```bash
wo site create example.com --html     # create example.com for static/html sites
wo site create example.com --php      # create example.com with [Current supported PHP release](https://endoflife.date/php)
wo site create example.com --php80      # create example.com with php 8.0 support
wo site create example.com --php81      # create example.com with php 8.1 support
wo site create example.com --php82      # create example.com with php 8.2 support
wo site create example.com --mysql    # create example.com with php 8.2 & mysql support
wo site create example.com --mysql --php83   # create example.com with php 8.3 & mysql support
wo site create example.com --proxy=127.0.0.1:3000 #  create example.com with nginx as reverse-proxy
```

### Switch between PHP versions

```bash
wo site update example.com --php74 # switch to PHP 7.4
wo site update example.com --php80 # switch to PHP 8.0
wo site update example.com --php81 # switch to PHP 8.1
wo site update example.com --php82 # switch to PHP 8.2
wo site update example.com --php83 # switch to PHP 8.3
```

### Sites secured with Let's Encrypt

```bash
wo site create example.com --wp -le #  wordpress & letsencrypt
wo site create sub.example.com --wp -le # wordpress & letsencrypt subdomain
wo site create example.com --wp --letsencrypt --hsts # wordpress & letsencrypt with HSTS
wo site create example.com --wp -le=wildcard --dns=dns_cf # wordpress & wildcard SSL certificate with Cloudflare DNS API
```

## Update WordOps

```bash
wo update
```

## Support

If you feel there is a bug directly related to WordOps, or if you want to suggest new features for WordOps, feel free to open an issue.
For any other questions about WordOps or if you need support, please use the [Community Forum](https://community.wordops.net/).

# Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.
There is no need to be a developer or a system administrator to contribute to WordOps project. You can still contribute by helping us to improve [WordOps documentation](https://github.com/WordOps/docs.wordops.net).
Otherwise, you can still contribute to the project by making a donation on [Ko-Fi](https://ko-fi.com/wordops).

## Credits

-   Source : [EasyEngine](https://github.com/easyengine/easyengine)

Apps & Tools shipped with WordOps :

-   [Acme.sh](https://github.com/Neilpang/acme.sh)
-   [WP-CLI](https://github.com/wp-cli/wp-cli)
-   [Netdata](https://github.com/netdata/netdata)
-   [phpMyAdmin](https://www.phpmyadmin.net/)
-   [Composer](https://github.com/composer/composer)
-   [Adminer](https://www.adminer.org/)
-   [phpRedisAdmin](https://github.com/erikdubbelboer/phpRedisAdmin)
-   [opcacheGUI](https://github.com/amnuts/opcache-gui)
-   [eXtplorer](https://github.com/soerennb/extplorer)
-   [Webgrind](https://github.com/jokkedk/webgrind)
-   [MySQLTuner](https://github.com/major/MySQLTuner-perl)
-   [Fail2Ban](https://github.com/fail2ban/fail2ban)
-   [ClamAV](https://github.com/Cisco-Talos/clamav-devel)
-   [cheat.sh](https://github.com/chubin/cheat.sh)
-   [ProFTPd](https://github.com/proftpd/proftpd)
-   [Nginx-ultimate-bad-bot-blocker](https://github.com/mitchellkrogza/nginx-ultimate-bad-bot-blocker/)
-   [Nanorc](https://github.com/scopatz/nanorc)

Third-party debian packages shipped with WordOps :

-   [Nginx-wo by WordOps](https://build.opensuse.org/package/show/home:virtubox:WordOps/nginx)
-   [PHP by Ondřej Surý](https://launchpad.net/~ondrej/+archive/ubuntu/php)
-   [Redis](https://redis.io/docs/getting-started/installation/install-redis-on-linux/)

WordPress Cache Plugins supported by WordOps :

-   [Nginx-helper](https://github.com/rtCamp/nginx-helper)
-   [Cache-Enabler](https://github.com/keycdn/cache-enabler)
-   [Redis-object-cache](https://github.com/tillkruss/redis-cache)
-   [WP-Super-Cache](https://github.com/Automattic/wp-super-cache)
-   [WP-Rocket](https://github.com/wp-media/wp-rocket)

## License

-   [MIT](http://opensource.org/licenses/MIT) © [WordOps](https://wordops.net)
