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

from sys import path as sysPath
sysPath.append("../../utils")

import string, types
import time, copy
from cStringIO import StringIO
from cPickle import loads, dumps        # data = dumps(obj, -1)
from file_system import FileSystem
from system import system as _system

from mockSvnObjects import *


MOCK_SVN_DIRNAME = "_mockSvn"


class MockSvnInfos(object):
    # FileSystem (fs) usage:
    #   join()
    #   readFile()  
    #   writeFile()
    #   absolutePath()
    #   isFile()
    #   split()
    infosFilename = "__infos__"
    __fs = FileSystem()
    
    @staticmethod
    def load(path, fs):
        absPath = fs.absolutePath(path)
        filePath = fs.join(absPath, MOCK_SVN_DIRNAME, MockSvnInfos.infosFilename)
        data = fs.readFile(filePath)
        obj = loads(data)
        obj.__fs = fs
        obj.__rootObject = MockSvnRootObject.load(obj.__rootAbsPath, obj.__fs)
        obj.__absPath = absPath
        return obj
    
    
    def __init__(self, path, fs, rootObject=None):
        absPath = fs.absolutePath(path)
        if rootObject is None:
            rootObject = MockSvnRootObject(rootAbsPath=absPath)
        self.__rootAbsPath = rootObject.rootAbsPath
        self.__rootObject = rootObject            # do not persist
        self.__relPathFromRoot = ""               # for checking
        self.__infos = {}
        self.__fs = fs
        self.__absPath = absPath
        self.__changed = True
    
    
    def list(self):
        keys = self.__infos.keys()
        keys.sort()
        return [self.__infos[key] for key in keys]
    
    
    def _get(self, name):
        return self.__infos.get(name)
    
    
    def add(self, name):
        if self.__infos.has_key(name):
            info = self.__infos.get(name)
            if info.status!=MockSvnStatus.DELETED:
                raise Exception("Item already under version control!")
            else:
                info.status = MockSvnStatus.REPLACED
        else:
            isFile = self.__fs.isFile(self.__fs.join(self.__absPath, name))
            if not isFile:
                raise Exception("Currently can only add files!")
            info = MockSvnItemInfo(name, isFile)
            self.__copySource(name)
            info.status = MockSvnStatus.ADDED
        self.__infos[name] = info
        self.__changed = True
    
    
    def commit(self, name, user, logMessage, rev=None):
##        NORMAL = "normal"
##        ADDED = "added"
##        MISSING = "missing"
##        DELETED = "deleted"
##        REPLACED = "replaced"
##        MODIFIED = "modified"
##        MERGED = "merged"           #
##        CONFLICTED = "conflicted"   #
##        IGNORED = "ignored"         #
        info = self.__infos.get(name)
        if info is None:
            raise Exception("Item not under version control!")
        if rev is None:
            rev = self.__rootObject.createNextRevision(user, logMessage)
        self.status(name) # get the latest status
        # decide what to do based on status
        if info.status==MockSvnStatus.ADDED or \
           info.status==MockSvnStatus.MODIFIED or \
           info.status==MockSvnStatus.REPLACED:
            self.__copySource(name)
            info.setLastChangedRevision(rev)
            info.status = MockSvnStatus.NORMAL
        elif info.status==MockSvnStatus.NORMAL:
            pass # it does not need commiting
        elif info.status==MockSvnStatus.DELETED:
            del self.__infos[name]
            info.status = MockSvnStatus.NORMAL
            self.__fs.delete(self.__fs.join(self.__absPath, MOCK_SVN_DIRNAME, name))
        elif info.status==MockSvnStatus.MISSING:
            raise Exception("File is missing.")
        self.__changed = True
    
    
    def update(self, name):
        info = self.__infos.get(name)
        if info is None:
            raise Exception("Item not under version control!")
        # Update current revision number
        info.setCurrentRevision(self.__rootObject.revisions.head)
        self.__changed = True
    
    
    def delete(self, name):
        info = self.__infos.get(name)
        if not self.__infos.has_key(name):
            raise Exception("Item is not under version control!")
        isFile = self.__fs.isFile(self.__fs.join(self.__absPath, name))
        if isFile==False:
            raise Exception("Currently can only delete files!")
        if info.status!=MockSvnStatus.NORMAL:
            raise Exception("'%s' has changed since last commit" % name)
        info.status = MockSvnStatus.DELETED
        self.__fs.delete(name)
        self.__infos[name] = info
        self.__changed = True
    
    
    def status(self, name):
        info = self.__infos.get(name)
        absPath = self.__fs.join(self.__absPath, name)
        status = ""
        if self.__isModified(name) and info.status != MockSvnStatus.REPLACED:
            if info.status == MockSvnStatus.DELETED:
                info.status = MockSvnStatus.REPLACED
            else:
                info.status = MockSvnStatus.MODIFIED
        if not self.__fs.exists(absPath) and info.status != MockSvnStatus.DELETED:
            info.status = MockSvnStatus.MISSING
        return info.status
    
    def revert(self):
        pass
    
    def save(self):
        if self.__changed:
            absPath = self.__absPath
            filePath = self.__fs.join(absPath, MOCK_SVN_DIRNAME, self.infosFilename)
            rootObject = self.__rootObject
            self.__rootObject = None
            fs = self.__fs
            self.__fs = None
            self.__changed = False
            data = dumps(self, -1)
            self.__rootObject = rootObject
            self.__fs = fs
            self.__fs.writeFile(filePath, data)
        self.__rootObject.save(self.__fs)
    
    def __copySource(self, name):
        srcFile = self.__fs.join(self.__absPath, name)
        destFile = self.__fs.join(self.__absPath, MOCK_SVN_DIRNAME, name)
        self.__fs.copy(srcFile, destFile)
    
    def __isModified(self, name):
        srcFile = self.__fs.join(self.__absPath, name)
        copiedFile = self.__fs.join(self.__absPath, MOCK_SVN_DIRNAME, name)
        srcData = self.__fs.readFile(srcFile)
        copiedData = self.__fs.readFile(copiedFile)
        return srcData!=copiedData




class MockSvnItemInfo(object):
    # Constructor
    #   __init__(name, isFile, revision, status=MockSvnStatus.ADDED)
    # Properties
    #   name
    #   currentRevision
    #   lastChangedRevision
    #   status
    #   history
    #   isFile
    #   isDirectory
    # Methods
    #   getLogs(limit=10)
    
    def __init__(self, name, isFile, revision=None, status=MockSvnStatus.ADDED):
        self.__name = name
        self.__isFile = isFile
        self.__currentRevision = None
        self.__lastChangedRevision = None
        self.__status = MockSvnStatus.ADDED
        self.__history = []             # of changes only
    
    @property
    def name(self):
        return self.__name
    
    @property
    def currentRevision(self):
        return self.__currentRevision
    
    @property
    def lastChangedRevision(self):
        return self.__lastChangedRevision
    
    def __getStatus(self):
        return self.__status
    def __setStatus(self, value):
        self.__status = value
    status = property(__getStatus, __setStatus)
    
    @property
    def isFile(self):
        return self.__isFile
    
    @property
    def isDirectory(self):
        return not self.__isFile
    
    def setLastChangedRevision(self, rev):
        self.__lastChangedRevision = rev
        self.__currentRevision = rev
    
    def setCurrentRevision(self, rev):
        self.__currentRevision = rev
    
    def getLogs(self, limit=10):
        # return upto 'limit' number of history entries (which contain revision info.)
        items = self.__history[-limit:]
        logs = [str(item.revision) for item in items]
        return logs
    
    def __str__(self):
        s = "%s | %s | %s | %s"
        if self.__currentRevision is None:
            currentRevisionNumber = "-"
        else:
            currentRevisionNumber = self.__currentRevision.number
        if self.__lastChangedRevision is None:
            lastChangedRevisionNumber = "-"
        else:
            lastChangedRevisionNumber = self.__lastChangedRevision.number
        s = s % (self.__name, currentRevisionNumber, lastChangedRevisionNumber, self.__status)
        return s




class MockSvnRootObject(object):
    rootObjectFilename = "__rootObj__"
    
    @staticmethod
    def load(path, fs):
        filePath = fs.join(path, MOCK_SVN_DIRNAME, MockSvnRootObject.rootObjectFilename)
        data = fs.readFile(filePath)
        obj = loads(data)
        obj.__rootAbsPath = path
        return obj
        
    def __init__(self, rootAbsPath):
        self.__revisions = MockSvnRevisions()
        self.__rootAbsPath = rootAbsPath
    
    @property
    def rootAbsPath(self):
        return self.__rootAbsPath
    
    @property
    def revisions(self):
        return self.__revisions
    
    @property
    def currentRevisionNumber(self):
        return self.__revisions.head.number

    def createNextRevision(self, committedBy, logMessage, dateTime=None):
        return self.__revisions.createNextRevision(committedBy, logMessage, dateTime)
    
    def save(self, fs):
        if self.__revisions.changed:
            self.__revisions.changed = False
            filePath = fs.join(self.__rootAbsPath, MOCK_SVN_DIRNAME, self.rootObjectFilename)
            data = dumps(self, -1)
            fs.writeFile(filePath, data)







