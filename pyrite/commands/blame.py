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
from pyrite.git.repository import Repo
from pyrite.utils.template import Template
from pyrite.utils.help import HelpError

options = [
('l', 'long', _('show long rev'), 0),
('c', 'commit', _('show the file from its state in this commit'), 1),
('s', 'start-line', _('start showing at this line number'), 1),
('e', 'end-line', _('don\'t show after this line number'), 1)
]

help_str =_("""
pyt blame [options] file

The blame command shows information about when and by whom lines in a file
were authored.  You can limit the output to certain lines and/or get
information based on a different revision of the file.

--end-line can only be used if --start-line is specified.  if end-line has
a "+" or "-" infront of it, it will be used as a range from start-line.
""")

def run(cmd, args, flags, io, settings, repo):
    use_long = 'long' in flags
    commit = flags.get('commit', None)
    start = flags.get('start-line', None)
    end = flags.get('end-line', None)

    if not args:
        raise HelpError(cmd, _('Need a file to view'))

    if end and not start:
        raise HelpError(cmd, _('Need a file to view'))

    style = None
    if use_long:
        style = '{ID}'
    else:
        style = '{ID|short}'
    style += ' ({AUTHOR} {AUTHOR_DATE|humandate} {LINENO}) {LINE}'

    template = Template(style)
    template.compile()
    gen = repo.blame(args[0], commit=commit, startline=start,
                            endline=end)
    for lineno, c, line, orig_lineno in gen:
        c['LINE'] = line
        c['LINENO'] = lineno
        io.info(template.get_complete(c))
