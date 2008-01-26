
import pyrite
from gettext import gettext as _

help_str='Show help'

class HelpError(Exception):
    """Raised to show help"""
    
def show_help(prefix, template, threshold, suffix):
    pyrite.ui.info(prefix)
    for c in sorted(pyrite.commands.keys()):
        options = pyrite.commands[c]
        if 2 > options[1] >= threshold:
            pyrite.ui.info(template % (c, options[3]))
    pyrite.ui.info(suffix)
    
def show_full_help():
    show_help(pyrite.help_str + _('\nAll commands...\n\n'),
                _('%s\t%s'),
                0,
                '\n' + _('For more aliases type "%s"') % 'pyt help -v')
                
def show_command_help(cmd):
    if not pyrite.commands.has_key(cmd): raise HelpError
    o = pyrite.commands[cmd]
    pyrite.dyn_import(o[0])
    
    mod = pyrite.modules[o[0]]
    pyrite.ui.info(o[4] + '\n')
    pyrite.ui.info(o[3] + '\n')
    pyrite.ui.info(mod.help_str + '\n')
    if len(o[2]) > 0:
        pyrite.ui.info(_('options:\n'))
        for s, l, m in o[2]:
            if len(s) > 0:
                pyrite.ui.info('-%s\t--%s\t%s' % (s, l, m))
            else:
                pyrite.ui.info('  \t--%s\t%s' % (l, m))
    pyrite.ui.info('\n' + _('For more options type "pyt help"'))

def run(*args, **flags):
    if flags.has_key('basic'):
        show_help(pyrite.help_str + _('\n\nBasic commands...\n\n'),
                    _('%s\t%s'),
                    1,
                    _('\n\n' + _('For more options type "pyt help"')))
    elif flags.has_key('command'):
        cmd = flags['command']
        if cmd == 'help':
            show_full_help()
            return
        show_command_help(flags['command'])
    elif flags.has_key('verbose'):
        print 'v'
        for c in sorted(pyrite.commands.keys()):
            cmd = c
            options = pyrite.commands[c]
            if c in pyrite.aliases_map:
                for a in aliases_map[c]:
                    cmd = cmd + ', ' + a
            pyrite.ui.info(cmd)
            pyrite.ui.info('\t%s' % options[3])
    elif len(args) == 1:
        try:
            show_command_help(args[0])
        except HelpError:
            show_full_help()    
    else:
        show_full_help()
        
