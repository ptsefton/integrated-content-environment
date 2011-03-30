
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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
import types

enableCElementTree = False
ElementTree = None
cElementTree = None
if ElementTree is None:
    try:
        from xml.etree import ElementTree as ElementTree
    except ImportError:
        try:
            import ElementTree as ElementTree
        except ImportError:
            try:
                from elementtree import ElementTree
            except ImportError:
                print "Error loading ElementTree! Please install and try again."
                sys.exit(1)
pyElementTree = ElementTree
try:
    from xml.etree import cElementTree as cElementTree
except ImportError:
    try:
        import cElementTree as cElementTree
    except ImportError:
        cElementTree = None
if enableCElementTree and cElementTree is not None:
    ElementTree = cElementTree
# NOTE: ElementTree.__name__ will tell you which element tree is being used.



# ignore script and style elements and it's contents
# p -> P
## ol, ul -> LIST
## li -> LI
## table -> TABLE
## tr -> TR
## th, td -> TH, TD
## div -> DIV HEADER
# sup[@class='ref'] -> REF @TYPE="P"
# b[@class='xrefc'] -> XREF @TYPE="COMPOUND"
# sup -> SP
# sub -> SB
# i -> IT
# b -> B
# ignore all other elements
# NOTE: do not nest <P> elements
class XhtmlToSciXml(object):
    def __init__(self, xhtmlStr):
        self.__xhtmlStr = xhtmlStr
        self.__sciXmlStr = None
        self.__ignoreList = ["script", "style"]
        self.__map = {  "p":"P", 
                        ##"sup":"SP", "sub":"SB", "i":"IT", "b":"B",
                        "th":"P", "td":"P", "li":"P", 
                        "ul":"DIV", "ol":"DIV", "table":"DIV", "tr":"DIV", "tbody":"DIV",
                        "dd":"P", "dt":"P", "dl":"P",
                        "div":"DIV", "br":"SPAN",
                     }
        self.__inP = False
        self.__inElemList = []      # not including P element
        self.__outputs = []
        self.__wrap = "<PAPER><BODY><DIV><HEADER/>\n%s\n</DIV></BODY></PAPER>"
        self.__location = []
        self.__offset = 0
    
    
    @property
    def xhtmlStr(self):
        return self.__xhtmlStr
    
    @property
    def sciXmlStr(self):
        if self.__sciXmlStr is None:
            self._convert()
        return self.__sciXmlStr

    
    def _convert(self):
        x = ElementTree.XML(self.__xhtmlStr)
        self.__location.append(1)
        self.__processElement(x)
        self.__sciXmlStr = self.__wrap % ("".join(self.__outputs))
    
    
    def __writeText(self, text):
        if text is None or text=="":
            return
        #if not self.__inP:
        #    self.__openP()
        self.__outputs.append(text)
    
    
    def __processElement(self, e):
        if e.tag in self.__ignoreList:
            return
        tag = self.__map.get(e.tag, "SPAN")
        self.__offset = 1
        self.__openElem(tag)
        if e.text is not None:
            self.__writeText(e.text)
            self.__offset += 1
        for child in e.getchildren():
            self.__location.append(self.__offset)
            self.__processElement(child)
            self.__offset = self.__location.pop()
            self.__offset += 1
            if child.tail is not None:
                self.__writeText(child.tail)
                self.__offset += 1
        self.__closeElem(tag)
    
    
    def __openElem(self, name):
        if name=="":
            pass
        #elif name=="P":
        #    self.__openP()
        else:
            location = "/" + "/".join([str(i) for i in self.__location]) #+ "/" + str(self.__offset)
            self.__outputs.append("<%s loc='%s'>" % (name, location))
            self.__inElemList.append(name)
    
    
    def __closeElem(self, name):
        if name=="":
            pass
        #elif name=="P":
        #    self.__closeP()
        else:
            while self.__inElemList!=[]:
                n = self.__inElemList.pop()
                self.__outputs.append("</%s>" % n)
                if n==name:
                    break
    
    
    def __openP(self):
        if self.__inP:
            # close any other open elements
            self.__closeP()
        location = "/".join([str(i) for i in self.__location])
        if self.__offset!=0: 
            location += ("/" + str(self.__offset))
        self.__outputs.append("<P location='%s'>" % location)
        self.__inP = True
    
    def __closeP(self):
        if self.__inP:
            while self.__inElemList!=[]:
                self.__closeElem(self.__inElemList[-1])
            self.__outputs.append("</P>")
            self.__inP = False
    
    
    def getXhtmlElem(self, loc):
        loc = loc.strip("/")
        r = ElementTree.XML(self.__xhtmlStr)
        x = r
        steps = [int(i) for i in loc.split("/")]
        steps.pop(0)
        for step in steps:
            children = []
            if x.text is not None:
                children.append(x.text)
            for c in x.getchildren():
                children.append(c)
                if c.tail is not None:
                    children.append(c.tail)
            index = step-1
            x = children[index]
        if type(x) in types.StringTypes:
            return x
        else:
            return ElementTree.tostring(x)


# Modify the document backwards (starting at the end) so that positions do not change as the
#   document is being modified!


if __name__ == "__main__":
    xhtml = """<div>
        Testing<p>Para</p> two <table><tr><td>TD</td><th>TH</th></tr></table> 3 <p><div>DIV</div>test</p>
        <script>SCRIPT</script>
        <style>STYLE</style>
        <i>Italic</i><b>Bold</b>
        <sup>SUP</sup> <sub>SUB</sub>
        <div><p>Testing <p>123</p>.</p></div>
        <div>1<!-- -->3<?test ?>5&amp;7<p>end</p><p/> x</div>
    </div>"""
    o = XhtmlToSciXml(xhtml)
    print "\n\n"
    print "xhtml='%s'\n" % xhtml
    print o.sciXmlStr
    print 
    print o.getXhtmlElem("/1/21")
    print o.getXhtmlElem("/1/21/2")
    print o.getXhtmlElem("/1/21/2/1")









