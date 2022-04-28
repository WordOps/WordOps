"""WordOps GIT module"""
import os

from sh import ErrorReturnCode, git
from wo.core.logging import Log


class WOGit:
    """Intialization of core variables"""
    def ___init__():
        # TODO method for core variables
        pass

    def add(self, paths, msg="Intializating"):
        """
            Initializes Directory as repository if not already git repo.
            and adds uncommited changes automatically
        """
        for path in paths:
            global git
            wogit = git.bake("-C", "{0}".format(path))
            if os.path.isdir(path):
                if not os.path.isdir(path + "/.git"):
                    try:
                        Log.debug(self, "WOGit: git init at {0}"
                                  .format(path))
                        wogit.init(path)
                    except ErrorReturnCode as e:
                        Log.debug(self, "{0}".format(e))
                        Log.error(self, "Unable to git init at {0}"
                                  .format(path))

                status = wogit.status("-s")
                if len(status.splitlines()) > 0:
                    try:
                        Log.debug(self, "WOGit: git commit at {0}"
                                  .format(path))
                        wogit.add("--all")
                        wogit.commit("-am {0}".format(msg))
                    except ErrorReturnCode as e:
                        Log.debug(self, "{0}".format(e))
                        Log.error(self, "Unable to git commit at {0} "
                                  .format(path))
            else:
                Log.debug(self, "WOGit: Path {0} not present".format(path))

    def checkfilestatus(self, repo, filepath):
        """
            Checks status of file, If its tracked or untracked.
        """
        global git
        wogit = git.bake("-C", "{0}".format(repo))
        status = wogit.status("-s", "{0}".format(filepath))
        if len(status.splitlines()) > 0:
            return True
        else:
            return False

    def rollback(self, paths, msg="Rolling-Back"):
        """
            Rollback last commit to restore previous.
            configuration and commit changes automatically
        """
        for path in paths:
            global git
            wogit = git.bake("-C", "{0}".format(path))
            if os.path.isdir(path):
                if not os.path.isdir(path + "/.git"):
                    Log.error(
                        self, "Unable to find a git repository at {0}"
                              .format(path))
                try:
                    Log.debug(
                        self, "WOGit: git stash --include-untracked at {0}"
                              .format(path))
                    wogit.stash("push", "--include-untracked", "-m {0}"
                                .format(msg))
                except ErrorReturnCode as e:
                    Log.debug(self, "{0}".format(e))
                    Log.error(self, "Unable to git reset at {0} "
                              .format(path))
            else:
                Log.debug(self, "WOGit: Path {0} not present".format(path))

    def clone(self, repo, path, branch='master'):
        """Equivalent to git clone """
        if not os.path.exists('{0}'.format(path)):
            global git
            try:
                git.clone(
                    '{0}'.format(repo),
                    '{0}'.format(path),
                    '--branch={0}'.format(branch),
                    '--depth=1')
            except ErrorReturnCode as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Unable to git clone at {0} "
                          .format(path))
        else:
            Log.debug(self, "WOGit: Path {0} already exist".format(path))
