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
import os, sys

#module1 = Extension('pyrite.writer', sources=['pyrite/writer.c'])

if sys.argv[1] == 'version':
    from pyrite.git.repository import Repo, RepoError
    repo = Repo()

    version=''
    tag, distance, id = repo.describe()
    if tag and distance:
        version = '%s-%d-%s' % (tag, distance, id[:8])
    elif tag:
        version = tag
    else:
        version = tup[2]

    f = open('pyrite/__version__.py', 'w+')
    f.write('version = \'' + version + '\'\n')

elif sys.argv[1] == 'fix-home-path':
    path = os.path.expanduser(os.path.join('~', 'bin', 'pyt'))
    libpath = os.path.expanduser(os.path.join('~', 'lib', 'python'))
    if os.path.isfile(path) and os.path.isdir(libpath):
        f = open(path, 'r')
        try:
            lines = f.readlines()
            f.close()
            lines.insert(1, 'import sys\n')
            lines.insert(2, 'sys.path.insert(1, "%s")\n' % libpath)
            f = open(path, 'w+')
            f.writelines(lines)
        finally:
            if f:
                f.close()
else:
    pkgs = [
        'pyrite',
        'pyrite.commands',
        'pyrite.utils',
        'pyrite.addons',
        'pyrite.git'
    ]
    setup(name='pyrite', version='0', description='Pyrite git porcelain',
          license='GNU GPL', scripts=['pyt'],
          packages=pkgs, #ext_modules=[module1],
          package_data={'pyrite' : [os.path.join('templates', '*.tmpl')]}
        )

