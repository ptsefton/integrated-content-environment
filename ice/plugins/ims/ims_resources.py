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

import ims_resource
from hashlib import md5


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]


class ImsResources(dict):
    # ImsResources   (keyed by resource.identifier)
    #  Constructor:
    #    ImsResources(parent, includeSource=False)
    #  Properties:
    #    rep (ReadOnly)
    #    startPath (ReadOnly)
    #    files (ReadOnly) [] array of files (hrefs)
    #    [resourceIdentifier]
    #  Methods:
    #    createResource(href)
    #    addResource(resource)
    #    removeResource(resource)
    #    getResourceByHref(href)
    #    containsResource(href)
    #    load(resourcesNode)
    #    serialize(xml)
    #    
    ImsResource = ims_resource.ImsResource
    def __init__(self, parent, includeSource=False):
        dict.__init__(self)        
        self.iceContext = parent.iceContext
        self.__hrefs = dict()
        self.__parent = parent
        self.__startPath = parent.startPath
        self.__includeSource = includeSource
    
    
    @property
    def rep(self):
        return self.__parent.rep


    def __getitem__(self, key):        # override
        return dict.get(self, key, None)
    
    def __setitem__(self, key, value):    # override
        if value.identifier!=key:
            raise Exception("can only add resources with an identifier that equals the key value!")
        if value.href==None:
            raise Exception("the add resource's href is None!")
        dict.__setitem__(self, key, value)
        try:
            self.__hrefs[value.href] = value
        except:
            # for unPickle-ing
            self.__hrefs = dict()
            self.__hrefs[value.href] = value
    
    
    def get(self, key, *args):    # override
        return dict.get(self, key, *args)

    def __delitem__(self, key):    # override
        if self.has_key(key):
            res = self.pop(key)
            try:
                self.__hrefs.pop(res.href)
            except:
                pass


    def addResource(self, resource):
        #self.__resources[resource.identifier] = resource
        self[resource.identifier] = resource
        return resource
    
    
    def removeResource(self, resource):
        id = resource.identifier
        if self.has_key(id):
            del self[id]        # Note: this calls the above __delitem__ method
            return resource
        else:
            return None
    
    
    def getResourceByHref(self, href):
        if self.__hrefs.has_key(href):
            return self.__hrefs[href]
        else:
            return None


    def containsResource(self, href):
        return self.__hrefs.has_key(href)
    
    
    def __getStartPath(self):
        return self.__startPath
    startPath = property(__getStartPath)
    
    
    def __getFiles(self):
        files = {}
        #for res in self.__resources.itervalues():
        for res in self.itervalues():
            fs = res.files
            files.update(zip(fs, fs))
        return files.keys()
    files = property(__getFiles)
    
    
    def getIdFor(self, href):
        s = self.iceContext.url_join(self.startPath, href)
        #name, ext = self.iceContext.fs.splitExt(s)
        name = s
        hash = md5(name)
        return hash.hexdigest()    
    
    
    def createResource(self, href, resNode=None, update=False):
        resource = self.ImsResource(self, href=href, resNode=resNode, \
                    includeSource=self.__includeSource, update=update)
        return resource
        
    
    def load(self, resourcesNode, update=False):
        resourceNodes = resourcesNode.getNodes(".//*[local-name()='resource']")
        for resNode in resourceNodes:
            imsRes = self.createResource(href=None, resNode=resNode, update=update)
            self.addResource(imsRes)
    
    
    def serialize(self, xml):
        node = xml.createElement("resources")
        #keys = self.__resources.keys()
        keys = self.keys()
        keys.sort()
        node.addContent("\n")
        for key in keys:
            #resource = self.__resources[resourceKey]
            resource = self[key]
            node.addChild(resource.serialize(xml))
            node.addContent("\n")
        return node
    
    
    def __str__(self):
        xml = self.iceContext.Xml("<root/>")
        node = self.serialize(xml)
        s = str(node)
        xml.close()
        return s
    
    
    #def items(self):
    #    for key in self.__resources.keys():
    #        yield self.__resources[key]
    
    #def iterResources(self):
    #    return self.__resources.itervalues()









