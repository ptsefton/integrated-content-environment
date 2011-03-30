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

import time


class RevInfo(object):
    # Constructor:
    #   __init__(revNum, username, logMessage, dateTime=None)
    # Properties:
    #   revNum
    #   dateTime
    #   username
    #   logMessage
    # Methods:
    #   __str__()
    def __init__(self, revNum, username, logMessage, dateTime=None):
        self.__revNum = revNum
        self.__username = username
        self.__logMessage = logMessage
        if dateTime is None:
            dateTime = time.time()
        self.__dateTime = dateTime
    
    @property
    def revNum(self):
        return self.__revNum
    
    @property
    def dateTime(self):
        return self.__dateTime
    
    @property
    def username(self):
        return self.__username
    
    @property
    def logMessage(self):
        return self.__logMessage
    
    def __str__(self):
        s = "Rev#%s, %s, username='%s'\nlogMessage:'%s'"
        s = s % (self.__revNum, time.ctime(self.__dateTime), 
                    self.__username, self.__logMessage)
        return s



