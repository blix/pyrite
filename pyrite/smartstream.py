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
        self.lastidx = 0
        self.done = False

    def readlines(self):
        for line in self.readline():
            yield line

    def readline(self):
        if not self.buffer:
            self.buffer = self.stream.read(1024 * 20)
        nextidx = self.buffer.find('\n', self.lastidx) + 1
        if self.lastidx > -1:
            if nextidx > 0:
                s = self.buffer[self.lastidx:nextidx]
                self.lastidx = nextidx
                return s
            arrbuf = [self.buffer[self.lastidx:]]
            while True:
                buf2 = self.stream.read(1024 * 20)
                if not buf2:
                    self.buffer = buf2
                    s = ''.join(arrbuf)
                    return s
                nextidx = buf2.find('\n') + 1
                if nextidx > 0:
                    arrbuf.append(buf2[:nextidx])
                    self.lastidx = nextidx
                    self.buffer = buf2
                    s = ''.join(arrbuf)
                    return s
                else:
                    arrbuf.append(buf2)

