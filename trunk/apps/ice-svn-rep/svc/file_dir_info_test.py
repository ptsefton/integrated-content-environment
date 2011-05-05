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
from history_item import HistoryItem, HistoryActions    # HistoryItem(revNum, HistoryActions)
from file_dir_info import FileInfo, DirInfo


testPath = "svc/tempTest"


class FileInfoTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        pass
    
    def setUp(self):
        self.svcUtil = SvcUtil(IceCommon)
        self.svcUtil.SVC_DIR = "_svc"
    
    def tearDown(self):
        IceCommon.fs.delete(testPath)
        pass
    
    def testOne(self):
        print "-ok-"


    
class DirInfoTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        pass
    
    def setUp(self):
        self.svcUtil = SvcUtil(IceCommon)
        self.svcUtil.SVC_DIR = "_svc"
    
    def tearDown(self):
        IceCommon.fs.delete(testPath)
        pass
    
    def testOne(self):
        print "-ok-"

    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





