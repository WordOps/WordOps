"""WordOps packages repository operations"""
import os

from wo.core.logging import Log
from wo.core.shellexec import WOShellExec
from wo.core.variables import WOVar


class WORepo():
    """Manage Repositories"""

    def __init__(self):
        """Initialize """
        pass

    def add(self, repo_url=None, ppa=None):
        """
        This function used to add apt repositories and or ppa's
        If repo_url is provided adds repo file to
            /etc/apt/sources.list.d/
        If ppa is provided add apt-repository using
            add-apt-repository
        command.
        """

        if repo_url is not None:
            repo_file_path = ("/etc/apt/sources.list.d/" +
                              WOVar().wo_repo_file)
            try:
                if not os.path.isfile(repo_file_path):
                    with open(repo_file_path,
                              encoding='utf-8', mode='a') as repofile:
                        repofile.write(repo_url)
                        repofile.write('\n')
                        repofile.close()
                elif repo_url not in open(repo_file_path,
                                          encoding='utf-8').read():
                    with open(repo_file_path,
                              encoding='utf-8', mode='a') as repofile:
                        repofile.write(repo_url)
                        repofile.write('\n')
                        repofile.close()
                return True
            except IOError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "File I/O error.")
            except Exception as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Unable to add repo")
        if ppa is not None:
            ppa_split = ppa.split(':')[1]
            ppa_author = ppa_split.split('/')[0]
            Log.debug(self, "ppa_author = {0}".format(ppa_author))
            ppa_package = ppa_split.split('/')[1]
            Log.debug(self, "ppa_package = {0}".format(ppa_package))
            if os.path.exists(
                '/etc/apt/sources.list.d/{0}-ubuntu-{1}-{2}.list'
                    .format(ppa_author,
                            ppa_package, WOVar.wo_platform_codename)):
                Log.debug(self, "ppa already added")
                return True
            if WOShellExec.cmd_exec(
                    self, "LC_ALL=C.UTF-8 add-apt-repository -y '{ppa_name}'"
                    .format(ppa_name=ppa)):
                Log.debug(self, "Added PPA {0}".format(ppa))
                return True
        return False

    def remove(self, ppa=None, repo_url=None):
        """
        This function used to remove ppa's
        If ppa is provided adds repo file to
            /etc/apt/sources.list.d/
        command.
        """
        if ppa:
            WOShellExec.cmd_exec(self, "add-apt-repository -y "
                                 "--remove '{ppa_name}'"
                                 .format(ppa_name=ppa))
        elif repo_url:
            repo_file_path = ("/etc/apt/sources.list.d/" +
                              WOVar().wo_repo_file)

            try:
                repofile = open(repo_file_path, "w+", encoding='utf-8')
                repofile.write(repofile.read().replace(repo_url, ""))
                repofile.close()
            except IOError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "File I/O error.")
            except Exception as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Unable to remove repo")

    def add_key(self, keyid, keyserver=None):
        """
        This function adds imports repository keys from keyserver.
        default keyserver is hkp://keyserver.ubuntu.com
        user can provide other keyserver with keyserver="hkp://xyz"
        """
        try:
            WOShellExec.cmd_exec(
                self, "apt-key adv --keyserver {serv}"
                .format(serv=(keyserver or
                              "hkp://keyserver.ubuntu.com")) +
                " --recv-keys {key}".format(key=keyid))
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to import repo key")

    def download_key(self, key_url):
        """
        This function download gpg keys and add import them with apt-key add"
        """
        try:
            WOShellExec.cmd_exec(
                self, "curl -sL {0} ".format(key_url) +
                "| apt-key add -")
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to import repo keys")
