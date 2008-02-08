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

help_str = _("""
pyt track [-f | --force] [-v | --verbose] [files...]

Start tracking files.  When run without [files], will track all files in the
repository working directory.  Tracking files can be controlled with
pyt config ignore <pattern>, -f can be used to override the ignored setting.
""")

def run(cmd, *args, **flags):
    is_force = flags.has_key('force')
    is_verbose = flags.has_key('verbose')
    
    for line in pyrite.repo.add(is_force, is_verbose, args):
        pyrite.ui.info(line)	

