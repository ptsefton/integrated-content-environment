#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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

import os
import sys
##if sys.path.count("../ice")==0: sys.path.append("../ice")
##from ixe_globals import *
from ice_common import IceCommon
IceCommon.setup()


from diff_util import *

from ims_item import *
imsItem = ImsItem

imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]

# NOTE: item @identifierref == resource @identifier

simpleItemTestXml = """<item identifier="default-61259e595362bef92c48bbc3a018263c-1" 
                    identifierref="61259e595362bef92c48bbc3a018263c" isvisible="True">
                    <title>Introduction</title>
</item>"""
#        <resource identifier="61259e595362bef92c48bbc3a018263c" type="webcontent"
#            href="intro/introduction.htm">
#            <file href="intro/introduction.htm"/>
#            <file href="intro/introduction_files/459cceb9_226x226.gif"/>
#        </resource>

nestedItemTestXml = """<item identifier="default-6b1fac15e90e48129c944af960de6b5a-1"
                identifierref="6b1fac15e90e48129c944af960de6b5a" isvisible="True">
                <title>Study Guide</title>
                <item identifier="default-3b9a62f98b3b22396c22af668b858dc6-1"
                    identifierref="3b9a62f98b3b22396c22af668b858dc6" isvisible="True">
                    <title>Module 1 About Stuff</title>
                    <item identifier="default-5285e7c6f41844d36bb234c3e8047819-1"
                        identifierref="5285e7c6f41844d36bb234c3e8047819" isvisible="True">
                        <title>PDF</title>
                    </item>
                </item>
                <item identifier="default-998b710ec34f3fea931df125a307c3ad-1"
                    identifierref="998b710ec34f3fea931df125a307c3ad" isvisible="True">
                    <title>Module 2 More about stuff</title>
                </item>
                <item identifier="default-7a35b3f45f8c976510e07ae89599fcad-1"
                    identifierref="7a35b3f45f8c976510e07ae89599fcad" isvisible="True">
                    <title>Module 3 Even more about stuff</title>
                </item>
</item>
"""
#        <resource identifier="6b1fac15e90e48129c944af960de6b5a" type="webcontent"
#            href="study-materials/study_guide.htm">
#            <file href="study-materials/study_guide.htm"/>
#        </resource>
#        <resource identifier="3b9a62f98b3b22396c22af668b858dc6" type="webcontent"
#            href="study-materials/module01.htm">
#            <file href="study-materials/module01.htm"/>
#            <file href="study-materials/module01_files/m638bc800_100x75.gif"/>
#        </resource>
#        <resource identifier="5285e7c6f41844d36bb234c3e8047819" type="webcontent"
#            href="media/module01.pdf">
#            <file href="media/module01.pdf"/>
#        </resource>
#        <resource identifier="998b710ec34f3fea931df125a307c3ad" type="webcontent"
#            href="study-materials/module02.htm">
#            <file href="study-materials/module02.htm"/>
#        </resource>
#        <resource identifier="7a35b3f45f8c976510e07ae89599fcad" type="webcontent"
#            href="study-materials/module03.htm">
#            <file href="study-materials/module03.htm"/>
#        </resource>


class mockRep(object):
    def __init__(self):
        pass
        
    def getItemNameFor(self, file):
        return file
        
    def hasMeta(self, file, name):
        return True
    
    def getMeta(self, file, name):
        return file + "-" + name


class mockOrganizations(object):
    def __init__(self):
        self.resources = mockResources()
        self.rep = mockRep()


class mockOrganization(ImsItem):
    def __init__(self):
        parent = mockOrganizations()
        ImsItem.__init__(self, parent)
        self.__resources = parent.resources
        #self.__items = []
    
    def __getResources(self):
        return self.__resources
    resources = property(__getResources)
    
    def __getParentItem(self):
        return None
    parentItem = property(__getParentItem)
    
    def __getStartPath(self):
        return "/test/"
    startPath = property(__getStartPath)
    
    def makeIdentifier(self, idRef):
        return "mock-%s-1" % idRef
    
    def getIdentifier(self, idRef):
        return "orgMakeId"
    
    def getDefaultItem(self):
        children = self.getAllChildItems()
        for child in children:
            if child.isDefaultItem:
                return child
        return None
    
    def __str__(self):
        return "[mockOrg object]"    # items=" + str(len(self.__items))

        
class mockResources(dict):
    def __init__(self):
        dict.__init__(self)
        self.resArray = []
        res = mockResource("61259e595362bef92c48bbc3a018263c", "intro/introduction.htm")
        self[res.id] = res
        self.resArray.append(res)
        res = mockResource("6b1fac15e90e48129c944af960de6b5a", "study-materials/study_guide.htm")
        self[res.id] = res
        self.resArray.append(res)
        res = mockResource("3b9a62f98b3b22396c22af668b858dc6", "study-materials/module01.htm")
        self[res.id] = res
        self.resArray.append(res)
        res = mockResource("5285e7c6f41844d36bb234c3e8047819", "media/module01.pdf")
        self[res.id] = res
        self.resArray.append(res)
        res = mockResource("998b710ec34f3fea931df125a307c3ad", "study-materials/module02.htm")
        self[res.id] = res
        self.resArray.append(res)
        res = mockResource("7a35b3f45f8c976510e07ae89599fcad", "study-materials/module03.htm")
        self[res.id] = res
        self.resArray.append(res)
        
    def __getitem__(self, key):
        return dict.get(self, key, None)
    
    def testGetResource(self, index):
        return self.resArray[index]


class mockResource(object):
    def __init__(self, id, href, exists=True, isWordDoc=False):
        self.id = id
        self.identifier = id
        self.href = href
        self.exists = exists
        self.isWordDoc = isWordDoc
        self.repPath = "/test/" + href
    def __str__(self):
        return "mockResouce object id=" + self.id
    
    
mockOrg = mockOrganization()


def test_itemInit():
    print "test_itemInit()"
    item = imsItem(mockOrg)
    xmlStr = str(item)
    assert xmlStr == """<item identifierref="" identifier="" isvisible="True"><title></title></item>"""

    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()    
    item = imsItem(mockOrg, itemXmlNode=simpleItemTestNode)
    assertSameXml(str(item), str(simpleItemTestNode))
    
    resource = mockOrg.resources.testGetResource(0)
    item = imsItem(mockOrg, resource=resource)
    expected = """<item identifierref="61259e595362bef92c48bbc3a018263c" identifier="mock-61259e595362bef92c48bbc3a018263c-1" isvisible="True"><title>/test/intro/introduction.htm-title</title></item>"""
    print (str(item))
    assertSameXml(str(item), expected)

    xml.close()


# Property tests
def test_startPath():
    print "test_startPath"
    item = imsItem(mockOrg)
    assert item.startPath == "/test/"


def test_title():
    print "test_title"
    item = imsItem(mockOrg)
    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    
    assert item.title == ""
    item.load(simpleItemTestNode)
    assert item.title == "Introduction"
    item.title = "test"
    assert item.title == "test"
    xml.close()


def test_isVisible():
    print "test_isVisible"
    item = imsItem(mockOrg)
    
    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    
    item.load(simpleItemTestNode)
    assert item.isVisible == True
    
    simpleItemTestNode.setAttribute("isvisible", "False")
    item.load(simpleItemTestNode)
    assert item.isVisible == False

    item.isVisible = True
    assert item.isVisible == True
    item.isVisible = False
    assert item.isVisible == False
    xml.close()


def test_isWordDoc():
    print "test_isWordDoc"
    item = imsItem(mockOrg)
    
    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    
    item.load(simpleItemTestNode)
    assert item.isWordDoc == False
    
    item.resource.isWordDoc = True
    assert item.isWordDoc == True
    
    xml.close()


def test_expanded():
    print "test_expanded"
    item = imsItem(mockOrg)
    assert item.expanded == False
    item.expanded = True
    assert item.expanded == True


def test_resources():
    print "test_resources"
    item = imsItem(mockOrg)
    assert item.resources is mockOrg.resources


def test_resource():
    print "test_resource"
    item = imsItem(mockOrg)
    
    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    item.load(simpleItemTestNode)
    id = simpleItemTestNode.getAttribute("identifierref")
    
    resource = item.resource
    res = mockOrg.resources[id]
    assert resource is res
    xml.close()


# Test methods
def test_addItem():
    print "test_addItem()"
    item1 = imsItem(mockOrg)
    item1.title = "One"
    item2 = imsItem(mockOrg)
    item2.title = "Two"
    item3 = imsItem(item2)
    item3.title = "Three"
    
    item1.addItem(item2)
    item1.addItem(item3)
    
    xml = IceCommon.Xml("<root/>")
    xml.addChild(item1.serialize(xml))
    assert xml.getContent("/item/title") == "One"
    assert xml.getContent("/item/item[1]/title") == "Two"
    assert xml.getContent("/item/item[2]/title") == "Three"
    xml.close()
    

def test_addItemBefore():
    print "test_addItemBefore()"
    item1 = imsItem(mockOrg)
    item1.title = "One"
    item2 = imsItem(mockOrg)
    item2.title = "Two"
    item3 = imsItem(item2)
    item3.title = "Three"
    
    item1.addItem(item2)
    item1.addItemBeforeItem(item3, item2)
    xml = IceCommon.Xml("<root/>")
    xml.addChild(item1.serialize(xml))
    assert xml.getContent("/item/title") == "One"
    assert xml.getContent("/item/item/title") == "Three"
    assert xml.getContent("/item/item[2]/title") == "Two"
    xml.close()


def test_removeItem():
    print "test_removeItem()"
    item1 = imsItem(mockOrg)
    item1.title = "One"
    item2 = imsItem(mockOrg)
    item2.title = "Two"
    item3 = imsItem(item2)
    item3.title = "Three"

    item1.addItem(item2)
    item1.addItem(item3)
    
    item1.removeItem(item2)
    assert len(item1.getAllChildItems()) == 1
    item = item1.getAllChildItems()[0]
    assert item is item3


def test_getAllChildItems():
    print "test_getAllChildItems()"
    item1 = imsItem(mockOrg)
    item1.title = "One"
    item2 = imsItem(mockOrg)
    item2.title = "Two"
    item3 = imsItem(item2)
    item3.title = "Three"

    item1.addItem(item2)
    item1.addItem(item3)
    
    childItems = item1.getAllChildItems()
    assert len(childItems)==2
    assert childItems[0] is item2
    assert childItems[1] is item3


def test_getItem():
    print "test_getItem()"
    
    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)

    childItems = item.getAllChildItems()
    for childItem in childItems:
        i = item.getItem(childItem.identifier)
        assert i is childItem
    xml.close()
    assert item.getItem(item.identifier) is item


def test_getItemByIdRef():
    # NOTE: returns the first item found with this idRef
    print "test_getItemByIdRef()"

    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)

    childItems = item.getAllChildItems()
    for childItem in childItems:
        i = item.getItemByIdRef(childItem.identifierRef)
        assert i is childItem
    xml.close()
    assert item.getItemByIdRef(item.identifierRef) is item


def test_makeIdentifier():
    # Test that this method calls mockOrganization's makeIdentifier() method
    print "test_makIdentifier()"
    item = imsItem(mockOrg)
    assert item.makeIdentifier("x") == "mock-x-1"


def test_isDefaultItem():
    print "test_isDefaultItem"
    item = imsItem(mockOrg)
    assert item.isDefaultItem == False
    item.setAsDefaultItem()
    assert item.isDefaultItem == True
    item.setAsDefaultItem(False)
    assert item.isDefaultItem == False


def test_setAsDefaultItem():
    print "test_setAsDefaultItem()"
    mockOrg = mockOrganization()
    
    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)
    mockOrg.addItem(item)
    xml.close()
    
    children = item.getAllChildItems()
    child = children[3]
    item.setAsDefaultItem()
    assert item.isDefaultItem
    child.setAsDefaultItem()
    assert child.isDefaultItem
    assert item.isDefaultItem==False
    item.setAsDefaultItem()
    assert child.isDefaultItem==False


def test_load():
    print "test_load()"
    item = imsItem(mockOrg)

    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    item.load(simpleItemTestNode)
    assertSameXml(str(item), str(simpleItemTestNode))
    xml.close()
    
    
    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item.load(nestedItemTestNode)
    assertSameXml(str(item), str(nestedItemTestNode))
    xml.close()


def test_serialize():
    print "test_serialize()"
    xml = IceCommon.Xml(simpleItemTestXml)
    simpleItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=simpleItemTestNode)
    node = item.serialize(xml)
    assertSameXml(str(node), simpleItemTestXml)
    xml.close()
    


#def test_getIdentifierList():
#    print "test_getIdentifierList()"
#    mockOrg = mockOrganization()
#    xml = IceCommon.Xml(nestedItemTestXml)
#    nestedItemTestNode = xml.getRootNode()
#    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)
#    mockOrg.addItem(item)
#    xml.close()
#
#    list = item.getIdentifierList()
#    print list


def test_getNextItem():
    print "test_getNextItem()"  #lookDown=True
    mockOrg = mockOrganization()
    
    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)
    mockOrg.addItem(item)
    xml.close()
    
    nextItem = item.getNextItem()
    assert nextItem.title=="Module 1 About Stuff"
    nextItem = nextItem.getNextItem()
    assert nextItem.title=="Module 2 More about stuff"
    nextItem = nextItem.getNextItem()
    assert nextItem.title=="Module 3 Even more about stuff"
    nextItem = nextItem.getNextItem()
    assert nextItem is None
    
    nextItem = item.getNextItem(lookDown=False)
    assert nextItem is None


#<item identifier="default-6b1fac15e90e48129c944af960de6b5a-1"
#                identifierref="6b1fac15e90e48129c944af960de6b5a" isvisible="True">
#                <title>Study Guide</title>
#                <item identifier="default-3b9a62f98b3b22396c22af668b858dc6-1"
#                    identifierref="3b9a62f98b3b22396c22af668b858dc6" isvisible="True">
#                    <title>Module 1 About Stuff</title>
#                    <item identifier="default-5285e7c6f41844d36bb234c3e8047819-1"
#                        identifierref="5285e7c6f41844d36bb234c3e8047819" isvisible="True">
#                        <title>PDF</title>
#                    </item>
#                </item>
#                <item identifier="default-998b710ec34f3fea931df125a307c3ad-1"
#                    identifierref="998b710ec34f3fea931df125a307c3ad" isvisible="True">
#                    <title>Module 2 More about stuff</title>
#                </item>
#                <item identifier="default-7a35b3f45f8c976510e07ae89599fcad-1"
#                    identifierref="7a35b3f45f8c976510e07ae89599fcad" isvisible="True">
#                    <title>Module 3 Even more about stuff</title>
#                </item>
#</item>
def test_getPreviousItem():
    print "test_getPreviousItem()"
    mockOrg = mockOrganization()
    
    xml = IceCommon.Xml(nestedItemTestXml)
    nestedItemTestNode = xml.getRootNode()
    item = imsItem(mockOrg, itemXmlNode=nestedItemTestNode)
    mockOrg.addItem(item)
    xml.close()

    print "===="
    print mockOrg.__class__.__name__
    print mockOrg.parentItem
    print mockOrg
    print "===="

    aItem = item.getNextItem().getNextItem()
    print "aItem=", aItem.title
    prevItem = aItem.getPreviousItem()
    print "prevItem=", prevItem.title
    assert prevItem.title == "Module 1 About Stuff"
    prevItem = prevItem.getPreviousItem()
    print "prevItem=", prevItem.title
    assert prevItem.title == "Study Guide"
    
    print "---"
    print prevItem.__class__.__name__
    print prevItem.parentItem
    print "---"
    prevItem = prevItem.getPreviousItem()
    print prevItem
    print "-----"
    
    
def test_test():
    pass


if __name__=="__main__":
    IceCommon.system.cls()
    print "Testing"
    test_itemInit()
    test_startPath()
    test_title()
    test_isVisible()
    test_isWordDoc()
    test_expanded()
    test_resources()
    test_resource()

    test_addItem()
    test_addItemBefore()
    test_removeItem()
    test_getAllChildItems()
    test_getItem()
    test_getItemByIdRef()
    test_makeIdentifier()
    test_isDefaultItem()
    test_setAsDefaultItem()
    test_load()
    test_serialize()
    #test_getIdentifierList()
    test_getNextItem()
    test_getPreviousItem()
    print "Done"

 