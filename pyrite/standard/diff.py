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
pyt diff [options] [startcommit[..endcommit]] [-- paths]

The diff command shows a diff shows differences between 2 commit points.  If
no commit is given, the diff will be between the working set and HEAD.
If one commit is given, the diff will be between the working set and the
commit.  You can specify a set of paths to narrow down the result of the patch.
""")

def run(cmd, *args, **flags):
    stat = flags.has_key('stat')
    color = flags.has_key('color')
    template = flags.get('template', None)
    style = flags.get('style', None)
    detect = flags.get('detect')
    ignorewhite = 'none'
    
    if flags.has_key('ignore-eol'):
        ignorewhite = 'eol'
    if flags.has_key('ignore_whitespace'):
        ignorewhite = 'all'
    
    startcommit = endcommit = None
    if len(args) > 0:
        commits = args[0].split('..')
        startcommit = commits[0]
        if len(commits) == 2:
            endcommit = commits[1]
        args = args[1:]

    if style:
        pass
        #here we look up the style in the pyrite/styles directory
        #if it is a full path then we look at the path
        #we then read the file into the template variable

    pyrite.repo.update_index(None)
    output = pyrite.repo.diff(startcommit, endcommit, args, stat=stat,
                                color=color, template=template, detect=detect,
                                ignorewhite=ignorewhite)

    pyrite.ui.info(line)
