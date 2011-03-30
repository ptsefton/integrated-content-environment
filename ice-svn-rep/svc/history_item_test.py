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

import sys
import time
import os
os.chdir("..")
sys.path.append("../ice")
from ice_common import IceCommon

from history_item import HistoryItem, HistoryActions

testPath = "svc/tempTest"

#HistoryItem
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

class HistoryItemTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testInit(self):
        hi = HistoryItem(42, HistoryActions.AddedFile)
        self.assertEquals(str(hi), "Rev#42 AddedFile")
        
        hi = HistoryItem(42, HistoryActions.Updated)
        self.assertEquals(str(hi), "Rev#42 Updated")
    

    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





