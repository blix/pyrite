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
('f', 'force', _('remove even if modified'), 0),
('n', 'no-remove', _('do not actually remove the file(s)'), 0),
('u', 'untrack', _('do not remove the file(s), just stop tracking them'), 0),
('r', 'recursive', _('remove recursively'), 0)
]

help_str =_("""
pyt rm [options] <source> <destination>

The rm command will remove a file from both the repository and the disk.  The
command can also be used to mark a file deleted in the repository but not
actually remove it from the disk.
""")

def run(cmd, *args, **flags):
    force = 'force' in flags
    recurse = 'recursive' in flags
    noop = 'no-remove' in flags
    untrack = 'untrack' in flags
    
    if not args:
        raise HelpError(cmd, _('Need at least a source and a destination'))

    output = pyrite.repo.delete(args, force=force, recursive=recurse,
                                noop=noop, cached=untrack)

    pyrite.ui.info(output)
