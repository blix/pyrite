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

    def unescape(self, line):
        idx = line.find('#')
        if idx > -1:
            line = line[:idx]
        idx = line.find(';')
        if idx > -1:
            line = line[:idx]
        line = line.replace('[!]', '!')
        return line.strip()

    def read(self):
        f = None
        try:
            f = open(self.filename, 'r')
            current_section = None
            for line in f.readlines():
                # need to preserve the original line so we can
                # not strip out qcomments etc
                orig = line
                line = self.unescape(line)
                if not line:
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
                        current_section = {}, orig
                        self._options[section_name] = current_section
                else:
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        raise IniParseError(_('Bad config line!'))
                    if current_section == None:
                        raise IniParseError(_('Config line outside of block!'))
                    name = parts[0].strip()
                    value = parts[1].strip()
                    if name in current_section:
                        current_section[name].append((value, orig))
                    current_section[0][name] = [(value, orig)]
        except (IOError, OSError):
            pass
        finally:
            if f:
                f.close()

    def get(self, section, name, default=None, num=0):
        if section in self._options:
            sec = self._options[section][0]
            if name in sec:
                return sec[name][num][0]
        return default

    def items(self, section):
        if section in self._options.iterkeys():
           for name, values in self._options[section][0].iteritems():
               for v in values:
                   yield name, v[0]

    def write(self, filename):
        import shutil
        import os
        f = None
        try:
            f = open(filename + '.tmp', 'w+')
            for section, names in self._options.iteritems():
                if names[1]:
                    f.write('\n')
                    f.write(names[1])
                else:
                    f.write('\n[%s]\n' % section)
                for name, values in names[0].iteritems():
                    for v in values:
                       if v[1]:
                           f.write(v[1])
                       else:
                           f.write('%s=%s\n' % (name, v[0]))
            f.close()
            f = None
            shutil.copyfile(filename + '.tmp', filename)
        finally:
            if f:
                f.close()
            os.remove(filename + '.tmp')

    def set(self, section, name, value, num=0):
        if section in self._options:
            sec = self._options[section][0]
        else:
            sec = {}, None
            self._options[section] = sec
        if name in sec:
            sec[0][name][num] = (value, None)
        else:
            sec[0][name] = [(value, None)]

    def remove_option(self, section, name, num=0):
        if section in self._options:
           sec = self._options[section][0]
           if name in sec:
               del sec[name][num]
               if not sec[name]:
                  del sec[name]
           if not sec:
              del self._options[section]

    def sections(self):
        for section in self._options.iterkeys():
            yield section


