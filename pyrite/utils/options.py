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

from collections import deque

class OptionParser(object):
    def __init__(self, command, module, global_options):
        self._options = {}
        self._switches = {}
        self._short_switches = {}
        self._args = []
        self._command = command

        for short, longopt, m, flags in module.options:
            self._short_switches[short] = longopt
            self._switches[longopt] = not not flags

        for short, longopt, m, flags in global_options:
            self._short_switches[short] = longopt
            self._switches[longopt] = not not flags

    def get_args(self):
        return self._args

    def get_flags(self):
        return self._options

    def parse(self, arguments):
        arguments = deque(arguments)
        malformed_message = _('Malformed argument "%s".')
        missing_message = _('Missing required value for "%s".')
        unknown_message = _('Unknown arguement "%s".')
        while arguments:
            arg = arguments.popleft()
            l = len(arg)
            if l < 2:
                raise HelpError(self._command, malformed_message % arg)
            if arg == '--':
                self._args.extend(arguments)
                break
            if arg[0] == '-':
                if arg[1] == '-':
                    if l < 4:
                        raise HelpError(self._command,
                                        malformed_message % arg)
                    longopt = arg[2:]
                else:
                    arg = arg[1:]
                    if l != 2:
                        raise HelpError(self._command,
                                        malformed_message % arg)
                    longopt = self._short_switches.get(arg, arg)

                if not longopt in self._switches:
                    raise HelpError(self._command, unknown_message % arg)
                has_opts = self._switches[longopt]
                if has_opts:
                    if not arguments:
                        raise HelpError(self._command,
                                        missing_message % longopt)
                    self._options[longopt] = arguments.popleft()
                else:
                    self._options[longopt] = True
            else:
                self._args.append(arg)
