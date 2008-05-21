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

from pyrite.repository import Repo, RepoError
import pyrite
import os

class SequencerError(Exception):
    """The sequencer has encountered a problem and cannot continue."""

class UnintializedSequencerError(SequencerError):
    """The sequencer is not properly initialized."""

class SequencerDirtyWorkdirError(SequencerError):
    """The workdir is dirty, cannot continue"""

class SequencerMergeNeeded(SequencerError):
    """The sequence was not completed, user needs to take action"""

class Sequencer(object):
    def __init__(self, repo, preserve_merges=False):
        self._repo = repo
        repo.validate()
        self.clear()
        self._preserve = preserve_merges
        self._squashed = []
        self._head = None
        self._branch = None
        self._last_action = -1
        self._message = None
        self._marks = {}

    def set_head(self, head):
        self._head = head

    def set_branch(self, branch):
        self._branch = branch

    def head(self):
        return self._head

    def branch(self):
        return self._branch

    def clear(self):
        self._seq = []

    def remove(self, idx):
        del self._seq[idx]

    def add(self, item, idx=-1):
        if idx < 0:
            self._seq.append(item)
        else:
            self._insert(idx, item)

    def abort(self):
        if not self._head or not self._branch:
            raise UnintializedSequencerError(_('original HEAD not set'))
        self._repo.move_head_to(self._head, True)

    def skip(self):
        if 0 > self._last_action:
            raise UnintializedSequencerError(_('last action unkown'))
        cmd, id, rest = self._seq[self._last_action].split(None, 2)
        self._repo.move_head_to('HEAD', True)
        return id, rest

    def finish_last(self):
        if 0 > self._last_action:
            raise UnintializedSequencerError(_('last action unkown'))
        if self._last_action >= len(self._seq):
            return True

        if not self._repo.changed_files():
            raise SequencerError(_('Nothing to commit, you probably '
                                   'want to "pyt track" something\n'
                                   'or "pyt rebase skip"'))

        cmd, id, rest = self._seq[self._last_action].split(None, 2)
        if cmd in ('pick', 'edit') and not self._message:
            c = self._repo.get_commit_info(id, [Repo.SUBJECT, Repo.BODY])
            self._message = c[Repo.SUBJECT] + '\n' + ''.join(c[Repo.BODY])
        elif cmd == 'squash':
            return True
        else:
            raise SequencerError(_('don\'t know what to do with %s right '
                                   'now') % item)

        if self._message:
            extra = [
                _('This is a commit message.'),
                _('Lines beginning with "#" will be removed'),
                _('To abort checkin, remove the contents of the file '
                  'before checking in.'),
                _('  On branch %s') % pyrite.repo.branch(),
                _('  '),
                _('Changed Files...'),
                _('  ')
            ]
            for x in pyrite.repo.changed_files():
                extra.append('  ' + ' '.join(x))
            self._message = pyrite.ui.edit(self._message, extra,
                                            'pyt-message')
        if not self._message:
            raise SequencerError(_('Empty commit message, aborting commit.'))

        self._repo.update_index()
        c = {Repo.SUBJECT: self._message}
        self._repo.commit(c)
        self._message = []
        if cmd == 'squash':
            self._squashed = []
        return True

    def run(self):
        if not self._head:
            raise UnintializedSequencerError(_('original HEAD not set'))
        if not self._branch:
            raise UnintializedSequencerError(_('original branch not set'))
        if self._repo.branch() != self._branch:
            raise SequencerError(_('Cannot continue, current branch should '
                              'be %s\n  Please switch to %s using "pyt co %s"')
                            % (self._branch, self._branch, self._branch))
        if self._repo.changed_files():
            if self._head == self._repo.get_commit_info(
                                data=[Repo.ID])[Repo.ID]:
                raise SequencerDirtyWorkdirError()

        commands = {
            'pick': self._pick,
            'edit': self._edit,
            'merge': self._merge,
            'squash': self._squash,
            'reset': self._reset,
            'mark': self._mark,
            'tag': self._tag
        }
        if self._last_action >= len(self._seq):
            yield True, None, None
            return
        for item in self._seq[self._last_action + 1:]:
            self._last_action += 1

            cmd, rest = item.split(None, 1)
            if cmd not in commands:
                raise SequencerError(_('Bad sequence command: %s') % cmd)
            if cmd != 'squash' and self._squashed:
                cont, id, subject = self._complete_squash()
                yield cont, 'squish', id, subject
            cont, id, subject = commands[cmd](rest)
            yield cont, cmd, id, subject
        if self._squashed:
            cont, id, subject = self._complete_squash()
            yield cont, 'squish', id, subject

    def _pick(self, rest, nocommit=False):
        try:
            cid, subject = self._get_commit_id(rest)
            self._repo.cherry_pick(cid, nocommit)
        except RepoError, inst:
            raise SequencerMergeNeeded(inst.message)
        return True, cid, subject

    def _edit(self, rest):
        try:
            cid, subject = self._get_commit_id(rest)
            self._repo.cherry_pick(cid, True)
        except RepoError, inst:
            raise SequencerMergeNeeded(inst.message)
        return False, cid, subject

    def _squash(self, rest):
        try:
            cid, subject = self._get_commit_id(rest)
            if not self._squashed:
                commit = self._repo.get_commit_info('HEAD',
                                                    [Repo.SUBJECT,
                                                    Repo.BODY, Repo.ID])
                if not commit:
                    return False
                self._squashed.append(commit)
                changed_files = [ f.strip() for m, f in
                                 self._repo.changed_files('HEAD')]
                self._repo.move_head_to('HEAD^')
                for l in self._repo.add_files(False, False, changed_files):
                    pass
            commit = self._repo.get_commit_info(cid, [Repo.SUBJECT,
                                                    Repo.BODY, Repo.ID])
            if not commit:
                return False
            self._squashed.append(commit)
            self._repo.cherry_pick(cid, True)
            return True, cid, subject
        except RepoError, inst:
            raise SequencerMergeNeeded()

    def _squash_message(self):
        message = []
        for num, commit in enumerate(self._squashed):
            if num:
                message.append('\n')
            message.append(_('# Commit message from %s\n\n') %
                           commit[Repo.ID])
            message.append(commit[Repo.SUBJECT])
            message.append('\n')
            message.append(''.join(commit[Repo.BODY]))
            message.append('\n')

        extra = [
            _('This is a commit message.'),
            _('Lines beginning with "#" will be removed'),
            _('To abort checkin, remove the contents of the file '
              'before checking in.'),
            _('  '),
            _('Changed Files...'),
            _('  ')
        ]

        for x in self._repo.changed_files():
            extra.append('  ' + ' '.join(x))
        return message, extra

    def _complete_squash(self):
        if not self._squashed:
            return True, None, None

        message, extra = self._squash_message()

        message = pyrite.ui.edit(message, extra, 'pyt-message')
        if not message:
            return False, None, None
        commit = {Repo.SUBJECT: message}
        self._repo.commit(commit)
        self._squashed = []
        commit = self._repo.get_commit_info('HEAD', (Repo.ID, Repo.SUBJECT))
        return True, commit[Repo.ID], commit[Repo.SUBJECT]

    def _merge(self, rest):
        commits = rest.split()
        self._repo.merge(commits)
        return True, None, None

    def _reset(self, rest):
        try:
            cid = self._get_commit_id(rest)
            self._repo.move_head_to(cid, True)
        except RepoError, inst:
            raise SequencerError(inst.message)
        return True, None, None

    def _mark(self, rest):
        try:
            id = self._repo.get_commit_info('HEAD', [Repo.ID])[Repo.ID]
            self._marks[rest] = id
        except RepoError, inst:
            raise SequencerError(inst.message)
        return True, None, None

    def _tag(self, rest):
        pass

    def _get_commit_id(self, rest):
        cid, subject = rest.split(None, 1)
        if cid[0] == ':':
            if not cid[1:] in self._marks:
                raise SequencerError(_('Bad mark %s') % cid[1:])
            cid = self._marks[cid[1:]]
        return cid, subject
