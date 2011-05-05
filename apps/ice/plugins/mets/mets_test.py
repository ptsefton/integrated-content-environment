#!/usr/bn/env python
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

import sys, os
sys.path.append("../utils")
from file_system import *
from system import *
from time import gmtime, strftime

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader

try:
    from xml.etree import ElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

from mets import *

class MetsTests(TestCase):
    def __init__(self, name):
        TestCase.__init__(self, name)
    
    def setUp(self):
        self.mets = Mets(iceContext, "METS_TEST", METS_NLA_PROFILE)
        self.mets.setCreateDate("2007-12-12T10:30:50")
        self.mets.setLastModDate("2007-12-12T11:30:50")
        self.mets.addDisseminator(MetsAgent.TYPE_INDIVIDUAL, "ICE User")
        self.mets.addCreator("ICE 2.0")
        self.mods = ElementTree.Element("{%s}mods" % MODS_NS)
        pass
    
    def tearDown(self):
        pass
    
    def testGetXmlInOrder(self):
        dmdSec1 = self.mets.addDmdSecWrap("dmdSec1", "MODS", self.mods)
        dmdSec2 = self.mets.addDmdSecRef("dmdSec2", "URL", "MODS", "mods.xml")
        
        fileGrp = self.mets.addFileGrp("Original")
        file1 = self.mets.addFile(fileGrp, "test1.odt", "test1.odt", "dmdSec1", "")
        file2 = self.mets.addFile(fileGrp, "conflict.gif", "testing/conflict.gif", "dmdSec1", "")
        
        div1 = self.mets.addDiv("section", "dmdSec1")
        div2 = self.mets.addDiv("article", "dmdSec1", div1)
        
        self.mets.addFptr(div1, file1.id)
        self.mets.addFptr(div2, file2.id)
        
        xml = self.mets.getXml()
        f = open("mets.xml")
        data = f.read()
        f.close()
        
        self.assertEqual(data, xml)
    
    def testGetXmlOutOfOrder(self):
        #structMap
        div1 = self.mets.addDiv("section", "dmdSec1")
        div2 = self.mets.addDiv("article", "dmdSec1", div1)
        
        #dmdSec
        dmdSec1 = self.mets.addDmdSecWrap("dmdSec1", "MODS", self.mods)
        dmdSec2 = self.mets.addDmdSecRef("dmdSec2", "URL", "MODS", "mods.xml")
        
        #fileSec
        fileGrp = self.mets.addFileGrp("Original")
        file1 = self.mets.addFile(fileGrp, "test1.odt", "test1.odt", "dmdSec1", "")
        file2 = self.mets.addFile(fileGrp, "conflict.gif", "testing/conflict.gif", "dmdSec1", "")
        
        #structMap
        self.mets.addFptr(div1, file1.id)
        self.mets.addFptr(div2, file2.id)
        
        xml = self.mets.getXml()
        f = open("mets.xml")
        data = f.read()
        f.close()
        
        self.assertEqual(data, xml)
    
    def testGetXmlInline(self):
        dmdSec1 = self.mets.addDmdSecWrap("dmdSec1", "MODS", self.mods)
        dmdSec2 = self.mets.addDmdSecRef("dmdSec2", "URL", "MODS", "mods.xml")
        
        fileGrp = self.mets.addFileGrp("Original")
        file1 = self.mets.addFile(fileGrp, "test1.odt", "test1.odt", "dmdSec1",)
        file2 = self.mets.addFile(fileGrp, "conflict.gif", "testing/conflict.gif",
                                  "dmdSec1", wrapped = True)
        
        div1 = self.mets.addDiv("section", "dmdSec1")
        div2 = self.mets.addDiv("article", "dmdSec1", div1)
        
        self.mets.addFptr(div1, file1.id)
        self.mets.addFptr(div2, file2.id)
        
        xml = self.mets.getXml()
        f = open("mets_inline.xml")
        data = f.read()
        f.close()
        
        self.assertEqual(data, xml)
    
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





