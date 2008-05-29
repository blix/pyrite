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

options = [('v', 'verbose', _('print full help and aliases'), 0)]

help_str="""
pyt help <command>

Shows list of commands or help for a command.
"""

def run(cmd, args, flags):
    if 'verbose' in flags:
        raise HelpError(verbose=True)
    if args:
        raise HelpError(args[0])
    raise HelpError(cmd)
