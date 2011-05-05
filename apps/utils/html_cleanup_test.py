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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys
    sys.path.append("../ice")
    from ice_common import IceCommon

from html_cleanup import HtmlCleanup

from xml_diff import XmlTestCase        # self.assertSameXml
from unittest import TestCase


class HtmlCleanupTests(XmlTestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def xtestSimple(self):
        html = "<html><br><p>Para1<p>Para2<div one two=2/>Test</div></html>"
        #expected = '<html><br/><p>Para1<p>Para2<div one="one" two="2"/>Test</p></p></html>'
        expected = '<html><br/><p>Para1</p><p>Para2</p><div one="one" two="2"/>Test</html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testGeneral(self):
        html = "<html>&#160&#21475;<a   href=?x=<&test=4&x  href=two href=3>link"
        expected = '<html>&#160;&#21475;<a href="?x=&lt;&amp;test=4&amp;x" href="two" href="3">link</a></html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testNesting(self):
        html = "<html><body><p>Testing<b></bad><br></br><br>bold</p>"
        expected = '<html><body><p>Testing<b><br/><br/>bold</b></p></body></html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testEscaping(self):
        html = "<html><test att1='< > & &#160 &nbsp; &amp; &lt; &gt;' att2=&&amp;&lt;<>& &#160&<</test>"
        expected = '<html><test att1="&lt; &gt; &amp; &#160; &#160; &amp; &lt; &gt;" ' + \
                        'att2="&amp;&amp;&lt;&lt;">&amp; &#160;&amp;&lt;</test></html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testEncoding(self):
        html = "<html><one att=one&two att2='one <& \"two'>&<2 two"
        expected = '<html><one att="one&amp;two" att2="one &lt;&amp; &quot;two">&amp;&lt;2 two</one></html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testEmptyElem(self):
        html = "<html><br><?test?><w:test att='one'></w:test><br>"
        expected = '<html><br/><?test?><w:test att="one"/><br/></html>'
        xml = HtmlCleanup.cleanup(html)
        #print xml
        self.assertEqual(xml, expected)
    
    def testBadComment(self):
        html = "<html><head><script type='text/javascript'><!-- PopUp -- Comment --></script></head><body>Nothing</body></html>"
        expected = '<html><head><script type="text/javascript"><!-- PopUp == Comment --></script></head><body>Nothing</body></html>'
        xml = HtmlCleanup.cleanup(html)
        self.assertEqual(xml, expected)
    
    def xtestFile(self):
        file = "testData/test1.htm"
        f = open(file, "rb")
        html = f.read()
        f.close()
        xml = HtmlCleanup.cleanup(html)
        f = open("testData/test1Output.htm", "wb")
        f.write(xml)
        f.close()

    def testScriptElement(self):
        html = """<html><head><script type='text/javascript'>//<![CDATA[
        if (1<2) alert('two&');<!-- PopUp -- Comment -->
        //]]>
        </script></head><body>Nothing</body></html>"""
        expected = '<html><head><script type="text/javascript"><!-- PopUp == Comment --></script></head><body>Nothing</body></html>'
        xml = HtmlCleanup.cleanup(html)
        #self.assertEqual(xml, expected)

    def testX(self):
        html = """<div><p id="h2de112c0p1">Para.</p><blockquote class="bq"><p id="h65bbb66fp1">Blockquote (bq1):
<ul class="lib"><li><p id="hdd5ea3fp1">li2b</p><p id="h17f52eddp1">li2p</p></li><li><p id="hdd5ea3fp2">li2b</p><p id="h17f52eddp2">li2p</p><p id="h1c35d593p1"/></li></ul></p>
</blockquote></div>"""
        expected = """<div><p id="h2de112c0p1">Para.</p><blockquote class="bq"><p id="h65bbb66fp1">Blockquote (bq1):
<ul class="lib"><li><p id="hdd5ea3fp1">li2b</p><p id="h17f52eddp1">li2p</p></li><li><p id="hdd5ea3fp2">li2b</p><p id="h17f52eddp2">li2p</p><p id="h1c35d593p1"/></li></ul></p>
</blockquote></div>"""
        xml = HtmlCleanup.cleanup(html)
        self.assertEqual(xml, expected)
        
        
#        self.assertEqual(xml, expected)




if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





