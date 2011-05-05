#!/usr/bin/env python
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(".")
    os.chdir("../..")
    from ice_common import IceCommon
# XmlTestCase        # self.assertSameXml


from plugin_oooUtils import *



class OOoUtilsTests(IceCommon.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


class OooPathTests(TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        self.out = StringIO()
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testInit(self):
        oooPath = OooPath()
    
    
    def testIsOooPathOK(self):
        #   isOooPathOK(oooPath="")
        oooPath = OooPath(output=None)
        oPath = oooPath.getBestOooPath()
        self.assertTrue(oooPath.isOooPathOK(oPath))
    
    def testGetOooPythonPath(self):
        #   getOooPythonPath(oooPath)
        oooPath = OooPath(output=None)
        oPath = oooPath.getBestOooPath()
        pPath = oooPath.getOooPythonPath(oPath)
        print "python path='%s'" % pPath
    
    def testGetBestOooPath(self):
        #   getBestOooPath()
        oooPath = OooPath(output=None)
        bestPath = oooPath.getBestOooPath()
        print "oooPath='%s'" % bestPath


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())




