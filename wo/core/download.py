"""WordOps download core classes."""
import os
import requests

from wo.core.logging import Log


class WODownload():
    """Method to download using urllib"""
    def __init__():
        pass

    def download(self, packages):
        """Download packages, packages must be list in format of
        [url, path, package name]"""
        for package in packages:
            url = package[0]
            filename = package[1]
            pkg_name = package[2]
            try:
                directory = os.path.dirname(filename)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                Log.info(self, "Downloading {0:20}".format(pkg_name), end=' ')
                with open(filename, "wb") as out_file:
                    req = requests.get(url, timeout=(5, 30))
                    if req.encoding is None:
                        req.encoding = 'utf-8'
                    out_file.write(req.content)
                Log.info(self, "{0}".format("[" + Log.ENDC + "Done" +
                                            Log.OKBLUE + "]"))
            except requests.RequestException as e:
                Log.debug(self, "[{err}]".format(err=str(e.reason)))
                Log.error(self, "Unable to download file, {0}"
                          .format(filename))
                return False
        return 0

    def latest_release(self, repository, name=False):
        """Get the latest release number of a GitHub repository.\n
        repository format should be: \"user/repo\""""
        try:
            req = requests.get(
                'https://api.github.com/repos/{0}/releases/latest'
                .format(repository),
                timeout=(5, 30))
            github_json = req.json()
        except requests.RequestException as e:
            Log.debug(self, str(e))
            Log.error(self, "Unable to query GitHub API")
        if name:
            return github_json["name"]
        else:
            return github_json["tag_name"]

    def pma_release(self):
        """Get the latest phpmyadmin release number from a json file"""
        try:
            req = requests.get(
                'https://www.phpmyadmin.net/home_page/version.json',
                timeout=(5, 30))
            pma_json = req.json()
        except requests.RequestException as e:
            Log.debug(self, str(e))
            Log.error(self, "Unable to query phpmyadmin API")
        return pma_json["version"]
