#Copyright 2008 Govind Salinas <blix@sophiasuchtig.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


#import gettext
#gettext.install('pyt')
def noop(message):return message #Don't know if I really want to localize the
                              #cmd line. For now continue to add localzable
                              #strings with the _() but make it a noop
import __builtin__
__builtin__.__dict__['_'] = noop

import extensions, options, UI, repository
import pyrite.standard.config as pytconfig
import pyrite.standard.help as pythelp
import sys, imp

config = None

repo = None

ui = UI.UI()

# commands with the second element as 0 are shown only in extended help
# commands with the second element as 1 are shown in normal help

commands = {
('alter','rebase'): ('alter', 0,
            _('Alter the history to change order, contents partens etc')),
('bisect',): ('bisect', 0,
            _('Find the change that introduced a bug by binary search.')),
('blame', 'annotate'): ('blame', 0,
            _('Show what revision and author edited a file line-by-line')),
('branch',): ('branch', 1,
            _('list, switch to, create or delete branches')),
('checkout', 'co'): ('checkout', 1,
            _('Checkout a specific revision of the history')),
('checkin', 'commit', 'ci'): ('checkin', 1,
            _('Record changes to the repository')),
('cherry',): ('cherry', 0,
            _('Apply the change introduced by an existing commit')),
('clone',): ('clone', 1,
            _('Clone a repository into a new directory')),
('config',): ('config', 1,
            _('Set or get configuration variables')),
('diff',): ('diff', 1,
            _('diff between to commits or a commit and the working set')),
('email',): ('email', 0,
            _('Send a collection of patches as emails')),
('export',): ('export', 0,
            _('Export patches suitable to be emailed or imported')),
('fetch',): ('fetch', 0,
            _('Get objects and refs from another repository')),
('grep',): ('grep', 0,
            _('Print lines matching a pattern')),
('gui', 'view'): ('gui', 1,
            _('launch the graphical interface or history browser')),
('help',): ('help', 1,
            _('view the general help or help for a command')),
('import', 'apply'): ('import', 0,
            _('Import a patch that has been exported by pyt')),
('init',): ('init', 1,
            _('Create an empty repository')),
('log', 'hist', 'history'): ('log', 1,
            _('Show commit logs')),
('move', 'mv', 'rename'): ('move', 0,
            _('Move or rename a file and tell pyt about it')),
('pull',): ('pull', 1,
            _('Fetch and merge in one operation')),
('push',): ('push', 1,
            _('Update remote refs and their associated objects')),
('recover',): ('recover', 0,
            _('Recover the previous state of a branch.')),
('remove', 'rm'): ('remove', 0,
            _('Remove files from the working set and tell pyt about it')),
('resolve', 'res'): ('resolve', 1,
            _('Resolve a merge conflict')),
('revert',): ('revert', 0,
            _('Revert a change in the history by applying a new commit')),
('show',): ('show', 0,
            _('show files, tags and commits')),
('status',): ('status', 1,
            _('Show status of the working set')),
('tag',): ('tag', 0,
            _('create, list or delete tags')),
('track', 'add', 'update'): ('track', 1,
                 _('look for added or removed files from the repository')),
('verify', 'fsck'): ('verify', 0,
            _('verify integrity of the repository'))
}

help_str = _("Pyrite Distributed SCM")

modules = {}

global_options = [
('h', 'help', _(''), 0),
('', 'debug-subcommands', _(''), 0),
('', 'debug-suppress-output', _(''), 0),
('', 'debug-profile', _(''), 0),
('', 'debug-profile-extra', _(''), 0),
('', 'debug-profile-sort', _(''), 0),
('', 'debug-exceptions', _(''), 0)
]

def get_command_info(cmd):
    for c, info in commands.iteritems():
        if cmd in c:
            return info

def dyn_import(module, is_extension=False, path=None):
    if module in modules:
        return
    package = None
    if is_extension:
        if path:
            raise Exception('custom extension paths not yet supported')
        else:
            package = 'pyrite.addons'
    else:
        package = 'pyrite.standard'
    try:
        m = __import__(package, fromlist=module)
        f, p, d = imp.find_module(module, m.__path__)
        modules[module] = m = imp.load_module(package + '.' + module,
                                              f, p, d)
        return m
    except ImportError, inst:
        ui.warn(_('Failed to load extension %s: %s') %
                       (module, inst.message))
        return None

def exec_command(module, cmd, args, flags):
    extensions.on_before_command(module, cmd, args, flags)
    module.run(cmd, args, flags)
    extensions.on_after_command(module, cmd, args, flags)

def run():
    show_trace = False
    dummy_out = None
    try:
        global repo
        repo = repository.Repo()
        global config
        config = pytconfig.Config()
        extensions.on_load(commands)

        if len(sys.argv) < 2:
            raise pythelp.HelpError()
        cmd = sys.argv[1]
        cmd_info = get_command_info(cmd)
        if not cmd_info:
            raise pythelp.HelpError(cmd)

        m = dyn_import(cmd_info[0])
        flags,args = options.parse(m.options, sys.argv[2:], cmd)
        module = modules[cmd_info[0]]

        if 'help' in flags:
            raise pythelp.HelpError(cmd)
        if 'debug-subcommands' in flags:
            repo._debug_commands = True
        if 'debug-exceptions' in flags:
            show_trace = True
        if 'debug-suppress-output' in flags:
            dummy_out = open('/dev/null', 'w')
            ui.stdout = dummy_out
        if 'debug-profile' in flags:
            import cProfile
            import pstats
            cProfile.runctx('exec_command(module, cmd, args, flags)',
                            globals(), locals(), 'pyt-profile')
            p = pstats.Stats('pyt-profile')
            p.sort_stats(flags.get('debug-profile-sort', 'cumulative'))
            p.print_title()
            p.print_stats()
            if 'debug-profile-extra' in flags:
                p.print_callers()
        else:
            exec_command(module, cmd, args, flags)

    except pythelp.HelpError, inst:
        pythelp.on_help_error(inst)
        if show_trace:
            raise
    except repository.RepoError, inst:
        if show_trace:
            raise
        ui.error_out(inst)
    finally:
        if dummy_out:
            dummy_out.close()
