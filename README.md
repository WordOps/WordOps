<h1 align="center" style="font-size:54px;"><a href="https://wordops.org">
  WordOps</a>
  <br>
</h1>

<h2 align="center">An essential toolset that eases WordPress site and server administration</h2>

<p align="center">
<a href="https://travis-ci.org/WordOps/WordOps"><img src="https://travis-ci.org/WordOps/WordOps.svg?branch=master" alt="build"></a>
<img src="https://img.shields.io/github/license/wordops/wordops.svg" alt="MIT">
<img src="https://img.shields.io/github/last-commit/wordops/wordops.svg" alt="Commits">

</p>



<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#usage">Usage</a> •
  <a href="#cheatsheet">Cheatsheet</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

---

## Key Features

- Easy Migration from EasyEngine v3 (migration script development in progress)
- Automated WordPress, Nginx, PHP, MySQL & Redis installation
- Optimized Nginx configuration with multiple cache backends support
- Let's Encrypt SSL certificates

## Requirements

### Operating System

- Ubuntu : 16.04 LTS (Xenial) - 18.04 LTS (Bionic)
- Debian :  8 (Jessie) - 9 (Stretch)

### Ports requirements

- SSH (22 or custom)
- HTTP & HTTPS (80 & 443)
- WO Admin (22222)
- GPG key Server (11371 outbound)

## Getting Started

```bash
wget -qO wo wordops.se/tup && sudo bash wo     # Install WordOps
sudo wo site create example.com --wp     # Install required packages & setup WordPress on example.com
```

## Must read

WordOps made some fundamental changes:

- We've deprecated the mail stack. Less is more. As an alternative, take a look at [iRedMail](https://www.iredmail.org/) or [Caesonia](https://github.com/vedetta-com/caesonia). And an alternative for Roundcube is [Rainloop](https://www.rainloop.net/).
- Support for w3tc is dropped as a security precaution.
- PHP 5.6 has been replaced by PHP 7.2 and PHP 7.0 will be replaced by PHP 7.3.

We will not overwrite previous php versions Nginx upstreams to avoid issues during the migration from EEv3. A step by step guide will be published soon to explain how to fully migrate from EasyEngine v3 to WordOps

## Usage

### Standard WordPress sites

```bash
wo site create example.com --wp                  # install wordpress without any page caching
wo site create example.com --wpsc                # install wordpress with wp-super-cache plugin
wo site create example.com --wpfc                # install wordpress + nginx fastcgi_cache
wo site create example.com --wpredis             # install wordpress + nginx redis_cache
```

### WordPress multsite with subdirectory

```bash
wo site create example.com --wpsubdir            # install wpmu-subdirectory without any page caching
wo site create example.com --wpsubdir --wpsc     # install wpmu-subdirectory with wp-super-cache plugin
wo site create example.com --wpsubdir --wpfc     # install wpmu-subdirectory + nginx fastcgi_cache
wo site create example.com --wpsubdir --wpredis  # install wpmu-subdirectory + nginx redis_cache
```

### WordPress multsite with subdomain

```bash
wo site create example.com --wpsubdomain            # install wpmu-subdomain without any page caching
wo site create example.com --wpsubdomain --wpsc     # install wpmu-subdomain with wp-super-cache plugin
wo site create example.com --wpsubdomain --wpfc     # install wpmu-subdomain + nginx fastcgi_cache
wo site create example.com --wpsubdomain --wpredis  # install wpmu-subdomain + nginx redis_cache
```

### Non-WordPress sites

```bash
wo site create example.com --html     # create example.com for static/html sites
wo site create example.com --php      # create example.com with php support
wo site create example.com --mysql    # create example.com with php & mysql support
```

### HHVM enabled sites

```bash
wo site create example.com --wp --hhvm           # create example.com WordPress site with HHVM support
wo site create example.com --php --hhvm          # create example.com php site with HHVM support
```

## Cheatsheet

|                    |  single site  | 	multisite w/ subdir  |	multisite w/ subdom     |
|--------------------|---------------|-----------------------|--------------------------|
| **NO Cache**       |  --wp         |	--wpsubdir           |	--wpsubdomain           |
| **WP Super Cache** |	--wpsc       |	--wpsubdir --wpsc    |  --wpsubdomain --wpsc    |
| **Nginx fastcgi_cache**    |  --wpfc       |  --wpsubdir --wpfc    |  --wpsubdomain --wpfc    |
| **Redis cache**    |  --wpredis    |  --wpsubdir --wpredis |  --wpsubdomain --wpredis |


## Update WordOps

```bash
wo update
```

## Credits

- [EasyEngine](https://github.com/easyengine/easyengine)

## License

- [MIT](http://opensource.org/licenses/MIT) © [WordOps](https://wordops.org)