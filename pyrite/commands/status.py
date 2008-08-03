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
from pyrite.utils.help import HelpError

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

def print_header(color, io, repo):
    branch = repo.branch()
    tag, distance, id = repo['HEAD'].describe()

    io.info(_('Currently on branch "%s%s%s"') %
                   ((color and pyrite.utils.io.bold_color or ''),
                    branch, pyrite.utils.io.reset_color))

    io.info(_('tip points to %s%s%s') %
                   ((color and pyrite.utils.io.commit_color or ''), id[:8],
                    pyrite.utils.io.reset_color))
    if tag:
        io.info(_('You are %d commits ahead of %s') % (distance, tag))
    io.info('')

def run(cmd, args, flags, io, settings, repo):
    amend = 'amend' in flags
    color = 'color' in flags or \
            pyrite.utils.io.affirmative(settings.get_option('pyrite.color'))

    commit = 'HEAD'
    if amend:
        commit = 'HEAD^'

    print_header(color, io, repo)
    output = repo.diff(commit, None, args, detect=True, stat=True,
                                patch=False)

    if color:
        output = io.color_diffstat(output)
    if io.info(''.join(output)):
        io.info('')

    changed = repo.list(tracked=False, untracked=True)
    if changed:
        io.info(_('## The following files are neither tracked '
                             'nor ignored'))
        io.info('')

        for f in changed:
            io.info(' ' + f)
        io.info('')

    unresolved = repo.get_unresolved()
    if unresolved:
        io.info(_('## The following files need conflict resolution.'))
        io.info('')
        for f in unresolved:
            io.info(' ' + f)

        io.info('')
