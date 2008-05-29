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
from pyrite.repository import Repo
from pyrite.utils.help import HelpError

options = [
('f', 'files', _('Revert files in the working directory'), 0),
('u', 'undo', _('Undo a commit by applying a reverse patch'), 1),
('m', 'mainline', _('Undo a commit by applying a reverse patch'), 1),
('e', 'edit', _('Edit the commit message before commiting'), 0),
('n', 'no-commit', _('Prepare the working set but do not commit'), 0)
]

help_str =_("""
pyt revert -f [files]
pyt revert [undo commit options] -u <commit>

The revert command has 2 forms.

The form using -f allows you to undo your changes to your working directory.
The files will be re-checked out from the HEAD commit. (-1, -m, -n are not
compatable with this form)

The form using -u will apply a reverse-commit that undoes the patch of an
existing commit.  -e, -m and -n can only be used with this form.
""")

def run(cmd, args, flags, io, settings, repo):
    commit = flags.get('undo', None)
    files = 'files' in flags
    edit = 'edit' in flags
    dryrun = 'no-commit' in flags
    mainline = flags.get('mainline', None)

    if files and (commit or edit or dryrun or mainline):
        raise HelpError(cmd, _('-f/--files cannotbe used with any other '
                               'argument'))
    if (dryrun or edit or mainline) and not commit:
        raise HelpError(cmd, _('missing -u/--undo <commit>'))

    if files:
        changed = repo.changed_files()
        if not changed:
            io.info(_('No files can be reverted, working directory '
                             'is clean.\n\n'))
            return
        if args:
            for l in repo.checkout('HEAD', paths=args):
                pass
        else:
            repo.move_head_to('HEAD', True)

        changed = changed - repo.changed_files()
        if changed:
            io.info(_('Reverted the following files:'))
            for status, filename in changed:
                io.info(filename)
        else:
            io.info(_('No files reverted.'))
    else:
        if not commit:
            raise HelpError(cmd, _('No action chosen! You must use either '
                                   '-f or -c'))
        c = repo.get_commit_info(commit, [Repo.ID, Repo.SUBJECT])
        message = [
            _('Revert: '), c[Repo.SUBJECT],
            '\n\n This reverts commit', c[Repo.ID], '\n\n'
        ]

        if edit:
            extra = [
                _('This is a commit message.'),
                _('Lines beginning with "#" will be removed'),
                _('To abort checkin, do not save this file'),
                _('  ')
            ]

            message = io.edit(message, extra, 'revert-' + c[Repo.ID])
            if not message:
                io.error_out(_('No commit message, aborting.'))

        output = repo.revert(commit, dryrun=dryrun, mainline=mainline)
        for line in output:
            io.info(line)
