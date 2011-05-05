#!/usr/local/bin/python
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

import os
import sys
sys.path.append("../ice")
from ice_common import IceCommon

from file_system import FileSystem






class FileSystemTests(IceCommon.TestCase):
    
    def removeDirectory(self, dir):
        if os.path.exists(dir):
            files = os.listdir(dir)
            for file in files:
                    file = dir + "/" + file
                    if os.path.isdir(file):
                            self.removeDirectory(file)
                    else:
                            os.remove(file)
            os.rmdir(dir)
        
    
    def setUp(self):
        self.__testDir = "tempTestDir"
        self.fs = FileSystem(self.__testDir)
        self.removeDirectory(self.__testDir)
        assert(os.path.exists(self.__testDir)==False)
        try: os.mkdir(self.__testDir)
        except: pass
    
    def tearDown(self):
        self.removeDirectory(self.__testDir)
        pass
    
    def testCurrentWorkingDirectory(self):
        testDir = os.path.abspath(self.__testDir).replace("\\", "/")
        self.assertEqual(self.fs.currentWorkingDirectory, testDir)

    #    absolutePath(path)
    def testAbsolutePath(self):
        # on windows root will equal "c:/"
        root = os.path.abspath("/").replace("\\", "/")
        #print "root='%s'" % root
        self.assertEqual(self.fs.absolutePath("."), self.fs.currentWorkingDirectory)
        self.assertEqual(self.fs.absolutePath(".."), os.path.abspath(".").replace("\\", "/"))
        self.assertEqual(self.fs.absolutePath("/"), root)
        self.assertEqual(self.fs.absolutePath("/test/one"), root + "test/one")
        self.assertEqual(self.fs.absolutePath("/test\\one"), root + "test/one")
    
    #    join(*args)
    def testJoin(self):
        self.assertEqual(self.fs.join("one", "two", "3"), "one/two/3")
        self.assertEqual(self.fs.join("one/", "two/"), "one/two/")
        self.assertEqual(self.fs.join("one", "/two"), "/two")
        self.assertEqual(self.fs.join(".", ".."), "./..")
        
    #    split(path)
    def testSplit(self):
        self.assertEqual(self.fs.split("one/two/three"), ("one/two", "three"))
        self.assertEqual(self.fs.split("one"), ("", "one"))
        self.assertEqual(self.fs.split("../."), ("..", "."))
        self.assertEqual(self.fs.split(""), ("", ""))
    
    #    splitExt(path)
    def testSplitExt(self):
        self.assertEqual(self.fs.splitExt("one/two"), ("one/two", ""))
        self.assertEqual(self.fs.splitExt("one.two.ext"), ("one.two", ".ext"))
        self.assertEqual(self.fs.splitExt("one/two.ext/three"), ("one/two.ext/three", ""))
        self.assertEqual(self.fs.splitExt(".ext"), ("", ".ext"))
        self.assertEqual(self.fs.splitExt(""), ("", ""))
    
    #    splitPathFileExt(path)\
    def testSplitPathFileExt(self):
        self.assertEqual(self.fs.splitPathFileExt("/one/two"), ("/one", "two", ""))
        self.assertEqual(self.fs.splitPathFileExt("one.two.ext"), ("", "one.two", ".ext"))
        self.assertEqual(self.fs.splitPathFileExt("one/two.ext/three"), ("one/two.ext", "three", ""))
        self.assertEqual(self.fs.splitPathFileExt(".ext"), ("", "", ".ext"))
        self.assertEqual(self.fs.splitPathFileExt(""), ("", "", ""))
    
    #    exists(path)
    def testExists(self):
        testFile = "testExistsFile"
        testDir = "testExistsDir"
        
        self.assertFalse(self.fs.exists(testFile))
        self.assertFalse(self.fs.exists(testDir))
        f = open(os.path.join(self.__testDir, testFile), "wb")
        f.write("Testing")
        f.close()
        os.mkdir(os.path.join(self.__testDir, testDir))
        self.assertTrue(self.fs.exists(testFile))
        self.assertTrue(self.fs.exists(testDir))
        
    
    #    isFile(path)
    def testIsFile(self):
        testFile = "testIsFile"
        testDir = "testIsFileDir"
        
        self.assertFalse(self.fs.isFile(testFile))
        self.assertFalse(self.fs.isFile(testDir))
        f = open(os.path.join(self.__testDir, testFile), "wb")
        f.write("Testing")
        f.close()
        os.mkdir(os.path.join(self.__testDir, testDir))
        self.assertTrue(self.fs.isFile(testFile))
        self.assertFalse(self.fs.isFile(testDir))
    
    #    isDirectory(path)
    def testIsDirectory(self):
        testFile = "testIsDirFile"
        testDir = "testIsDir"
        
        self.assertFalse(self.fs.isDirectory(testFile))
        self.assertFalse(self.fs.isDirectory(testDir))
        f = open(os.path.join(self.__testDir, testFile), "wb")
        f.write("Testing")
        f.close()
        os.mkdir(os.path.join(self.__testDir, testDir))
        self.assertFalse(self.fs.isDirectory(testFile))
        self.assertTrue(self.fs.isDirectory(testDir))
    
    #    makeDirectory(path)
    def testMakeDirectory(self):
        dir1 = "makeDir"
        dir2 = "makeDir2/subDir/subSubDir"
        self.assertFalse(self.fs.isDirectory(dir1))
        self.assertFalse(self.fs.isDirectory(dir2))
        self.fs.makeDirectory(dir1)
        self.fs.makeDirectory(dir2)
        self.assertTrue(self.fs.isDirectory(dir1))
        self.assertTrue(self.fs.isDirectory(dir2))
    
    #    delete(path)
    def testDelete(self):
        file = "deleteFile"
        dir = "dir/subDir/subSubDir"
        self.fs.writeFile(file, "testing")
        self.fs.writeFile(self.fs.join(dir, "file"), "test")
        self.assertTrue(self.fs.isDirectory(dir))
        self.assertTrue(self.fs.isFile(file))
        self.fs.delete(file)
        self.fs.delete(dir)
        self.assertFalse(self.fs.isDirectory(dir))
        self.assertFalse(self.fs.isFile(file))
    
    #    copy(fromPath, toPath)
    def testCopy(self):
        # Simple file copy test
        fromFile = "copyFile"
        toFile = "copyToFile"
        toDirFile = "dir/subDir/copyToFile"
        self.fs.writeFile(fromFile, "test data")
        self.assertFalse(self.fs.exists(toFile))
        self.fs.copy(fromFile, toFile)
        self.fs.copy(fromFile, toDirFile)
        self.assertTrue(self.fs.exists(toFile))
        self.assertEqual(self.fs.readFile(toFile), self.fs.readFile(fromFile))
        self.assertEqual(self.fs.readFile(toDirFile), self.fs.readFile(fromFile))
        
        # Directory, subDirectory and files copy test
        dir = "copyDir"
        toDir = "copyToDir"
        self.fs.writeFile("copyDir/subDir/file", "testing")
        self.assertFalse(self.fs.exists(toDir))
        self.fs.copy(dir, toDir)
        self.assertEqual(self.fs.readFile("copyDir/subDir/file"), self.fs.readFile("copyToDir/subDir/file"))
    
    #    move(fromPath, toPath)
    def testMove(self):
        # move file test
        file = "file"
        toFile = "toFile"
        toDirFile = "dir/subDir/toFile"
        self.fs.writeFile(file, "testing")
        self.fs.move(file, toFile)
        self.assertFalse(self.fs.isFile(file))
        self.assertTrue(self.fs.isFile(toFile))
        self.fs.move(toFile, toDirFile)
        self.assertFalse(self.fs.isFile(toFile))
        self.assertTrue(self.fs.isFile(toDirFile))
        
        # move dir test
        dir = "dirToMove"
        toDir = "movedDir"
        self.fs.writeFile(self.fs.join(dir, "file"), "testing")
        self.fs.move(dir, toDir)
        self.assertFalse(self.fs.isDirectory(dir))
        self.assertTrue(self.fs.isDirectory(toDir))
        self.assertEqual(self.fs.readFile(self.fs.join(toDir, "file")), "testing")
    
    
    #  walk(path)
    def testWalk(self):
        tree = ["./one.txt", "./test/two.txt", "./test/subDir/three.txt"]
        tree.sort()
        for f in tree:
            self.fs.writeFile(f, "testData")
        rFiles = []
        for path, dirs, files in self.fs.walk("."):
            self.assertTrue(path.endswith("/"))
            for file in files:
                rFiles.append(path + file)
        rFiles.sort()
        self.assertEqual(tree, rFiles)
    
    
    #  walker(path, func)
    def testWalker(self):
        tree = ["./one.txt", "./test/two.txt", "./test/subDir/three.txt"]
        tree.sort()
        for f in tree:
            self.fs.writeFile(f, "testData")
            
        def callback(path, dirs, files):
            self.assertTrue(path.endswith("/"))
            for file in files:
                rFiles.append(path + file)
            
        rFiles = []
        self.fs.walker(".", callback)
        rFiles.sort()
        self.assertEqual(tree, rFiles)
    
    
    #  createTempDirectory
    def testCreateTempDirectory(self):
        tempDir = self.fs.createTempDirectory()
        self.assertNotEqual(tempDir, None)
        self.assertTrue(len(str(tempDir))>1)
        self.assertTrue(tempDir.isTempDirectory)
        self.assertTrue(os.path.isdir(str(tempDir)))
        
        tempDir.delete()
        #print str(tempDir)
    
    #  writeFile(path, data)
    def testWriteFile(self):
        file = "writeFile"
        data = "Testing\nThe End.\n"
        self.assertFalse(self.fs.isFile(file))
        self.fs.writeFile(file, data)
        self.assertTrue(self.fs.isFile(file))
        self.assertEqual(self.fs.readFile(file), data)
    
    #  readFile(path)
    def testReadFile(self):
        file = "writeFile"
        data = "Testing\nThe End.\n"
        self.assertFalse(self.fs.isFile(file))
        self.fs.writeFile(file, data)
        self.assertTrue(self.fs.isFile(file))
        self.assertEqual(self.fs.readFile(file), data)
    
    #  zip(toZipFile, path="./")
    def testZip(self, data="TestData\n", files=None):
        pathToZip = "zipDir"
        if files is None:
            files = ["one.txt", "two.txt", "dir/three.txt", "dir2/subDir/four.txt"]
        zipFile = "test.zip"
        for file in files:
            path = self.fs.join(pathToZip, file)
            self.fs.writeFile(path, data)
        self.fs.zip(zipFile, pathToZip)
        self.assertTrue(self.fs.isFile(zipFile))
        
    
    #  unzipToTempDirectory(zipFile)
    def testUnzipToTempDirectory(self):
        self.testZip()
        tempDir = self.fs.unzipToTempDirectory("test.zip")
        self.assertTrue(tempDir.isFile("one.txt"))
        tempDir.delete()
        
    
    #  unzipToDirectory(zipFile, path)
    def testUnzipToDirectory(self):
        data="Testing\n123\n"
        self.testZip(data=data)
        self.fs.unzipToDirectory("test.zip", "temp")
        self.assertTrue(self.fs.isDirectory("temp"))
        self.assertEqual(self.fs.readFile("temp/dir2/subDir/four.txt"), data)
    
    
    def testZipList(self):
        files = ["one.txt", "two.txt", "dir/three.txt", "dir2/subDir/four.txt"]
        self.testZip(files=files)
        list = self.fs.zipList("test.zip")
        files.sort()
        list.sort()
        self.assertEqual(list, files)
    
    #  readFromZipFile(zipFile, filename)
    def testReadFromZipFile(self):
        data="Testing\n123\n"
        self.testZip(data=data)
        result = self.fs.readFromZipFile("test.zip", "one.txt")
        self.assertEqual(data, result)
        result = self.fs.readFromZipFile("test.zip", "dir2/subDir/four.txt")
        self.assertEqual(data, result)
    
    
    #  addToZipFile(zipFile, filename, data)
    def testAddToZipFile(self):
        files = ["one.txt", "two.txt", "dir/three.txt", "dir2/subDir/four.txt"]
        self.testZip(files=files)
        # Test adding a new File
        self.fs.addToZipFile("test.zip", "newFile.txt", "testing")
        files.append("newFile.txt")
        files.sort()
        rList = self.fs.zipList("test.zip")
        rList.sort()
        self.assertEqual(rList, files)
        # Test replacing a file
        self.fs.addToZipFile("test.zip", "one.txt", "replaceData")
        rList = self.fs.zipList("test.zip")
        rList.sort()
        self.assertEqual(rList, files)
        self.assertEqual(self.fs.readFromZipFile("test.zip", "one.txt"), "replaceData")
    
    
    #  list(path=".")
    def testList(self):
        dir = "listDir"
        files = ["one", "two", "three"]
        dirs = ["four", "five"]
        for f in files:
            self.fs.writeFile(self.fs.join(dir, f), "testing")
        for d in dirs:
            self.fs.makeDirectory(self.fs.join(dir, d))
        list = self.fs.list(dir)
        list.sort()
        all = files + dirs
        all.sort()
        self.assertEqual(list, all)
    
    #  listFiles(path=".")
    def testListFiles(self):
        dir = "listDir"
        files = ["one", "two", "three"]
        dirs = ["four", "five"]
        files.sort()
        dirs.sort()
        for f in files:
            self.fs.writeFile(self.fs.join(dir, f), "testing")
        for d in dirs:
            self.fs.makeDirectory(self.fs.join(dir, d))
        list = self.fs.listFiles(dir)
        list.sort()
        self.assertEqual(list, files)
    
    #  listDirectories(path=".")
    def testDirectories(self):
        dir = "listDir"
        files = ["one", "two", "three"]
        dirs = ["four", "five"]
        for f in files:
            self.fs.writeFile(self.fs.join(dir, f), "testing")
        for d in dirs:
            self.fs.makeDirectory(self.fs.join(dir, d))
        list = self.fs.listDirectories(dir)
        list.sort()
        dirs.sort()
        self.assertEqual(list, dirs)

    #  listDirsFiles(path=".")
    def testListDirsFiles(self):
        dir = "listDir"
        files = ["one", "two", "three"]
        dirs = ["four", "five"]
        files.sort()
        dirs.sort()
        for f in files:
            self.fs.writeFile(self.fs.join(dir, f), "testing")
        for d in dirs:
            self.fs.makeDirectory(self.fs.join(dir, d))
        rdirs, rfiles = self.fs.listDirsFiles(dir)
        rdirs.sort()
        rfiles.sort()
        self.assertEqual(rdirs, dirs)
        self.assertEqual(rfiles, files)



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





