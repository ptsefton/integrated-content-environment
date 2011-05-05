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

import urllib



class ImsItem(object):
    """ IMS Item """
    # ImsItem
    #  Constructor:
    #    ImsItem(parent, [resource], [itemXmlNode])
    #  Properties:
    #    rep (ReadOnly)
    #    parentItem (R/W)
    #    startPath (ReadOnly)
    #    identifier (ReandOnly)
    #    identifierRef (ReadOnly)
    #    isWordDoc (ReadOnly)
    #    title (R/W)
    #    isVisible (R/W)
    #    expanded (R/W)
    #    resources (ReadOnly)
    #    resource (ReadOnly)
    #    href (ReadOnly)
    #    isDefaultItem (ReadOnly)
    #    items
    #  Methods:
    #    setAsDefaultItem([set=True])
    #    addItem(item, [index])
    #    addItemBeforeItem(addItem, beforeItem)
    #    removeItem()
    #    getAllChildItems()
    #    getItem(identifier)
    #    getItemByIdRef(idRef)
    #    load(itemNode)
    #    serialize(xml)
    #    getNextItem([lookDown=True)
    #    getPreviousItem()
    #    addBeforeMe(item)
    #
    def __init__(self, parent, resource=None, itemXmlNode=None):
        self.__parent = parent
        self.__resource = None
        self.__resources = None
        self.__identifierRef = ""
        self.__identifier = ""
        self.__title = ""
        self.__isVisible = True
        self.__items = []
        
        self.__expanded = False
        
        # This bit still needs to be refactored
        if resource!=None:
            self.__resource = resource
            self.__identifierRef = resource.identifier
            self.__identifier = self.makeIdentifier(self.__identifierRef)
            href = resource.href
            repPath = resource.repPath
            item = self.rep.getItemForUri(repPath)
            if item.hasMeta("title"):
                self.__title = item.getMeta("title")
                if self.__title is None or self.__title=="":
                    self.__title = ""
            else:
                self.__title = "[%s]" % self.iceContext.fs.split(href)[1]
                if href=="toc.htm" or href=="default.htm":
                    self.__isVisible = False

        if itemXmlNode!=None:
            self.load(itemXmlNode)
                
            #self.resource
        if resource==None and itemXmlNode==None:
            #print "No data!!!"
            pass
    
    
    @property
    def iceContext(self):
        return self.__parent.iceContext
    
    
    @property
    def rep(self):
        return self.__parent.rep
    
    
    @property
    def resources(self):
        if self.__resources is None:
            self.__resources = self.__parent.resources
        return self.__resources
    
    
    @property 
    def resource(self):
        if self.__resource==None:
            self.__resource = self.resources[self.__identifierRef]
        return self.__resource
    
    
    @property
    def startPath(self):
        return self.__parent.startPath
    
    
    @property
    def parent(self):
        return self.__parent
    
    
    @property
    def href(self):
        res = self.resource
        if res is None:
            return None
        return res.href
    
    
    # Note: parentItem is overwritten in ims_organization class to return None
    def __getParentItem(self):
        return self.__parent
    def __setParentItem(self, value):
        self.__parent = value
    parentItem = property(__getParentItem, __setParentItem)


    def __getIdentifier(self):
        return self.__identifier
    identifier = property(__getIdentifier)
    
    
    def makeIdentifier(self, idRef):
        return self.__parent.makeIdentifier(idRef)
    
    
    def __getIdentifierRef(self):        # refers to the identifier of the resource item
        return self.__identifierRef
    identifierRef = property(__getIdentifierRef)
    

    def __getIsWordDoc(self):
        res = self.resource
        if res!=None and res.exists:
            return res.isWordDoc
        return False
    isWordDoc = property(__getIsWordDoc)
    
    
    def __getTitle(self):
        title = self.__title
        if title=="":
            href = self.href
            if href is None:
                title = "** Has NO resource **"
            else:
                title = "[%s] Untitled " % self.iceContext.fs.split(href)[1]
        return title
    def __setTitle(self, value):
        if value is None:
            value = ""
        self.__title = value.strip()
    title = property(__getTitle, __setTitle)
    
    
    def __getIsVisible(self):
        return self.__isVisible
    def __setIsVisible(self, value):
        self.__isVisible = value
    isVisible = property(__getIsVisible, __setIsVisible)
    
    
    def __getExpanded(self):
        return self.__expanded
    def __setExpanded(self, value):
        self.__expanded = value
    expanded = property(__getExpanded, __setExpanded)
    
    
    # Protected property - for use by imsOrganization
    def __getItems(self):
        return self.__items
    _items = property(__getItems)
    
    
    def addItem(self, item, index=9999):
        self.__items.insert(index, item)
        item.parentItem = self
        return True
    
    
    def addItemBeforeItem(self, addItem, beforeItem):
        try:
            index = self.__items.index(beforeItem)
            self.__items.insert(index, addItem)
            addItem.parentItem = self
            return True
        except:
            return False
    
    def remove(self):
        """ Remove itself from it's parent """
        parent = self.parentItem
        if parent is not None:
            parent.removeItem(self)
            
    def removeItem(self, item):
        """ Removes this item from its list of child items """
        self.__items.remove(item)
    
    
    def getAllChildItems(self):
        items = list(self.__items)    # clone self.__items
        for item in self.__items:
            items.extend(item.getAllChildItems())    # extend with all of its children
        return items
    
    
    def getItem(self, identifier):
        if identifier == self.__identifier:
            return self
        for item in self.__items:
            if item.identifier==identifier:
                return item
            else:
                i = item.getItem(identifier)
                if i!=None:
                    return i
        return None
    
        
    def getItemByIdRef(self, idRef):
        # NOTE: returns the first item found with this idRef
        if self.__identifierRef==idRef:
            return self
        for item in self.__items:
            if item.identifierRef==idRef:
                return item
            else:
                i = item.getItemByIdRef(idRef)
                if i!=None:
                    return i
        return None
    
    
    def __getIsDefaultItem(self):
        return self.__identifier.endswith("-default")
    isDefaultItem = property(__getIsDefaultItem)
    
        
    def setAsDefaultItem(self, set=True):
        if set:
            if not self.isDefaultItem:
                # clear the current default item (if one exists)
                parentItem = self
                while parentItem.parentItem!=None:
                    parentItem = parentItem.parentItem
                item = parentItem.getDefaultItem()
                if item!=None:
                    item.setAsDefaultItem(False)
                self.__identifier += "-default"
        else:
            if self.__identifier.endswith("-default"):
                self.__identifier = self.__identifier[:-len("-default")]
    
    
    def load(self, itemNode):
        """itemNode can be an item or an organization"""
        #print "ims_item.load()"
        self.__identifier = itemNode.getAttribute("identifier")
        self.__identifierRef = itemNode.getAttribute("identifierref")
        if itemNode.getAttribute("isvisible") and itemNode.getAttribute("isvisible").lower()=="false":
            self.__isVisible = False
        else:
            self.__isVisible = True
        self.__title = itemNode.getContent("./*[local-name()='title']")
        # sub items
        itemNodes = itemNode.getNodes("./*[local-name()='item']")
        ids = []
        for subItem in itemNodes:
            item = ImsItem(self)
            subIds = item.load(subItem)
            ids.extend(subIds)
            ids.append(item.identifier)
            self.addItem(item)
        if self.__title.endswith("] Untitled "):
            res = self.resource           
            if res is not None: 
                mTitle = self.rep.getItem(res.repPath).getMeta("title")
                if mTitle is not None and mTitle!="":
                    self.__title = mTitle
        return ids
    
    
    def serialize(self, xml):
        node = xml.createElement(elementName="item", elementContent=None, \
            identifier=self.__identifier, identifierref=self.__identifierRef, \
            isvisible=str(self.__isVisible).lower())
        #print "Title=", self.title
        node.addContent("\n")
        titleNode = xml.createElement(elementName="title", elementContent=self.title)
        node.addChild(titleNode)
        node.addContent("\n")
        for item in self.__items:
            n = item.serialize(xml)
            node.addChild(n)
            node.addContent("\n")
        return node


    def __str__(self):
        xml = self.iceContext.Xml("<root/>")
        node = self.serialize(xml)
        s = str(node)
        xml.close()
        return s
        
    
#    def getIdentifierList(self):
#        idList = [self.__identifier]
#        for item in self.__items:
#            idList.extend(item.getIdentifierList())
#        return idList


    #===================================
    def getNextItem(self, lookDown=True):
        next = self.__getNextItem(lookDown)
        if next==None:
            return None
        res = next.resource
        if res==None:
            return next
        if self.iceContext.fs.splitExt(res.href)[1] != ".htm":
            return next.getNextItem(lookDown)
        return next
    
    
    def __getNextItem(self, lookDown=True):
        if self.parentItem==None:
            return None
        if lookDown and len(self.__items)>0:
            return self.__items[0]
        items = self.parentItem.__items
        selfIndex = items.index(self)
        nextIndex = selfIndex + 1
        if nextIndex==len(items):
            return self.parentItem.getNextItem(lookDown=False)
        else:
            return items[nextIndex]
    
    
    def getPreviousItem(self):
        prev = self.__getPreviousItem()
        if prev==None:
            return None
        res = prev.resource
        if res==None:
            return prev
        if self.iceContext.fs.splitExt(res.href)[1] != ".htm":
            return prev.getPreviousItem()
        return prev
    
    
    def __getPreviousItem(self):
        if self.parentItem==None:
            return None
        items = self.parentItem.__items
        selfIndex = items.index(self)
        if selfIndex==0:
            return self.parentItem
        return items[selfIndex-1]
    
    
    def addBeforeMe(self, item):
        try:
            index = self.parentItem._items.index(self)
            self.parentItem.addItem(item, index)
            return True
        except:
            return False
    
    
    def getItemContextPath(self, results=[]):   # called by ims_organization.getContextPath()
        packagePath = self.startPath
        if self.parentItem is not None:
            href = self.resource.href
            fullPath = self.iceContext.url_join(packagePath, href)
            self.parentItem.getItemContextPath(results)
            if href!="toc.htm":
                results.append( (fullPath, self.title) )
    
    
    def getHtmlList(self, xml=None, expandItem=None, recurse=False):
        returnStr = False
        if xml is None:
            xml = self.iceContext.Xml("<root/>")
            returnStr = True
        
        if len(self.__items)>0:
            listItems = []
            for item in self.__items:
                if item.isVisible:
                    listItems.extend(item.__getHtmlListItem(xml, expandItem, recurse))
            if len(listItems)>0:
                ulNode = xml.createElement("ul", style="list-style-type: none")
                ulNode.addChildren(listItems)
                if returnStr:
                    s = str(ulNode)
                    xml.close()
                    return s
                else:
                    return ulNode
        if returnStr:
            xml.close()
            return ""
        else:
            return None
    
    
    def __getHtmlListItem(self, xml, expandItem=None, recurse=False):
        res = self.resource
        url = None
        if res!=None and res.exists:
            if res.href=="toc.htm" or res.href=="default.htm":
                return ""
            url = self.startPath + res.href
            #sourceFileName = url.replace(".htm", self.iceContext.oooDefaultExt)
            item = self.rep.getItemForUri(url)
            repTitle = item.getMeta("title")
            if repTitle is None:
                repTitle = "[" + self.iceContext.fs.split(res.href)[1] + "]"
        else:
            # resource does not exist
            pass
        liNodes = [xml.createElement("li")]
        
        if res!=None and res.exists:
            if not url.startswith("/"):
                url = "/" + url
            aNode = xml.createElement("a", elementContent=self.title, href=urllib.quote(url))
            liNodes[0].addChild(aNode)
        else:
            liNodes[0].setContent(self.title)
        if (expandItem is self) or recurse:
            ulNode = self.getHtmlList(xml, recurse=recurse)  # may return None
            if ulNode!=None:
                liNodes[0].addChild(ulNode)
        return liNodes    
    
    
    def __getItems(self):
        return self.__items
    items = property(__getItems)

