# [WordOps](https://wordops.org/)

[![Travis Build Status](https://travis-ci.org/WordOps/WordOps.svg)](https://travis-ci.org/WordOps/WordOps)

WordOps (wo) is the essential toolset that eases WordPress site and server administration.

**WordOps currently supports:**

- Ubuntu 14.04, 16.04 & 18.04
- Debian 7, 8 & 9

**Port requirements:**

| Name  | Port Number | Inbound | Outbound  |
|:-----:|:-----------:|:-------:|:---------:|
|SSH    |22           | ✓       |✓          |
|HTTP    |80           | ✓       |✓          |
|HTTPS/SSL    |443           | ✓       |✓          |
|WO Admin    |22222           | ✓       |          |
|GPG Key Server    |11371           |        |✓          |

## Quick start

```bash
wget -qO wo wordops.se/tup && sudo bash wo     # Install WordOps
sudo wo site create example.com --wp     # Install required packages & setup WordPress on example.com
```
## Must read!

WordOps made some fundamental changes:

* We've deprecated the mail stack. Less is more. As an alternative, take a look at [iRedMail](https://www.iredmail.org/) or [Caesonia](https://github.com/vedetta-com/caesonia). And an alternative for Roundcube is [Rainloop](https://www.rainloop.net/).
* Support for w3tc is dropped as a security precaution.
* We are currently migrating the PHP 5.x series to PHP 7.1 and PHP 7.2. We'll offer an easy to use migration script once we are confident enough to unleash this daemon. For now, new sites get installed with PHP 7.2 as the default.

## Update WordOps

#### With one simple command
```
wo update
```

## More site creation commands

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

## Cheatsheet - site creation

|                    |  single site  | 	multisite w/ subdir  |	multisite w/ subdom     |
|--------------------|---------------|-----------------------|--------------------------|
| **NO Cache**       |  --wp         |	--wpsubdir           |	--wpsubdomain           |
| **WP Super Cache** |	--wpsc       |	--wpsubdir --wpsc    |  --wpsubdomain --wpsc    |
| **Nginx cache**    |  --wpfc       |  --wpsubdir --wpfc    |  --wpsubdomain --wpfc    |
| **Redis cache**    |  --wpredis    |  --wpsubdir --wpredis |  --wpsubdomain --wpredis |

## License
[MIT](http://opensource.org/licenses/MIT)