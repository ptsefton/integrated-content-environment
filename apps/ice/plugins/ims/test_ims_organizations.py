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

from ims_organizations import imsOrganizations

imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]

orgsXmlTestStr = """<organizations default="default">
    <organization identifier="default"/>
    <organization identifier="test-id"/>
</organizations>
"""

class mockOrganization(object):
    def __init__(self, parent, identifier="default", title="Untitled"):
        self.parent = parent
        self.identifier = identifier
        self.title = title
    
    def load(self, orgNode):
        id = orgNode.getAttribute("identifier")
        self.identifier = id
        
    def serialize(self, xml):
        node = xml.createElement("mockOrganization", identifier=self.identifier)
        return node    
imsOrganizations.imsOrganization = mockOrganization

class mockResources(object):
    pass

class mockRepository(object):
    pass

class mockParent(object):
    def __init__(self, rep=None, resources=None):
        if rep==None:
            rep = mockRepository()
        if resources==None:
            resources = mockResources()
        self.__rep = rep
        self.__resources = resources
        self.saveCalled = False
        
    def __getRep(self):
        return self.__rep
    rep = property(__getRep)
    
    def __getResources(self):
        return self.__resources
    resources = property(__getResources)
    
    def __getStartPath(self):
        return "/test/"
    startPath = property(__getStartPath)
    
    def save(self):
        self.saveCalled = True
    
# imsOrganizations
#  Constructor:
#    imsOrganizations(parent, [defaultName="default"])
#  Properties:
#    rep (ReadOnly)
#    resources (ReadOnly)
#    parent (ReadOnly)
#    startPath (ReadOnly)
#    defaultOrganization (ReadOnly)
#    
#  Methods:
#    addOrganization(org)
#    getOrganization(orgName)
#    load(orgsNode)
#    serialize(xml)
#    save()
#

def test_init():
    parent = mockParent()
    orgs = imsOrganizations(parent)

    assert orgs.parent is parent
    assert orgs.rep is parent.rep
    assert orgs.resources is parent.resources
    assert orgs.startPath == "/test/"
    defaultOrg = orgs.defaultOrganization
    assert defaultOrg is not None
    
    print str(orgs)
    assert str(orgs) == """<organizations default="default"><mockOrganization identifier="default"/></organizations>"""


def test_load_serialize():
    parent = mockParent()
    orgs = imsOrganizations(parent)
    xml = IceCommon.Xml(orgsXmlTestStr)
    
    orgs.load(xml.getRootNode())
    
    orgsNode = orgs.serialize(xml)
    expected = """<organizations default="default"><mockOrganization identifier="default"/><mockOrganization identifier="test-id"/></organizations>"""
    assertSameXml(orgsNode, expected)
    
    xml.close()


def test_add_getOrganization():
    #    addOrganization(org)
    #    getOrganization(orgName)
    parent = mockParent()
    name = "defaultTest"
    orgs = imsOrganizations(parent, defaultName=name)

    mockOrg = mockOrganization(orgs, identifier=name)
    mockOrg2 = mockOrganization(orgs, identifier="test")
    orgs.addOrganization(mockOrg)
    orgs.addOrganization(mockOrg2)
    assert orgs.defaultOrganization is mockOrg
    assert orgs.getOrganization(name) is mockOrg
    assert orgs.getOrganization("test") is mockOrg2
    

def test_save():    
    parent = mockParent()
    orgs = imsOrganizations(parent)
    
    assert parent.saveCalled==False
    orgs.save()
    assert parent.saveCalled
    












