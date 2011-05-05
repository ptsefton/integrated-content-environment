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
import sys, getopt
sys.path.append("../../utils")

from file_system import FileSystem
from system import system
from html_cleanup import HtmlCleanup


try:
    from xml.etree.ElementTree import ElementTree, XML, tostring
except ImportError:
    try:
        import ElementTree
    except ImportError:
        from elementtree import ElementTree
    ElementTree, XML, tostring = ElementTree.ElementTree, ElementTree.XML, ElementTree.tostring


class HtmlToOdt(object):
    blankTemplate = "testData/blank.odt"
    HtmlParser = None                       # convertHtmlToXml
    oonss = {
        "office":"urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "style":"urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        "text":"urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "table":"urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "draw":"urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
        "fo":"urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
        "xlink":"http://www.w3.org/1999/xlink",
        "dc":"http://purl.org/dc/elements/1.1/",
        "meta":"urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
        "number":"urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
        "svg":"urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
        "chart":"urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
        "dr3d":"urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
        "math":"http://www.w3.org/1998/Math/MathML",
        "form":"urn:oasis:names:tc:opendocument:xmlns:form:1.0",
        "script":"urn:oasis:names:tc:opendocument:xmlns:script:1.0",
        "ooo":"http://openoffice.org/2004/office",
        "ooow":"http://openoffice.org/2004/writer",
        "oooc":"http://openoffice.org/2004/calc",
        "dom":"http://www.w3.org/2001/xml-events",
        "xforms":"http://www.w3.org/2002/xforms",
        "xsd":"http://www.w3.org/2001/XMLSchema",
        "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    }
    styles = {"bold":"T1", "italic":"T3", "boldItalic":"T2"}
    
    def __init__(self, fs):
        self.__fs = fs
        #self.oons = self.oonss
        self.oons = {}
        for key, value in self.oonss.iteritems():
            self.oons[key] = "{" + value + "}"
        self.__tags = []
    
    def convert(self, htmlFile, outputFile):
        html = self.HtmlParser.convertHtmlToXml(self.__fs.readFile(htmlFile))
        self.__fs.copy(self.blankTemplate, outputFile)
        content = self.__fs.readFromZipFile(outputFile, "content.xml")
        et = ElementTree(XML(content))
        odtTextElement = et.find("//"+self.oons["office"]+"text")
        
        self.__parseHtml(html, odtTextElement)
        
        content = tostring(et.getroot())
        self.__fs.addToZipFile(outputFile, "content.xml", content)
    
    
    
    def __parseHtml(self, html, odtTextElement):
        et = ElementTree(XML(html))
        html = et.getroot()
        title = html.find(".//head/title")
        if title is not None:
            title = title.text
            #<text:p text:style-name="Title">Title</text:p>
            titleElem = odtTextElement.makeelement(self.oons["text"]+"p", attrib = {self.oons["text"]+"style-name":"Title"})
            titleElem.text = title
            odtTextElement.append(titleElem)
            
        for elem in html.find(".//body").getchildren():
            self._parseElement(elem, odtTextElement)
        #print tostring(odtTextElement)
  
    
    def _parseElement(self, elem, odtElem, level=1, styleName="p"):
        pass

    def parseChildren(elem, odtElem, level, styleName):
        self.__pushTag(tag)
        for e in elem.getchildren():
            #if e.text:
            #  odtElem.text = e.text
            self._parseElement(e, odtElem, level, styleName)
            #if e.tail:
            #  odtElem.tail = e.tail
            self.__popTag()

    def makeP(elem, odtElem, level, styleName = "p", parent=None):
        if parent is None:
            parent = odtElem
        #<text:p text:style-name="Standard">para </text:p>

        #Only output a p if there are no more container elements below us
        if elem.find(".//p") <> None or elem.find(".//div") <> None:
        #TODO - need to be a bit smarter about his - what if there are divs in nested li elements?
            parseChildren(elem, odtElem, level, styleName)
        else:
            print "making a p: " + tostring(elem) + styleName
            p = odtElem.makeelement(self.oons["text"]+"p", attrib={self.oons["text"]+"style-name":styleName})
            p.text = elem.text
            odtElem.append(p)
            #need to work out what kind of children we have
            nestChildren = True
            blockElements = ["ul","ol","div","p", "li"]
            #TODO: move this into parseChildren - but we will need to pass in two nodes to do it
            #added parent for this purpose - this is passed in when we make a list to prevent nesting
            for e in elem.getchildren():
                print "Got an element %s" % e.tag
                if nestChildren and blockElements.count(e.tag) == 0:
                    self._parseElement(e, p, level + 1, styleName)
                #OOPS - took out stuff to do with tail
            else:
                nestChildren = False
                self._parseElement(e, parent, level + 1, styleName)
        print tostring(odtElem)
        tag = elem.tag
        if tag=="p" or tag=="div": 
            makeP(elem, odtElem, level, styleName)
        elif tag.startswith("h"):
            #<text:p text:style-name="h1">Heading 1</text:p>
            p = odtElem.makeelement(self.oons["text"]+"p", attrib={self.oons["text"]+"style-name":tag})
            p.text = elem.text
            odtElem.append(p)
        elif tag=="ul" or tag=="ol":
            #Make a stand-alone one element ODF list for every li
            if tag =="ul":
                styletype = "b"
            else:
                styletype = "n"
            for e in elem.getchildren():
                if e.tag=="li":
                    list = odtElem.makeelement(self.__ns("text", "list"), 
                                attrib={self.__ns("text", "style-name"):"li%s%s" % (level, styletype)})
                    odtElem.append(list)             
                    listItem = odtElem.makeelement(self.__ns("text", "list-item"), {})
                    list.append(listItem)
                    #Pass in the parent element cos we don't want nested lists
                    makeP(e, listItem, level, "li%s%s" % (level, styletype), odtElem)
                    #p = odtElem.makeelement(self.__ns("text", "p"),
                    #        attrib={self.__ns("text", "style-name"):"li%s%s" % (level, styletype)})
                    #TODO: this is too simple - what about if there are p elements in the li?
                    #p.text = e.text
                    #listItem.append(p)
                    #for i in e.getchildren():
                    #    self._parseElement(i, odtElem, level+1)
                else:
                    self._parseElement(e, odtElem, level+1)
        elif tag=="b":
            self.__pushTag(tag)
            if elem.text:
                style = self.__getCurrentStyle()
                span = odtElem.makeelement(self.oons["text"]+"span", attrib={self.oons["text"]+"style-name":style})
                span.text = elem.text
                odtElem.append(span)
            for e in elem.getchildren():
                self._parseElement(e, odtElem)
                if e.tail:
                    style = self.__getCurrentStyle()
                    span = odtElem.makeelement(self.oons["text"]+"span", attrib={self.oons["text"]+"style-name":style})
                    span.text = e.tail
                    odtElem.append(span)
            self.__popTag()
        elif tag=="i":
            self.__pushTag(tag)
            if elem.text:
                style = self.__getCurrentStyle()
                span = odtElem.makeelement(self.oons["text"]+"span", attrib={self.oons["text"]+"style-name":style})
                span.text = elem.text
                odtElem.append(span)
            for e in elem.getchildren():
                self._parseElement(e, odtElem, level)
                if e.tail:
                    style = self.__getCurrentStyle()
                    span = odtElem.makeelement(self.oons["text"]+"span", attrib={self.oons["text"]+"style-name":style})
                    span.text = e.tail
                    odtElem.append(span)
            self.__popTag()
        else:
            if elem.text:
                odtElem.text=elem.text
            #TODO - worry about tail
            parseChildren(elem, odtElem, level, styleName)
    
    def __getCurrentStyle(self):
        l = self.__tags[-2:]
        style = ""
        if len(l)>1:
            if l==["i", "b"] or l==["b", "i"]:
                style = self.styles["boldItalic"]
            else:
                print "Unsupport sequence '%s'" % l
        else:
            t = l[0]
            if t=="b":
                style = self.styles["bold"]
            elif t=="i":
                style = self.styles["italic"]
            else:
                print "no style for '%s'" % t
        #print "l='%s', style='%s'" % (str(l), style)
        return style
    
    def __pushTag(self, tag):
        #print "push '%s'" % tag
        self.__tags.append(tag)
    
    def __popTag(self):
        tag = self.__tags.pop()
        #print "pop '%s'" % tag
    
    def __ns(self, ns, tag):
        return self.oons[ns] + tag
#main as per http://www.artima.com/weblogs/viewpost.jsp?thread=4829



class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
            inputFile = args[0]
            outputFile = args[1]
            fs = FileSystem('.')
            HtmlToOdt.HtmlParser = HtmlCleanup
            h2o = HtmlToOdt(fs)
            h2o.convert(inputFile, outputFile)
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
    





