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

from rev_info import RevInfo
testPath = "svc/tempTest"

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
class RevInfoTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        pass
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testAll(self):
        t = 1209433200
        revInfo = RevInfo(42, "user-name", "log message", t)
        self.assertEquals(revInfo.revNum, 42)
        self.assertEquals(revInfo.username, "user-name")
        self.assertEquals(revInfo.logMessage, "log message")
        self.assertEquals(revInfo.dateTime, t)
        #print revInfo
        expected = "Rev#42, Tue Apr 29 11:40:00 2008, username='user-name'\nlogMessage:'log message'"
        self.assertEquals(str(revInfo), expected)
    
    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





