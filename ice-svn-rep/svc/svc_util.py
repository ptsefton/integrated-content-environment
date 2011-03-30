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



class SvcUtil(object):
    SVC_DIR = ".svc"
    ROOTINFOFILENAME = "rootInfo.dat"
    DIRINFOFILENAME = "dirInfo.dat"
    
    # Constructor:
    #   __init__(iceContext)
    #           # iceContext.fs, .guid(), .loads(), .dumps(), .md5Hex()
    # Properties:
    #   fs
    # Methods:
    #   split(name)
    #   guid()
    #   md5Hex(data)
    #   loads(data)
    #   dumps(obj)
    #   readRootInfo(absPath)
    #   saveRootInfo(absPath, data)
    #   readDirInfo(absPath)
    #   saveDirInfo(absPath, data)
    #   saveFile(absFile)
    #   restoreFile(absFile)
    #   deleteDir(absPath)
    #   restoreDir(absPath)
    #   
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
    
    @property
    def fs(self):
        return self.__fs
    
    
    def split(self, name):
        return self.__fs.split(name)
    
    
    def guid(self):
        return self.iceContext.guid()
    
    
    def md5Hex(self, data):
        return self.iceContext.md5Hex(data)
    
    
    def loads(self, data):
        return self.iceContext.loads(data)
    
    
    def dumps(self, obj):
        return self.iceContext.dumps(obj)
    
    
    #???
    def saveRootInfo(self, absPath, data):
        path = self.__fs.join(absPath, self.SVC_DIR, self.ROOTINFOFILENAME)
        self.__fs.writeFile(path, data)
    
    
    #???
    def readRootInfo(self, absPath):
        data = None
        path = self.__fs.join(absPath, self.SVC_DIR, self.ROOTINFOFILENAME)
        data = self.__fs.readFile(path)
        return data
    
    
    #???
    def saveDirInfo(self, absPath, data):
        path = self.__fs.join(absPath, self.SVC_DIR, self.DIRINFOFILENAME)
        self.__fs.writeFile(path, data)
    
    
    #???
    def readDirInfo(self, absPath):
        path = self.__fs.join(absPath, self.SVC_DIR, self.DIRINFOFILENAME)
        data = self.__fs.readFile(path)
        return data
    
    
    #???
    def saveFile(self, absFile):
        path, filename = self.__fs.split(absFile)
        toFile = self.__fs.join(path, self.SVC_DIR, filename)
        data = self.__fs.readFile(absFile)
        self.__fs.writeFile(toFile, data)
    
    
    #???
    def restoreFile(self, absFile):
        print "restoreFile()"
        path, filename = self.__fs.split(absFile)
        print "path='%s', filename='%s'" % (path, filename)
        fromFile = self.__fs.join(path, self.SVC_DIR, filename)
        print "fromFile='%s'" % fromFile
        data = self.__fs.readFile(fromFile)
        self.__fs.writeFile(absFile, data)
    
    
    #???
    def deleteDir(self, absPath):
        print "deleteDir()"
        absPath = absPath.rstrip("/")
        path, name = self.__fs.split(absPath)
        toPath = self.__fs.join(path, self.SVC_DIR, name)
        self.__fs.move(absPath, toPath)
    
    
    #???
    def restoreDir(self, absPath):
        absPath = absPath.rstrip("/")
        path, name = self.__fs.split(absPath)
        fromPath = self.__fs.join(path, self.SVC_DIR, name)
        self.__fs.move(fromPath, absPath)



# RevInfo
# Constructor:
#   __init__(revNum, username, logMessage, dateTime=None)
# Properties:
#   revNum
#   dateTime
#   username
#   logMessage
# Methods:
#   __str__()

# HistoryItem
# Constructor:
#   __init__(revNum, historyAction)
# Properties:
#   revNum
#   historyAction
# Methods:
#   __str__()
# HistoryActions
#   AddedFile
#   AddedDir
#   Updated
#   Deleted
#   ChangedAddedFile
#   ChangedAddedDir

