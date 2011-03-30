#
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

"""
Atom Pub Service to process the request of atom feed through ICE-Service
@requires: xml.etree / cElementTree / elementtree library    
"""

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

APP_NS0 = "http://purl.org/atom/app#"
APP_NS = "http://www.w3.org/2007/app"
ATOM_NS = "http://www.w3.org/2005/Atom"
ATOM_ENTRY_TYPE = ["application/atom+xml;type=entry", "application/atom+xml", "entry" ]
SWORD_NS = "http://purl.org/net/sword/"

class AtomPubService(object):
    """ Base class for Atom Pub Service to produce atom feed
    """
    def __init__(self, xml):
        """ Atom Pub Service Constructor
        @param xml: xml content
        @type xml: String
        @rtype: void
        """
        self.service = ElementTree.XML(xml)
        workspaceElems = self.service.findall("{%s}workspace" % APP_NS)
        if workspaceElems == []:
            workspaceElems = self.service.findall("{%s}workspace" % APP_NS0)
        self.workspaces = []
        for workspaceElem in workspaceElems:
            self.workspaces.append(Workspace(self, workspaceElem))
    
    def getUrlForEntry(self):
        """ gets the first url that accepts atom entries
        @rtype: String
        @return: the first url found in the entry
        """
        for ws in self.workspaces:
            for col in ws.collections:
                if col.acceptsEntry():
                    return col.href
    
    def getUrlForType(self, type):
        """ gets the first url that accepts the specified mime type
        @param type: mimetype
        @type type: String 
        @rtype: String
        @return: the first url found in entry or None if not found
        """
        for ws in self.workspaces:
            for col in ws.collections:
                if col.acceptsType(type):
                    return col.href
        return None
    
    def getSwordElement(self, tag):
        """ retrieving SWORD element values
        @param tag: tag for SWORD element
        @type tag: String
        @rtype: String
        @return: value of atom element based on specified tag
        """
        return self.service.find("{%s}%s" % (SWORD_NS, tag))
    
    def getSwordElementList(self, tag):
        """ retrieving SWORD element values list
        @param tag: for SWORD element 
        @type tag: String
        @rtype: String
        @return: list of values of atom elements based on specified tag
        """
        return self.service.findall("{%s}%s" % (SWORD_NS, tag))

class Workspace(object):
    """ Base class for Workspace
    """
    def __init__(self, service, elem):
        """ Workspace Constructor
        @param service: service Elements
        @type service: ElementTree._Element, or xml_wrapper.ElementWrapper
        @param elem: individual Element
        @type elem: ElementTree._Element, or xml_wrapper.ElementWrapper
        @rtype: void
        """
        self.elem = elem
        self.service = service
        self.title = elem.find("{%s}title" % ATOM_NS).text
        collectionElems = elem.findall("{%s}collection" % APP_NS)
        if collectionElems == []:
            collectionElems = elem.findall("{%s}collection" % APP_NS0)
        self.collections = []
        for collectionElem in collectionElems:
            self.collections.append(Collection(self, collectionElem))
    
    def __str__(self):
        """ str method
        @rtype: String
        @return: title of the workspace
        """
        return "Workspace: %s" % self.title
    
    def getSwordElement(self, tag):
        """ retrieving SWORD element values
        @param tag: tag for SWORD element
        @type tag: String
        @rtype: String
        @return: value of atom element based on specified tag
        """
        return self.elem.find("{%s}%s" % (SWORD_NS, tag))
    
    def getSwordElementList(self, tag):
        """ retrieving SWORD element values list
        @param tag: for SWORD element 
        @type tag: String
        @rtype: list
        @return: list of values of atom elements based on specified tag
        """
        return self.elem.findall("{%s}%s" % (SWORD_NS, tag))

class Collection(object):
    """ Base class for Collection
    """
    def __init__(self, workspace, elem):
        """ Collection Constructor
        @param workspace: workspace Elements
        @type workspace: ElementTree._Element, or xml_wrapper.ElementWrapper
        @param elem: individual Element
        @type elem: ElementTree._Element, or xml_wrapper.ElementWrapper
        @rtype: void
        """
        self.elem = elem
        self.workspace = workspace
        self.href = elem.get('href')
        self.title = elem.find("{%s}title" % ATOM_NS).text
        acceptElems = elem.findall("{%s}accept" % APP_NS)
        if acceptElems == []:
            acceptElems = elem.findall("{%s}accept" % APP_NS0)
        self.accepts = []
        for acceptElem in acceptElems:
            self.accepts.append(acceptElem.text)
    
    def acceptsEntry(self):
        """ 
        @rtype: boolean
        @return: true if entry is in ATOM_ENTRY_TYPE list
        """
        for accept in self.accepts:
            if accept in ATOM_ENTRY_TYPE:
                return True
        return False
    
    def acceptsType(self, type):
        """ 
        @param type: type of collection
        @type type: String 
        @rtype: boolean
        @return: true if type is 'accept'
        """
        for accept in self.accepts:
            wildcard = accept.find('*')
            if wildcard > -1:
                start = accept.split('/')[0]
                if type.startswith(start):
                    return True
            else:
                if accept == type:
                    return True
        return False
    
    def __str__(self):
        """ 
        @rtype: String
        @return: title of the collection
        """
        return "Collection: %s @ %s" % (self.title, self.href)
    
    # for retrieving SWORD element values
    def getSwordElement(self, tag):
        """ retrieving SWORD element values
        @param tag: tag for SWORD element
        @type tag: String
        @rtype: String
        @return: value of atom element based on specified tag
        """
        return self.elem.find("{%s}%s" % (SWORD_NS, tag))
    
    def getSwordElementList(self, tag):
        """ retrieving SWORD element values list
        @param tag: for SWORD element 
        @type tag: String
        @rtype: list
        @return: list of values of atom elements based on specified tag
        """
        return self.elem.findall("{%s}%s" % (SWORD_NS, tag))
    
