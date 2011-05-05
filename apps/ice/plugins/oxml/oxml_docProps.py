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


class DocProps(object, SaxContentHandler):
    # docProps/core.xml
    # xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    # xmlns:dc="http://purl.org/dc/elements/1.1/"
    # xmlns:dcterms="http://purl.org/dc/terms/"
    # xmlns:dcmitype="http://purl.org/dc/dcmitype/"
    # xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    #
    # dc:title
    # dc:creator
    # cp:lastModifiedBy
    # cp:revision
    # dcterms:created     2010-04-01T01:14:00Z
    # dcterms:modified    2010-04-01T01:14:00Z
    def __init__(self, xmlStr):
        SaxContentHandler.__init__(self)
        self._properties = {}   # elementName:TextContent
        self.__name = None
        if xmlStr is not None:
            saxParseString(xmlStr, self)

    @property
    def title(self):
        return self._properties.get("dc:title", None)

    def getProperty(self, name):
        return self._properties.get(name, None)

    # Sax event handlers
    def startElement(self, name, _attrs):
        self.__name = name

    def endElement(self, name):
        self.__name = None

    def characters(self, data):
        if self.__name:
            self._properties[self.__name] = data

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



