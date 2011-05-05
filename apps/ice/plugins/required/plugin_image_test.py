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

from plugin_image import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os

import sys
sys.path.append("../../../utils")
from file_system import FileSystem

testFile1 = "testData/testTransparent2.gif"
testFile2 = "testData/testNonTrans.gif"
tempGifFile = "testData/temp.gif"
tempJpgFile = "testData/temp.jpg"


class IceImageTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def __getData(self, filename):
        f = open(filename, "rb")
        data = f.read()
        f.close()
        return data


    def xtestHasTransparency(self):
        imageData = self.__getData(testFile1)
        im = IceImage(imageData)
        self.assertTrue(im.hasTransparency())

        imageData = self.__getData(testFile2)
        im = IceImage(imageData)
        self.assertFalse(im.hasTransparency())

    def xtestRemoveTransparency(self):
        imageData = self.__getData(testFile1)
        im = IceImage(imageData)
        self.assertTrue(im.hasTransparency())
        im.removeTransparency()
        self.assertFalse(im.hasTransparency())
        im.resizeImage2()
        im.save(tempJpgFile)

        imageData = self.__getData(tempJpgFile)
        im = IceImage(imageData)
        pxl=im.getPixel((1,1))
        #p=im.getpalette()
        #pxl=p[index]
        self.assertEqual(pxl, (255, 255, 255))

    def testHasTransparency2(self):
        testFormula = "testData/1_a.gif"
        import Image
        from cStringIO import StringIO

        #use image directly
        im = Image.open(testFormula)
        #Make it transparent first before convert to L (grayscale)
        s = StringIO()
        newSize = (212, 45)
        im.save(s, "GIF")

        data = s.getvalue()

        iceImage = IceImage(data, ".gif")
        data = iceImage.bwResizeImage(newSize)
        fs = FileSystem()
        fs.writeFile("testData/iceImage1.gif", data)


if __name__ == "__main__":
    #IceCommon.runUnitTests(locals())
    unittest.main()






