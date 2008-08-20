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

class HelpError(Exception):
    """Raised to show help"""

    def __init__(self, cmd=None, message=None, verbose=False):
        self.cmd = cmd
        self.message = message
        self.verbose = verbose

def output_header(io):
    from pyrite.__version__ import version
    io.info(pyrite.help_str + _(' version ') + version)
    io.info('')

def show_help(prefix, template, threshold, suffix, io):
    output_header(io)

    io.info(prefix)
    commands = {}
    for c, options in pyrite.commands._commands.iteritems():
        if 2 > options[1] >= threshold:
            commands[c[0]] = template % (c[0].ljust(10), options[2])
    for c in sorted(commands.itervalues()):
        io.info(c)
    io.info(suffix)

def show_full_help(io):
    show_help(_('All commands...\n'), _(' %s %s'), 0,
                '\n' + _('For more aliases type "%s"\n\n') %
                'pyt help -v', io)

def show_command_help(cmd, message, io):
    cmd_info = pyrite.commands.get_command_info(cmd)
    if not cmd_info:
        raise HelpError(cmd)

    pyrite.dyn_import(cmd_info[0], io)
    mod = pyrite.modules[cmd_info[0]]

    io.info(cmd_info[2])
    io.info(mod.help_str)
    if len(mod.options) > 0:
        io.info(_('\noptions:'))
        for s, l, m, f in mod.options:
            if len(s) > 0:
                io.info(' -%s, --%s %s' % (s, l.ljust(15), m))
            elif len(l) > 0:
                io.info('      --%s %s' % (l.ljust(15), m))
            else:
                io.info('\n*' + m)
    io.info('\n' + _('For other commands run "%s"') % 'pyt help"')
    if message:
        io.info('')
        io.info(message)
    io.info('')

def show_extensions(io):
    output_header()

    io.info(_('The following extensions have been loaded...\n\n'))
    io.info(_(' name:').ljust(31) + _(' description'))
    io.info('-' * 80 + '\n\n')
    
    for name, module in pyrite.extensions.extensions().iteritems():
        io.info(' ' + (name + ':').ljust(30) + ' ' + module.description)
    io.info('')
    io.info(_('For help on an extension, type "%s"\n\n') %
                   'pyt help <extension-name>')

def show_extension_help(ext, message, io):
    output_header()
    io.info(pyrite.extensions.extensions()[ext].description)
    io.info(pyrite.extensions.extensions()[ext].help_str)
    if message:
        io.info('\n\n' + message)

def on_help_error(err, io):
    if not err.cmd:
        if err.verbose:
            output_header(io)

            messages = {}
            for c, info in pyrite.commands.iteritems():
                cmd = c[0]
                messages[cmd] = ', '.join(c) + ':\n\t' + info[2] + '\n\n'
            for m in sorted(messages.itervalues()):
                io.info(m)
        else:
            show_help(_('Basic commands...\n'), _(' %s %s'), 1,
                      _('\n' + _('For more options type "%s"\n\n') %
                        'pyt help'), io)
        return

    info = pyrite.commands.get_command_info(err.cmd)
    if not info:
        if err.cmd == 'addons':
            show_extensions(io)
        elif err.cmd in pyrite.extensions.extensions():
            show_extension_help(err.cmd, err.message, io)
        else:
            show_help(_('Unknown command "%s"\n\nBasic commands...\n') %
                      err.cmd, _(' %s %s'), 1, '\n' +
                      _('For more options type "%s"\n\n') % 'pyt help', io)
    elif err.cmd == 'help':
            show_full_help(io)
    else:
        show_command_help(err.cmd, err.message, io)

