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


import time


class MockSvnStatus(object):
    NONE = "none"
    UNVERSIONED = "unversioned"
    NORMAL = "normal"
    ADDED = "added"
    MISSING = "missing"
    DELETED = "deleted"
    REPLACED = "replaced"
    MODIFIED = "modified"
    MERGED = "merged"           #
    CONFLICTED = "conflicted"   #
    IGNORED = "ignored"         #
    _LIST = [NONE, UNVERSIONED, NORMAL, ADDED, MISSING, DELETED, REPLACED,
                MODIFIED, MERGED, CONFLICTED, IGNORED]
    
    @staticmethod
    def parse(s):
        s = s.lower()
        if s in self._LIST:
            return s
        else:
            return None


class _MockSvnRevision(object):
    def __init__(self, number, committedBy, logMessage, dateTime=None):
        if dateTime is None:
            dateTime = time.time()
        self.__number = number
        self.__dateTime = dateTime
        self.__committedBy = committedBy
        self.__logMessage = logMessage
    
    @property
    def number(self):
        return self.__number
    
    @property
    def committedBy(self):
        return self.__committedBy
    
    @property
    def logMessage(self):
        return self.__logMessage
    
    @property
    def dateTime(self):
        return self.__dateTime
    
    def __str__(self):
        dateTimeStr = time.ctime(self.__dateTime)
        s = "r%s | %s | %s\n%s" % (self.__number, self.__committedBy, dateTimeStr, self.__logMessage)
        return s


class MockSvnRevisions(object):
    def __init__(self):
        self.__revisions = []
        self.__changed = True
    
    @property
    def head(self):
        return self.getRevision(-1)
    
    @property
    def prev(self):
        return self.getRevision(-2)
    
    def __getChanged(self):
        return self.__changed
    def __setChanged(self, value):
        self.__changed = value
    changed = property(__getChanged, __setChanged)
    
    def getRevision(self, number):
        try:
            return self.__revisions[number]
        except:
            return None
    
    def createNextRevision(self, committedBy, logMessage, dateTime=None):
        if self.head is None:
            number = 0
        else:
            number = self.head.number + 1
        if dateTime is None:
            dateTime = time.time()
        rev = _MockSvnRevision(number, committedBy, logMessage, dateTime)
        self.__revisions.append(rev)
        self.__changed = True
        return rev



class MockSvnHistory(object):
    def __init__(self, revision, changeType):
        self.__revision=revision
        self.__changeType=None        # e.g. "added", "updated", "copied from ?", "recreated", "deleted"
    
    @property
    def revision(self):
        return self.__revision








