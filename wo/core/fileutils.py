"""WordOps file utils core classes."""
import fileinput
import os
import pwd
import shutil
import codecs

from wo.core.logging import Log


class WOFileUtils():
    """Utilities to operate on files"""
    def __init__():
        pass

    def remove(self, filelist):
        """remove files from given path"""
        for file in filelist:
            if os.path.isfile(file):
                Log.info(self, "Removing {0:65}".format(file), end=' ')
                os.remove(file)
                Log.info(self, "{0}".format("[" + Log.ENDC + "Done" +
                                            Log.OKBLUE + "]"))
                Log.debug(self, 'file Removed')
            if os.path.isdir(file):
                try:
                    Log.info(self, "Removing {0:65}".format(file), end=' ')
                    shutil.rmtree(file)
                    Log.info(self, "{0}".format("[" + Log.ENDC + "Done" +
                                                Log.OKBLUE + "]"))
                except shutil.Error as e:
                    Log.debug(self, "{err}".format(err=str(e.reason)))
                    Log.error(self, 'Unable to Remove file ')

    def create_symlink(self, paths, errormsg=''):
        """
        Create symbolic links provided in list with first as source
        and second as destination
        """
        src = paths[0]
        dst = paths[1]
        if not os.path.islink(dst):
            try:
                Log.debug(self, "Creating Symbolic link, Source:{0}, Dest:{1}"
                          .format(src, dst))
                os.symlink(src, dst)
            except OSError as e:
                Log.debug(self, "{0}{1}".format(e.errno, e.strerror))
                Log.error(self, "Unable to create symbolic link ...\n ")
        else:
            Log.debug(self, "Destination: {0} exists".format(dst))

    def remove_symlink(self, filepath):
        """
            Removes symbolic link for the path provided with filepath
        """
        try:
            Log.debug(self, "Removing symbolic link: {0}".format(filepath))
            os.unlink(filepath)
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to reomove symbolic link ...\n")

    def copyfiles(self, src, dest):
        """
        Copies files:
            src : source path
            dest : destination path

            Recursively copy an entire directory tree rooted at src.
            The destination directory, named by dst, must not already exist;
            it will be created as well as missing parent directories.
        """
        try:
            Log.debug(self, "Copying files, Source:{0}, Dest:{1}"
                      .format(src, dest))
            shutil.copytree(src, dest)
        except shutil.Error as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, 'Unable to copy files from {0} to {1}'
                      .format(src, dest))
        except IOError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to copy files from {0} to {1}"
                      .format(src, dest), exit=False)

    def copyfile(self, src, dest):
        """
        Copy file:
            src : source path
            dest : destination path
        """
        try:
            Log.debug(self, "Copying file, Source:{0}, Dest:{1}"
                      .format(src, dest))
            shutil.copy2(src, dest)
        except shutil.Error as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, 'Unable to copy file from {0} to {1}'
                      .format(src, dest))
        except IOError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to copy file from {0} to {1}"
                      .format(src, dest), exit=False)

    def searchreplace(self, fnm, sstr, rstr):
        """
            Search replace strings in file
            fnm : filename
            sstr: search string
            rstr: replace string
        """
        try:
            Log.debug(self, "Doing search and replace, File:{0},"
                      "Source string:{1}, Dest String:{2}"
                      .format(fnm, sstr, rstr))
            for line in fileinput.input(fnm, inplace=True):
                print(line.replace(sstr, rstr), end='')
            fileinput.close()
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to search {0} and replace {1} {2}"
                      .format(fnm, sstr, rstr), exit=False)

    def mvfile(self, src, dst):
        """
            Moves file from source path to destination path
            src : source path
            dst : Destination path
        """
        try:
            Log.debug(self, "Moving file from {0} to {1}".format(src, dst))
            shutil.move(src, dst)
        except Exception as e:
            Log.debug(self, "{err}".format(err=e))
            Log.error(self, 'Unable to move file from {0} to {1}'
                      .format(src, dst))

    def chdir(self, path):
        """
            Change Directory to path specified
            Path : path for destination directory
        """
        try:
            Log.debug(self, "Changing directory to {0}"
                      .format(path))
            os.chdir(path)
        except OSError as e:
            Log.debug(self, "{err}".format(err=e.strerror))
            Log.error(self, 'Unable to Change Directory {0}'.format(path))

    def chown(self, path, user, group, recursive=False):
        """
            Change Owner for files
            change owner for file with path specified
            user: username of owner
            group: group of owner
            recursive: if recursive is True change owner for all
                       files in directory
        """
        userid = pwd.getpwnam(user)[2]
        groupid = pwd.getpwnam(user)[3]
        try:
            Log.debug(self, "Changing ownership of {0}, Userid:{1},Groupid:{2}"
                      .format(path, userid, groupid))
            # Change inside files/directory permissions only if recursive flag
            # is set
            if recursive:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        os.chown(os.path.join(root, d), userid,
                                 groupid)
                    for f in files:
                        os.chown(os.path.join(root, f), userid,
                                 groupid)
            os.chown(path, userid, groupid)
        except shutil.Error as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to change owner : {0}".format(path))
        except Exception as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to change owner : {0} ".format(path))

    def chmod(self, path, perm, recursive=False):
        """
            Changes Permission for files
            path : file path permission to be changed
            perm : permissions to be given
            recursive: change permission recursively for all files
        """
        try:
            Log.debug(self, "Changing permission of {0}, Perm:{1}"
                      .format(path, perm))
            if recursive:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), perm)
                    for f in files:
                        os.chmod(os.path.join(root, f), perm)
            else:
                os.chmod(path, perm)
        except OSError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to change owner : {0}".format(path))

    def wpperm(self, path, harden=False):
        """
            Fix WordPress site permissions
            path : WordPress site path
            harden : set 750/640 instead of 755/644
        """
        userid = pwd.getpwnam('www-data')[2]
        groupid = pwd.getpwnam('www-data')[3]
        try:
            Log.debug(self, "Fixing WordPress permissions of {0}"
                      .format(path))
            if harden:
                dperm = '0o750'
                fperm = '0o640'
            else:
                dperm = '0o755'
                fperm = '0o644'

            for root, dirs, files in os.walk(path):
                for d in dirs:
                    os.chown(os.path.join(root, d), userid,
                             groupid)
                    os.chmod(os.path.join(root, d), dperm)
                for f in files:
                    os.chown(os.path.join(root, d), userid,
                             groupid)
                    os.chmod(os.path.join(root, f), fperm)
        except OSError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to change owner : {0}".format(path))

    def mkdir(self, path):
        """
            create directories.
            path : path for directory to be created
            Similar to `mkdir -p`
        """
        try:
            Log.debug(self, "Creating directories: {0}"
                      .format(path))
            os.makedirs(path)
        except OSError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to create directory {0} ".format(path))

    def isexist(self, path):
        """
            Check if file exist on given path
        """
        try:
            return bool(os.path.exists(path))
        except OSError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to check path {0}".format(path))

    def grep(self, fnm, sstr):
        """
            Searches for string in file and returns the matched line.
        """
        try:
            Log.debug(self, "Finding string {0} to file {1}"
                      .format(sstr, fnm))
            for line in open(fnm, encoding='utf-8'):
                if sstr in line:
                    return line
            return False
        except OSError as e:
            Log.debug(self, "{0}".format(e.strerror))
            Log.error(self, "Unable to Search string {0} in {1}"
                      .format(sstr, fnm))

    def grepcheck(self, fnm, sstr):
        """
            Searches for string in file and returns True or False.
        """
        if os.path.isfile('{0}'.format(fnm)):
            try:
                Log.debug(self, "Finding string {0} to file {1}"
                          .format(sstr, fnm))
                for line in open(fnm, encoding='utf-8'):
                    if sstr in line:
                        return True
                return False
            except OSError as e:
                Log.debug(self, "{0}".format(e.strerror))
                Log.error(self, "Unable to Search string {0} in {1}"
                          .format(sstr, fnm))
        return False

    def rm(self, path):
        """
            Remove files
        """
        Log.debug(self, "Removing {0}".format(path))
        if WOFileUtils.isexist(self, path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except shutil.Error as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Unable to remove directory : {0} "
                          .format(path))
            except OSError as e:
                Log.debug(self, "{0}".format(e))
                Log.error(self, "Unable to remove file  : {0} "
                          .format(path))

    def findBrokenSymlink(self, sympath):
        """
            Find symlinks
        """
        links = []
        broken = []

        for root, dirs, files in os.walk(sympath):
            if root.startswith('./.git'):
                # Ignore the .git directory.
                continue
            for filename in files:
                path = os.path.join(root, filename)
                if os.path.islink(path):
                    target_path = os.readlink(path)
                    # Resolve relative symlinks
                    if not os.path.isabs(target_path):
                        target_path = os.path.join(os.path.dirname(path),
                                                   target_path)
                    if not os.path.exists(target_path):
                        links.append(path)
                        broken.append(path)
                        os.remove(path)
                    else:
                        links.append(path)
                else:
                    # If it's not a symlink we're not interested.
                    continue
        return True

    def textwrite(self, path, content):
        """
            Write content into a file
        """
        Log.debug(self, "Writing content in {0}".format(path))
        try:
            with open("{0}".format(path),
                      encoding='utf-8', mode='w') as final_file:
                final_file.write('{0}'.format(content))
        except IOError as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to write content in {0}".format(path))

    def textappend(self, path, content):
        """
            Append content to a file
        """
        Log.debug(self, "Writing content in {0}".format(path))
        try:
            with open("{0}".format(path),
                      encoding='utf-8', mode='a') as final_file:
                final_file.write('{0}'.format(content))
        except IOError as e:
            Log.debug(self, "{0}".format(e))
            Log.error(self, "Unable to append  content in {0}".format(path))

    def enabledisable(self, path, enable=True):
        """Switch conf from .conf.disabled to .conf or vice-versa"""
        if enable is True:
            Log.debug(self, "Check if disabled file exist")
            if os.path.exists('{0}.disabled'.format(path)):
                Log.debug(self, "Moving .disabled file")
                shutil.move('{0}.disabled'.format(path), path)
                return True
            else:
                return False
        else:
            Log.debug(self, "Check if .conf file exist")
            if os.path.exists(path):
                Log.debug(self, "Moving .conf file")
                shutil.move(path, '{0}.disabled'.format(path))
                return True
            else:
                return False
