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
import os
from pyrite.standard.help import HelpError

help_str = """
pyt tag -d | --delete <tagname>
pyt tag -l | --list [pattern]
pyt tag -v | --verify <tagname>
pyt tag [-s | -a | -k <key-id>] [-m <message>] <tagname>

The tag command is used to create, list or delete tags.  The --verify
option will verify the gpg signature.  The --sign, -annotate and --key options
create tags.  You will need to specify a message for the tag, you can use
--message or the editor will be launched to allow you to edit the message.
"""

def _get_message(message, name):

    if message: return message
    
    extra = [_('This is a tag message.'),
            _('Lines beginning with "#" will be removed'),
            _('To abort tagging, do not save this file')]

    message = pyrite.ui.edit('', extra, 'pyt-edit-' + name)
    if not message:
        raise HelpError({'command': cmd, 'message': 
                        _('No commit message')})
    return message

def run(cmd, *args, **flags):
    
    if flags.has_key('list'):
        lines = None
        if len(args) > 0:
            lines = pyrite.repo.list_tags(args[0])
        else:
            lines = pyrite.repo.list_tags(None)
        pyrite.ui.info(lines)
        return
    
    if len(args) < 1:
            raise HelpError({'command': cmd, 'message':
                            _('No tag name specified')})
  
    if flags.has_key('verify'):
        pyrite.ui.info(pyrite.repo.verify_tag(args[0]))
    elif flags.has_key('delete'):
        pyrite.ui.info(pyrite.repo.delete_tags(args))
    else:
        
        message = flags.get('message', None)
        key = flags.get('key', None)

        if key:
            message = _get_message(message, args[0])
            pyrite.ui.info(pyrite.repo.create_tag(args[0], message, key=key))
        elif flags.has_key('sign'):
            message = _get_message(message, args[0])
            pyrite.ui.info(pyrite.repo.create_tag(args[0], message, sign=True))
        elif flags.has_key('annotated'):
            message = _get_message(message, args[0])
            pyrite.ui.info(pyrite.repo.create_tag(args[0], message))
        else:
            pyrite.ui.info(pyrite.repo.create_tag(args[0], None))

