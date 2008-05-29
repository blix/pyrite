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

class IniParseError(Exception):
    """Cannot parse ini file."""

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
                     raise IniParseError(_('Bad config line!'))
                if line[0] == '[':
                    if line[-1] != ']':
                        raise IniParseError(_('Bad Config block!'))
                    section_name = line[1:-1]
                    if section_name in self._options:
                        current_section = self._options[section_name]
                    else:
                        current_section = self._options[section_name] = {}
                else:
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        raise IniParseError(_('Bad config line!'))
                    if current_section == None:
                        raise IniParseError(_('Config line outside of block!'))
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


