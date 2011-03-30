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

import ims_organization


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]


class ImsOrganizations(dict):
    # ImsOrganizations
    #  Constructor:
    #    ImsOrganizations(parent, [defaultName="default"])
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
    ImsOrganization = ims_organization.ImsOrganization
    def __init__(self, parent, defaultName="default"):
        dict.__init__(self)
        self.iceContext = parent.iceContext
        self.__parent = parent
        self.__defaultName = defaultName
        org = self.ImsOrganization(self, defaultName)
        self.addOrganization(org)
    
    
    @property
    def rep(self):
        return self.__parent.rep
    
    
    @property
    def resources(self):
        return self.__parent.resources
    
    
    @property
    def parent(self):
        return self.__parent
    
    
    @property
    def startPath(self):
        return self.__parent.startPath
    
    @property
    def defaultOrganization(self):
        return self.getOrganization(self.__defaultName)
    
    
    def __getitem__(self, key):    # override (dict __getitem__)
        return dict.get(self, key, None)
    
    def __setitem__(self, key, value):    # override (dict)
        dict.__setitem__(self, key, value)
    
    def get(self, key, *args):    # override (dict)
        return dict.get(self, key, *args)
    
    
    def pickle(self):
        pass
    
    
    def addOrganization(self, org):
        #self.__organizations[org.identifier] = org
        self[org.identifier] = org
        
    
    def getOrganization(self, orgName):
        #return self.__organizations.get(orgName, None)
        return self[orgName]
    
    
    def save(self):
        self.__parent.save()
    
    
    def load(self, orgsNode):
        orgNodes = orgsNode.getNodes(".//*[local-name()='organization']")
        for org in orgNodes:
            imsOrg = self.ImsOrganization(self)
            imsOrg.load(org)
            self.addOrganization(imsOrg)
    
    
    def serialize(self, xml):
        node = xml.createElement("organizations", default=self.__defaultName)
        #for o in self.__organizations.values():
        for o in self.values():
            node.addChild(o.serialize(xml))
            node.addContent("\n")
        return node
        
    
    def __str__(self):
        xml = self.iceContext.Xml("<root/>")
        node = self.serialize(xml)
        s = str(node)
        xml.close()
        return s
    
    
    #def __getOrganizations(self):
    #    return self.__organizations.values()
    #organizations = property(__getOrganizations)













