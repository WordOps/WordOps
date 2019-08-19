from wo.core.logging import Log
import os

"""
Render Templates
"""


class WOTemplate():
    def tmpl_render(self, fileconf, template, data, overwrite=True):
        if (not overwrite):
            if not os.path.isfile('{0}'.format(fileconf)):
                data = dict(data)
                Log.debug(self, 'Writting the configuration to '
                          'file {0}'.format(fileconf))
                wo_template = open('{0}'.format(fileconf),
                                   encoding='utf-8', mode='w')
                self.app.render((data), '{0}'.format(template),
                                out=wo_template)
                wo_template.close()
        else:
            if (not os.path.isfile('{0}.custom'
                                   .format(fileconf))):
                data = dict(data)
                Log.debug(self, 'Writting the configuration to '
                          'file {0}'.format(fileconf))
                wo_template = open('{0}'.format(fileconf),
                                   encoding='utf-8', mode='w')
                self.app.render((data), '{0}'.format(template),
                                out=wo_template)
                wo_template.close()
