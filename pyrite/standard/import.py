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
import os

options = [
('b', 'bundle', _('Import a bundle.'), 1),
('i', 'interactive', _('Run interactively.'), 0),
('s', 'signoff', _('Add Signed-off-by line to message.'), 0),
('', 'skip', _('Skip the current patch.'), 0),
('', 'resolved', _('Current patch conflict is resolved'), 0)
]

help_str =_("""
pyt import [options] <exportfile>|<exportfiledir>
pyt import -b <file>

The import command allows you import pyt exported patch files as well as pyt
bundle files.  These should be compatable with files generated by
git-format-patch and git-bundle.

When there is a confilcting patch, --skip and --resolved can be used to
continue operation.

Interactive mode allows inspection of the patch and editing of the commit
message.
""")

def _read_pending(import_file):
    f = open(import_file, 'r')
    files = [ line.strip() for line in f.readlines() ]
    return files

def run(cmd, *args, **flags):
    bundle = flags.get('bundle', None)
    is_interactive = 'interactive' in flags
    sign = 'signoff' in flags
    skip = 'skip' in flags
    resolved = 'resolved' in flags
    directory = None
    files = []
    
    if bundle and (is_interactive or sign or skip or resolved):
        raise HelpError(cmd, _('Bundle cannot be used with any other '
                               'arguments'))

    if bundle:
        pyrite.repo.import_bundle(bundle, args)
        pyrite.ui.info(_('Bundle successfully imported'))
        return

    if len(args) < 1 and not skip and not resolved:
        raise HelpError(cmd, _('Missing file(s) or directory'))
    if len(args) == 1:
        if os.path.exists(args[0]) and os.path.isdir(args[0]):
            directory = args[0]
            files = os.listdir()
    else:
        files = args

    import_file = os.path.join(pyrite.repo.get_repo_dir(), 'import_status')
    import_file_exists = os.path.exists(import_file)
    if import_file_exists and not skip and not resolved:
        pyrite.ui.error_out(_('Import in progress, run with --skip or'
                                ' --resolve'))
    if skip:
        if not import_file_exists:
            pyrite.ui.error_out(_('No pending import; nothing to skip'))
        files = _read_pending(import_file)
        if len(files) > 1:
            files = args[1:]
        if not files:
            os.remove(import_file)
            return

    if resolved:
        if not import_file_exists:
            pyrite.ui.error_out(_('No pending import; nothing to '
                                    'apply resolved'))
        files = _read_pending(import_file)

    if is_interactive:
        pass

    if import_file_exists:
        os.remove(import_file)
    
    status = True
    f = message = None
    for filename in files:
        if not os.path.isfile(filename):
            pyrite.ui.error_out(_('%s does not exits') % filename)
        if not status:
            f.write(filename + '\n')
            continue
        status, message = pyrite.repo.import_patch(filename, sign=sign)
        if not status:
            f = open(import_file, 'w+')
            f.write(filename + '\n')

    if not status:
        pyrite.ui.error(message)
        pyrite.ui.error_out(_('failed to apply %s, run with --skip to skip '
                            'or --resolve to fix the conflict and complete '
                            'the import.') % filename )

