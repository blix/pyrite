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
        raise HelpError({'command': cmd,'message':
                _('no-tags and extra-tags are conflicing arguments')})
    elif tags: tags = 'normal'
    elif extra_tags: tags = 'extra'
    else: tags = 'none'

    if len(args) > 0:
        repo = args[0]
    if len(args) > 1:
        refspec = args[1].split(':')
        if len(refspec) > 2:
            raise HelpError({'command':cmd, 'message':
                            _('Invalid ref spec')})
        source = target = refspec[0]
        if len(refspec) > 1:
            target = refspec[1]
            
    output = pyrite.repo.pull(repo, source, target, force=is_force, tags=tags,
                                depth=depth, commit=commit, rebase=is_rebase)
    for line in output:
        pyrite.ui.info(line)
