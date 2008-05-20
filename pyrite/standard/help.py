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
from pyrite import options as pytoptions

options = [('v', 'verbose', _('print full help and aliases'), 0)]

help_str="""
pyt help <command>

Shows list of commands or help for a command.
"""

class HelpError(Exception):
    """Raised to show help"""

    def __init__(self, cmd=None, message=None, verbose=False):
        self.cmd = cmd
        self.message = message
        self.verbose = verbose

def show_help(prefix, template, threshold, suffix):
    from pyrite.__version__ import version
    pyrite.ui.info(pyrite.help_str + _(' version ') + version)
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
    show_help(_('All commands...\n'), _(' %s %s'), 0,
                '\n' + _('For more aliases type "%s"') % 'pyt help -v')

def show_command_help(cmd, message):
    cmd_info = pytoptions.get_command_info(cmd)
    if not cmd_info:
        raise HelpError(cmd)

    pyrite.dyn_import(cmd_info[0])
    mod = pyrite.modules[cmd_info[0]]
    pyrite.ui.info(cmd_info[2])
    pyrite.ui.info(mod.help_str)
    if len(mod.options) > 0:
        pyrite.ui.info(_('\noptions:'))
        for s, l, m, f in mod.options:
            if len(s) > 0:
                pyrite.ui.info(' -%s, --%s %s' % (s, l.ljust(15), m))
            elif len(l) > 0:
                pyrite.ui.info('      --%s %s' % (l.ljust(15), m))
            else:
                pyrite.ui.info('\n*' + m)
    pyrite.ui.info('\n' + _('For other commands run "pyt help"'))
    if message:
        pyrite.ui.info('\n')
        pyrite.ui.info(message)
    pyrite.ui.info('\n')

def on_help_error(err):
    if not err.cmd:
        if err.verbose:
            from pyrite.__version__ import version
            pyrite.ui.info(pyrite.help_str + _(' version ') + version
                           + '\n')
            messages = {}
            for c, info in pyrite.commands.iteritems():
                cmd = c[0]
                messages[cmd] = ', '.join(c) + ':\n\t' + info[2] + '\n\n'
            for m in sorted(messages.keys()):
                pyrite.ui.info(messages[m])
        else:
            show_help(_('\nBasic commands...\n'), _(' %s %s'), 1,
                      _('\n' + _('For more options type "pyt help"')))
        return

    info = pytoptions.get_command_info(err.cmd)
    if not info:
        show_help(_('\nUnknown command %s\nBasic commands...\n') % err.cmd,
                    _(' %s %s'), 1, '\n' +
                    _('For more options type "pyt help"'))
    elif err.cmd == 'help':
            show_full_help()
    else:
        show_command_help(err.cmd, err.message)

def run(cmd, *args, **flags):
    if 'verbose' in flags:
        raise HelpError(verbose=True)
    if args:
        raise HelpError(args[0])
    raise HelpError(cmd)
