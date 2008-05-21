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
('f', 'force', _('force rename even if target exists'), 0),
('i', 'ignore-errors', _('skip operations that result in errors'), 0),
('n', 'no-move', _('do not actually move the file(s)'), 0)
]

help_str =_("""
pyt move [options] <source> <destination>
pyt move [options] <sources>... <destination dir>

The move command will either move a set of existing files/directories to
another directory or it will rename a single existing file or directory. 
""")

def run(cmd, args, flags):
    force = 'force' in flags
    ignore = 'ignore' in flags
    noop = 'no-move' in flags
    
    if len(args) < 2:
        raise HelpError(cmd, _('Need at least a source and a destination'))


    dest = args.pop()

    output = pyrite.repo.move(args, dest, force=force, ignore=ignore,
                                noop=noop)

    pyrite.ui.info(output)
