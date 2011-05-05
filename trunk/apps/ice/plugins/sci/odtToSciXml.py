
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
import time

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


from oscar3 import Oscar3



# ignore script and style elements and it's contents
# p -> P


class OdtToSciXml(object):
    def __init__(self, iceContext, odtFile, oscar3ServerUri="http://localhost:8181"):
        self.iceContext = iceContext
        self.__odtFile = odtFile
        self.__sciXmlStr = None
        self.__ignoreList = ["script", "style"]
        self.__map = {  "p":"P", "span":"SPAN", "table":"DIV",  
                     }      # else use "SPAN" as the default
        self.__inP = False
        self.__inElemList = []      # not including P element
        self.__outputs = []
        self.__wrap = "<PAPER><BODY><DIV><HEADER/>\n%s\n</DIV></BODY></PAPER>"
        self.__location = []
        self.__offset = 0
        self.__ns = {}
        self.__nsn = {}
        for k, v in self.iceContext.OOoNS.iteritems():
            self.__ns[k] = "{%s}" % v
            self.__nsn[v] = k
        self.__oscar3ServerUri = oscar3ServerUri
        self.__ids = []
    
    
    @property
    def sciXmlStr(self):
        if self.__sciXmlStr is None:
            self._convert()
        return self.__sciXmlStr

    
    def process(self):
        self.__ids = []
        content = self.iceContext.fs.readFromZipFile(self.__odtFile, "content.xml")
        ns = self.__ns
        et = ElementTree
        odtContent = et.XML(content)
        odtContentBody = odtContent.find(ns["office"]+"body")
        bodyText = odtContentBody.find(ns["office"]+"text")
        
        # process all at this level
        self.__processLevel(bodyText)
        sciXmlStr = "".join(self.__outputs)
        sciXmlStr = self.__wrap % sciXmlStr
        
        print "getting data from oscar3"
        inlineAnnotatedSci = self.__getInlineAnnotatedSci(sciXmlStr)
        x = et.XML(inlineAnnotatedSci)
        bodydiv = x.find("BODY/DIV")
        
        print "marking up the odt file"
        self.__processAnnotatedSciElement(bodydiv)
        for i in range(len(self.__ids)):
            oe = self.__ids[i]
            if oe.a:
                self.__markupAndAnnotate(oe)
        
        print "saving"
        data = et.tostring(odtContent)
        self.iceContext.fs.addToZipFile(self.__odtFile, "content.xml", data)
    
    
    def __processAnnotatedSciElement(self, elem):
        # decorate(/annotate) the OOo elements     self.__ids
        id = elem.get("locId", 0)
        oe = self.__ids[int(id)]
        prevSibling = None
        for e in elem.getchildren():
            if e.tag=="ne":
                if prevSibling is None:     # elem.text section
                    oe.a = True
                    oe.aText = elem.text
                    oe.aTextElems.append(e)
                else:                       # prevSibling.tail section
                    oe.a = True
                    oe.aTail = prevSibling.tail
                    oe.aTailElems.append(e)
            id = e.get("locId")
            if id is not None:
                oe = self.__ids[int(id)]
                prevSibling = e
                self.__processAnnotatedSciElement(e)
    
    
    def __markupAndAnnotate(self, oe):
        if oe.a==False:
            return
        parent = oe.parent
        # find my index
        index = 0
        for e in parent.getchildren():
            if e==oe:
                break
            index += 1
        if oe.aTextElems!=[]:
            oe.text = oe.aText
            oe.aTextElems.reverse()
            for ne in oe.aTextElems:
                type = ne.get("type")
                surfaceText = ne.get("surface")
                atts = ["%s: %s" % (k, v) for k, v in ne.items()]
                ss = self.__createStyleElem(type, ne.items())
                noteElem = self.__createNote(atts)
                ss.tail = ne.tail
                ss.text = surfaceText
                ss.append(noteElem)
                oe.insert(0, ss)
        if oe.aTailElems!=[]:
            oe.tail = oe.aTail
            oe.aTailElems.reverse()
            for ne in oe.aTailElems:
                type = ne.get("type")
                surfaceText = ne.get("surface")
                atts = ["%s: %s" % (k, v) for k, v in ne.items()]
                ss = self.__createStyleElem(type, ne.items())
                noteElem = self.__createNote(atts)
                ss.tail = ne.tail
                ss.text = surfaceText
                ss.append(noteElem)
                oe.parent.insert(index+1, ss)       # add next sibling
                for c in ne.getchildren():
                    i = int(c.get("locId", "0"))
                    if i:
                        e = self.__ids[i]
                        e.parent.remove(e)
    
    
    def __getInlineAnnotatedSci(self, sciXmlStr):
        oscar = Oscar3(self.iceContext, serverUri=self.__oscar3ServerUri)
        inlineAnnotatedSci = oscar.inlineAnnotate(sciXmlStr)
        return inlineAnnotatedSci
    
    
    def __processLevel(self, elem):
        pss = elem.getchildren()
        ns = self.__ns
        # filter for only p & span elements
        l = [ns["text"]+"p", ns["text"]+"span"]
        pss = [e for e in pss if e.tag in l]
        for e in pss:
            e.parent = elem
            name = e.tag.split("}")[-1]
            # output
            e.a = False
            e.aText = None
            e.aTextElems = []
            e.aTail = None
            e.aTailElems = []
            e.locId = len(self.__ids)
            self.__ids.append(e)
            name = self.__map.get(name, "SPAN")
            self.__openElem(name)
            self.__writeText(e.text)
            # process children
            self.__processLevel(e)
            self.__closeElem(name)
            self.__writeText(e.tail)
    
    
    def __nsReverse(self, name):
        if name.find("}")!=-1:
            ns, name = name.split("}")
            name = self.__nsn.get(ns[1:], "?") + ":" + name
        return name
    
    
    def __writeText(self, text):
        if text is None or text=="":
            return
        self.__outputs.append(text)
    
    
    def __openElem(self, name):
        if name=="":
            pass
        else:
            self.__outputs.append("<%s locId='%s'>" % (name, len(self.__ids)-1))
            self.__inElemList.append(name)
    
    
    def __closeElem(self, name):
        if name=="":
            pass
        else:
            while self.__inElemList!=[]:
                n = self.__inElemList.pop()
                self.__outputs.append("</%s>" % n)
                if n==name:
                    break
    
    
    def __createNote(self, notes=[]):
        et = ElementTree
        a = et.Element(self.__ns["office"] + "annotation")
        c = et.Element(self.__ns["dc"] + "creator")
        c.text = "SciMarkup"
        d = et.Element(self.__ns["dc"] + "date")    #2008-11-20T00:00:00
        d.text = "%s-%s-%sT00:00:00" % time.localtime()[:3]
        a.append(c)
        a.append(d)
        for note in notes:
            t = et.Element(self.__ns["text"] + "p")
            t.text = note
            a.append(t)
        return a
        
    
    
    def __createStyleElem(self, styleType, atts):
        lookup = {  "DATA": "i-experimental-data",
                    "ONT": "i-ontology-term",
                    "CM": "i-chemical",     # with ('-structure') and without stucture
                    "CMs": "i-chemical-structure",     # with ('-structure') and without stucture
                    "RN": "i-reaction",
                    "CJ": "i-chemical-adjective",
                    "ASE": "i-enzyme",
                    "CPR": "i-chemical-prefix",
                 }
        if styleType=="CM" and "cmlRef" in [n for n,v in atts]:
            styleType = "CMs"
        styleName = lookup.get(styleType, "i-b");
        et = ElementTree
        s = et.Element(self.__ns["text"] + "span", attrib={self.__ns["text"]+"style-name": styleName})
        return s
    


# Modify the document backwards (starting at the end) so that positions do not change as the
#   document is being modified!


if __name__ == "__main__":
    # need iceContext
    import sys, os
    if len(sys.argv)>1:
        filename = sys.argv[1]
        if filename.endswith(".odt"):
            filename = filename[:-4]
    else:
        filename = "test"
    inputOdt = os.getcwd() + "/%s.odt" % filename
    outputOdt = os.getcwd() + "/sci-%s.odt" % filename
    sys.path.append(".")
    os.chdir("../../")
    import ice_common
    iceContext = ice_common.IceCommon
    iceContext.fs.copy(inputOdt, outputOdt)
    
    print "processing '%s'" % inputOdt
    o = OdtToSciXml(iceContext, outputOdt)
    o.process()
    print "done saved to '%s'" % outputOdt
    









