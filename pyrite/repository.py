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
        if location: self._location = os.path.expanduser(location)
        else: self._location = os.getcwd()
        self.refresh()

    def refresh(self):
        self._branches = None
        self._remotes = None
        proc = Popen(('git-rev-parse', '--git-dir', '--show-cdup'),
                        cwd=self._location, stdout=PIPE)
        if proc.wait(): self._is_repo = False
        else:
            self._is_repo = True
            self._repo_dir = proc.stdout.readline().strip()
            topdir = proc.stdout.readline().strip()
            if topdir:
                self._location = os.path.join(self._location, topdir)

    def get_repo_dir(self):
        return self._repo_dir

    def is_repo(self):
        return self._is_repo
        
    def validate(self):
        if not self._is_repo: raise RepoError(_('Not under a repo')) 

    def init(self):
        proc = Popen(('git-init'), cwd=self._location)
        if proc.wait():
            raise RepoError(_('Failed to init repo'))

    def del_branch(self, names, force):
    #TODO: need to give better error when branch exists
        self.validate()
        args = ['git-branch']
        if force: args.append('-D')
        else: args.append('-d')
        for n in names: args.append(n)
        proc = Popen(args, cwd=self._location, stderr=PIPE)
        if proc.wait(): raise RepoError(_('Failed to delete branch %s') % names)

    def rename_branch(self, oldname, newname, force):
    #TODO: need to give better error when branch exists
        self.validate()
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
        self.validate()
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
        self.validate()
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
            tokens = b.split()
            if len(tokens) == 2:
                self._current_branch = tokens[1].strip()
                self._branches.append(self._current_branch)
            else: self._branches.append(tokens[0].strip())

    def branches(self):
        self.validate()
        if self._branches:
            return self._branches
        else:
            self._read_branches()
            return self._branches

    def branch(self):
        self.validate()
        if self._branches:
            return self._current_branch
        else:
            self._read_branches()
            return self._current_branch

    def remotes(self):
        self.validate()
        if self._remotes:
            return self._remotes
        else:
            self._read_remotes()
            return self._remotes

    def get_head_sha(self):
        self.validate()
        proc = Popen(('git-rev-list', '--max-count=1', 'HEAD'),
                        cwd=self._location, stdout=PIPE)
        if proc.wait(): raise RepoError(_('Count not find HEAD sha'))
        return proc.stdout.readline().strip()

    def get_commit_info(self, commit):
        self.validate()
        proc = Popen(('git-rev-list', '--max-count=1',
                        '--pretty=format:%an %ae%n%b', commit),
                        cwd=self._location, stdout=PIPE)
        if proc.wait(): return None, None, None
        lines = proc.stdout.readlines()
        if len(lines) < 3: return None, None, None
        return lines[2:].join('\n'), lines[1].strip()

    def update_index(self):
        self.validate()
        proc = Popen(('git-add', '-u'), cwd=self._location)
        if proc.wait(): raise RepoError(_('Failed to update index'))

    def changed_files(self):
        self.validate()
        proc = Popen(('git-diff-index', '--name-status', 'HEAD'),
                        cwd=self._location, stdout=PIPE)
        if proc.wait(): raise RepoError(_('Failed to get changed files'))
        for line in proc.stdout.readlines():
            parts = line.split()
            yield parts[0], parts[1]

    def commit(self, use_message, use_author, verify=True, commit=None):
        self.validate()
        args = ['git-commit']
        if not verify: args.append('--no-verify')
        if use_author:
            args.append('--author')
            args.append(use_author)
        if commit:
            args.append('-C')
            args.append(commit)
        else:
            args.append('-m')
            args.append(use_message)
        proc = Popen(args, cwd=self._location)
        if proc.wait(): raise RepoError(_('Failed to commit change'))

