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
try:
    from xml.etree.ElementTree import ElementTree, XML, tostring
except ImportError:
    try:
        import ElementTree
    except ImportError:
        from elementtree import ElementTree
    ElementTree, XML, tostring = ElementTree.ElementTree, ElementTree.XML, ElementTree.tostring


import sys, os
sys.path.append("../../utils")
sys.path.append(".")
dir = os.getcwd()
os.chdir("../../ice")
from ice_common import IceCommon
IceCommon.setup()
os.chdir(dir)

from html_cleanup import HtmlCleanup              # convertHtmlToXml


from htmlToOdt import HtmlToOdt
HtmlToOdt.HtmlParser = HtmlCleanup

testDataPath = "testData/"


class HtmlToOdtTests(IceCommon.XmlTestCase):
    def setUp(self):
        self.__fs = IceCommon.FileSystem(".")
        self.htmlToOdt = HtmlToOdt(self.__fs)
        
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()        
    
    def tearDown(self):
        pass
        #sys.stdout = self.stdout
    
    def testInit(self):
        htmlToOdt = HtmlToOdt(self.__fs)
    
    def xtestConvertSimple1Test(self):
        #TODO - fix this test but it's not really a unit test
        #too much going on
        htmlFile = testDataPath + "simple1.html"
        outputFile = testDataPath + "simple1_output.odt"
        exceptedFile = testDataPath + "simple1.odt"
        
        self.htmlToOdt.convert(htmlFile, outputFile)
        
        resultContent = self.__fs.readFromZipFile(outputFile, "content.xml")
        #self.__fs.writeFile(testDataPath + "simple1ExceptedContent.xml", resultContent)
        expectedContent = self.__fs.readFile(testDataPath + "simple1ExceptedContent.xml")
        self.assertSameXml(resultContent, expectedContent, "content does not match expectedContent!")
        #self.__compareFiles(outputFile, exceptedFile, 
        #    "outputFile is not the same as the excepted file!")

    
    def testIgnoreDivs(self):
        testString = "<div><div><p>p</p></div></div>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """
        <x>
             <ns0:p xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0" ns0:style-name="p">p</ns0:p>
        </x>
        """
        outputEt = ElementTree(XML("<x/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        self.assertSameXml(tostring(outputEt),outputString)

   
    def testP(self):
        testString = "<p>p</p>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:p ns0:style-name="p" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0">p</ns0:p></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertEqual(tostring(outputEt),outputString)
    
    def testSimpleUl(self):
        testString = "<ul><li>1</li><li>2</li></ul>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">1</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">2</ns0:p></ns0:list-item></ns0:list></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertEqual(tostring(outputEt),outputString)
    
    def testSimpleUlWithDivs(self):
        testString = "<ul><li><div>1</div></li><li><div>2</div></li></ul>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">1</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">2</ns0:p></ns0:list-item></ns0:list></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertSameXml(tostring(outputEt),outputString)

    def testSimpleUlWithA(self):
        testString = "<ul><li><a href='x'>1</a></li></ul>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">1</ns0:p></ns0:list-item></ns0:list></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertSameXml(tostring(outputEt),outputString)

    def testSimpleOl(self):
        testString = "<ol><li>1</li><li>2</li></ol>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:list ns0:style-name="li1n" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1n">1</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li1n" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1n">2</ns0:p></ns0:list-item></ns0:list></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertSameXml(tostring(outputEt),outputString)


    def testNestedUl(self):
        testString = "<ul><li>1<ul><li>x</li><li>y</li></ul></li><li>2</li></ul>"
        testEt = ElementTree(XML(testString)).getroot()
        outputString = """<y><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">1</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li2b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li2b">x</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li2b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li2b">y</ns0:p></ns0:list-item></ns0:list><ns0:list ns0:style-name="li1b" xmlns:ns0="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><ns0:list-item><ns0:p ns0:style-name="li1b">2</ns0:p></ns0:list-item></ns0:list></y>"""
        outputEt = ElementTree(XML("<y/>")).getroot()
        self.htmlToOdt._parseElement(testEt,outputEt)
        #print tostring(outputEt)
        self.assertSameXml(tostring(outputEt),outputString)


    def __compareFiles(self, outputFile, exceptedFile, msg=None):
        # compare content.xml and styles.xml
        resultContent = self.__fs.readFromZipFile(outputFile, "content.xml")
        exceptedContent = self.__fs.readFromZipFile(exceptedFile, "content.xml")
        self.assertSameXml(resultContent, exceptedContent, msg, printDiff=False)



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())







