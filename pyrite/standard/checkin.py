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
import os

help_str="""
pyt checkin [-m | --message <message>]
            [-a | --author <author>] [-s | --signoff] [-s | --signoff]
            [-v | --verbose] [-n | --no-verify] [--no-edit]
            
            [-c | --commit <commit>]
            
pyt checkin [-s | --signoff] [-v | --verbose] [-n | --no-verify]
            [-a | --author] --amend

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

def run(cmd, *args, **flags):
    use_commit = flags.get('commit', None)
    use_author = flags.get('author', None)
    use_message = flags.get('message', None)
    edit = not flags.has_key('no-edit')
    amend = flags.has_key('amend')
    sign = flags.has_key('signoff')
    verify = not flags.has_key('no-verify')
    verbose = flags.has_key('verbose')

    if use_commit and use_message:
        raise HelpError({'command': cmd, 'message':
                         _('Cannot specify commit and message')})
    elif use_commit:
        use_message, use_author = repo.get_commit_info(use_commit)
    elif amend:
        use_message, use_author = repo.get_commit_info('HEAD')

    extra = [_('This is a commit message.'),
            _('Lines beginning with "#" will be removed'),
            _('To abort checkin, do not save this file'),
            _('  On branch %s') % pyrite.repo.branch(),
            _('  '),
            _('Changed Files...'),
            _('  ')]

    for x in pyrite.repo.changed_files():
        extra.append('  ' + ' '.join(x))

    if edit:
        if not use_message: use_message = '\n'
        f = os.path.join(pyrite.repo.get_repo_dir(),
                     'pyt-edit-' + pyrite.repo.get_head_sha())
        new_msg = pyrite.ui.edit(use_message, extra, f)
        if new_msg == use_message:
            pyrite.ui.info(_('Message unchanged. Aborting checkin'))
            return
        use_message = new_msg

    if not use_message: raise HelpError({'command': cmd, 'message': 
                                            _('No commit message')})
    if sign:
        use_message += '\n\tSigned-off-by:' + pyrite.config.get_user() + '\n'

    pyrite.repo.update_index()
    pyrite.repo.commit(use_message, use_author, verify=verify, commit=use_commit)

