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
('d', 'delete', _('delete the named branch'), 0),
('f', 'force', _('force creation or deletion'), 0),
('m', 'move', _('rename the branch'), 0),
('r', 'remote', _('list or delete remote-tracking branches'), 0),
('v', 'verbose', _('show detailed information'), 0),
('a', 'all', _('show all branches'), 0),
('s', 'switch', _('Create a branch and switch to it'), 1)
]

help_str=_("""
pyt branch [option] -d | --delete <branch>
pyt branch [option] -m | --move <oldname> <newname>
pyt branch [-f | --force] <newbranch> [startpoint]
pyt branch [-a | --all] | [-r | --remote]
pyt branch -s | --switch <newbranch> [startpoint]

With no arguments given a list of existing branches will be shown, the
current branch will be highlighted with an asterisk. Option -r causes
the remote-tracking branches to be listed, and option -a shows both.

Specifying just a branchame will create a new branch with an optional starting
commit.  Use the force flag to create or rename new branch with an existing
name.  Force can also be used to delete a branch when it has unmerged changes.

The --switch flag will create a branch and switch to it in one step.

The --track and --no-track optons override configuration options.

The branch command will not switch to the new branch, use checkout.
'pyt help checkout' for more.
""")

def run(cmd, args, flags):
    is_verbose = 'verbose' in flags
    is_force = 'force' in flags
    show_remote = 'remote' in flags
    show_all = 'all' in flags
    is_tracking = pyrite.config.get_option('branch.track', False)
    delete = flags.get('delete', None)
    switch = flags.get('switch', None)
    is_move = 'move' in flags

    try:
        if delete:
            pyrite.repo.del_branch(args, is_force)
        elif is_move:
            if len(args) != 2:
                raise HelpError(cmd, _('Need oldbranch and newbranch'))
            pyrite.repo.rename_branch(args[0], args[1], force=is_force)
        elif switch:
            start = 'HEAD'
            if len(args) > 1:
                raise HelpError(cmd, _('Cannot create branch with paths'))
            elif args and pyrite.repo.get_commit_info(args[0]):
                start = args[0]
            pyrite.repo.create_branch(switch, start=start, force=is_force)
            output = pyrite.repo.checkout(switch, force=is_force, is_merge=True)
            for x in output:
                pass #throw away output
        else:
            if len(args) < 1:
                current = pyrite.repo.branch()
                if show_all or not show_remote:
                    for b in pyrite.repo.branches():
                        if b == current:
                            pyrite.ui.info('* ' + b)
                        else:
                            pyrite.ui.info('  ' + b)
                if show_all or show_remote:
                    for r in pyrite.repo.remotes():
                        if r == current:
                            pyrite.ui.info('* ' + r)
                        else:
                            pyrite.ui.info('  ' + r)
            else:
                pyrite.repo.create_branch(args[0], force=is_force,
                                            track=is_tracking)
    except pyrite.repository.RepoError, inst:
        pyrite.ui.error_out(inst)
