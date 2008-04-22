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
from time import gmtime, strftime
help_str =_("""
pyt export [OPTIONS] [firstcommit[..lastcommit]]
pyt export -b <file> | --bundle <file> [firstcommit[..lastcommit]
pyt export -v <file> | --verify <file>
pyt export -a | --archive <commit> [--format tgz | zip] [paths]...

The export command has 3 modes.

Normally it allows you to export specific patches so they can be imported into
another repository/branch.  This is basically a short hand for generating a
diff for each commit and putting into a consistant format.

The compose options allows you to write an additional message that can be used
to preface your patches.

The output file should be the directory where you want to save the export patch
files in.

With the --bundle option, it creates a mini-repository that can be pulled or
fetched from.  This is useful when you cannot use the normal network protocol.
--bundle cannot be used with any other option.

The --verify option verifies a bundle.  It cannot be used with any other
option.

The --archive option will export the working directory (optionally limited by
paths) to a archive file into a tarball (tgz).  You can choose a specific
revision to export.  This flag can only be used with the --format flag which
allows you to export to a zip archive instead of a tarball.  An archive only
contians tracked files.
""")

def _parse_range(args):
    if not args:
        raise HelpError({'command': 'export', 'message': _('Need to specify a '
                         'commit or commit range')})
    first = last = None
    spec = args[0]
    idx = spec.find('..')
    if idx < 0:
        first = spec
    else:
        first = spec[:idx]
        last = spec[idx + 2:]
    return first, last, args[1:]

def _run_patch_export(compose, outdir, numbered, force, args):
    firstcommit = lastcommit = None
    
    firstcommit, lastcommit, args = _parse_range(args)
    
    if compose:
        hist = pyrite.repo.get_history(firstcommit, lastcommit, -1)
        count = 0
        for item in hist:
            count += 1
        endname = lastcommit
        if not endname:
            endname = pyrite.repo.get_commit_info()
        message = pyrite.ui.edit(None, None,
                    'pyt-header-' + firstcommit + '-' + endname[Repo.ID] +
                    '.txt')
        message = message.lstrip()
        idx = message.find(os.linesep)
        title = ''
        if idx > -1:
            title = message[:idx]
            message = message[idx:]
        else:
            title = message
            message = ''

        subject = title
        filename = '0000-' + title
        if len(filename) > 50:
            filename = filename[:50]
        filename = filename.strip()
        filename = filename.replace(' ', '-')
        filename = filename.replace('\t', '-')
        filename = os.path.join(outdir,  filename + '.txt')
        if numbered:
            subject = 'Subject: [PATCH 0/' + str(count) + '] ' + title + '\n'
        else:
            subject = 'Subject: [PATCH] ' + title + '\n'

        mode = 'w'
        if force: mode = '+w'
        fd = open(filename, mode)
        from_field = 'From: ' + pyrite.config.get_user() + '\n'
        date_field = 'Date: ' + strftime("%a, %d %b %Y %H:%M:%S +0000",
                                            gmtime()) + '\n'
        message = from_field + date_field + subject + message
        
        fd.write(message)

    pyrite.repo.export_patch(firstcommit, lastcommit, outdir, force=force,
                        numbered=numbered)

def run(cmd, *args, **flags):
    compose = 'compose' in flags
    outdir = flags.get('output-dir', None)
    numbered = 'numbered' in flags
    force = 'force' in flags
    bundle = flags.get('bundle', None)
    verify = flags.get('verify', None)
    archive = flags.get('archive', None)
    format = flags.get('format', 'tgz')

    if bundle and (verify or compose or outdir or numbered or
                    force or archive):
        raise HelpError({'command': cmd, 'message': _('bundle used with '
                        'incompatable option')})
    if archive and verify or compose or outdir or numbered or force:
        raise HelpError({'command': cmd, 'message': _('archive used with '
                        'incompatable option')})
    if 'format' in flags and not archive:
        raise HelpError({'command': cmd, 'message': _('format used without '
                        'archive')})

    if bundle:
        first, last, args = _parse_range(args)
        pyrite.repo.export_bundle(bundle, first, last)
    elif verify:
        success, reason = pyrite.repo.verify_bundle(verify)
        if success:
            pyrite.ui.info(_('Its good!'))
        else:
            pyrite.ui.error_out(reason)
    elif archive:
        commit = None
        if not args:
            commit = 'HEAD'
        else:
            commit = args[0]
            args = args[1:]
        pyrite.repo.export_archive(archive, commit, paths=args, format=format)
    else:
        _run_patch_export(compose, outdir, numbered, force, args)
    
