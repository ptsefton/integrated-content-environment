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


class DocRels(object, SaxContentHandler):
    # word/_rels/document.xml.rels
    # xmlns="http://schemas.openxmlformats.org/package/2006/relationships"
    # <Relationships>
    #   <Relationship Id='rId3' Target="media/image3.jpeg" Type="http://.../image" [TargetMode="External"] />
    def __init__(self, xmlStr):
        SaxContentHandler.__init__(self)
        self._rels = {}     # id:(Target, Type, TargetMode)
        if xmlStr is not None:
            saxParseString(xmlStr, self)

    def getTarget(self, id):
        return self._rels.get(id, (None, None, None))[0]

    def getType(self, id):
        return self._rels.get(id, (None, None, None))[1]

    def getTargetMode(self, id):
        return self._rels.get(id, (None, None, None))[2]

    # Sax event handlers
    def startElement(self, name, _attrs):
        attrs = {}
        for k in _attrs.keys():
            attrs[k]=_attrs.get(k)
        if name=="Relationship":
            id = attrs.get("Id")
            type = attrs.get("Type")
            target = attrs.get("Target")
            mode = attrs.get("TargetMode")
            self._rels[id]=(target, type, mode)

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





