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

import subprocess
import os

class RepoError(Exception):
    """Thrown when repo fails"""

class Repo(object):
    def __init__(self, location=None):
        if location: self._location = os.path.expanduser(location)
        else: self._location = os.getcwd()
        self.refresh()
        
    def _popen(self, args, cwd=None, stdin=False):
        if not cwd: cwd = self._location
        if stdin: stdin = subprocess.PIPE
        else: stdin = None
        return subprocess.Popen(args, cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    stdin=stdin)

    def refresh(self):
        self._branches = None
        self._remotes = None
        proc = self._popen(('git', 'rev-parse', '--git-dir', '--show-cdup'))
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
        proc = self._popen(('git', 'init'), cwd=self._location)
        if proc.wait():
            raise RepoError(_('Failed to init repo'))

    def del_branch(self, names, force):
    #TODO: need to give better error when branch exists
        self.validate()
        args = ['git', 'branch']
        if force: args.append('-D')
        else: args.append('-d')
        for n in names: args.append(n)
        proc = self._popen(args)
        if proc.wait(): raise RepoError(_('Failed to delete branch %s') % names)

    def rename_branch(self, oldname, newname, force):
    #TODO: need to give better error when branch exists
        self.validate()
        proc = None
        if force:
            proc = self._popen(('git', 'branch', '-M', oldname, newname))
        else:
            proc = self._popen(('git', 'branch', '-m', oldname, newname))
        if proc.wait():
            raise RepoError(_('Failed to rename branch %s to %s') % (oldname,
                                newname))

    def create_branch(self, name, force, track=True):
        self.validate()
        args = ['git', 'branch']
        if force: args.append('-f')
        if track: args.append('--track')
        else: args.append('--no-track')
        args.append(name)
        proc = self._popen(args)
        if proc.wait():
            if not force and name in self.branches():
                 raise RepoError(_('Could not create branch, branch exists'))
            else: raise RepoError(_('Could not create branch'))

    def checkout(self, commit, is_merge, paths=None):
        self.validate()
        args = ['git', 'checkout']
        if is_merge: args.append('-m')
        args.append(commit)
        if paths: args.extend(paths)
        proc = self._popen(args)
        if proc.wait(): raise RepoError(_('Failed to switch to %s'), commit)
        
    def _read_remotes(self):
        self._remotes = []
        if not self.is_repo:
            return
        proc = self._popen(('git', 'branch', '-r'))
        if proc.wait(): raise RepoError('Could not get remotes list')
        for b in proc.stdout.readlines():
             self._remotes.append(b.strip())

    def _read_branches(self):
        self._branches = []
        self._current_branch = None
        if not self.is_repo:
            return
        proc = self._popen(('git', 'branch'))
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
        proc = self._popen(('git', 'rev-list', '--max-count=1', 'HEAD'))
        if proc.wait(): raise RepoError(_('Count not find HEAD sha'))
        return proc.stdout.readline().strip()

    def get_commit_info(self, commit):
        self.validate()
        proc = self._popen(('git', 'rev-list', '--max-count=1',
                        '--pretty=format:%an %ae%n%b', commit))
        if proc.wait(): return None, None, None
        lines = proc.stdout.readlines()
        if len(lines) < 3: return None, None, None
        return lines[2:].join('\n'), lines[1].strip()

    def update_index(self):
        self.validate()
        proc = self._popen(('git', 'add', '-u'))
        if proc.wait(): raise RepoError(_('Failed to update index'))

    def changed_files(self):
        self.validate()
        proc = self._popen(('git', 'diff-index', '--name-status', 'HEAD'))
        if proc.wait(): raise RepoError(_('Failed to get changed files'))
        for line in proc.stdout.readlines():
            parts = line.split()
            yield parts[0], parts[1]

    def commit(self, use_message, use_author, verify=True, commit=None):
        self.validate()
        args = ['git', 'commit']
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
        proc = self._popen(args)
        if proc.wait(): raise RepoError(_('Failed to commit change'))

    def gc(self, prune, aggressive):
        self.validate()
        args = ['git', 'gc']
        if prune: args.append('--prune')
        if aggressive: args.append('--aggressive')
        proc = self._popen(args)
        if proc.wait(): raise RepoError(_('Failed to gc'))

    def verify(self, verbose):
        self.validate()
        if verbose:
            proc = self._popen(('git', 'fsck', '--verbose'))
        else:
            proc = self._popen(('git', 'fsck'))
        if proc.wait():
            raise RepoError(_('Verify failed.'))
        return proc.stdout.readlines()

    def add(self, is_force, is_verbose, files):
        self.validate()
        args = ['git', 'add']
        if is_force: args.append('-f')
        if is_verbose: args.append('-v')
        if len(files) > 0: args.extend(files)
        else: args.append('.')
        proc = self._popen(args, cwd=os.getcwd())
        if proc.wait():
            raise RepoError(_('Could not add files'))
        for line in proc.stdout.readlines():
            yield line
            
    def list_tags(self, pattern):
        self.validate()
        proc = None
        if pattern:
            proc = self._popen(('git', 'tag', '-l', pattern))
        else:
            proc = self._popen(('git', 'tag', '-l'))
        if proc.wait():
            raise RepoError(_('Failed to list tags'))
        for line in proc.stdout.readlines():
            yield line

    def verify_tag(self, tag):
        self.validate()
        proc = self._popen(('git', 'tag', '-v', tag))
        if proc.wait():
            raise RepoError(_('Failed to verify tag'))
        for line in proc.stdout.readlines():
            yield line
        for line in proc.stderr.readlines():
            yield line

    def delete_tags(self, tags):
        self.validate()
        args = ['git', 'tag', '-d']
        args.extend(tags)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to delete tag(s)'))
        return proc.stdout.readlines()

    def create_tag(self, name, message, key=None, sign=False):
        self.validate()
        args = ['git', 'tag']
        if message:
            args.append('-m')
            args.append(message)
        if key:
            args.append('-u')
            args.append(key)
        elif sign: args.append('-s')
        args.append(name)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to create tag'))
        return proc.stdout.readlines()

    def push(self, repo, source, target, force=False, all_branches=False,
                all_tags=False, verbose=False):
        self.validate()
        args = ['git', 'push']
        if force: args.append('f')
        if all_branches: args.append('--all')
        if all_tags: args.append('--tags')
        if verbose: args.append('-v')
        args.append(repo)
        if source: 
            arg = source
            if target: arg += ':' + target
            args.append(arg)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to push'))
        for line in proc.stdout.readlines():
            yield line
            
    def pull(self, repo, source, target, force=False, tags="normal",
                commit=True, depth=-1, rebase=False):
        self.validate()
        args = ['git', 'pull']
        if force: args.append('-f')
        if tags == 'none': args.append('--no-tags')
        elif tags == 'extra': args.append('--tags')
        if depth > -1: args.append('--depth=%d' % depth)
        if not commit: args.append('--no-commit')
        if rebase: args.append('--rebase')
        args.append(repo)
        if source: 
            arg = source
            if target: arg += ':' + target
            args.append(arg)
        #print args
        proc = self._popen(args)
        if proc.wait():
            print '\n'.join(proc.stderr.readlines())    
            raise RepoError(_('Failed to pull'))
        for line in proc.stdout.readlines():
            yield line

