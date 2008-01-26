
import getopt, sys
from copy import copy

def parse(commands):
    return {}
    
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

