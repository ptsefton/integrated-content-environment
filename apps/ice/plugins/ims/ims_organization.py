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

from ims_item import ImsItem


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]


class ImsOrganization(ImsItem):
    # ImsOrganization   Note: Inherits from ImsItem
    #  Constructor:
    #    ImsOrganization(parent, [identifier="default"], [title="Untitled"])
    #  Properties:         (.xxxx = inherited member. [.xxx] = unused inherited member)
    #    .rep (ReadOnly)
    #    parent (ReadOnly)
    #    parentItem (R/W) - overriden to be ReadOnly and returns None
    #    .startPath (ReadOnly)
    #    .identifier (ReandOnly)
    #    .title (R/W)
    #    .resources (ReadOnly)
    #    isDefaultItem (ReadOnly) - overriden
    #    defaultItem (ReadOnly)  same as getDefaultItem()
    #    [.identifierRef (ReadOnly)]
    #    [.isWordDoc (ReadOnly)]
    #    [.isVisible (R/W)]
    #    [.expanded (R/W)]
    #    [.resource (ReadOnly)]
    #  Methods:
    #    setAsDefaultItem([set=True]) - overriden
    #    .addItem(item, [index])
    #    .addItemBeforeItem(addItem, beforeItem)
    #    .removeItem()
    #    .getAllChildItems()
    #    .getItem(identifier)
    #    .getItemByIdRef(idRef)
    #    load(orgNode)  - (overriden)
    #    serialize(xml)  - (overriden)
    #    [.getNextItem([lookDown=True)]
    #    [.getPreviousItem()]
    #    save()
    #    getDefaultItem()
    #    makeIdentifier(idRef)
    #    addFileItem(href, [index])
    #    deleteItem(item)
    #    getItemByHref(href)
    #    expandAll()
    #    minimizeAll()
    #    moveBefore(moveItemIdentifiers, destItemIdentifier)
    #    moveTo(moveItemIdentifiers, destItemIdentifier)
    #    
    def __init__(self, parent, identifier="default", title="Untitled"):
        ImsItem.__init__(self, parent)
        #self.__parent = parent                  #?? imsItem
        #self.iceContext = parent.iceContext
        #self.__rep = parent.rep                 #?? imsItem
        #self.__resources = parent.resources     #?? imsItem
        #self.__title = title                    #?? imsItem
        self.title = title
        self.__identifier = identifier        # Uses imsItem.identifier property to read this field
        self.__itemIdentifiers = dict()   # used for ID generation
        # TODO find a better identifier for organization since this won't be unique
    
    
    # Override imsItem's parentItem propertry to return None
    def __getParentItem(self):
        return None
    parentItem = property(__getParentItem)
    
    
    # Override imsItem's identifier property
    def __getIdentifier(self):
        return self.__identifier
    identifier = property(__getIdentifier)
    
    
    def save(self):
        self.__parent.save()
    
    
    def __getIsDefaultItem(self):
        return self.getDefaultItem() is None
    isDefaultItem = property(__getIsDefaultItem)
    
    def setAsDefaultItem(self, set=True):
        if set==True:
            item = self.getDefaultItem()
            if item!=None:
                item.setAsDefaultItem(set=False)
        else:
            print "Can not unset an organization as a default item"
    
    def getDefaultItem(self):
        items = self.getAllChildItems()
        for item in items:
            if item.isDefaultItem:
                return item
        return None
    defaultItem = property(getDefaultItem)
    
    
    def makeIdentifier(self, idRef):
        if self.__itemIdentifiers.has_key(idRef):
            num = self.__itemIdentifiers[idRef] + 1
            self.__itemIdentifiers[idRef] = num
        else:
            num = 1
            self.__itemIdentifiers[idRef] = num
        return self.__getIdentifier(idRef, num)
    
    
    def __getIdentifier(self, idRef, num=1):
        return self.__identifier + "-" + idRef + "-" + str(num)
    
    
    def addFileItem(self, href, index=9999):
        resource = self.resources.getResourceByHref(href)
        if resource!=None:
            id = resource.identifier
        else:
            id = self.resources.getIdFor(href)
            #raise Exception("item not found in the resources! href=%s" % href)
        
        # check if we already have an item with this base id
        if not self.__itemIdentifiers.has_key(id):
            item = ImsItem(self, resource)
            self.addItem(item, index)
            return item
        else:
            return self.__itemIdentifiers[id]
    
    
    def deleteItem(self, item):                        #
        if item==self:
            return
        # Remove this item from its parent
        item.parentItem.removeItem(item)
        # Now add any/all of it's children items to it's parent item
        for i in item._items:
            item.parentItem.addItem(i)
    
    
    def load(self, orgNode):
        ids = ImsItem.load(self, orgNode)
        for id in ids:
            parts = id.split("-")
            idRef = parts[1]
            num = int(parts[2])
            if self.__itemIdentifiers.has_key(idRef):
                if self.__itemIdentifiers[idRef] < num:
                    self.__itemIdentifiers[idRef] = num
            else:
                self.__itemIdentifiers[idRef] = num

    
    def serialize(self, xml):
        node = xml.createElement(elementName="organization", identifier=self.identifier, \
                    structure="")
        node.addChild(xml.createElement("title", elementContent=self.title))
        node.addContent("\n")
        for item in self._items:
            node.addChild(item.serialize(xml))
            node.addContent("\n")
        return node

    
    def getContextPath(self, href):
        item = self.getItemByHref(href)
        if item is None:
            return ""
        results = []
        item.getItemContextPath(results)
        return results
        #link = "<a href='%s'>%s</a>" % (self.iceContext.url_join(packagePath, "toc.htm"), rootName)
        #for p, title in results:
        #    link += "%s<a href='%s'>%s</a>" % (sep, p, title)
        #return link
    
    
    def __str__(self):
        xml = self.iceContext.Xml("<root/>")
        node = self.serialize(xml)
        s = str(node)
        xml.close()
        return s
    
        
    def getItemByHref(self, href):
        # NOTE: returns the first item found with this Href
        res = self.resources.getResourceByHref(href)
        if res!=None:
            item = self.getItemByIdRef(res.identifier)
            return item
        else:
            return None
    
        
    def expandAll(self):
        for item in self.getAllChildItems():
            item.expanded = True
    
    
    def minimizeAll(self):
        for item in self.getAllChildItems():
            item.expanded = False
    
    
    def moveBefore(self, moveItemIdentifiers, destItemIdentifier):
        if type(moveItemIdentifiers)==type(""):
            moveItemIdentifiers = moveItemIdentifiers.split(",")
        destItem = self.getItem(destItemIdentifier)
        for id in moveItemIdentifiers:
            if destItemIdentifier==id:
                continue
            item = self.getItem(id)
            if item.getItem(destItemIdentifier)==None:    # if destItem is not a child of this item then
                item.parentItem.removeItem(item)
                destItem.addBeforeMe(item)
    
    
    # moveInTo
    def moveTo(self, moveItemIdentifiers, destItemIdentifier):
        if type(moveItemIdentifiers)==type(""):
            moveItemIdentifiers = moveItemIdentifiers.split(",")
        destItem = self.getItem(destItemIdentifier)
        for id in moveItemIdentifiers:
            if destItemIdentifier==id:
                continue
            item = self.getItem(id)
            if item.getItem(destItemIdentifier)==None:
                item.parentItem.removeItem(item)
                destItem.addItem(item)

















