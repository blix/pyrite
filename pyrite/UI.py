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

from sys import stdout, stderr, stdin, exit
import os
import pyrite
import platform
from subprocess import Popen, PIPE


def affirmative(response):
    return response.lower() in ('true', 'yes', '1')

def negative(response):
    return response.lower() in ('false', 'no', '0')

class UI(object):
    def __init__(self):
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin

    def ask(self, question, responses, default):
        while True:
            self.stdout.write(question + ' [')
            first = True
            for r in responses:
                if not first:
                    self.stdout.write('/')
                else:
                    first = False
                if default == r:
                    r = r.upper()
                self.stdout.write(r)
            self.stdout.write('] ')
            answer = self.stdin.readline()
            answer = answer.strip().lower()
            if answer in responses:
                print answer
                return answer

    def _write(self, stream, msg):
        did_write = False
        try:
            if msg.__class__ == ''.__class__:
                did_write = True
                if msg[-1] == '\n':
                    stream.write(msg)
                else:
                    stream.write(msg)
                    stream.write('\n')
            else:
                for l in msg:
                    did_write = True
                    if l[-1] == '\n':
                        stream.write(l)
                    else:
                        stream.write(l)
                        stream.write('\n')
        except IOError:
            pass
        finally:
            try:
                stream.flush()
            except IOError:
                pass
        return did_write

    def info_stream(self):
        return self.stdout

    def info(self, msg):
        return self._write(self.stdout, msg)

    def error(self, msg):
        return self._write(self.stderr, msg)

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
