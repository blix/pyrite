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

options = [
('c', 'color', _('Show in color'), 0),
('', 'amend', _('Show what would an ammended commit would do'), 0)
]

help_str =_("""
pyt status [options] [paths]...

The status command shows what the current state of the working directory is.
It is useful to see what would be commited.  Passing the --amend option allows
you to see what would happen if you did a checkin with the --amend flag.  Also
like checkin, you can use paths to limit what is reported by status.
""")

def print_header(color):
    branch = pyrite.repo.branch()
    tag, distance, id = pyrite.repo.describe()

    pyrite.ui.info(_('Currently on branch "%s%s%s"') %
                   ((color and pyrite.UI.bold_color or ''),
                    branch, pyrite.UI.reset_color))

    pyrite.ui.info(_('tip points to %s%s%s') %
                   ((color and pyrite.UI.commit_color or ''), id[:8],
                    pyrite.UI.reset_color))
    if tag:
        pyrite.ui.info(_('You are %d commits ahead of %s') % (distance, tag))
    pyrite.ui.info('')

def run(cmd, args, flags):
    amend = 'amend' in flags
    color = 'color' in flags or \
            pyrite.UI.affirmative(pyrite.config.get_option('pyrite.color'))

    commit = 'HEAD'
    if amend:
        commit = 'HEAD^'

    print_header(color)
    output = pyrite.repo.diff(commit, None, args, detect=True, stat=True,
                                patch=False)

    if color:
        output = pyrite.UI.color_diffstat(output)
    if pyrite.ui.info(''.join(output)):
        pyrite.ui.info('')

    changed = pyrite.repo.list(tracked=False, untracked=True)
    if changed:
        pyrite.ui.info(_('## The following files are neither tracked '
                             'nor ignored'))
        pyrite.ui.info('')

        for f in changed:
            pyrite.ui.info(' ' + f)
        pyrite.ui.info('')

    unresolved = pyrite.repo.get_unresolved()
    if unresolved:
        pyrite.ui.info(_('## The following files need conflict resolution.'))
        pyrite.ui.info('')
        for f in unresolved:
            pyrite.ui.info(' ' + f)

        pyrite.ui.info('')
