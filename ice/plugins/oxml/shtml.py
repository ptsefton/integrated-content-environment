#!/usr/bin/env python
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

"""  """

import string
import types
import urllib
from xml.sax.saxutils import escape, quoteattr  #, unescape
from xml.dom.minidom import parseString


# List of HTML5 void elements
# area, base, br, col, command, embed, hr, img, input, keygen, link, meta, param, source
#  void elements may be self closing e.g. <hr /> but can not have a closing tag
#       e.g. <hr></hr>
#  non-void elements e.g. p
#   must not be self closing e.g. can not be <p />
#   but must be <p></p>

HTML5VoidElements = ["area", "base", "br", "col", "command", "embed", "hr",
        "img", "input", "keygen", "link", "meta", "param", "source"]

#class Attribute(object):
    # Constructon(name, value)
    # Properties:
    #    name         (R/W)
    #    value        (R/W)
    #    quotedValue  (ReadOnly)
    # Methods:
    #
#class Style(object):
    # Constructor(name, value)
    # Properties:
    #    name         (R/W)
    #    value        (R/W)
    # Methods:
    #    __str__
#class Node(object):                # Not used directly
    # Contructor(type, parent)
    # Properties:
    #    type        (ReadOnly)
    #    name        (ReadOnly)
    #    atts        (ReadOnly)
    #    items       (ReadOnly)
    #    value       (ReadOnly)
    #    parent      (R/W)
    # Methods:
    #    getNextNode()
    #    getNextElementNode()
    #
#class Element(Node):
    # Constructor(*args, **kwargs)
    #   e.g. Element("div", "text contents", attName=2, {"name":"test", "class":"hi"})
    # Properties:
    #    name          (ReadOnly)
    #    localName     (ReadOnly)
    #    atts          (ReadOnly)
    #    items         (ReadOnly)
    #    value         (ReadOnly)
    # Methods:
    #    addAttribute(name, value=None)
    #    setAttribute(name, value=None)
    #    getAttribute(name)
    #    remove(node)
    #    addChild(node)
    #    addChildElement(*args, **kwargs) - same argument options as this class
    #    getNextNode(node=None)
    #    __str__()
#class Text(Node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
#class RawText(Node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
#class Comment(Node):
    # Constructor(value="")
    # Properties:
    #   value       (ReadOnly)
    # Methods:
    #   __str__()


# types.StringType, types.UnicodeType, types.StringTypes(str & unicode types)
# under IronPython both StringType & UnicodeType are the same type.
from types import StringType, UnicodeType, StringTypes
import sys
if sys.platform=="cli":     # IronPython
    # every thing as a unicode string
    def asString(s):
        if type(s) is not StringType:
            s = unicode(s)
        return s
else:                       # cPython
    # every thing as utf-8 encoded str (or unicode)
    def asString(s):
        t = type(s)
        if t is StringType:
            pass
        elif t is UnicodeType:
            s = s.encode("utf-8")
        else:
            s = str(s)
        return s



class Shtml(object):
    # Constructor()
    # Properties:
    #   title
    #   head    (ReadOnly Element)
    #   body    (ReadOnly Element)
    # Methods:
    #   addStyle(s, value=None)
    #   formatted(includeXmlDec=False, includeDocType=True)
    #   toString(includeXmlDec=False, includeDocType=True)
    #   createStyle(name, value)
    #   createElement(*args, **kwargs)
    #   createAttribute(name, value, parent=None)
    #   createText(value, parent=None)
    #   createRawText(value, parent=None)
    #   createComment(value, parent=None)
    #   formatted(includeXmlDec=False, includeDocType=True)
    #   toString(includeXmlDec=False, includeDocType=True)
    #   __str__()
    def __init__(self):
        self.styles = []
        self.__html = Element("html")
        self.__head = Element("head")
        self.__title = Element("title")
        self.__style = Element("style")
        self.__style.setAttribute("type", "text/css")
        self.__body = Element("body")
        self.__html.setAttribute("xmlns", "http://www.w3.org/1999/xhtml")
        self.__html.addChild(self.__head)
        self.__html.addChild(self.__body)
        
        meta = Element("meta")
        meta.setAttribute("http-equiv", "Content-Type")
        meta.setAttribute("content", "text/html; charset=UTF-8")
        self.__head.addChild(meta)
        self.__head.addChild(self.__title)
        self.__head.addChild(self.__style)


    def __getTitle(self):
        return self.__title.value
    def __setTitle(self, value):
        items = self.__title.items
        for item in items:
            self.__title.remove(item)
        self.__title.addChild(value)
    title = property(__getTitle, __setTitle)


    @property
    def head(self):
        return self.__head

    @property
    def body(self):
        return self.__body

    def addStyle(self, s, value=None):
        if isinstance(s, Style):
            self.styles.append(s)
        elif type(s) is types.StringType and value is not None:
            st = Style(s, value)
            self.styles.append(st)
        else:
            raise Exception("Invalid arguments!")


    def createStyle(self, name, value):
        return Style(name, value)

    def createElement(self, *args, **kwargs):
        parent = None
        if kwargs.has_key("parent"):
            parent = kwargs.pop("parent")
        n = Element(*args, **kwargs)
        if parent is not None:
            parent.addChild(n)
        return n

    def createAttribute(self, name, value, parent=None):
        a = Attribute(name, value)
        if parent is not None:
            parent.addAttribute(a)
        return a

    def createText(self, value="", parent=None):
        n = Text(value)
        if parent is not None:
            parent.addChild(n)
        return n

    def createRawText(self, value="", parent=None):
        n = RawText(value)
        if parent is not None:
            parent.addChild(n)
        return n

    def createComment(self, value="", parent=None):
        n = Comment(value)
        if parent is not None:
            parent.addChild(n)
        return n


    def formatted(self, includeXmlDec=False, includeDocType=True):
        d = parseString(self.toString(includeXmlDec, includeDocType))
        d.normalize()
        s = d.toprettyxml("  ")
        d.unlink()
        if includeXmlDec==False:
            s = s.split("?>\n", 1)[-1]
        return s


    def toString(self, includeXmlDec=False, includeDocType=True):
        self.__addStyles()
        s = str(self.__html)
        if includeDocType:
             #docType = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
             docType = "<!DOCTYPE html>\n"      # HTML 5
             s = docType + s
        if includeXmlDec:
            xmlDec = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            s = xmlDec + s
        return s


    def __str__(self):
        return self.toString(True, True)

    def __unicode__(self):
        # Note: never called under IronPython
        return str(self).decode("utf-8")
    
    def __addStyles(self):
        for i in self.__style.items:
            self.__style.remove(i)
        s = ""
        for style in self.styles:
            s += str(style) + "\n"
        s = s[:-1]
        #rawText = RawText("<!--\n" + s + "\n-->")
        rawText = RawText("/*<![CDATA[*/\n" + s + "\n/*]]>*/\n" )
        self.__style.addChild(rawText)

    def __addScripts(self):
        #rawText = RawText("<!--//--><![CDATA[//><!--\n" + s + "\n//--><!]]>")
        rawText = RawText("/*<![CDATA[*/\n" + s.replace("]]>", "] ] >") + "\n/*]]>*/\n" )



class Attribute(object):
    # Constructon(name, value)
    # Properties:
    #    name         (R/W)
    #    value        (R/W)
    #    quotedValue  (ReadOnly)
    # Methods:
    
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __getName(self):
        return self.__name
    def __setName(self, name):
        self.__name = asString(name)
    name = property(__getName, __setName)

    def __getValue(self):
        return self.__value
    def __setValue(self, value):
        self.__value = asString(value)
        # Only for href ???
        # if name is contains unicode characters e.g. u'\u2019'
        #self.__value = urllib.quote(value).replace("%3A", ":")
    value = property(__getValue, __setValue)

    @property
    def quotedValue(self):
        return quoteattr(self.__value).replace("'", "&#39;")



class Style(object):
    # Constructor(name, value)
    # Properties:
    #    name         (R/W)
    #    value        (R/W)
    # Methods:
    #    __str__
    
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __getName(self):
        return self.__name
    def __setName(self, name):
        self.__name = asString(name)
    name = property(__getName, __setName)

    def __getValue(self):
        return self.__value
    def __setValue(self, value):
        self.__value = asString(value)
    value = property(__getValue, __setValue)

    def __str__(self):
        s = "%s {%s}" % (self.name, self.value)
        return s



class Node(object):
    # Contructor(type, parent)
    # Properties:
    #    type        (ReadOnly)
    #    name        (ReadOnly)
    #    atts        (ReadOnly)
    #    items       (ReadOnly)
    #    value       (ReadOnly)
    #    parent      (R/W)
    #    tag
    # Methods:
    #    getNextNode()
    #    getNextElementNode()
    #    
    
    def __init__(self, type, parent):
        self.__parent = parent
        self.__setType(type)
        self.tag = None
        self.tagLevel = None
        
    def __getType(self):
        return self.__type
    def __setType(self, type):
        if type=="text" or type=="element" or type=="comment":
            self.__type=type
        else:
            raise Exception("Unknown type '%s'" % type)
    type = property(__getType)

    def __getParent(self):
        return self.__parent
    def __setParent(self, value):
        if isinstance(value, Node) or value is None:
            if self.__parent is not None:
                self.__parent.remove(self)
            self.__parent = value
        else:
            raise Exception("parent can only be set to a Node type or None!")
    parent = property(__getParent, __setParent)

    @property
    def name(self):
        return None

    @property
    def atts(self):
        return {}

    @property
    def items(self):
        return []

    @property
    def value(self):
        return ""

    def getNextNode(self):
        return self.parent.getNextNode(self)

    def getNextElementNode(self):
        n = self.getNextNode()
        while not isinstance(n, Element):
            if n is None:
                break
            n.getNextNode()
        return n

    def __str__(self):
        return "[NODE object (__str__ should have been overriden!)]"


class Element(Node):
    # Constructor(*args, **kwargs)
    #   e.g. Element("div", "text contents", attName=2, {"name":"test", "class":"hi"})
    # Properties:
    #    name          (Read/Write)
    #    localName     (ReadOnly)
    #    atts          (ReadOnly)
    #    items         (ReadOnly)   children
    #    value         (ReadOnly)
    #    text          (ReadOnly)
    # Methods:
    #    addAttribute(name, value=None)
    #    setAttribute(name, value=None)
    #    getAttribute(name)
    #    remove(node=None)
    #    addChild(node)
    #    addChildElement(*args, **kwargs) - same argument options as this class
    #    getNextNode(node=None)
    #    prepend(n)
    #    getFirstChild()
    #    getChildren()
    #    getLastChild()
    #    __str__()

    def __init__(self, *args, **kwargs):
        Node.__init__(self, "element", None)
        if len(args)==0:
            raise Exception("atleast one 'element name' argument required!")
        self.__name = asString(args[0])
        self.__atts = {}
        self.__items = []
        for k, v in kwargs.iteritems():
            self.addAttribute(k, v)
        for arg in args[1:]:
            if type(arg) is types.DictType:
                for k, v in arg.iteritems():
                    self.addAttribute(k, v)
            else:
                self.addChild(arg)

    def __getName(self):
        return self.__name
    def __setName(self, name):
        self.__name = asString(name)
    name = property(__getName, __setName)

    @property
    def localName(self):
        n = self.__name
        return n[n.find(":")+1:]

    @property
    def atts(self):
        return self.__atts

    @property
    def items(self):
        return self.__items

    @property
    def children(self):
        return self.__items

    @property
    def value(self):
        value = ""
        if self.__name=="br":
            value = "\n"
        for item in self.__items:
            if not isinstance(item, Comment):
                value += item.value
        return value

    @property
    def text(self):
        t = ""
        for c in self.__items:
            if isinstance(c, Text):
                t += c.value
        return t

    
    def addAttribute(self, name, value=None):
        self.setAttribute(name, value)
        return self
    
    def setAttribute(self, name, value=None):
        if isinstance(name, Attribute):
            self.__atts[name.name] = name
        elif type(name) is types.StringType and value is not None:
            att = Attribute(asString(name), asString(value))
            self.__atts[att.name] = att
        else:
            raise Exception("Invalid arguments!")
        return self
    
    def getAttribute(self, name):
        a = self.__atts.get(asString(name), None)
        if a is not None:
            a = a.value
        return a
    
    def remove(self, n=None):
        if n is None:
            p = self.parent
            if p is not None:
                p.remove(self)
            return self
        x = self.__items.remove(n)
        return x
    
    def addChild(self, n):
        if isinstance(n, Node):
            n.parent = self
            self.__items.append(n)
        else:
            textNode = Text(n, parent=self)
            self.__items.append(textNode)
        return self

    def addChildElement(self, *args, **kwargs):
        n = Element(*args, **kwargs)
        self.addChild(n)
        return n

    def prepend(self, n):
        if isinstance(n, Node):
            n.parent = self
        else:
            n = Text(n, parent=self)
        self.__items.insert(0, n)
        return self
    
    def getNextNode(self, n=None):
        if n is not None:
            x = self.__items.index(n)
            if x < len(self.__items):
                return self.__items[x+1]
        if self.parent is None:
            return None
        else:
            return self.parent.getNextNode(self)

    def getFirstChild(self):
        if len(self.__items) > 0:
            return self.__items[0]
        return None
    
    def getChildren(self):
        nodes = []
        for item in self.__items:
            nodes.append(item)
        return nodes
    
    def getLastChild(self):
        itemSize = len(self.__items) -1
        if itemSize > 0:
            return self.__items[itemSize]
        elif itemSize == 0:
            return self.__items[0]
        return None     


    def __str__(self):
        name = self.name
        if self.__items==[]:
            if name in HTML5VoidElements:
                s = "<%s%s />" % (name, self.__getAttributes())
            else:
                s = "<%s%s></%s>" % (name, self.__getAttributes(), name)
        else:
            ss = []
            for item in self.__items:
                ss.append(str(item))
            s = string.join(ss, "")
            s = "<%s%s>%s</%s>" % (name, self.__getAttributes(), s, name)
        return s

    def __getAttributes(self):
        s = ""
        if self.__atts=={}:
            s = ""
        else:
            keys = self.__atts.keys()
            keys.sort()
            for key in keys:
                s += " %s=%s" % (key, self.__atts[key].quotedValue)
        return s


class Text(Node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
    
    def __init__(self, value="", parent=None):
        Node.__init__(self, "text", parent)
        self.__value = asString(value)

    @property
    def value(self):
        return self.__value

    @property
    def name(self):
        return "[TextNode]"

    def __str__(self):
        s = escape(self.__value)
        return s


class RawText(Node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
    
    def __init__(self, value="", parent=None):
        Node.__init__(self, "text", parent)
        self.__value = asString(value)

    @property
    def value(self):
        return self.__value

    @property
    def name(self):
        return "[RawTextNode]"

    def __str__(self):
        return self.__value


class Comment(Node):
    # Constructor(value="", parent=None)
    # Properties:
    #   value       (ReadOnly)
    # Methods:
    #   __str__()
    def __init__(self, value="", parent=None):
        Node.__init__(self, "comment", parent)
        self.__value = asString(value)

    @property
    def value(self):
        return self.__value
    
    def __str__(self):
        return "<!--" + self.__value + "-->"



def test():
    s = Shtml()
    s.title = "TestTitle"
    s.body.addChild(s.createElement("div", "testing", {"class":"test"}, a=5))
    span = s.body.addChildElement("span", "Test text")
    comment = s.createComment("a test comment")
    s.body.addChild(comment)
    s.createComment("testComment", parent=s.body)

    print s
    print "---"
    print s.formatted(False)


if __name__=="__main__":
    test()


