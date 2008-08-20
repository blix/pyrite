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

import os
from pyrite.utils.ini import IniParser, IniParseError

class SettingsError(Exception):
    """Raised when unable to load config"""

class Settings(object):
    _not_under_repo_error = _("Not under a repository")
    _missing_config_arg = _("Category and Name must be supplied")
    def __init__(self, repo):
        self.repo = repo
        self.user = None
        self.user_config_path = os.path.expanduser('~/.gitconfig')
        self.user_config = IniParser(self.user_config_path)
        try:
            self.user_config.read()

            if repo.is_in_repo():
                self.repo_config_path = os.path.join(repo.get_git_dir(),
                                                     'config')
                self.repo_config = IniParser(self.repo_config_path)
                self.repo_config.read()
        except IniParseError, inst:
            raise SettingsError(inst)
        repo.set_settings(self)

    def set_repo_option(self, item, value, is_all):
        if not self.repo.is_in_repo():
            raise SettingsError(self._not_under_repo_error)
        self._set_option(self.repo_config, self.repo_config_path, item, value,
                            is_all)

    def set_user_option(self, item, value, is_all):
        self._set_option(self.user_config, self.user_config_path, item, value,
                            is_all)

    def del_repo_option(self, item, is_all):
        if not self.repo.is_in_repo():
            raise SettingsError(self._not_under_repo_error)
        self._del_option(self.repo_config, self.repo_config_path, item, is_all)

    def del_user_option(self, item, is_all):
        self._del_option(self.user_config, self.user_config_path, item, is_all)

    def get_option(self, item, default=None, is_all=False):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise SettingsError(_missing_config_arg)
        value = None
        if self.repo.is_in_repo():
            value = self.repo_config.get(category, name)
        if value == None:
            value = self.user_config.get(category, name)
            if value == None:
                value = default
        return value

    def get_repo_option(self, item, default=None, is_all=False):
        category, name = self._split_option(item)
        if category == None or name == None:
            raise SettingsError(_missing_config_arg)
        if self.repo.is_in_repo():
            return self.repo_config.get(category, name)
        if default:
            return default
        raise SettingsError(_not_under_repo_error)

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

        if self.repo.is_in_repo():
            for k, v in self._items(category, self.repo_config):
                items[k] = v

        for k, v in items.items():
            yield k, v

    def update_ignore(self, item, remove):
        if not self.repo.is_in_repo():
            raise SettingsError(self._not_under_repo_error)
        lines = []
        try:
            f = open(repo.get_ignore_file(), 'r+')
            lines = f.readlines()
        finally: f.close()
        item = item + '\n'
        if item in lines and remove:
            lines.remove(item)
        elif not remove:
            lines.append(item)
        try:
            f = open(repo.get_ignore_file(), 'w+')
            f.writelines(lines)
        finally: f.close()

    def _split_option(self, option):
        parts = option.split('.')
        l = len(parts)
        if 2 > l or l > 3:
            raise SettingsError(_('Malformed option string: %s') %
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

