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



class HistoryItem(object):
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
    def __init__(self, revNum, historyAction):
        self.__revNum = revNum
        self.__historyAction = historyAction
    
    @property
    def revNum(self):
        return self.__revNum
    
    @property
    def historyAction(self):
        return self.__historyAction
    
    def __str__(self):
        return "Rev#%s %s" % (self.__revNum, self.__historyAction)
    


class HistoryActions(object):
    class _HistoryAction(object):
        def __init__(self, name):
            self.__name = name
        def __str__(self):
            return self.__name
    AddedFile = _HistoryAction("AddedFile")
    AddedDir = _HistoryAction("AddedDir")
    Updated = _HistoryAction("Updated")
    Deleted = _HistoryAction("Deleted")
    ChangedAddedFile = _HistoryAction("ChangedAddedFile")
    ChangedAddedDir = _HistoryAction("ChangedAddedDir")



