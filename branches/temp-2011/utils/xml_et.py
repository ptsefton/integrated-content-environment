
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

try:
    from xml.etree import ElementTree as ElementTree
except ImportError:
    try:
        import ElementTree as ElementTree
    except ImportError:
        try:
            from elementtree import ElementTree
        except ImportError:
            raise ImportError("Error loading ElementTree! Please install and try again.")


class ETXML(object):
    ## What about thread safty?  particularly with the usage of the blankns
    class ExtendElementTree(object):
        # extend ElementTree
        def __init__(self):
            ElementTree._ElementInterface.tostring = ElementTree.tostring
            ElementTree._ElementInterface.__str__ = ElementTree.tostring
            #ElementTree._ElementInterface.ns = self.__ooons
            ElementTree._ElementInterface.makens = self.makens
            ElementTree._ElementInterface.findns = self.findns
            ElementTree._ElementInterface.findallns = self.findallns
            ElementTree._ElementInterface.makeelementns = self.makeelementns
            self.ns = {}
            self.blankns = ""
        
        def addNamespaces(self, ns={}):
            for key, value in ns.iteritems():
                Elementtree._namespace_map[value] = key
                self.ns[key] = "{%s}" % value
                if key=="":
                    self.blankns = "{%s}" % value                
        
        def makens(self, str):
            def mReplace(m):
                m = m.group()
                return self.ns.get(m[:-1], m)
            if str.find(":")>-1:
                return re.sub("\w+\:", mReplace, str)
            else:
                return self.blankns + str
        def findns(self, et, xpath):
            return et.find(self.makens(xpath))
        def findallns(self, et, xpath):
            return et.findall(self.makens(xpath))
        def makeelementns(self, et, elemName, attr={}):
            return et.makeelement(self.makens(elemName), attr)
        
    __extendElementTree = ETXML.ExtendElementTree()
    
    @staticmehtod
    def addNamespaces(ns={}):
        pass
    
    ## Wrapped Element
    class Element(object):
        def __init__(self, elem, parentElem=None, rootElem=None):
            pass
    
    def __init__(self, xml, ns={}):
        self.__xml = None
        self.__parents = {}
        try:
            if xml.startswith("<"):
                self.__xml = ElementTree.XML(xml)
            else:
                self.__xml = ElementTree.parse(xml)
        except Exception, e:
            # try cleaning up the xml with HtmlCleanup and try again
            raise
        self.__getParents(self.__xml)
    
    @property
    def rootElement(self):
        return ETXML.Element(self.__xml, None, self.__xml)
    
    def __getParents(self, elem):
        for c in elem.getchildren():
            self.__parents[c] = elem
            self.__getParents(c)
    
    
    
##class _Node(object):
    # Constructor
    #   
    # Properties
    #   
    #   
    # Methods
    #    getType()
    #    isElement()
    #    getName()
    #    setName(name)
    #    getNode(xpath)
    #    getNodes(xpath)
    #    getFirstChild()
    #    getLastChild()
    #    getNextSibling()
    #    getPrevSibling()
    #    getParent()
    #    getChildren()
    #    copy()
    #    getAttributes()
    #    getAttribute(name)
    #    setAttribute(name, content)
    #    removeAttribute(name)
    #    setRawContent(rawText)
    #    setContent(text)
    #    addRawContent(text)
    #    addContent(text)
    #    getContent(xpath=None)
    #    getContents(xpath=None)
    #    addChild(node)
    #    addChildren(nodeList)
    #    addNextSibling(node)
    #    addPrevSibling(node)
    #    delete()
    #    remove()
    #    replace(nodeOrNodeList)
    #    serialize(format=True)
    #    __str__()

##class xml(_Node):
    # Note: extends the _Node class
    # Constructor
    #   __init__(xmlcontent, nsList=None, parseAsHtml=False, dom=None)
    # Properties
    #   fileName
    #   isHtml
    #   nsList
    #   
    # Methods
    #   close()
    #   addNamespaceList(nsList)
    #   getRootNode()
    #   createElement(elementName, elementContent=None, elementNS=None, **args)
    #   createText(content)
    #   createPI(name, content=None)
    #   createComment(content)
    #   addComment(content)
    #   addElement(elementName)
    #   getNode(xpath)  *
    #   getNodes(xpath)  *
    #   getContents(xpath)  *
    #   xmlStringToElement(xmlString)
    #   xmlStringToNodeList(xmlString)
    #   applyXslt(xslt)
    #   saveFile(fileName=None)
    ## Plus the following inherited methods  
    #    getType()
    #    isElement()
    #    getName()
    #    setName(name)
    #    getNode(xpath) - overriden
    #    getNodes(xpath) - overriden
    #    getFirstChild()
    #    getLastChild()
    #    getNextSibling()
    #    getPrevSibling()
    #    getParent()
    #    getChildren()
    #    copy()
    #    getAttributes()
    #    getAttribute(name)
    #    setAttribute(name, content)
    #    removeAttribute(name)
    #    setRawContent(rawText)
    #    setContent(text)
    #    addRawContent(text)
    #    addContent(text)
    #    getContent(xpath=None)
    #    getContents(xpath=None)  - overriden
    #    addChild(node)
    #    addChildren(nodeList)
    #    addNextSibling(node)
    #    addPrevSibling(node)
    #    delete()
    #    remove()
    #    replace(nodeOrNodeList)
    #    serialize(format=True)
    #    __str__()
    #   



