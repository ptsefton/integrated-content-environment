#!/usr/bin/env python
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

from ice_rep import *
from svn_rep import ItemStatus

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os



fs = FileSystem(".")
testFSRepZip = "testFSRep.zip"
tempFSRep = "tempFSRep"
tempFSRepUrl = ""
if system.isWindows:
    tempFSRepUrl = "file:///" + fs.join(fs.absolutePath("."), tempFSRep)
else:
    tempFSRepUrl = "file://" + fs.join(fs.absolutePath("."), tempFSRep)
tempRepPath = "tempRep"
tempRepPath2 = "tempRep2"


def removeTempFSRep():
    try:
        fs.delete(tempRepPath)
    except: pass
    try:
        fs.delete(tempRepPath2)
    except: pass
    fs.delete(tempFSRep)


def createTempFSRep():
    fs.unzipToDirectory(testFSRepZip, tempFSRep)



class IceRepositoryTests(TestCase):
    def setUp(self):
        if False:   # use mock objects
            self.basePath = "/root/"
            self.svnUrl = "http://testingSvnUrl/"
            self.history = []
            
            self.files = {"/root/.site/site.py":("#data", None)}
            self.mockFs = MockFileSystem(self.files)
            self.mockSvnRep = MockSvnRep(basePath=self.basePath, svnUrl=self.svnUrl, \
                            files=self.files, history=self.history)
            
            self.iceRep = IceRepository(basePath=self.basePath, repUrl=self.svnUrl, \
                        name="Default", svnRep=self.mockSvnRep, fileSystem=self.mockFs)
            self.iceRep.setExecDataMethod(self.dummyMethod)
        else:
            removeTempFSRep()
            createTempFSRep()
            self.svnUrl = tempFSRepUrl
            self.basePath = tempRepPath
            basePath = fs.absolutePath(self.basePath)
            svnRep = svn_rep.svnRep(basePath=basePath, svnUrl=self.svnUrl, \
                                    iceLogger=None, output=None)
            self.iceRep = IceRepository(basePath=self.basePath, repUrl=self.svnUrl, \
                        name="Default", svnRep=svnRep, fileSystem=fs)
            self.iceRep.setExecDataMethod(self.dummyMethod)
            self.iceRep2 = None
            #
            #global fs
            #fs = FileSystem(".")
            #
            def wrappedReadFile(path):
                #print "readFile('%s')" % path
                if path.endswith("/.site/site.py"):
                    return "#"
                return readFile(path)
            if fs.readFile!=wrappedReadFile:
                readFile = fs.readFile
                fs.readFile = wrappedReadFile
            #
            def wrappedIsFile(path):
                #print "isFile('%s')" % path
                if path.endswith("/.site/site.py"):
                    return True
                r = isFile(path)
                return r
            if fs.isFile!=wrappedIsFile:
                isFile = fs.isFile
                fs.isFile = wrappedIsFile
        self.xmlContent = "<body>This is some testdata.</body>"
        self.title = "Title"
    
    
    def createSecondCheckout(self):
        # Second checkout
        #self.svnUrl = tempFSRepUrl
        self.basePath2 = tempRepPath2
        basePath2 = fs.absolutePath(self.basePath2)
        svnRep2 = svn_rep.svnRep(basePath=basePath2, svnUrl=self.svnUrl, \
                                iceLogger=None, output=None)
        self.iceRep2 = IceRepository(basePath=basePath2, repUrl=self.svnUrl, \
                    name="Default", svnRep=svnRep2, fileSystem=fs)
        self.iceRep2.setExecDataMethod(self.dummyMethod)
        return self.iceRep2
    
    
    def tearDown(self):
        pass
    
    
    def dummyMethod(self, *args):
        return None
    
    
    def renderMethod(self, file, absFile, rep):
        from converted_data import ConvertedData
        #convertedData = method(file, absFile, self)
        convertedData = ConvertedData()
        convertedData.addMeta("title", self.title)
        convertedData.addMeta("testTwo", "Two")
        convertedData.addRenditionData(".xhtml.body", self.xmlContent)
        return convertedData
    
    
    #   getLogData(relPath, levels=None)
    #   update(relPath="/", report=None)
    def testUpdate(self):
        iceRep = self.iceRep
        iceRep2 = self.createSecondCheckout()
        relPath = "/TestRep/Test.txt"
        relPath2 = "/TestRep/Test2.txt"
        iceRep2.write(relPath, "Changes 2")
        iceRep2.write(relPath2, "Testing 2")
        iceRep2.sync("/TestRep")
        iceRep.update("/TestRep")
        self.assertEqual(iceRep.statusList(relPath).status, ItemStatus.Normal)
        self.assertEqual(iceRep.statusList(relPath2).status, ItemStatus.Normal)
        self.assertEqual(iceRep.getItem(relPath).read(), "Changes 2")
        self.assertEqual(iceRep.getItem(relPath2).read(), "Testing 2")
        # also test properties
    

    
    #   cleanup(relPath)
    def testCleanup(self):
        iceRep = self.iceRep
        iceRep.cleanup("TestRep")
    
    
    
    
    #   statusList(relPath, recurse=False, update=None)     # returns a list of LstItems
    def testStatusList(self):        
        iceRep = self.iceRep        
        listItems = iceRep.statusList("TestRep", recurse=False, update=False)
        
        for listItem in listItems:
            #print str(listItem),
            #print listItem.path, listItem.isfile, listItem.isdir, \
            #        listItem.isversioned, listItem.status, listItem.repos_status
            pass
        self.assertEqual(len(listItems), 4)
        listItem = listItems[2]
        self.assertEqual(listItem.path, "/TestRep/Test.txt")
        self.assertTrue(listItem.isfile)
        self.assertFalse(listItem.isdir)
        self.assertTrue(listItem.isversioned)
        self.assertEqual(listItem.status, ItemStatus.Normal)
        self.assertEqual(listItem.repos_status, None)
        # also test properties
        #  (as above)
    
    
    




# SvnRep

##"""
##=== Public Property ===
##svnUrl
##=== Public Methods ===
##__init__(basePath=None, svnUrl=None)
##setGetUsernamePasswordCallback(callback)
##login(username=None, password=None, callback=None, retries=None)
##isAuthenticated()
##isSvnUrlValid(svnUrl=None)
##logout()
##autoCreateCheckoutCheck(messageWriter=None)
##
##cleanup(path=None)
##
##revert(path, recurse=True)
##delete(path)
##mkdir(path, message="mkdir")
##move(sourcePath, destinationPath)
##copy(sourcePath, destinationPath)
##export(sourcePath, destinationPath)
##getLogData(path, levels=None)
##
###getProperty(path, name)
###setProperty(path, name, value)
###hasProperty(path, name)
###getAllPropertyNames(path)
###deleteProperty(path, name)
###deleteAllProperties(path)
##
##list(path, recurse=False, update=False, ignore=False)
##add(path, recurse=True)
##update(path, recurse=True)
##commit(path, recurse=True, message="commit")
##
##getStatus(path, update=False)
##urlList(path)
##urlCat(path)
##revision(path, includeUrl=False)    # if includeUrl -> (OutOfDate, pathRev#, urlRev#, repRev#)
##"""
class MockSvnRep(object):
    def __init__(self, basePath=None, svnUrl=None, files={}, history=[]):
        self.__basePath = basePath
        self.__svnUrl = svnUrl
        self.__loggedIn = True
        self.__committedFiles = files
        self.files = files
        self.history = history
    
    @property
    def svnUrl(self):
        return self.__svnUrl
    
    def setGetUsernamePassworkCallback(self, callback):
        pass
    
    def login(self, username=None, password=None, callback=None, retries=None):
        self.__loggedIn = True
        return True
    
    def isAuthenticated(self):
        return self.__loggedIn
    
    def isSvnUrlValid(self, svnUrl=None):
        return True
    
    def logout(self):
        self.__loggedIn = False
    
    def autoCreateCheckoutCheck(self, messageWriter=None):
        return True
    
    def cleanup(self, path=None):
        pass
    
    def revert(self, path, recurse=True):
        #self.files = dict(self.__committedFiles)
        pass
    
    def delete(self, path):
        if self.files.has_key(path):
            self.files.pop(path)
    
    def mkdir(self, path):
        if not path.endswith("/"):
            path += "/"
        self.files[path]=("[DIR]")
    
    def move(self, sourcePath, destinationPath):
        pass
    
    def copy(self, sourcePath, destinationPath):
        pass
    
    def export(self, sourcePath, destinationPath):
        pass
    
    def getLogData(self, path, levels=None):
        pass
    
    #def getProperty(self, path, name):
    #    pass
    #
    #def setProperty(self, path, name, value):
    #    pass        
    #
    #def hasProperty(self, path, name):
    #    pass
    #
    #def getAllPropertyNames(self, path):
    #    pass
    #
    #def deleteProperty(self, path, name):
    #    pass
    #
    #def deleteAllProperties(self, path):
    #    pass
    #
    
    def getStatus(self, path, update=False):
        return None
    
    def list(self, path, recurse=False, update=False, ignore=False):
        return []
    
    def add(self, path, recurse=True):
        if self.files.has_key(path):
            #self.files[path][0]
            pass
    
    def update(self, path, recurse=True):
        pass
    
    def commit(self, path, recurse=True, message="commit"):
        pass
    
    def urlList(self, path):
        pass
    
    def urlCat(self, path):
        pass
    
    def revision(path, includeUrl=False):
        return 1

    class ListItem:
        """
            path              filepath
            is_locked         boolean
            isversioned       boolean 
            status            ItemStatus object
            repos_status      ItemStatus object or None
            commit_author     commit author string
            commit_revision   integer
            commit_time       commit time
            isfile            boolean
            isdir             boolean
            text_time         text time
            revision          integer
            name              filename
        """
        def __init__(self, path):
            pass
        
        def getCompleteStatus(self):
            return "?"
        
        # ItemStatus :- An enumeration object
        #    Normal
        #    Unversioned
        #    Added
        #    Modified
        #    Deleted
        #    Missing
        #    Ignored
        #    Merged
        #    Conflicted
        #    Replaced
        #    Obstructed
        #    inComplete
        #    Unknown
        #    PropModified
        

    

class MockFileSystem(object):
#       .split, .splitExt, join
#       .exists(path), isDirectory(), isFile()
#       .makeDirectory(path)
#       .getModifiedTime(path)
#       .walk(path)
#       .listDirectories(path)
    def __init__(self, files={}):
        self.files = files
        self.dirs = {"/":[]}
        for file in files:
            if not file.startswith("/"):
                continue
            if file.endswith("/"):
                dir = file
                filename = ""
            else:
                dir, filename = os.path.split(file)
            dir = self.__addDir(dir)
            if filename!="":
                self.dirs[dir].append(filename)
    
    def __addDir(self, dir):
        if dir=="" or dir=="/":
            return "/"
        if not dir.endswith("/"):
            dir += "/"
        if not self.dirs.has_key(dir):
            self.dirs[dir] = []
            d, f = os.path.split(dir[:-1])
            d = self.__addDir(d)
            if d!="" and f!="":
                self.dirs[d].append(f+"/")
        return dir
    
    def absolutePath(self, path):
        if path==".":
            r = "/root"
        elif path.startswith("/"):
            r = path
        else:
            r = "/root/" + path
        return r
    
    def split(self, path):
        return os.path.split(path)
    
    def splitExt(self, path):
        return os.path.splitext(path)
    
    def makeDirectory(self, path):
        self.__addDir(path)
    
    def isDirectory(self, path):
        if not path.endswith("/"):
            path += "/"
        return self.dirs.has_key(path)
    
    def isFile(self, path):
        return self.files.has_key(path)
    
    def exists(self, path):
        return self.isDirectory(path) or self.isFile(path)
    
    def getModifiedTime(self, path):
        return 111
    
    def walk(self, path):
        if not path.endswith("/"):
            path += "/"
        dirnames = [i[:-1] for i in self.dirs.get(path, []) if i.endswith("/")]
        filenames = [i for i in self.dirs.get(path, []) if not i.endswith("/")]
        dirpath = path[:-1]
        yield (dirpath, dirnames, filenames)
        for path in [path+dir+"/" for dir in dirnames]:
            for x in self.walk(path):
                yield x
    
    def readFile(self, path):
        return self.files.get(path, (None, None))[0]
    
    def writeFile(self, path, data):
        dir, filename = os.path.split(path)
        dir = self.__addDir(dir)
        if filename not in self.dirs[dir]:
            self.dirs[dir].append(filename)
        oData, svnProp = self.files.get(path, (None, None))
        if svnProp is not None:
            if data!=oData:
                #svnProp data modified
                pass
        else:
            pass
        self.files[path] = (data, svnProp)
    
    def delete(self, path):
        if self.isFile(path):
            dir, filename = os.path.split(path)
            if not dir.endswith("/"):
                dir += "/"
            self.dirs[dir].remove(filename)
            del self.files[path]
        elif self.isDirectory(path):
            # delete all it's children
            if not path.endswith("/"):
                path += "/"
            for dir in self.listDirectories(path):
                self.delete(path + dir)
            for file in self.listFiles(path):
                self.delete(path + file)
            #print "del '%s'" % path
            del self.dirs[path]
            # remove dirname from it's parent
            p = os.path.split(path)[0] 
            if not p.endswith("/"):
                p += "/"
            #self.dirs[p].remove(path)
            
    
    def listFiles(self, path):
        if not path.endswith("/"):
            path += "/"
        files = [i for i in self.dirs.get(path, []) if not i.endswith("/")]
        return files
    
    def listDirectories(self, path):
        if not path.endswith("/"):
            path += "/"
        dirs = [i[:-1] for i in self.dirs.get(path, []) if i.endswith("/")]
        return dirs
    
    def __str__(self):
        return "[A Mock FileSystem object!]"



if __name__ == "__main__":
    try:
        os.system("reset")
    except:
        try:
            os.system("cls")
        except:
            print
            print
    print "---- Testing ----"
    print
    
    # Run only the selected tests
    #  Test Attribute testXxxx.slowTest = True
    #  fastOnly (do not run any slow tests)
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = ["Add", "testAddGetRemoveImage"]
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and TestCase in i.__bases__]
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            testing = []
            for i in l:
                if i.lower() not in runTests:
                    #print "Removing '%s'" % i
                    delattr(x, i)
                else:
                    #print "Testing '%s'" % i
                    testing.append(i)
        x = None
        print "Running %s selected tests - %s" % (len(testing), str(testing)[1:-1])
    
    unittest.main()





