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

options = [('v', 'verbose', _('print full help and aliases'), 0)]

help_str="""
pyt help <command>

Shows list of commands or help for a command.
"""

class HelpError(Exception):
    """Raised to show help"""

def show_help(prefix, template, threshold, suffix):
    pyrite.ui.info(prefix)
    commands = {}
    for c in pyrite.commands.keys():
        options = pyrite.commands[c]
        if 2 > options[1] >= threshold:
            commands[c[0]] = template % (c[0].ljust(10), options[2])
    for c in sorted(commands.keys()):
        pyrite.ui.info(commands[c])
    pyrite.ui.info(suffix)

def show_full_help():
    show_help(pyrite.help_str + _('\nAll commands...\n'),
                _(' %s %s'),
                0,
                '\n' + _('For more aliases type "%s"') % 'pyt help -v')

def show_command_help(cmd, message):
    cmd_info = None
    for c, info in pyrite.commands.iteritems():
        if cmd in c:
            cmd_info = info
            break
    else:
        raise HelpError

    pyrite.dyn_import(cmd_info[0])
    mod = pyrite.modules[cmd_info[0]]
    pyrite.ui.info(cmd_info[2])
    pyrite.ui.info(mod.help_str)
    if len(mod.options) > 0:
        pyrite.ui.info(_('options:\n'))
        for s, l, m, f in mod.options:
            if len(s) > 0:
                pyrite.ui.info(' -%s --%s %s' % (s.ljust(2), l.ljust(10), m))
            else:
                pyrite.ui.info('     --%s %s' % (l.ljust(10), m))
    pyrite.ui.info('\n' + _('For other commands run "pyt help"'))
    if message:
        pyrite.ui.info('\n')
        pyrite.ui.info(message)
    pyrite.ui.info('\n')

def run(cmd, *args, **flags):
    if flags.has_key('basic'):
        show_help(pyrite.help_str + _('\n\nBasic commands...\n'),
                    _(' %s %s'),
                    1,
                    _('\n' + _('For more options type "pyt help"')))
    elif flags.has_key('unknown'):
        show_help(pyrite.help_str + _('\n\nUnknown command %s\nBasic '
                                      'commands...\n') % cmd,
                    _(' %s %s'),
                    1,
                    _('\n' + _('For more options type "pyt help"')))
    elif flags.has_key('command'):
        cmd = flags['command']
        if cmd == 'help':
            show_full_help()
            return
        show_command_help(flags['command'], flags.get('message', None))
    elif flags.has_key('verbose'):
        pyrite.ui.info(pyrite.help_str + '\n')
        messages = {}
        for c, info in pyrite.commands.iteritems():
            cmd = c[0]
            messages[cmd] = ', '.join(c) + ':\n\t' + info[2] + '\n\n'
        for m in sorted(messages.keys()):
            pyrite.ui.info(messages[m])
    elif len(args) == 1:
        try:
            show_command_help(args[0], None)
        except HelpError:
            show_full_help()    
    else:
        show_full_help()
        
