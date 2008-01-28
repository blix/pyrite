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

help_str = """
This command creates an empty pyt repository. An initial HEAD
file that references the HEAD of the master branch is also created.

Running pyt init in an existing repository is safe. It will not
overwrite things that are already there."""
            
def run(cmd, *args, **flags):
    pyrite.repo.init()

