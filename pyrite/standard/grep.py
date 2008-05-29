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
import sys

options = [
('i', 'ignore-case', _('ignore case differences'), 0),
('w', 'whole-word', _('match whole word'), 0),
('n', 'no-binary', _('do not match against binary files'), 0),
('v', 'invert', _('invert match'), 0),
('f', 'full-path', _('print the full path to the file'), 0),
('', 'no-name', _('do not print the path/name of the file'), 0),
('b', 'basic-string', _('match string is not a regex'), 0),
('c', 'count', _('print the number of matches per file'), 0),
('r', 'revision', _('match against the supplied revision'), 1)
]

help_str =_("""
pyt grep [options] <pattern> <paths>...

The grep command is a useful tool for searching your project for patterns.
You can also choose to search previous revisions without having to check
them out.
""")

def run(cmd, args, flags, io, settings, repo):
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
        raise HelpError(cmd, _('Cannot use both --full-path and --no-name'))

    path = False
    if full_path:
        path = True
    if no_name:
        path = None

    if not args:
        raise HelpError(cmd, _('Need a pattern to search for'))

    pattern = args.pop(0)

    found_matches = False
    for line in repo.grep(pattern, args, commit=commit, ignore=ignore,
                                 whole=whole, ignore_binary=no_bin,
                                 invert=invert, path=path, not_regex=basic,
                                 count=count):
        io.info(line)
        found_matches = True
    if not found_matches:
        sys.exit(128)
