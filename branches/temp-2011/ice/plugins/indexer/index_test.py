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

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os

import sys
sys.path.append("../ice-utils")
sys.path.append("../utils")
from file_system import FileSystem
from system import system
fs = FileSystem()
from cStringIO import StringIO

from index import *

# inject xml_util
import index
import xml_util
index.Xml = xml_util.xml


testDataPath = "testData"
testIndexPath = "tempIndex"

class testIndex(TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        #sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testInit(self):
        index = Index(fs, testIndexPath)
        self.assertTrue(fs.exists(testIndexPath))
    
    def testIndexContent(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId")
        
        searchResults = index.searchContents("content")
        self.assertEqual(len(searchResults), 1)
        searchResults.close()
        searchResults = index.searchContents("notInContent")
        self.assertEqual(len(searchResults), 0)
        searchResults.close()
        
        index = Index(fs, testIndexPath)
        index.indexContent(content, id="testId2")
        searchResults = index.searchContents("content")
        expected = ["testId", "testId2"]
        ids = searchResults.keys()
        ids.sort()
        expected.sort()
        self.assertEqual(ids, expected)
        searchResults.close()
    
    def testIndexContent2(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = ""
        meta = {"one":"oNe", "tags":["one", "tWo", "teST", "this"], "path":"/one/TWo/three"}
        index.indexContent(content, id="testId", metaItems=meta, comments="Comments One")
        
        meta = {"one":"ONE", "tags":["one", "twO", "Test", "this"], "path":"/one/TWo/four"}
        index.indexContent(content, id="testId2", metaItems=meta, comments="Comments Two")
        
        # NOTE: there are NO wild cards in keywordQueries and are case-sensitive (not the storing analyzer
        #           may have already lowerCased the content
        #   also pathQueryStr is case-sensitive and may only contain a optional trailing '*'
        searchResults = index.search(queryStr="tags:tEst ", keywordQueryStr=None, pathQueryStr=None)
        for id, doc in searchResults.iteritems():
            #print "'%s', '%s', '%s'" % (doc.get("comments"), doc.get("one"), doc.get("list"))
            pass
        self.assertEqual(len(searchResults), 2)
        searchResults.close()
        
        searchResults = index.search(queryStr=None, keywordQueryStr=None, pathQueryStr="/one/TWo/*")
        for id, doc in searchResults.iteritems():
            #print "'%s', '%s', '%s'" % (doc.get("comments"), doc.get("one"), doc.get("list"))
            pass
        self.assertEqual(len(searchResults), 2)
        searchResults.close()        
    
    
    def testIndexContent3(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = ""
        meta = {"ids":["1234"], "1234":["tag1 tag2", "tag3"]}
        index.indexContent(content, id="one", metaItems=meta)
        
        searchResults = index.search("ids:1234")
        #print "found %s" % len(searchResults)
        for doc in searchResults.itervalues():
            #print doc.get("1234")
            #print "x='%s'" % doc.get("x")
            #print dir(doc)
            for field in doc.getFields():
                #print field.name(), field.stringValue()
                pass
        searchResults.close()
        
    
    def xtestTest(self):
        index = Index(fs, testIndexPath)
        index.create()
        
        index.test(self)
    
    
    def testSearchContent(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test one content."
        index.indexContent(content, id="testId1", title="OneTitle")
        content = "This is just some test two content."
        index.indexContent(content, id="testId2", title="Two Title")
        
        searchResults = index.searchContents("content")
        self.assertEqual(len(searchResults), 2)
        self.assertEqual(searchResults["testId1"].get("id"), "testId1")
        self.assertEqual(searchResults["testId1"].get("title"), "OneTitle")
            
        searchResults.close()
        searchResults = index.searchContents("notInContent")
        self.assertEqual(len(searchResults), 0)
        searchResults.close()
        
   

    def testSearchId(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId")
        
        searchResults = index.searchId("testId")
        self.assertTrue(searchResults is not None)
        self.assertEqual(searchResults.value.get("id"), "testId")
        searchResults.close()
        #print doc
    
    def testReIndexContent(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId")
        
        searchResults = index.searchContents("content")
        self.assertEqual(searchResults.keys(), ["testId"])
        searchResults.close()
        searchResults = index.searchContents("notInContent")
        self.assertEqual(searchResults.keys(), [])
        searchResults.close()
        
        index = Index(fs, testIndexPath)
        index.indexContent(content, id="testId")
        searchResults = index.searchContents("content")
        expected = ["testId"]
        ids = searchResults.keys()
        ids.sort()
        expected.sort()
        self.assertEqual(ids, expected)
        searchResults.close()
   
    def testKeywords(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId", other="one two")
        
        searchResults = index.searchContents("other:one")
        self.assertEqual(searchResults.keys(), ["testId"])
        searchResults.close()

        searchResults = index.searchContents("other:two")
        self.assertEqual(searchResults.keys(), ["testId"])
        searchResults.close()
    
    
    def testSearchMeta(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId", metaItems={"meta":"one"})
        
        searchResults = index.searchMeta("meta", "one")
        #print searchResults
        self.assertTrue(searchResults is not None)
        self.assertTrue(searchResults["testId"].get("id"), "testId")
        searchResults.close()
        #self.assertEqual(doc.value.get("meta"), "one")
        #self.assertEqual(hits.length(), 1)
    
    def testIndexingHtml(self):
        path = testDataPath + "/test2.html"
        absPath = fs.absolutePath(path)
        
        if not fs.exists(absPath):
            fs.writeFile(path, "<html><head></head><body>Testing on html File</body></html>")
        
        index = Index(fs, testIndexPath)
        index.create()
        id = fs.splitExt(fs.split(path)[1])[0]
        contents = unicode(fs.readFile(path), 'iso-8859-1') 
        #index.index Xml Content(contents, id)      ## no indexing of xml
        
        searchResults = index.searchContents("Testing")
        self.assertEqual(searchResults.keys(), ["test2"])   
        searchResults.close()
        searchResults = index.searchContents("notInContent")
        self.assertEqual(searchResults.keys(), [])       
        searchResults.close()
        
        searchResults = index.searchContents("body")
        self.assertEqual(searchResults.keys(), [])       
        searchResults.close()
    

    def testDelete(self):
        index = Index(fs, testIndexPath)
        index.create()
        content = "This is just some test content."
        index.indexContent(content, id="testId")
        
        searchResults = index.searchId("testId")
        self.assertTrue(searchResults is not None)
        searchResults.close()
        index.deleteIndex("testId")
        searchResults = index.searchId("testId")
        self.assertEqual(searchResults.keys(), [])
        searchResults.close()
        searchResults = index.searchContents("content")
        self.assertEqual(searchResults.keys(), [])
        searchResults.close()
    
    
    def testQueryTokenizer(self):
        #queryStr = " \t\n123 one two+three-four4!five^*?\n\t"
        #qt = QueryTokenizer(queryStr)
        #print qt.tokens
        
        #queryStr = "\"123 one\" (two+\"three)\"-(four4))!five"
        #qt = QueryTokenizer(queryStr)
        #print qt.tokens
        
        queryStr = "+tags:(one two) three (tags:four)"
        print queryStr
        qt = QueryTokenizer(queryStr)
        print qt.tokens
        tags = qt.extractTag("tags")
        print "%s - %s" % (tags, qt.tokens)


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





