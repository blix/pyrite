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

options = [('v', 'verbose', _('output extra information'), 0)]

help_str =_("""
pyt verify [-v | --verbose]

Verify checks the validity of the repository and reports any problems.
""")

def run(cmd, args, flags, io, settings, repo):
    output = repo.verify(flags.has_key('verbose'))
    io.info(output)
