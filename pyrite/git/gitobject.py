#Copyright 2008 Govind Salinas <blix@sophiasuchtig.com>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from subprocess import Popen, PIPE
import os

class GitError(Exception):
    """Thrown when git command fails"""

class GitObject(object):
    def __init__(self, settings=None, io=None, location=None, obj=None):
        if obj:
            self._location = obj._location
            self._settings = obj._settings
            self._io = obj._io
            self._git_dir = obj._git_dir
            self._is_in_repo = not not self._git_dir
            self._work_tree = obj._work_tree
        else:
            if location:
                self._location = os.path.expanduser(location)
            else:
                self._location = os.getcwd()
            self._io = io
            self._settings = settings
            self.refresh()
        self._debug_commands = os.environ.get('PYT_DBG_CMD', None)

    def set_settings(self, settings):
        self._settings = settings

    @property
    def settings(self):
        return self._settings

    def refresh(self):
        self._git_dir = None
        self._is_in_repo = not not self.get_git_dir()
        self._work_tree = None

    def _popen(self, args, cwd=None, stdin=False, stdout=PIPE, stderr=PIPE):
        if not cwd:
            cwd = self._location
        if stdin:
            stdin = PIPE
        else:
            stdin = None
        if os.environ.get('PYTDBG'):
            if not self._io or self._io == True:
                print args
            else:
                self._io.info(str(args))
        return Popen(args, cwd=cwd, stdout=stdout, stderr=stderr,
                     stdin=stdin)

    def _is_git_dir(self, d):
        """ This is taken from the git setup.c:is_git_directory
            function."""

        if os.path.isdir(d) and \
                os.path.isdir(os.path.join(d, 'objects')) and \
                os.path.isdir(os.path.join(d, 'refs')):
            headref = os.path.join(d, 'HEAD')
            return os.path.isfile(headref) or \
                    (os.path.islink(headref) and
                    os.readlink(headref).startswith('refs'))
        return False

    def get_work_tree(self):
        if not self._work_tree:
            self._work_tree = os.getenv('GIT_WORK_TREE')
            if not self._work_tree or not os.path.isdir(self._work_tree):
                self._work_tree = os.path.abspath(
                                    os.path.join(self._git_dir, '..'))
        return self._work_tree

    def get_git_dir(self):
        if not self._git_dir:
            self._git_dir = os.getenv('GIT_DIR')
            if self._git_dir and self._is_git_dir(self._git_dir):
                return self._git_dir
            curpath = self._location
            while curpath:
                if self._is_git_dir(curpath):
                    self._git_dir = curpath
                    self._is_bare = True
                    break
                gitpath = os.path.join(curpath, '.git')
                if self._is_git_dir(gitpath):
                    self._git_dir = gitpath
                    self._is_bare = False
                    break
                curpath, dummy = os.path.split(curpath)
                if not dummy:
                    break
        return self._git_dir

    def is_bare(self):
        return self._is_bare

    def validate(self):
        if not self._is_in_repo:
            raise GitError(_('Not under a repo'))

    def is_in_repo(self):
        return self._is_in_repo
