#!/usr/bin/python
#
#    Copyright (C) 2007  Distance and e-Learning Centre, 
#    University of Southern Queensland
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import sys, os
sys.path.append("../ice")
cdir = os.getcwd()
os.chdir("..")
from ice_common import IceCommon
IceCommon.setup()
os.chdir(cdir)

from mockSvn import *

system = IceCommon.system
FileSystem = IceCommon.FileSystem
fs = IceCommon.fs


testPath = "tempTest/"


class MockFileSystem(object):
    def join(self, *args):
        return fs.join(*args)
    
    def split(self, path):
        return fs.split(path)
    
    def absolutePath(self, file):
        return file
    
    def isFile(self, file):
        return True
    
    def readFile(self, file):
        return None
    
    def writeFile(self, file, data):
        pass
    
    def copy(self, srcFile, destFile):
        pass
    
    def delete(self, file):
        pass
    
    def exists(self, file):
        return True


class MockSvnInfosTests(IceCommon.TestCase):
    def setUp(self):
        self.__fs = FileSystem()
        self.__path = testPath
        self.__infos = MockSvnInfos(self.__path, self.__fs)
        self.__fs.delete(testPath)
    
    def tearDown(self):
        pass
    
    
    def testAddFile(self):
        self.__fs.writeFile(self.__path + "test.txt", "test for adding a file")
        self.__infos.add("test.txt")
        info = self.__infos._get("test.txt")
        self.assertEqual(info.status, MockSvnStatus.ADDED)
    
    
    def testReal(self):
        self.__fs.delete("test")
        self.__fs.writeFile(self.__path + "test.txt", "Hello World!")
        self.__infos.add("test.txt")
        self.__infos.commit("test.txt", "tester", "testing real")
        self.__infos.save()
        
        info = self.__infos._get("test.txt")
        self.assertEqual(info.status, MockSvnStatus.NORMAL)
    
    
    def testDelete(self):
        self.__fs.writeFile(self.__path + "test.txt", "test for deleting a file")
        self.__infos.add("test.txt")
        self.__infos.commit("test.txt", "tester", "testing delete")
        self.__infos.delete("test.txt")
        info = self.__infos._get("test.txt")
        self.assertEqual(info.status, MockSvnStatus.DELETED)
    
    
    def testStatus(self):
        self.__fs.delete("test")
        
        self.__fs.writeFile(self.__path + "normal.txt", "normal")
        self.__infos.add("normal.txt")
        self.__infos.commit("normal.txt", "tester", "testing Status")
        
        self.__fs.writeFile(self.__path + "missing.txt", "missing")
        self.__infos.add("missing.txt")
        self.__infos.commit("missing.txt", "tester", "testing Status")
        self.__fs.delete(self.__path + "missing.txt")
        
        self.__fs.writeFile(self.__path + "deleted.txt", "deleted")
        self.__infos.add("deleted.txt")
        self.__infos.commit("deleted.txt", "tester", "testing Status")
        self.__infos.delete("deleted.txt")
        
        self.__fs.writeFile(self.__path + "replaced.txt", "normal")
        self.__infos.add("replaced.txt")
        self.__infos.commit("replaced.txt", "tester", "testing Status")
        self.__infos.delete("replaced.txt")
        self.__fs.writeFile(self.__path + "replaced.txt", "replaced")
        self.__infos.add("replaced.txt")
        
        self.__fs.writeFile(self.__path + "modified.txt", "normal")
        self.__infos.add("modified.txt")
        self.__infos.commit("modified.txt", "tester", "testing Status")
        self.__fs.writeFile(self.__path + "modified.txt", "modified")
        
        self.__fs.writeFile(self.__path + "added.txt", "added")
        self.__infos.add("added.txt")
        
        infos = self.__infos
        self.assertEqual(infos.status("added.txt"), "added")
        self.assertEqual(infos.status("deleted.txt"), "deleted")
        self.assertEqual(infos.status("missing.txt"), "missing")
        self.assertEqual(infos.status("modified.txt"), "modified")
        self.assertEqual(infos.status("normal.txt"), "normal")
        self.assertEqual(infos.status("replaced.txt"), "replaced")
    
    
    def testCommit(self):
        fs.delete("test")
        
        self.__fs.writeFile(self.__path + "test.txt", "testing commit")
        self.__infos.add("test.txt")
        self.__infos.commit("test.txt", "tester", "testing commit")
        self.assertTrue(self.__fs.exists(self.__fs.join(self.__path, MOCK_SVN_DIRNAME, "test.txt")))
        
        self.__infos.delete("test.txt")
        self.__infos.commit("test.txt", "tester", "testing commit")
        self.assertFalse(self.__fs.exists(self.__fs.join(self.__path, MOCK_SVN_DIRNAME, "test.txt")))
    
    
    def testRevert(self):
        self.__fs.writeFile(self.__path + "test.txt", "testing revert")




if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






