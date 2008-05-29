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
from pyrite.utils.settings import Settings
from pyrite.utils.help import HelpError

options = [
('r', 'repo-only', _('option only applies to current repo'), 0),
('d', 'delete', _('delete option'), 0),
('a', 'all', _('show all configured options'), 0),
('s', 'set', _('set a option'), 0),
('i', 'ignore', _('ignore a pattern of files'), 0),
('u', 'unignore', _('stop ignoring a pattern of files'), 0),
('', 'add', _('add variable with the name even if it exists'), 0)
]

help_str = _("""
pyt config -i | --ignore <glob>
pyt config -u | --unignore <glob>
pyt config [-r | --repo-only] [-a | --all] <option> <value>
pyt config [-r | --repo-only] [-a | --all] -s | --set <option> <value>
pyt config [-r | --repo-only] [-a | --all] -d | --delete  <option>
pyt config [-r | --repo-only] --add <option> <value>
 
You can query/set/replace/unset options with this command. The name is
actually the section and the key separated by a dot, and the value will
be escaped.

Multiple lines can be added to an option by using the --add option. If
you want to update or unset an option which can occur on multiple
lines, a POSIX regexp value_regex needs to be given. Only the existing
values that match the regexp are updated or unset.

Options come in the form of section.<subsection>.option.

if there is no subsection it comes out as

[section]
option=value

otherwise it will be

[section "subsection"]
option=value

""")

def run(cmd, args, flags):
    is_user = True
    is_all = False
    if flags.has_key('repo-only'):
        is_user = False

    if 'all' in flags and 'set' in flags:
        raise Exception("Sorry, multiple config lines with the same name not"
                            "implemented yet.")
        is_all = True

    try:
        if flags.has_key('ignore'):
            item = options['ignore']
            config.update_ignore(item, remove=False)
        elif flags.has_key('unignore'):
            item = options['ignore']
            update_ignore(item, remove=True)
        elif flags.has_key('add'):
            raise Exception("Sorry, multiple config lines with the same name not"
                                "implemented yet.")
            if is_user:
                pyrite.settings.add_user_option(args[0], ' '.join(args[1:]))
            else:
                pyrite.settings.add_repo_option(args[0], ' '.join(args[1:]))
        elif flags.has_key('delete'):
            if is_user:
                pyrite.settings.del_user_option(args[0], is_all)
            else:
                pyrite.settings.del_repo_option(args[0], is_all)
        elif flags.has_key('set'):
            if is_user:
                pyrite.settings.set_user_option(args[0], ' '.join(args[1:]),
                                                is_all)
            else:
                pyrite.settings.set_repo_option(args[0], ' '.join(args[1:]),
                                                is_all)
        else:
            if not args:
                pyrite.utils.io.info(_('Global config values...\n\n'))
                for k,v in pyrite.settings.all_user():
                    pyrite.utils.io.info(_(' %s %s') % (k.ljust(30), v))
                pyrite.utils.io.info(_('\nThis repository\'s config values...\n\n'))
                for k,v in pyrite.settings.all_repo():
                    pyrite.utils.io.info(_(' %s %s') % (k.ljust(30), v))
            else:
                for option in args:
                    value = pyrite.settings.get_option(option, is_all)
                    if not value:
                        value = ''
                    pyrite.utils.io.info(_('%s = %s') % (option, value))
    except ConfigError, inst:
        pyrite.utils.io.error_out(inst)


