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
from pyrite.git.repository import Repo
from pyrite.git.gitobject import GitError
from pyrite.git.commit import Commit
import os
from TestSuite import PyriteTestCase

TESTDIR = PyriteTestCase.TESTDIR

class InitTest(PyriteTestCase):
    def testInit(self):
        self.reset_test_dir()
        repo = Repo(location=TESTDIR)
        repo.init()
        self.assertTrue(repo.is_in_repo())
        self.assertEquals(repo.get_git_dir(), os.path.join(TESTDIR, '.git'))

class CommitTest(PyriteTestCase):
    def setUp(self):
        self.reset_test_dir()
        self.repo = Repo(location=TESTDIR)
        self.repo.init()

    def doSimpleCommit(self, filename):
        self.createAndAdd(filename)
        c = {Commit.SUBJECT: filename}
        self.repo.commit(c)

    def testNormalCommit(self):
        fn_name = self.whoami()

        self.doSimpleCommit(fn_name)
        c = Commit('HEAD', data=[Commit.SUBJECT], obj=self.repo)
        self.assertTrue(c)
        self.assertEquals(c.subject, fn_name)

    def testCommitCommit(self):
        fn_name = self.whoami()

        self.doSimpleCommit(fn_name)
        c = Commit.get_raw_commits(self.repo, None, 'HEAD', 1,
                                   [Commit.SUBJECT, Commit.ID,
                                    Commit.AUTHOR, Commit.AUTHOR_DATE]).next()
        self.assertTrue(c)
        auth = c[Commit.AUTHOR]
        del c[Commit.AUTHOR]
        auth_date = c[Commit.AUTHOR_DATE]
        del c[Commit.AUTHOR_DATE]
        subj = c[Commit.SUBJECT]
        c[Commit.SUBJECT] = 'should not be used'

        self.createAndAdd(fn_name + '2')
        self.repo.commit(c)
        c2 = Commit.get_raw_commits(self.repo, None, 'HEAD', 1,
                                    [Commit.SUBJECT, Commit.ID,
                                     Commit.AUTHOR, Commit.AUTHOR_DATE]).next()
        self.assertEqual(auth, c2[Commit.AUTHOR])
        self.assertEqual(auth_date, c2[Commit.AUTHOR_DATE])
        self.assertEqual(subj, c2[Commit.SUBJECT])
        self.assertNotEqual(c[Commit.ID], c2[Commit.ID])

class AddTest(PyriteTestCase):
    def setUp(self):
        self.reset_test_dir()
        self.repo = Repo(location=TESTDIR)
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

class LogTest(PyriteTestCase):
    def setUp(self):
        self.reset_test_dir()
        self.repo = Repo(location=TESTDIR)
        self.repo.init()

    def testLog(self):
        fn_name = self.whoami()

        self.createAndAdd(fn_name)
        self.repo.commit({Commit.SUBJECT: 'test'})
        count = 0
        for commit in Commit.get_commits(self.repo, None, None):
            count += 1
        self.assertEqual(count, 1)
