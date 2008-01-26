
from copy import copy
from pyrite.standard.help import HelpError

class OptionParser:
    def __init__(self, command):
        self._options = {}
        self._args = []
        self._switches = {}
        self._command = command
        
    def get_args(self): return self._args
    
    def get_switches(self): return self._options
        
    def add_option(self, short, longopt):
        self._switches[short] = longopt
        
    def parse(self, arguments):
        stop = False
        last = None
        for a in arguments:
            l = len(a)
            if stop: self._args.append(a) 
            elif a == '--': stop = True
            elif l > 3 and a.startswith('--'):
                longopt = a[2:]
                if longopt in self._switches.values():
                    self._options[longopt] = ""
                    last = longopt
                else:
                    raise HelpError, {'command': self._command}
            elif l == 2 and a[0] == '-':
                if self._switches.has_key(a[1]):
                    longopt = self._switches[a[1]]
                    self._options[longopt] = ""
                    last = longopt
                else:
                    raise HelpError, {'command': self._command}
            elif last != None:
                self._options[last] = a
                last = None
            else:
                self._args.append(a)
                stop = True

def parse(options, arguments, command):
    parser = OptionParser(command)
    for s,l,m in options:
        parser.add_option(s, l)
    parser.parse(arguments)
    return parser.get_switches(), parser.get_args()
    
def expand_aliases(commands, aliases_map):
    items = commands.copy()
    for c, options in items.iteritems():
        aliases = c.split('|')
        if len(aliases) > 1:
            aliases_map[c] = []
            for a in aliases:
                o = copy(options)
                o[1] = 2
                commands[a] = o
            commands[aliases[0]][1] = options[1]
            aliases_map[c].append(a)
            del commands[c]

