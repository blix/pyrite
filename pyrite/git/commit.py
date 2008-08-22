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

from gitobject import GitObject, GitError
import time
from pyrite.utils.smartstream import SmartStream

class Commit(GitObject):
    AUTHOR = 'AUTHOR'
    AUTHOR_EMAIL = 'AUTHOR_EMAIL'
    AUTHOR_DATE = 'AUTHOR_DATE'
    COMMITER = 'COMMITER'
    COMMITER_EMAIL = 'COMMITER_EMAIL'
    COMMIT_DATE = 'COMMIT_DATE'
    SUBJECT = 'SUBJECT'
    ID = 'ID'
    PARENTS = 'PARENTS'
    BODY = 'BODY'
    DIFFSTAT = 'DIFFSTAT'
    PATCH = 'PATCH'
    TREE = 'TREE'
    FILES = 'FILES'
    REFS = 'REFS'
    AUTHOR_DATE_OFFSET = 'AUTHOR_DATE_OFFSET'
    COMMITER_DATE_OFFSET = 'COMMITER_DATE_OFFSET'

    def __init__(self, commitish=None, data=None, raw_commit=None, obj=None):
        GitObject.__init__(self, obj=obj)
        if not commitish and not raw_commit:
            raise GitError(_('Need commitish or raw_commit to '
                             'build commit.'))
        self._data = data and data or [Commit.ID]
        if not raw_commit:
            if not isinstance(commitish, str):
                raise TypeError()
            gen = Commit.get_raw_commits(self, None, commitish,
                                                  1, self._data)
            try:
                self._raw_commit = gen.next()
            except StopIteration:
                raise LookupError()
        else:
            if not isinstance(raw_commit, dict):
                raise TypeError()
            self._raw_commit = raw_commit
        self._description = None

    @property
    def id(self):
        return self._raw_commit[Commit.ID]

    @property
    def short(self):
        return self._raw_commit[Commit.ID][:8]

    @property
    def author(self):
        return '"%s" <%s>' % (self._raw_commit[Commit.AUTHOR],
                              self._raw_commit[Commit.AUTHOR_EMAIL])

    @property
    def author_name(self):
        return self._raw_commit[Commit.AUTHOR]

    @property
    def author_email(self):
        return self._raw_commit[Commit.AUTHOR_EMAIL]

    @property
    def authored_date(self):
        return time.gmtime(int(self._raw_commit[Commit.AUTHOR_DATE])), \
                self._raw_commit[Commit.AUTHOR_DATE_OFFSET]

    @property
    def commiter(self):
        return '"%s" <%s>' % (self._raw_commit[Commit.COMMITER],
                              self._raw_commit[Commit.COMMITER_EMAIL])

    @property
    def commiter_name(self):
        return self._raw_commit[Commit.COMMITER]

    @property
    def commiter_email(self):
        self._raw_commit[Commit.COMMITER_EMAIL]

    @property
    def commited_date(self):
        return humandate(self._raw_commit[Commit.COMMIT_DATE]) + ' ' + \
                self._raw_commit[Commit.COMMITER_DATE_OFFSET]

    @property
    def parent_ids(self):
        return self._raw_commit[Commit.PARENTS]

    @property
    def tree(self):
        return self._raw_commit[Commit.TREE]

    @property
    def subject(self):
        return self._raw_commit[Commit.SUBJECT]

    @property
    def body(self):
        return self._raw_commit[Commit.BODY]

    @property
    def patch(self):
        return self._raw_commit[Commit.PATCH]

    @property
    def diffstat(self):
        return self._raw_commit[Commit.DIFFSTAT]

    @property
    def refs(self):
        return self._raw_commit[Commit.REFS]

    @property
    def raw(self):
        return self._raw_commit

    def describe(self):
        if not self._description:
            self._description = Commit.describe_commit(self,
                                    self._raw_commit[Commit.ID], self)
        return self._description

    def __str__(self):
        return self.id

    def __repr__(self):
        return '<%s.%s id="%s">' % (Commit.__module__, Commit.__name__,
                                    self.id)

    @staticmethod
    def describe_commit(gitobj, id, commit=None):
        gitobj.validate()
        if not id:
            id = 'HEAD'
        proc = gitobj._popen(('git', 'describe', '--abbrev=40', id))
        parts = proc.stdout.read().split('-')
        if proc.wait():
            c = commit and commit or Commit(id, obj=gitobj)
            return None, 0, c.id
        if len(parts) == 3:
            return parts[0], int(parts[1]), parts[2].strip()[1:]
        tag = parts[0].strip()
        c = commit and commit or Commit(id, gitobj)
        return tag, 0, id

    @classmethod
    def is_commit(cls, gitobj, name):
        gitobj.validate()
        proc = gitobj._popen(('git', 'rev-list', name))
        return not proc.wait()

    @classmethod
    def get_commits(cls, gitobj, first, last, limit=-1, data=None,
                    follow=False, paths=None, skip=0, incoming=False,
                    reverse=False, reflog=False, ordered=False, all=False):
        for c in Commit.get_raw_commits(gitobj, first, last, limit, data,
                                        follow, paths, skip, incoming,
                                        reverse, reflog, ordered, all):
            yield Commit(data=data, raw_commit=c, obj=gitobj)

    @classmethod
    def get_raw_commits(cls, gitobj, first, last, limit=-1, data=None,
                        follow=False, paths=None, skip=0, incoming=False,
                        reverse=False, reflog=False, ordered=False, all=False):
        gitobj.validate()
        args = ['git', 'log']
        if not data:
            data = [Commit.ID]
        args.extend(cls._get_format_args(data))
        if limit > -1:
            args.append('-' + str(limit))
        if follow:
            args.append('--follow')
        if skip:
            args.append('--skip=' + str(skip))
        if incoming:
            args.append('--cherry-pick')
            args.append('--left-right')
        if incoming or reverse:
            args.append('--reverse')
        if reflog:
            args.append('-g')
        if ordered:
            args.append('--topo-order')
        if all:
            args.append('--all')
        else:
            if not last:
                last = 'HEAD'
            if first:
                args.append(first + (incoming and '...' or '..') + last)
            else:
                args.append(last)
        if paths:
            args.append('--full-history')
            args.append('--')
            args.extend(paths)
        proc = gitobj._popen(args)
        for commit in cls._parse_raw_output(data, SmartStream(proc.stdout)):
            if incoming:
                id = commit[Commit.ID]
                if id[0] == '>':
                    commit[Commit.ID] = id[1:]
                else:
                    continue
            yield commit
        if proc.wait():
            raise GitError(_('Failed to get log: %s') % proc.stderr.read())

    @staticmethod
    def _get_format_args(data):
        options = ['--pretty=raw']
        if Commit.PATCH in data:
            options.append('-p')
            options.append('-c')
        if Commit.DIFFSTAT in data:
            options.append('--stat')
        if Commit.REFS in data:
            options.append('--decorate')
        return options

    @staticmethod
    def _parse_message(commit, firstline, stream):
        commit[Commit.SUBJECT] = stream.readline().strip()
        buf = []
        append = buf.append
        readline = stream.readline
        type = Commit.BODY
        while True:
            line = readline()
            if not line or line[0] != ' ':
                commit[type] = buf
                return line
            append(line[4:])

    @staticmethod
    def _parse_diffstat(commit, firstline, stream):
        if firstline.startswith('commit'):
            return firstline
        buf = []
        append = buf.append
        readline = stream.readline
        type = Commit.DIFFSTAT
        while True:
            line = readline()
            if not line or line[0] != ' ':
                commit[type] = buf
                return line
            append(line)

    @staticmethod
    def _parse_patch(commit, firstline, stream, parse_files=False):
        if firstline.startswith('commit'):
            commit[Commit.PATCH] = ''
            return firstline
        buf = [firstline]
        append = buf.append
        readline = stream.readline
        type = Commit.PATCH

        def parse_normal():
            while True:
                line = readline()
                if not line or line[0] == 'c':
                    commit[type] = buf
                    return line
                append(line)

        def parse_with_files():
            in_header = False
            while True:
                line = readline()
                if not line or line[0] == 'c':
                    commit[type] = buf
                    return line
                if line.startswith('diff '):
                    in_header = True
                elif line[0] == '@':
                    in_header = False
                if in_header and (line.startswith('+++ ') or
                                  line.startswith('--- ')):
                    if line[4:] != '/dev/null':
                        commit[Commit.FILES].add(line[4:])
                append(line)

        if parse_files:
            return parse_with_files()
        else:
            return parse_normal()

    @staticmethod
    def _parse_raw_header(commit, firstline, stream):
        parents = commit[Commit.PARENTS] = []

        parts = firstline.strip().split()
        commit[Commit.ID] = parts[1]
        refs = commit[Commit.REFS] = []
        for part in parts[2:]:
            part = part.strip('(),')
            if not part.startswith('refs'):
                continue
            refs.append(part)
        commit[Commit.TREE] = stream.readline().split()[1].strip()
        line = stream.readline()
        while line[:3] == 'Ref':
            line = stream.readline()
        while line[:3] == 'par':
            parents.append(line.split()[1].strip())
            line = stream.readline()
        idx = line.find('<')
        commit[Commit.AUTHOR] = line[7:idx - 1]
        idx2 = line.rfind('>') + 1
        commit[Commit.AUTHOR_EMAIL] = line[idx + 1:idx2 - 1]
        commit[Commit.AUTHOR_DATE] = line[idx2 + 1:-6]
        commit[Commit.AUTHOR_DATE_OFFSET] = line[-6:-1]
        line = stream.readline()
        idx = line.find('<')
        commit[Commit.COMMITER] = line[10:idx - 1]
        idx2 = line.rfind('>') + 1
        commit[Commit.COMMITER_EMAIL] = line[idx + 1:idx2 - 1]
        commit[Commit.COMMIT_DATE] = line[idx2 + 1:-6]
        commit[Commit.COMMITER_DATE_OFFSET] = line[-6:-1]

        return stream.readline()

    @classmethod
    def _parse_raw_output(cls, prop_types, stream):
        commit = {}

        line = stream.readline()
        while line:
            line = cls._parse_raw_header(commit, line, stream)
            line = cls._parse_message(commit, line, stream)
            if Commit.DIFFSTAT in prop_types:
                line = cls._parse_diffstat(commit, line, stream)
            else:
                commit[Commit.DIFFSTAT] = ''
            if Commit.PATCH in prop_types:
                line = cls._parse_patch(commit, line, stream,
                                        Commit.FILES in prop_types)
            else:
                commit[Commit.PATCH] = ''
            while line == '\n':
                line = stream.readline()
            yield commit
            commit = {}
