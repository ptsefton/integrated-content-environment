
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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
import pickle
import base64
import time

#from ims_organizer import ImsOrganizer


pluginName = "ice.function.editManifestOld"
pluginDesc = "Manifest editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    path = iceContext.fs.split(__file__)[0]
    ImsOrganizer.myPath = path
    pluginFunc = edit_manifest
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def isPackage(self):
    return self.isPackage    

def isClient(self):
    return not self.iceContext.isServer

# Organize (manifest)
def edit_manifest(self):
    #__refresh(self)
    path = self.packagePath
    if path=="":
        path = self.path
    # ReRender to update 'Title' meta data
    result = self.rep.getItem(path).render(force=False, skipBooks=True)
    
    mf = self.getImsManifest()
    if mf is not None:
        imsOrg = ImsOrganizer(mf, "default", self.formData)
        body = imsOrg.getEditableHtmlList()
        self["body"] = body
        self['title'] = "Package organizer"
    else:
        return
#edit_manifest.options={"toolBarGroup":"common", "position":14, "postRequired":False,
#                    "enableIf":isPackage, "label":"_Organizer",
#                    "title":"Organize content and edit titles",
#                    "destPath":"%(package-path)s"+"edit_manifest"}



class ImsOrganizer:
    myPath = ""                     # injected data
    TemplateFilename = "ims-organizer.tmpl"
    
    # package == organization
    def __init__(self, mf, orgName, formData):
        self.iceContext = mf.iceContext
        self.rep = mf.rep
        self.__fs = self.iceContext.fs
        self.__mf = mf
        self.__idCount = 0
        # Get organization
        self.__org = mf.organizations[orgName]
        self.__formData = formData
        self.__selected = []
        self.__edit = None
        self.__state = None
        self.__baseUrlFeedback = None
        #print "*** ImsOrganizer.__init()"
        if formData.has_key("ispostback") and formData.method=="POST":
            if formData.has_key("state"):
                # Restore state
                stateStr = formData.value("state")
                self.__state = _State.restore(stateStr)
        else:
            #print "  ImsOrganizer.__init__() update and saving"
            self.__mf.update()
            self.__mf.save()
        
        if self.__state==None:
            # else create a new state object
            self.__state = _State(None)
            self.__state.expanded = {}
            
        self.__package = self.__org
        expanded = self.__state.expanded
        for item in self.__package.getAllChildItems():
            if expanded.has_key(item.identifier):
                item.expanded = expanded[item.identifier]
            
        if formData.has_key("ispostback") and formData.method=="POST":
            self.__processFormData(formData)
            if self.__package==self.__org:
                self.save()
                
        for item in self.__package.getAllChildItems():
            self.__state.expanded[item.identifier] = item.expanded
    
    
    def getEditableHtmlList(self):
        org = self.__package
        items = []
        def addItems(orgItems, newItemList):
            for orgItem in orgItems:
                if orgItem.href is not None:
                    if orgItem.href=="toc.htm" or orgItem.href=="default.htm":
                        continue
                res = orgItem.resource
                i = self.iceContext.Object()
                i.id = orgItem.identifier
                i.convertFlag = False
                i.isVisible = orgItem.isVisible
                i.isDefaultItem = orgItem.isDefaultItem
                i.isWordDoc = orgItem.isWordDoc
                
                url = orgItem.startPath + orgItem.href
                item = self.rep.getItemForUri(url)
                repTitle = item.getMeta("title")
                if repTitle==None:
                    repTitle = "[" + self.iceContext.fs.split(orgItem.href)[1] + "]"
                i.repTitle = self.iceContext.textToHtml(repTitle)
                i.title = self.iceContext.textToHtml(orgItem.title)
                i.eTitle = i.title
                if res is not None:
                    item = self.rep.getItem(res.repPath)
                    title = item.getMeta("title")
                    if title is not None:
                        i.eTitle = title
                    if item.convertFlag:
                        i.convertFlag = True                
                i.href = self.iceContext.textToHtml(orgItem.href, includeSpaces=False).replace("'", "&apos;")
                i.expanded = orgItem.expanded
                i.edit = (self.__edit==orgItem)
                i.entries = []
                if len(orgItem.items)>0:
                    addItems(orgItem.items, i.entries)
                newItemList.append(i)
        addItems(org.items, items)
        
        package = self.__package
        editPackage = False
        if self.__edit==self.__package:
            editPackage = True
        d = { "stateStr":self.__state.getStateStr(),
              "title":self.iceContext.textToHtml(org.title), 
              "entries":items, 
              "editPackage":editPackage, 
              "package":package,  
            }
        file = self.__fs.join(self.myPath, self.TemplateFilename)
        htmlTemplate = self.iceContext.HtmlTemplate(templateFile=file)
        allowMissing = True
        html = htmlTemplate.transform(d, allowMissing=allowMissing)
        if htmlTemplate.missing!=[]:
            print "----"
            print "Missing items for template='%s'" % str(htmlTemplate.missing)
            print "----"
        #print html
        return html
    
    
    def save(self):
        self.__mf.save()
    
    
    def __processFormData(self, formData):
        actx = formData.value("actx")
        data = formData.value("data")
        if actx=="":
            d = formData.value("movehere")
            if d!="":
                actx = "movehere"
                data = d
            d = formData.value("movebefore")
            if d!="":
                actx = "movebefore"
                data = d
            if formData.has_key("ok"):
                actx = "ok"
                data = formData.value("editId")
        if formData.has_key("selected"):
            self.__selected = formData.values("selected")
            
        #print "actx=", actx
        #print " data=", data
        package = self.__package
        pItem = package.getItem(data)    # ById
        if pItem is not None:
            item2 = self.rep.getItem(pItem.resource.repPath)
        else:
            item2 = None
            if actx=="ok":
                actx = "okPackage"
        if actx=="minmax":
            pItem.expanded = not pItem.expanded
        elif actx=="movehere" and data=="top":
            for id in self.__selected:
                i = package.getItem(id)
                if i!=None:
                    p = i.parentItem
                    p.removeItem(i)
                    package.addItem(i)
            self.__selected = []
        elif actx=="movehere":
            for id in self.__selected:
                i = package.getItem(id)
                #Do not allow to move to itself
                if pItem != i:
                    if i!=None:
                        p = i.parentItem
                        p.removeItem(i)
                        pItem.addItem(i)
            self.__selected = []
        elif actx=="movebefore":
            beforeItem = pItem
            pItem = beforeItem.parentItem
            if beforeItem!=None:
                for id in self.__selected:
                    i = package.getItem(id)
                    if i==beforeItem:
                        continue
                    if i!=None:
                        p = i.parentItem
                        p.removeItem(i)
                        pItem.addItemBeforeItem(addItem=i, beforeItem=beforeItem)
            self.__selected = []
        elif actx=="edit":
            if pItem is None:
                self.__edit = package
            else:
                self.__edit = pItem
        elif actx=="ok":
            title = formData.value("title")
            hide = formData.has_key("hide")
            homePage = formData.has_key("homePage")
            pItem.title = title
            pItem.isVisible = not hide
            if homePage:
                for i in package.getAllChildItems():
                    if i.isDefaultItem:
                        i.setAsDefaultItem(False)
                pItem.setAsDefaultItem(True)
                package.setAsDefaultItem(False)
            else:
                if pItem.isDefaultItem:
                    pItem.setAsDefaultItem(False)
                    package.setAsDefaultItem(True)
            if pItem.isWordDoc:
                render = formData.has_key("render")
                item2.convertFlag = render
                item2.flush()
        elif actx=="okPackage":
            # Package (organization) edit
            title = formData.value("title")
            homePage = formData.has_key("homePage")
            package.title = title
            if homePage:
                for i in package.getAllChildItems():
                    if i.isDefaultItem:
                        i.setAsDefaultItem(False)
                package.setAsDefaultItem(True)
        elif actx=="expandAll":
            package.expandAll()
        elif actx=="minimizeAll":
            package.minimizeAll()


class _State:
    # this is a state-full object
    """ This (class) object's state is saved between requests """
    def __init__(self, package):
        self.package = package
    
    def restore(klass, stateStr):
        str = base64.decodestring(stateStr)
        obj = pickle.loads(str)
        return obj
    restore = classmethod(restore)
    
    def getStateStr(self):
        """ serialize and encode self (state) """
        str = pickle.dumps(self)
        str = base64.encodestring(str)
        return str



class _Package:
    def __init__(self, org):
        self.identifier = org.identifier
        self.title = org.title
        self.items = []
        
        for item in org.items:
            i = _Item(item)
            i.parentItem = self
            self.items.append(i)
        # get all items
        items = list(self.items)
        for item in self.items:
            items.extend(item.getAllChildItems())
        self.__allItems = {}    # id, item
        for item in items:
            self.__allItems[item.identifier] = item
        defaultItem = org.getDefaultItem()
        if defaultItem==None:
            self.__default = True
        else:
            self.__default = False
            defaultId = defaultItem.identifier

    def __getIsDefaultItem(self):
        return self.__default
    isDefaultItem = property(__getIsDefaultItem)

    def setAsDefaultItem(self, set):
        self.__default = set
        
    def getItem(self, identifier):
        if self.__allItems.has_key(identifier):
            return self.__allItems[identifier]
        return None
        
    def getAllChildItems(self):
        return self.__allItems.values()

    def removeItem(self, item):
        self.items.remove(item)
        item.parentItem = None

    def addItem(self, item):
        self.items.append(item)
        item.parentItem = self
    
    def addItemBeforeItem(self, addItem, beforeItem):
        index = self.items.index(beforeItem)
        self.items.insert(index, addItem)
        addItem.parentItem = self
    
    def minimizeAll(self):
        for item in self.__allItems:
            item.expanded = False
    
    def expandAll(self):
        for item in self.__allItems:
            item.expanded = True
    
    def save(self):
        pass
    
    def __str__(self):
        str = "Package - Title='%s', id='%s'" % (self.title, self.identifier)
        if self.default:
            str += " (Default)"
        return str

    def toString(self):
        s = str(self) + "\n"
        for item in self.items:
            s += item.toString(1)
        return s    


class _Item:
    def __init__(self, item):
        self.expanded = False
        
        self.identifier = item.identifier
        self.title = item.title
        self.isVisible = item.isVisible
        self.href = None
        self.isWordDoc = False
        self.items = []
        self.parentItem = None
        
        self.__startPath = item.startPath
        #self.__documentType = item.getDocumentType()
        self.__convertFlag = item.getConvertFlag()
        self.__default = item.isDefaultItem
        res = item.getResource()
        if res!=None and res.exists:
            self.href = res.href
            self.isWordDoc = res.isWordDoc()
            
        for i in item.items:
            i2 = _Item(i)
            i2.parentItem = self
            self.items.append(i2)
    
    def __getIsDefaultItem(self):
        return self.__default
    isDefaultItem = property(__getIsDefaultItem)
        
    def setAsDefaultItem(self, set):
        self.__default = set
    
    def getAllChildItems(self):
        items = list(self.items)
        for item in self.items:
            items.extend(item.getAllChildItems())
        return items
    
    def __getStartPath(self):
        return self.__startPath
    startPath = property(__getStartPath)
    
    def removeItem(self, item):
        self.items.remove(item)
        item.parentItem = None

    def addItem(self, item):
        self.items.append(item)
        item.parentItem = self
    
    def addItemBeforeItem(self, addItem, beforeItem):
        index = self.items.index(beforeItem)
        self.items.insert(index, addItem)
        addItem.parentItem = self
    
    def getConvertFlag(self):
        return self.__convertFlag
    
    def setConvertFlag(self, state):
        self.__convertFlag = state
    
    def __str__(self):
        str = "Item - Title='%s', id='%s'" % (self.title, self.identifier)
        if self.__default:
            str += " (default)"
        return str
        
    def toString(self, level=0):
        s = "\t" * level + str(self) + "\n"
        for item in self.items:
            s += item.toString(level+1)
        return s








