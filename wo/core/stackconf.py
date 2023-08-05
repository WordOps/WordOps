import os

from wo.core.logging import Log
from wo.core.template import WOTemplate
from wo.core.variables import WOVar


class WOConf():
    """wo stack configuration utilities"""
    def __init__():
        pass

    def nginxcommon(self):
        """nginx common configuration deployment"""
        wo_php_version = list(WOVar.wo_php_versions.keys())
        ngxcom = '/etc/nginx/common'
        if not os.path.exists(ngxcom):
            os.mkdir(ngxcom)
        for wo_php in wo_php_version:
            Log.debug(self, 'deploying templates for {0}'.format(wo_php))
            data = dict(upstream="{0}".format(wo_php),
                        release=WOVar.wo_version)
            WOTemplate.deploy(self,
                              '{0}/{1}.conf'
                              .format(ngxcom, wo_php),
                              'php.mustache', data)

            WOTemplate.deploy(
                self, '{0}/redis-{1}.conf'.format(ngxcom, wo_php),
                'redis.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpcommon-{1}.conf'.format(ngxcom, wo_php),
                'wpcommon.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpfc-{1}.conf'.format(ngxcom, wo_php),
                'wpfc.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpsc-{1}.conf'.format(ngxcom, wo_php),
                'wpsc.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wprocket-{1}.conf'.format(ngxcom, wo_php),
                'wprocket.mustache', data)

            WOTemplate.deploy(
                self, '{0}/wpce-{1}.conf'.format(ngxcom, wo_php),
                'wpce.mustache', data)
