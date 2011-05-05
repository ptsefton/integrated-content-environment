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


import types, string
from hashlib import md5
import time
import ims_resources
import ims_organizations


class imsError(Exception) : pass
class imsFileError(imsError) : pass


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]


    
class ImsManifest(object):
    # ImsManifest
    #  Constructor:
    #    ImsManifest(iceContext, startPath="/", filename=None, includeSource=False)
    #  Properties:
    #    rep (ReadOnly)
    #    organizations (ReadOnly)
    #    resources (ReadOnly)
    #    parent (ReadOnly)
    #    startPath (ReadOnly)
    #    defaultOrganization (ReadOnly)
    #    filename
    #    title              (ReadOnly -
    #    
    #  Methods:
    #    update()
    #    load(manifest=None)
    #    save(filename=None)
    #    
    
    # Factory
    @staticmethod
    def getManifest(iceContext, mfItem, includeSource=False, forceCreate=False):
        mf = None
        createdManifest = False
        modifiedDate = mfItem.lastModifiedDateTime
        mfName = "%s-%s-%s/%s" % \
            (iceContext.rep.name, mfItem.relPath, includeSource, modifiedDate)
        mfcache = iceContext.cache.get("manifest")
        if mfcache is not None and mfcache[0]==mfName:
            #print "loading manifest from cache"
            mf = mfcache[1]
        if mf is None:
            #mf = ImsManifest(iceContext, packagePath, includeSource=includeSource)
            mf = ImsManifest(iceContext, mfItem, includeSource=includeSource)
            mf.cacheName = mfName
            iceContext.cache["manifest"] = (mfName, mf)
            if forceCreate:
                createdManifest = True
            else:
                try:
                    mf.load()
                except Exception, e:
                    msg = str(e)
                    print "ims_manifest.getManifest() load error"
                    if msg.endswith("not found!"):
                        createdManifest = True
                    else:
                        raise e
            if createdManifest:
                try:
                    mf.update()
                    mf.save()
                except Exception, e:
                    print "update() or save() error"
                    raise e
        return mf, createdManifest
    
    
    # Create ImsManifest form an ICE Manifest object
    @staticmethod
    def createImsManifest(iceContext, packageItem, manifest, 
                includeSource=False, includeSkin=True):
        # create a dummy imsItem for the constructor
        imsItem = iceContext.Object()
        imsItem.parentItem = iceContext.Object()
        imsItem.parentItem.relPath = packageItem.relPath
        imsItem.parentItem.walk = packageItem.walk
        imsManifest = ImsManifest(iceContext, imsItem, includeSource)
        resources = imsManifest.resources
        org = imsManifest.defaultOrganization
        org.title = manifest.title
        def getItem(i):
            name = i.renditionName
            if name=="":                    ## for external ice content
                name = i.relPath
            iitem = org.addFileItem(name)
            iitem.title = i.title
            iitem.isVisible = not i.isHidden
            org.removeItem(iitem)
            return iitem
        def addChildren(imsItem, mItem):
            for i in mItem.children:
                iitem = getItem(i)
                imsItem.addItem(iitem)
                addChildren(iitem, i)
        # First add resources
        def addResource(renditionName):
            res = resources.createResource(renditionName)
            resources.addResource(res)
        def addResources(mItem):
            for i in mItem.children:
                name = i.renditionName
                if name=="":                    ## for external ice content
                    name = i.relPath
                addResource(name)
                addResources(i)
        addResources(manifest)
        addResource("toc.htm")
        addResource("default.htm")
        skinItem = packageItem.getChildItem("skin")
        rootSkinItem = iceContext.rep.getItem("skin")
        skinItems = {}
        for items in skinItem.walk(filesOnly=True):
            for item in items:
                relPath = item.relPath[len(packageItem.relDirectoryPath):]
                skinItems[relPath] = relPath
        for items in rootSkinItem.walk(filesOnly=True):
            for item in items:
                relPath = item.relPath[1:]
                skinItems[relPath] = relPath
        for relPath in skinItems.iterkeys():
            #Make sure .svn folder is not included
            if relPath.find(".svn")<0:
                addResource(relPath)
        addChildren(org, manifest)
        return imsManifest
    
    
    ImsResources = ims_resources.ImsResources
    ImsOrganizations = ims_organizations.ImsOrganizations
    def __init__(self, iceContext, imsItem, includeSource=False):
        #print "\n-- imsManifest init --"
        self.iceContext = iceContext
        self.__parent = None
        startPath = imsItem.parentItem.relPath
        if not startPath.endswith("/"):
            startPath += "/"
        self.__startPath = startPath
        self.__resources = self.ImsResources(self, includeSource=includeSource)
        self.__organizations = self.ImsOrganizations(self)
        self.__imsItem = imsItem
        self.__loadedMD5 = None
        self.__includesource = includeSource
        #self.__item = 
    
    
    @property
    def rep(self):
        return self.iceContext.rep
    
    
    @property
    def organizations(self):
        return self.__organizations
    
    
    @property
    def resources(self):
        return self.__resources
    
    
    @property
    def parent(self):
        return None
    
    
    @property
    def startPath(self):
        return self.__startPath
    
    
    @property
    def defaultOrganization(self):
        return self.__organizations.defaultOrganization
    
    
    @property
    def title(self):
        return self.defaultOrganization.title
    
    
    def load(self, manifestXmlStr=None):
        #print
        #print "IMS load()"
        t = time.time() 
        if manifestXmlStr is None:
            manifestXmlStr = self.__imsItem.read()
        if manifestXmlStr is None:
            r = self.update()
            self.save()
            return r
        r = self.__load(manifestXmlStr)
        print " IMS load() done. '%s'" % (time.time()-t)
        if False:    ## For testing Pickling
            iceContext = self.iceContext
            try:
                self.iceContext = None
                self.__resources.iceContext = None
                self.__organizations.iceContext = None
                
                data = iceContext.dumps(self)
                print "  size=%s" % len(data)
            except Exception, e:
                print "Error pickling ims_manifest - '%s'" % str(e)
            self.iceContext = iceContext
            self.__resources.iceContext = iceContext
            self.__organizations.iceContext = iceContext
            print " IMS load()2 done. '%s'" % (time.time()-t)
            try:
                obj = iceContext.loads(data)
            except Exception, e:
                print "error - %s" % str(e)
            print " IMS load()3 done. '%s'" % (time.time()-t)
        return r
    
    def __load(self, manifestXmlStr):
        manifestDom = None
        manifestNode = None
        
        # load the manifest XML into the DOM and get the root node
        try:
            doctypeStr = """<!DOCTYPE manifest SYSTEM "imscp_rootv1p1.dtd" >"""
            manifestXmlStr = manifestXmlStr.replace(doctypeStr, "")
            manifestDom = self.iceContext.Xml(manifestXmlStr, imsNSList)
            manifestNode = manifestDom.getNode("/")
            manifestSize = "Manifest size=%sK" % str( (len(manifestXmlStr)+512)/1024 )
            self.__loadedMD5 = self.__getMD5(manifestXmlStr)
        except Exception, e:
            msg = "IMS Load Error, error loading the manifest XML : - " + str(e.__class__)
            msg += "\n%s" % str(e)
            raise Exception(msg)
        
        try:
            # Deserialize the resources from the DOM  (self.__resources)
            resNode = manifestNode.getNode(".//*[local-name()='resources']")
            # Create and load new resources
            res = self.ImsResources(self, includeSource=self.__includesource)
            res.load(resNode, update=False)
            self.__resources = res
            
            # Also create a new organizations object (using the new resources object)
            self.__organizations = self.ImsOrganizations(self)
            
            # Deserialize the organizations  (self.__organizations)
            orgsNodes = manifestNode.getNodes(".//*[local-name()='organizations']")
            self.__organizations.load(orgsNodes[0])
            
            # HACK to be fixed up -refactored out
            #OK now remove any items that do not have resources associated with it
            for org in self.__organizations.values():
                delItems = []
                for item in org.getAllChildItems():
                    if item.resource==None:
                        delItems.append(item)
                for item in delItems:
                    org.deleteItem(item)
            
            if manifestDom!=None:
                manifestDom.close()
        except Exception, e:
            print "IMS Load Error: - " + str(e.__class__)
            errText = self.iceContext.formattedTraceback()
            print errText
            print "-----"
            print
    
    
    def update(self):
        #print
        #print "IMS Update()"
        t = time.time() 
        r = self.__update()
        print " IMS Update() done. '%s'" % (time.time()-t)
        return r
    
    def __update(self):
        #st = time.time()
        #print "__update() build step"
        organization = self.defaultOrganization
        for listItems in self.__imsItem.parentItem.walk(filesOnly=True):  # ~ 2/3
            for item in listItems:
                #print "item.relPath='%s'" % item.relPath
                # do not do root level elements e.g. index, manifest.xml, *.dtd, *.zip etc
                # BUT do include master documents *.odm
                ## And do not include /src/ files
                if item.relPath.find("/src/")!=-1:
                    continue
                notList = [".zip", ".xml", ".dtd", ".odm"]
                if self.iceContext.fs.split(item.relPath)[0]==self.__startPath[:-1]:
                    ext = item.ext
                    if ext in notList:
                        continue
                if item.isIgnored:
                    continue
                self.__createAndAddItem(organization, item)
        # Add toc.htm and default.htm
        fileName = self.iceContext.url_join(self.__startPath, "toc.htm")
        i = self.rep.getItem(fileName)
        self.__createAndAddItem(organization, i)
        fileName = self.iceContext.url_join(self.__startPath, "default.htm")
        i = self.rep.getItem(fileName)
        self.__createAndAddItem(organization, i)
        # Add skin files 
        def addFiles(path):
            rPath = self.iceContext.url_join(self.__startPath, path)
            #print "*** addFiles('%s') rPath='%s'" % (path, rPath)
            item = self.rep.getItem(rPath)
            for listItems in item.walk(filesOnly=True):
                for i in listItems:
                    self.__createAndAddItem(organization, i)
        addFiles("/skin")
        
        #print "__update() build step done in %s" % (time.time()-st)
        #st = time.time()
        #print "__update() remove missing step"
        
        # Remove missing items and resources step
        # Remove missing resources and items   NOTE: item == imsItem
        for res in self.__resources.values():
            res.update()
            if not res.exists:
                print "Resource href='%s' does not exist - removing" % res.href
                self.__resources.removeResource(res)
        for item in organization.getAllChildItems():
            if item.resource==None:
                print "ImsItem has no resource! (removing) title='%s'" % item.title
                # Remove
                organization.deleteItem(item)
            elif item.resource.exists==False:
                print "ImsItem's resource does not exist (removing) title='%s'" % item.title
                # Remove
                organization.deleteItem(item)
        #print "__update() remove missing step done in %s" % (time.time()-st)
        #print "__update() done"
    
    
    def save(self, imsItem=None):
        #raise Exception("imsManifest.save() called")
        #print "IMS Save"
        xml = self.serialize()
        md5 = self.__getMD5(xml)
        
        if imsItem is None:
            imsItem = self.__imsItem
        # Only save if there are changes to be saved
        if self.__loadedMD5!=md5:
            # save the changes
            # write to file
            print "saving imsManifest"
            self.__loadedMD5 = md5
            imsItem.write(xml)
        else:
            # Data is unchanged, no need to save
            pass
    
    
    def __createAndAddItem(self, organization, item):
        """create an item from the given filename and add this item to self"""
        ext = item.ext
        name = item.relPath[:-len(ext)]
        if name.startswith(self.__startPath):
            name = name[len(self.__startPath):]
        if item:
            if item.hasHtml:
                ext = ".htm"
            elif item.hasPdf:
                ext = ".pdf"
        href = name + ext
        
        # Add to the resources
        if not self.__resources.containsResource(href):
            # adds or replaces the resource with an updated one
            #print "createResource href='%s'" % href
            res = self.__resources.createResource(href)
            if res.href!=href:
                raise Exception("href's differ, possible unknown type.")
            if res.exists:
                # Only add resources that exists
                #print "adding Resource href='%s'" % href
                self.__resources.addResource(res)
            else:
                return
        else:
            pass
            #resource = self.__resources.getResourceByHref(href)
            #resource.update()
        
        # Add to the organization unless in a skin, media or src directory
        if      href.startswith("skin/") or href.find("/skin/")>-1 or \
                href.startswith("src/") or href.find("/src/")>-1 or \
                href.startswith("media/"):
            return
        # only adds to organization if organization does not contain this item
        organization.addFileItem(href)
    
    
    def __getMD5(self, data=None):
        if data==None:
            data = self.serialize()
        m = md5(data)
        return m.hexdigest()
    
    
    def __getCaller(self):
        # (filename, line#, methodName, lineStr)
        return traceback.extract_stack(limit=3)[0]
    
    
    def serialize(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8" ?>
        <!DOCTYPE manifest SYSTEM "imscp_rootv1p1.dtd" >
  <manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" identifier="MANIFEST-6971EFA4-1391-578F-D1CE-39875264E76A" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p2.xsd">
  <metadata>
  <schema>IMS Content</schema>
  <schemaversion>1.2.2</schemaversion>
  </metadata>
  </manifest>
"""
        xml = self.iceContext.Xml(xmlStr, imsNSList)
        node = xml.getRootNode()
        node.addContent("\n")
        node.addChild(self.__organizations.serialize(xml))
        node.addContent("\n")
        node.addChild(self.__resources.serialize(xml))
        node.addContent("\n")
        
        s = str(xml)
        xml.close()
        return s

    def __str__(self):
        return self.serialize()







