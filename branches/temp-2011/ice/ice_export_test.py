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

from ice_export import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os
from cStringIO import StringIO
from file_system import *
from system import *


testFixupObjUrl1 = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="800" height="624" ID="Captivate1">
  <param name="movie" value="lookupphone_skin.swf">
  <param name="quality" value="high">
  <param name="loop" value="0">
  <embed src="lookupphone_skin.swf" width="800" height="624" loop="0" quality="high" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash" menu="false"></embed>
</object>"""
testFixupObjUrl2 = """<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="800" height="624" ID="Captivate1">
  <param name="movie" value="one/two/lookupphone_skin.wmv?test">
  <param name="quality" value="high">
  <param name="loop" value="0">
  <embed src="one/two/lookupphone_skin.wmv?test" width="800" height="624" loop="0" quality="high" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash" menu="false"></embed>
</object>"""
testFixupObjUrl3 = """ """


class FixupObjectUrlsTests(TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testOne(self):
        iio = iceIO(rep=None)
        htmlStr = testFixupObjUrl1
        fixObjUrls = FixupObjectUrls(iio)
        fixObjUrls.setToPath(toPath="/")
        result = fixObjUrls.htmlFixup(htmlStrData=htmlStr, toPath="/")
        #fixObjUrls.finished()  # now copy all referenced media files and fixup the manifest
        self.assertEqual(htmlStr, result)
        
    def testTwo(self):
        iio = iceIO(rep=None)
        htmlStr = testFixupObjUrl2
        fixObjUrls = FixupObjectUrls(iio)
        fixObjUrls.setToPath(toPath="/root")
        result = fixObjUrls.htmlFixup(htmlStrData=htmlStr, toPath="/root/one/")
        #fixObjUrls.finished()  # now copy all referenced media files and fixup the manifest
        #self.assertEqual(htmlStr, result)
        #print result       
        



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





