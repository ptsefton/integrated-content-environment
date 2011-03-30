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


""" """
from types import UnicodeType
import re

# NOTE: oxml2xhtml_utils also fixes up the SAX parser when working under IronPython
from oxml2xhtml_utils import TimeIt, DataCapture, Image, ParseWordHtml
from oxml2xhtml_utils import SaxContentHandler, saxParseString
from word import MSWord
# (MSWord.ErrorMessage == None) if all OK
from wordDocBuilder import WordDocBuilder
from shtml import Shtml

from oxml_docRels import DocRels
from oxml_wordNumbering import WordNumbering
from oxml_docProps import DocProps

from oxml2xhtml_baseState import BaseState
from oxml2xhtml_basic_states import (NullState, DocumentState, BodyState,
        ParaState, ParaPropState, ParaNumPropState,
        RunState, RunPropState, TextState, HyperlinkState,
        SectPropState,
        IgnoreState, UnknownState)
from oxml2xhtml_obj_states import (DrawingState, InlineState, AnchorState, GraphicState,
        GraphicDataState, PicState, PicPropState, PicBlipFillState,
        PicSpanPropState, XFormState, ChartState, PictState, ShapeTypeState,
        ShapeState, ObjectState)
from oxml2xhtml_table_states import (TableState, TablePropState, TableGridState,
        TableRowState, TableCellState, TableCellPropState)
from oxml2xhtml_omath_states import (OMathState)



stateTree = {       # Note: "*" is a wildcard e.g. matches any element
    "NullState": {"w:document":DocumentState},
    "DocumentState": {"w:body":BodyState},
    "BodyState": {"w:p":ParaState, "w:tbl":TableState, "w:sectPr":SectPropState},
    "ParaState": {"w:pPr":ParaPropState, "w:r":RunState, "w:proofErr":IgnoreState,
                    "m:oMath":OMathState, "w:hyperlink":HyperlinkState},
    "RunState": {"w:rPr":RunPropState, "w:t":TextState, "w:drawing":DrawingState,
                 "w:pict":PictState, "w:object":ObjectState},
    "DrawingState": {"wp:inline":InlineState, "wp:anchor":AnchorState},
    "InlineState": {"a:graphic":GraphicState},
    "AnchorState": {"a:graphic":GraphicState},
    "GraphicState": {"a:graphicData":GraphicDataState},
    "GraphicDataState": {"pic:pic":PicState, "c:chart":ChartState},
    "PicState": {"pic:nvPicPr":PicPropState, "pic:blipFill":PicBlipFillState, "pic:spPr":PicSpanPropState},
    "PicPropState": {},
    "ParaPropState": {"w:numPr": ParaNumPropState},
    "ParaNumPropState": {},
    "PicSpanPropState": {"a:xfrm":XFormState},
    "ChartState": {},
    "XFormState": {},
    "OMathState": {},
    "HyperlinkState": {"w:r":RunState, "w:proofErr":IgnoreState},
    "ObjectState": {"v:shapetype":ShapeTypeState, "v:shape":ShapeState},
    "PictState": {"v:shapetype":ShapeTypeState, "v:shape":ShapeState},
    "ShapeTypeState": {},
    "ShapeState": {},
    "TableState": {"w:tblPr":TablePropState, "w:tblGrid":TableGridState,
                    "w:tr":TableRowState},
    "TablePropState": {},
    "TableGridState": {},
    "TableRowState": {"w:tc":TableCellState},
    "TableCellState": {"w:tcPr":TableCellPropState, "w:p":ParaState},
    "TableCellPropState": {},
    "IgnoreState" : {},
    #"PropertyState": {"w:pStyle":StyleState, "w:pPr":PropertyState, "w:numPr":NumPropState},
    #"NumPropState": {},
    "UnknownState": {"*":UnknownState}
}

BaseState._stateTree = stateTree
    
#===============================================
#===============================================
class Oxml2xhtml(object, SaxContentHandler):
    _OXMLNS = {
        "ve":"http://schemas.openxmlformats.org/markup-compatibility/2006",
        "o":"urn:schemas-microsoft-com:office:office",
        "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "m":"http://schemas.openxmlformats.org/officeDocument/2006/math",
        "v":"urn:schemas-microsoft-com:vml",
        "wp":"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "w10":"urn:schemas-microsoft-com:office:word",
        "w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wne":"http://schemas.microsoft.com/office/word/2006/wordml"
    }

    
    def __init__(self, context=None):
        SaxContentHandler.__init__(self)

        self.context = context
        #
        h = Shtml()
        self.__html = h
        self.__addHtmlStyles(self.__html)
        
        self.__styles = None
        self.__meta = {"authors": []}
        self.__eDepth = 0
        self.__currentState = NullState(self)
        self.__docxFile = None
        self.__images = {}          # name: {}
        self.__objImages = {}       # srcName: ?
        self._filesRelPath = None
        self.outputFile = None
        self.__numbering = None
        self.__dataCaptures = {}
        self.idPrefix = ""
        self.bookmarkPrefix = "_bm_"        # note: will be idPrefix + bookmarkPrefix
        self.processTime = 0
        self.__setup()


    @property
    def html(self):
        return self.__html


    @property
    def currentHtmlElement(self):
        return self.__html.body


    @property
    def oxml(self):
        return self


    def __getState(self):
        return self.__currentState
    def __setState(self, value):
        #print "changing state to ", value
        if not isinstance(value, BaseState):
            raise Exception("currentState can only be set to object of BaseState type!")
        self.__currentState = value
    currentState = property(__getState, __setState)

    
    @property
    def styles(self):
        return self.__styles


    @property
    def numbering(self):
        if self.__numbering is None:
            # print "numbering.xml"
            try:
                fs = self.context.fs
                numberingXmlStr = fs.readFromZipFile(self.__docxFile, "word/numbering.xml")
            except Exception, e:
                numberingXmlStr = None
            self.__numbering = WordNumbering(numberingXmlStr)
            #self.__numbering.getNumLevelInfo(numId, level)  # "start":"1", "format":"decimal"
            #print self.__numbering._abstractNumbers
        return self.__numbering
    
    @property
    def docRels(self):
        return self._docRels


    def startDataCapturing(self, id):
        dataCapture = DataCapture()
        self.__dataCaptures[id] = dataCapture
        return dataCapture

    def stopDataCapturing(self, id):
        if self.__dataCaptures.has_key(id):
            return self.__dataCaptures.pop(id)
        return None


    # for testing only
    def _process(self, contentXmlStr, stylesXmlStr=None):
        self._docRels = DocRels(None)
        self._docProps = DocProps(None)
        saxParseString(contentXmlStr, self)

    
    def processFile(self, file, filesRelPath=None):
        timeIt = TimeIt()
        fs = self.context.fs
        self.__docxFile = file
        if self.outputFile is None:
            self.outputFile = fs.splitExt(file)[0] + ".htm"
        if filesRelPath is None:
            self._filesRelPath = fs.splitExt(fs.split(file)[-1])[0] + "_files/"

        #print "document.xml.rels"
        relXmlStr = fs.readFromZipFile(file, "word/_rels/document.xml.rels")
        self._docRels = DocRels(relXmlStr)

        #print "core.xml"
        coreXmlStr = fs.readFromZipFile(file, "docProps/core.xml")
        self._docProps = DocProps(coreXmlStr)
        titleProp = self._docProps.title
        if titleProp:
            self.html.title = titleProp

        #print "document.xml"
        contentXmlStr = fs.readFromZipFile(file, "word/document.xml")
        if contentXmlStr is not None:
            saxParseString(contentXmlStr, self)
        else:
            print "Warning: '%s' contains no 'word/document.xml' file!" % file
        if self.html.title=="":
            self.html.title = "[Untitled]"
        self.processTime = timeIt.mS()


    def __setup(self):
        pass


    def addObjImage(self, imgElem, dataCapture, srcName=None):
        fs = self.context.fs
        if srcName is None or srcName=="":
            srcName = "object_%s" % (len(self.__objImages)+1)
        name, ext = fs.splitExt(srcName)
        if ext=="":
            ext = ".png"
        #print "name='%s', ext='%s'" % (name, ext)
        srcName = fs.join(self._filesRelPath, name) + ext
        self.__objImages[srcName] = (dataCapture, imgElem)
        return srcName


    def getEmbeddedObjectImages(self, fs, path=None):
        htmlFile = self._createObjDoc(fs, path)
        if htmlFile is not None:
            if Image:
                return self._extractImages(fs, htmlFile, Image, path)
        return []

    def _createObjDoc(self, fs, path=None):
        if self.__objImages=={}:
            return None
        htmlFile = None
        #print "--- createObjDoc ---"
        docBuilder = WordDocBuilder()
        for key, value in self.__objImages.iteritems():
            dataCapture, imgElem = value
            docBuilder.addParagraph([key, dataCapture.toString()])
            #print key
        #print docBuilder.toString()
        if MSWord.ErrorMessage:
            msg = MSWord.ErrorMessage
            if msg.find("No module named clr")>-1:
                print "Not running under IronPython!"
            else:
                print "*** %s" % MSWord.ErrorMessage
        else:
            word = MSWord()
            objDocument = docBuilder.toString()
            htmlFile = word.extractObjectImages(fs=fs, file=self.__docxFile,
                objDocument=objDocument)
        return htmlFile


    def _extractImages(self, fs, htmlFile, Image, path=None):
        files = []
        if path is None:
            path = fs.splitExt(self.outputFile)[0] + "_files"
        path = fs.absPath(path)
        print "path='%s', %s" % (path, fs.isDirectory(path))
        if not fs.isDirectory(path):
            fs.makeDirectory(path)
            print " %s" % fs.isDirectory(path)
        htmlPath = fs.split(htmlFile)[0] + "/"
        htmlData = fs.readFile(htmlFile)
        images = ParseWordHtml.parseHtml(htmlData)
        def parseInt(s, v):     # helper method
            try:
                return int(s)
            except:
                return v
        # process the images
        for name, atts in images.iteritems():
            imgFile = htmlPath + atts.get("src")
            imgElem = self.__objImages.get(name, (None, None))[1]
            # Read image
            image = Image(imgFile)
            width = parseInt(atts.get("width"), image.width)
            height = parseInt(atts.get("height"), image.height)
            if hasattr(imgElem, "doNotResize"):
                pass
                #print "not resizing this ****"
            else:
                width = width/2
                height = height/2
                image.resize(width, height)
            iname = fs.split(name)[-1]
            alt = atts.get("alt", atts.get("id", iname))
            # Update image attributes
            imgElem.setAttribute("src", name)
            imgElem.setAttribute("alt", alt)
            imgElem.setAttribute("title", atts.get("title", alt))
            style = "width:%spx;height:%spx;" % (width, height)
            #style += "vertical-align:text-bottom;"
            imgElem.setAttribute("class", "inlineImgVAlign")
            imgElem.setAttribute("style", style)
            # save image as X and close
            iFullname = path + "/" + iname
            files.append(iFullname)
            image.saveAs(iFullname)
            image.close()
        return files

    
    def addImage(self, picState, ext=".jpg"):
        target = picState.target
        fs = self.context.fs
        name = fs.split(target)[-1]
        # change extension
        name, ext2 = fs.splitExt(name)
        name += ext
        src = fs.join(self._filesRelPath, name)
        self.__images[name] = {"target":target,
                                "xmm":picState.xmm,
                                "ymm":picState.ymm,
                                "cropRect":picState.cropRect,   # (left, top, right, bottom)
                                "src":src}
        return src

    
    def writeImagesTo(self, path=None):
        fs = self.context.fs
        if path is None:
            path = fs.splitExt(self.outputFile)[0] + "_files/"
        if not fs.isDirectory(path):
            fs.makeDirectory(path)
        for name, info in self.__images.iteritems():
            saveToFile = fs.join(path, name)
            if Image is not None:
                #print "*** Using Image"
                try:
                    image = Image.ImageFromZip(self.__docxFile, "word/" + info.get("target"))
                    # assuming 96dpi (96/25.4)
                    x = int(info["xmm"] * 96 / 25.4 + 0.5)
                    y = int(info["ymm"] * 96 / 25.4 + 0.5)
                    crop = info["cropRect"]
                    if crop!=(0,0,0,0):
                        # First crop the image
                        l, t, r, b = crop
                        if l>0:
                            l = image.width * l / 100000
                        if r>0:
                            r = image.width * r / 100000
                        if t>0:
                            t = image.height * t / 100000
                        if b>0:
                            b = image.height * b / 100000
                        #print "crop %s" % ((l,t,r,b),)
                        try:
                            image.crop(l, t, r, b)
                        except Exception, e:
                            print "Error in crop '%s'" % str(e)
                    #print "-- %s" % (info.get("target"))
                    #print "  x=%s %s, y=%s, %s" % (x, image.width, y, image.height)
                    if x!=image.width or y!=image.height:
                        image.resize(x, y)
                    #print "saveToFile='%s'" % saveToFile
                    ext = saveToFile.rsplit(".", 1)[1].lower()
                    if ext==".jpg" or ext==".jpeg":
                        image.saveAsJpeg(saveToFile)
                    else:
                        image.saveAs(saveToFile)
                except Exception, e:
                    print "Error in writeImagesTo() - %s" % str(e)
                    # do the old way - better than nothing
                    imageData = fs.readFromZipFile(self.__docxFile, "word/" + info.get("target"))
                    fs.writeFile(saveToFile, imageData)
            else:
                imageData = fs.readFromZipFile(self.__docxFile, "word/" + info.get("target"))
                fs.writeFile(saveToFile, imageData)


    def writeHtmlTo(self, file=None):
        fs = self.context.fs
        if file is None:
            file = self.outputFile
        html = self.__html.toString()
        if type(html) is UnicodeType:
            html = html.encode("utf-8")
        fs.writeFile(file, html)


    #===========================
    # sax event handler methods
    #===========================
    def startElement(self, name, _attrs):
        attrs = {}
        for k in _attrs.keys():
            attrs[k]=_attrs.get(k)
        self.__currentState._startElement(name, attrs)
        self.__eDepth += 1
        for d in self.__dataCaptures.itervalues():
            d.startElement(name, attrs)

    
    def endElement(self, name):
        self.__eDepth -= 1
        for d in self.__dataCaptures.itervalues():
            d.endElement(name)
        self.__currentState._endElement(name)
    
    
    def characters(self, data):
        for d in self.__dataCaptures.itervalues():
            d.characters(data)
        self.__currentState._characters(data)
    #===========================
    
    
    def serialize(self):
        """ xhtml output (utf-8 encoded)"""
        s = str(self.__html)
        if type(s) is UnicodeType:
            s = s.encode("utf-8")
        return s


    def __addHtmlStyles(self, h):
        """ add default html output styles """
        h.addStyle("dt", "font-weight:bold;")
        h.addStyle(".title", "text-align:center; color:#d87000;")
        h.addStyle("h1", "color:#000080;")
        h.addStyle("h2", "color:#000080;")
        h.addStyle("h3", "color:#000080;")
        h.addStyle("h4", "color:#000080;")
        h.addStyle("h5", "color:#000080;")
        h.addStyle("h6", "color:#000080;")
        h.addStyle(".centered", "text-align:center;")
        h.addStyle(".right-aligned", "text-align:right;")
        h.addStyle(".indented", "padding-left:4ex;")
        h.addStyle("pre.pre", "background-color:#eeeeee;")

        h.addStyle("blockquote.bq", "font-style:italic;")

        h.addStyle(".level1", "padding-left:4ex;")
        h.addStyle(".level2", "padding-left:8ex;")
        h.addStyle(".level3", "padding-left:12ex;")
        h.addStyle(".level4", "padding-left:16ex;")
        h.addStyle(".level5", "padding-left:20ex;")

        h.addStyle("ol.lin>li", "list-style-type:decimal;")
        h.addStyle("ol.lii>li", "list-style-type:lower-roman;")
        h.addStyle("ol.liI>li", "list-style-type:upper-roman;")
        h.addStyle("ol.lia>li", "list-style-type:lower-alpha;")
        h.addStyle("ol.liA>li", "list-style-type:upper-alpha;")

        h.addStyle("td", "border:1px solid black;")
        h.addStyle("table", "border:1px solid black;")

        h.addStyle("li", "padding-bottom:0px;")

        h.addStyle("img.inlineImgVAlign", "vertical-align:text-bottom;")


    def __str__(self):
        """ Formatted xhtml output (utf-8 encoded)"""
        s = self.__html.formatted()
        if type(s) is types.UnicodeType:
            s = s.encode("utf-8")
        return s



if __name__=="__main__":
    from oxml2xhtml_test import test
    test()

