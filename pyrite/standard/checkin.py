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

import pyrite
from pyrite.standard.help import HelpError
from pyrite.repository import Repo
import os

options = [
('c', 'commit', _('Reuse commit message, author and timestamp'), 1),
('a', 'author', _('Use as author of the commit'), 1),
('m', 'message', _('Use as the commit message'), 1),
('s', 'signoff', _('Add a Signed-off-by line to the message'), 0),
('n', 'no-verify', _('bypass precommit hooks'), 0),
('', 'amend', _('Replace the current tip with the new commit'), 0),
('e', 'edit', _('Force invoking the editor for the commit message'), 0),
]

help_str="""
pyt checkin [OPTIONS] [ [--] <paths>...]

Check-in your changes to the repository so they become part of the history.
Options allow you to specify a message, author such as
"Your Name your.name@example.com".  Also lets you add a signed-off line to
the commit message.

The amend option allows you to replace the tip of the current branch with the
combined changes from the working set and the tip.  This is useful for making
trivial updates to changes that have not been published.

The commit option allows you to re-use the commit message, author and timestamp
of a previous commit as the default messages for the current commit.
"""

def run(cmd, args, flags):
    use_commit = flags.get('commit', None)
    use_author = flags.get('author', None)
    use_message = flags.get('message', None)
    #need to decide if ament or use_commit mean that editor should not
    #be invoked by default
    edit = flags.has_key('edit') or (not use_message and not use_commit)
    amend = flags.has_key('amend')
    sign = flags.has_key('signoff')
    verify = not flags.has_key('no-verify')

    data = [Repo.SUBJECT, Repo.AUTHOR, Repo.AUTHOR_EMAIL, Repo.BODY, Repo.ID]
    commitdata = {}

    if use_commit and use_message:
        raise HelpError(cmd, _('Cannot specify commit and message'))
    elif use_commit:
        commitdata = pyrite.repo.get_commit_info(use_commit, data)
        use_message = commitdata[Repo.SUBJECT] + '\n' + \
                            ''.join(commitdata[Repo.BODY])

    extra = [_('This is a commit message.'),
            _('Lines beginning with "#" will be removed'),
            _('To abort checkin, remove the contents of the file '
              'before saving.'),
            _('  On branch %s') % pyrite.repo.branch(),
            _('  '),
            _('Changed Files...'),
            _('  ')]

    try:
        if amend:
            commitdata = pyrite.repo.get_commit_info('HEAD', data)
            if not use_message:
                use_message = commitdata[Repo.SUBJECT] + '\n' + \
                                ''.join(commitdata[Repo.BODY])
            amend = commitdata[Repo.ID]
            del commitdata[Repo.ID]
            if args:
                for f in pyrite.repo.changed_files('HEAD'):
                    args.append(f[1])
            diff = [l for l in pyrite.repo.diff('HEAD^', 'HEAD',
                                                None, binary=True)]
            pyrite.repo.move_head_to('HEAD^')
            pyrite.repo.apply(diff, toindex=True)
        elif args:
            pyrite.repo.move_head_to('HEAD')
        pyrite.repo.update_index(args)

        if sign:
            if not use_message: use_message = ''
            use_message += _('\n\nSigned-off-by: %s\n\n') % \
                                    pyrite.config.get_user()

        if edit:
            for x in pyrite.repo.changed_files():
                if not args or x[1] in args:
                    extra.append('  ' + ' '.join(x))

            if not use_message:
                use_message = '\n'

            new_msg = pyrite.ui.edit(use_message, extra,
                                     pyrite.repo.get_commit_info()[Repo.ID])
            use_message = new_msg

        if not use_message.strip():
            if amend:
                pyrite.repo.move_head_to(amend)
            pyrite.ui.error_out(_('No commit message, aborting'))

        commitdata[Repo.SUBJECT] = use_message
        if Repo.BODY in commitdata:
            del commitdata[Repo.BODY]
        pyrite.repo.commit(commit=commitdata, verify=verify)
        amend = False
    finally:
        if amend and amend != True:
            pyrite.repo.move_head_to(amend)
