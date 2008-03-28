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
pyt show [options] [commit | tag] <path>...
pyt show [options] <commit>
pyt show [options] <tag>

The 2nd and 3rd forms of the show command will display the message for a tag or
a commit.  It will display the contents of a file or files for the first form.

If you only supply files, then the default to show is from the current HEAD.
""")

def run(cmd, *args, **flags):
    style = flags.get('style', None)
    template = flags.get('template', None)
    commit = None
    tag = None
    files = []
    
    if style and template:
        raise HelpError({'command':cmd, 'message': _('"style" and "template"'
                            ' are conflicting arguments.')})
    
    if not args:
        raise HelpError({'command':cmd, 'message':
                        _('Need something to show')})
    if args[0] in pyrite.repo.list_tags():
        tag = args[0]
        if len(args) > 1:
            files = args[1:]
    elif pyrite.repo.get_commit_info(args[0]):
        commit = args[0]
        if len(args) > 1:
            files = args[1:]
    else:
        commit = 'HEAD'
        files = args

    output = pyrite.repo.show(files, commit=commit, tag=tag)

    pyrite.ui.info(output)
