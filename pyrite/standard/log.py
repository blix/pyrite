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
from pyrite.repository import Repo
from pyrite.template import FileTemplate, Template

help_str=_("""
pyt log [options] [firstcommit[..[lastcommit]]] [paths]...

The log command is used to show the history for commits.  A range can be
specified using either commit IDs or symbolic names. If no range is specified
then the history of the current branch is shown.  If only a single commit is
given then the history of that commit is shown.  If the range is given as
<commit>.. then all decendents of <commit> are shown.  Finally, if you specify
2 commits, then you will see the history between those 2 commits.

You can also limit the history searched to a one or more paths.
""")

def run(cmd, *args, **flags):
    style = flags.get('style', None)
    template = flags.get('template', 'normal_log')
    limit = flags.get('limit', 10)
    show_patch = flags.has_key('patch')
    follow = flags.has_key('follow-renames')
    if flags.has_key('all'):
        limit = -1
    
    if flags.has_key('style') and flags.has_key('template'):
        raise HelpError({'command': cmd, 'message':
                        _('"style" and "template" are redundant.')})
                        
    if flags.has_key('limit') and flags.has_key('all'):
        raise HelpError({'command': cmd, 'message':
                        _('"limit" and "all" conflict.')})

    first = last = None
    paths = None
    if len(args) > 0:
        idx = args[0].find('..')
        if idx < 0:
            first = args[0]
            if not pyrite.repo.get_commit_info(first):
                raise HelpError({'command': cmd, 'message':
                    _('Cannot resolve %s to a commit') % first})
        else:
            first = args[0][:idx]
            last = args[0][idx + 2:]
        paths = args[1:]

    formatter = None
    if style:
        formatter = Template(style)
    else:
        formatter = FileTemplate(template)

    data = formatter.compile()
    if not show_patch and Repo.PATCH in data:
        data.remove(Repo.PATCH)
    output = pyrite.repo.get_history(first, last, limit, data=data,
                                       follow=follow, paths=paths)

    for commit_data in output:
        formatter.generate(commit_data, pyrite.repo)

    pyrite.ui.raw_write('\n')