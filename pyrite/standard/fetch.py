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
import os
from time import gmtime, strftime

options = [
('f', 'force', _('allows local branch to be overwritten'), 0),
('n', 'no-tags', _('do not download any tags'), 0),
('d', 'depth', _('maximum number of commits to fetch'), 0)
]

help_str =_("""
pyt fetch [options] <branch>
pyt fetch [options] <localrepo> | <remoterepo> <sourcebranch1>[:destbranch1]...

The fetch command will copy changes from one repository and branch to
the local repository.  A repository can be a local one with a regular file
path or a remote on over the ssh or http protocols.

If no repository is given, then the local repository is used, this is useful
for updating local branches from one another.  If no destination branch is
given, then the current branch is assumed.
""")

def run(cmd, args, flags):
    force = 'force' in flags
    notags = 'no-tags' in flags
    depth = flags.get('depth', -1)
    repo = None
    branchspecs = []
    
    if not args:
        pyrite.utils.io.error_out('Defaults not supported yet, '
                            'specify at least a branch')
    def split_branches(s):
        parts = s.split(':')
        if len(parts) > 1:
            return parts[0], parts[1]
        return (parts[0], '')

    if len(args) == 1:
        branchspecs.append(split_branches(args[0]))
    else:
        repo = args.pop(0)
        branchspecs = [ split_branches(s) for s in args ]

    output = pyrite.repo.fetch(repo, branchspecs, force=force, depth=depth,
                                notags=notags)
    pyrite.utils.io.info(output)
