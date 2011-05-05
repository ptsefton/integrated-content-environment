#!/usr/bin/python
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

from mockSimpleClient import *

import sys
from file_system import FileSystem
from system import system


class MockSimpleClientTests(TestCase):
    def setUp(self):
        pass
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()        
    
    def tearDown(self):
        pass
        #sys.stdout = self.stdout
    
    def testInitCreate(self):
        path = "."
        MockSimpleClient(path=None, fs=FileSystem("tempTest"), create=True)

    
    def testInit(self):
        fs = FileSystem("tempTest")
        path = "."
        sClient = MockSimpleClient(path=None, fs=fs, create=True)
        print "rev#", sClient.rootRevisionNumber
        fs.writeFile("one.txt", "testing one")
        sClient.addFile("one.txt")
        print sClient.list()
        sClient.commit(paths=["one.txt"], logMessage="Commit Test")
        print sClient.list()
        fs.writeFile("one.txt", "testing one modified")
        print sClient.list()
        
        print "---"
        sClient = MockSimpleClient(path=None, fs=fs)
        print sClient.list()
        sClient.commit(paths=["one.txt"], logMessage="2nd commit")
        print sClient.list()
        print sClient.logFile("one.txt")
        fs.writeFile("one.txt", "testing one modified2")
        print sClient.list()
        sClient.revertFile("one.txt")
        print sClient.list()


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






