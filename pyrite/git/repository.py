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

from gitobject import *
from commit import Commit

class Repo(GitObject):
    _status = {
        '?': 'untracked',
        'H': 'uptodate',
        'C': 'modified',
        'M': 'modified',
        'D': 'deleted',
        'A': 'added'
    }

    def __init__(self, settings=None, io=None, location=None, obj=None):
        GitObject.__init__(self, settings, io, location, obj)
        self._branches = None
        self._remotes = None
        self._tags = None

    def __getitem__(self, key):
        if isinstance(key, slice):
            li = []
            step = key.step
            if step:
                for idx, c in enumerate(Commit.get_raw_commits(self,
                                                          key.start,
                                                          key.stop)):
                    if not (idx % step):
                        li.append(Commit(raw_commit=c, obj=self))
            else:
                for c in Commit.get_raw_commits(self, key.start, key.stop):
                    li.append(Commit(raw_commit=c, obj=self))
            return li
        elif isinstance(key, str):
            return Commit(key, obj=self)
        else:
            raise TypeError()

    def refresh(self):
        self._branches = None
        self._remotes = None
        self._tags = None
        GitObject.refresh(self)

    def init(self):
        proc = self._popen(('git', 'init'), cwd=self._location)
        if proc.wait():
            raise GitError(_('Failed to init repo: %s') % proc.stderr.read())
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
            raise GitError(_('Failed to delete branch %s: %s') %
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
            raise GitError(_('Failed to rename branch %s to %s: %s') %
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
                 raise GitError(_('Could not create branch, branch exists'))
            else:
                raise GitError(_('Could not create branch: %s') %
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
             raise GitError(_('Failed to switch to %s: %s') % (commit,
                                proc.stderr.read()))

    def _read_remotes(self):
        self._remotes = []
        proc = self._popen(('git', 'branch', '-r'))
        for b in proc.stdout.readlines():
            status = b[0]
            branch = b[2:].strip()
            if status == '*':
                self._current_branch = branch
            self._remotes.append(branch)
        if proc.wait():
            raise GitError('Could not get remotes list: %s' %
                            proc.stderr.read())

    def _read_branches(self):
        self._branches = []
        self._current_branch = None
        proc = self._popen(('git', 'branch'))
        for b in proc.stdout.readlines():
            status = b[0]
            branch = b[2:].strip()
            if status == '*':
                self._current_branch = branch
            self._branches.append(branch)
        if proc.wait():
            raise GitError(_('Could not get branch list: %s') %
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
            raise GitError(_('Failed to update index: %s') %
                                proc.stderr.read())

    def changed_files(self, commit=None):
        self.validate()
        proc = None
        if commit:
            proc = self._popen(('git', 'diff', '--name-status', commit,
                                commit + '^'))
        else:
            proc = self._popen(('git', 'diff',
                                '--name-status', 'HEAD'))
        retval = set((line[0], line[2:-1]) for line in proc.stdout.readlines())
        if proc.wait():
            raise GitError(_('Failed to get changed files: %s') %
                                proc.stderr.read())
        return retval

    def commit(self, commit=None, verify=True):
        self.validate()
        have_msg = Commit.SUBJECT in commit
        args = ['git', 'commit']
        if not verify:
            args.append('--no-verify')
        if commit:
            if Commit.AUTHOR in commit:
                args.append('--author')
                args.append(commit[Commit.AUTHOR] + ' <' +
                            commit[Commit.AUTHOR_EMAIL] + '>')
            if Commit.ID in commit:
                args.append('-C')
                args.append(commit[Commit.ID])
                have_msg = False
            elif have_msg:
                args.append('-F')
                args.append('-')
        proc = self._popen(args, stdin=have_msg)
        if have_msg:
            proc.stdin.writelines(commit[Commit.SUBJECT])
            if Commit.BODY in commit:
                proc.stdin.writelines(commit[Commit.BODY])
            proc.stdin.close()
        if proc.wait():
            raise GitError(_('Failed to commit change: %s') %
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
            raise GitError(_('Failed to gc: %s') % proc.stderr.read())

    def verify(self, verbose):
        self.validate()
        if verbose:
            proc = self._popen(('git', 'fsck', '--verbose'))
        else:
            proc = self._popen(('git', 'fsck'))
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise GitError(_('Verify failed: %s') % proc.stderr.read())

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
            raise GitError(_('Could not add files: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to list tags: %s') % proc.stderr.read())
        return self._tags

    def verify_tag(self, tag):
        self.validate()
        proc = self._popen(('git', 'tag', '-v', tag))
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise GitError(_('Failed to verify tag: %s') % proc.stderr.read())

    def delete_tags(self, tags):
        self.validate()
        args = ['git', 'tag', '-d']
        args.extend(tags)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise GitError(_('Failed to delete tag(s): %s') %
                            proc.stderr.read())

    def create_tag(self, name, message, commit='HEAD', key=None, sign=False):
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
        args.append(commit)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise GitError(_('Failed to create tag: %s') % proc.stderr.read())

    def push(self, repo, source, target, force=False, all_branches=False,
                all_tags=False, verbose=False):
        self.validate()
        args = ['git', 'push']
        if force:
            args.append('-f')
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
            raise GitError(_('Failed to push: %s') % proc.stderr.read())
            
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
            raise GitError(_('Failed to pull: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to clone: %s') % proc.stderr.read())

    def num_stat(self, start, end):
        self.validate()
        spec = start
        if not end:
            end = 'HEAD'
        if not start:
            spec = end
        else:
            spec = start + '..' + end
        proc = self._popen(('git', 'diff', '--numstat', spec))
        for line in proc.stdout.readlines():
            added, lost, name = line.split(None, 2)
            if added != '-':
                yield int(added), int(lost), name
        if proc.wait():
            raise GitError(_('Failed to get numstat: %s') %
                            proc.stderr.read())

    def diff(self, start, end, paths=None, stat=False, patch=True,
                detect=False, ignorewhite='none', binary=False):
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
        if binary:
            args.append('--binary')
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
            raise GitError(_('Failed to diff: %s') % proc.stderr.read())

    def get_unresolved(self):
        self.validate()
        proc = self._popen(('git', 'ls-files', '-t', '--exclude-standard',
                            '--unmerged'))
        files = {}
        for item in proc.stdout.readlines():
            parts = item.split()
            files[parts[4]] = parts[0]
        proc.wait()
        return files

    def list(self, tracked=True, untracked=False):
        self.validate()
        args = ['git', 'ls-files', '-t', '--exclude-standard']
        if tracked:
            args.append('-c')
        if untracked:
            args.append('-o')
        proc = self._popen(args)
        files = {}
        for item in proc.stdout.readlines():
            status = item[0]
            f = item[2:].strip()
            files[f] = Repo._status[status]
        if tracked:
            proc.wait()
            proc = self._popen(('git', 'diff', '--name-status', 'HEAD'))
            for line in proc.stdout.readlines():
                status, filename = line.split()
                files[filename.strip()] = Commit._status[status[0]]

        proc.wait()
        return files

    def _convert_range(self, first, last):
        if not last:
            last = 'HEAD'
        if not first:
            first = 'HEAD'
        first = first + '^..' + last
        return first

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
            raise GitError(_('Failed to merge: %s') % proc.stderr.read())

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
        for l in proc.stdout.readlines():
            yield l
        if proc.wait():
            raise GitError(_('Failed to export: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to import %s: %s') % (filename,
                            proc.stderr.read()))

    def export_bundle(self, filename, first, last):
        import time
        self.validate()
        dummy_tagname = None
        if (last != 'HEAD' and not os.path.exists(os.path.join(
            self.get_git_dir(), 'refs', 'tags', last)) and
            not os.path.exists(os.path.join(self.get_git_dir(), 'refs',
                                            'heads', last)) and
            not os.path.exists(os.path.join(self.get_git_dir(), 'refs',
                                            'remotes', last))):

            dummy_tagname = 'pyrite-temp-tag-' + str(time.time())
            for l in self.create_tag(dummy_tagname, None, last):
                pass
            last = dummy_tagname
        args = ['git', 'bundle', 'create', filename,
                self._convert_range(first, last)]
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            yield line
        if proc.wait():
            raise GitError(_('Failed to export: %s') % proc.stderr.read())
        if dummy_tagname:
            for l in self.delete_tags([dummy_tagname]):
                pass

    def verify_bundle(self, filename):
        args = ['git', 'bundle', 'verify', filename]
        proc = self._popen(args)
        if proc.wait():
            return False, proc.stderr.read().strip()
        return True, None

    def export_archive(self, filename, commit, paths=None, format='tgz'):
        import gzip
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
            raise GitError(_('Failed to export: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to fetch: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to move: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to remove: %s') % proc.stderr.read())

    def show(self, commit='HEAD', tag=None, files=None):
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
            raise GitError(_('Failed to show: %s') % proc.stderr.read())

    def move_head_to(self, commit='HEAD', workdir=False):
        self.validate()
        args = ['git', 'reset', '-q']
        if workdir:
            args.append('--hard')
        args.append(commit)
        proc = self._popen(args, stdout=None)
        if proc.wait():
            raise GitError(_('Failed to move head: %s') % proc.stderr.read())

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
            raise GitError(_('Failed to revert: %s') % proc.stderr.read())

    def cherry_pick(self, commit, dryrun=False):
        self.validate()
        args = ['git', 'cherry-pick']
        if dryrun:
            args.append('--no-commit')
        args.append(commit)
        proc = self._popen(args)
        for line in proc.stdout.readlines():
            pass
        if proc.wait():
            raise GitError(proc.stderr.read())

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
                raise GitError(_('Failed to grep: %s') % err_str)

    def apply(self, diff, toindex=False, getstat=False):
        self.validate()
        args = ['git', 'apply', '--binary']
        if toindex:
            args.append('--cached')
        if getstat:
            args.extend(['--stat', '--summary', '--apply'])
        args.append('-')
        proc = self._popen(args, stdin=True)
        proc.stdin.writelines(diff)
        proc.stdin.close()
        for line in proc.stdout.readlines():
            pass
        if proc.wait():
            raise GitError(_('Failed to apply %s') % proc.stderr.read())

    def _parse_blame(self, stream):
        commits = {}
        line = stream.readline()
        while line:
            line = line.strip()
            if not line:
                continue
            id, orig_lineno, rest = line.split(None, 2)
            cur_lineno = rest.split()[0]
            c = None
            if not id in commits:
                c = {Commit.ID: id}
                commits[id] = c
            else:
                c = commits[id]
            while True:
                if line.startswith('\t'):
                    line_contents = line[1:]
                    yield cur_lineno, commits[id], \
                            line_contents, orig_lineno
                    line = stream.readline()
                    break
                key, value = line.split(None, 1)
                if key == 'author':
                    c[Commit.AUTHOR] = value.strip()
                elif key == 'author-email':
                    c[Commit.AUTHOR_EMAIL] = value.strip()
                elif key == 'author-time':
                    c[Commit.AUTHOR_DATE] = value.strip()
                elif key == 'commiter':
                    c[Commit.COMMITER] = value.strip()
                elif key == 'commiter-mail':
                    c[Commit.COMMITER_EMAIL] = value.strip()
                elif key == 'commiter-time':
                    c[Commit.COMMIT_DATE] = value.strip()
                elif key == 'summary':
                    c[Commit.SUBJECT] = value.strip()
                line = stream.readline()

    def blame(self, file, commit=None, startline=None, endline=None):
        self.validate()
        args = ['git', 'blame', '-p']
        if startline != None:
            args.append('-L')
            limits = str(startline)
            if endline != None:
                limits += ',' + str(endline)
            args.append(limits)
        if commit:
            args.append(commit)
        args.append('--')
        args.append(file)
        proc = self._popen(args)
        for data in self._parse_blame(proc.stdout):
            yield data
        if proc.wait():
            raise GitError(_('Failed to get blame info: %s') %
                            proc.stderr.read())

    def cat_file(self, filename, cat_to=None, commit='HEAD'):
        self.validate()
        try:
            if cat_to.__class__ == ''.__class__:
                stream = open(cat_to, 'w')
            else:
                stream = cat_to
            stream.writelines(self.show(commit, [filename]))
        except GitError:
            return False
        finally:
            if cat_to.__class__ == ''.__class__:
                stream.close()
        return True
