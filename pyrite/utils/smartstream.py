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

class SmartStream(object):
    def __init__(self, stream):
        self.stream = stream
        self.buffer = None
        self.lastindex = 0
        self.buflen = 0
        self.done = False

    def readline(self):
        line = ''
        while not line or line[-1] != '\n':
            if not self.buffer or self.lastindex >= self.buflen:
                self.buffer = self.stream.read(1024 * 30)
                self.lastindex = 0
                if not self.buffer:
                    break
                self.buffer = self.buffer.splitlines(True)
                self.buflen = len(self.buffer)
            line += self.buffer[self.lastindex]
            self.lastindex += 1
        return line

