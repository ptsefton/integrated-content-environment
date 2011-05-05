#!/usr/bin/env python
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

#from xml.sax import ContentHandler as SaxContentHandler
import xml.sax

from sys import platform
from time import time
import re

Image = None

if platform=="cli":     # support for IronPython
    from ipImage import Image
    try:
        import clr
        clr.AddReference("System.Xml")
        import System.Xml
        from System.Xml import XmlNodeType
        import System.IO
        _parseString = xml.sax.parseString
        def _wrappedParseString(xmlStr, saxHandler, *args):
            try:
                xmlStr = xmlStr.decode("utf-8")
            except:
                pass
            try:
                _parseString(xmlStr, saxHandler, *args)
            except xml.sax.SAXReaderNotAvailable, e:
            #if True:
                # str(e)=="No parsers found"
                textReader = System.IO.StringReader(xmlStr)
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
                        text = xmlReader.Value
                        saxHandler.characters(text)
                    elif xmlReader.NodeType==XmlNodeType.Whitespace:
                        text = xmlReader.Value
                        saxHandler.characters(text)
                    elif xmlReader.NodeType==XmlNodeType.SignificantWhitespace:
                        text = xmlReader.Value
                        saxHandler.characters(text)
                xmlReader.Close()
                textReader.Close()
        xml.sax.parseString = _wrappedParseString
    except:
        pass

SaxContentHandler = xml.sax.ContentHandler
saxParseString = xml.sax.parseString

class DataCapture(object):
    def __init__(self):
        self.__events = []

    # Events to capture
    def startElement(self, name, attrs):
        self.__events.append(("startElement", name, attrs))

    def endElement(self, name):
        self.__events.append(("endElement", name, None))

    def characters(self, data):
        self.__events.append(("characters", data, None))

    def toString(self):
        parts = []
        for t, n, a in self.__events:
            if t=="startElement":
                parts.append("<%s%s>" % (n, self.__getAttributes(a)))
            elif t=="endElement":
                parts.append("</%s>" % n)
            elif t=="characters":
                parts.append(self.__escapeText(n))
        return "".join(parts)

    def __str__(self):
        return self.toString()

    def __getAttributes(self, attrs):
        s = ""
        if attrs=={}:
            s = ""
        else:
            keys = attrs.keys()
            keys.sort()
            for key in keys:
                aValue = self.__escapeText(attrs[key])
                aValue = aValue.replace('"', "&quot;")
                s += ' %s="%s"' % (key, aValue)
        return s

    def __escapeText(self, t):
        t = t.replace("&", "&amp;")
        return t.replace("<", "&lt;").replace(">", "&gt;")


class ParseWordHtml(object):
    _SampleHtml = """<div class=Section1>
<p class=MsoNormal><span lang=EN-AU>testEmeddedObjects_files/object_1.png<img
width=215 height=205
src="obj_files/image002.gif" alt="5-Point Star: Star"></span></p>
<p class=MsoNormal><span lang=EN-AU>testEmeddedObjects_files/object_3.png<img
width=516 height=239 
src="obj_files/image003.gif" alt="Word Art Test"></span></p>
</div>"""
    
    @staticmethod
    def parseHtml(htmlData):
        # Note: this htmlFile is NOT XHTML
        #  so just use regex to extra the data we want
        images = {}
        paras = re.split("\<p.*?><span.*?>", htmlData)[1:]
        paras = [(i.split("<",1)[0],
                        re.split("\<img\s+", i)[1].split(">",1)[0])
                        for i in paras]
        # process the images
        for name, att in paras:
            rest = att
            atts = {}
            while rest.find("=")!=-1:
                n, rest = rest.split("=", 1)
                n = n.strip()
                if rest.startswith("'"):
                    value, rest = rest[1:].split("'", 1)
                elif rest.startswith('"'):
                    value, rest = rest[1:].split('"', 1)
                else:
                    value, rest = re.split("\s+", rest, 1)
                atts[n] = value
            images[name] = atts
        return images



class TimeIt(object):
    def __init__(self, start=True):
        self.startTime = None
        self.stopTime = None
        if start:
            self.startTime = time()

    def stop(self):
        stopTime = time()

    def mS(self):
        stopTime = self.stopTime
        if stopTime is None:
            stopTime = time()
        elaspedMS = int((stopTime-self.startTime) * 1000)
        return elaspedMS

    def __str__(self):
        return "%smS" % self.mS()



