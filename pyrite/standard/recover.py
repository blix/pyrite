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

options = [
('s', 'show-reflog', _('Show what can be recovered from the reflog.'), 0),
('c', 'commit', _('What to recover, set the current "tip" to this.'), 1),
('f', 'force', _('Force even if working directory is dirty.'), 0)
]

help_str =_("""
pyt recover -s | --show-reflog
pyt recover [-f | --force] -c | --commit <commit>

The recover command is used to reset the current branch to a particular
state.  You can use it to rollback the changes on the current branch to
an existing commit.

The true usefulness of this command is when you have been editing your
history and you realize that your current state is bad and you want to get
back to a previous state.  You can use this command to recover that state if
you know the commit id.

Knowing the id of a commit that no longer exists on any branch is difficult
unlsess you have it written down somewhere.  Fortunately, your local changes
are written to the "reflog."  The reflog contains the recent history of
local changes to the repository.  You can use the "-r" flag to see what is
available from the reflog.

Note that commits are not kept around indefinately.  If a commit is not on
any branch or referenced by a tag then it will eventually be removed from
the repository.  This does not happen for several weeks to allow the user
time to recover those commits if they need to.
""")
    
def run(cmd, args, flags):
    force = 'force' in flags
    commit = flags.get('commit')
    show_reflog = 'show-reflog' in flags

    if not show_reflog and not commit:
        raise HelpError(cmd, _('No action specified.\nUse "--show-reflog" '
                               'or "--commit <commit>" to take an action.'))

    c = pyrite.repo.get_commit_info(commit, [Repo.ID])
    if not c:
        raise HelpError(_('%s does not appear to be a commit.') % commit)

    if not force:
        dirty = pyrite.repo.changed_files()
        if dirty:
            raise HelpError(_('Your working directory has changes, if you'
                              'want to lose them, use "--force"'))

    if show_reflog:
        from pyrite.template import Template
        template = Template('{ID|short} {AUTHOR_DATE|humandate} '
                            '{SUBJECT|short:length=50}\n', False)
        data = template.compile()
        output = pyrite.repo.get_history(None, None, -1, data, reflog=True)
        for c in output:
            template.write_to_stream(c, pyrite.ui.info_stream())
        return

    branch = pyrite.repo.branch()
    id = pyrite.repo.get_commit_info('HEAD', [Repo.ID])[Repo.ID][:8]
    pyrite.repo.move_head_to(c[Repo.ID], True)
    pyrite.ui.info(_('You are on branch "%s", its tip was "%s".') %
                   (branch, id))
    pyrite.ui.info(_('Run "pyt recover -c %s" to undo.') % id)
    c = pyrite.repo.get_commit_info(commit, [Repo.ID])
    pyrite.ui.info(_('Tip now points to "%s"') % c[Repo.ID])
    pyrite.ui.info('')
