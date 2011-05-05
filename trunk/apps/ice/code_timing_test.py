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

from code_timing import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os


gTime = None

class GTimeTests(TestCase):
    def setUp(self):
        self.gTime = GTime()
    
    def tearDown(self):
        pass
    
    def testStartTimingStopAll(self):
        gTime = self.gTime
        gTime.startTiming()
        gTime.stopAll()
        self.assertNotEqual(gTime.totalTime, 0.0)
        
    
    def testTotalTime(self):
        gTime = self.gTime
        gTime.startTiming()
        self.assertEqual(gTime.totalTime, 0.0)
        time.sleep(.1)
        gTime.stopAll()
        self.assertAlmostEqual(gTime.totalTime, .1, 2)
    
    def testMark(self):
        gTime = self.gTime
        gTime.startTiming()
        gTime.mark("test1")
        time.sleep(0.1)
        gTime.mark("test2")
        gTime.stopAll()
        marks = gTime.marks
        self.assertEqual(len(marks), 3)
        self.assertEqual(marks[0][0], "test1")
        self.assertEqual(marks[1][0], "test2")
        self.assertEqual(marks[2][0], "END")
        self.assertAlmostEqual(marks[0][1], 0, 2)
        self.assertAlmostEqual(marks[1][1], 0.1, 2)
        self.assertAlmostEqual(marks[1][2], 0.1, 2)
        self.assertAlmostEqual(gTime.totalTime, marks[1][1], 2)
    
    def testStartStop(self):
        gTime = self.gTime
        gTime.startTiming()
        gTime.start("section", "subSection")
        gTime.stop("section", "subSection")
        gTime.stopAll()
    
    def testGetSectionNames(self):
        gTime = self.gTime
        gTime.startTiming()
        gTime.start("section1", "subSection")
        gTime.stop("section1", "subSection")
        gTime.start("section2", "subSection")
        gTime.stop("section2", "subSection")
        gTime.stopAll()
        sectionNames = gTime.getSectionNames()
        self.assertEqual(sectionNames, ["section1", "section2"])

    def testGetSectionData(self):
        gTime = self.gTime
        print "----"
        gTime.startTiming()
        gTime.start("section", "subSection")
        time.sleep(0.1)
        gTime.stop("section", "subSection")
        gTime.start("section", "subSection")
        time.sleep(0.1)
        if True:
            gTime.start("section", "subSection")    # Note: nested
            time.sleep(0.1)
            gTime.stop("section", "subSection")     # Note: nested
        gTime.start("section", "subSection2")
        time.sleep(0.1)
        gTime.stop("section", "subSection2")
        gTime.stop("section", "subSection")
        gTime.stopAll()
        timingData = gTime.getSectionData("section")
        print timingData
        gTime.isHtmlPage = True
        print gTime
        
    
    def testgetDisplayLines(self):
        gTime = self.gTime



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
    runTests = ["Add", "testAddGetRemoveImage"]
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and TestCase in i.__bases__]
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            testing = []
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





