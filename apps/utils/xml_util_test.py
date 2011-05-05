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

from xml_util import *
from xml_diff import XmlTestCase

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os

# Class xml
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



class XmlTests(XmlTestCase):
    def setUp(self):
        self.xmlStr = """<root>
        <items><item a='1'>one</item><item a='2'>two</item><item a='3'>three</item></items>
        <item a='4'>four</item>
        <test>testing<num>123</num></test>
        </root>"""
        self.xml = xml(self.xmlStr)
    
    def tearDown(self):
        self.xml.close()
    
    def testInit(self):
        x = self.xml
        self.assertSameXml(self.xmlStr, x)
        

    def testProperties(self):
        x = self.xml
        self.assertEqual(None, x.fileName)
        self.assertEqual(False, x.isHtml)
        self.assertEqual([], x.nsList)
    
    #   addNamespaceList(nsList)
    def testAddNamespaceList(self):
        x = self.xml
        self.assertEqual([], x.nsList)
        nsList = [("one", "1"), ("two", "2")]
        x.addNamespaceList(nsList)
        self.assertEqual(nsList, x.nsList)
        
    
    #   getRootNode()
    def testGetRootNode(self):
        x = self.xml
        rootNode = x.getRootNode()
        self.assertEqual(rootNode.getName(), "root")
        self.assertTrue(rootNode.getParent() is None)
    
    #   createElement(elementName, elementContent=None, elementNS=None, **args)
    def testCreateElement(self):
        x = self.xml
        e = x.createElement("test")
        self.assertEqual(e.getName(), "test")
        self.assertTrue(e.isElement())
        self.assertEqual(str(e), "<test/>")
        
        e = x.createElement("test", elementContent="data", one=1, two="2")
        self.assertEqual(str(e), '<test two="2" one="1">data</test>')
    
    #   createText(content)
    def testCreateText(self):
        x = self.xml
        text = "some text"
        node = x.createText(text)
        self.assertEqual(node.getType(), "text")
        self.assertEqual(str(node), text)
    
    #   createPI(name, content=None)
    def testCreatePI(self):
        x = self.xml
        text = "some text"
        pi = x.createPI(text)
        self.assertEqual(pi.getType(), "pi")
        self.assertEqual(str(pi), "<?%s?>" % text)
    
    #   createComment(content)
    def testCreateComment(self):
        x = self.xml
        text = "some text"
        node = x.createComment(text)
        self.assertEqual(node.getType(), "comment")
        self.assertEqual(str(node), "<!--%s-->" % text)
    
    #   addComment(content)
    def testAddComment(self):
        x = self.xml
        text = "comment"
        x.addComment(text)
        rNode = x.getRootNode()
        comment = rNode.getLastChild()
        self.assertEqual(str(comment), "<!--%s-->" % text)
    
    #   addElement(elementName)
    def testAddElement(self):
        x = self.xml
        x.addElement("testx")
        rNode = x.getRootNode()
        node = rNode.getLastChild()
        self.assertEqual(str(node), "<testx/>")
        
    
    #   xmlStringToElement(xmlString)
    def testXmlStringToElement(self):
        x = self.xml
        xstr = "<test/>"
        e = x.xmlStringToElement(xstr)
        self.assertEqual(e.getType(), "element")
        self.assertEqual(e.getName(), "test")
        self.assertEqual(str(e), xstr)
    
    #   xmlStringToNodeList(xmlString)
    def testXmlStringToNodeList(self):
        x = self.xml
        xstr = "<test/><two/>"
        nodeList = x.xmlStringToNodeList(xstr)
        self.assertEqual(len(nodeList), 2)
    
    #   applyXslt(xslt)
    def testApplyXslt(self):
        x = self.xml
    
    #   saveFile(fileName=None)
    def testSaveFile(self):
        x = self.xml
    

    #    getType()
    def testGetType(self):
        x = self.xml
        r = x.getRootNode()
        self.assertEqual(r.getType(), "element")
        
    
    #    isElement()
    def testIsElement(self):
        x = self.xml
        r = x.getRootNode()
        self.assertTrue(r.isElement())
        
    
    #    setName(name)
    #    getName()
    def testSetGetName(self):
        x = self.xml
        n = x.getNode("//num")
        self.assertEqual(n.getName(), "num")
        n.setName("xx")
        self.assertEqual(n.getName(), "xx")
        self.assertEqual(str(n), "<xx>123</xx>")
        
    
    #    getNode(xpath) - overriden
    def testGetNode(self):
        x = self.xml
        n = x.getNode("//num")
        self.assertEqual(str(n), "<num>123</num>")
        
    
    #    getNodes(xpath) - overriden
    def testGetNodes(self):
        x = self.xml
        nodes = x.getNodes("//item")
        self.assertEqual(len(nodes), 4)
    
    #    getFirstChild()
    def testGetFirstChild(self):
        x = self.xml
        items = x.getNode("//items")
        item = x.getNode("//items/item")
        n = items.getFirstChild()
        self.assertEqual(str(item), str(n))
        #self.assertEqual(item, n)
    
    #    getLastChild()
    def testGetLastChild(self):
        x = self.xml
        items = x.getNode("//items")
        item = x.getNode("//items/item[@a='3']")
        n = items.getLastChild()
        self.assertEqual(str(item), str(n))
    
    #    getNextSibling()
    def testGetNextSibling(self):
        x = self.xml
        item = x.getNode("//items/item[@a='2']")
        nextItem = x.getNode("//items/item[@a='3']")
        n = item.getNextSibling()
        self.assertEqual(str(nextItem), str(n))
    
    #    getPrevSibling()
    def testGetPrevSibling(self):
        x = self.xml
        item = x.getNode("//items/item[@a='2']")
        pItem = x.getNode("//items/item[@a='1']")
        n = item.getPrevSibling()
        self.assertEqual(str(pItem), str(n))
    
    #    getParent()
    def testGetParent(self):
        x = self.xml
        item = x.getNode("//items/item[@a='2']")
        pItem = x.getNode("//items")
        n = item.getParent()
        self.assertEqual(str(pItem), str(n))
    
    #    getChildren()
    def testGetChildren(self):
        x = self.xml
        items = x.getNode("//items")
        nodes = items.getChildren()
        self.assertEqual(len(nodes), 3)
        items = items.getNodes("*")
        self.assertEqual(len(items), 3)
        for i in range(3):
            self.assertEqual(str(nodes[i]), str(items[i]))
    
    #    copy()
    def testCopy(self):
        x = self.xml
        n = x.getNode("//num")
        n = n.copy()
        x.getRootNode().addChild(n)
        nodes = x.getNodes("//num")
        self.assertEqual(len(nodes), 2)
    
    #    getAttributes()
    def testGetAttributes(self):
        x = self.xml
        n = x.getNode("//item")
        atts = n.getAttributes()
        self.assertEqual(atts, {"a":"1"})
    
    #    setAttribute(name, content)
    #    getAttribute(name)
    def testSetGetAttribute(self):
        x = self.xml
        n = x.getNode("//item")
        attValue = n.getAttribute("a")
        self.assertEqual(attValue, "1")
        n.setAttribute("a", "test")
        attValue = n.getAttribute("a")
        self.assertEqual(attValue, "test")
        
        attValue = n.getAttribute("x")
        self.assertEqual(attValue, None)
        n.setAttribute("x", "testx")
        attValue = n.getAttribute("x")
        self.assertEqual(attValue, "testx")
    
    #    removeAttribute(name)
    def testRemoveAttribute(self):
        x = self.xml
        n = x.getNode("//item")
        atts = n.getAttributes()
        self.assertEqual(atts, {"a":"1"})
        n.removeAttribute("a")
        atts = n.getAttributes()
        self.assertEqual(atts, {})
    
    #    setRawContent(rawText)
    #    addRawContent(text)
    def testSetAddRawContent(self):
        x = self.xml
        n = x.getNode("//item")
        self.assertEqual(n.getContent(), "one")
        n.addRawContent("-&amp;-")
        self.assertEqual(n.getContent(), "one-&-")
        n.setRawContent("-&amp;&lt;-")
        self.assertEqual(n.getContent(), "-&<-")
    
    #    setContent(text)
    #    getContent(xpath=None)
    #    addContent(text)
    def testSetGetAddContent(self):
        x = self.xml
        n = x.getNode("//item")
        self.assertEqual(n.getContent(), "one")
        n.setContent("test")
        self.assertEqual(n.getContent(), "test")
        n.addContent("123")
        self.assertEqual(n.getContent(), "test123")
    
    #    getContents(xpath=None)  - overriden
    def testGetContents(self):
        x = self.xml
        contents = x.getContents("//items/item")
        self.assertEqual(contents, ["one", "two", "three"])
    
    #    addChild(node)
    def testAddChild(self):
        x = self.xml
        e = x.createElement("testx")
        r = x.getRootNode()
        r.addChild(e)
        node = r.getLastChild()
        self.assertEqual(str(e), str(node))
    
    #    addChildren(nodeList)
    def testAddChildren(self):
        x = self.xml
        nodes = x.xmlStringToNodeList("<one/><two/>")
        r = x.getRootNode()
        r.addChildren(nodes)
        ln = r.getLastChild()
        self.assertEqual(str(ln), "<two/>")
        sln = ln.getPrevSibling()
        self.assertEqual(str(sln), "<one/>")
    
    #    addNextSibling(node)
    def testAddNextSibling(self):
        x = self.xml
        n = x.getNode("//item[@a='2']")
        e = x.createElement("x")
        n.addNextSibling(e)
        n2 = n.getNextSibling()
        self.assertEqual(str(e), str(n2))
    
    #    addPrevSibling(node)
    def testAddPrevSibling(self):
        x = self.xml
        n = x.getNode("//item[@a='2']")
        e = x.createElement("x")
        n.addPrevSibling(e)
        n2 = n.getPrevSibling()
        self.assertEqual(str(e), str(n2))
    
    #    delete()
    def testDelete(self):
        x = self.xml
        n = x.getNode("//item[@a='2']")
        n.delete()
        n = x.getNode("//item[@a='2']")
        self.assertEqual(n, None)
    
    #    remove()
    def testRemove(self):
        x = self.xml
        n = x.getNode("//item[@a='2']")
        node = n.remove()
        n = x.getNode("//item[@a='2']")
        self.assertEqual(n, None)
        n = x.getNode("//items")
        n.addChild(node)
        n = x.getNode("//item[@a='2']")
        self.assertTrue(n != None)
    
    #    replace(nodeOrNodeList)
    def testReplace(self):
        x = self.xml
        test = x.getNode("//test")
        numNode = test.getNode("num")
        nodeList = x.getNodes("//item")
        numNode.replace(nodeList)
        node = test.getNode("num")
        self.assertTrue(node is None)
        nodes = test.getNodes("item")
        self.assertEqual(len(nodes), 4)
        test.addChild(numNode)
        node = test.getNode("num")
        self.assertTrue(node is not None)
    
    #    serialize(format=True)
    def testSerialize(self):
        x = self.xml
        dec = '<?xml version="1.0"?>\n'
        self.assertEqual(x.serialize(), dec + self.xmlStr.replace("'", '"') + "\n")
        r = x.getRootNode()
        #print r.serialize()
    
    #    __str__()
    def testStr(self):
        x = self.xml
        dec = '<?xml version="1.0"?>\n'
        self.assertEqual(str(x), dec + self.xmlStr.replace("'", '"') + "\n")
        r = x.getRootNode()
        self.assertEqual(str(r), self.xmlStr.replace("'", '"'))
    
    



if __name__ == "__main__":
    try:
        os.system("reset")
    except:
        try:
            os.system("cls")
        except:
            print
            print
    print "---- Testing ----"
    print
    unittest.main()





