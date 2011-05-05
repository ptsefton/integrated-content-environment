#!/usr/bn/env python
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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

import sys
import time
import os
from cPickle import dumps, loads
from hashlib import md5
import random

os.chdir("..")
sys.path.append("../ice")
from ice_common import IceCommon

from svc_util import SvcUtil

testPath = "svc/tempTest"


class MockFileSystem(object):
    class _Dir(object):
        def __init__(self):
            self.__files = {}
            self.__dirs = {}
        @property
        def files(self):
            return self.__files
        @property
        def dirs(self):
            return self.__dirs
        def clear(self):
            self.__dirs = {}
            self.__files = {}
    
    def __init__(self, cwd="/test"):
        self.__files = {}       # name:data
        self.__rootDir = MockFileSystem._Dir()
        self.__cwd = cwd
        self.__currentDir = self.makeDirectory(cwd)
    
    @property
    def currentWorkingDirectory(self):
        return self.__cwd
    
    def split(self, path):
        return os.path.split(path)
    
    def __splitDirName(self, path, create=False):
        path = path.replace("\\", "/")
        path = path.replace("//", "/")
        if path.startswith("/"):
            dir = self.__rootDir
            path = path[1:]
        else:
            dir = self.__currentDir
        while path.find("/")!=-1:
            dname, path = path.split("/", 1)
            d = dir.dirs.get(dname, None)
            if d is None:
                if create:
                    d = MockFileSystem._Dir()
                    dir.dirs[dname] = d
                else:
                    return None, None
        return dir, path
    
    def join(self, a, *args):
        return os.path.join(a, *args)
    
    def makeDirectory(self, name):
        dir, name = self.__splitDirName(name, True)
        if not dir.dirs.has_key(name):
            dir.dirs[name] = MockFileSystem._Dir()
        return dir.dirs[name]
    
    def writeFile(self, name, data):
        print "writeFile(name='%s', data='%s')" % (name, data)
        dir, name = self.__splitDirName(name, True)
        dir.files[name] = data
    
    def readFile(self, name):
        print "readFile(name='%s')" % (name)
        dir, name = self.__splitDirName(name)
        if dir is None:
            return None
        data = dir.files.get(name, None)
        print "readFile(name='%s') data='%s'" % (name, data)
        return data
    
    def move(self, src, dest):
        dir, name = self.__splitDirName(src)
        if dir is None:
            raise Exception("src directory does not exist!")
        if dir.dirs.has_key(name):
            dDir, dName = self.__splitDirName(dest, True)
            dDir.dirs[dName] = dir.dirs[name]
            del dir.dirs[name]
        elif dir.files.has_key(name):
            dDir, dName = self.__splitDirName(dest, True)
            dDir.files[dName] = dir.files[name]
            del dir.files[name]
        else:
            raise Exception("src not file or directory not found!")
    
    def delete(self, name):
        print "delete(name='%s')" % name
        dir, name = self.__splitDirName(name)
        if dir is None:
            return
        if dir is self.__rootDir and name=="":
            dir.clear
        if dir.dirs.has_key(name): 
            del dir.dirs[name]
        if dir.files.has_key(name): 
            del dir.files[name]
    
    def isFile(self, name):
        dir, name = self.__splitDirName(name)
        return dir.files.get(name, None) is not None
    
    def isDirectory(self, name):
        dir, name = self.__splitDirName(name)
        return dir.dirs.has_key(name)
    
    def exists(self, name):
        if self.isDirectory(name):
            return True
        return self.isFile(name)
    


class MockIceCommon(object):
    def __init__(self, fs=None):
        if fs is None:
            fs = MockFileSystem()
        self.__fs = fs
        self.__idCounter = 0
    
    @property
    def fs(self):
        return self.__fs
    
    def guid(self):
        self.__idCounter += 1
        return hex(self.__idCounter)[2:].rjust(32, "0")
    
    def md5Hex(self, data):
        return md5(data).hexdigest()
    
    def loads(self, data):
        return loads(data)
    
    def dumps(self, obj):
        return dumps(obj)
    

# SvcUtil
# Constructor:
#   __init__(IceCommon)
#           # IceCommon.fs, .guid(), .loads(), .dumps(), .md5Hex()
# Properties:
#   fs
# Methods:
#   split(name)
#   guid()
#   md5Hex(data)
#   loads(data)
#   dumps(obj)
#   readRootInfoData(absPath)
#   saveRootInfo(absPath, data)
#   loadDirInfo(absPath)
#   saveDirInfo(dirInfo, absPath)
#   saveFile(absFile)
#   restoreFile(absFile)
#   deleteDir(absPath)
#   restoreDir(absPath)
class SvcUtilTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
    
    def setUp(self):
        self.iceCommon = IceCommon
        self.iceCommon = MockIceCommon()
        self.svcUtil = SvcUtil(self.iceCommon)
        self.svcUtil.SVC_DIR = "_svc"
    
    def tearDown(self):
        self.iceCommon.fs.delete(testPath)
    
    #========== TESTS ===========
    
    def testFs(self):
        svcUtil = self.svcUtil
        self.assertEquals(svcUtil.fs, self.iceCommon.fs)
    
    def testSplit(self):
        #   split(name)
        svcUtil = self.svcUtil
        path, name = svcUtil.split("test/ing/123")
        self.assertEquals(path, "test/ing")
        self.assertEquals(name, "123")
    
    def testGuid(self):
        #   guid()
        svcUtil = self.svcUtil
        guid1 = svcUtil.guid()
        guid2 = svcUtil.guid()
        self.assertEquals(len(guid1), 32)
        self.assertTrue(guid1!=guid2)
    
    def testMd5Hex(self):
        #   md5Hex(data)
        svcUtil = self.svcUtil
        md5 = svcUtil.md5Hex("Hello")
        self.assertEquals(md5, "8b1a9953c4611296a827abf8c47804d7")
    
    def testLoadsDumps(self):
        #   loads(data)
        #   dumps(obj)
        svcUtil = self.svcUtil
        obj = {"test":42, "d":{}, "l":[1,2,"three"]}
        data = svcUtil.dumps(obj)
        obj2 = svcUtil.loads(data)
        self.assertEquals(obj, obj2)
    
    def testSaveReadRootInfoData(self):
        #   saveRootInfo(absPath, data)
        #   readRootInfo(absPath)
        svcUtil = self.svcUtil
        data = "Testing RootInfo save/read\n"
        svcUtil.saveRootInfo(testPath, data)
        data2 = svcUtil.readRootInfo(testPath)
        self.assertEquals(data2, data)
        path = self.iceCommon.fs.join(testPath, svcUtil.SVC_DIR, svcUtil.ROOTINFOFILENAME)
        self.assertTrue(self.iceCommon.fs.isFile(path))
        self.assertEquals(self.iceCommon.fs.readFile(path), data)
    
    def testSaveReadDirInfo(self):
        #   saveDirInfo(absPath, data)
        #   readDirInfo(absPath)
        svcUtil = self.svcUtil
        data = "Testing DirInfo save/read\n"
        svcUtil.saveDirInfo(testPath, data)
        data2 = svcUtil.readDirInfo(testPath)
        self.assertEquals(data2, data)
        path = self.iceCommon.fs.join(testPath, svcUtil.SVC_DIR, svcUtil.DIRINFOFILENAME)
        self.assertTrue(self.iceCommon.fs.isFile(path))
        self.assertEquals(self.iceCommon.fs.readFile(path), data)
    
    def testSaveRestoreFile(self):
        #   saveFile(absFile)
        #   restoreFile(absFile)
        svcUtil = self.svcUtil
        fs = self.iceCommon.fs
        filename = "test.txt"
        file = fs.join(testPath, filename)
        data = "TestData for test.txt\n"
        fs.writeFile(file, data)
        svcUtil.saveFile(file)
        tPath = fs.join(testPath, svcUtil.SVC_DIR, filename)
        data2 = fs.readFile(tPath)
        self.assertEquals(data2, data)
        #deleting
        fs.delete(file)
        self.assertFalse(fs.exists(file))
        svcUtil.restoreFile(file)
        self.assertEquals(fs.readFile(file), data)
        #changes
        fs.writeFile(file, "changed")
        svcUtil.restoreFile(file)
        self.assertEquals(fs.readFile(file), data)
    
    def testDeleteRestoreDir(self):
        #   deleteDir(absPath)
        #   restoreDir(absPath)
        svcUtil = self.svcUtil
        fs = self.iceCommon.fs
        dirname = "subDir"
        path = fs.join(testPath, dirname)
        fs.writeFile(fs.join(path, "test.txt"), "testing\n")
        self.assertTrue(fs.exists(path))
        svcUtil.deleteDir(path)
        self.assertFalse(fs.exists(path))
        self.assertTrue(fs.exists(fs.join(testPath, svcUtil.SVC_DIR, dirname)))
        # Restore
        svcUtil.restoreDir(path)
        self.assertTrue(fs.exists(path))
        self.assertFalse(fs.exists(fs.join(testPath, svcUtil.SVC_DIR, dirname)))




if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





