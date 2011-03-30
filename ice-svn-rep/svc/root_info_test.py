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

from svc_util import SvcUtil
from root_info import RootInfo

testPath = "svc/tempTest"

# RootInfo
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

class RootInfoTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        pass
    
    def setUp(self):
        self.svcUtil = SvcUtil(IceCommon)
        self.svcUtil.SVC_DIR = "_svc"
    
    def tearDown(self):
        IceCommon.fs.delete(testPath)
    
    def testCreate(self):
        rootInfo = RootInfo(self.svcUtil, testPath)
        self.assertEquals(len(rootInfo.id), 32)
        self.assertEquals(rootInfo.name, "tempTest")
        self.assertEquals(rootInfo.currentRevNum, -1)
        self.assertEquals(rootInfo.revInfos, [])
    
    def testSaveLoad(self):
        rootInfo = RootInfo(self.svcUtil, testPath)
        id = rootInfo.id
        rootInfo.save()
        path = IceCommon.fs.join(testPath, self.svcUtil.SVC_DIR, self.svcUtil.ROOTINFOFILENAME)
        self.assertTrue(IceCommon.fs.isFile(path))
        rootInfo = RootInfo.load(self.svcUtil, testPath)
        self.assertTrue(rootInfo!=None)
        self.assertEquals(rootInfo.id, id)
        self.assertEquals(rootInfo.absPath, testPath)
    
    def testAddRevision(self):
        #   addRevision(username, logMessage, dateTime=None)
        rootInfo = RootInfo(self.svcUtil, testPath)
        id = rootInfo.id
        rootInfo.save()
        rootInfo.load(self.svcUtil, testPath)
        rootInfo.addRevision("user1", "test0")
        self.assertEquals(rootInfo.currentRevNum, 0)
        rootInfo.addRevision("user1", "test1")
        self.assertEquals(rootInfo.currentRevNum, 1)
        self.assertEquals(len(rootInfo.revInfos), 2)
        self.assertEquals(rootInfo.revInfos[1].logMessage, "test1")


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
    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





