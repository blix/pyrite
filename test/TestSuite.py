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

import unittest
import os, sys

sys.path.insert(0, os.path.abspath('..'))

class PyriteTestCase(unittest.TestCase):
    TESTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'testdata'))

    def touch(self, filename):
        filename = os.path.join(PyriteTestCase.TESTDIR, filename)
        f = open(filename, 'w+')
        f.close()

    def whoami(self):
        return sys._getframe(1).f_code.co_name

    def consume_output(self, generator):
        for line in generator:
            pass

    def reset_test_dir(self):
        for curdir, dirs, files in os.walk(PyriteTestCase.TESTDIR,
                                           topdown=False):
            for f in files:
                f = os.path.abspath(os.path.join(curdir, f))
                os.remove(f)
            os.rmdir(curdir)
        os.mkdir(PyriteTestCase.TESTDIR)

def run_all_tests():
    suite = unittest.TestSuite()
    for root, dirs, files in os.walk('.'):
        if root == '.':
            continue
        modstr = '.'.join(root.split(os.sep))[2:]
        for f in files:
            if f.startswith('__') or not f.endswith('.py'):
                continue
            modstr += '.' + f[:-3]
            module = __import__(modstr)
            for c in dir(module):
                if c[0] == '_':
                    continue
                submod = module.__getattribute__(c)
                for item in dir(submod):
                    x = submod.__getattribute__(item)
                    if isinstance(x, type(object)) and \
                            issubclass(x, unittest.TestCase):
                        s = unittest.TestLoader().loadTestsFromTestCase(x)
                        suite.addTests(s)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_all_tests()
