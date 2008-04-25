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

# this should probably be done such that you can give the patches rather than
# a two step process to gen the patch files and then send them

options = []

help_str =_("""
pyt email <files>...

The email command is a convenient way of sending patches over email.  Often
normal mail programs can make sending patches difficult because they try and
format the email to make it look nice.  It is also convenient for sending a
patch series, since it minimizes the work that needs to be done.
""")


def run(cmd, *args, **flags):

    startcommit = endcommit = None
    if len(args) > 0:
        commits = args[0].split('..')
        if pyrite.repo.get_commit_info(commits[0]):  
            startcommit = commits[0]
            if len(commits) == 2:
                endcommit = commits[1]
            args = args[1:]
    else:
        startcommit = 'HEAD'

    buf = [
        _('From: ') + pyrite.config.get_option('user.name') + ' <' +
                    pyrite.config.get_option('user.email') + '>\n',
        _('SMTP-Server: ') +  pyrite.config.get_option('sendemail.smtpserver')
                            + '\n',
        _('SMTP-User: ') + pyrite.config.get_option('sendemail.smtpuser')
                            + '\n',
        _('SMTP-Password: ') + pyrite.config.get_option('sendemail.smtppass')
                            + '\n',
        _('SMTP-Port: ') + pyrite.config.get_option('sendemail.smtpport')
                            + '\n',
        _('SSL: ') + pyrite.config.get_option('sendemail.smtpssl') + '\n',
        _('To: ') + pyrite.config.get_option('sendemail.to') + '\n',
        _('CC: ') + pyrite.config.get_option('sendemail.cc') + '\n',
        _('BCC: ') + pyrite.config.get_option('sendemail.bcc') + '\n'
        ]

    extra = [_('The above information will be used for all'
               ' patches to be sent')]
    buf = pyrite.ui.edit(buf, extra, 'pyt-email').splitlines()
    print buf
    if len(buf) != 9:
        raise pyrite.ui.error_out(_('invalid email options'))
    fromaddr = buf[0].split(':')[1].strip()
    server = buf[1].split(':')[1].strip()
    user = buf[2].split(':')[1].strip()
    passwd = buf[3].split(':')[1].strip()
    port = buf[4].split(':')[1].strip()
    ssl = buf[5].split(':')[1].strip().lower()
    to = [ e.strip() for e in buf[6].split(':')[1].split(',') ]
    cc = [ e.strip() for e in buf[7].split(':')[1].split(',') ]
    bcc = [ e.strip() for e in buf[8].split(':')[1].split(',') ]

    if not to:
        pyrite.ui.error_out(_('Must specify a "to" address.'))
    if not fromaddr:
        pyrite.ui.error_out(_('Must specify a "from" address.'))
    if not server:
        pyrite.ui.error_out(_('Must specify a mail server.'))
    if not port:
        pyrite.ui.error_out(_('Must specify a mail server port.'))
    if not passwd:
        pyrite.ui.error_out(_('Must specify a mail server password.'))
    if not user:
        pyrite.ui.error_out(_('Must specify a mail server user.'))

    emai_args = ['git', 'send-email', '--from', fromaddr,
            '--smtp-server', server, '--smtp-server-port', port,
            '--smtp-user', user, '--smtp-pass', passwd]
    if ssl == 'true' or ssl == 'yes':
        emai_args.append('--smtp-ssl')
    for e in bcc:
        emai_args.append('--bcc')
        emai_args.append(e)
    for e in cc:
        emai_args.append('--cc')
        emai_args.append(e)
    for e in to:
        emai_args.append('--to')
        emai_args.append(e)
    emai_args.extend(args)
    import subprocess
    for line in subprocess.Popen(emai_args).stdout.readlines():
        pyrite.ui.info(line)