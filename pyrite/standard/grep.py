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
import sys

help_str =_("""
pyt grep [options] <pattern> <paths>...

The grep command is a useful tool for searching your project for patterns.
You can also choose to search previous revisions without having to check
them out.
""")

def run(cmd, *args, **flags):
    ignore = 'ignore-case' in flags
    whole = 'whole-word' in flags
    no_bin = 'no-binary' in flags
    invert = 'invert' in flags
    full_path = 'full-path' in flags
    no_name = 'no-name' in flags
    basic = 'basic-string' in flags
    count = 'count' in flags
    commit = flags.get('revision', None)

    if full_path and no_name:
        raise HelpError({'command': cmd, 'message':
            _('Cannot use both --full-path and --no-name')})

    path = False
    if full_path:
        path = True
    if no_name:
        path = None

    if not args:
        raise HelpError({'command': cmd, 'message':
            _('Need a pattern to search for')})

    pattern = args[0]
    args = args[1:]

    found_matches = False
    for line in pyrite.repo.grep(pattern, args, commit=commit, ignore=ignore,
                                 whole=whole, ignore_binary=no_bin,
                                 invert=invert, path=path, not_regex=basic,
                                 count=count):
        pyrite.ui.info(line)
        found_matches = True
    if not found_matches:
        sys.exit(128)
