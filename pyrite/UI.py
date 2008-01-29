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

import sys, os
import pyrite
import platform
from subprocess import Popen, PIPE

class UI(object):
    def __init__(self):
        pass
        
    def info(self, msg):
        print msg
       
    def error_out(self, msg):
        sys.stderr.write(str(msg) + '\n')
        sys.exit(2)
        
    def debug(self, msg):
        pass
        
    def get_platform_editor(self):
        if platform.system() == 'Windows': return ['write.exe']
        else: return ['/bin/env', 'vi']

    def edit(self, message, extra, tmpfile, strip_prefix='#'):
        msg = ''
        if message: msg = message
        if extra:
            for line in extra:
                msg += strip_prefix + ' ' + line + '\n'
        editor = pyrite.config.get_option('ui.editor')
        if not editor:
            editor = self.get_platform_editor()
        f = open(tmpfile, 'w+')
        try: f.write(msg)
        finally: f.close()
        tmpfile = os.path.abspath(tmpfile)
        editor.append(tmpfile)
        print editor
        proc = Popen(editor)
        if proc.wait(): return message
        msg = None
        f = open(tmpfile, 'r')
        try: msg = f.readlines()
        finally:
            f.close()
            os.remove(tmpfile)
        if not msg: return message
        msg = [ line for line in msg if not line.startswith(strip_prefix)]
        return ''.join(msg)
        
