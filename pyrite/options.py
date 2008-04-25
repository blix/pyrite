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

class ParseError(Exception):
    """Could Not Parse Argument"""

def get_command_info(cmd):
    for c, info in pyrite.commands.iteritems():
        if cmd in c:
            return info

class OptionParser(object):
    def __init__(self, command):
        self._options = {}
        self._args = []
        self._switches = {}
        self._command = command
        
    def get_args(self): return self._args
    
    def get_switches(self): return self._options
        
    def add_option(self, short, longopt, flags):
        required = False
        has_opt = False
        if flags == 1 or flags == 3: has_opt = True
        if flags == 2 or flags == 3: required = True
        self._switches[longopt] = (short, required, has_opt)
        
    def parse(self, arguments):
        stop = False
        last = None
        for a in arguments:
            l = len(a)
            if stop: self._args.append(a) 
            elif a == '--': stop = True
            elif a.startswith('--'):
                if l < 4: raise ParseError(_('Malformed argument %s') % a)
                longopt = a[2:]
                if longopt in self._switches:
                    short, required, has_opts = self._switches[longopt]
                    self._options[longopt] = True
                    if has_opts: last = longopt
                else:
                    raise pyrite.standard.help.HelpError(self._command)
            elif a[0] == '-':
                if len(a) < 2: raise ParseError(_('Malformed argument %s') % a)
                a = a[1]
                if l != 2: raise ParseError(_('Malformed argument %s') % a)
                for longopt, values in self._switches.iteritems():
                    short, required, has_opts = values
                    if short == a:
                        self._options[longopt] = True
                        if has_opts: last = longopt
                        break
                else:
                    raise pyrite.standard.help.HelpError(self._command)
            elif last != None:
                self._options[last] = a
                last = None
            else:
                self._args.append(a)
                stop = True

def parse(options, arguments, command):
    parser = OptionParser(command)
    for s,l,m, f in options:
        parser.add_option(s, l, f)
    parser.parse(arguments)
    return parser.get_switches(), parser.get_args()

