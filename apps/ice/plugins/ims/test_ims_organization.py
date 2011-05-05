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

from ice_common import IceCommon
IceCommon.setup()



from diff_util import *

from ims_organization import imsOrganization


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]

organizationXmlStr = """<organization identifier="default" structure="">
    <title>Untitled</title>
    <item identifier="default-1d8994d66d3f5774b5d92b143bfd2daa-1"
        identifierref="1d8994d66d3f5774b5d92b143bfd2daa" isvisible="True">
        <title>Assessment</title>
    </item>
    <item identifier="default-61259e595362bef92c48bbc3a018263c-1"
        identifierref="61259e595362bef92c48bbc3a018263c" isvisible="True">
        <title>Introduction</title>
    </item>
    <item identifier="default-6b1fac15e90e48129c944af960de6b5a-1"
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
</organization>"""

class mockRepository(object):
    def __init__(self):
        pass
        
    def getItemNameFor(self, file):
        return file
        
    def hasMeta(self, file, name):
        return True
    
    def getMeta(self, file, name):
        return file + "-" + name

class mockResources(dict):
    def __init__(self):
        dict.__init__(self)
        self.resArray = []
        def addMockResource(id, href):
            res = mockResource(id, href)
            self[res.id] = res
            self.resArray.append(res)
        addMockResource("1d8994d66d3f5774b5d92b143bfd2daa", "intro/assessment.htm")
        addMockResource("61259e595362bef92c48bbc3a018263c", "intro/introduction.htm")
        addMockResource("6b1fac15e90e48129c944af960de6b5a", "study-materials/study_guide.htm")
        addMockResource("3b9a62f98b3b22396c22af668b858dc6", "study-materials/module01.htm")
        addMockResource("5285e7c6f41844d36bb234c3e8047819", "media/module01.pdf")
        addMockResource("998b710ec34f3fea931df125a307c3ad", "study-materials/module02.htm")
        addMockResource("7a35b3f45f8c976510e07ae89599fcad", "study-materials/module03.htm")
        addMockResource("testID", "test/one.txt")

        
    def getResourceByHref(self, href):
        for r in self.resArray:
            if r.href==href:
                return r
        return None
    
    def testGetResource(self, index):
        return self.resArray[index]


class mockResource(object):
    def __init__(self, id, href, exists=True, isWordDoc=False):
        self.id = id
        self.identifier = id
        self.href = href
        self.exists = exists
        self.isWordDoc = isWordDoc
        self.repPath = "/start/path/" + href
    def __str__(self):
        return "mockResouce object id=" + self.id
    

class mockParent(object):
    def __init__(self):
        self.rep = mockRepository()
        self.resources = mockResources()
        self.saveCalled = False
        self.startPath = "/start/path/"
        
    def save(self):
        self.saveCalled = True

# imsOrganization   Note: Inherits from imsItem
#  Constructor:
#    imsOrganization(parent, [identifier="default"], [title="Untitled"])
#  Properties:
#    .rep (ReadOnly)
#    parent (ReadOnly)
#    .parentItem (R/W) - overriden to be ReadOnly and returns None
#    .startPath (ReadOnly)
#    .identifier (ReandOnly)
#    .title (R/W)
#    .resources (ReadOnly)
#    .isDefaultItem (ReadOnly) - overriden
#    defaultItem (ReadOnly)  same as getDefaultItem()
#  Methods:
#    .setAsDefaultItem([set=True]) - overriden
#    .addItem(item, [index])
#    .addItemBeforeItem(addItem, beforeItem)
#    .removeItem()
#    .getAllChildItems()
#    .getItem(identifier)
#    .getItemByIdRef(idRef)
#    load(orgNode)  - (overriden)
#    serialize(xml)  - (overriden)
#    save()
#    getDefaultItem()
#    makeIdentifier(idRef)
#    addFileItem(href, [index])
#    deleteItem(item)
#    getResourceByHref(href):
#    getItemByFilePath(href):
#    expandAll()
#    minimizeAll()
#    moveBefore(moveItemIdentifiers, destItemIdentifier)
#    moveTo(moveItemIdentifiers, destItemIdentifier)
#    

def getTestOrg():
    parent = mockParent()
    org = imsOrganization(parent)
    xml = IceCommon.Xml(organizationXmlStr)
    node = xml.getRootNode()
    org.load(node)
    xml.close()
    return org

#Tests
def test_init():
    parent = mockParent()
    org = imsOrganization(parent)


def test_load_serialize():
    #    load(orgNode)  - (overriden)
    org = getTestOrg()

    orgXmlStr = str(org)
    assertSameXml(orgXmlStr, organizationXmlStr)


def test_serialize():
    #    serialize(xml)  - (overriden)
    org = getTestOrg()
    
    xml = IceCommon.Xml("<root/>")
    orgNode = org.serialize(xml)
    assertSameXml(str(orgNode), organizationXmlStr)
    xml.close()


def test_save():
    #    save()
    parent = mockParent()
    org = imsOrganization(parent)

    assert parent.saveCalled == False
    org.save()
    assert parent.saveCalled


def test_readonly_properties():
    #    .rep (ReadOnly)
    #    parent (ReadOnly)
    #    .parentItem (R/W) - overriden to be ReadOnly and returns None
    #    .startPath (ReadOnly)
    #    .identifier (ReandOnly)
    #    .resources (ReadOnly)
    #    .isDefaultItem (ReadOnly) - overriden
    #    defaultItem (ReadOnly)  same as getDefaultItem()
    parent = mockParent()
    org = imsOrganization(parent)

    assert org.rep is parent.rep
    assert org.parent is parent
    assert org.parentItem is None
    assert org.startPath == parent.startPath
    assert org.identifier == "default"
    assert org.resources is parent.resources
    assert org.isDefaultItem == True    # Because non of it's items are the defaultItem
    assert org.defaultItem is None


def test_title():
    #    .title (R/W)
    parent = mockParent()
    org = imsOrganization(parent)

    assert org.title=="Untitled"
    org.title = "NewTitle"
    assert org.title=="NewTitle"


def test_DefaultItem():
    #    .setAsDefaultItem([set=True]) - overriden
    #    getDefaultItem()
    org = getTestOrg()

    item = org.getAllChildItems()[1]
    item.setAsDefaultItem()
    assert item.isDefaultItem
    assert org.isDefaultItem == False
    assert org.defaultItem is item
    
    org.setAsDefaultItem()
    assert org.isDefaultItem 
    assert org.defaultItem is None
    assert item.isDefaultItem == False


def test_inherited_methods():
    #    .addItem(item, [index])
    #    .addItemBeforeItem(addItem, beforeItem)
    #    .removeItem()
    #    .getAllChildItems()
    #    .getItem(identifier)
    #    .getItemByIdRef(idRef)
    org = getTestOrg()
    item = org.getAllChildItems()[2]
    assert org.getItem(item.identifier) is item
    assert org.getItemByIdRef(item.identifierRef) is item
    assert len(item.getAllChildItems()) == 4
    xItem = item.getAllChildItems()[2]
    item.removeItem(xItem)
    assert len(item.getAllChildItems()) == 3
    item.addItem(xItem)
    assert len(item.getAllChildItems()) == 4


def test_makeIdentifier():
    #    makeIdentifier(idRef)
    parent = mockParent()
    org = imsOrganization(parent)
    
    id = org.makeIdentifier("test")
    assert id == "default-test-1"
    id = org.makeIdentifier("test")
    assert id == "default-test-2"


def test_addFileItem():
    #    addFileItem(href, [index])
    org = getTestOrg()

    assert len(org.getAllChildItems())==7
    addedItem = org.addFileItem("test/one.txt")
    assert len(org.getAllChildItems())==8


def test_deleteItem():
    #    deleteItem(item)
    org = getTestOrg()
    
    allItems = org.getAllChildItems()
    assert len(allItems)==7
    item = allItems[2]
    org.deleteItem(item)
    assert len(org.getAllChildItems())==6


def test_getItemByHref():
    #    getItemByHref(href):
    org = getTestOrg()
    
    item = org.getItemByHref("intro/assessment.htm")
    assert item is not None
    assert item.title == "Assessment"
    

def test_expandAll_minimizeAll():
    #    expandAll()
    #    minimizeAll()
    org = getTestOrg()
    allItems = org.getAllChildItems()
    for item in allItems:
        assert item.expanded == False
    org.expandAll()
    for item in allItems:
        assert item.expanded
    org.minimizeAll()
    for item in allItems:
        assert item.expanded == False
    

def test_moveBefore():
    #    moveBefore(moveItemIdentifiers, destItemIdentifier)
    org = getTestOrg()
    assert len(org._items) == 3
    item = org._items[1]
    org.moveBefore(item.identifier, org._items[0].identifier)
    assert item is org._items[0]


def test_moveTo():
    #    moveTo(moveItemIdentifiers, destItemIdentifier)
    org = getTestOrg()
    allItems = org.getAllChildItems()
    assert len(org._items) == 3
    ids = []
    for item in allItems:
        ids.append(item.identifier)
    org.moveTo(",".join(ids), org.identifier)
    assert len(org._items) == 7






