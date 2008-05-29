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

import pyrite, os
from pyrite.standard.help import HelpError

options = [
    ('t', 'tool', _('tool to use for merge'), 1),
    ('f', 'file', _('file to resolve merge'), 1)
]

help_str =_("""
pyt resolve [-t | --tool "<tool and options"] [-f file]

The resolve command will help you resolve merge conflicts.  Thes conflicts
can happen any time you merge, rebase or even when you switch branches.

You will need to use an external tool to do the actual conflict resolution.
You can specify this tool with the --tool option or with the pyrite.mergetool
configuration option.  The tool will need to be able to handle 3-way merges.
You can specify the tool as follows:

"/path/to/mymergetool {base} {mine} {theirs} {result}"


When mymergetool is run, {base}, {mine} and {theirs} will be replaced with
the paths to different versions of the file for merging.

Some tools, like meld, do not take a base file, so it is optional.  For example
you can do the following if meld is in your path.

pyt resolve -t "meld {mine} {result} {theirs}" -f foo

which will cause Pyrite to launch meld to do the merge.
""")

def run(cmd, args, flags):
    f = flags.get('file', None)
    toolspec = flags.get('tool', pyrite.config.get_option('pyrite.mergetool'))

    files_to_resolve = pyrite.repo.get_unresolved()

    if f and not f in files_to_resolve:
        pyrite.utils.io.error_out(_('%s does not need to be resolved') % f)

    if f:
        files_to_resolve = {f:'M'}

    if not files_to_resolve:
        pyrite.utils.io.info(_('No files to resolve.'))
        import sys
        sys.exit(0)

    if not toolspec:
        toolspec = 'vimdiff -f -- {mine} {result} {theirs}'

    for f in files_to_resolve.keys():
        base = None
        mine = None
        theirs = None
        try:
            dummy, tail = os.path.split(f)
            base = os.path.join(pyrite.repo.get_repo_dir(), 'base-' + tail)
            if not pyrite.repo.cat_file(f, cat_to=base, commit=':1'):
                base = None

            mine = os.path.join(pyrite.repo.get_repo_dir(), 'mine-' + tail)
            if not pyrite.repo.cat_file(f, cat_to=mine, commit=':2'):
                mine = None

            theirs = os.path.join(pyrite.repo.get_repo_dir(), 'theirs-' + tail)
            if not pyrite.repo.cat_file(f, cat_to=theirs, commit=':3'):
                theirs = None

            if not mine or not theirs:
                pyrite.utils.io.error_out(_('Could not get all versions of file %s')
                                    % f)
            if not base:
                base = ''
            cmd = toolspec.replace('{base}', '"' + base + '"')
            cmd = cmd.replace('{mine}', '"' + mine + '"')
            cmd = cmd.replace('{theirs}', '"' + theirs + '"')
            cmd = cmd.replace('{result}', '"' +
                              os.path.join(pyrite.repo.get_work_dir(), f)
                              + '"')
            os.system(cmd)

            answer = pyrite.utils.io.ask(_('Accept Merge'), ['y', 'n'], 'y')
            if answer == 'y':
                for l in pyrite.repo.add_files(False, False, [f]):
                    pass
        finally:
            if base:
                os.remove(base)
            if mine:
                os.remove(mine)
            if theirs:
                os.remove(theirs)
