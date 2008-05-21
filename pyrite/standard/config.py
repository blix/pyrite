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


import ConfigParser, os
import pyrite
from pyrite.standard.help import HelpError

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

class ConfigError(Exception):
    """Raised when unable to load config"""

class Config(object):
    _not_under_repo_error = _("Not under a repository")
    _missing_config_arg = _("Category and Name must be supplied")
    def __init__(self):
        self.user = None
        self.user_config_path = os.path.expanduser('~/.pytrc')
        self.user_config = ConfigParser.SafeConfigParser()
        f = None
        try:
            f = open(self.user_config_path, 'rw')
            self.user_config.readfp(f)
        except (IOError, OSError):
            pass
        finally:
            f.close()
        if pyrite.repo.is_repo():
            self.repo_config_path = os.path.join(pyrite.repo.get_repo_dir(),
                                                    'pytrc')
            self.repo_config = ConfigParser.SafeConfigParser()
        try:
            f = open(self.repo_config_path, 'rw')
            self.repo_config.readfp(f)
        except (IOError, OSError), inst:
            pass
        finally:
            f.close()

    def set_repo_option(self, item, value, is_all):
        if not pyrite.repo.is_repo():
            raise ConfigError(self._not_under_repo_error)
        self._set_option(self.repo_config, self.repo_config_path, item, value,
                            is_all)

    def set_user_option(self, item, value, is_all):
        self._set_option(self.user_config, self.user_config_path, item, value,
                            is_all)

    def del_repo_option(self, item, is_all):
        if not pyrite.repo.is_repo():
            raise ConfigError(self._not_under_repo_error)
        self._del_option(self.repo_config, self.repo_config_path, item, is_all)

    def del_user_option(self, item, is_all):
        self._del_option(self.user_config, self.user_config_path, item, is_all)

    def get_option(self, item, is_all=False):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise ConfigError(_missing_config_arg)
        if pyrite.repo.is_repo() and self.repo_config.has_option(category, name):
            return self.repo_config.get(category, name)
        elif self.user_config.has_option(category, name):
            return self.user_config.get(category, name)
        else:
            return ''

    def _items(self, category, config):
        parts = category.split('.')
        if len(parts) == 1:
            category = parts[0]
        elif parts:
            category = parts[0] + ' "' + parts[1] + '"'
        if self.user_config.has_section(category):
            for k, v in self.user_config.items(category):
                yield k, v

    def items(self, category):
        items = {}
        for k, v in self._items(category, self.user_config):
            items[k] = v

        for k, v in self._items(category, self.repo_config):
            items[k] = v

        for k, v in items.items():
            yield k, v

    def update_ignore(self, item, remove):
        if not pyrite.repo.is_repo():
            raise ConfigError(self._not_under_repo_error)
        lines = []
        try:
            f = open(pyrite.repo.get_ignore_file(), 'r+')
            lines = f.readlines()
        finally: f.close()
        item = item + '\n'
        if item in lines and remove:
            lines.remove(item)
        elif not remove:
            lines.append(item)
        try:
            f = open(pyrite.repo.get_ignore_file(), 'w+')
            f.writelines(lines)
        finally: f.close()

    def _split_option(self, option):
        parts = option.split('.')
        l = len(parts)
        if 2 > l or l > 3:
            raise HelpError('config', _('Malformed option string: %s') %
                            option)
        if l == 2:
            return parts[0], parts[1]
        else:
            return parts[0] + ' "' + parts[1] + '"', parts[2]

    def _del_option(self, config, file_obj, item, is_all):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise ValueError(_missing_config_arg)
        if config.has_section(category):
            config.remove_option(category, name)
            if config.options(category).empty():
                config.remove_section(category)
            config.write(file_obj)

    def _set_option(self, config, path, item, value, is_all):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise ValueError(_missing_config_arg)
        if not config.has_section(category):
            config.add_section(category)
        config.set(category, name, value)
        try:
            f = open(path, 'w+')
            config.write(f)
        except:
            raise ParseError(_('Could not write to config file'))

    def get_user(self):
        if self.user:
            return self.user
        user = self.get_option('user.name')
        if not user:
            user = os.getlogin()
        email = self.get_option('user.email')
        if not email:
            email = os.getlogin() + '@' + os.uname()[1]
        self.user = user + ' ' + email
        return self.user

    def _all_config(self, config):
        for section in config.sections():
            section = '.'.join([part.strip("\"")
                                for part in section.split()])
            for name, value in self._items(section, config):
                yield section + '.' + name, value

    def all_user(self):
        return self._all_config(self.user_config)

    def all_repo(self):
        return self._all_config(self.repo_config)

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
                pyrite.config.add_user_option(args[0], ' '.join(args[1:]))
            else:
                pyrite.config.add_repo_option(args[0], ' '.join(args[1:]))
        elif flags.has_key('delete'):
            if is_user:
                pyrite.config.del_user_option(args[0], ' '.join(args[1:]),
                                                is_all)
            else:
                pyrite.config.del_repo_option(args[0], ' '.join(args[1:]),
                                                is_all)
        elif flags.has_key('set'):
            if is_user:
                pyrite.config.set_user_option(args[0], ' '.join(args[1:]),
                                                is_all)
            else:
                pyrite.config.set_repo_option(args[0], ' '.join(args[1:]),
                                                is_all)
        else:
            if not args:
                pyrite.ui.info(_('Global config values...\n\n'))
                for k,v in pyrite.config.all_user():
                    pyrite.ui.info(_(' %s %s') % (k.ljust(30), v))
                pyrite.ui.info(_('\nThis repository\'s config values...\n\n'))
                for k,v in pyrite.config.all_repo():
                    pyrite.ui.info(_(' %s %s') % (k.ljust(30), v))
            else:
                for option in args:
                    value = pyrite.config.get_option(option, is_all)
                    if not value:
                        value = ''
                    pyrite.ui.info(_('%s = %s') % (option, value))
    except ConfigError, inst:
        pyrite.ui.error_out(inst)


