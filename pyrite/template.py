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
import time
import os.path

class Template(object):
    def __init__(self, style, color):
        self._style = style
        self._compiled_buffer = []
        self.color = color

    def compiled_buffer(self):
        return self._compiled_buffer

    def compile(self):
        parts_len = len(self._style)
        start_pos = self._style.find('{')
        end_pos = -1
        buffer = self._compiled_buffer
        repo_props = set()
        empty_dict = {}
        while start_pos > -1:
            if start_pos > end_pos + 1:
                # just text, tuple with just a string
                buffer.append((self._style[end_pos + 1:start_pos],))
            if self._style[start_pos + 1] == '{':
                # start new variable
                end_pos = start_pos
                start_pos = self._style.find('{', start_pos + 2)
            else:
                end_pos = self._style.find('}', start_pos)
                if end_pos < 0:
                    # first text segment, tuple with just a str
                    buffer.append(self._style[start_pos:],)
                else:
                    cmd = self._style[start_pos + 1:end_pos]
                    # separate formatters
                    parts = cmd.split('|')
                    # formaters are a list of (function, args-dict)
                    formatters = []
                    for p in parts[1:]:
                        # formatters can have args, put any in dict
                        # args start at the ":"
                        arg_start = p.find(':')
                        if arg_start > -1:
                            args = {}
                            # args are comma separated
                            for arg in p[arg_start + 1:].split(','):
                                name, value = arg.split('=')
                                args[name] = value
                            fn = self._get_fn(p[:arg_start])
                            formatters.append((fn, args))
                        else:
                            # get formatter func
                            fn = self._get_fn(p)
                            formatters.append((fn, empty_dict))
                    # we are parsing out what this wants to show
                    # so we can return it to caller
                    repo_props.add(self._get_repo_prop(parts[0]))
                    buffer.append((parts[0], formatters))
                    # move on
                    start_pos = self._style.find('{', end_pos + 1)
        buffer.append((self._style[end_pos + 1:],))
        return repo_props

    def short(self, input, length=7):
        length = int(length)
        if len(input) > length:
            return input[:length]
        return input

    def humandate(self, timestamp):
        t = int(timestamp)
        utc = datetime.utcfromtimestamp(t)
        return utc.strftime('%a, %d %b %Y %H:%M:%S')

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

    def ctimedate(self, timestamp):
        d = datetime.utcfromtimestamp(int(timestamp))
        return d.ctime()

    def _get_fn(self, fn_name):
        fn = getattr(self, fn_name, None)
        if fn and callable(fn):
            return fn
        raise NameError(fn_name)

    def add_if_present(self, item, to_append='\n'):
        if item:
            return item + to_append
        return item

    def get(self, item, index=0):
        return item[int(index)]

    def _get_repo_prop(self, what):
        return getattr(Repo, what, 0)

    def join(self, item, joinstr=' '):
        return joinstr.join(item)

    def static_prop_nl(self):
        return '\n'

    def static_prop_curdate(self):
        return time.mktime(datetime.utcnow().timetuple())

    def color_diff(self, item):
        if not self.color:
            return item
        return pyrite.UI.color_diff(item)

    def color_diffstat(self, item):
        if not self.color:
            return item
        return pyrite.UI.color_diffstat(item)

    def _get_data(self, data, repo, what):
        if what in data:
            return data[what]
        repo_item = getattr(Repo, what, None)
        if repo_item in data:
            return data[repo_item]
        if repo:
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
        static_item = getattr(self, 'static_prop_' + what, None)
        if static_item:
            return static_item()
        return ''

    def indent(self, item):
        if item.__class__ == ''.__class__:
            item = item.replace('\n', '\n   ')
            item = '   ' + item
            return item
        else:
            buf = ['   ' + line for line in item]
            return buf

    def write_to_stream(self, data, stream, repo=None):
        write = stream.write
        try:
            for chunk in self._generate(data, repo):
                if chunk.__class__ == ''.__class__:
                    write(chunk)
                else:
                    map(write, chunk)
        except IOError:
            pass
        finally:
            try:
                stream.flush()
            except IOError:
                pass

    def get_complete(self, data, repo=None):
        all_data = []
        for chunk in self._generate(data, repo):
            all_data.append(chunk)
        return ''.join(all_data)

    def _generate(self, data, repo=None):
        for t in self._compiled_buffer:
            if len(t) == 1:
                yield t[0]
            else:
                prop = self._get_data(data, repo, t[0])
                for formatter, args in t[1]:
                    prop = formatter(prop, **args)
                if prop == None: #dont want empty string to trigger fail
                    pyrite.ui.error_out(_('Could not display %s with %s') % t)
                yield(prop)

class FileTemplate(Template):
    def __init__(self, filename, color):
        try:
            f = None
            if not filename.endswith('.tmpl'):
                filedir = os.path.dirname(__file__)
                realname = filename + '.tmpl'
                try:
                    f = file(os.path.join(filedir, 'templates', realname))
                except IOError:
                    pyrite.ui.error_out(_('%s is not a standard '
                                          'template') % filename)
            else:
                try:
                    f = file(filename)
                except IOError:
                    pyrite.ui.error_out(_('Cannot open %s') % filename)
            style = f.read()
            Template.__init__(self, style, color)
        finally:
            if f:
                f.close()
