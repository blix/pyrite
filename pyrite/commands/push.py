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

options = [
('a', 'all', _('push all heads'), 0),
('t', 'all-tags', _('push all tags'), 0),
('f', 'force', _('allows remote brach to be overwritten'), 0),
('v', 'verbose', _('show extra output'), 0)
]
help_str =_("""
pyt push [-a] [-t] [-f] [-v] [targetrepo] [localsource[:targetbranch]]

The push commands updates another repository.  This is normally a repository
on another machine over the network, but it can be used between two local
repositories.  [localsource] can be anything that evaluates to a commit in
the local repository such as an (abbreviated) sha1 for a commit, branch, tag
or symbolic name such as HEAD^.  [targetbranch] is the name of a head on 
the remote repository, if you specify a non-existing name you can create a
new branch.  Specifying ":<targetbranch> will delete the branch on the
remote server.  Defaults and names for remotes can be set with pyt config.

If you do not specify a targetbranch, it will use the name of the checked-
out branch.  If you do not specify localsource or targetbranch, then all
heads that exist in both repositories will be update.
""")

def run(cmd, args, flags, io, settings, repo):
    is_all = flags.has_key('all')
    all_tags = flags.has_key('all-tags')
    is_force = flags.has_key('force')
    is_verbose = flags.has_key('verbose')
    repo = 'origin'
    source = target = None
    
    if len(args) > 2:
        raise HelpError(cmd, _('Wrong number of arguments'))
                        
    if args:
        repo = args.pop(0)
    if args:
        refspec = args[0].split(':')
        if len(refspec) > 2:
            raise HelpError(cmd, _('Invalid ref spec'))
        source = target = refspec[0]
        if len(refspec) > 1:
            target = refspec[1]
    output = repo.push(repo, source, target, force=is_force,
                                all_branches=is_all, all_tags=all_tags,
                                verbose=is_verbose)
    for line in output:
        io.info(line)
