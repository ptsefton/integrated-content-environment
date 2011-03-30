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

from oxml2xhtml_utils import SaxContentHandler, saxParseString


class WordNumbering(object, SaxContentHandler):
    # word/numbering.xml
    def __init__(self, xmlStr):
        SaxContentHandler.__init__(self)
        self._nums = {}                 # Maps numId to abstractNumId
        self._abstractNumbers = {}      # abstractNumId: ?
        self.__num = None
        self.__abstractNumber = None
        self.__level = None
        if xmlStr is not None:
            saxParseString(xmlStr, self)

    def getNumLevelInfo(self, numId, level):
        anum = self._nums.get(numId, "")
        return self._abstractNumbers.get(anum, {}).get(level, {})

    # Sax event handlers
    def startElement(self, name, _attrs):
        attrs = _attrs
        if name=="w:num":
            self.__num = attrs.get("w:numId")
        elif name=="w:abstractNumId":
            val = attrs.get("w:val")
            self._nums[self.__num] = val
        elif name=="w:abstractNum":
            val = attrs.get("w:abstractNumId")
            self.__abstractNumber = {}
            self._abstractNumbers[val] = self.__abstractNumber
        elif name=="w:lvl":
            ilevel = attrs.get("w:ilvl")            # 0 -
            self.__level = {}
            self.__abstractNumber[ilevel] = self.__level
        elif name=="w:start":
            start = attrs.get("w:val")              # 1
            self.__level["start"] = start
        elif name=="w:numFmt":
            format = attrs.get("w:val")             # decimal, lowerLetter, lowerRoman
            self.__level["format"] = format
        elif name=="w:lvlText":
            text = attrs.get("w:val")
            self.__level["text"] = text
        elif name=="w:lvlJc":
            jc = attrs.get("w:val")
            self.__level["jc"] = jc
        elif name=="w:ind":
            leftIndent = attrs.get("w:left")
            self.__level["leftIndent"] = leftIndent

    def endElement(self, name):
        pass

    def characters(self, data):
        pass

#    def processingInstruction(self, target, data):
#        pass
#
#    def setDocumentLocator(self, locator):
#        pass
#
#    def startDocument(self):
#        pass
#
#    def endDocument(self):
#        pass
#
#    def startPrefixMapping(self, *args):
#        pass
#
#    def endPrefixMapping(self, *args):
#        pass






