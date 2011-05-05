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

from ooo_automate import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os, time, sys
from cStringIO import StringIO
sys.path.append("../utils")
sys.path.append("../../../utils")
from file_system import *
from system import *


ooPort=2002
ooHost="localhost"

testData = "bookTestData/"
baseBookfile = testData + "default.odt"
baseBookfile1 = testData + "Studybook.odt"
m1file = testData + "one.odt"
m2file = testData + "two.odt"
m3file = testData + "three.odt"
tempOutput = testData + "tempBookOut.odt"
tempOutput2 = testData + "tempBookOut2.odt"

fs = FileSystem(".")

class OoObjectTests(TestCase):
    def setUp(self):
        pass
#        self.stdout = sys.stdout
#        sys.stdout = StringIO()
    
    def tearDown(self):
        pass
#        sys.stdout = self.stdout
    
    def xtestInsertDocument(self):
        o = OoObject(ooPort=ooPort, ooHost=ooHost)
        #baseBookfile = testData + "ManuallyCreatedTemplate.odt"
        baseBookDocument = fs.absPath(baseBookfile1)
        
        o.loadDocument(baseBookDocument)
        o.gotoEnd()
        o.insertDocument(m1file)
        o.saveDocument(fs.absPath(tempOutput), toExt=".odt")
    
    
    def testBuildBook(self):
        #This test if for buildBook2
        o = OoObject(ooPort=ooPort, ooHost=ooHost)
        baseBookDocument = fs.absPath(baseBookfile1)
        doc1 = (fs.absPath(m1file), fs.absPath(m1file), "", {"InsertPageBreak":True, "Page": "Odd"})
        doc2 = (fs.absPath(m2file), fs.absPath(m2file), "", {"InsertPageBreak":True, "Page": "Odd"})
        doc3 = (fs.absPath(m3file), fs.absPath(m3file), "", {"InsertPageBreak":True, "Page": "Odd"})
        
        try:
            #urlBookmarks = o.buildBook2(baseBookDocument, bookDocumentsPathUrl=[doc1, doc2, doc3])
            #odtResult = o.saveDocument(fs.absPath(tempOutput), toExt=".odt")
            pass
        finally:
            o.close()
    
    def xtestBuildBook(self):
        o = OoObject(ooPort=ooPort, ooHost=ooHost)
        #baseBookDocument = os.path.abspath(baseBookfile)
        baseBookDocument = fs.absPath(baseBookfile)
        #doc1 = (os.path.abspath(m1file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc1 = (fs.absPath(m1file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc2 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc2 = (fs.absPath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc3 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc3 = (fs.absPath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc4 = (os.path.abspath(m1file), "", {"InsertPageBreak":False})
        doc4 = (fs.absPath(m1file), "", {"InsertPageBreak":False})
        try:
            urlBookmarks = o.buildBook(baseBookDocument, bookDocumentsPathUrl=[doc1, doc2, doc3, doc4])
            #odtResult = o.saveDocument(os.path.abspath(tempOutput), toExt=".odt")
            odtResult = o.saveDocument(fs.absPath(tempOutput), toExt=".odt")
        finally:
            o.close()
        
        try:
            urlBookmarks = o.buildBook(tempOutput, bookDocumentsPathUrl=[doc1, doc2, doc3, doc4])
            #odtResult = o.saveDocument(os.path.abspath(tempOutput2), toExt=".odt")
            odtResult = o.saveDocument(fs.absPath(tempOutput2), toExt=".odt")
        finally:
            o.close()
    
    def xtestBuildBookWithTestTemplate(self):
        testData = "bookTestData/"
        baseBookfile = testData + "template_testing_Default.odt"
        ch1file = testData + "chp1_with_headers.odt"
        ch2file = testData + "chp2_with_header.doc"
        ch3file = testData + "chp3_with_header.doc"
        tempOutput = testData + "tempBookOut.odt"
        tempOutput2 = testData + "tempBookOut2.odt"
        o = OoObject(ooPort=ooPort, ooHost=ooHost)
        #baseBookDocument = os.path.abspath(baseBookfile)
        baseBookDocument = fs.absPath(baseBookfile)
        #doc1 = (os.path.abspath(m1file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc1 = (fs.absPath(ch1file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc2 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc2 = (fs.absPath(ch2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc3 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc3 = (fs.absPath(ch3file), "", {"InsertPageBreak":True, "Page":"Odd"})
        #doc4 = (os.path.abspath(m1file), "", {"InsertPageBreak":False})
        doc4 = (fs.absPath(ch2file), "", {"InsertPageBreak":False})
        try:
            urlBookmarks = o.buildBook(baseBookDocument, bookDocumentsPathUrl=[doc1, doc2, doc3, doc4])
            #odtResult = o.saveDocument(os.path.abspath(tempOutput), toExt=".odt")
            odtResult = o.saveDocument(fs.absPath(tempOutput), toExt=".odt")
        finally:
            o.close()
        
        try:
            urlBookmarks = o.buildBook(tempOutput, bookDocumentsPathUrl=[doc1, doc2, doc3, doc4])
            #odtResult = o.saveDocument(os.path.abspath(tempOutput2), toExt=".odt")
            odtResult = o.saveDocument(fs.absPath(tempOutput2), toExt=".odt")
        finally:
            o.close()


if __name__ == "__main__":
    system.cls()
    print "---- Testing ----"
    print
    unittest.main()





