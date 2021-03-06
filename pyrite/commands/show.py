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
from pyrite.git.commit import Commit

options = [
('s', 'style', _('use a predefined style'), 0),
('t', 'template', _('specify your own template to use'), 0)
]

help_str =_("""
pyt show [options] [commit | tag] <path>...
pyt show [options] <commit>
pyt show [options] <tag>

The 2nd and 3rd forms of the show command will display the message for a tag or
a commit.  It will display the contents of a file or files for the first form.

If you only supply files, then the default to show is from the current HEAD.
""")

def run(cmd, args, flags, io, settings, repo):
    style = flags.get('style', None)
    template = flags.get('template', None)
    commit = None
    tag = None

    if style and template:
        raise HelpError(cmd, _('"style" and "template" are conflicting '
                               'arguments.'))

    if not args:
        raise HelpError(cmd, _('Need something to show'))
    if args[0] in repo.list_tags():
        tag = args.pop(0)
    elif Commit.is_commit(repo, args[0]):
        commit = args.pop(0)
    else:
        commit = 'HEAD'

    output = repo.show(commit=commit, tag=tag, files=args)

    io.info(output)
