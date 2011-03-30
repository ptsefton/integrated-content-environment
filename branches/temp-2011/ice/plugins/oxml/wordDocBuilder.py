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

import types

class WordDocBuilder(object):
    # Constructor:
    #   WordDocBuilder()
    # Properties:
    # Methods:
    #   addParagraph(contents)
    #   createTextRun(text)         - returns a textRun string
    #   toString()

    DocBodyElement = """<w:document
 xmlns:ve="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
 >
 <w:body>
 %s
 </w:body>
</w:document>"""
    SectionProp = """<w:sectPr w:rsidR="00D7006D" w:rsidRPr="00D7006D" w:rsidSect="00BB59AC">
 <w:pgSz w:w="11906" w:h="16838"/>
 <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
 <w:cols w:space="708"/><w:docGrid w:linePitch="360"/>
</w:sectPr>"""
    def __init__(self):
        self.__paras = []

    def addParagraph(self, contents):
        if type(contents) is types.ListType:
            pass
        else:
            contents = [contents]
        def testWrap(c):
            if c.startswith("<m:oMath") or c.startswith("<w:r"):
                pass
            elif c.startswith("<"):
                # wrap in a run (w:r)
                c = "<w:r>%s</w:r>" % c
            else:
                # just plain text
                c = self.createTextRun(c)
            return c
        contents = [testWrap(c) for c in contents]
        para = "<w:p>%s</w:p>" % "".join(contents)
        self.__paras.append(para)

    def createTextRun(self, text):
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        return '<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % text

    def _getBodyContents(self):
        """ for testing only """
        return self.__paras

    def toString(self):
        h = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        s = "\n".join(self.__paras)
        return h + self.DocBodyElement % s

    def __str__(self):
        s = "\n".join(self.__paras)
        return self.DocBodyElement % s


