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

import extensions, pyrite
from pyrite.git.repository import Repo
from pyrite.git.gitobject import GitError
from pyrite.utils.io import IO
from pyrite.utils.settings import Settings
from pyrite.utils.options import OptionParser
from pyrite.utils.help import HelpError, on_help_error
from pyrite.commands import _commands, get_command_info
import sys

global_options = [
('h', 'help', _(''), 0),
('', 'debug-subcommands', _(''), 0),
('', 'debug-suppress-output', _(''), 0),
('', 'debug-profile', _(''), 0),
('', 'debug-profile-extra', _(''), 0),
('', 'debug-profile-sort', _(''), 0),
('', 'debug-exceptions', _(''), 0)
]

def exec_command(module, cmd, args, flags, io, settings, repo):
    extensions.on_before_command(module, cmd, args, flags, io,
                                 settings, repo)
    module.run(cmd, args, flags, io, settings, repo)
    extensions.on_after_command(module, cmd, args, flags, io,
                                settings, repo)

def run():
    show_trace = False
    dummy_out = None
    io = IO()
    try:
        repo = Repo(io=io)
        settings = Settings(repo)
        extensions.on_load(io, _commands, settings)
        io.initialize(settings, repo)

        if len(sys.argv) < 2:
            raise HelpError()
        cmd = sys.argv[1]
        cmd_info = get_command_info(cmd)
        if not cmd_info:
            raise HelpError(cmd)

        m = pyrite.dyn_import(cmd_info[0], io)
        options = OptionParser(cmd, m, global_options)
        options.parse(sys.argv[2:])
        flags = options.get_flags()
        args = options.get_args()
        module = pyrite.modules[cmd_info[0]]

        if 'help' in flags:
            raise HelpError(cmd)
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
            cProfile.runctx('exec_command(module, cmd, args, flags, '
                            'io, settings, repo)',
                            globals(), locals(), 'pyt-profile')
            p = pstats.Stats('pyt-profile')
            p.sort_stats(flags.get('debug-profile-sort', 'cumulative'))
            p.print_title()
            p.print_stats()
            if 'debug-profile-extra' in flags:
                p.print_callers()
        else:
            exec_command(module, cmd, args, flags, io, settings, repo)

    except HelpError, inst:
        on_help_error(inst, io)
        if show_trace:
            raise
    except GitError, inst:
        if show_trace:
            raise
        io.error_out(inst)
    finally:
        if dummy_out:
            dummy_out.close()


