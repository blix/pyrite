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

The export command allows you to export specific patches so they can be
imported into another repository/branch.  This is basically a short hand for
generating a diff for each commit and putting into a consistant format.

The compose options allows you to write an additional message that can be used
to preface your patches.

The output file should be the directory where you want to save the export patch
files in.
""")

def run(cmd, *args, **flags):
    compose = flags.has_key('compose')
    outdir = flags.get('output-dir', '.')
    numbered = flags.has_key('numbered')
    force = flags.has_key('force')
    firstcommit = lastcommit = None
    
    if len(args) < 1:
        raise HelpError({'command': cmd,
                        'message':
                            _('Need to specify a commit or commit range')})
    idx = args[0].find('..')
    if idx < 0:
        firstcommit = args[0]
    else:
        firstcommit = args[0][:idx]
        lastcommit = args[0][idx + 2:]

    if compose:
        hist = pyrite.repo.get_history(firstcommit, lastcommit, -1)
        count = 0
        for item in hist:
            count += 1
        endname = lastcommit
        if not endname:
            endname = pyrite.repo.get_head_sha()
        message = pyrite.ui.edit(None, None,
                    'pyt-header-' + firstcommit + '-' + endname + '.txt')
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

