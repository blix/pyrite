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
('n', 'no-checkout', _('no checkout of HEAD is done after clone'), 0),
('b', 'bare', _('clone target dir is the git dir'), 0),
('d', 'depth', _('create a shallow clone up to depth'), 0)
]

help_str =_("""
pyt clone [OPTIONS] <source> [targetdir]

The clone command creates a new copy of the source repository.  You can use
--bare to create a repository suitable for pushing to and --depth to limit
the amount of history to fetch.  --no-checkout does not checkout HEAD to
the new working directory.  A remote branch "origin" will be created to 
track the changes from the original repository.

If the targetdir is not supplied, pyt will try and use the name of the source
repository.
""")

def run(cmd, args, flags, io, settings, repo):
    is_bare = flags.has_key('bare')
    depth = flags.get('depth', -1)
    checkout = not flags.has_key('no-checkout')

    if len(args) < 1:
        raise HelpError(cmd, _('Missing source repo'))
    source = args[0]

    if len(args) > 1:
        target = args[1]

    output = repo.clone(source, directory=target, bare=is_bare,
                                depth=depth, checkout=checkout)
    for line in output:
        io.info(line)
