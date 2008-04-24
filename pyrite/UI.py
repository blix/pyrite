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

from sys import stdout, stderr, exit
import os
import pyrite
import platform
from subprocess import Popen, PIPE

class UI(object):
    def __init__(self):
        pass

    def _write(self, stream, msg):
        did_write = False
        if msg.__class__ == ''.__class__:
            did_write = True
            if msg and msg[-1] == '\n':
                stream.write(msg)
            else:
                stream.write(msg)
                stream.write('\n')
        else:
            for l in msg:
                did_write = True
                if l and l[-1] == '\n':
                    stream.write(l)
                else:
                    stream.write(l)
                    stream.write('\n')
        return did_write

    def info_stream(self):
        return stdout

    def info(self, msg):
        return self._write(stdout, msg)

    def error(self, msg):
        return self._write(stderr, msg)

    def error_out(self, msg):
        self.error(_('Error: ') + str(msg) + '\n')
        exit(2)
        
    def debug(self, msg):
        pass
        
    def get_platform_editor(self):
        if platform.system() == 'Windows': return ['write.exe']
        else: return ['/usr/bin/env', 'vi']

    def edit(self, message, extra, tmpfile, strip_prefix='#'):
        msg = ['\n']
        if message:
            if message.__class__ == ''.__class__:
                msg = [message, '\n']
            else:
                msg = message
        if extra:
            for line in extra:
                msg.append(strip_prefix)
                msg.append(' ')
                msg.append(line)
                msg.append('\n')

        editor = pyrite.config.get_option('ui.editor')
        if not editor:
            editor = self.get_platform_editor()

        path = os.path.join(pyrite.repo.get_repo_dir(), 'pyt-edit-' + tmpfile)
        f = open(path, 'w+')
        try:
            f.write(''.join(msg))
        finally:
            f.close()
        path = os.path.abspath(path)
        editor.append(path)
        proc = Popen(editor)
        if proc.wait():
            return message
        msg = None
        f = open(path, 'r')
        try:
            msg = f.readlines()
        finally:
            f.close()
            os.remove(path)
        msg = [ line for line in msg if not line.startswith(strip_prefix)]
        return ''.join(msg)
        
