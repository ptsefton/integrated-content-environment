#
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
sys.path.append("../ice")
from ice_common import IceCommon
IceCommon.setup()

from odtCreator import OdtCreator
OdtCreator.IceCommon = IceCommon

testOutput = "testData/temp.odt"
testImage = "testData/cml.png"


class TestOdtCreator(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        self.__fs = IceCommon.fs
        self.iceContext = IceCommon

    def setUp(self):
        self.__fs.delete(testOutput)
    
    def tearDown(self):
        pass
    
    def testInit(self):
        odtCreator = OdtCreator(self.iceContext)
        odtCreator.close()

    def testSave(self):
        self.assertTrue(self.__fs.exists(testOutput)==False)
        odtCreator = OdtCreator(self.iceContext)
        odtCreator.saveTo(testOutput)
        odtCreator.close()
        self.assertTrue(self.__fs.exists(testOutput))

    def testSetTitle(self):
        odtCreator = OdtCreator(self.iceContext)
        #odtCreator.setPropertyTitle("***TESTING PRO_TITLE***")
        #odtCreator.setDocumentTitle("+++TESTING DOC_TITLE+++")
        odtCreator.setTitle("TESTING TITLE")
        odtCreator.addParagraph("A new test paragraph!")
        odtCreator.saveTo(testOutput)
        odtCreator.close()

    def testX(self):
        odtCreator = OdtCreator(self.iceContext)
        odtCreator.setTitle("TESTING TITLE")
        odtCreator.addParagraph("A new test paragraph!")
        odtCreator.addImage(testImage)
        odtCreator.addParagraph("")
        odtCreator.addParagraph("A new test paragraph!")
        odtCreator.addImage(testImage, "TestImage", imageData=None, linkHref="http://www.usq.edu.au")
        odtCreator.saveTo(testOutput)
        odtCreator.close()



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())













