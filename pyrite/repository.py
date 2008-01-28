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

from subprocess import Popen, PIPE
import os

class GitError(Exception):
    """Thrown when git-xxx errors"""

class Repo:
    def __init__(self, location=None):
        if location: self._location = location
        else: self._location = os.getcwd()
        self.refresh()

    def refresh(self):
        proc = Popen(('git-rev-parse', '--git-dir'), cwd=self._location,
                        stdout=PIPE, stderr=PIPE)
        if proc.wait(): self._is_repo = False
        else:
            self._is_repo = True
            self._repo_dir = proc.stdout.readline()

    def get_repo_dir(self):
        return self._repo_dir

    def is_repo(self):
        return self._is_repo

    def init(self):
        proc = Popen(('git-init'), cwd=self._location, stdout=PIPE,
                        stderr=PIPE)
        if proc.wait():
            raise GetError(serr.readlines().join('\n'))

