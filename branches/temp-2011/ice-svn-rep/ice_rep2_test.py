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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import os, sys
    sys.path.append("../ice")
    from ice_common import IceCommon

from ice_render import IceRender
from ice_rep2 import IceRepository

from cStringIO import StringIO


fs = IceCommon.FileSystem(".")
testFSRepZip = "testFSRep.zip"
tempFSRep = "tempFSRep"
tempFSRepUrl = ""
if IceCommon.system.isWindows:
    tempFSRepUrl = "file:///" + fs.join(fs.absolutePath("."), tempFSRep)
else:
    tempFSRepUrl = "file://" + fs.join(fs.absolutePath("."), tempFSRep)
tempRepPath = "tempRep"

logger = IceCommon.logger

#
#
#
#
#


def removeTempFSRep():
    try:
        fs.delete(tempRepPath)
    except: pass
    fs.delete(tempFSRep)


def createTempFSRep():
    fs.unzipToDirectory(testFSRepZip, tempFSRep)


class MockIceRender(object):
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   renderMethods               # e.g. {".odt":renderMethod, ".doc":renderMethod}
    #   postRenderPlugin
    # Methods:
    #   setPostRenderPlugin(postRenderMethod)
    #   getRenderableFrom(ext)      #
    #   getRenderableTypes(ext)     #
    #   getRenderableExtensions()
    #   isExtensionRenderable(ext)
    #   addRenderMethod(ext, (*)renderMethod, renditionExts)   # renderMethod*
    #   render(rep, filesToRender, output=None)
    #
    #       (*)renderMethod()  
    #               message, renderedFiles = renderMethod(rep, filesToBeRendered, output=output)
    #                  message = "ok"
    def __init__(self, iceContext):
        self.renderMethods = {}
        self.__renderMethods = {}               # e.g. {".odt": renderMethod, ".doc": renderMethod }  
        self.__renderableTypes = {}             # e.g. {".odt":[".htm", ".pdf"], ".doc":[".htm", ".pdf"], ".odm":[".pdf"]}
        self.__renderableFromCollection = {}    # e.g. {".htm":[".odt", ".doc"] , ".pdf":[".odt", ".doc", ".odm"]}
        self.postRenderPlugin = None
    def setPostRenderPlugin(self, postRender):
        self.postRenderPlugin = postRender
    def getRenderableFrom(self, ext):
        return self.__renderableFromCollection.get(ext, [])
    def getRenderableTypes(self, ext):
        return self.__renderableTypes.get(ext, [])
    def getRenderableExtensions(self):
        return self.__renderMethods.keys()
    def isExtensionRenderable(self, ext):
        return self.__renderMethods.has_key(ext)
    def addRenderMethod(self, ext, renderMethod, renditionExts):
        #print "addRenderMethod(ext='%s', renditionExts='%s')" % (ext, renditionExts)
        self.__renderMethods[ext] = renderMethod
        self.__renderableTypes[ext] = renditionExts
        for rType in renditionExts:
            if self.__renderableFromCollection.has_key(rType):
                if ext not in self.__renderableFromCollection[rType]:
                    self.__renderableFromCollection[rType].append(ext)
            else:
                self.__renderableFromCollection[rType] = [ext]
    def render(self, rep, filesToRender, output=None):
        return "ok", []



class IceRepositoryTests(IceCommon.TestCase):
    def setUp(self):
        # change the logger printHandler so that it does not print
        try:
            for handler in logger.handlers:
                if handler.__class__.__name__=="printHandler":
                    def emit(record):
                        #print handler.format(record)
                        pass
                    handler.emit = emit
        except: 
            pass
        
        self.output = StringIO()
        iceRender = IceRender(IceCommon)
        if False:   # use mock objects
            self.basePath = "/root/"
            self.svnUrl = "http://testingSvnUrl/"
            self.history = []
            
            self.files = {"/root/.site/site.py":("#data", None)}
            self.mockFs = MockFileSystem(self.files)
            self.mockSvnRep = MockSvnRep(basePath=self.basePath, svnUrl=self.svnUrl, \
                            files=self.files, history=self.history)
            self.iceRep = IceRepository(basePath=self.basePath, repUrl=self.svnUrl, \
                        name="Default", svnRep=self.mockSvnRep, fileSystem=self.mockFs, \
                        output=self.output, iceRender=iceRender)
            self.iceRep.setExecDataMethod(self.dummyMethod)
        else:
            removeTempFSRep()
            createTempFSRep()
            self.svnUrl = tempFSRepUrl
            self.basePath = tempRepPath
            basePath = fs.absolutePath(self.basePath)
            iceContext = IceCommon()
            iceContext.output = self.output
            # use the dummy indexer for testing
            iceContext.RepositoryIndexer = iceContext.DummyRepositoryIndexer  
            svnRep = IceCommon.SvnRep(iceContext, basePath=basePath, svnUrl=self.svnUrl, \
                                    iceLogger=None, output=None)
            self.iceRep = IceRepository(iceContext, basePath=self.basePath, repUrl=self.svnUrl, \
                        name="Default", svnRep=svnRep, fileSystem=fs, output=self.output, \
                        iceRender=MockIceRender(iceContext))
                        #iceRender=iceRender)
            #print "---"
            #print iceRender.getRenderableFrom(".odt")
            #print iceRender.getRenderableTypes(".odt")
            #print iceRender.getRenderableExtensions()
            #print "---"
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
    
    
    def tearDown(self):
        pass
    
    
    def dummyMethod(self, *args):
        return None
    
    
    def renderMethod(self, file, absFile, rep):
        from converted_data import convertedData
        #convertedData = method(file, absFile, self)
        convertedData = ConvertedData()
        convertedData.addMeta("title", self.title)
        convertedData.addMeta("testTwo", "Two")
        convertedData.addRenditionData(".xhtml.body", self.xmlContent)
        return convertedData
    
    
    def testInit(self):
        # Note: All done in setUp() method
        pass
    
    
    def testProps(self):
        # Properties:
        #   name        The repository name
        #   site
        #   isSetup
        #   isAuthRequired
        #   isAuthenticated
        iceRep = self.iceRep
        
        self.assertEqual(iceRep.name, "Default")
        self.assertTrue(iceRep.isSetup)
    
    
    #   getAbsPath(relPath)
    def testGetAbsPath(self):
        iceRep = self.iceRep
        absPath = iceRep.getAbsPath("TestRep")
        self.assertEqual(absPath, fs.absolutePath(self.basePath + "/TestRep"))
    
    
    

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
    IceCommon.runUnitTests(locals())





