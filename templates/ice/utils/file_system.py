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
from cStringIO import StringIO


class System(object):
    # Constructor
    #    __init__()
    # Properties:
    #    platform
    #    environment
    #    sysPaths
    #    isWindows
    #    isLinux
    #    isMac
    #    
    # Methods:
    #    sysPathAdd(path)
    #    cls()
    #    getOsConfigPath(appName, create=False)
    #    execute(command)
    #    start
    #    
    def __init__(self):
        self.__platform = sys.platform
        self.__environ = os.environ
        self.__sysPath = sys.path
        self.__isWindows = False
        self.__isLinux = False
        self.__isMac = False
        self.__isCli = False
        self.__system = None
        if self.__platform=="win32":
            self.__isWindows = True
        elif self.__platform.startswith("linux"):    #sys.platform=="linux2":
            self.__isLinux = True
        elif self.__platform=="darwin":
            self.__isMac = True
        elif self.__platform=="cli":
            self.__isCli = True
            import System
            self.__system = System
        else:
            raise Exception("Unknown or unsupported operating system! platform='%s'" % sys.platform)
    
    @property
    def platform(self):
        return self.__platform

    @property
    def environment(self):
        return self.__environ
    
    @property
    def sysPaths(self):
        return self.__sysPath
    
    @property
    def isWindows(self):
        return self.__isWindows
    
    @property
    def isLinux(self):
        return self.__isLinux
    
    @property
    def isMac(self):
        return self.__isMac

    @property
    def isCli(self):
        return self.__isCli

    def sysPathAdd(self, path):
        if path not in self.__sysPath:
            self.__sysPath.append(path)
    
    
    def cls(self):
        """ Clears to console window """
        try:
            if self.isWindows:
                os.system("cls")
            elif self.isCli:
                self.__system.Console.Clear()
            else:
                os.system("reset")
        except:
            print "\n\n"
    
    def getOsHomeDirectory(self):
        if self.isWindows:
            home = os.path.split(self.__getWindowsConfigPath())[0]
        else:
            home = self.__getUnixConfigPath()
        return home
    
    def getOsConfigPath(self, appName, create=False):
        appName = appName.lower()
        if self.isWindows:
            appData = self.__getWindowsConfigPath(appName)
        else:
            appData = self.__getUnixConfigPath(appName)
        if create and not os.path.exists(appData):
            os.mkdir(appData)
        return appData
    
    def __getUnixConfigPath(self, appName=None):
        appData = self.environment.get("HOME")
        if appName is not None:
            appData = os.path.join(appData, "." + appName)
        return appData
    
    def __getWindowsConfigPath(self, appName=None):
        import _winreg
        def expandvars(s):    # expand environmental variables
            def subEvn(m):    # sub %Xxxx% with os.environ variable (if there is one)
                return self.environment.get(m.group(1))
            import re
            envRegex = re.compile(r'%([^|<>=^%]+)%')
            return envRegex.sub(subEvn, s)
        
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, \
                "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
        try:
            ret = _winreg.QueryValueEx(key, "AppData")
        except:
            return None
        else:
            key.Close()
            if ret[1] == _winreg.REG_EXPAND_SZ:
                appData = expandvars(ret[0])
            else:
                appData = ret[0]
        if appName is not None:
            appData = os.path.join(appData, appName.title())
        return appData
    
    def execute(self, command, *args):
        #Note: Windows bug?  (This appears to be a problem with popen)
        #       if you have a quoted command you can not have any quoted arguments
        #       and if you do not hava a quoted command you can have any number of quoted arguments!
        cmd = command
        if not self.isWindows:
            args = ['"%s"' % arg for arg in args]
        if not cmd.startswith('"'):
            if cmd.find(" ")>-1:
                cmd = '"%s"' % cmd
        if len(args)>0:
            cmd += " " + " ".join(args)
        
        #print "--------system.execute---------"
        #print "cmd='%s'" % cmd
        #print "-------------------------------"
        
        p = os.popen(cmd)
        #time.sleep(.05)
        result = p.read()
        
        msg = ""
        closedOK = False
        for x in range(10):
            try:
                p.close()
            except:
                msg += "Failed close process - retry %s\n" % str(x)
                time.sleep(0.125)
            else:
                closedOK = True
                if x:
                    msg += "OK closed process on retry\n"
                else:
                    msg += "OK closed"
                break
        if closedOK==False:
            msg += "WARNING: Failed to close process!\n"
        return result, msg
    
    def execute2(self, command, printErr=True, *args):
        #Note: Windows bug?  (This appears to be a problem with popen)
        #       if you have a quoted command you can not have any quoted arguments
        #       and if you do not hava a quoted command you can have any number of quoted arguments!
        cmd = command
        if not self.isWindows:
            args = ['"%s"' % arg for arg in args]
        if not cmd.startswith('"'):
            if cmd.find(" ")>-1:
                cmd = '"%s"' % cmd
        if len(args)>0:
            cmd += " " + " ".join(args)
        
        stdin, stdout, stderr = os.popen3(cmd)
        #stdin.write()
        #stdin.flush()
        if printErr:
            elines = []
            while True:
                err = stderr.readline()
                if err=="":
                    break
                else:
                    sys.stdout.write("stderr> " + err)
                    elines.append(err)
            errResult = "".join(elines)
        else:
            errResult = stderr.read()
        outResult = stdout.read()
        stdin.close()
        stdout.close()
        stderr.close()
        return outResult, errResult
system = System()



class FileSystem(object):
    # Constructor
    #    __init__(cwd=".")
    # Properties:
    #    currentWorkingDirectory
    #    
    # Methods:
    #    absolutePath(path=".")
    #    join(*args)
    #    split(path)
    #    splitExt(path)
    #    splitPathFileExt(path)
    #    exists(path)
    #    isFile(path)
    #    isDirectory(path)
    #    makeDirectory(path)
    #    delete(path)
    #    copy(fromPath, toPath)
    #    move(fromPath, toPath)
    #    walk(path, filterFunc=None)
    #    walker(path, func)
    #    createTempDirectory()
    #    writeFile(path, data)
    #    readFile(path)
    #    zip(toZipFile, path="./")
    #    unzipToTempDirectory(zipFile)
    #    unzipToDirectory(zipFile, path)
    #    readFromZipFile(zipFile, filename)
    #    zipList(zipFile)
    #    addToZipFile(zipFile, filename, data)
    #    list(path=".")
    #    listFiles(path=".")
    #    listDirectories(path=".")
    #    listDirsFiles(path=".")    - return a tuple of dirs and files
    #    getModifiedTime(path)
    #    touch(path, mtime=None)
    #    chmod(path, number)
    #    
    def __init__(self, cwd="."):
        self.__cwd = "."
        self.currentWorkingDirectory = os.path.abspath(cwd)
        self.__hiddenDirectories = []
        self.__isTempDirectory = False
    
    
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
                print "Warning: cleanup up tempDirectory!"
                self.delete()
    
    @property
    def isTempDirectory(self):
        return self.__isTempDirectory
    
    
    def absPath(self, path="."):
        return self.absolutePath(path)
    def absolutePath(self, path="."):
        return os.path.abspath(os.path.join(self.__cwd, path)).replace("\\", "/")
    
    
    def join(self, *args):
        return os.path.join(*args).replace("\\", "/")
    
        
    def split(self, path):
        return os.path.split(path)
    
    
    def splitExt(self, path):
        return os.path.splitext(path)
    
    
    def splitPathFileExt(self, path):
        """ returns a tuple of (path, file, ext) """
        path, file = self.split(path)
        file, ext = self.splitExt(file)
        return path, file, ext
    
    
    def exists(self, path):
        return os.path.exists(self.absolutePath(path))
    
    
    def isFile(self, path):
        return os.path.isfile(self.absolutePath(path))
    
    
    def isDirectory(self, path):
        return os.path.isdir(self.absolutePath(path))
    
    
    def makeDirectory(self, path):
        path = self.absolutePath(path)
        if not os.path.exists(path):
            os.makedirs(path)
    
    
    def delete(self, path=None):
        """ delete/removes a file or directory (and all of its content) """
        if path is None:
            if self.__isTempDirectory:
                path = "."
            else:
                raise Exception("path argument must be given and not None!")
        if self.exists(path):
            if self.isFile(path):
                os.remove(self.absolutePath(path))
            else:
                self.__removeDirectory(self.absolutePath(path))
    
    
    def copy(self, fromPath, toPath):
        """ copy a file or directory """
        fromAbsPath = self.absolutePath(fromPath)
        toAbsPath = self.absolutePath(toPath)
        if self.isFile(fromPath):
            self.__copyFile(fromAbsPath, toAbsPath)
        if self.isDirectory(fromPath):
            self.__copyDirectory(fromAbsPath, toAbsPath)
    
    
    def move(self, fromPath, toPath):
        """ movies a file or directory """
        fromAbsPath = self.absolutePath(fromPath)
        toAbsPath = self.absolutePath(toPath)
        try:
            os.renames(fromAbsPath, toAbsPath)
        except:
            if system.isCli:
                import System.IO.File as file
                file.Move(fromAbsPath, toAbsPath)
    
    
    def walk(self, path, filterFunc=None):
        """ path = path to walk
            yields a tuple of (path, dirs, files)
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
#                elif os.path.isfile(itemPath):
#                    files.append(item)
#            orgDirs = dirs.copy()
#            p = self.join(path, dirPath[len(absPath):])
#            func(p, dirs, files)
#            if len(orgDirs)!=len(dirs):
#                for dir in orgDirs:
#                    if dir not in dirs:
#                        fNames.remove(dir)
        

    def writeFile(self, path, data):
        self.__makeParent(path)
        f = None
        try:
            f = open(self.absolutePath(path), "wb")
            f.write(data)
        finally:
            if f is not None:
                f.close()
    
    
    def readFile(self, path):
        f = None
        data = None
        try:
            try:
                f = open(self.absolutePath(path), "rb")
                data = f.read()
            finally:
                if f is not None:
                    f.close()
        except:
            pass
        return data
    
    
    def createTempDirectory(self):
        path = tempfile.mkdtemp()
        fs = FileSystem(path)
        fs.__isTempDirectory = True
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
    
    
    def unzipToTempDirectory(self, zipFile):
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
        path = self.absolutePath(path)
        return os.listdir(path)
    
    def listFiles(self, path="."):
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        return [i for i in self.list(path) if os.path.isfile(absPath + i)]
    
    def listDirectories(self, path="."):
        absPath = self.absolutePath(path)
        if not absPath.endswith("/"):
            absPath += "/"
        return [i for i in self.list(path) if os.path.isdir(absPath + i)]
    
    def listDirsFiles(self, path="."):
        absPath = self.absolutePath(path)
        dirs = []
        files = []
        if not absPath.endswith("/"):
            absPath += "/"
        for item in self.list(path):
            itemPath = absPath + item
            if os.path.isdir(itemPath):
                dirs.append(item)
            elif os.path.isfile(itemPath):
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


    def getModifiedTime(self, path):
        absPath = self.absolutePath(path)
        return os.path.getmtime(absPath)
        # access time getatime,  changed time getctime
    
    def touch(self, path, mtime=None):
        absPath = self.absolutePath(path)
        if mtime is None:
            mtime.time.time()
        #os.utime(path, accessTime, modifiedTime)
        os.utime(absPath, mtime, mtime)
        return mtime
    
    
    def chmod(self, path, number):
        absPath = self.absolutePath(path)
        os.chmod(path, number)


    # ====  Private Method  ====
    def __removeDirectory(self, dir):
        if os.path.exists(dir):
            files = os.listdir(dir)
            for file in files:
                    file = dir + "/" + file
                    if os.path.isdir(file):
                            self.__removeDirectory(file)
                    else:
                            os.remove(file)
            os.rmdir(dir)
    
    
    def __copyDirectory(self, fromAbsPath, toAbsPath, excludeDirectories=[]):
        if not os.path.exists(toAbsPath):
            os.makedirs(toAbsPath)
        for item in os.listdir(fromAbsPath):
            itemPath = os.path.join(fromAbsPath, item)
            if os.path.isfile(itemPath):
                self.__copyFile(itemPath, os.path.join(toAbsPath, item))
            else:
                if item not in excludeDirectories:
                    self.__copyDirectory(itemPath, os.path.join(toAbsPath, item))


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
            raise Exception("Can not make directory '%s', already exists as a file!" % path)
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
            raise Exception("Can not add to a closed ZipString")
        self.zip.writestr(filename, data)
    
    def close(self):
        """ closes the ZipString and release all data."""
        if self.isClosed==False:
            self.__closezip()
            self.s.close()
            self.isClosed = True
            
    def __closezip(self):
        if self.isZipClosed==False:
            self.zip.close()
            self.isZipClosed = True
            
    def getZipData(self):
        self.__closezip()
        if self.isClosed:
            raise Exception("Can not getZipData when ZipString is closed!")
        return self.s.getvalue()













