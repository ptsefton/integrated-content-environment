#!/usr/bin/env ip
#
#    Copyright (C) 2010  Distance and e-Learning Centre,
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

import xml.sax
import sys
if sys.platform=="cli":
    try:
        import clr
        clr.AddReference("System.Xml")
        import System.Xml
        from System.Xml import XmlNodeType
        import System.IO
        _parseString = xml.sax.parseString
        def _wrappedParseString(str, saxHandler, *args):
            try:
                _parseString(str, saxHandler, *args)
            except xml.sax.SAXReaderNotAvailable, e:
                # str(e)=="No parsers found"
                textReader = System.IO.StringReader(str)
                xmlReader = System.Xml.XmlTextReader(textReader)
                while xmlReader.Read():
                    if xmlReader.NodeType==XmlNodeType.Element:
                        name = xmlReader.Name
                        isEmptyElement = xmlReader.IsEmptyElement
                        attrs = {}
                        while xmlReader.MoveToNextAttribute():
                            attrs[xmlReader.Name] = xmlReader.Value
                        saxHandler.startElement(name, attrs)
                        if isEmptyElement:
                            saxHandler.endElement(name)
                    elif xmlReader.NodeType==XmlNodeType.EndElement:
                        saxHandler.endElement(xmlReader.Name)
                    elif xmlReader.NodeType==XmlNodeType.Text:
                        saxHandler.characters(xmlReader.Value)
                    elif xmlReader.NodeType==XmlNodeType.Whitespace:
                        #print "*white* %s" % repr(xmlReader.Value)
                        saxHandler.characters(xmlReader.Value)
                xmlReader.Close()
                textReader.Close()
        xml.sax.parseString = _wrappedParseString
    except:
        pass

class TestSAX(object, xml.sax.ContentHandler):
    def __init__(self, xmlStr):
        xml.sax.ContentHandler.__init__(self)
        try:
            xml.sax.parseString(xmlStr, self)
        except xml.sax.SAXReaderNotAvailable, e:
            print str(e)
            if False:
                textReader = System.IO.StringReader(xmlStr)
                xmlReader = System.Xml.XmlTextReader(textReader)
                saxHandler = self
                while xmlReader.Read():
                    if xmlReader.NodeType==XmlNodeType.Element:
                        name = xmlReader.Name
                        attrs = {}
                        while xmlReader.MoveToNextAttribute():
                            attrs[xmlReader.Name] = xmlReader.Value
                        saxHandler.startElement(name, attrs)
                    elif xmlReader.NodeType==XmlNodeType.EndElement:
                        saxHandler.endElement(xmlReader.Name)
                    elif xmlReader.NodeType==XmlNodeType.Text:
                        saxHandler.characters(xmlReader.Value)
                    elif xmlReader.NodeType==XmlNodeType.Whitespace:
                        saxHandler.characters(xmlReader.Value)

    # Sax event handlers
    def startElement(self, name, attrs):
        print "startElement name='%s', attrs='%s'" % (name, attrs)

    def endElement(self, name):
        print "endElement name='%s'" % name

    def characters(self, data):
        print "  characters data='%s'" % data


def test():
    print "--Testing SAX--"
    xml = """<root xmlns:x="Xxxx">
    <items>
     <item a="one" n="1">One</item>
     <item a="two" n="2">Two</item>
    </items>
    <x:test>testing &amp; &gt; &#160;.</x:test>
    <empty e='e'/>
</root>"""
    test = TestSAX(xml)



if __name__=="__main__":
    test()
