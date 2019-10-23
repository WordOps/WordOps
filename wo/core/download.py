"""WordOps download core classes."""
import os
from requests import get, RequestException

from wo.core.logging import Log


class WODownload():
    """Method to download using urllib"""
    def __init__():
        pass

    def download(self, packages):
        """Download packages, packges must be list in format of
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
                    req = get(url, timeout=15)
                    if req.encoding is None:
                        req.encoding = 'utf-8'
                    out_file.write(req.content)
                Log.info(self, "{0}".format("[" + Log.ENDC + "Done"
                                            + Log.OKBLUE + "]"))
            except RequestException as e:
                Log.debug(self, "[{err}]".format(err=str(e.reason)))
                Log.error(self, "Unable to download file, {0}"
                          .format(filename))
                return False
