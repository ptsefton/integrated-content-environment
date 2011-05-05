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
from xml.sax.saxutils import escape, unescape, quoteattr
from xml.dom.minidom import parseString


class shtml(object):
    def __init__(self):
        self.styles = []
        self.__html = element("html")
        self.__head = element("head")
        self.__title = element("title")
        self.__style = element("style")
        self.__style.setAttribute("type", "text/css")
        self.__body = element("body")
        self.__html.setAttribute("xmlns", "http://www.w3.org/1999/xhtml")
        self.__html.addChild(self.__head)
        self.__html.addChild(self.__body)
        
        meta = element("meta")
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
        
    def __getBody(self):
        return self.__body
    body = property(__getBody)

    def addStyle(self, s, value=None):
        if isinstance(s, style):
            self.styles.append(s)
        elif type(s) is types.StringType and value is not None:
#            if s.startswith("bq") or s.startswith("li") or (s.startswith("h") and s[1].isdigit() and s[2] == "."):
#                s = s.replace(".", "_")
#                s = "." + s 
            st = style(s, value)
            self.styles.append(st)
        else:
            raise Exception("Invalid arguments!")

    def formatted(self):
        d = parseString(str(self))
        d.normalize()
        s = d.toprettyxml()
        d.unlink()
        return s

    def __str__(self):
        self.__addStyles()
        htmlHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
        #html = "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        #html += "<head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />\n"
        #html +=    "<title></title>\n"
        #html +=     "<style type=\"text/css\"></style>\n"
        #html += "</head>\n"
        #html += "<body></body>\n</html>\n"
        s = htmlHeader + str(self.__html)
        return s
    
    def __addStyles(self):
        for i in self.__style.items:
            self.__style.remove(i)
        s = ""
        for style in self.styles:
            s += str(style) + "\n"
        s = s[:-1]
        self.__style.addChild(s)



class attribute(object):
    # Constructon(name, value)
    # Properties:
    #    name         (R/W)
    #    value        (R/W)
    #    quotedValue  (ReadOnly)
    # Methods:
    #    
    
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __getName(self):
        return self.__name
    def __setName(self, name):
        self.__name = str(name)
    name = property(__getName, __setName)

    def __getValue(self):
        return self.__value
    def __setValue(self, value):
        try:
            self.__value = str(value)
        except:
            # if name is contains unicode characters e.g. u'\u2019'
            self.__value = urllib.quote(value.encode("utf-8")).replace("%3A", ":")
            #print "attribute value='%s'" % self.__value
    value = property(__getValue, __setValue)
    
    def __getQuotedValue(self):
        return quoteattr(self.__value)
    quotedValue = property(__getQuotedValue)



class style(object):
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
        self.__name = str(name)
    name = property(__getName, __setName)

    def __getValue(self):
        return self.__value
    def __setValue(self, value):
        self.__value = str(value)
    value = property(__getValue, __setValue)

    def __str__(self):
        s = "%s {%s}" % (self.name, self.value)
        return s



class node(object):
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
    
    def __init__(self, type, parent):
        self.__parent = parent
        self.__setType(type)
        
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
        if isinstance(value, node) or value is None:
            if self.__parent is not None:
                self.__parent.remove(self)
            self.__parent = value
        else:
            raise Exception("parent can only be set to a node type or None!")
    parent = property(__getParent, __setParent)

    def __getName(self):
        return None
    name = property(__getName)
    
    def __getAtts(self):
        return {}
    atts = property(__getAtts)
    
    def __getItems(self):
        return []
    items = property(__getItems)
    
    def __getValue(self):
        return ""
    value = property(__getValue)

    def getNextNode(self):
        return self.parent.getNextNode(self)

    def getNextElementNode(self):
        n = self.getNextNode()
        while not isinstance(n, element):
            n.getNextNode()
        return n

    def __str__(self):
        return "[NODE object (__str__ should have been overriden!)]"


class element(node):
    # Constructor(name [, value])
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
    #    getNextNode(node=None)
    #    __str__()
    
    def __init__(self, name, value=None, parent=None):
        node.__init__(self, "element", parent)
        self.__name = name
        self.__atts = {}
        self.__items = []
        if value is not None:
            self.addChild(value)

    def __getName(self):
        return self.__name
    name = property(__getName)
    
    def __getLocalName(self):
        n = self.__name
        return n[n.find(":")+1:]
    localName = property(__getLocalName)
    
    def __getAtts(self):
        return self.__atts
    atts = property(__getAtts)
    
    def __getItems(self):
        return self.__items
    items = property(__getItems)
    
    def __getValue(self):
        value = ""
        if self.__name=="br":
            value = "\n"
        for item in self.__items:
            if not isinstance(item, comment):
                value += item.value
        return value
    value = property(__getValue)
    
    def addAttribute(self, name, value=None):
        self.setAttribute(name, value)
    
    def setAttribute(self, name, value=None):
        if isinstance(name, attribute):
            self.__atts[name.name] = name
        elif type(name) is types.StringType and value is not None:
            att = attribute(name, value)
            self.__atts[att.name] = att
        else:
            raise Exception("Invalid arguments!")
    
    def getAttribute(self, name):
        return self.__atts.get(name, None)
    
    def remove(self, n):
        x = self.__items.remove(n)
    
    def addChild(self, n):
        if isinstance(n, node):
            n.parent = self
            self.__items.append(n)
        else:
            if type(n) is types.UnicodeType:
                s = n.encode("utf-8")
            else:
                s = str(n)
            textNode = text(s, parent=self)
            self.__items.append(textNode)
    
    def prepend(self, n):
        if isinstance(n, node):
            n.parent = self
        else:
            if type(n) is types.UnicodeType:
                s = n.encode("utf-8")
            else:
                s = str(n)
            n = text(s, parent=self)
        self.__items.insert(0, n)
    
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
        node = []
        for item in self.__items:
            node.append(item)
        return node
    
    def getLastChild(self):
        itemSize = len(self.__items) -1
        if itemSize > 0:
            return self.__items[itemSize]
        elif itemSize == 0:
            return self.__items[0]
        return None     
        
    
    def __str__(self):
        name = self.name
        if type(name) is types.UnicodeType:
            name = name.encode("utf-8")
        if self.__items==[]:
            s = "<%s%s />" % (name, self.__getAttributes())
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


class text(node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
    
    def __init__(self, value="", parent=None):
        node.__init__(self, "text", parent)
        if type(value) is types.UnicodeType:
            value = value.encode("utf-8")
        self.__value = value
        
    def __getValue(self):
        return str(self.__value)
    value = property(__getValue)

    def __getName(self):
        return "[textNode]"
    name = property(__getName)

    def __str__(self):
        s = escape(self.__value)
        return s


class rawText(node):
    # Constructor(value="")
    # Properties:
    #    value    (ReadOnly)
    #    [name     (ReadOnly)]
    # Methods:
    #    __str__
    
    def __init__(self, value="", parent=None):
        node.__init__(self, "text", parent)
        if type(value) is types.UnicodeType:
            value = value.encode("utf-8")
        self.__value = value
        
    def __getValue(self):
        return str(self.__value)
    value = property(__getValue)

    def __getName(self):
        return "[rawTextNode]"
    name = property(__getName)

    def __str__(self):
        return self.__value


class comment(node):
    def __init__(self, value="", parent=None):
        node.__init__(self, "comment", parent)
        if type(value) is types.UnicodeType:
            value = value.encode("utf-8")
        self.__value = value
        
    def __getValue(self):
        return str(self.__value)
    value = property(__getValue)
    
    def __str__(self):
        return "<!--" + self.__value + "-->"





