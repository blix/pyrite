
import pyrite
from gettext import gettext as _

class HelpError(Exception):
    """Raised to show help"""

def run(**args):
    if args.has_key('basic'):
        pyrite.ui.info(pyrite.help_str + '\n\nBasic commands...\n\n')
        for c in sorted(pyrite.commands.keys()):
            options = pyrite.commands[c]
            if options[1] == 1:
                pyrite.ui.info('%s\t%s' % (c, options[3]))
        pyrite.ui.info('\n\n' + _('For more options type "pyt help"'))
    elif args.has_key('command'):
        o = pyrite.commands[args['command']]
        mod = pyrite.ext[o[0]]
        pyrite.ui.info(pyrite.help_str + '\n\n')
        pyrite.ui.info(mod.help_str + '\n\n')
        for s, l, m in options[2]:
            if len(s) > 0:
                pyrite.ui.info('-%s\t--%s\t%s' % (s, l, m))
            else:
                pyrite.ui.info('  \t--%s\t%s' % (l, m))
        pyrite.ui.info('\n\n' + _('For more options type "pyt help"'))
    elif args.has_key('verbose'):
        pyrite.ui.info(pyrite.help_str + '\n\nAll commands and aliases...\n\n')
        for c in sorted(pyrite.commands.keys()):
            cmd = c
            options = pyrite.commands[c]
            if c in pyrite.aliases_map:
                for a in aliases_map[c]:
                    cmd = cmd + ', ' + a
            pyrite.ui.info(cmd)
            pyrite.ui.info('\t%s' % options[3])
    else:
        pyrite.ui.info(pyrite.help_str + '\n\nAll commands...\n\n')
        for c in sorted(pyrite.commands.keys()):
            options = pyrite.commands[c]
            if options[1] < 2:
                pyrite.ui.info('%s\t%s' % (c, options[3]))
        pyrite.ui.info('\n' + _('For more aliases type "') + 'pyt help -v' +
                        _('"'))
