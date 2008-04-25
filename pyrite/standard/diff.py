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
('r', 'revision-start', _('revision to use as base for comparison'), 1),
('R', 'revision-end', _('revision to diff against revision-start'), 1),
('s', 'stat', _('show a diffstat'), 0),
('c', 'color', _('show colored diff'), 0),
('d', 'detect', _('detect renames and copies'), 0),
('e', 'ignore-eol', _('ignore end of line whitespace differences'), 0),
('w', 'ignore-whitespace', _('ignore all whitespace'), 0)
]

help_str =_("""
pyt diff [OPTIONS] [-- paths]

The diff command shows a diff shows differences between 2 commit points.  If
no --revision-start commit is given, the diff will be between the working set
and HEAD.  Giving --revision-start or --revision-end but not both will diff
be between the working set and the commit.  You can specify a set of paths
to narrow down the result of the patch.
""")

def run(cmd, *args, **flags):
    stat = flags.has_key('stat')
    color = flags.has_key('color')
    detect = flags.get('detect')
    startcommit = flags.get('revision-start', 'HEAD')
    endcommit = flags.get('revision-end', None)
    ignorewhite = 'none'

    if flags.has_key('ignore-eol'):
        ignorewhite = 'eol'
    if flags.has_key('ignore_whitespace'):
        ignorewhite = 'all'

    output = pyrite.repo.diff(startcommit, endcommit, args, stat=stat,
                                detect=detect, ignorewhite=ignorewhite)

    pyrite.ui.info(output)
