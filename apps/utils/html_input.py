
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

import types
import re



class NodeType(object):
    Unknown = "Unknown"
    XmlDeclaration = "XmlDeclaration"      # <?xml
    StartElement = "StartElement"          # <Alpha
    EmptyElement = "EmptyElment"            # 
    EndElement = "EndElement"              # </Alpah
    Comment = "Comment"                    # <!--
    CDATA = "CDATA"                        # <!CDATA[ ...]]>
    PI = "PI"                              # <?
    Text = "Text"                          # 
    MsoDeclaration = "MsoDeclaration"      # <![Xxxx]>
    Declaration = "Declaration"            # <!DOCTYPE or what ever >
    #Entity                 # &Aplha; &#Num; &#xHex;



class HtmlInput(object):
    def __init__(self, html):
        self.__data = html
        self.__pos = 0
        self.__len = len(html)
        
    
    def getNode(self):
        if self.__isEOI:
            return None
        nodeType = self._getNodeType()
        if nodeType==NodeType.StartElement or nodeType==NodeType.EmptyElement:
            node = self.__getElementNode()
        elif nodeType==NodeType.EndElement:
            node = self.__getEndElementNode()
        elif nodeType==NodeType.PI:
            node = self.__getPINode()
        elif nodeType==NodeType.Comment:
            node = self.__getCommentNode()
        elif nodeType==NodeType.CDATA:
            node = self.__getCDataNode()
        elif nodeType==NodeType.Text:
            node = self.__getTextNode()
        elif nodeType==NodeType.MsoDeclaration:
            node = self.__getMsoDeclarationNode()
        elif nodeType==NodeType.Declaration:
            node = self.__getDeclarationNode()
        else:
            raise Exception("Unknown NodeType '%s'" % nodeType)
        return node
    
    def _getNodeType(self):
        nodeType = NodeType.Text    # Default
        nChar = self.__nextChar
        if nChar=="<":
            self.__remove(1)
            nChar = self.__nextChar
            if self.__isAlpha(nChar):   # Element
                nodeType = NodeType.StartElement
            elif nChar=="?":
                nodeType = NodeType.PI
            elif nChar=="/":            # </
                self.__remove(1)
                if self.__isAlpha(self.__nextChar):
                    nodeType = NodeType.EndElement
                self.__pos -= 1
            elif nChar=="!":
                if self.__assert("!--"):
                    nodeType = NodeType.Comment
                elif self.__assert("![CDATA["):
                    nodeType = NodeType.CDATA
                elif self.__assert("!["):
                    nodeType = NodeType.MsoDeclaration
                else:
                    nodeType = NodeType.Declaration
            self.__pos -= 1
        return nodeType
    
    def __getElementNode(self):
        atts = {}
        attList = []
        name = None
        nodeType = NodeType.Unknown
        
        if not self.__assert("<"):
            raise Exception("Expected a '<' character!")
        pos = self.__pos
        self.__remove(1)
        name = self.__getElementName()
        text = None
        # get attributes
        while self.__isNotEOI:
            nChar = self.__nextChar
            if nChar==">":
                self.__remove(1)
                nodeType = NodeType.StartElement
                break
            elif nChar=="<":
                # Error/Exception this is not an element after all it is just text!
                #  restore self.__pos and return a textNode
                self.__pos = pos + 1
                nodeType = NodeType.Text
                name = None
                text = "<" + self.__getText()
                attList = []
                break
            elif nChar=="/":
                if self.__assert("/>"):
                    self.__remove(2)
                    nodeType = NodeType.EmptyElement
                    break
                else:
                    self.__remove(1)    # just ignore it
            elif self.__isAlpha(nChar):
                attName = self.__getAttributeName()
                if self.__assert("="):
                    self.__remove(1)
                    attValue = self.__getAttributeValue()
                else:
                    attValue = attName
                #
                count = 2
                if atts.has_key(attName):
                    pass
                att = Attribute(attName, attValue)
                atts[attName] = att
                attList.append(att)
            else:
                self.__remove(1)
        return Node(nodeType, name, text, attList)
    
    def __getEndElementNode(self):
        if not self.__assert("</"):
            raise Exception("Expected '</'!")
        self.__remove(2)
        name = self.__getElementName()
        self.__getUpto(">")
        return Node(NodeType.EndElement, name, None)
    
    def __getPINode(self):
        if not self.__assert("<?"):
            raise Exception("Expected '<?'!")
        self.__remove(2)
        value = self.__getUpto("?>")
        name = value.split()[0]
        return Node(NodeType.PI, name, value)
    
    def __getCommentNode(self):
        if not self.__assert("<!--"):
            raise Exception("Expected '<!--'!")
        self.__remove("<!--")
        return Node(NodeType.Comment, None, self.__getUpto("-->"))
    
    def __getTextNode(self):
        return Node(NodeType.Text, None, self.__getText())
    
    def __getCDataNode(self):
        if not self.__assert("<![CDATA["):
            raise Exception("Expected '<![CDATA['!")
        self.__remove("<![CDATA[")
        data = self.__getUpto("]]>")
        return Node(NodeType.CDATA, None, data)
    
    def __getMsoDeclarationNode(self):
        if not self.__assert("<!["):
            raise Exception("Expected '<!['!")
        self.__remove("<![")
        data = self.__getUpto("]>")
        return Node(NodeType.MsoDeclaration, None, data)
    
    def __getDeclarationNode(self):
        if not self.__assert("<!"):
            raise Exception("Expected '<!'!")
        self.__remove("<!")
        data = self.__getUpto(">")
        return Node(NodeType.Declaration, None, data)
    
    @property
    def __isEOI(self):
        return self.__pos >= self.__len
    
    @property
    def __isNotEOI(self):
        return self.__pos < self.__len
    
    @property
    def __nextChar(self):
        if self.__isEOI:
            return ""
        return self.__data[self.__pos]
    
    @property
    def __isNextAlpha(self):
        if self.__isNotEOI:
            c = self.__nextChar
            if self.__isAlpha(c):
                return True
        return False
    
    def __assert(self, s):
        return self.__data[self.__pos: self.__pos+len(s)]==s
    
    def __getElementName(self):
        name = self.__getName()
        self.__removeWhitespace()
        return name
    
    def __getAttributeName(self):
        name = self.__getName()
        self.__removeWhitespace()
        return name
    
    def __getAttributeValue(self):
        self.__removeWhitespace()
        nChar = self.__nextChar
        if nChar=="'" or nChar=='"':
            self.__remove(1)
            s = self.__getUpto(nChar)
        else:
            s = self.__getUptoWhitespaceOr(">")
            if s.endswith("/"):         # backup one
                s = s[:-1]
                self.__pos-=1
        self.__removeWhitespace()
        return s
    
    def __getName(self):
        start = self.__pos
        if self.__isNextAlpha:
            while self.__isNotEOI:
                c = self.__nextChar
                if c.isalnum() or c==":" or c=="." or c=="_" or c=="-":
                    self.__remove(1)
                else:
                    break
        else:
            return None
        return self.__data[start:self.__pos]
    
    def __getText(self):
        # read upto a <Alpha or </ or <! or <?
        start = self.__pos
        while self.__isNotEOI:
            if self.__nextChar=="<":
                if self._getNodeType()!=NodeType.Text:
                    break
            self.__remove(1)
        return self.__data[start:self.__pos]
    
    def __getUptoWhitespaceOr(self, endStr):
        start = self.__pos
        endChar = endStr[0]
        while self.__isNotEOI:
            nChar = self.__nextChar
            if nChar.isspace():
                break
            if nChar==endChar and self.__assert(endStr):
                break
            self.__remove(1)
        return self.__data[start:self.__pos]
    
    def __getUpto(self, endStr):
        start = self.__pos
        c = endStr[0]
        s = None
        while self.__isNotEOI:
            if self.__nextChar==c:
                if self.__assert(endStr):
                    break
            self.__remove(1)
        s = self.__data[start:self.__pos]
        self.__remove(endStr)
        return s
    
    def __remove(self, num=1):
        if type(num) in types.StringTypes:
            num = len(num)
        self.__pos += num
    
    def __removeWhitespace(self):
        while self.__nextChar.isspace():
            self.__remove(1)
    
    def __isAlpha(self, char):
        return char.isalpha() or char=="_"



class Node(object):
    def __init__(self, nodeType, name, value, attributes=[]):
        if nodeType == NodeType.Unknown:
            raise Exception("Unknown NodeType")
        self.__nodeType = nodeType
        self.__name = name
        self.__value = value
        self.__attributes = attributes
        self.__script = None
    
    def __getNodeType(self):
        return self.__nodeType
    def __setNodeType(self, value):
        self.__nodeType = value
    nodeType = property(__getNodeType, __setNodeType)
    
    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value
    
    @property
    def attributes(self):
        return self.__attributes
    
    @property
    def asXml(self):
        s = ""
        if self.__nodeType==NodeType.StartElement:
            s = "<%s" % self.__name
            for att in self.__attributes:
                value = self.__fullEncodedText(att.value)
                value = value.replace('"', "&quot;")
                s += " %s=\"%s\"" % (att.name, value)
            s += ">"
        elif self.__nodeType==NodeType.EmptyElement:
            s = "<%s" % self.__name
            for att in self.__attributes:
                value = self.__fullEncodedText(att.value)
                value = value.replace('"', "&quot;")
                s += " %s=\"%s\"" % (att.name, value)
            s += "/>"
        elif self.__nodeType==NodeType.EndElement:
            s = "</%s>" % self.__name
        elif self.__nodeType==NodeType.Comment:
            s = "<!--%s-->" % self.__value.replace("--", "==")
        elif self.__nodeType==NodeType.CDATA:
            if self.__script:
                s = "//<![CDATA[\n%s\n//]]>\n" % self.__value
            else:
                s = "<![CDATA[%s]]>" % self.__value
        elif self.__nodeType==NodeType.PI:
            s = "<?%s?>" % (self.__value)
        elif self.__nodeType==NodeType.Text:
            s = self.__fullEncodedText(self.__value)
        elif self.__nodeType==NodeType.MsoDeclaration:
            value = self.__fullEncodedText(self.__value)
            value = value.replace('"', "&quot;")
            s = "<mso-declaration value=\"%s\" />" % value
        elif self.__nodeType==NodeType.Declaration:
            s = "<!%s>" % self.__value
            s = ""      # ignore for now  Note: not valid in an xml document
        else:
            raise Exception("Unsupported NodeType '%s'" % self.__nodeType)
        return s
    
    def __str__(self):
        return self.asXml
    
    def __fullEncodedText(self, s):
        s = self.__cleanUpAmps(s)
        #s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        return s
    
    def __cleanUpAmps(self, s):
        # replace any missing ';'  e.g. &#160
        def repl(match):
            return match.groups()[0] + ";"
        sub = re.sub(r"(\&\#\d+)(?!;)(?!\d)", repl, s)
        
        pattern = r"\&"                          # find '&'
        pattern += r"(?!\#\d+\;)"                # not followed by #Digits
        pattern += r"(?!\#(x|X)[0-9a-fA-F]+\;)"  # not followed by #xHex;
        pattern += r"(?!\w+\;)"                  # not followed by a name
        sub = re.sub(pattern, "&amp;", sub)
        return sub



class Attribute(object):
    def __init__(self, name, value):
        self.__name = name
        self.__value = value
    
    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value
    
    def __str__(self):
        value = self.__escapeXml(self.__value)
        return '%s="%s"' % (self.__name, value.replace('"', "&quot;"))
    
    def __escapeXml(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")













