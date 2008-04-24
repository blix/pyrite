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
help_str =_("""
pyt status [options] [paths]...

The status command shows what the current state of the working directory is.
It is useful to see what would be commited.  Passing the --amend option allows
you to see what would happen if you did a checkin with the --amend flag.  Also
like checkin, you can use paths to limit what is reported by status.
""")

def run(cmd, *args, **flags):
    amend = 'amend' in flags
    color = 'color' in flags

    commit = 'HEAD'
    if amend:
        commit = 'HEAD^'

    output = pyrite.repo.diff(commit, None, args, detect=True, stat=True,
                                patch=False)

    did_print = pyrite.ui.info(output)

    first = True
    for f in pyrite.repo.get_untracked():
        if first:
            if did_print:
                pyrite.ui.info('\n')
            pyrite.ui.info(_('## The following files are neither tracked '
                             'nor ignored\n'))
            first = False
        pyrite.ui.info(f)
    if not first or (first and did_print):
        pyrite.ui.info('\n')
