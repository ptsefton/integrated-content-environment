
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

""" """

import libxml2
import os
import types
import tempfile


class _Node(object):
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
    
    #   
    #   
    #   
    def __init__(self, node):
        self.__node = node

    def __newNode(self, node):
        if node==None:
            return None
        else:
            return _Node(node)
            
    def getType(self):
        return self.__node.type
        
    def isElement(self):
        return self.__node.type=="element"
        
    def getName(self):
        return self.__node.name
        
    def setName(self, name):
        self.__node.setName(name)

    def getNode(self, xpath):
        nodes = self.__node.xpathEval(xpath)
        if len(nodes)>0:
            return self.__newNode(nodes[0])
    def getNode2(self, xpath):
        nodes = self.__node.xpathEval(xpath)
        if len(nodes)>0:
            return self.__newNode(nodes[0])
        
    def getNodes(self, xpath):
        nodes = []
        ns = self.__node.xpathEval(xpath)
        for n in ns:
            nodes.append(self.__newNode(n))
        return nodes
    
    def getFirstChild(self):
        return self.__newNode(self.__node.children)
    
    def getLastChild(self):
        return self.__newNode(self.__node.last)
        
    def getNextSibling(self):
        return self.__newNode(self.__node.next)
        
    def getPrevSibling(self):
        return self.__newNode(self.__node.prev)
    
    def getParent(self):
        p = self.__node.parent
        if p!=None and p.type=="element":
            return self.__newNode(self.__node.parent)
        else:
            return None
    
    def getChildren(self):
        """ returns a list of nodes (NodeList) """
        nodes = []
        n = self.__node.children
        while n!=None:
            nodes.append(self.__newNode(n))
            n = n.next
        return nodes

    def copy(self):
        return self.__newNode(self.__node.copyNode(1))
        
    def getAttributes(self):
        atts = {}
        att = self.__node.properties
        while att!=None:
            atts[att.name] = att.content
            att = att.next
        return atts
    
    def getAttribute(self, name):
        att = self.__node.hasProp(name)
        if att==None:
            return None
        else:
            return att.content
    
    def setAttribute(self, name, content):
        att = self.__node.hasProp(name)
        if att==None:
            att = self.__node.newProp(name, content)
        else:
            #Note: this is a work around for a bug when adding 'one & two' type text
            t = libxml2.newText(content)
            content = t.serialize()
            t.freeNode()
            att.setContent(content)
    
    def removeAttribute(self, name):
        att = self.__node.hasProp(name)
        if att!=None:
            att.removeProp()

    def setRawContent(self, rawText):
        self.__node.setContent(rawText)
        return self
    
    def setContent(self, text):
        #Note: this is a work around for a bug when adding 'one & two' type text
        t = libxml2.newText(text)
        text = t.serialize()
        t.freeNode()
        self.__node.setContent(text)
        return self
    
    def addRawContent(self, text):
        tmpNode = libxml2.newNode("tmp")
        try:
            tmpNode.setContent(text)
            textNode = tmpNode.children
            textNode.replaceNode(None)
            tmpNode.freeNode()
            self.__node.addChild(textNode)
        except:
            tmpNode.freeNode()
            raise Exception("text is not a well-formed raw xml string")
    
    def addContent(self, text):
        self.__node.addContent(text)
        return self
        
    def getContent(self, xpath=None):
        if xpath==None:
            return self.__node.content
        else:
            node = self.getNode(xpath)
            if node!=None:
                return node.__node.content
            else:
                return None
    content = property(getContent, setContent)
    
    def getContents(self, xpath=None):
        if xpath==None:
            return [self.__node.content]
        else:
            contents = []
            nodes = self.__node.xpathEval(xpath)
            for node in nodes:
                contents.append(node.content)
            return contents

    def addChild(self, node):
        if node.__node.parent!=None:
            node.__node.replaceNode(None)
        self.__node.addChild(node.__node)
        return self
    
    def addChildren(self, nodeList):
        for node in nodeList:
            self.addChild(node)
        return self
    
    def addNextSibling(self, node):
        self.__node.addNextSibling(node.__node)
        return self
    
    def addPrevSibling(self, node):
        self.__node.addPrevSibling(node.__node)
        return self

    def delete(self):
        if self.__node.parent!=None:
            self.__node.replaceNode(None)
        self.__node.freeNode()
        self.__node = None

    def remove(self):
        self.__node.replaceNode(None)
        return self
        
    #def __del__(self):
    #    # must keep a record of it's parent document to do this because the parent may have already been GC!
    #    if self.__node!=None and self.__node.parent==None:
    #        print "Warning: node type='%s', name='%s' has no parent and has not been deleted!" % (self.__node.type, self.__node.name)
        
    def replace(self, nodeOrNodeList):
        if isinstance(nodeOrNodeList, _Node):
            self.__node.replaceNode(nodeOrNodeList.__node)
        else:
            if self.__node.type=="text" and len(nodeOrNodeList)>0:
                node = nodeOrNodeList.pop(0)
                self.__node.replaceNode(node.__node)
                for n in nodeOrNodeList:
                    node.__node.addNextSibling(n.__node)
                    node = n
            else:
                for node in nodeOrNodeList:
                    self.__node.addPrevSibling(node.__node)
                self.__node.replaceNode(None)
        return self
        
    def serialize(self, format=True):
        if format:
            return self.__node.serialize(None, 1)
        else:
            return self.__node.serialize()
    
    def __str__(self):
        return self.__node.serialize()



class xml(_Node):
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
    def __init__(self, xmlcontent, nsList=[], parseAsHtml=False, dom=None):
        # Note: the 'dom' argument is only for internal use. Please do not use.
        self.fileName = None
        self.isHtml = False
        self.nsList = []
        self.__dom = None
        if dom!=None:
            self.__dom = dom
        elif os.path.isfile(xmlcontent):
            self.fileName = xmlcontent
            try:
                if parseAsHtml: raise
                self.__dom = libxml2.parseFile(xmlcontent)
            except:
                self.__dom = libxml2.htmlParseFile(xmlcontent, "UTF-8")
                self.isHtml = True
        else:
            #print "parsing string"
            if xmlcontent.startswith("<"):
                try:
                    #print "still parsing string"
                    if parseAsHtml: raise
                    self.__dom = libxml2.parseDoc(xmlcontent)
                    #print "finished parsing"
                except:
                    if not xmlcontent.startswith("<"):
                        raise Exception("'%s' is not XML")
                    #print "parsing string as html"
                    self.__dom = libxml2.htmlParseDoc(xmlcontent, "UTF-8")
                    self.isHtml = True
            else:
                raise Exception("No xml content given!")
                #self.__dom = libxml2.parseDoc("<root/>")
        
        self.__context = self.__dom.xpathNewContext()
        self.addNamespaceList(nsList)
        _Node.__init__(self, self.__dom)
        self.__rootNode = _Node(self.__dom.getRootElement())
    
    def __del__(self):
        if self.__dom!=None:
            print "Warning: xml object was not closed! (fileName='%s')" % self.fileName
            print "  Closing now."
            self.close()
    
    def close(self):
        if self.__dom != None:
            self.__dom.freeDoc()
            self.__dom = None
            self.__context = None
    
    def addNamespaceList(self, nsList):
        for nsName, nsUrl in nsList:
            self.__context.xpathRegisterNs(nsName, nsUrl)
        self.nsList += nsList

    def getRootNode(self):
        return self.__rootNode
    
    def createElement(self, elementName, elementContent=None, elementNS=None, **args):
        node = self.__dom.newDocNode(elementNS, elementName, None)
        for name, content in args.items():
            node.newProp(name, str(content))
        node = _Node(node)
        if elementContent!=None:
            node.setContent(elementContent)
        return node
        
    def createText(self, content):
        node = self.__dom.newDocText(content)
        return _Node(node)
    
    def createPI(self, name, content=None):
        node = self.__dom.newDocPI(name, content)
        return _Node(node)
        
    def createComment(self, content):
        node = self.__dom.newDocComment(content)
        return _Node(node)

    def addComment(self, content):
        node = self.createComment(content)
        self.__rootNode.addChild(node)
        
    def addElement(self, elementName):
        node = self.createElement(elementName)
        self.__rootNode.addChild(node)
        return node
    
    def getNode(self, xpath):
        node = None
        ns = self.__context.xpathEval(xpath)
        if len(ns)>0:
            node = _Node(ns[0])
        return node
    
    def getNodes(self, xpath):
        nodes = []
        ns = self.__context.xpathEval(xpath)
        for n in ns:
            nodes.append(_Node(n))
        return nodes
        
    def getContents(self, xpath):
        nodes = []
        ns = self.__context.xpathEval(xpath)
        for n in ns:
            nodes.append(n.content)
        return nodes
    
    def xmlStringToElement(self, xmlString):
        dom = libxml2.parseDoc(xmlString)
        node = dom.getRootElement()
        node.replaceNode(None)
        
        # fixup context
        self.__dom.addChild(node)
        node.replaceNode(None)
        
        node = _Node(node)
        dom.free()
        return node
    
    def xmlStringToNodeList(self, xmlString):
        nodeList = []
        dom = libxml2.parseDoc("<r>" + xmlString + "</r>")
        rootNode = dom.getRootElement()
        node = rootNode.children
        while node!=None:
            nodeList.append(_Node(node))
            nextNode = node.next
            node.replaceNode(None)
            
            # fixup context
            self.__dom.addChild(node)
            node.replaceNode(None)
            
            node = nextNode
        dom.free()
        return nodeList
            
    
    def applyXslt(self, xslt):
        dom = xslt.transformToDom(self.__dom)
        return self.__class__(xmlcontent="", dom=dom)
    
    #===============================
#    def walk(self, node=None):
#        if node==None:
#            node = self.__context.getRootElement()
#        for n in node.walk_depth_first():
#            if n.type=="element":
#                yield n.type, n.name, None
#                p = n.properties
#                while p!=None:
#                    yield p.type, p.name, p.content
#                    p = p.next
#            else:
#                yield n.type, n.name, n.content
    
    
    def saveFile(self, fileName=None):
        if fileName==None:
            fileName = self.fileName
            if fileName==None:
                return
        self.__dom.saveFile(fileName)
                
    
    #def __str__(self):
    #    return self.__context.getRootElement().serialize()


#    libxml2 Reading
# children - (property) first child
# next     - (property) next child
# prev     - (property) prev child
# type     - (property string) "document_xml", "text", "element", "comment", "pi", "attribut", "framement"
# name     - (property) the name of the node
# properties - (property) the first attribute of an element  (next for the next proptery)
# content  - (property) the content of the node
# getRootElement() - get the rootElement
# get_doc()    - get the document DOM for the node
# walk_depth_first() - walk the nodes within a node or document

#    libxml2 Writing
# doc.newCDataBlock(content, len(content))
# doc.newDocComment(content)
# doc.newDocFragment()
# doc.newDocPI(name, content)
# doc.newDocText(content)
# doc.newDocNode(namespace, elementName, content)  or (None, name, None)
#
# node.newChild(ns, elementName, content)  # also adds the element
# node.newProp(attName, content)    # and adds
# node.addContent(content)    # adds text
# node.addChild(node)    # or fragment
# node.addNextSibling(node)
# node.addPrevSibling(node)
# node.addSibling(node)
# node.get_doc()

# free()                dom.free()
# freeNode()            node.freeNode()
# freeNodeList()

# saveFile(filename)

# libxml2.newNode(name)
# libxml2.newPI(name, content)
# libxml2.newComment(content)
# libxml2.newText(content)




