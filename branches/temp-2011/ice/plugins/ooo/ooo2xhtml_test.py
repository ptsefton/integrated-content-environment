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

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os

import sys
sys.path.append("../../utils")
from file_system import FileSystem
from system import system
import file_system

from ooo2xhtml import *

testOdtData = "testData2/chen.odt"


class ooo2xhtmlTests(TestCase):
    def setUp(self):
        self.__fs = FileSystem(".")
    
    def tearDown(self):
        pass
    
    def testName(self):
        o2xhtml = Ooo2xhtml(iceContext)
        if self.__fs.isFile(testOdtData)==False:
            msg = "testData '%s' not found!" % testOdtData
            print msg
            print self.__fs.absolutePath(testOdtData)
            self.assertFail(msg)
            return
        contentXmlStr = self.__fs.readFromZipFile(testOdtData, "content.xml")
        o2xhtml.process(contentXmlStr)
        html = str(o2xhtml.shtml)
        print len(html)
        for k, i in o2xhtml.meta.iteritems():
            print "%s - '%s'" % (k, str(i))
            print



if __name__ == "__main__":
    system.cls()
    print "---- Testing ----"
    print
    
    # Run only the selected tests
    #  Test Attribute testXxxx.slowTest = True
    #  fastOnly (do not run any slow tests)
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and \
                            (TestCase in i.__bases__ or XmlTestCase in i.__bases__)]
        testing = []
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            for i in l:
                if i.lower() not in runTests:
                    #print "Removing '%s'" % i
                    delattr(x, i)
                else:
                    #print "Testing '%s'" % i
                    testing.append(i)
        x = None
        print "Running %s selected tests - %s" % (len(testing), str(testing)[1:-1])
    
    unittest.main()





