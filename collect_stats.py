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

import os, re

exclude_paths = [
    'bin',
    'lib',
    'dist',
    '.git'
]

print ''

py_files = []

for root, dirs, files in os.walk('.'):
    parts = root.split(os.path.sep)
    if len(parts) > 1 and parts[1] in exclude_paths:
        continue
    for f in files:
        if f.endswith('.py'):
            py_files.append(os.path.join(root, f))

print 'Total number of python files: %s' % len(py_files)

empty = re.compile('^\\s*$')
comment = re.compile('^\\s*#')
imp = re.compile('^import')
frm = re.compile('^from')

num_lines = 0
for f in py_files:
    fd = open(f)
    try:
        for l in fd.readlines():
            if empty.search(l) or comment.search(l) or imp.search(l) or \
                                frm.search(l):
                continue
            num_lines += 1
    finally:
        if fd:
            fd.close()

print 'Total number of python code lines: %s\n' % num_lines

from pyrite.repository import Repo

def print_branch_stats(repo_dir, branch):
    repo = Repo(repo_dir)
    hist = repo.get_history(branch, None, -1, [Repo.AUTHOR, Repo.AUTHOR_EMAIL])
    count = 0
    authors = {}
    for commit in hist:
        count += 1
        if commit[Repo.AUTHOR] in authors:
            authors[commit[Repo.AUTHOR]][0] += 1
        else:
            authors[commit[Repo.AUTHOR]] = [1, commit[Repo.AUTHOR_EMAIL]]

    print 'Number of commits in %s: %d' % (branch, count)
    print 'Total number of authors is: %d' % len(authors)
    print 'They are...'
    num_sorted = {}
    for name, info in authors.items():
        num = info[0]
        if num in num_sorted:
            num_sorted[num].append(name + ' <' + info[1] + '>')
        else:
            num_sorted[num] = [name + ' <' + info[1] + '>']

    for n in sorted(num_sorted.keys()):
        for a in sorted(num_sorted[n]):
            print a + ': ' + str(n)
    print ''

    tag = repo.most_recent_tag(branch, abbrev=0)
    hist = repo.get_history(tag, branch, -1)
    count = 0
    for commit in hist:
        count += 1
    if count == 0:
        tag = repo.most_recent_tag(branch + '^', abbrev=0)
        hist = repo.get_history(tag, branch, -1)
        for commit in hist:
            count += 1
    if count > 0:
        print 'Number of commits since %s: %d' % (tag, count)

print_branch_stats('.', 'master')
print ''
print_branch_stats('.', 'next')
print ''