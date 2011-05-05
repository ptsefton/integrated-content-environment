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

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader

from ice_common import IceCommon
IceCommon.setup()



class IceCommonTests(object):
    def setUp(self):
        pass
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()        
    
    def tearDown(self):
        pass
        #sys.stdout = self.stdout
    
    def testInit(self):
        from file_system import FileSystem
        from system import System, system
        fileSystem = FileSystem()
        
        print IceCommon.openOfficeName
        IceCommon.setup(system, fileSystem)
    
    def testTwo(self):
        pass
    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






