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


import os, pyrite
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

class IniParser(object):
    def __init__(self, filename):
        self.filename = filename
        self._options = {}

    def read(self):
        f = None
        try:
            f = open(self.filename, 'r')
            current_section = None
            for line in f.readlines():
                line = line.strip()
                if not line or line[0] == '#' or line[0] == ';':
                     continue
                if len(line) < 3:
                     raise ConfigError(_('Bad config line!'))
                if line[0] == '[':
                    if line[-1] != ']':
                        raise ConfigError(_('Bad Config block!'))
                    section_name = line[1:-1]
                    if section_name in self._options:
                        current_section = self._options[section_name]
                    else:
                        current_section = self._options[section_name] = {}
                else:
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        raise ConfigError(_('Bad config line!'))
                    if current_section == None:
                        raise ConfigError(_('Config line outside of block!'))
                    name = parts[0].strip()
                    value = parts[1].strip()
                    if name in current_section:
                        current_section[name].append(value)
                    current_section[name] = [value]
        except (IOError, OSError):
            pass
        finally:
            if f:
                f.close()

    def get(self, section, name, default=None, num=0):
        if section in self._options:
            sec = self._options[section]
            if name in sec:
                return sec[name][num]
        return default

    def items(self, section):
        if section in self._options.keys():
           for name, values in self._options[section].items():
               for v in values:
                   yield name, v

    def write(self, filename):
        f = None
        try:
            f = open(filename, 'w+')
            for section, names in self._options.items():
                 f.write('\n[%s]\n' % section)
                 for name, values in names.items():
                     for v in values:
                         f.write('%s=%s\n' % (name, v))
        finally:
            if f:
                f.close()

    def set(self, section, name, value, num=0):
        if section in self._options:
            sec = self._options[section]
        else:
            sec = self._options[section] = {}
        if name in sec:
            sec[name][num] = value
        else:
            sec[name] = [value]

    def remove_option(self, section, name, num=0):
        if section in self._options:
           sec = self._options[section]
           if name in sec:
               del sec[name][num]
               if not sec[name]:
                  del sec[name]
           if not sec:
              del self._options[section]

    def sections(self):
        for section in self._options.keys():
            yield section


class Config(object):
    _not_under_repo_error = _("Not under a repository")
    _missing_config_arg = _("Category and Name must be supplied")
    def __init__(self):
        self.user = None
        self.user_config_path = os.path.expanduser('~/.gitconfig')
        self.user_config = IniParser(self.user_config_path)
        self.user_config.read()

        if pyrite.repo.is_repo():
            self.repo_config_path = os.path.join(pyrite.repo.get_repo_dir(),
                                                 'config')
            self.repo_config = IniParser(self.repo_config_path)
            self.repo_config.read()

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
        value = None
        if pyrite.repo.is_repo():
            value = self.repo_config.get(category, name)
        if not value:
            value = self.user_config.get(category, name)
        return value

    def _items(self, category, config):
        parts = category.split('.')
        if len(parts) == 1:
            category = parts[0]
        elif parts:
            category = parts[0] + ' "' + parts[1] + '"'
        for k, v in config.items(category):
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

    def _del_option(self, config, path, item, is_all):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise ValueError(_missing_config_arg)
        config.remove_option(category, name)
        config.write(path)

    def _set_option(self, config, path, item, value, is_all):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise ValueError(_missing_config_arg)
        config.set(category, name, value)
        config.write(path)

    def get_user(self):
        if self.user:
            return self.user
        user = self.get_option('user.name')
        if not user:
            user = os.getlogin()
        email = self.get_option('user.email')
        if not email:
            email = '<%s@%s>' % (os.getlogin(), os.uname()[1])
        else:
            if email[0] != '<':
                email = '<' + email + '>'
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
                pyrite.config.del_user_option(args[0], is_all)
            else:
                pyrite.config.del_repo_option(args[0], is_all)
        elif flags.has_key('set'):
            if is_user:
                pyrite.config.set_user_option(args[0], ' '.join(args[1:]),
                                                is_all)
            else:
                pyrite.config.set_repo_option(args[0], ' '.join(args[1:]),
                                                is_all)
        else:
            if not args:
                pyrite.utils.io.info(_('Global config values...\n\n'))
                for k,v in pyrite.config.all_user():
                    pyrite.utils.io.info(_(' %s %s') % (k.ljust(30), v))
                pyrite.utils.io.info(_('\nThis repository\'s config values...\n\n'))
                for k,v in pyrite.config.all_repo():
                    pyrite.utils.io.info(_(' %s %s') % (k.ljust(30), v))
            else:
                for option in args:
                    value = pyrite.config.get_option(option, is_all)
                    if not value:
                        value = ''
                    pyrite.utils.io.info(_('%s = %s') % (option, value))
    except ConfigError, inst:
        pyrite.utils.io.error_out(inst)


