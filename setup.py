#!/usr/bin/env python
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

from distutils.core import setup, Extension
from pyrite.repository import Repo, RepoError
import os

module1 = Extension('pyrite.writer', sources=['pyrite/writer.c'])

repo = Repo()
version=''
try:
    tag, ncommits, abbrev = repo.most_recent_tag().split('-')
    version = tag + '-' + abbrev[1:]
except:
    c = repo.get_commit_info()
    version = c[Repo.ID][:10]

f = open('pyrite/__version__.py', 'w+')
f.write('version = ' + version + '\n')

def get_template_files():
    template_files = []
    for root, dirs, files, in os.walk('templates'):
        for f in files:
            template_files.append(os.path.join(root, f))
    return template_files

setup(name='pyrite', version='0', description='Pyrite git porcelain',
      license='GNU GPL', scripts=['pyt'],
      packages=['pyrite', 'pyrite.standard'], ext_modules=[module1],
      data_files=[(os.path.join('pyrite', 'templates'), get_template_files())]
    )

