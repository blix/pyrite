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
import gzip

class RepoError(Exception):
    """Thrown when repo fails"""

class Repo(object):
    _status = {
        '?': 'untracked',
        'H': 'uptodate',
        'C': 'modified',
        'M': 'modified',
        'D': 'deleted',
        'A': 'added'
    }

    AUTHOR = 0
    AUTHOR_EMAIL = 1
    AUTHOR_DATE = 2
    COMMITER = 3
    COMMITER_EMAIL = 4
    COMMIT_DATE = 5
    SUBJECT = 6
    ID = 7
    PARENTS = 8
    BODY = 9
    DIFFSTAT = 10
    PATCH = 11
    FILES = 12

    _last_property = FILES

    _properties = {
        AUTHOR: '%an',
        AUTHOR_EMAIL: '%ae',
        AUTHOR_DATE: '%at',
        COMMITER: '%cn',
        COMMITER_EMAIL: '%ce',
        COMMIT_DATE: '%ct',
        SUBJECT: '%s',
        ID: '%H',
        PARENTS: '%P',
        BODY: '%b',
        DIFFSTAT: '--stat',
        PATCH: '-p',
        FILES: '--name-status'
    }

    def __init__(self, location=None):
        if location:
            self._location = os.path.expanduser(location)
        else:
            self._location = os.getcwd()
        self.refresh()

    def _popen(self, args, cwd=None, stdin=False,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE):
        if not cwd:
            cwd = self._location
        if stdin:
            stdin = subprocess.PIPE
        else:
            stdin = None
        return subprocess.Popen(args, cwd=cwd,
                                    stdout=stdout,
                                    stderr=stderr,
                                    stdin=stdin)

    def refresh(self):
        self._branches = None
        self._remotes = None
        self._repo_dir = None
        self._is_repo = not not self.get_repo_dir()
        self._tags = None

    def _is_git_dir(self, d):
        if os.path.isdir(d) and os.path.isdir(os.path.join(d, 'objects')) and \
                os.path.isdir(os.path.join(d, 'refs')):
            headref = os.path.join(d, 'HEAD')
            return os.path.isfile(headref) or \
                    (os.path.islink(headref) and
                    os.readlink(headref).startswith('refs'))

    def get_repo_dir(self):
        if not self._repo_dir:
            self._repo_dir = os.getenv('GIT_DIR')
            if self._repo_dir and self._is_git_dir(self._repo_dir):
                return self._repo_dir
            curpath = self._location
            while curpath:
                if self._is_git_dir(curpath):
                    self._repo_dir = curpath
                    break
                elif self._is_git_dir(os.path.join(curpath, '.git')):
                    self._repo_dir = os.path.join(curpath, '.git')
                    break
                curpath, dummy = os.path.split(curpath)
                if not dummy:
                    break
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
        self.refresh()

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

    def create_branch(self, name, start='HEAD', force=False, track=True):
        self.validate()
        args = ['git', 'branch']
        if force:
            args.append('-f')
        if track:
            args.append('--track')
        else:
            args.append('--no-track')
        args.append(name)
        args.append(start)
        proc = self._popen(args)
        if proc.wait():
            if not force and name in self.branches():
                 raise RepoError(_('Could not create branch, branch exists'))
            else:
                raise RepoError(_('Could not create branch: %s') %
                                    proc.stderr.read())

    def checkout(self, commit, is_merge=False, force=False, paths=None):
        self.validate()
        args = ['git', 'checkout']
        if is_merge:
            args.append('-m')
        elif force:
            args.append('-f')
        args.append(commit)
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
             raise RepoError(_('Failed to switch to %s: %s') % (commit,
                                proc.stderr.read()))
        
    def _read_remotes(self):
        self._remotes = []
        if not self.is_repo:
            return
        proc = self._popen(('git', 'branch', '-r'))
        for b in proc.stdout.readlines():
            status = b[0]
            branch = b[2:].strip()
            if status == '*':
                self._current_branch = branch
            self._remotes.append(branch)
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
            status = b[0]
            branch = b[2:].strip()
            if status == '*':
                self._current_branch = branch
            self._branches.append(branch)
        if proc.wait():
            raise RepoError(_('Could not get branch list: %s') %
                                proc.stderr.read())

    def branches(self):
        self.validate()
        if not self._branches:
            self._read_branches()
            
        for b in self._branches:
            yield b

    def branch(self):
        self.validate()
        if not self._branches:
            self._read_branches()
        return self._current_branch

    def remotes(self):
        self.validate()
        if not self._remotes:
            self._read_remotes()
        for r in self._remotes:
            yield r

    def _get_format_args(self, data):
        options = ['-z']
        format = '--pretty=format:'
        first = True
        for prop in data:
            opt = Repo._properties[prop]
            if opt[0] == '%':
                if first:
                    format += '%x00' + opt + '%x00'
                    first = False
                else:
                    format += opt + '%x00'
            else:
                options.append(opt)
        options.insert(0, format)
        if not Repo.PATCH in data:
            options.append('-s')
        return options

    def _parse_git_data(self, prop_types, stream):
        cur_buf = stream.read(1024 * 10)
        idx = 0
        num_props = len(prop_types)
        separator = '\0'
        properties = {}
        while cur_buf:
            field, x, cur_buf = cur_buf.partition('\0')
            if not idx and not field:
                continue
            if not cur_buf:
                new_buf = stream.read(1024 * 10)
                if new_buf:
                    if not x:
                        cur_buf = field + new_buf
                    else:
                        cur_buf = new_buf
                    continue
            properties[prop_types[idx]] = field
            idx = (idx + 1) % num_props
            if not idx:
                yield properties
                properties = {}
        if properties:
            yield properties

    def get_commit_info(self, commit='HEAD', data=None):
        self.validate()
        args = ['git', 'show']
        if not data:
            data = [Repo.ID]
        args.extend(self._get_format_args(data))
        args.append(commit)
        proc = self._popen(args)
        retval = self._parse_git_data(data, proc.stdout).next()
        if proc.wait():
            return None
        if retval:
            return retval
        return None

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

    def commit(self, commit=None, verify=True, paths=None):
        self.validate()
        args = ['git', 'commit']
        if not verify:
            args.append('--no-verify')
        if commit:
            if Repo.AUTHOR in commit:
                args.append('--author')
                args.append(commit[Repo.AUTHOR] + ' <' +
                            commit[Repo.AUTHOR_EMAIL] + '>')
            if Repo.ID in commit:
                args.append('-C')
                args.append(commit[Repo.ID])
            elif Repo.SUBJECT in commit:
                args.append('-m')
                if Repo.BODY in commit:
                    args.append(commit[Repo.SUBJECT] + '\n' +
                                commit[Repo.BODY])
                else:
                    args.append(commit[Repo.SUBJECT])
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to commit change: %s') %
                            proc.stdout.read() + proc.stderr.read())

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
        wd = os.getcwd()
        if not wd.startswith(self._location):
            wd = self._location
        proc = self._popen(args, cwd=wd)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Could not add files: %s') % proc.stderr.read())
            
    def list_tags(self, pattern=None):
        if self._tags:
            return self._tags
        self.validate()
        proc = None
        if pattern:
            proc = self._popen(('git', 'tag', '-l', pattern))
        else:
            proc = self._popen(('git', 'tag', '-l'))
        self._tags = [ line.strip() for line in proc.stdout.readlines()]
        if proc.wait():
            raise RepoError(_('Failed to list tags: %s') % proc.stderr.read())
        return self._tags

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
        
    def diff(self, start, end, paths, stat=False, patch=True,
                detect=False, ignorewhite='none'):
        self.validate()
        args = ['git', 'diff']
        if patch:
            args.append('-p')
        if stat:
            args.append('--stat')
            args.append('--summary')
        if detect:
            args.append('-M')
            args.append('-C')
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
        args = ['git', 'ls-files', '-o', '-c', '-t']
        proc = self._popen(args)
        files = {}
        for item in proc.stdout.readlines():
            status = item[0]
            f = item[2:].strip()
            files[f] = Repo._status[status]
        proc.wait()
        proc = self._popen(('git', 'diff', '--name-status', 'HEAD'))
        for line in proc.stdout.readlines():
            status, filename = line.split()
            files[filename.strip()] = Repo._status[status[0]]
        proc.wait()
        return files

    def _convert_range(self, first, last):
        if not first:
            first = 'HEAD^'
        else:
            first += '^'
        if not last:
            last = 'HEAD'
        first = first + '..' + last
        return first

    def get_history(self, first, last, limit, data=None, follow=False,
                    paths=None, skip=0):
        self.validate()
        args = ['git', 'log']
        if not data:
            data = [Repo.ID]
        args.extend(self._get_format_args(data))
        if limit > -1:
            args.append('-' + str(limit))
        if follow:
            args.append('--follow')
        if skip:
            args.append('--skip=' + str(skip))
        if not first:
            first = 'HEAD'
        if last:
            args.append(first + '..' + last)
        else:
            args.append(first)
        if paths:
            args.append('--')
            args.extend(paths)
        proc = self._popen(args)
        for commit in self._parse_git_data(data, proc.stdout):
            yield commit
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

    def import_bundle(self, filename, refs):
        self.validate()
        args = ['git', 'pull', filename]
        if refs:
            args.extend(refs)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to import %s: %s') % (filename,
                            proc.stderr.read()))

    def export_bundle(self, filename, first, last):
        self.validate()
        args = ['git', 'bundle', 'create', filename,
                self._convert_range(first, last)]
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to export: %s') % proc.stderr.read())

    def verify_bundle(self, filename):
        args = ['git', 'bundle', 'verify', filename]
        proc = self._popen(args)
        if proc.wait():
            return False, proc.stderr.read().strip()
        return True, None

    def export_archive(self, filename, commit, paths=None, format='tgz'):
        self.validate()
        args = ['git', 'archive', ]
        if format == 'tgz':
            format = 'tar'
        elif format == 'zip':
            pass
        else:
            raise HelpError(_('Invalid format %s') % format)
        args.append('--format=' + format)
        args.append(commit)
        args.extend(paths)
        f = None
        if format == 'tar':
            f = gzip.GzipFile(filename, 'w')
        else:
            f = open(filename, 'w')
        try:
            proc = self._popen(args)
            data = proc.stdout.read(4096)
            while data:
                f.write(data)
                data = proc.stdout.read(4096)
        finally:
            f.close()
        if proc.wait():
            os.remove(filename)
            raise RepoError(_('Failed to export: %s') % proc.stderr.read())

    def fetch(self, repo, branchspecs, force=False, depth=-1, notags=False):
        self.validate()
        args = ['git', 'fetch']
        if force:
            args.append('--force')
        if depth > 0:
            args.append('--depth=' + depth)
        if notags:
            args.append('--no-tags')
        if repo:
            args.append(repo)
        else:
            args.append('.')
        for source, dest in branchspecs:
            if not dest:
                dest = self.branch()
            args.append(source + ':' + dest)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to fetch: %s') % proc.stderr.read())

    def move(self, sources, dest, force=False, ignore=False, noop=False):
        self.validate()
        args = ['git', 'mv']
        if force:
            args.append('-f')
        if ignore:
            args.append('-k')
        if noop:
            args.append('-n')
        args.extend(sources)
        args.append(dest)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to move: %s') % proc.stderr.read())

    def delete(self, paths, force=False, recursive=False, noop=False,
                cached=False):
        self.validate()
        args = ['git', 'rm']
        if force:
            args.append('-f')
        if recursive:
            args.append('-r')
        if noop:
            args.append('-n')
        if cached:
            args.append('--cached')
        args.extend(paths)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to remove: %s') % proc.stderr.read())

    def show(self, files, commit='HEAD', tag=None):
        self.validate()
        args = ['git', 'show']
        treeish = None
        if tag:
            treeish = tag
        else:
            treeish = commit
        if files:
            for f in files:
                args.append(treeish + ':' + f)
        else:
            args.append(treeish)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to show: %s') % proc.stderr.read())

    def move_head_to(self, commit, workdir=False):
        self.validate()
        args = ['git', 'reset']
        if not commit:
            commit='HEAD'
        if workdir:
            args.append('--hard')
        else:
            args.append('--mixed')
        args.append(commit)
        proc = self._popen(args)
        if proc.wait():
            raise RepoError(_('Failed to move head: %s') % proc.stderr.read())

    def most_recent_tag(self, branch=None):
        self.validate()
        if not branch:
            branch = self._current_branch
        proc = self._popen(('git', 'describe', '--abbrev=10',
                            '--tags', branch))
        if self.wait():
            raise RepoError(_('Unable to get most recent tag %s') %
                            proc.stderr.read())
        return proc.stdout.read().strip()

    def revert(self, commit, dryrun=False, mainline=None):
        self.validate()
        args = ['git', 'revert', '--no-edit']
        if dryrun:
            args.append('--no-commit')
        if mainline:
            args.append('--mainline')
            args.append(str(mainline))
        args.append(commit)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to revert: %s') % proc.stderr.read())

    def cherry(self, downstream, limit=None):
        self.validate()
        args = ['git', 'cherry', 'HEAD', downstream]
        if limit:
            args.append(limit)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise RepoError(_('Failed to get cherry info %s') %
                            proc.stderr.read())

    def cherry_pick(self, commit, dryrun=False):
        self.validate()
        args = ['git', 'cherry-pick']
        if dryrun:
            args.append('--no-commit')
        args.append(commit)
        proc = None
        proc = self._popen(args, stdout=None)
        if proc.wait():
            raise RepoError(proc.stderr.read())

    def grep(self, pattern, files, commit=None, ignore=False, whole=False,
                ignore_binary=False, invert=False, path=False,
                not_regex=False, count=False):
        self.validate()
        args = ['git', 'grep', '-e', pattern]
        if ignore:
            args.append('--ignore-case')
        if whole:
            args.append('--word-regexp')
        if ignore_binary:
            args.append('-I')
        if invert:
            args.append('--invert-match')
        if path:
            args.append('--full-name')
        elif path == None:
            args.append('-h')
        if not_regex:
            args.append('--fixed-strings')
        if count:
            args.append('--count')
        if commit:
            args.append(commit)
        else:
            args.append('.')
        if files:
            args.append('--')
            args.extend(files)

        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            err_str = proc.stderr.read()
            if err_str:
                raise RepoError(_('Failed to grep: %s') % err_str)
