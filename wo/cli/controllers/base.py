"""WordOps base controller."""

from cement.core.controller import CementBaseController, expose
from wo.core.variables import WOVariables
VERSION = WOVariables.wo_version

BANNER = """
WordOps v%s
Copyright (c) 2018 WordOps.
""" % VERSION


class WOBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = ("WordOps is the commandline tool to manage your"
                       " websites based on WordPress and Nginx with easy to"
                       " use commands")
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            ]

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()
