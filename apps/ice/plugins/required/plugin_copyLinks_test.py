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

from plugin_copyLinks import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
from xml_diff import XmlTestCase    # assertSameXml(self, actual, expected, msg=None, printDiff=True)
                                    # assertNotSameXml(self, actual, expected, msg=None, printDiff=False)
                                    #

class mockRep(object):
    class MockProp(object):
        def __init__(self, file, write):
            self.__file = file
            self.__writeMethod = write
        def touch(self):
            self.__writeMethod("rep.prop.touch(%s)\n" % self.__file)
        def isHtmlItem(self):
            return True
    def __init__(self, output=None):
        self.content = None
        self.output = output
        self.__fs = fs
    def walker(self, startPath, exts):
        files = ["/package/to/one.odt"]
        return files
    def getAbsPath(self, file):
        value = IceCommon.url_join("/repRoot", file)
        self.__write("rep.getAbsPath(%s) - %s\n" % (file, value))
        return value
    def unzipToTempDir(self, file):
        tempDir = self.__fs.makeDirectory()
        name = str(tempDir)
        name = self.__fs.join(name, "content.xml")
        fs.writeFile(name, testXmlOne)
        return tempDir
    def zipFromTempDir(self, file, tempDir):
        name = str(tempDir)
        name = self.__fs.join(name, "content.xml")
        self.content = self.__fs.readFile(name)
    def getProperty(self, file):
        return self.MockProp(file, self.write)
    def __write(self, msg):
        if self.output is not None:
            self.output.write(msg)

rep = mockRep()


testXmlOne = """<test xmlns:xlink='http://www.w3.org/1999/xlink'>
<a xlink:href='http://other.com/package/from/one.htm'/>
<a xlink:href='http://localhost:8000/package/from/two.htm'/>
<div>
  <a xlink:href='http://other.com/package/from/three'/>
  <a xlink:href='http://localhost:8000/package/from/four'/>
  <a xlink:href='http://localhost:8000/package/from/five'/>
  <a xlink:href='http://localhost:8000/package/from/six'/>
  <a xlink:href='http://localhost:8000/package/other/seven'/>
</div></test>"""

testXmlOneExpected = """<?xml version="1.0"?>
<test xmlns:xlink="http://www.w3.org/1999/xlink">
<a xlink:href="http://other.com/package/from/one.htm"/>
<a xlink:href="http://localhost:8000/package/to/two.htm"/>
<div>
  <a xlink:href="http://other.com/package/from/three"/>
  <a xlink:href="http://localhost:8000/package/to/four"/>
  <a xlink:href="http://localhost:8000/package/to/five"/>
  <a xlink:href="http://localhost:8000/package/to/six"/>
  <a xlink:href="http://localhost:8000/package/other/seven"/>
</div></test>
"""


class CopyLinksTests(XmlTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFixupLinks(self):
        expectedList = ['http://other.com/package/from/one.htm', 'http://localhost:8000/package/to/two.htm', 'http://other.com/package/from/three', 'http://localhost:8000/package/to/four', 'http://localhost:8000/package/to/five', 'http://localhost:8000/package/to/six', 'http://localhost:8000/package/other/seven']
        cl = copyLinks(rep, localBaseUrl = "http://localhost:")

        copyFrom = "/package/from/"
        copyTo = "/package/to/"
        dom = IceCommon.Xml(testXmlOne, [("xlink", "http://www.w3.org/1999/xlink")])
        cl._testFixupLinks(dom, copyFrom, copyTo)
        refNodes = dom.getNodes("//*[@xlink:href]")
        resultList = []
        for node in refNodes:
            url = node.getAttribute("href")
            resultList.append(url)
        self.assertEqual(resultList, expectedList)
        dom.close()

        # Test with
        copyFrom = "package/from/"
        copyTo = "/package/to"
        dom = IceCommon.Xml(testXmlOne, [("xlink", "http://www.w3.org/1999/xlink")])
        cl._testFixupLinks(dom, copyFrom, copyTo)
        refNodes = dom.getNodes("//*[@xlink:href]")
        resultList = []
        for node in refNodes:
            url = node.getAttribute("href")
            resultList.append(url)
        self.assertEqual(resultList, expectedList)
        dom.close()

        copyFrom = "package/from/"
        copyTo = "/package/to/here/"
        expectedList = ['http://other.com/package/from/one.htm', 'http://localhost:8000/package/to/here/two.htm', 'http://other.com/package/from/three', 'http://localhost:8000/package/to/here/four', 'http://localhost:8000/package/to/here/five', 'http://localhost:8000/package/to/here/six', 'http://localhost:8000/package/other/seven']
        dom = IceCommon.Xml(testXmlOne, [("xlink", "http://www.w3.org/1999/xlink")])
        cl._testFixupLinks(dom, copyFrom, copyTo)
        refNodes = dom.getNodes("//*[@xlink:href]")
        resultList = []
        for node in refNodes:
            url = node.getAttribute("href")
            resultList.append(url)
        self.assertEqual(resultList, expectedList)
        dom.close()

    def testConvert(self):
        copyFrom = "package/from/"
        copyTo = "/package/to"
        cl = copyLinks(rep, localBaseUrl = "http://localhost:")
        cl.convert(copyFrom, copyTo)
        content = rep.content
        self.assertEqual(content, testXmlOneExpected)



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




