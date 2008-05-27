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

    def __init__(self, cmd=None, message=None, verbose=False):
        self.cmd = cmd
        self.message = message
        self.verbose = verbose

def output_header():
    from pyrite.__version__ import version
    pyrite.ui.info(pyrite.help_str + _(' version ') + version)
    pyrite.ui.info('')

def show_help(prefix, template, threshold, suffix):
    output_header()
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
                '\n' + _('For more aliases type "%s"\n\n') % 'pyt help -v')

def show_command_help(cmd, message):
    cmd_info = pyrite.get_command_info(cmd)
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
    pyrite.ui.info('\n' + _('For other commands run "%s"') % 'pyt help"')
    if message:
        pyrite.ui.info('')
        pyrite.ui.info(message)
    pyrite.ui.info('')

def show_extensions():
    output_header()

    pyrite.ui.info(_('The following extensions have been loaded...\n\n'))
    pyrite.ui.info(_(' name:').ljust(31) + _(' description'))
    pyrite.ui.info('-' * 80 + '\n\n')
    
    for name, module in pyrite.extensions.extensions().items():
        pyrite.ui.info(' ' + (name + ':').ljust(30) + ' ' +
                       module.description)
    pyrite.ui.info('')
    pyrite.ui.info(_('For help on an extension, type "%s"\n\n') %
                   'pyt help <extension-name>')

def show_extension_help(ext, message):
    output_header()
    pyrite.ui.info(pyrite.extensions.extensions()[ext].description)
    pyrite.ui.info(pyrite.extensions.extensions()[ext].help_str)
    if message:
        pyrite.ui.info('\n\n' + message)

def on_help_error(err):
    if not err.cmd:
        if err.verbose:
            output_header()

            messages = {}
            for c, info in pyrite.commands.iteritems():
                cmd = c[0]
                messages[cmd] = ', '.join(c) + ':\n\t' + info[2] + '\n\n'
            for m in sorted(messages.keys()):
                pyrite.ui.info(messages[m])
        else:
            show_help(_('Basic commands...\n'), _(' %s %s'), 1,
                      _('\n' + _('For more options type "%s"\n\n') %
                        'pyt help'))
        return

    info = pyrite.get_command_info(err.cmd)
    if not info:
        if err.cmd == 'addons':
            show_extensions()
        elif err.cmd in pyrite.extensions.extensions():
            show_extension_help(err.cmd, err.message)
        else:
            show_help(_('Unknown command "%s"\n\nBasic commands...\n') %
                      err.cmd, _(' %s %s'), 1, '\n' +
                      _('For more options type "%s"\n\n') % 'pyt help')
    elif err.cmd == 'help':
            show_full_help()
    else:
        show_command_help(err.cmd, err.message)

def run(cmd, args, flags):
    if 'verbose' in flags:
        raise HelpError(verbose=True)
    if args:
        raise HelpError(args[0])
    raise HelpError(cmd)
