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
('f', 'force', _('allows local branch to be overwritten'), 0),
('n', 'no-tags', _('do not download any tags'), 0),
('e', 'extra-tags', _('download all tags even those not tracked'), 0),
('d', 'depth', _('maximum number of commits to fetch'), 1),
('', 'no-commit', _('merge the working set without commiting'), 0),
('s', 'summary', _('show a diffstat at the end of the merge'), 0),
('r', 'rebase', _('local changes are moved on top of pulled changes'), 0)
]

help_str =_("""
pyt pull [options] <sourcerepo> [sourcebranch[:targetbranch]]

The pull commands fetches history from the sourcerepo and merges it.
""")

def run(cmd, *args, **flags):
    is_force = flags.has_key('force')
    tags = not flags.has_key('no-tags')
    extra_tags = flags.has_key('extra-tags')
    depth = flags.get('depth', -1)
    commit = not flags.has_key('no-commit')
    print_summary = flags.has_key('summary')
    is_rebase = flags.has_key('rebase')
    repo = 'origin'
    source = target = None
    
    if (not tags) and extra_tags:
        raise HelpError(cmd, _('no-tags and extra-tags are conflicing '
                               'arguments'))
    elif tags:
        tags = 'normal'
    elif extra_tags:
        tags = 'extra'
    else:
        tags = 'none'

    if len(args) > 0:
        repo = args[0]
    if len(args) > 1:
        refspec = args[1].split(':')
        if len(refspec) > 2:
            raise HelpError(cmd, _('Invalid ref spec'))
        source = target = refspec[0]
        if len(refspec) > 1:
            target = refspec[1]
            
    output = pyrite.repo.pull(repo, source, target, force=is_force, tags=tags,
                                depth=depth, commit=commit, rebase=is_rebase)
    for line in output:
        pyrite.ui.info(line)
