#!/usr/local/bin/python
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys
    sys.path.append("../ice")
    from ice_common import IceCommon
from xml_diff import XmlTestCase        # self.assertSameXml
from unittest import TestCase




class XmlTestCaseTests(TestCase):
    # XmlTestCase
    def setUp(self):
        class Test(XmlTestCase):
            def test(self):
                pass
        self.test = Test("test")
    
    def tearDown(self):
        pass
    
    
    def __expectAssertionError(self, actual, excepted, same=True, output=None):
        msg = ""
        try:
            if same:
                if output is None: output=True
                self.test.assertSameXml(actual, excepted, printDiff=output)
            else:
                if output is None: output=False
                self.test.assertNotSameXml(actual, excepted, printDiff=output)
            msg = "expected an assertion error!"
            self.fail(msg)
        except AssertionError, e:
            if msg!="":
                raise e
            msg = str(e)
        return msg
    
    
    def testAssertSameXml(self):
        xmlStr1 = "<root><item a='2' b='1'/></root>"
        xmlStr2 = "<root><item b=\"1\" a='2'></item></root>"
        xmlStr3 = "<root><item a='2' b='11'/></root>"
        t = self.test
        
        # should assert to being the same
        t.assertSameXml("<root/>", "<root></root>")
        t.assertSameXml(xmlStr1, xmlStr2)
        xml = IceCommon.Xml(xmlStr1)
        t.assertSameXml(xml, xmlStr1)
        t.assertSameXml(xml, xmlStr2)
        t.assertSameXml(xmlStr2, xml)
        xml.close()
        
        
        # should raise an AssertionError
        msg = self.__expectAssertionError(None, None)
        expectedMsg = 'Xml not the same!\n\t(not XML data) actual==None and expected==None!'
        self.assertEqual(msg, expectedMsg)
        #print repr(msg)
        
        msg = self.__expectAssertionError("", "")
        expectedMsg = 'Xml not the same!\n\tActual is not well-formed XML! (or is not an xmlString or dom/node)'
        self.assertEqual(msg, expectedMsg)
        #print repr(msg)
        
        msg = self.__expectAssertionError(None, "<root/>")
        expectedMsg = 'Xml not the same!\n\tactual==None and actual!=expected!'
        self.assertEqual(msg, expectedMsg)
        #print repr(msg)
        
        msg = self.__expectAssertionError(xmlStr1, xmlStr3)
        expectedMsg = 'Xml not the same!\n\t  <root>\n\n-   <item a="2" b="1"></item>\n\n+   <item a="2" b="11"></item>\n\n?                  +\n\n  </root>\n\nactual = \'<root>\n  <item a="2" b="1"></item>\n</root>\'\nexpected = \'<root>\n  <item a="2" b="11"></item>\n</root>\''
        self.assertEqual(msg, expectedMsg)
        #print repr(msg)
    
    
    def testAssertNotSameXml(self):
        xmlStr1 = "<root><item a='2' b='1'/></root>"
        xmlStr2 = "<root><item b=\"1\" a='2'></item></root>"
        xmlStr3 = "<root><item a='2' b='11'/></root>"
        t = self.test
        
        t.assertNotSameXml(xmlStr1, xmlStr3)
        
        msg = self.__expectAssertionError(xmlStr1, xmlStr2, same=False)
        self.assertEqual(msg, 'Xml actual is the same as Xml expected!')
    
        msg = self.__expectAssertionError(xmlStr1, xmlStr2, same=False, output=True)
        self.assertEqual(msg, 'Xml actual is the same as Xml expected!')


#normalizeXml(xml, format=True, stripWhiteOnlyText=True)
class XmlNormalizeTests(TestCase):
    def setUp(self):
        self.normalizeXml = XmlDiff().normalizeXml
    
    def tearDown(self):
        pass
    
    def testNormalizeXmlRemoveDeclaration(self):
        xmlStr = "<?xml version='1.0'?>\n<root></root>"
        expected = "<root></root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlFormat(self):
        xmlStr = "<?xml version='1.0'?>\n<root><items><item/><item>One</item></items></root>"
        expected = """<root>
  <items>
    <item></item>
    <item>One</item>
  </items>
</root>"""
        actual =  self.normalizeXml(xmlStr, format=True)
        #print "--- Expcected ---"
        #print expected
        #print
        #print "--- Actual ---"
        #print actual
        #print
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlAttributes(self):
        xmlStr = "  <root ><item  z     =  'x'  a=\"y\"></item></root   >"
        expected = "<root><item a=\"y\" z=\"x\"></item></root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlEmptyElements(self):
        xmlStr = "  <root ><item  /></root   >"
        expected = "<root><item></item></root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlWhiteOnlyText(self):
        xmlStr = "  <root>\t \n<item>  \t\r\n    </item> </root>"
        expected = """<root>
  <item></item>
</root>"""
        actual =  self.normalizeXml(xmlStr, format=True, stripWhiteOnlyText=True)
        self.assertEqual(expected, actual)
        #expected = "<root><item></item></root>"
        #actual =  self.normalizeXml(xmlStr, format=False, stripWhiteOnlyText=True)
        #assert expected==actual
    
    def testNormalizeXmlEntities(self):
        xmlStr = "<root> > &#160; &#xa0; &#xA0; </root>"
        expected = "<root> &gt; \xc2\xa0 \xc2\xa0 \xc2\xa0 </root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlComments(self):
        xmlStr = "<root><!-- this is a comment--></root>"
        expected = "<root></root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlPis(self):
        xmlStr = "<root><?test testing?></root>"
        expected = "<root><?test testing?></root>"
        actual =  self.normalizeXml(xmlStr, format=False)
        self.assertEqual(expected, actual)
    
    def testNormalizeXmlWellFormed(self):
        xmlStr = """<li><a href="/test/test3.htm">Title3</a><ul style="list-style-type: none"><li><a href="/test/test3/test.htm">Test3 Title</a></li></ul></li>"""
        expected = xmlStr
    #    expected = """<li>
    #  <a href="/test/test3.htm">
    #Title3
    #  </a>
    #  <ul style="list-style-type: none">
    #    <li>
    #      <a href="/test/test3/test.htm">
    #Test3 Title
    #      </a>
    #    </li>
    #  </ul>
    #</li>"""
        actual = self.normalizeXml(xmlStr, format=False, stripWhiteOnlyText=True)
        #print "Actual="
        #print actual
        #print
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





