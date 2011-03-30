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

from rev_info import RevInfo


class RootInfo(object):
    # Constructor:
    #   static load(svcUtil, absPath)
    #   __init__(svcUtil, absPath)
    # Properties:
    #   id
    #   name
    #   currentRevNum
    #   revInfos
    #   absPath
    #   
    # Methods:
    #   addRevision(username, logMessage, dateTime=None)
    #   save()
    #   
    @staticmethod
    def load(svcUtil, absPath):
        data = svcUtil.readRootInfo(absPath)
        if data is None:
            return None
        rootInfo = svcUtil.loads(data)
        rootInfo.__svcUtil = svcUtil
        rootInfo.__absPath = absPath
        return rootInfo
    
    
    def __init__(self, svcUtil, absPath):
        self.__id = svcUtil.guid()
        self.__name = svcUtil.split(absPath)[1]
        self.__absPath = absPath
        self.__currentRevNum = -1
        self.__revInfos = []
        self.__svcUtil = svcUtil
    
    
    @property
    def id(self):
        return self.__id
    
    
    @property 
    def name(self):
        return self.__name
    
    
    @property
    def currentRevNum(self):
        return self.__currentRevNum
    
    
    @property
    def revInfos(self):
        return self.__revInfos
    
    
    @property
    def absPath(self):
        return self.__absPath
    
    
    def addRevision(self, username, logMessage, dateTime=None):
        self.__currentRevNum += 1
        revNum = self.__currentRevNum
        revInfo = RevInfo(revNum, username, logMessage, dateTime)
        self.__revInfos.append(revInfo)
        return revInfo
    
    
    def save(self):
        svcUtil = self.__svcUtil
        absPath = self.__absPath
        data = svcUtil.dumps(self)
        svcUtil.saveRootInfo(absPath, data)
        self.__svcUtil = svcUtil
        self.__absPath = absPath


