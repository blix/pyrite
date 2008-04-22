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

help_str = _("""
pyt checkout [-f | --force] <commit> [path1] [path2] [path3]...

Update the working directory or files specified by paths to the <commit>.
<commit> can be any commit, tag or branch.

When <commit> is a branch with no paths, it checks out and switches to that
branch.  The --branch flag will create a branch and switch to it in one step.
""")

def run(cmd, *args, **flags):
    is_force = False
    is_merge = False
    if flags.has_key('force'):
        is_force = True
    if flags.has_key('merge'):
        is_merge = True

    if len(args) < 1: raise HelpError({'command': cmd, 'message':
                                        'Need a commit'})
    for line in pyrite.repo.checkout(args[0], is_merge, paths=args[1:]):
        pyrite.ui.info(line)

