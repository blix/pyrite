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
        if location:
            self._location = os.path.expanduser(location)
        else:
            self._location = os.getcwd()
        self.refresh()
        
    def _popen(self, args, cwd=None, stdin=False):
        if not cwd:
            cwd = self._location
        if stdin:
            stdin = subprocess.PIPE
        else:
            stdin = None
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
        if not self._is_repo:
            raise RepoError(_('Not under a repo')) 

    def init(self):
        proc = self._popen(('git', 'init'), cwd=self._location)
        if proc.wait():
            raise RepoError(_('Failed to init repo: %s') % proc.stderr.read())

    def del_branch(self, names, force):
    #TODO: need to give better error when branch exists
        self.validate()
        args = ['git', 'branch']
        if force:
            args.append('-D')
        else:
            args.append('-d')
        for n in names: args.append(n)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to delete branch %s: %s') %
                         (names, proc.stderr.read()))

    def rename_branch(self, oldname, newname, force):
    #TODO: need to give better error when branch exists
        self.validate()
        proc = None
        if force:
            proc = self._popen(('git', 'branch', '-M', oldname, newname))
        else:
            proc = self._popen(('git', 'branch', '-m', oldname, newname))
        if proc.wait():
            raise RepoError(_('Failed to rename branch %s to %s: %s') %
                                (oldname, newname, proc.stderr.read()))

    def create_branch(self, name, force, track=True):
        self.validate()
        args = ['git', 'branch']
        if force:
            args.append('-f')
        if track:
            args.append('--track')
        else:
            args.append('--no-track')
        args.append(name)
        proc = self._popen(args)
        if proc.wait():
            if not force and name in self.branches():
                 raise RepoError(_('Could not create branch, branch exists'))
            else:
                raise RepoError(_('Could not create branch: %s') %
                                    proc.stderr.read())

    def checkout(self, commit, is_merge, paths=None):
        self.validate()
        args = ['git', 'checkout']
        if is_merge:
            args.append('-m')
        args.append(commit)
        if paths: args.extend(paths)
        proc = self._popen(args)
        if proc.wait():
             raise RepoError(_('Failed to switch to %s: %s') % (commit,
                                proc.stderr.read()))
        
    def _read_remotes(self):
        self._remotes = []
        if not self.is_repo:
            return
        proc = self._popen(('git', 'branch', '-r'))
        for b in proc.stdout.readlines():
             self._remotes.append(b.strip())
        if proc.wait():
            raise RepoError('Could not get remotes list: %s' %
                            proc.stderr.read())

    def _read_branches(self):
        self._branches = []
        self._current_branch = None
        if not self.is_repo:
            return
        proc = self._popen(('git', 'branch'))
        for b in proc.stdout.readlines():
            tokens = b.split()
            if len(tokens) == 2:
                self._current_branch = tokens[1].strip()
                self._branches.append(self._current_branch)
            else: self._branches.append(tokens[0].strip())
        if proc.wait():
            raise RepoError(_('Could not get branch list: %s') %
                                proc.stderr.read())

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
        if proc.wait():
            raise RepoError(_('Count not find HEAD sham: %s') %
                                proc.stderr.read())
        return proc.stdout.readline().strip()

    def get_commit_info(self, commit):
        self.validate()
        proc = self._popen(('git', 'rev-list', '--max-count=1',
                        '--pretty=format:%an <%ae>%n%s%n%b', commit))
        if proc.wait():
            return None, None, None
        lines = proc.stdout.readlines()
        if len(lines) < 3: return None, None, None
        return ''.join(lines[2:]), lines[1].strip()

    def update_index(self, paths=None):
        self.validate()
        if paths:
            proc = self._popen(('git', 'reset', '--mixed'))
            proc.wait()
        args = ['git', 'add']
        if paths:
            args.append('--')
            args.extend(paths)
        else:
            args.append('-u')
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to update index: %s') %
                                proc.stderr.read())

    def changed_files(self, commit=None):
        self.validate()
        proc = None
        if commit:
            proc = self._popen(('git', 'diff', '--name-status', commit,
                                commit + '^'))
        else:
            proc = self._popen(('git', 'diff-index', '--cached',
                                '--name-status', 'HEAD'))
        for line in proc.stdout.readlines():
            parts = line.split()
            yield parts[0], parts[1]
        if proc.wait():
            raise RepoError(_('Failed to get changed files: %s') %
                                proc.stderr.read())

    def commit(self, use_message, use_author, verify=True, commit=None,
                paths=None):
        self.validate()
        args = ['git', 'commit']
        if not verify:
            args.append('--no-verify')
        if use_author:
            args.append('--author')
            args.append(use_author)
        if commit:
            args.append('-C')
            args.append(commit)
        else:
            args.append('-m')
            args.append(use_message)
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to commit change') + proc.stderr.read())

    def gc(self, prune, aggressive):
        self.validate()
        args = ['git', 'gc']
        if prune:
            args.append('--prune')
        if aggressive:
            args.append('--aggressive')
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to gc: %s') % proc.stderr.read())

    def verify(self, verbose):
        self.validate()
        if verbose:
            proc = self._popen(('git', 'fsck', '--verbose'))
        else:
            proc = self._popen(('git', 'fsck'))
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Verify failed: %s') % proc.stderr.read())

    def add_files(self, is_force, is_verbose, files):
        self.validate()
        args = ['git', 'add']
        if is_force:
            args.append('-f')
        if is_verbose:
            args.append('-v')
        if len(files) > 0:
            args.extend(files)
        else:
            args.append('.')
        proc = self._popen(args, cwd=os.getcwd())
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Could not add files: %s') % proc.stderr.read())
            
    def list_tags(self, pattern):
        self.validate()
        proc = None
        if pattern:
            proc = self._popen(('git', 'tag', '-l', pattern))
        else:
            proc = self._popen(('git', 'tag', '-l'))
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to list tags: %s') % proc.stderr.read())

    def verify_tag(self, tag):
        self.validate()
        proc = self._popen(('git', 'tag', '-v', tag))
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to verify tag: %s') % proc.stderr.read())

    def delete_tags(self, tags):
        self.validate()
        args = ['git', 'tag', '-d']
        args.extend(tags)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to delete tag(s): %s') %
                            proc.stderr.read())

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
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to create tag: %s') % proc.stderr.read())

    def push(self, repo, source, target, force=False, all_branches=False,
                all_tags=False, verbose=False):
        self.validate()
        args = ['git', 'push']
        if force:
            args.append('f')
        if all_branches:
            args.append('--all')
        if all_tags:
            args.append('--tags')
        if verbose:
            args.append('-v')
        args.append(repo)
        if source: 
            arg = source
            if target: arg += ':' + target
            args.append(arg)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to push: %s') % proc.stderr.read())
            
    def pull(self, repo, source, target, force=False, tags="normal",
                commit=True, depth=-1, rebase=False):
        self.validate()
        args = ['git', 'pull']
        if force:
            args.append('-f')
        if tags == 'none':
            args.append('--no-tags')
        elif tags == 'extra':
            args.append('--tags')
        if depth > -1:
            args.append('--depth=%d' % depth)
        if not commit:
            args.append('--no-commit')
        if rebase:
            args.append('--rebase')
        args.append(repo)
        if source: 
            arg = source
            if target: arg += ':' + target
            args.append(arg)

        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to pull: %s') % proc.stderr.read())

    def clone(self, repo, directory, bare=False, checkout=True, depth=-1):
        args = ['git', 'clone']
        if bare:
            args.append('--bare')
        if not checkout:
            args.append('--no-checkout')
        if depth > -1:
            args.append('--depth=%d' % depth)
        args.append(repo)
        if directory:
            args.append(directory)

        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to clone: %s') % proc.stderr.read())
        
    def diff(self, start, end, paths, stat=False, color=False, template=None,
                detect=False, ignorewhite='none'):
        self.validate()
        args = ['git', 'diff', '--stat']
        if not stat:
            args.append('-p')
        if color:
            args.append('--color')
        if detect:
            args.extend(['-B', '-M', '-C'])
        if ignorewhite == 'all':
            args.append('-w')
        elif ignorewhite == 'eol':
            args.append('--ignore-space-at-eol')
        spec = start
        if not start:
            spec = 'HEAD'
        elif end:
            spec = start + '..' + end
        args.append(spec)
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to diff: %s') % proc.stderr.read())

    def list(self):
        self.validate()
        args = ['git', 'ls-files', '-c', '-d', '-m', '-o', '-k', '-t', '-z']
        proc = self._popen(args)
        files = {}
        for item in proc.stdout.read().split('\0'):
            item = item.strip()
            if len(item) < 3:
                continue
            status = item[0]
            filename = item[2:]
            files[filename] = Repo.Status[status]
        proc.wait()
        return files

    def _convert_range(self, first, last):
        first += '^'
        if not last:
            last = 'HEAD'
        first = first + '..' + last
        return first
    
    def get_history(self, first, last, limit, show_patch=False, follow=False,
                    paths=None):
        #TODO: In the future, this should return a list of commit objects
        # The commit objects can have some simple information in them and
        # fetch the rest when asked for it.  For now we will not show the
        # "body" information.
        
        self.validate()
        args = ['git', 'log', '--pretty=format:%H %P\t%an\t%ae\t%ad\t%s']
        if limit > -1:
            args.append('-' + str(limit))
        #if show_patch: args.append('-p')
        # Ignore patch parameter for now to simplfy the parse
        if follow:
            args.append('--follow')
        if first:
            args.append(self._convert_range(first, last))
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            idx = line.find(' ')
            ID = line[:idx]
            idx2 = line.find('\t')
            parents = line[idx+1:idx2].split(' ')
            name, email, date, subj = line[idx2+1:].split('\t')
            yield ID, parents, name, email, date, subj
        if proc.wait():
            raise RepoError(_('Failed to get log: %s') % proc.stderr.read())

    def merge(self, branch, show_summary=False, merge_strategy=None,
                message=None):
        self.validate()
        args = ['git', 'merge']
        if show_summary:
            args.append('--summary')
        if merge_strategy:
            args.append('-s')
            args.append(merge_strategy)
        if message: 
            args.append('-m')
            args.append(message)
        args.append(branch)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to merge: %s') % proc.stderr.read())

    def export_patch(self, first, last, outdir, force=False, numbered=False):
        self.validate()
        args = ['git', 'format-patch']
        if outdir:
            if outdir == '-':
                args.append('--stdout')
            else:
                args.append('-o')
                args.append(outdir)
        if force:
            args.append('-f')
        if numbered:
            args.append('--numbered')
        commits = self._convert_range(first, last)
        args.append(commits)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to export: %s') % proc.stderr.read())

    def import_patch(self, filename, sign=False):
        self.validate()
        dt = os.path.join(self._repo_dir, 'dotest')
        args = ['git', 'am']
        if sign:
            args.append('--signoff')
        args.append(filename)
        proc = self._popen(args, cwd=os.getcwd())        
        if proc.wait():
            try:
                os.remove('.dotest')
            except OSError:
                pass
            return False, proc.stderr.readlines()
        return True, None

