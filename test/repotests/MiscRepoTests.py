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
from pyrite.repository import Repo, RepoError
import os
from TestSuite import PyriteTestCase

TESTDIR = PyriteTestCase.TESTDIR

class InitTest(PyriteTestCase):
    def testInit(self):
        self.reset_test_dir()
        repo = Repo(TESTDIR)
        repo.init()
        self.assertTrue(repo.is_repo())
        self.assertEquals(repo.get_repo_dir(), os.path.join(TESTDIR, '.git'))

class CommitTest(PyriteTestCase):
    def setUp(self):
        self.reset_test_dir()
        self.repo = Repo(TESTDIR)
        self.repo.init()

    def doSimpleCommit(self, filename):
        self.createAndAdd(filename)
        c = {Repo.SUBJECT: filename}
        self.repo.commit(c)

    def testNormalCommit(self):
        fn_name = self.whoami()

        self.doSimpleCommit(fn_name)
        c = self.repo.get_commit_info('HEAD', [Repo.SUBJECT])
        self.assertTrue(c)
        self.assertEquals(c[Repo.SUBJECT], fn_name)

    def testCommitCommit(self):
        fn_name = self.whoami()

        self.doSimpleCommit(fn_name)
        c = self.repo.get_commit_info('HEAD', [Repo.SUBJECT, Repo.ID,
                                               Repo.AUTHOR, Repo.AUTHOR_DATE])
        self.assertTrue(c)
        auth = c[Repo.AUTHOR]
        del c[Repo.AUTHOR]
        auth_date = c[Repo.AUTHOR_DATE]
        del c[Repo.AUTHOR_DATE]
        subj = c[Repo.SUBJECT]
        c[Repo.SUBJECT] = 'should not be used'

        self.createAndAdd(fn_name + '2')
        self.repo.commit(c)
        c2 = self.repo.get_commit_info('HEAD', [Repo.SUBJECT, Repo.ID,
                                               Repo.AUTHOR, Repo.AUTHOR_DATE])
        self.assertEqual(auth, c2[Repo.AUTHOR])
        self.assertEqual(auth_date, c2[Repo.AUTHOR_DATE])
        self.assertEqual(subj, c2[Repo.SUBJECT])
        self.assertNotEqual(c[Repo.ID], c2[Repo.ID])

class AddTest(PyriteTestCase):
    def setUp(self):
        self.reset_test_dir()
        self.repo = Repo(TESTDIR)
        self.repo.init()

    def testSimpleAdd(self):
        fn_name = self.whoami()

        self.createAndAdd(fn_name)

    def testAddFromToplevel(self):
        fn_name = self.whoami()

        origwd = os.getcwd()
        os.chdir(TESTDIR)
        try:
            os.mkdir(os.path.join(TESTDIR, fn_name))
            self.createAndAdd(os.path.join(fn_name, fn_name))
        finally:
            os.chdir(origwd)

    def testAddFromSubdir(self):
        fn_name = self.whoami()

        origwd = os.getcwd()
        try:
            os.mkdir(os.path.join(TESTDIR, fn_name))
            os.chdir(os.path.join(TESTDIR, fn_name))
            self.touch(os.path.join(fn_name, fn_name))
            self.consume_output(self.repo.add_files(False, False, [fn_name]))
        finally:
            os.chdir(origwd)
