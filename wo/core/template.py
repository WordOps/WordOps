import os

from wo.core.logging import Log


"""
Render Templates
"""


class WOTemplate:
    """WordOps template utilities"""

    def deploy(self, fileconf, template, data, overwrite=True):
        """Deploy template with render()"""
        data = dict(data)
        if (not os.path.isfile('{0}.custom'
                               .format(fileconf))):
            if (not overwrite):
                if not os.path.isfile('{0}'.format(fileconf)):
                    Log.debug(self, 'Writting the configuration to '
                              'file {0}'.format(fileconf))
                    wo_template = open('{0}'.format(fileconf),
                                       encoding='utf-8', mode='w')
                    self.app.render((data), '{0}'.format(template),
                                    out=wo_template)
                    wo_template.close()
            else:
                Log.debug(self, 'Writting the configuration to '
                          'file {0}'.format(fileconf))
                wo_template = open('{0}'.format(fileconf),
                                   encoding='utf-8', mode='w')
                self.app.render((data), '{0}'.format(template),
                                out=wo_template)
                wo_template.close()
        else:
            Log.debug(self, 'Writting the configuration to '
                      'file {0}.orig'.format(fileconf))
            wo_template = open('{0}.orig'.format(fileconf),
                               encoding='utf-8', mode='w')
            self.app.render((data), '{0}'.format(template),
                            out=wo_template)
            wo_template.close()
