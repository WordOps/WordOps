import os
import time

from cement.core.controller import CementBaseController, expose
from requests import RequestException, get, json
from wo.core.download import WODownload
from wo.core.logging import Log
from wo.core.variables import WOVar


def wo_update_hook(app):
    pass


class WOUpdateController(CementBaseController):
    class Meta:
        label = 'wo_update'
        stacked_on = 'base'
        aliases = ['update']
        aliases_only = True
        stacked_type = 'nested'
        description = ('update WordOps to latest version')
        arguments = [
            (['--force'],
             dict(help='Force WordOps update', action='store_true')),
            (['--beta'],
             dict(help='Update WordOps to latest mainline release '
                  '(same than --mainline)',
                  action='store_true')),
            (['--mainline'],
             dict(help='Update WordOps to latest mainline release',
                  action='store_true')),
            (['--branch'],
                dict(help="Update WordOps from a specific repository branch ",
                     action='store' or 'store_const',
                     const='develop', nargs='?')),
            (['--travis'],
             dict(help='Argument used only for WordOps development',
                  action='store_true')),
        ]
        usage = "wo update [options]"

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        filename = "woupdate" + time.strftime("%Y%m%d-%H%M%S")

        wo_current = WOVar.wo_version
        try:
            wo_github_latest = get(
                'https://api.github.com/repos/WordOps/WordOps/releases/latest',
                timeout=(5, 30)).json()
        except RequestException:
            Log.debug(
                self, "Request to GitHub API failed. "
                "Switching to Gitea instance")
            wo_github_latest = get(
                'https://git.virtubox.net/api/v1/repos/virtubox/WordOps/tags',
                timeout=(5, 30)).json()
            wo_latest = wo_github_latest[0]["name"]
        else:
            wo_latest = wo_github_latest["tag_name"]

        install_args = ""
        if pargs.mainline or pargs.beta:
            wo_branch = "mainline"
        elif pargs.branch:
            wo_branch = pargs.branch
        else:
            wo_branch = "master"
        if pargs.force:
            install_args = install_args + "--force "
        else:
            if not pargs.travis:
                if wo_current == wo_latest:
                    Log.error(
                        self, "WordOps {0} is already installed"
                        .format(wo_latest))

        if not os.path.isdir('/var/lib/wo/tmp'):
            os.makedirs('/var/lib/wo/tmp')
        WODownload.download(self, [["https://raw.githubusercontent.com/"
                                    "WordOps/WordOps/{0}/install"
                                    .format(wo_branch),
                                    "/var/lib/wo/tmp/{0}".format(filename),
                                    "update script"]])

        if pargs.travis:
            if os.path.isfile('install'):
                try:
                    Log.info(self, "updating WordOps, please wait...")
                    os.system("/bin/bash install --travis "
                              "--force")
                except OSError as e:
                    Log.debug(self, str(e))
                    Log.error(self, "WordOps update failed !")
        else:
            try:
                Log.info(self, "updating WordOps, please wait...")
                os.system("/bin/bash /var/lib/wo/tmp/{0} "
                          "-b {1} {2}".format(filename,
                                              wo_branch, install_args))
            except OSError as e:
                Log.debug(self, str(e))
                Log.error(self, "WordOps update failed !")

        os.remove("/var/lib/wo/tmp/{0}".format(filename))


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    app.handler.register(WOUpdateController)
    # register a hook (function) to run after arguments are parsed.
    app.hook.register('post_argument_parsing', wo_update_hook)
