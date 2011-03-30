
#!/usr/bin/env python
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

import re
from html_input import NodeType, Node, HtmlInput


class HtmlCleanup(object):
    xhtml_entities = {
                   "&zwnj;" : u"\u200c", "&aring;" : u"\u00e5",
                   "&yen;" : u"\u00a5", "&ograve;" : u"\u00f2", "&Chi;" : u"\u03a7",
                   "&delta;" : u"\u03b4", "&rang;" : u"\u232a", "&sup;" : u"\u2283",
                   "&trade;" : u"\u2122", "&Ntilde;" : u"\u00d1", "&xi;" : u"\u03be",
                   "&upsih;" : u"\u03d2", "&nbsp;" : u"\u00a0", "&Atilde;" : u"\u00c3",
                   "&radic;" : u"\u221a", "&otimes;" : u"\u2297", "&nabla;" : u"\u2207",
                   "&aelig;" : u"\u00e6", "&oelig;" : u"\u0153", "&equiv;" : u"\u2261",
                   "&lArr;" : u"\u21d0", "&infin;" : u"\u221e", "&Psi;" : u"\u03a8",
                   "&auml;" : u"\u00e4", "&circ;" : u"\u02c6", "&Epsilon;" : u"\u0395",
                   "&otilde;" : u"\u00f5", "&Icirc;" : u"\u00ce", "&Eacute;" : u"\u00c9",
                   "&ndash;" : u"\u2013", "&sbquo;" : u"\u201a", "&Prime;" : u"\u2033",
                   "&prime;" : u"\u2032", "&psi;" : u"\u03c8", "&Kappa;" : u"\u039a",
                   "&rsaquo;" : u"\u203a", "&Tau;" : u"\u03a4", "&uacute;" : u"\u00fa",
                   "&ocirc;" : u"\u00f4", "&lrm;" : u"\u200e", "&lceil;" : u"\u2308",
                   "&cedil;" : u"\u00b8", "&Alpha;" : u"\u0391", "&not;" : u"\u00ac",
                   "&Dagger;" : u"\u2021", "&AElig;" : u"\u00c6", "&ni;" : u"\u220b",
                   "&oslash;" : u"\u00f8", "&acute;" : u"\u00b4", "&zwj;" : u"\u200d",
                   "&alefsym;" : u"\u2135", "&laquo;" : u"\u00ab", "&shy;" : u"\u00ad",
                   "&rdquo;" : u"\u201d", "&ge;" : u"\u2265", "&Igrave;" : u"\u00cc",
                   "&nu;" : u"\u03bd", "&Ograve;" : u"\u00d2", "&lsaquo;" : u"\u2039",
                   "&sube;" : u"\u2286", "&rarr;" : u"\u2192", "&sdot;" : u"\u22c5",
                   "&supe;" : u"\u2287", "&Yacute;" : u"\u00dd", "&lfloor;" : u"\u230a",
                   "&rlm;" : u"\u200f", "&Auml;" : u"\u00c4", "&brvbar;" : u"\u00a6",
                   "&Otilde;" : u"\u00d5", "&szlig;" : u"\u00df", "&clubs;" : u"\u2663",
                   "&diams;" : u"\u2666", "&agrave;" : u"\u00e0", "&Ocirc;" : u"\u00d4",
                   "&Iota;" : u"\u0399", "&Theta;" : u"\u0398", "&Pi;" : u"\u03a0",
                   "&OElig;" : u"\u0152", "&Scaron;" : u"\u0160", "&frac14;" : u"\u00bc",
                   "&egrave;" : u"\u00e8", "&sub;" : u"\u2282", "&iexcl;" : u"\u00a1",
                   "&frac12;" : u"\u00bd", "&ordf;" : u"\u00aa", "&sum;" : u"\u2211",
                   "&prop;" : u"\u221d", "&Uuml;" : u"\u00dc", "&ntilde;" : u"\u00f1",
                   "&atilde;" : u"\u00e3", "&asymp;" : u"\u2248", "&uml;" : u"\u00a8",
                   "&prod;" : u"\u220f", "&nsub;" : u"\u2284", "&reg;" : u"\u00ae",
                   "&rArr;" : u"\u21d2", "&Oslash;" : u"\u00d8", "&THORN;" : u"\u00de",
                   "&yuml;" : u"\u00ff", "&aacute;" : u"\u00e1", "&Mu;" : u"\u039c",
                   "&hArr;" : u"\u21d4", "&le;" : u"\u2264", "&thinsp;" : u"\u2009",
                   "&dArr;" : u"\u21d3", "&ecirc;" : u"\u00ea", "&bdquo;" : u"\u201e",
                   "&Sigma;" : u"\u03a3", "&kappa;" : u"\u03ba", "&Aring;" : u"\u00c5",
                   "&tilde;" : u"\u02dc", "&emsp;" : u"\u2003", "&mdash;" : u"\u2014",
                   "&uarr;" : u"\u2191", "&times;" : u"\u00d7", "&Ugrave;" : u"\u00d9",
                   "&Eta;" : u"\u0397", "&Agrave;" : u"\u00c0", "&chi;" : u"\u03c7",
                   "&real;" : u"\u211c", "&eth;" : u"\u00f0", "&rceil;" : u"\u2309",
                   "&iuml;" : u"\u00ef", "&gamma;" : u"\u03b3", "&lambda;" : u"\u03bb",
                   "&harr;" : u"\u2194", "&Egrave;" : u"\u00c8", "&frac34;" : u"\u00be",
                   "&dagger;" : u"\u2020", "&divide;" : u"\u00f7", "&Ouml;" : u"\u00d6",
                   "&image;" : u"\u2111", "&hellip;" : u"\u2026", "&igrave;" : u"\u00ec",
                   "&Yuml;" : u"\u0178", "&ang;" : u"\u2220", "&alpha;" : u"\u03b1",
                   "&frasl;" : u"\u2044", "&ETH;" : u"\u00d0", "&lowast;" : u"\u2217",
                   "&Nu;" : u"\u039d", "&plusmn;" : u"\u00b1", "&bull;" : u"\u2022",
                   "&sup1;" : u"\u00b9", "&sup2;" : u"\u00b2", "&sup3;" : u"\u00b3",
                   "&Aacute;" : u"\u00c1", "&cent;" : u"\u00a2", "&oline;" : u"\u203e",
                   "&Beta;" : u"\u0392", "&perp;" : u"\u22a5", "&Delta;" : u"\u0394",
                   "&there4;" : u"\u2234", "&pi;" : u"\u03c0", "&iota;" : u"\u03b9",
                   "&scaron;" : u"\u0161", "&euml;" : u"\u00eb", "&notin;" : u"\u2209",
                   "&iacute;" : u"\u00ed", "&para;" : u"\u00b6", "&epsilon;" : u"\u03b5",
                   "&weierp;" : u"\u2118", "&uuml;" : u"\u00fc", "&larr;" : u"\u2190",
                   "&icirc;" : u"\u00ee", "&Upsilon;" : u"\u03a5", "&omicron;" : u"\u03bf",
                   "&upsilon;" : u"\u03c5", "&copy;" : u"\u00a9", "&Iuml;" : u"\u00cf",
                   "&Oacute;" : u"\u00d3", "&Xi;" : u"\u039e", "&ensp;" : u"\u2002",
                   "&ccedil;" : u"\u00e7", "&Ucirc;" : u"\u00db", "&cap;" : u"\u2229",
                   "&mu;" : u"\u03bc", "&empty;" : u"\u2205", "&lsquo;" : u"\u2018",
                   "&isin;" : u"\u2208", "&Zeta;" : u"\u0396", "&minus;" : u"\u2212",
                   "&loz;" : u"\u25ca", "&deg;" : u"\u00b0", "&and;" : u"\u2227",
                   "&tau;" : u"\u03c4", "&pound;" : u"\u00a3", "&curren;" : u"\u00a4",
                   "&int;" : u"\u222b", "&ucirc;" : u"\u00fb", "&rfloor;" : u"\u230b",
                   "&crarr;" : u"\u21b5", "&ugrave;" : u"\u00f9", "&exist;" : u"\u2203",
                   "&cong;" : u"\u2245", "&theta;" : u"\u03b8", "&oplus;" : u"\u2295",
                   "&permil;" : u"\u2030", "&Acirc;" : u"\u00c2", "&piv;" : u"\u03d6",
                   "&Euml;" : u"\u00cb", "&Phi;" : u"\u03a6", "&Iacute;" : u"\u00cd",
                   "&Uacute;" : u"\u00da", "&Omicron;" : u"\u039f", "&ne;" : u"\u2260",
                   "&iquest;" : u"\u00bf", "&eta;" : u"\u03b7", "&yacute;" : u"\u00fd",
                   "&Rho;" : u"\u03a1", "&darr;" : u"\u2193", "&Ecirc;" : u"\u00ca",
                   "&zeta;" : u"\u03b6", "&Omega;" : u"\u03a9", "&acirc;" : u"\u00e2",
                   "&sim;" : u"\u223c", "&phi;" : u"\u03c6", "&sigmaf;" : u"\u03c2",
                   "&macr;" : u"\u00af", "&thetasym;" : u"\u03d1", "&Ccedil;" : u"\u00c7",
                   "&ordm;" : u"\u00ba", "&uArr;" : u"\u21d1", "&forall;" : u"\u2200",
                   "&beta;" : u"\u03b2", "&fnof;" : u"\u0192", "&cup;" : u"\u222a",
                   "&rho;" : u"\u03c1", "&micro;" : u"\u00b5", "&eacute;" : u"\u00e9",
                   "&omega;" : u"\u03c9", "&middot;" : u"\u00b7", "&Gamma;" : u"\u0393",
                   "&euro;" : u"\u20ac", "&lang;" : u"\u2329", "&spades;" : u"\u2660",
                   "&rsquo;" : u"\u2019", "&thorn;" : u"\u00fe", "&ouml;" : u"\u00f6",
                   "&or;" : u"\u2228", "&raquo;" : u"\u00bb", "&Lambda;" : u"\u039b",
                   "&part;" : u"\u2202", "&sect;" : u"\u00a7", "&ldquo;" : u"\u201c",
                   "&hearts;" : u"\u2665", "&sigma;" : u"\u03c3", "&oacute;" : u"\u00f3" }

    @staticmethod
    def convertHtmlToXml(html):
        htmlCleanup = HtmlCleanup()
        # HtmlCleanup.xhtml_entities
        def testReplace(m):
            s = m.group()
            s = HtmlCleanup.xhtml_entities.get(s, s)
            return s
        html = re.sub(r"\&[^;\s]+\;", testReplace, html)
        html = htmlCleanup.__putInvalidDivToBody(html)    #for cmap html
        xml = htmlCleanup.convertToXml(html)
        try:
            xml = xml.encode("utf8")
        except:
            pass
        return xml
    
    def __putInvalidDivToBody(self, html):
        #this is a dirty code created to avoid manual process for the cmap html file
        #### QUESTION: do we need to write back the valid html to the file?? 
        htmlTag = html
        htmlString = html.replace("</HTML>", "</html>").replace("</BODY>", "</body>")
        htmlArray = htmlString.split("</html>")  #cmap usually using capital letters
        
        if (len(htmlArray)==2):
            divTag = htmlArray[1].strip()
            if divTag != "":
                htmlTag = htmlArray[0].replace("</body>", "")
                htmlTag = "%s%s</body></html>" % (htmlTag, divTag)
                
                #### fix up java script so cmap will be displayed in firefox
                #document.getElementById(popupName).style.left = event.layerX;
                #document.getElementById(popupName).style.top = event.layerY;
                
                htmlTag = htmlTag.replace("document.getElementById(popupName).style.left = event.layerX;", "document.getElementById(popupName).style.left = event.layerX + 'px';")
                htmlTag = htmlTag.replace("document.getElementById(popupName).style.top = event.layerY;", "document.getElementById(popupName).style.top = event.layerY + 'px';")
        return htmlTag
    
    @staticmethod
    def cleanup(html):
        htmlCleanup = HtmlCleanup()
        r = htmlCleanup.convertToXml(html)
        return r
    
    
    def __init__(self):
        # not block element inside 'p' elements
        self.__notNestedInLists = {"p":["p"], "div":["p"]}
        self.__notNestedInLists = {"p":[], "div":[]}
        self.__emptyElements = {}
        self.AddEmptyElement("meta")
        self.AddEmptyElement("link")
        self.AddEmptyElement("br")
        self.AddEmptyElement("hr")
        self.AddEmptyElement("input")
        self.AddEmptyElement("img")
        
        self.AddEmptyElement("META")
        self.AddEmptyElement("LINK")
        self.AddEmptyElement("BR")
        self.AddEmptyElement("HR")
        self.AddEmptyElement("INPUT")
        self.AddEmptyElement("IMG")
    
    def AddEmptyElement(self, tag):
        self.__emptyElements[tag] = tag
    
    @property
    def notNestedInLists(self):
        return self.__notNestedInLists
    
    def convertToXml(self, html, startTagName=None):
        self.__nodes = []
        self.__htmlInput = HtmlInput(html)
        while True:
            node = self.__htmlInput.getNode()
            if node is None:
                break
            self.__nodes.append(node)
        
        # Get xml results
        documentNode = None
        stack = []          # append() and pop()
        xmlStrs = []
        
        # now process all the nodes
        skipNextNode=False
        for x in xrange(len(self.__nodes)):
            if skipNextNode:
                skipNextNode=False
                continue
            node = self.__nodes[x]
            # Test for the start of the document
            if documentNode is None:
                if node.nodeType==NodeType.StartElement or \
                        node.nodeType==NodeType.EmptyElement:
                    if startTagName is None or startTagName==node.name:
                        documentNode = node
                    else:
                        continue
                elif node.nodeType==NodeType.Text or \
                        node.nodeType==NodeType.EndElement or \
                        node.nodeType==NodeType.Comment:
                    continue        # continue until we find a document (start) node
            
            if node.nodeType==NodeType.StartElement or \
                    node.nodeType==NodeType.EmptyElement:
                if node.nodeType==NodeType.StartElement:
                    # Test to see if this StartElement should be just an EmptyElement
                    try:
                        nextNode = self.__nodes[x+1]
                    except:
                        nextNode = None
                    if nextNode is not None and \
                            nextNode.nodeType==NodeType.EndElement and \
                            nextNode.name==node.name:
                        # Then change this to an EmptyElement NodeType
                        node.nodeType = NodeType.EmptyElement
                        #x += 1
                        skipNextNode=True
                    elif self.__emptyElements.has_key(node.name):
                        # Then change this to an EmptyElement NodeType
                        node.nodeType = NodeType.EmptyElement
                                        
                # Do for StartElements and EmptyElements
                # do not nest some elements within other elements e.g. do not nest p inside of p's
                notToBeNestedInList = self.__notNestedInLists.get(node.name, [])
                for nName in notToBeNestedInList:
                    while stack.count(nName):
                        name = stack.pop()
                        n = Node(NodeType.EndElement, name, None)
                        xmlStrs.append(n.asXml)
                if node.nodeType==NodeType.StartElement:
                    # push its name on the stack for later closing
                    stack.append(node.name)
            elif node.nodeType==NodeType.EndElement and \
                    self.__emptyElements.has_key(node.name):
                continue        # just ignore it
            elif node.nodeType==NodeType.EndElement:
                if stack.count(node.name):
                    while True:
                        name = stack.pop()
                        n = Node(NodeType.EndElement, name, None)
                        if name==node.name:
                            break
                        else:
                            xmlStrs.append(n.asXml)
                else:
                    # ignore invalid closing tags
                    continue
                if stack==[] and documentNode.name==node.name:
                    xmlStrs.append(node.asXml)
                    break
            xmlStrs.append(node.asXml)
        
        while len(stack):
            name = stack.pop()
            n = Node(NodeType.EndElement, name, None)
            xmlStrs.append(n.asXml)
        
        xmlStr = "".join(xmlStrs)
        data = xmlStr.replace("&nbsp;", "&#160;")
        
        # HACK  - does this belong here ??????  - I think not, but where?
        # test of encoding  e.g. "windows-1252"
        #       data.decode("windows-1252").encode("utf-8")
        self.__encoding = None
        cpattern = re.compile("<meta\s+[^>]*?(?P<q>'|\")Content-Type(?P=q)[^>]*>", \
                re.IGNORECASE)
        data = re.sub(cpattern, self.__processMeta, data)
        #print "encoding='%s'" % self.__encoding
        if self.__encoding is not None:
            try:
                data = data.decode(self.__encoding).encode("utf-8")
            except:
                pass
        
        return data
    
    
    def __processMeta(self, m):
        s = m.group()
        pattern = "content\s*=\s*(?P<q>'|\").*?charset\s*=\s*([^\s]*).*?(?P=q)"
        cpattern = re.compile(pattern, re.IGNORECASE)
        if len(m.groups())>1:
            self.__encoding = m.groups()[1]
            s = s.replace(self.__encoding, "utf-8")
        else:
            s = re.sub(cpattern, self.__processMeta, s)
        #print "s='%s'" % s
        return s


    
    
