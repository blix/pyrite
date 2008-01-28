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

class RepoError(Exception):
    """Thrown when repo fails"""

class Repo(object):
    def __init__(self, location=None):
        if location: self._location = location
        else: self._location = os.getcwd()
        self.refresh()

    def refresh(self):
        self._branches = None
        self._remotes = None
        proc = Popen(('git-rev-parse', '--git-dir'), cwd=self._location,
                        stdout=PIPE)
        if proc.wait(): self._is_repo = False
        else:
            self._is_repo = True
            self._repo_dir = proc.stdout.readline()

    def get_repo_dir(self):
        return self._repo_dir

    def is_repo(self):
        return self._is_repo

    def init(self):
        proc = Popen(('git-init'), cwd=self._location)
        if proc.wait():
            raise RepoError(_('Failed to init repo'))

    def del_branch(self, names, force):
    #TODO: need to give better error when branch exists
        args = ['git-branch']
        if force: args.append('-D')
        else: args.append('-d')
        for n in names: args.append(n)
        proc = Popen(args, cwd=self._location, stderr=PIPE)
        if proc.wait(): raise RepoError(_('Failed to delete branch %s') % names)

    def rename_branch(self, oldname, newname, force):
    #TODO: need to give better error when branch exists
        proc = None
        if force:
            proc = Popen(('git-branch', '-M', oldname, newname),
                            cwd=self._location, stderr=PIPE)
        else:
            proc = Popen(('git-branch', '-m', oldname, newname),
                            cwd=self._location, stderr=PIPE)
        if proc.wait():
            raise RepoError(_('Failed to rename branch %s to %s') % (oldname,
                                newname))

    def create_branch(self, name, force, track=True):
        args = ['git-branch']
        if force: args.append('-f')
        if track: args.append('--track')
        else: args.append('--no-track')
        args.append(name)
        proc = Popen(args, cwd=self._location)
        if proc.wait():
            if not force and name in self.branches():
                 raise RepoError(_('Could not create branch, branch exists'))
            else: raise RepoError(_('Could not create branch'))

    def checkout(self, commit, is_merge, paths=None):
        args = ['git-checkout']
        if is_merge: args.append('-m')
        args.append(commit)
        if paths: args.extend(paths)
        proc = Popen(args, cwd=self._location, stderr=PIPE)
        if proc.wait(): raise RepoError(_('Failed to switch to %s'), commit)
        
    def _read_remotes(self):
        self._remotes = []
        if not self.is_repo:
            return
        proc = Popen(('git-branch', '-r'), cwd=self._location, stdout=PIPE)
        if proc.wait(): raise RepoError('Could not get remotes list')
        for b in proc.stdout.readlines():
             self._remotes.append(b.strip())

    def _read_branches(self):
        self._branches = []
        self._current_branch = None
        if not self.is_repo:
            return
        proc = Popen(('git-branch'), cwd=self._location, stdout=PIPE)
        if proc.wait(): raise RepoError('Could not get branch list')
        for b in proc.stdout.readlines():
            tokens = b.split(' ')
            if len(tokens) == 2:
                self._current_branch = tokens[1].strip()
                self._branches.append(self._current_branch)
            else: self._branches.append(tokens[2].strip())

    def branches(self):
        if self._branches:
            return self._branches
        else:
            self._read_branches()
            return self._branches
            
    def branch(self):
        if self._branches:
            return self._current_branch
        else:
            self._read_branches()
            return self._current_branch

    def remotes(self):
        if self._remotes:
            return self._remotes
        else:
            self._read_remotes()
            return self._remotes

