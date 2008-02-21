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

help_str=_("""
pyt branch [option] -d | --delete <branch>
pyt branch [option] -m | --move <oldname> <newname>
pyt branch [-f | --force] <newbranch> [startpoint]
pyt branch [-a | --all] [-r | --remote]

With no arguments given a list of existing branches will be shown, the
current branch will be highlighted with an asterisk. Option -r causes
the remote-tracking branches to be listed, and option -a shows both.

Specifying just a branchame will create a new branch with an optional starting
commit.  Use the force flag to create or rename new branch with an existing
name.  Force can also be used to delete a branch when it has unmerged changes.

The --track and --no-track optons override configuration options.

The branch command will not switch to the new branch, use checkout.
'pyt help checkout' for more.
""")

def run(cmd, *args, **flags):
    is_verbose = False
    is_force = False
    is_remote = False
    is_all = False
    is_tracking = pyrite.config.get_option('branch.track', False)
    
    if flags.has_key('all'):
        is_all = True
    if flags.has_key('track'):
        is_track = True
    if flags.has_key('no-track'):
        is_track = False
    if flags.has_key('verbose'):
        is_verbose = True
    if flags.has_key('remote'):
        is_remote = True
    if flags.has_key('force'):
        is_force = True
    try:
        if flags.has_key('delete'):
            pyrite.repo.del_branch(args, is_force)
        elif flags.has_key('move'):
            if len(args) != 2:
                raise HelpError({'command': cmd, 'message':
                                    _('Need oldbranch and newbranch')})
            pyrite.repo.rename_branch(args[0], args[1], is_force)
        else:
            if len(args) < 1:
                branches = []
                if is_all or not is_remote:
                    branches.extend(pyrite.repo.branches())
                if is_all or is_remote: branches.extend(pyrite.repo.remotes())
                current = pyrite.repo.branch()
                for b in branches:
                    if b == current:
                        print '* ' + b
                    else: print '  ' + b
            else:
                pyrite.repo.create_branch(args[0], is_force, is_tracking)
    except pyrite.repository.RepoError, inst:
        pyrite.ui.error_out(inst)
