import stat
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

import os
import sys
import tempfile
import zipfile
import re
import time
from hashlib import md5
from cStringIO import StringIO
from glob import glob



class FileSystem(object):
    # Constructor
    #    __init__(cwd=".")
    # Properties:
    #    currentWorkingDirectory
    #    isTempDirectory
    #    fakeFiles
    #    
    # Methods:
    #    absolutePath(path=".")
    #    normPath(path)
    #    join(*args)
    #    split(path)
    #    splitExt(path)
    #    splitPathFileExt(path)
    #    size(path)         -> returns the size of the file or None if the file does not exist (or can not be accessed)
    #    exists(path)
    #    isFile(path)
    #    isDirectory(path)
    #    makeDirectory(path)
    #    delete(path=None)
    #    copy(fromPath, toPath)
    #    move(fromPath, toPath)
    #    walk(path, filterFunc=None)
    #    walker(path, func)
    #    createTempDirectory()
    #    writeFile(path, data)
    #    readFile(path)
    #    md5OfFile(path)            - returns the md5 of a file as a HexString
    #    zip(toZipFile, path="./")
    #    unzipToTempDirectory(zipFile)
    #    unzipToDirectory(zipFile, path)
    #    readFromZipFile(zipFile, filename)
    #    zipList(zipFile)
    #    addToZipFile(zipFile, filename, data)
    #    list(path=".")
    #    glob(matchPattern, path=".")
    #    listFiles(path=".")
    #    listDirectories(path=".")
    #    listDirsFiles(path=".")    - return a tuple of dirs and files
    #    getModifiedTime(path)
    #    touch(path, mtime=None)
    #    chmod(path, number)
    #    zipString()
    #
    def __init__(self, cwd="."):
        self.__cwd = "."
        self.currentWorkingDirectory = os.path.abspath(cwd)
        self.__hiddenDirectories = []
        self.__isTempDirectory = False
        self.__fakeFiles = {}       # key-AbsPath:data-value
        self.__fakeFilesPaths = {}  # key-Path:value-list(dictKeys)-of-fakeFiles (absPath)
    
    
    def __getCwd(self):
        return self.__cwd
    def __setCwd(self, value):
        self.__cwd = self.absolutePath(value)
    currentWorkingDirectory = property(__getCwd, __setCwd)
    
    
    def __str__(self):
        return self.__cwd
    
    
    def __del__(self):
        if self.__isTempDirectory:
            if self.exists("."):
                #print "Warning: cleanup up tempDirectory '%s'!" % str(self)
                self.delete()
    
    @property
    def isTempDirectory(self):
        return self.__isTempDirectory
    
    @property
    def fakeFiles(self):
        return self.__fakeFiles
    
    @property
    def fakeFilesPaths(self):
        return self.__fakeFilesPaths
    
    
    def setAsTempDirectoryToBeDeleted(self):
        self.__isTempDirectory = True
    
    
    def clone(self, newWorkingDirectory=None):
        fs = self.__class__(self.__cwd)
        fs.__hiddenDirectories = list(self.__hiddenDirectories)
        fs.__fakeFiles = dict(self.__fakeFiles)
        fs.__fakeFilesPaths = dict(self.__fakeFilesPaths)
        if newWorkingDirectory is not None:
            fs.currentWorkingDirectory = newWorkingDirectory
        return fs
    
    
    def updateFakeFiles(self, d):
        for file, data in d.iteritems():
            absPath = self.absolutePath(file)
            self.__fakeFiles[absPath] = data
            path, name = self.split(absPath)
            if not path.endswith("/"):
                path += "/"
            d = self.__fakeFilesPaths.get(path, None)
            if d is None:
                d = {}
                self.__fakeFilesPaths[path] = d
            d[absPath] = name
            # include parent directory
            ppath, name = self.split(path[:-1])
            ppath += "/"
            name += "/"
            d = self.__fakeFilesPaths.get(ppath, None)
            if d is None:
                d = {}
                self.__fakeFilesPaths[ppath] = d
            d[path] = name      # include parent directory
    
    def absPath(self, path="."):
        return self.absolutePath(path)
    def absolutePath(self, path="."):
        return os.path.abspath(os.path.join(self.__cwd, path)).replace("\\", "/")
    
    
    def normPath(self, path):
        return os.path.normpath(path)

    
    def join(self, *args):
        return os.path.join(*args).replace("\\", "/")
    
    def parent(self, path="."):
        return self.split(path)[0]

    def split(self, path="."):
        return os.path.split(path)
    
    
    def splitExt(self, path="."):
        file, ext = os.path.splitext(path)
        return file, ext
    
    
    def splitPathFileExt(self, path="."):
        """ returns a tuple of (path, file, ext) """
        path, file = self.split(path)
        file, ext = self.splitExt(file)
        return path, file, ext
    
    def size(self, path):
        absPath = self.absolutePath(path)
        size = None
        try:
            size = os.path.getsize(absPath)
        except:
            pass
        return size
    
    def exists(self, path="."):
        absPath = self.absolutePath(path)
        r = os.path.exists(absPath)
        if r==False and \
                (self.__fakeFiles.has_key(absPath) or \
                self.__fakeFilesPaths.has_key(absPath+"/")):
            r = True
        return r
    
    
    def isFile(self, path="."):
        absPath = self.absolutePath(path)
        r = os.path.isfile(absPath)
        if r==False and self.__fakeFiles.has_key(absPath):
            r = True
        return r
    
    
    def isDirectory(self, path="."):
        absPath = self.absolutePath(path)
        r = os.path.isdir(absPath)
        if r==False and self.__fakeFilesPaths.has_key(absPath+"/"):
            r = True
        return r
    
    
    def makeDirectory(self, path="."):
        absPath = self.absolutePath(path)
        if not os.path.exists(absPath):
            os.makedirs(absPath)
    
    
    def delete(self, path=None):
        """ delete/removes a file or directory (and all of its content) """
        if path is None:
            if self.__isTempDirectory:
                path = "."
            else:
                raise Exception("path argument must be given and not None!")
        absPath = self.absolutePath(path)
        if self.exists(absPath):
            if self.isFile(absPath):
                if not self.__accessMode(absPath):
                    self.__chmod(absPath)
                os.remove(absPath)
            else:
                self.__removeDirectory(absPath)
    
    def __accessMode(self, path):
        return os.access(path, os.W_OK)
    
    def __chmod(self, path, mode=0777):
        os.chmod(path, mode)
    
    
    def copy(self, fromPath, toPath, excludingDirectories=[]):
        """ copy a file or directory """
        fromAbsPath = self.absolutePath(fromPath)
        toAbsPath = self.absolutePath(toPath)
        if self.isFile(fromPath):
            self.__copyFile(fromAbsPath, toAbsPath)
        if self.isDirectory(fromPath):
            self.__copyDirectory(fromAbsPath, toAbsPath, excludingDirectories)
    
    
    def move(self, fromPath, toPath):
        """ movies a file or directory """
        fromAbsPath = self.absolutePath(fromPath)
        toAbsPath = self.absolutePath(toPath)
        try:
            os.renames(fromAbsPath, toAbsPath)
        except:
            from system import system 
            if system.isCli:
                import System.IO.File as file
                file.Move(fromAbsPath, toAbsPath)
    
    
    def walk(self, path=".", filterFunc=None):
        """ path = path to walk
            yields a tuple of (path, dirs, files)
            Note: path will always end with a '/'
            Note: dirs can be modified to filter the walking of directories
        """
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        #self.__fakeFiles = {}
        #self.__fakeFilesPaths = {}  # key-Path:value-list(dictKeys)-of-fakeFiles (absPath)
        #if self.__fakeFilesPaths.has_key(absPath):
        #    l = self.__fakeFilesPaths[absPath]
        #    print "list='%s'" % l
        
        for dirPath, dirs, files in os.walk(absPath):
            dirPath = dirPath.replace("\\", "/")
            if not dirPath.endswith("/"):
                dirPath += "/"
            p = self.join(path, dirPath[len(absPath):])
            if callable(filterFunc):
                filterFunc(p, dirs, files)
            yield p, dirs, files
    
    
    def walker(self, path, func):
        """ path = path to walk
            func = callback function that take (path, dirs, files)
            Note: path will always end with a '/'
            Note: dirs can be modified to filter the walking of directories
        """
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        
        for dirPath, dirs, files in os.walk(absPath):
            dirPath = dirPath.replace("\\", "/")
            if not dirPath.endswith("/"):
                dirPath += "/"
            p = self.join(path, dirPath[len(absPath):])
            func(p, dirs, files)

#        def walkCallback(arg, dirPath, fNames):
#            dirPath = dirPath.replace("\\", "/")
#            if not dirPath.endswith("/"):
#                dirPath += "/"
#            dirs = []
#            files = []
#            for item in fNames:
#                itemPath = dirPath + item
#                if os.path.isdir(itemPath):
#                    dirs.append(item)
#                elif self.isFile(itemPath):
#                    files.append(item)
#            orgDirs = dirs.copy()
#            p = self.join(path, dirPath[len(absPath):])
#            func(p, dirs, files)
#            if len(orgDirs)!=len(dirs):
#                for dir in orgDirs:
#                    if dir not in dirs:
#                        fNames.remove(dir)
        
    def write(self, path, data):
        return self.writeFile(path, data)
    def writeFile(self, path, data):
        self.__makeParent(path)
        f = None
        try:
            f = open(self.absolutePath(path), "wb")
            f.write(data)
        finally:
            if f is not None:
                f.close()
    

    def read(self, path):
        return self.readFile(path)
    def readFile(self, path):
        absPath = self.absolutePath(path)
        data = None
        try:
            f = None
            try:
                f = open(absPath, "rb")
                data = f.read()
            finally:
                if f is not None:
                    f.close()
        except:
            pass
        if data is None and self.__fakeFiles.has_key(absPath):
            data = self.__fakeFiles[absPath]
        return data
    
    
    def md5OfFile(self, path="."):
        data = self.readFile(path)
        return md5(data).hexdigest()
    
    
    def createTempDirectory(self, persist=False):
        path = tempfile.mkdtemp(".ice", "ICE-")
        fs = FileSystem(path)
        fs.__isTempDirectory = not persist
        return fs
    
    
    def zip(self, toZipFile, path="./"):
        """ zip all of the content of the given path """
        dir = self.absolutePath(path)
        toZipFile = self.absolutePath(toZipFile)
        zf = zipfile.ZipFile(toZipFile, "w", zipfile.ZIP_DEFLATED)
        dir = dir.rstrip("/\\")
        for root, dirs, files in os.walk(dir):
            root = root.replace("\\", "/")
            for filename in files:
                zf.write(os.path.join(root, filename), \
                         os.path.join(root[len(dir)+1:], filename))
        zf.close()
    
    
    def unzipToTempDirectory(self, zipFile, tempDir=None):
        if tempDir is None:
            tempDir = self.createTempDirectory()
        self.unzipToDirectory(zipFile, str(tempDir))
        return tempDir
    
    
    def unzipToDirectory(self, zipFile, toPath):
#def extractAll(file, dir):
        #Adapted from the Python Cookbook example which has a couple
        # of bugs when dealing with sxw's
        #http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252508
        
        #if not dir.endswith(':') and not os.path.exists(dir):
        #    os.mkdir(dir)
        self.makeDirectory(toPath)
        dir = self.absolutePath(toPath)
        file = self.absolutePath(zipFile)
        
        zf = zipfile.ZipFile(file)
        for i, name in enumerate(zf.namelist()):
            fullname = os.path.join(dir, name)
            d, filename = os.path.split(fullname)
            try:
               os.makedirs(d)
            except:
                pass            
            if not name.endswith('/'):
                f = open(fullname, 'wb')
                f.write(zf.read(name))
                f.close()
        zf.close()
    
    
    def readFromZipFile(self, zipFile, filename, toPath=None):
        zipFile = self.absolutePath(zipFile)
        data = None
        try:
            zf = zipfile.ZipFile(zipFile)
        except:
            return None
        try:
            data = zf.read(filename)
        finally:
            zf.close()
        if toPath is not None:
            toPath = self.absolutePath(toPath)
            if os.path.isdir(toPath):
                toFile = os.path.join(toPath, filename)
            else:
                toFile = toPath
            f = open(toFile, "wb")
            f.write(data)
            f.close()
        return data
    
    
    def zipList(self, zipFile):
        """ lists all the files in a zipFile """
        zipFile = self.absolutePath(zipFile)
        zf = None
        try:
            zf = zipfile.ZipFile(zipFile)
            return zf.namelist()
        finally:
            if zf is not None:
                zf.close()
    
    
    def addToZipFile(self, zipFile, filename, data):
        """ Replaces if this filename already exists in the zip file. """
        zipFile = self.absolutePath(zipFile)
        try:
            zf = zipfile.ZipFile(zipFile, "a", zipfile.ZIP_DEFLATED)
        except:
            return False
        if filename in zf.namelist():
            # replace
            zf.close()
            return self.__replaceZipFile(zipFile, filename, data)
        else:
            # add
            try:
                zf.writestr(filename, data)
                return True
            finally:
                zf.close()
            return False
    def __replaceZipFile(self, zipFile, filename, data):
        tempDir = self.unzipToTempDirectory(zipFile)
        try:
            tempDir.writeFile(filename, data)
        except:
            pass
        tempDir.zip(toZipFile=zipFile)
        tempDir.delete()
        return True
    
    
    def list(self, path="."):
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        try:
            l = os.listdir(absPath)
        except:
            l = []
        fakeList = self.__fakeFilesPaths.get(absPath)
        if fakeList is not None:
            fl = fakeList.values()
            fl = [i.rstrip("/") for i in fl]
            fl.extend(l)
            l = list(set(fl))
        return l
    
    
    def glob(self, matchPattern, path="."):
        path = self.join(path, matchPattern)
        absPath = self.absolutePath(path)
        files = glob(absPath)
        if (not path.startswith("/")) or path.find(":")>0:
            basePathLen = len(self.__cwd)+1
            files = [f[basePathLen:] for f in files]
        return files
    
    def listFiles(self, path="."):
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        l = [i for i in self.list(path) if self.isFile(absPath + i)]
        return l
    
    def listDirectories(self, path="."):
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        return [i for i in self.list(path) if self.isDirectory(absPath + i)]
    
    def listDirsFiles(self, path="."):
        absPath = self.absolutePath(path)
        dirs = []
        files = []
        if not absPath.endswith("/"):
            absPath += "/"
        for item in self.list(path):
            itemPath = absPath + item
            if self.isDirectory(itemPath):
                dirs.append(item)
            elif self.isFile(itemPath):
                files.append(item)
        return dirs, files
    
    def search(self, path, name):
        foundFiles = []
        dirs, files = self.listDirsFiles(path)
        for file in files:
            if file==name:
                foundFiles.append(self.join(path, file))
        for dir in dirs:
            nPath = self.join(path, dir)
            if dir==name:
                foundFiles.append(nPath)
            try:
                # HACK to fix problem with recursly search self links
                if not nPath.endswith("/%s/%s" % (dir, dir)):
                    foundFiles.extend(self.search(nPath, name))
            except:
                pass
        return foundFiles
    
    def reSearch(self, path, reName, compiledRe=None):
        if compiledRe is None:
            compiledRe = re.compile(reName)
        foundFiles = []
        dirs, files = self.listDirsFiles(path)
        for file in files:
            if compiledRe.match(file) is not None:
                foundFiles.append(self.join(path, file))
        for dir in dirs:
            nPath = self.join(path, dir)
            if compiledRe.match(dir) is not None:
                foundFiles.append(nPath)
            try:
                if not nPath.endswith("/%s/%s" % (dir, dir)):
                    foundFiles.extend(self.reSearch(nPath, reName, compiledRe))
            except:
                pass
        return foundFiles


    def getModifiedTime(self, path="."):
        absPath = self.absolutePath(path)
        return os.path.getmtime(absPath)
        # access time getatime,  changed time getctime
    
    def touch(self, path=".", mtime=None):
        absPath = self.absolutePath(path)
        if mtime is None:
            mtime.time.time()
        #os.utime(path, accessTime, modifiedTime)
        os.utime(absPath, mtime, mtime)
        return mtime
    
    
    def chmod(self, path, number):
        absPath = self.absolutePath(path)
        os.chmod(path, number)
    
    
    def zipString(self):
        return ZipString()


    # ====  Private Method  ====
    def __removeDirectory(self, dir):
        if os.path.exists(dir):
            files = os.listdir(dir)
            for file in files:
                    file = dir + "/" + file
                    if os.path.isdir(file):
                            self.__removeDirectory(file)
                    else:
                            if not self.__accessMode(file):
                                self.__chmod(file)
                            os.remove(file)
            os.rmdir(dir)
    
    
    def __copyDirectory(self, fromAbsPath, toAbsPath, excludeDirectories=[]):
        if not os.path.exists(toAbsPath):
            os.makedirs(toAbsPath)
        for item in os.listdir(fromAbsPath):
            itemPath = os.path.join(fromAbsPath, item)
            if self.isFile(itemPath):
                self.__copyFile(itemPath, os.path.join(toAbsPath, item))
            else:
                if item not in excludeDirectories:
                    self.__copyDirectory(itemPath, os.path.join(toAbsPath, item),excludeDirectories)


    def __copyFile(self, fromAbsPath, toAbsPath):
        parent = os.path.split(toAbsPath)[0]
        if not os.path.exists(parent):
            self.__makeParent(toAbsPath)
            assert os.path.isdir(parent)
        f = None
        data = None
        try:
            f = open(fromAbsPath, "rb")
            data = f.read()
        finally:
            if f is not None:
                f.close()
                f = None
        try:
            f = open(toAbsPath, "wb")
            f.write(data)
        finally:
            if f is not None:
                f.close()
    
    def __makeParent(self, path):
        path = self.split(path)[0]
        if self.isDirectory(path)==True:
            return False
        if self.isFile(path):
            raise Exception("Cannot make directory '%s', already exists as a file!" % path)
        self.makeDirectory(path)
        return True
    



class ZipString:
    def __init__(self):
        self.s = StringIO()
        self.zip = zipfile.ZipFile(self.s, "w", zipfile.ZIP_DEFLATED)
        self.isZipClosed = False
        self.isClosed = False
        
    def add(self, filename, data):
        if self.isZipClosed:
            raise Exception("Cannot add to a closed ZipString")
        self.zip.writestr(filename, data)
    
    def close(self):
        """ closes the ZipString and release all data."""
        if self.isClosed==False:
            self.__closezip()
            self.s.close()
            self.isClosed = True
            
    def __closezip(self):
        for zinfo in self.zip.filelist:
            zinfo.external_attr = 0666 << 16L       # or 0777
        
        if self.isZipClosed==False:
            self.zip.close()
            self.isZipClosed = True
            
    def getZipData(self):
        self.__closezip()
        if self.isClosed:
            raise Exception("Cannot getZipData when ZipString is closed!")
        return self.s.getvalue()













