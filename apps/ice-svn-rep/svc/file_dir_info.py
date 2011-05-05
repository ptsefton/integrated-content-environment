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

from root_info import RootInfo


class FileInfo(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   id
    #   name
    #   isFile
    #   isDir
    #   revNum
    #   lastChangedRevNum
    #   schedule            # Schedule.NONE=0, Schedule.Add=1, Schedule.Modify=2, Schedule.Delete=3
    # Methods:
    #   
    def __init__(self, id, name):
        self.__id = id
        self.__name = name
        self.__revNum = -1
        self.__lastChangedRevNum = -1
        self.schedule = Schedule.Add              #  (client)
        self.history = []                 # list of HistoryItems
        #self.__md5         # (server)
    
    @property
    def id(self):
        return self__id
    
    @property
    def name(self):
        return self.__name
    
    @property
    def isFile(self):
        return True
    
    @property
    def isDir(self):
        return False
    
    @property
    def revNum(self):
        return self.__revNum
    
    @property
    def lastChangedRevNum(self):
        return self.__lastChangedRevNum
    
    def setRevNum(self, revNum):
        self.__revNum = revNum
    
    def changed(self, historyItem):
        revNum = historyItem.revNum
        if revNum <= self.__lastChangedRevNum:
            raise Exception("historyItem.revNum must be greater than lastChangedRevNum!")
        self.__lastChangedRevNum = revNum
        self.__history.append(historyItem)
        if self.__revNum<revNum:
            self.__revNum = revNum



class DirInfo(FileInfo):
    # Constructor:
    #   __init__()
    # Properties:
    #   
    # Methods:
    #   
    @staticmethod
    def load(svcUtil, absPath):
        data = svcUtil.loadDirInfo(absPath)
        if data is None:
            return None
        dirInfo = svcUtil.loads(data, absPath)
        dirInfo.__svcUtil = svcUtil
        # get rootInfo object as well
        #   first try using self.__rootAbsPath
        rootInfo = RootInfo.load(svcUtil, dirInfo.__rootAbsPath)
        if rootInfo is None:
            # failed, OK now try using the relative path (in case we have been moved)
            path = svcUtil.fs.join(absPath, dirInfo.__rootRelPath)
            path = svcUtil.fs.normPath(path)
            rootInfo = RootInfo.load(svcUtil, path)
            if rootInfo is None:
                raise Exception("rootInfo object not found!")
            # else OK, so fix up absPath
            dirInfo.__rootAbsPath = path
        else:
            # make sure dirInfo.__rootRelPath is still correct
            pass
        # make sure that this is the correct rootInfo object
        if(dirInfo.__rootId!=rootInfo.Id):
            raise Exception("Can not find the correct rootInfo object!")
        dirInfo.__rootInfo = rootInfo
        return dirInfo
    
    
    def __init__(self, svcUtil, rootInfo, parentDirInfo, name):
        if parentDirInfo is None:       # root dirInfo
            self.__parentDirInfoRelPath = ""
            self.__relPath = name
        else:
            self.__parentDirInfoRelPath = parentDirInfo.relPath
            self.__relPath = svcUtil.join(self.__parentDirInfoRelPath, name)
        id = svcUtil.md5Hex(self.__relPath.lower())
        FileInfo.__init__(self, id, name)
        # for directories only
        self.__rootId = rootInfo.Id                     #  (client)
        self.__rootAbsPath = rootInfo.absPath           #  (client)
        self.__rootRelPath = None                   #  (client)
        self.__myFilesSchedule = Schedule.NONE      #  (client)
        self.__myDirsSchedule = Schedule.NONE       #  (client)
        self.__childrenRevs = []                    # 
        self.__files = {}               # key-lowercaseName : value-FileInfo
        self.__dirs = {}                # key-lowercaseName : [name, deleted]
        self.__svcUtil = svcUtil        #Note: not saved
        self.__rootInfo = rootInfo      #Note: not saved
    
    
    @property
    def isFile(self):
        return False
    
    @property
    def isDir(self):
        return True
    
    @property
    def relPath(self):
        return self.__relPath
    
    @property
    def rootRelPath(self):
        return self.__rootRelPath
    
    @property
    def parentDirInfo(self):        # is orphan?
        if self.__parentDirInfoRelPath is None:
            return None
        else:
            absPath = self.__svcUtil.fs.join(self.__rootAbsPath, self.__parentDirInfoRelPath)
            #self.__svcUtil
            return "????"
    
    
    def updateSchedule(self):       # up|down|none, check=yes|no
        s = Schedule.NONE
        for fi in self.__files:
            s |= fi.schedule
        self.__myFilesSchedule = s
        
        s = Schedule.NONE
        for di in self.__dirs:
            s |= di.schedule
        self.__myDirsSchedule = s
    
    
    def addFile(self, name):
        # first check that name is not already in use
        lname = name.lower()
        if self.__files.has_key(lname) or self.__dirs.has_key(lname):
            raise Exception("'%s' already exists" % lname)
        # check that it exists
        fullPath = self.__svcUtil.fs.join(self.__relPath, name)
        if self.__svcUtil.fs.isFile(fullPath)==False:
            raise Exception("'%s' does not exist or is not a file!" % name)
        # create new id for this item
        id = self.__svcUtil.md5Hex(fullPath.lower())
        fileInfo = FileInfo(id, name)
        self.__svcUtil.saveFile(fullPath)           # ???
        self.__files[name.lower()] = fileInfo
    
    
    def add(self, name):
        pass
    
    def delete(self, name):
        pass
    
    def revert(self, name):
        pass
    
    def committed(self, name):
        pass
    
    def update(self, name):
        pass
    
    def status(self, name=None):
        # return an array of StatusItem(s)  - name, id, revNum, lastChangedRevNum, schedule
        # if name=="." - me only
        # if name==None - all
        # else the selected item only
        statusItems = []
        if name is None:
            for i in self.__files:
                si = StatusItem(i.name, i.id, i.revNum, i.lastChangedRevNum, i.schedule)
                statusItems.append(si)
            for i in self.__dirs:
                si = StatusItem(i.name, i.id, i.revNum, i.lastChangedRevNum, i.schedule)
                statusItems.append(si)
        elif name=="." or name=="":
            si = StatusItem(self.name, self.id, self.revNum, self.lastChangedRevNum, self.schedule)
            statusItems.append(si)
        else:
            i = self.__files.get(name, None)
            if i is None:
                i = self.__dirs.get(name, None)
            if i is not None:
                si = StatusItem(i.name, i.id, i.revNum, i.lastChangedRevNum, i.schedule)
                statusItems.append(si)
        return statusItems
    
    
    def info(self):
        pass
    
    
    def save(self):
        svcUtil = self.__svcUtil
        self.__svcUtil = None
        rootInfo = self.__rootInfo
        self.__rootInfo = None
        
        absPath = svcUtil.fs.join(self.__rootAbsPath, self.__relPath)
        svcUtil.saveDirInfo(self, absPath)
        
        self.__svcUtil = svcUtil
        self.__rootInfo = rootInfo


# Status
class Schedule(object):
    NONE = 0
    Missing = 1
    Add = 2
    Modify = 4
    Delete = 8
    DeleteAdd = 16
    OutOfDate = 32
    #Deleted = 64
    #Note: Conflicting if Schedule > 32+1



class StatusItem(object):
    def __init__(self, name, id, revNum, lastChangedRevNum, schedule):
        self.name = name
        self.id = id
        self.revNum = revNum
        self.lastChangedRevNum = lastChangedRevNum
        self.schedule = schedule
