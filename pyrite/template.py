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
from pyrite.repository import Repo
from datetime import datetime
import os.path

class Template(object):
    def __init__(self, style):
        self._style = style
        self._compiled_buffer = []

    def compile(self):
        parts_len = len(self._style)
        start_pos = self._style.find('{')
        end_pos = -1
        buffer = self._compiled_buffer
        repo_props = 0
        while start_pos > -1:
            if start_pos > end_pos + 1:
                buffer.append((self._style[end_pos + 1:start_pos],))
            if self._style[start_pos + 1] == '{':
                end_pos = start_pos
                start_pos = self._style.find('{', start_pos + 2)
            else:
                end_pos = self._style.find('}', start_pos)
                if end_pos < 0:
                    buffer.append(self._style[start_pos:],)
                else:
                    cmd = self._style[start_pos + 1:end_pos]
                    sep_idx = cmd.find('|')
                    if sep_idx > -1:
                        prop = cmd[:sep_idx]
                        repo_props |= self._get_repo_prop(prop)
                        buffer.append((prop, cmd[sep_idx + 1:]))
                    else:
                        repo_props |= self._get_repo_prop(cmd)
                        buffer.append((cmd, None))
                    start_pos = self._style.find('{', end_pos + 1)
        buffer.append((self._style[end_pos + 1:],))
        return repo_props

    def short(self, input, length=6):
        if len(input) > length:
            return input[:lenthg]
        return input

    def humandate(self, timestamp):
        d = datetime.utcfromtimestamp(int(timestamp))
        return d.strftime('%a, %d %b %Y %H:%M:%S %z')

    def timestamp(self, timestamp):
        return timestamp

    def shortdate(self, timestamp):
        d = datetime.utcfromtimestamp(int(timestamp))
        return d.strftime('%Y-%m-%d')

    def reladate(self, timestamp, onlyshort=True):
        n = datetime.utcnow()
        d = datetime.utcfromtimestamp(int(timestamp))
        delta = n - d
        if delta.days > 10 and onlyshort:
            return shortdate(timestamp)

        if delta.days > 365:
            return _('%d years ago') % (delta.days // 365)
        if delta.days > 30:
            return _('%d months ago') % (delta.days // 30)
        if delta.days > 7:
            return _('%d weeks ago') % (delta.days // 7)
        if delta.days:
            return _('%d days ago') % delta.days
        if delta.seconds > 60*60:
            return _('%d hours ago') % (delta.seconds // (60*60))
        if delta.seconds > 60:
            return _('%d minutes ago') % (delta.seconds // 60)
        return _('%d seconds ago') % delta.seconds

    def isodate(self, timestamp):
        d = datetime.utcfromtimestamp(int(timestamp))
        return d.isoformat()

    def _get_fn(self, fn_name):
        fn = getattr(self, fn_name, None)
        if fn and callable(fn):
            return fn
        raise NameError(fn_name)

    def absent_ok(self, item):
        if not item:
            return ''
        return item

    def _get_repo_prop(self, what):
        return getattr(Repo, what, 0)

    def _get_data(self, data, repo, what):
        if what in data:
            return data[what]
        repo_item = getattr(repo, what, None)
        if repo_item in data:
            return data[repo_item]
        if what == 'branch':
            return repo.branch()
        if what == 'branches':
            return repo.branches()
        if what == 'remotes':
            return repo.remotes()
        if what == 'all_branches':
            ret = repo.branches().copy()
            ret.extend(repo.remotes())
            return ret
        return None

    def generate(self, data, repo=None):
        local_buffer = []
        for t in self._compiled_buffer:
            if len(t) == 1:
                local_buffer.append(t[0])
            else:
                prop = self._get_data(data, repo, t[0])
                if t[1]:
                    fmt_fn = self._get_fn(t[1])
                    local_buffer.append(fmt_fn(prop))
                else:
                    local_buffer.append(prop)

        pyrite.ui.raw_write(''.join(local_buffer))

class FileTemplate(Template):
    def __init__(self, filename):
        if os.path.isabs(filename):
            f = file(filename)
            style = f.read()
            Template.__init__(self, style)
        else:
            filedir = os.path.dirname(__file__)
            if not filename.endswith('.tmpl'):
                filename = filename + '.tmpl'
            f = file(os.path.join(filedir, '..', 'templates', filename))
            style = f.read()
            Template.__init__(self, style)