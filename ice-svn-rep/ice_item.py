#
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

from hashlib import md5
import re
import types
import time



class IceItem(object):
    # Constructor:
    #   __init__(iceContext, uriOrRelPath, other={})
    # Properties:
    #   guid                                            # ReadOnly
    #   uri                                             # ReadOnly
    #   name                                            # ReadOnly
    #   [extension]                                     # ReadOnly
    #   relPath                                         # ReadOnly
    #   relDirectoryPath                                # ReadOnly
    #   _absPath                                        # ReadOnly
    #   _propAbsPath                                    # ReadOnly
    #   exists                                          # ReadOnly
    #   sameNameAlreadyExists  e.g. there is another item that differs only by its extension
    #   isFile                                          # ReadOnly
    #   isDirectory                                     # ReadOnly
    #   isHidden                                        # ReadOnly  (not isVisible)
    #   isVersioned                                     # ReadOnly
    #   isMissing                                       # ReadOnly
    #   hasProperties       (canHaveProps)
    #   isMyChanges                                     # ReadOnly   # FileOnly (else False)
    #
    #   lastModifiedDateTime                            # ReadOnly
    #   lastChangedRevisionNumber                       # ReadOnly
    #   vcStatusStr                                     # ReadOnly
    #   vcStatus            # VersionControlStatus      # ReadOnly
    #   
    #   metaNames                                       # ReadOnly
    #   hasPdf                                          # ReadOnly
    #   hasHtml                                         # ReadOnly
    #   hasSlide                                        # ReadOnly
    #   displaySourceType                               # ReadOnly
    #   needsUpdating                                   # ReadOnly
    #   tags                # a list of tagNames        # ReadOnly (list only, note the list can still be changed)
    #   inlineAnnotations                               # ReadOnly
    #   convertFlag                                     # Read/Write
    #   inPackage                                       # ReadOnly
    #   isPackageRoot       (???) (plus site properties)
    #   
    #
    # Methods:
    #   getNamedItem(name)
    #   hasRendition(ext)
    #   add()
    #   read()                                                      # FileOnly (else raise Exception)
    #   write(data)                                                 # FileOnly (else raise Exception)
    #   listItems(update=False)       -> list of IceItems           # DirOnly (else ?)
    #   makeDirectory(message="mkdir")                              # DirOnly (non-exists)  (else raise Exception)
    #   delete()
    #   remove()
    #   revert()
    #   
    #   getLogData(levels=None)
    #   sync(...)                                   # high level
    #   update(...)
    #   commit(relPathList, message="commit")       # low level
    #   move(toIceItem)
    #   copy(toIceItem)
    #   export(absDestinationPath)
    #   
    #   extractFromZip(itemName)                                # (Zip)FileOnly (else raise Exception)
    #   replaceFileInZip(itemName, data)                            # (Zip)FileOnly (else raise Exception)
    #   zipFromTempDir(absTempDir)                                  # (zip)FileOnly (else raise Exception)
    #   unzipToTempDir()                                            # (Zip)FileOnly (else raise Exception)
    #   
    #   walk(fileExts=None, excludeExts=False)      # DirOnly (else ?)
    #   
    #   getStatus(update=False)
    #   _getCurrentMd5()
    #   setConvertedData(convertedData)
    #   getRendition(extension)
    #   getImage(name)
    #   hasMeta(name)
    #   removeMeta(name)
    #   setMeta(name, value)
    #   getMeta(name)
    #
    #   setTags(tags)                           # should not know about Tags!
    
    # callback method
    #  callback(item=None, displayMessage=None, step=None, exception=None, method=None, **extras)
    #           item = current working item
    #           displayMessage = message string to be displayed to user
    #           step = string - current processing step e.g. "rendering", or "done render"
    #           exception = exception if any - this may need be be raised if it can not be handled
    #           method = current method (optional)
    #           **extras = extra arguments
    #       Note: raise an IceCancelException() to cancel an opertion
    
    __mineCopyNamePrefix = "myChanges_"
    
    @staticmethod
    def hasPropertiesTest(relPath):
        noPropDirs = [".ice", "src", "temp", ".userData", ".cache", "skin"]
        pathParts = relPath.split("/")[1:]
        filename = pathParts.pop()
        for p in pathParts:
            if p in noPropDirs:
                return False
        return True
    
    
    @staticmethod
    def isHiddenTest(relPath):
        # any directory or file starting with a '.' e.g. ".svn", ".ice", ".site", ".indexes", ".cache", ".userData"
        relPath = relPath.strip("/")
        hiddenDirectories = ["skin"]
        for df in relPath.split("/"):
            if df.startswith("."):
                return True
            if df in hiddenDirectories:
                return True
        if relPath=="favicon.ico":
            return True
        if relPath.endswith("imscp_rootv1p1.dtd"):
            return True
        return False
    
    
    @staticmethod
    def ignoreTest(relPath):
        relPath = relPath.strip("/")
        name = relPath.rsplit("/", 1)[-1]
        ignoreStartsWith = ["~$", ".nfs", ".~"]        # and self.__mineCopyNamePrefix  ??? (always ignored in walker() method )
        ignore = [".DS_Store", "Thumbs.db", ".indexes", ".cache", ".temp"]
        ignoreEndsWith = ["~", ".tmp", ".mime", ".prej", ".pyc"]
        if name in ignore:
            return True
        for x in ignoreStartsWith:
            if name.startswith(x):
                return True
        for x in ignoreEndsWith:
            if name.endswith(x):
                return True
        return False
    
    
    @staticmethod
    def GetIceItem(iceContext, relPath):
        # Normalize path
        if type(relPath) not in types.StringTypes:
            raise Exception("relPath argument is not a string type!")
        relPath = iceContext.normalizePath(relPath)
        if relPath is None:
            raise Exception("relPath can not be None!")
        item = IceItem(iceContext, IceItem.hasPropertiesTest, 
                        IceItem.isHiddenTest, IceItem.ignoreTest)
        item.__setup(relPath)
        return item
    
    
    @staticmethod
    def GetIceItemForUri(iceContext, uri):
        # Note: if uri does not start with '/skin/' but contains '/skin/' and
        #       that file does not exist then remap to the root /skin/
        if uri.find("/skin/")>0:
            absPath = iceContext.rep.getAbsPath(uri)
            if not iceContext.fs.isFile(absPath):
                uri = uri[uri.find("/skin/"):]
        item = IceItem.__GetIceItemForUri(iceContext, uri)
        # Check for file download request (and remap if so)
        if item.isDirectory and (item.relPath!=item.uri):
            match = re.search("(.*?)_i([0-9a-fA-F]+)r(\-?\d+)(\..*)", uri)
            if match is not None:
                a, pathId, revNum, b = match.groups()
                item = IceItem.GetIceItemForUri(iceContext, a+b)
        return item
    
    
    @staticmethod
    def __GetIceItemForUri(iceContext, uri):
        if type(uri) not in types.StringTypes:
            raise Exception("uri argument is not a string type!")
        item = IceItem.GetIceItem(iceContext, uri)
        if item.exists and not item.isMissing:
            item.__uri = uri
            return item
        parentItem = item.parentItem
        while (parentItem is not None) and ((not parentItem.exists) or parentItem.isMissing):
            if parentItem.isFile:
                parentItem.__uri = uri
                return parentItem
            item = parentItem
            parentItem = item.parentItem
        if parentItem is None:
            parentItem = item
        relPath = item.relPath
        name, ext = iceContext.fs.splitExt(item.name)
        ext = ext.lower()
        if ext in iceContext.rep.render.renderedExtensions or ext==".mp3":
            # rendintion check
            # from parentItem item get renderable item with name (only no ext) of name
            item = parentItem.getNamedItem(name)
            if item is not None and item.hasXRendition(ext):
                item.__uri = uri
                return item
            elif item is not None and item.convertFlag:
                item.__uri = uri
                return item
        if ext==".htm":
            if name in ["toc", "default", "index"]:
                item = parentItem
                item.__uri = uri
                return item
            if name.endswith(".slide"):
                # slide check
                name, ext2 = iceContext.fs.splitExt(name)
                item = parentItem.getNamedItem(name)
                if item is not None and item.hasSlide:
                    item.__uri = uri
                    return item
        if ext==".dc" and name=="toc":
            item = parentItem
            item.__uri = uri
            return item
        if (ext=="" and name.endswith("_files")) or ext.endswith("_files"): # incase the filename has '.' in it!
            # image/media files check
            n = item.name
            n = n[:-len("_files")]
            # from parentItem item get renderable item with name (only no ext) of n
            item = parentItem.getNamedItem(n)
            if item is not None:
                item.__uri = uri
                return item
        # else just return the found parent item
        item = parentItem
        item.__uri = uri
        item.__uriNotFound = True
        return item
    
    
    
    def __init__(self, iceContext, hasPropertiesTest, isHiddenTest, ignoreTest):
        self.iceContext = iceContext
        self.__hasPropertiesTest = hasPropertiesTest
        self.__isHiddenTest = isHiddenTest
        self.__ignoreTest = ignoreTest
        
        self.__fs = iceContext.rep.fs
        self.__svnRep = iceContext.rep._svnRep
        self.__name = None
        self.__uri = None
        self.__relPath = None
        self.__absPath = None
        self.__propAbsPath = None
        self.__isFile = False
        self.__isDir = False
        self.__isHidden = None
        self.__isIgnored = None
        self.__isVersioned = None
        self.__hasProperties = False
        self.__isMyChanges = False
        self.__vcStatus = None
        self.__isMissing = False
        self.__uriNotFound = False
        self.__parentItem = None
        #
        self.__metaDict = None              # dictionary
        self.__metaChanged = False
        # tags
        self.__tagsChanged = False
        self.__tagList = None
        self.__inlineAnnotations = None
        # skin
        self.__isSkinDir = False
    
    
    def __setup(self, relPath=None, vcStatus=None):
        self.__vcStatus = vcStatus
        self.__isMissing = False
        if relPath is None:
            relPath = self.__relPath
        iceContext = self.iceContext
        rep = iceContext.rep
        fs = self.__fs
        relPath = iceContext.normalizePath(relPath)
        if relPath.startswith("."):
            if relPath.startswith("./"):
                relPath = relPath[1:]
            #if relPath.startswith(".skin/"):
        if not relPath.startswith("/"):
            relPath = "/" + relPath
        self.__absPath = rep.getAbsPath(relPath)
        self.__name = fs.split(relPath)[1]
        self.__relPath = relPath
        self.__isSkinDir = self.__name == "skin"
        if fs.isDirectory(self.__absPath):
            self.__isDir = True
            if not relPath.endswith("/"):
                relPath += "/"
                self.__relPath = relPath
        elif fs.isFile(self.__absPath):
            self.__isFile = True
        else:
            ## May be missing or incomplete - Check now
            status = self.vcStatus
            statusStr = self.vcStatusStr
            if status is not None:
                #print "May be missing relPath='%s' isDir=%s '%s'" % (relPath, status.isDir, str(status))
                self.__isFile = status.isFile
                self.__isDir = status.isDir
                if self.__isDir and not relPath.endswith("/"):
                    relPath += "/"
                if statusStr!="missing" and statusStr not in ["deleted", "unversioned"]:
                    print "**** may be missing but status is '%s'" % status
                if statusStr not in ["deleted", "unversioned"]:
                    self.__isMissing = True
        self.__relPath = relPath
        self.__uri = relPath
        self.__hasProperties = self.__hasPropertiesTest(relPath)
        self.__propAbsPath = self.__getPropAbsPath()
        #rep.getAbsPath(relPath)
    
    
    def reload(self):
        self.__setup()
    
    
    @property
    def isSkinDir(self):
        return self.__isSkinDir
    
    
    @property
    def guid(self):
        if self.hasProperties==False:
            return None
        try:
            id = self.__meta["_guid"]
            return id
        except Exception, e:
            print "---"
            print str(e)
            print "relPath='%s'" % self.relPath
            print "__meta.keys()='%s'" % self.__meta.keys()
            print "---"
            raise
    
    
    @property
    def name(self):
        if self.__name is None:
            self.__name = self.iceContext.fs.split(self.__relPath)[1]
            if self.isDirectory:
                self.__name += "/"
        return self.__name
    
    @property
    def ext(self):
        return self.iceContext.iceSplitExt(self.name)[1]
    
    @property
    def uri(self):
        return self.__uri
    
    
    @property
    def uriDiff(self):
        # returns any extra content on the uri (after the '/')
        ##return self.__uri[len(self.__relPath):].lstrip("/")
        uri = self.__uri.strip("/")
        relPath = self.__relPath.strip("/")
        relPathParts = relPath.split("/")
        uriParts = uri.split("/")
        l = len(relPathParts)
        r = "/".join(uriParts[l:])
        if r!="" and uriParts[l-1].endswith("_files"):
            r = "_files/" + r
        return r
    
    
    @property
    def relPath(self):
        return self.__relPath
    
    
    @property
    def relDirectoryPath(self):
        if self.__relPath.endswith("/"):
            return self.__relPath
        return self.__relPath[:-len(self.name)]
    
    
    ## This needs refactoring ********
    @property
    def thisUri(self):
        if self.isDirectory:
            thisUri = self.relPath
        else:
            thisUri = self.relDirectoryPath
            thisUri = "/".join(self.uri.split("/")[:thisUri.count("/")+1])
        return thisUri
    
    
    @property
    def _absPath(self):
        return self.__absPath
    
    
    @property
    def _propAbsPath(self):
        return self.__propAbsPath
    
    
    @property
    def exists(self):
        return self.isFile or self.isDirectory
    
    
    @property
    def isFile(self):
        return self.__isFile
    
    @property
    def isDir(self):
        return self.__isDir
    @property
    def isDirectory(self):
        return self.__isDir
    
    
    @property
    def sameNameAlreadyExists(self):
        raise Exception("Not yet implemented!")             ####
        return None
    
    
    @property
    def isHidden(self):
        if self.__isHidden is None:
            self.__isHidden = self.__isHiddenTest(self.relPath) or self.isIgnored
        return self.__isHidden
    
    
    @property
    def isIgnored(self):
        if self.__isIgnored is None:
            self.__isIgnored = self.__ignoreTest(self.relPath)
        return self.__isIgnored
    
    
    @property
    def hasProperties(self):
        try:
            if self.isIgnored or self.isHidden or self.isMyChanges:
                return False
        except:
            print "Error relPath='%s'" % self.relPath
        return self.__hasProperties
    
    
    @property
    def isMyChanges(self):
        return self.__name.startswith(self.__mineCopyNamePrefix)
    
    
    @property
    def lastModifiedDateTime(self):
        if self.exists==False:
            return 0
        if self.__fs.exists(self.__absPath)==False:
            return 0
        try:
            return self.__fs.getModifiedTime(self.__absPath)
        except:
            return 0
    
    @property
    def metaNames(self):
        return [n for n in self.__meta.keys() if not n.startswith("_")]
    
    @property
    def displaySourceType(self):
        return self.getMeta("_displaySourceType", False)
    
    @property
    def hasPdf(self):
        return self.hasXRendition(".pdf")
    
    @property
    def hasHtml(self):
        result = self.hasXRendition(".htm")
        if result==True:
            n, ext = self.iceContext.iceSplitExt(self.__name)
            if ext==".book.odt":
                book = self.bookInfo
                if book is not None:
                    try:
                        result = book.renderAsHtml
                    except: 
                        result = False
                else:
                    result = False
                return result
        # Hack: for .html and image files that are marked as HTM (convertFlag)
        if self.convertFlag:
            return True
        return result
    
    @property
    def hasText(self):
        return self.hasHtml()
    
    @property
    def hasSlide(self):
        return self.getMeta("isSlide")
    
    @property
    def hasAudio(self):
        if self.getMeta("_renderAudio") and self.convertFlag:
            #data = self.getRendition(".mp3") # this causes a conversion to MP3
            #return data != None
            # isTextToSpeechAvailable
            TtsPlugin = self.iceContext.getPluginClass("ice.extra.textToSpeech")
            if TtsPlugin is not None:
                tts = TtsPlugin(self.iceContext)
                return tts.isTextToSpeechAvailable
        return False
    
    
    def __getConvertFlag(self):
        """ Return True|False|None 
            Note: Just because the convertFlag is True does not mean that it is renderable
                only if convertFlag AND isRenderable are true should the item be rendered.
        """
        state = self.getMeta("_iceDoc")
        if state==None and self.isFile:
            # default value
            state = self.isRenderable
            if state and self.relPath.find("/media/")!=-1:
                state = False
        return state
    def __setConvertFlag(self, value):
        self.setMeta("_iceDoc", value)
    convertFlag = property(__getConvertFlag, __setConvertFlag)
    
    
    @property
    def isRenderable(self):     # Ignores the convertFlag state
        if self.isFile==False:
            return False
        ext = self.__fs.splitExt(self.__name)[1]
        if self.iceContext.rep.render.isExtensionRenderable(ext):
            if self.isHidden:
                return False
            if self.__propAbsPath is None:
                return False
            # is this item in a non-renderable location (path)
            return True
        return False
    
    
    @property
    def needsUpdating(self):
        if self.hasProperties==False:
            return False
        msgLines = []
        msgLines.append("needsUpdating checking '%s'" % self.__relPath)
        result = False
        try:
            lastSaved = self._lastSaved
            if lastSaved==None:
                lastSaved = -1
        except:
            lastSaved = -1
        modifiedTime = self.lastModifiedDateTime
        try:
            if not self.isFile:
                result = False
                return False
            # does this extension support any rendering e.g. to .htm, .pdf etc.
            if not self.isRenderable:
                msgLines.append(" not a renderable item!")
                result = False
                return False
            elif self.convertFlag==False:
                msgLines.append(" convertFlag is False!")
                result = False
                return False
            elif modifiedTime!=lastSaved:
                msgLines.append("  modifiedTime!=lastSaved")
                lastMd5 = self.__lastRenderedMd5
                if lastMd5 is None:
                    msgLines.append("  lastMd5 is None!")
                    result = True
                    return True
                currentMd5 = self._getCurrentMd5()
                if currentMd5 is None:
                    msgLines.append(" currentMD5 is None!")
                    result = False
                    return False
                if currentMd5==lastMd5:
                    msgLines.append("  different timestamp but same MD5")
                    self.lastSaved = modifiedTime       # just reset lastSaved
                    result = False
                else:
                    msgLines.append("  needs updating because MD5 differ")
                    result = True
            else:
                msgLines.append("  modifiedTime == lastSaved")
                result = False
            if self.iceContext.iceSplitExt(self.__relPath)[1] in \
                                                self.iceContext.bookExts:
                book = self.bookInfo
                if book is None:
                    msgLines.append("  no bookInfo found!")
                    result = False
                elif book.needsRendering:
                    if book.needsBuilding:
                        msgLines.append("  book document needs building and rendering")
                    else:
                        msgLines.append("  book document needs rendering")
                    result = True
        finally:
            pass
            #print "\n".join(msgLines) + "\n Result='%s'" % result
        return result
    
    
    @property
    def tags(self):
        return list(self.__tags)
    
    @property
    def __tags(self):
        if self.__tagList is None:
            self.__tagList = self.__readTags()
        return self.__tagList
    
    @property
    def taggedBy(self):
        return list(self.__taggedBy)
    
    @property
    def __taggedBy(self):
        taggedBy = self.getMeta("_taggedBy", [])
        return taggedBy
    
    
    @property
    def inlineAnnotations(self):
        if self.__propAbsPath is None:
            return None
        if self.__inlineAnnotations is None:
            inlineAnnoPath = self.__fs.join(self.__propAbsPath, 
                                                "inline-annotations")
            accessObj = self.__getDirOnlyAccessObject(inlineAnnoPath)
            IceInlineAnnotations = self.iceContext.IceInlineAnnotations
            if IceInlineAnnotations is not None:
                self.__inlineAnnotations = IceInlineAnnotations(accessObj)
            else:
                return None
        return self.__inlineAnnotations
    
    def __getDirOnlyAccessObject(self, path):
        obj = self.iceContext.Object()
        # writeFile(), readFile(), exists() (isDirectory), listFiles(), path
        def writeFile(filename, data):
            file = self.__fs.join(path, filename)
            self.__fs.writeFile(file, data)
            # add parent dir first
            self.__svnRep.add(path)
            self.__svnRep.add(file)    # Note: this could be optimized!
        obj.writeFile = writeFile
        def readFile(filename):
            file = self.__fs.join(path, filename)
            return self.__fs.readFile(file)
        obj.readFile = readFile
        def deleteFile(filename):
            file = self.__fs.join(path, filename)
            self.__svnRep.delete(file)
        obj.deleteFile = deleteFile
        def exists():
            return self.__fs.isDirectory(path)
        obj.exists = exists
        def listFiles():
            return self.__fs.listFiles(path)
        obj.listFiles = listFiles
        obj.path = path
        return obj
    
    
    @property
    def description(self):
        desc = self.getMeta("_description", None)
        if desc is None:
            desc = "[description has not been set!]"
            desc = ""
            html = self.getRendition(".xhtml.body")
            if html is not None and html!="":
                xml = self.iceContext.Xml(html)
                pNode = xml.getNode("//p")
                if pNode is not None:
                    desc = pNode.content
                    if len(desc)>180:
                        desc = desc[:150] + "..."
                xml.close()
        return desc
    def setDescription(self, description):
        self.setMeta("_description", description)
    
    
    #Note: "_lastModified.tmp" is NOT kept under version control 
    #   It is for local usage only.
    def __getLastSaved(self):
        if self.__propAbsPath is None:
            return None
        pname = self.__getPropertyName("_lastModified.tmp")
        data = self.__fs.readFile(pname)
        if data is not None:
            try:
                data = self.iceContext.loads(data)
            except:
                data = None
        return data
    def __setLastSaved(self, value):
        if self.__propAbsPath is None:
            return
        if self.__metaDict is None:
            if self.__readProperty("meta") is None:
                return -1
        pname = self.__getPropertyName("_lastModified.tmp")
        data = self.iceContext.dumps(value)
        self.__fs.writeFile(pname, data)
    _lastSaved = property(__getLastSaved, __setLastSaved)
    
    
    @property
    def bookInfo(self):
        data = self.getMeta("_bookInfo")
        if data is None:
            return None
        obj = self.iceContext.loads(data)
        obj.iceContext = self.iceContext
        return obj
    
    
    def setBookInfo(self, bookInfo):
        data = self.iceContext.dumps(bookInfo)
        self.setMeta("_bookInfo", data)
        return self
    
    
    @property
    def parentItem(self):
        if self.__parentItem is None:
            relPath = self.relPath
            if relPath=="/":
                return None
            if relPath.endswith("/"):
                relPath = relPath[:-1]
            relPath = self.__fs.split(relPath)[0]
            self.__parentItem = self.getIceItem(relPath)
        return self.__parentItem
    
    
    @property
    def inPackage(self):        # isPackage or inPackage???
        parent = self.parentItem
        return self.isPackageRoot or \
                (parent is not None and parent.inPackage)
    
    
    @property
    def isPackageRoot(self):
        # Hack: This is a dum way to test for package root
        #   and needs to be refactored (also the inPackage property)
        if self.isDirectory:
            manifest = self.getMeta("manifest")
            if manifest is not None:
                return True
            manifestItem = self.getChildItem("manifest.xml")
            return  manifestItem.isFile
        return False
    
    
    @property
    def packageRootItem(self):
        if self.inPackage:
            parent = self.parentItem
            while parent is not None and not parent.isPackageRoot:
                parent = parent.parentItem
            return parent
        else:
            return self
    
    @property
    def uriNotFound(self):
        return self.__uriNotFound
    
    
    #========== public methods ================
    
    def getIdUrl(self):
        rep = self.iceContext.rep
        serverData = rep.serverData
        name, ext = self.iceContext.iceSplitExt(self.__name)
        idRev = ""
        if serverData is not None:
            #id = serverData.getIdForRelPath(self.__relPath)
            id = serverData.getIdForRelPath(self.relDirectoryPath)
            ## get this items revision number. NOTE: may be -1 if only Added
            rev = self.lastChangedRevisionNumber
            idRev = "_i%sr%s" % (hex(id)[2:], rev)
        return name + idRev + ext
    
    
    def getIceItem(self, relPath):
        return IceItem.GetIceItem(self.iceContext, relPath)
    
    
    def getNamedItem(self, name):
        """ returns an (file) item with a name only (not including ext) of 'name' or None if none found. """
        files = self.__fs.glob("%s.*" % name, self.__absPath)
        if files==[]:
            return None
        else:
            filename = self.__fs.split(files[0])[1]
            relPath = self.__fs.join(self.relPath, filename)
            item = self.getIceItem(relPath)
            item.__parentItem = self
            return item
    
    
    def getChildItem(self, name):
        """ returns a file or directory child item with the given name (including ext)
            note: the item may not yet exist. """
        relPath = self.__fs.join(self.relPath, name)
        item = self.getIceItem(relPath)
        if name.find("/")==-1:
            item.__parentItem = self
        return item
    
    
    def setTags(self, tags):
        """ tags can be a list of tagNames or a string of whitespace delimited tagNames """
        if type(tags) is types.StringType:
            tags = tags.split()
        
        # remove duplicate tags  If tags differ only by case then delete the first tag(s) in list order
        tags = dict(zip([tag.lower() for tag in tags], tags)).values()
        tags.sort()
        
        orgTags = self.tags
        if orgTags!=tags:       # Test for any differences
            self.__tagList = tags
            self.__tagsChanged = True        
    
    
    def setTaggedBy(self, taggedBy):
        taggedBy.sort()
        if taggedBy!=self.__taggedBy:
            self.setMeta("_taggedBy", taggedBy)
    
    
    def touch(self):
        self._lastSaved = ""
        self.__setLastRenderedMd5(None)
    
    
    def _getCurrentMd5(self):
        data = self.read()
        if data is None:
            return False
        currentMd5 = md5(data).hexdigest()
        return currentMd5
    
    
    def removeMeta(self, name):
        meta = self.__meta
        if meta.has_key(name):
            del(meta[name])
            self.__metaChanged = True
    
    
    def setMeta(self, name, value):
        if self.__propAbsPath is None:
            return
        if value is None:
            self.removeMeta(name)
        else:
            if self.__meta.get(name, None)!=value:
                #print "setting meta '%s' to '%s'" % (name, value)
                self.__meta[name] = value
                self.__metaChanged = True
    
    
    def getMeta(self, name, value=None):
        if self.__propAbsPath is None:
            return value
        if name=="toc":
            value = self.__meta.get(name, "")
        else:
            value = self.__meta.get(name, value)
        return value
    
    
    def hasMeta(self, name):
        if self.__propAbsPath is None:
            return False
        return self.__meta.has_key(name)
    
    
    def getRendition(self, extension):
        if self.__propAbsPath is None:
            return None
        if extension==".xhtml.body":
            if self.convertFlag:
                ext = self.__fs.splitExt(self.__name)[1]
                if ext in [".jpg", ".png", ".gif"]:
                    html = "<div style='padding:1em;'>" + \
                            "<img src='%s' alt='%s'><!-- --></img></div>" % \
                            (self.__relPath, self.__name)
                    return html
                elif ext in [".html", ".htm"]:
                    data = self.__fs.readFile(self.__absPath)
                    clean = self.iceContext.HtmlCleanup.convertHtmlToXml(data)
                    xml = self.iceContext.Xml(clean, parseAsHtml=True)
                    # get the title
                    titleNode = xml.getNode("//title")
                    if titleNode is None:
                        self.removeMeta("title")
                    else:
                        self.setMeta("title", titleNode.getContent())
                    self.flush()
                    # get script elements outside in the head
                    scriptNodes = xml.getNodes("//head/script")
                    # get the body
                    bodyNode = xml.getNode("//body")
                    bodyNode.setName("div")
                    # insert script nodes in the body
                    firstChild = bodyNode.getFirstChild()
                    if firstChild is None:
                        bodyNode.addChildren(scriptNodes)
                    else:
                        for scriptNode in scriptNodes:
                            firstChild.addPrevSibling(scriptNode)
                    
                    #clean up space in href for cmap html
                    ### TODO: normalize the xpath to be more specific
                    aHref = xml.getNodes("//*[@href != '']")
                    for a in aHref:
                        hrefVal = a.getAttribute("href").strip()
                        a.setAttribute("href", hrefVal)
                    
                    html = str(bodyNode)
                    xml.close()
                    return html
        name = "rendition" + extension
        data = self.__readProperty(name)
        if extension in [".text", ".mp3"] and data is not None:
            pname = self.__getPropertyName(name)
            if self.__fs.getModifiedTime(pname) < self.lastModifiedDateTime:
                data = None
                #print "'%s' rendition will be updated" % extension[1:]
        if data is None:
            # on demand rendition creation
            if extension==".text":
                #print "\n**prop.getRendition(extension='%s')" % extension
                htmlData = self.getRendition(".xhtml.body")
                if htmlData is None:
                    # render first
                    print ".xhtm.body not found - re-rendering now"
                    self.render(True, False)
                    htmlData = self.getRendition(".xhtml.body")
                if htmlData is not None:
                    HtmlToText = self.iceContext.getPlugin("ice.extra.html2text").pluginFunc
                    data = HtmlToText(htmlData)
                self.__setRendition(extension, data)
            if extension==".mp3" and self.getMeta("_renderAudio"):
                text = self.getRendition(".text")
                if text is not None:
                    TtsPlugin = self.iceContext.getPluginClass("ice.extra.textToSpeech")
                    if TtsPlugin is not None:
                        tts = TtsPlugin(self.iceContext)
                        try:
                            data = tts.textToSpeech(text)
                        except Exception, e:
                            msg = str(e)
                            if msg.lower().find("text to speech service not available")!=-1:
                                return None
                            else:
                                raise Exception("Error in 'ice.extra.textToSpeech' plugin - '%s'" % str(e))
                        self.__setRendition(extension, data)
                else:
                    print "text rendition not found for '%s'" % self.relPath
        return data
    
    def __setRendition(self, extension, rendition):
        if extension not in self.__meta["_renditions"]:
            self.__meta["_renditions"].append(extension)
            self.__metaChanged = True
        name = "rendition" + extension
        self.__writeProperty(name, rendition)
    
    def hasRendition(self, extension):
        if self.__propAbsPath is None:
            return False
        name = "rendition" + extension
        pname = self.__getPropertyName(name)
        r = self.__fs.isFile(pname)
        if r==False and extension==".text":
            r = self.hasRendition(".xhtml.body")
        return r
    
    def hasXRendition(self, ext):
        result = False
        myExt = self.__fs.splitExt(self.__name)[1]
        renditions = list(self.iceContext.rep.render.getRenderableTypes(myExt))
        if self.hasAudio:
            renditions.append(".mp3")
        if ext in renditions:
            result = self.convertFlag
        return result
    
    
    def _setImage(self, name, data):
        name = "image-" + name
        if name not in self.__meta["_images"]:
            self.__meta["_images"].append(name)
            self.__metaChanged = True
        self.__writeProperty(name, data)
    
    
    def getImage(self, name):
        name = "image-" + name        
        return self.__getImage(name)
    
    
    def __getImage(self, name):
        data = self.__readProperty(name)
        
        if data is None:
            data = self.__readProperty(name + ".tmp")
            if data is None:
                # try and get image size info from image name
                m = re.search(r"(.*?)_(\d+)x(\d+)((bw)?)(\..*)", name)
                if m!=None:
                    fileName = m.group(1) + m.group(6)
                    imageExt = m.group(6)
                    bw = m.group(5)
                    size = (self.iceContext.strToInteger(m.group(2)), \
                                self.iceContext.strToInteger(m.group(3)))
                    data = self.__getImage(fileName)
                    if data!=None:
                        im = self.iceContext.IceImage(data)
                        if bw is not None:
                            if im.getSize()!=size:
                                data = im.bwResizeImage(size)
                        else:
                            if im.needsResizing(size):
                                data = im.resizeImage(size)
                        im = None
                if data!=None:
                    self._setImage(name + ".tmp", data)
        return data
    
    
    def setConvertedData(self, convertedData):
        # delete unused renditions, images, and (some) metaData
        renditionNames = self.getMeta("_renditions")
        imageNames = self.getMeta("_images")
        metaNames = self.metaNames
        
        if self.hasProperties:
            # delete all *.tmp files
            files = self.__fs.listFiles(self.__propAbsPath)
            files = [file for file in files if file.endswith(".tmp")]
            for file in files:
                self.__fs.delete(self.__fs.join(self.__propAbsPath, file))
        # delete all image's that are not in the new results
        for name in set(imageNames).difference(convertedData.imageNames):
            self.__deleteProperty(name)
        # delete all rendition's that have not been regenerated
        for name in set(renditionNames).difference(convertedData.renditionNames):
            self.__deleteProperty(name)
        for name in metaNames:
            self.removeMeta(name)
        self.__meta["_images"] = []
        self.__meta["_renditions"] = []
        self.__metaChanged = True
        
        # Add all the new data
        for name in convertedData.metaNames:
            data = convertedData.getMeta(name)
            self.setMeta(name, data)
        for name in convertedData.imageNames:
            data = convertedData.getImage(name)
            self._setImage(name, data)
        for name in convertedData.renditionNames:
            data = convertedData.getRendition(name)
            self.__setRendition(name, data)
        
        # Update renderedMD5 and _lastSaved
        renderedFileTime = convertedData.renderedTime
        renderedFileMD5 = convertedData.renderedMD5
        if renderedFileTime is None:
            renderedFileTime = self.lastModifiedDateTime
        if renderedFileMD5 is None:
            renderedFileMD5 = self._getCurrentMd5()
        self._lastSaved = renderedFileTime
        self.__setLastRenderedMd5(renderedFileMD5)        
        self.__getStatus()
        return self
    
    
    def flush(self, force=False):
        if self.isMissing:
            return self
        if self.__metaChanged or force:
            self.__saveMeta()
        if self.__tagsChanged:
            self.__saveTags()
        return self
    
    
    def close(self):
        return self.flush()
    
    
    def __list(self, update=False):
        l = self.iceContext.rep._svnRep.list(self.__absPath, update)
        name = self.__fs.split(self.__absPath)[1]
        if ".ice/" in l:
            l.remove(".ice/")
        if "./" in l:
            l.remove("./")
        def unUnicode(s):
            if type(s) is types.UnicodeType:
                return s.encode("utf-8")
            return s
        l = [unUnicode(i) for i in l]
        return l    
    
    
    
    def listItems(self, update=False):     # For directories only
        # return a list of items (with status)
        l = []
        if self.isFile:
            return [self]
        if not self.isDirectory:
            return l
        names = self.__list(update)
        for name in names:
            name = self.__fs.join(self.relPath, name)
            iceItem = self.getIceItem(name)
            l.append(iceItem)
        return l
    
    
    def write(self, data):
        dir = self.__fs.split(self.__absPath)[0]
        if not(self.__fs.exists(dir)):
            self.parentItem.makeDirectory()
        self.__fs.writeFile(self.__absPath, data)
        self.add()
        return self
    
    
    def read(self):
        data = None
        absPath = self.__absPath
        if self.isFile:
            data = self.__fs.readFile(absPath)
            ## Hack if can not find in skin try .skin
            if data is None:
                data = self.__fs.readFile(absPath.replace("/skin/", "/.skin/"))
        elif self.__fs.isFile(absPath.replace("/skin/", "/.skin/")):
            data = self.__fs.readFile(absPath.replace("/skin/", "/.skin/"))
        ##
        else:
            rFileName = self.__relPath
            index = rFileName.find("/skin/")
            if index>0:
                fileName = rFileName[index:]
                absFilename = self.iceContext.rep.getAbsPath(fileName)
                data = self.__fs.readFile(absFilename)
        return data
    
    
    def makeDirectory(self, message="mkdir", ignore=False):
        if self.exists:
            return False
        self.parentItem.makeDirectory(message)
        self.iceContext.rep._svnRep.makeDirectory(self._absPath, svnIgnore=ignore)
        self.__setup(self.__relPath)
        guid = self.guid
    
    
    def getLogData(self, levels=None):
        """ Returns a logData object or a list of logData objects levels is given
            The logData object has the following properties:
                date -    (string)
                message - (string)
                author -  (string)
                revisionNumber - (integer)
        """
        return self.iceContext.rep._svnRep.getLogData(self.__absPath, levels)
    
    
    ####################
    ####################
    
    def getCompleteStatus(self):
        return self.vcStatus.getCompleteStatus()
    
    @property
    def vcStatus(self):
        if self.__vcStatus is None:
            self.__vcStatus = self.__getStatus()
        return self.__vcStatus
    
    @property
    def vcStatusStr(self):
        vcStatus = self.vcStatus
        if vcStatus is None:
            return "?"
        return vcStatus.statusStr
    
    @property
    def lastChangedRevisionNumber(self):
        return self.vcStatus.lastChangedRevisionNumber
        
    @property
    def isVersioned(self):
        return self.vcStatus.isVersioned
    
    @property
    def isMissing(self):
        return self.__isMissing
    
    @property
    def isDeleted(self):
        return self.vcStatusStr=="deleted"
    
    @property
    def hasChanges(self):
        svn = self.iceContext.rep._svnRep
        r = False
        if self.isFile:
            r = svn.hasChanges(self.__absPath)
            if r==False and self.__propAbsPath is not None:
                r = svn.hasChanges(self.__propAbsPath)
        elif self.isDirectory:
            r = svn.hasChanges(self.__absPath)
            #if r==False and self.__propAbsPath is not None:
            #    r = svn.hasChanges(self.__propAbsPath)
            #if not r:
            #    for item in self.listItems():
            #        if item.hasChanges:
            #            r = True
            #            break
        return r
    
    
#    def remove(self):
#        # First check that all content has been committed
#        #   do not remove Added, Deleted, Modified content
#        p, l = self.__getCommitItemList(searchDepth=True)  #  returns a tuple (listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths)
#        if l!=[] or p!=[]:
#            raise self.iceContext.IceException("Can not remove modified content!")
#        self.__fs.delete(self.__absPath)
#        if self.__propAbsPath is not None:
#            self.__fs.delete(self.__propAbsPath)
#        self.__setup(self.relPath)
    
    
    def shelve(self):
        if self.isDirectory:
            # First check that all content has been committed
            #   do not remove Added, Deleted, Modified content
            p, l, u = self.__getCommitItemList(searchDepth=True)  #  returns a tuple (listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths)
            if l!=[] or p!=[]:
                raise self.iceContext.IceException("Can not remove modified content!")
            self.__fs.delete(self.__absPath)
            if self.__propAbsPath is not None:
                self.__fs.delete(self.__propAbsPath)
            # update self (empty)
            #self._update()  #FIXME _update would restore the directory being shelved
            ##
            if False:
                svn = self.iceContext.rep._svnRep
                svn.updateEmpty(absPath)
            ##
            self.__setup(self.relPath)
        #else:
        #    raise self.iceContext.IceException("Can only shelve a direcotry")
    
    
    def add(self, recurse=True):
        # first make sure that my parent is added
        #if self.__relPath.endswith("/media") or self.__relPath.find("/media/")!=-1:
        #    #print "not adding media"
        #    return
        parentItem = self.parentItem
        if parentItem is not None and not parentItem.isVersioned:
            parentItem.add()
        r = None
        svn = self.iceContext.rep._svnRep
        if not self.isIgnored:
            paths, rPaths = self.__getAddPaths(recurse=recurse)
            r = svn.add(paths)
            r2 = svn.add(rPaths, recurse=True)
            self.__setup()
        return r
    
    def __getAddPaths(self, recurse=True, paths=[], rPaths=[]):
        if not self.isIgnored:
            guid = self.guid
            self.__setup()
            if self.exists:
                paths.append(self._absPath)
                if self.__propAbsPath is not None:
                    paths.append(self.__fs.split(self.__propAbsPath)[0])
                    rPaths.append(self.__propAbsPath)
            if self.isDirectory:
                for item in self.listItems():
                    if item.isFile:
                        guid = item.guid
                        paths.append(item._absPath)
                        if item.__propAbsPath is not None:
                            rPaths.append(item.__propAbsPath)
                    elif item.isDirectory and recurse:
                        item.__getAddPaths(recurse, paths, rPaths)
        return paths, rPaths
    
    
    def delete(self):
        id = self.guid
        svn = self.iceContext.rep._svnRep
        r = svn.delete(self.__absPath)
        if r==False:
            self.__fs.delete(self.__absPath)
        if self.__propAbsPath is not None:
            r = svn.delete(self.__propAbsPath)
            if r==False:
                self.__fs.delete(self.__absPath)
        self.iceContext.rep.indexer.deleteIndex(id)
    
    
    def remove(self):
        self.__fs.delete(self.__absPath)
        if self.__propAbsPath is not None:
            self.__fs.delete(self.__propAbsPath)
    
    
    def revert(self):
        svn = self.iceContext.rep._svnRep
        svn.revert(self.__absPath)
        if self.__propAbsPath is not None:
            svn.revert(self.__propAbsPath)
    
    
    def move(self, destItem):
        #print "ice_item.move()"
        absPath = self.__absPath
        absDestPath = destItem.__absPath
        if self.__fs.exists(absDestPath):
            raise Exception("destination '%s' already exists" % absDestPath)
        parentItem = destItem.parentItem
        if parentItem is not None and parentItem.exists==False:
            destItem.parentItem.makeDirectory()
        svn = self.iceContext.rep._svnRep   # same as self.__svnRep
        #destItem.add()
        if self.isDirectory:
            # OK just move the directory
            svn.move(absPath, absDestPath)
        elif self.isFile:
            # OK we need to move the file and the properties
            #self.__svnRep.move(absPath, absDestPath)
            self.__svnRep.move(absPath, absDestPath)
            # Properties
            if self.__propAbsPath is not None:
                absDestPath = "/.ice/".join(destItem.__absPath.rsplit("/", 1))
                self.__svnRep.move(self.__propAbsPath, absDestPath)
        else:
            return
        self.iceContext.rep.indexer.reIndex(destItem)
    
    
    def copy(self, destItem, annotation=False):
        absPath = self.__absPath
        absDestPath = destItem.__absPath
        if self.__fs.exists(absDestPath):
            raise Exception("destination '%s' already exists" % absDestPath)
        parentItem = destItem.parentItem
        if parentItem is not None and parentItem.exists==False:
            destItem.parentItem.makeDirectory()
        svn = self.iceContext.rep._svnRep
        if self.isDirectory:
            svn.copy(absPath, absDestPath)
        elif self.isFile:
            svn.copy(absPath, absDestPath)
            destItem.__setup()
            if (self.__propAbsPath is not None) and (destItem.__propAbsPath is not None):
                absDestPath = "/.ice/".join(destItem.__absPath.rsplit("/", 1))
                self.__svnRep.copy(self.__propAbsPath, absDestPath)
        else:
            return
        destItem.__setup()
        for listItems in destItem.walk():
            for item in listItems:
                if item.hasProperties:
                    #print "relPath='%s' has prop" % item.relPath
                    oldGuid = item.guid
                    item.__createNewGuid()
                    # remove item some item properites:
                    #   ATOMPub, tags, annotations
                    item.removeMeta("_atomUrl")
                    item.removeMeta("_atomEntry")
                    item.removeMeta("_taggedBy")
                    item.__tagsChanged = True
                    item.__tagList = []
                    inlineAnnotations = item.inlineAnnotations
                    if not annotation:
                        inlineAnnotations.removeAllAnnotations()
                    item.flush(True)
        self.iceContext.rep.indexer.reIndex(destItem)
        
        
    
    
    #==========  RENDER ===============
    def render(self, force=False, skipBooks=True, callback=None, **kwargs):
        # first get a list of files to be rendered
        if not callable(callback):
            callback = self.__dummyCallback
        if self.isDirectory:
            callback(self, displayMessage="Getting list of files to render",
                    step="renderGetList")
        toBeRenderedItemList = self.__getToBeRenderedList(force=force, skipBooks=skipBooks)
        count = 0
        total = len(toBeRenderedItemList)
        for item in toBeRenderedItemList:
            count += 1
            if total==1:
                msg = "Rendering '%s'" % (item.relPath)
            else:
                msg = "Rendering '%s' %s of %s" % (item.relPath, count, total)
            if callback(item, displayMessage=msg, step="rendering")==False:
                continue        # skip this item
            try:
                item.__render(force=force, **kwargs)
            except Exception, e:
                callback(item, step="rendering", exception=e, method=self.render)
            item.flush()
            callback(item, step="done rendering")
        #callback(self, step="done all rendering")
        return count
    
    
    def __render(self, **kwargs):
        render = self.iceContext.rep.render
        try:
            convertedData = render.render(self, **kwargs)
            if convertedData is None:
                #print "  *** failed to render this item"
                raise Exception("Render failed!")
            
            # glossary processing
            extractTerms = self.getMeta("_glossary")
            addTooltips = self.getMeta("_glossary_terms")
            if extractTerms or addTooltips:
                GlossaryPlugin = self.iceContext.getPluginClass("ice.extra.glossary")
                if GlossaryPlugin is not None:
                    glossary = GlossaryPlugin(self.iceContext, self)
                    # check if we need to extract glossary terms and/or create
                    # tooltips for this item
                    convertedData = glossary.addScript(convertedData)
                    if extractTerms:
                        glossary.extractTerms(self, convertedData)
                    if addTooltips:
                        glossary.addTooltips(convertedData)
                else:
                    print " @ glossary plugin not found!"
            
            ## Check convertedData for errors
            
            self.setConvertedData(convertedData)
            convertedData.close()
            #self.flush()
            
            if convertedData.error:
                msg = convertedData.errorMessage
                if msg.startswith("Failed to connect to OpenOffice") or \
                        msg.startswith("Word document is Invalid"):
                    if self.iceContext.isServer:
                        msg = "Contact Ron and tell him to turn soffice back on..."
                    else:
                        msg = "Please restart OpenOffice and try again"
                raise Exception(msg)
            
            # ReIndex
            try:
                self.iceContext.rep.indexer.reIndex(self)
            except Exception, e:
                msg = "Warning: failed to Index content. error='%s'" % str(e)
                self.iceContext.writeln(msg)
                return msg
        except Exception, e:
            raise e
        return None
    
    
    def __getToBeRenderedList(self, itemList=None, force=False, skipBooks=True):
        if itemList is None:
            itemList = [self]
        toBeRenderedList = []
        renderExts = self.iceContext.rep.render.getRenderableExtensions()
        def filter(item):
            if item.isDirectory:
                return True
            ext = item.ext
            if item.relDirectoryPath.find("/src/")!=-1:
                return False
            if ext in renderExts:
                if skipBooks and ext in self.iceContext.bookExts:
                    return False
                if item.vcStatusStr in ["missing", "deleted"]:
                    return False
                if force or item.needsUpdating:
                    return True
            return False
        for item in itemList:
            for items in item.walk(filter, filesOnly=True):
                for i in items:
                    toBeRenderedList.append(i)
        if skipBooks==False:
            def extCmp(a, b):
                return cmp(b.ext, a.ext)
            toBeRenderedList.sort(extCmp)
        return toBeRenderedList
    
    
    def asyncRender(self, itemList=None, force=False, skipBooks=False, callback=None):
        id = self.iceContext.guid()
        
        def worker():
            try:
                job2 = self.iceContext.getAsyncJob(id)
                self.__asyncRenderWorker(job2, itemList, callback=callback,
                                    force=force, skipBooks=skipBooks)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
        
        job = self.iceContext.addAsyncJob(worker, id, message="Render")
        return job
    
    
    def __asyncRenderWorker(self, job, itemList, callback, force=False, skipBooks=False):
        status = job.status
        def renderCallback(item=None, displayMessage=None, step=None,
                            exception=None, method=None, **extras):
            #print " @@ updateCallback(step='%s')" % step
            if displayMessage is not None:
                status.message = displayMessage
            if step=="renderGettingList":
                pass
            elif step=="rendering":
                pass
            elif step=="rendered":
                pass
            if exception is not None:
                formattedTraceback = extras.get("traceback")
                if formattedTraceback is not None:
                    print formattedTraceback
        if callback is None:
            callback = renderCallback
        
        toBeRenderedCount = 0
        renderingCount = 0
        renderedCount = 0 
        errors = []
        resultDict = {}
        
        try:
            print " @ asyncRenderWorker() getting render list"
            # get list of items that need to be rendered
            msg = "Getting render list..."
            status.message = msg
            callback(self, displayMessage=msg, step="renderGettingList", job=job)
            toBeRenderedItemList = self.__getToBeRenderedList(itemList, force=force, skipBooks=skipBooks)
            toBeRenderedCount = len(toBeRenderedItemList)
            print " @ toBeRenderedItemList='%s'" % [i.relPath for i in toBeRenderedItemList]
            # OK now render each item
            for item in toBeRenderedItemList:
                try:
                    renderingCount += 1
                    msg = "Rendering %s of %s - '%s'" % \
                                (renderingCount, toBeRenderedCount, item.relPath)
                    print " @ asyncRenderWorker() %s" % msg
                    callback(self, displayMessage=msg, step="rendering", job=job)
                    item.__render()
                    item.flush()
                    renderedCount += 1
                    callback(self, step="rendered", job=job)
                except self.iceContext.IceCancelException, e:
                    raise e
                except Exception, e:
                    msg = str(e).strip("\n")
                    error = "Failed to render '%s' - '%s'" % (item.relPath, msg)
                    print " @ asyncRenderWorker() %s" % error
                    errors.append(error)
                    if len(errors)>10:
                        raise self.iceContext.IceCancelException("Too many errors")
            if renderedCount==toBeRenderedCount and errors==[]:
                # completed all ok
                status.message = ""
                status.resultSummary = "Completed rendering."
                status.resultDetails = "Rendered %s document ok" % renderedCount
                print " @ asyncRenderWorker() completed."
            else:
                status.message = ""
                status.resultSummary = "Completed rendering (%s of %s) with errors" % (renderedCount, toBeRenderedCount)
                status.resultError = "Rendered with %s errors (see details below)" % len(errors)
                status.resultDetails = "\n".join(errors)
                if status.resultDetails=="":
                    status.resultDetails = "No errors reported but rendering not completed?"
                print " @ asyncRenderWorker() %s" % status.resultSummary
                print " @ " + status.resultDetails.replace("\n", "\n @ ")
                print " @"
        except self.iceContext.IceCancelException, e:
            print " @ asyncRenderWorker() cancelled"
            status.resultSummary = "Rendered %s of %s (operation cancelled)" % (renderedCount, toBeRenderedCount)
            status.resultError = "Render cancelled"
            if errors!=[]:
                status.resultError += " with %s errors (see details below)" % len(errors)
                status.resultDetails = "\n".join(errors)
            resultDict["exception"] = e
            resultDict["cancelled"] = True
        except Exception, e:
            print " @ asyncRenderWorker unexpected exception - '%s'" % str(e)
            status.resultSummary = "Unexpected exception in __asyncRenderWorker()"
            status.resultError = str(e)
            formattedTraceback = self.iceContext.formattedTraceback()
            print formattedTraceback
            resultDict["formattedTraceback"] = formattedTraceback
            resultDict["exception"] = e
        resultDict["toBeRenderedCount"] = toBeRenderedCount
        resultDict["renderedCount"] = renderedCount
        resultDict["errors"] = errors
        return resultDict
    
    
    #==========  UPDATE ===============
    def _update(self, recurse=False, callback=None):
        self.__update(recurse, callback)
        self.__setup()
    
    def __update(self, recurse=False, callback=None):
        # Handle conflicts
        if callable(callback):
            r = callback(item=self, step="updating")
            if r==False:
                raise self.iceContext.IceCancelException()
        
        resolverDict = {"count":0, "info":None}
        def updateResolver(eMessage, path, e=None):
            #print "-- updateResolver(path='%s', eMessage='%s')" % (path, eMessage)
            # called on an svn update exception
            resolverDict["count"] += 1
            if resolverDict["count"] > 5:
                raise Exception(eMessage)
            if path.endswith("/.ice") or path.find("/.ice/")!=-1:
                if eMessage.startswith("Failed to add ") or \
                   eMessage=="Unrecognized line ending style":
                    self.__fs.delete(path)
                    print "**** updateResolver has removed conflicting .ice item '%s'" % path
                    return      # return and try again
                else:
                    print "**** updateResolver called for a .ice item"
                    print "  path='%s'" % path
                    print "  eMsg='%s'" % eMessage
            print "*** updateResolver called path='%s'" % (path)
        
        try:
            svn = self.iceContext.rep._svnRep
            #svn.updateFiles(self.__absPath, updateResolver=updateResolver)
            packagePath = self.iceContext.getPackagePathFor(self.relPath)
            
            if packagePath is not None and packagePath.strip("/") == self.relPath.strip("/"):
                svn.update2(self.__absPath, recurse=True, revision=None)
            else:
                svn.update2(self.__absPath, recurse=False, revision=None)
            if self.isMissing:  # if was missing update self and continue (else will not have propAbsPath etc)
                self.__setup()
                if self.isDirectory:
                    packagePath = self.iceContext.getPackagePathFor(self.relPath)
                    if packagePath is not None:
                        # first remove and recheck out with depth=infinity
                        self.__fs.delete(self.__absPath)
                        svn.updateAll(self.__absPath, updateResolver=updateResolver)
                        self.__setup()
            #if self.isDirectory and self.inPackage:
            #    print "inPackage"
            #    print "Updating all of '%s'" % self.relPath
            #    svn.updateAll(self.__absPath, updateResolver=updateResolver)
            if self.__propAbsPath is not None:
                svn.updateAll(self.__fs.split(self.__propAbsPath)[0], updateResolver=updateResolver)
            if callable(callback):
                r = callback(item=self, step="updated")
                if r==False: 
                    raise self.iceContext.IceCancelException()
        except self.iceContext.IceCancelException, e:
            raise e
        except Exception, e:
            if callable(callback):
                traceback = self.iceContext.formattedTraceback()
                r = callback(item=self, step="update", exception=e, traceback=traceback)
                if r==False: 
                    raise self.iceContext.IceCancelException()
            else:
                raise e
        if recurse and self.isDirectory:
            # get list of child directories and call this on them
            listItems = self.listItems()
            dirItems = [item for item in listItems if item.isDirectory]
            for dirItem in dirItems:
                dirItem.__update(recurse, callback)
    
    
    def _getToBeUpdatedList(self, callback=None, includeMissing=False):
        return self.__getToBeUpdatedList(callback=callback, includeMissing=includeMissing)
    
    def __getToBeUpdatedList(self, updateItemList=None, recurse=True, 
                            callback=None, includeMissing=False,  # includeMissing=not recurse
                            includeMissingTopLevel=True):         # for recursive calling
        # depth first
        if updateItemList is None:
            updateItemList = [self]
        if includeMissing is None:
            includeMissing = not recurse    # if recurse do not includeMissing, else includeMissing
        toBeUpdatedList = []
        toBeUpdatedListRelPaths = []
        for item in updateItemList:
            addingToUpdateList = True
            #if added, try to check if it's exist in server
            if item.vcStatusStr=="added":
            #if not exist in server, then no need to put in list
                svn = self.iceContext.rep._svnRep
                packagePath = self.iceContext.getPackagePathFor(self.relPath)
                if packagePath is None:
                    packagePath = ""
                itemUrl = self.iceContext.urlJoin(svn.svnUrl,
                        packagePath.lstrip("/"))
                fileListInServer = svn.list(itemUrl)
                if fileListInServer==[]:
                    addingToUpdateList = False             
            if item.isDirectory and addingToUpdateList:
                #print " isOutOfDate='%s'" % item.getStatus(True).isOutOfDate
                if recurse:
                    l = item.listItems(update=True)
                    #print "done listItems(update=True)"
                    l = [i for i in l if i.getStatus(True).isOutOfDate and \
                            (not i.isIgnored or i.isSkinDir)]
                    #print len(l)
                    if includeMissing==False:
                        for i in list(l):
                            if i.isMissing and not i.isSkinDir:
                                l.remove(i)
                    #print len(l)
                    for i in list(l):
                        if i.isDirectory:
                            l2 = i.__getToBeUpdatedList(recurse=recurse, 
                                        callback=callback, includeMissing=includeMissing,
                                        includeMissingTopLevel=False)
                            l2.extend(l)
                            l = l2
                    for i in l:
                        if i.relPath not in toBeUpdatedListRelPaths:
                            toBeUpdatedList.append(i)   
                            toBeUpdatedListRelPaths.append(i.relPath)
                if item.getStatus(True).isOutOfDate and not item.isIgnored:
                    if item.relPath not in toBeUpdatedListRelPaths:
                        toBeUpdatedList.append(item)   
                        toBeUpdatedListRelPaths.append(item.relPath)
            elif item.isFile:
                if item.getStatus(True).isOutOfDate:
                    if item.relPath not in toBeUpdatedListRelPaths:
                        toBeUpdatedList.append(item)   
                        toBeUpdatedListRelPaths.append(item.relPath)
            elif (includeMissing or includeMissingTopLevel) and item.isMissing:
                if item.relPath not in toBeUpdatedListRelPaths:
                    toBeUpdatedList.append(item)      
                    toBeUpdatedListRelPaths.append(item.relPath)
            if item not in toBeUpdatedList:
                toBeUpdatedList.append(item)
        return toBeUpdatedList
    
    
    def asyncUpdate(self, updateItemList, callback=None):
        id = self.iceContext.guid()
        
        def worker():
            try:
                job2 = self.iceContext.getAsyncJob(id)
                self.__asyncUpdateWorker(job2, updateItemList, callback)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
        
        job = self.iceContext.addAsyncJob(worker, 
                                        id, message="Update")
        return job
        
    
    def __asyncUpdateWorker(self, job, updateItemList, callback):
        status = job.status
        status.message = "Updating..."
        print " @ asyncUpdateWorker()"
        
        toBeUpdatedItemList = []
        toBeUpdatedCount = 0
        # Note: python closures can not write to closed variables (so access via a dict)
        access = {"updateCount":0, "updated":0, "errors":[]}
        
        def updateCallback(item=None, displayMessage=None, step=None,
                            exception=None, method=None, **extras):
            #print " @@ updateCallback(step='%s')" % step
            errors = []
            job = extras.get("job")
            if displayMessage is not None:
                job.status.message = displayMessage
            if step=="updating":
                access["updateCount"] += 1
                msg = "Updating %s of %s - '%s'" % \
                        (access["updateCount"], toBeUpdatedCount, item.relPath)
                errors = access["errors"]
                if errors!=[]:
                    msg += " (%s error(s) received)" % len(errors)
                job.status.message = msg
            elif step=="updated":
                access["updated"] += 1
            if exception is not None:
                errorMsg = str(exception)
                print "   @@ updateCallback exception='%s'" % errorMsg
                formattedTraceback = extras.get("traceback")
                if formattedTraceback is not None:
                    print formattedTraceback
                if step=="update":
                    error = "Error updating '%s', error '%s'" % (item.relPath, errorMsg)
                    errors = access["errors"]
                    errors.append(error)
                    if len(errors)>10:
                        raise self.iceContext.IceCancelException("Too many errors")
                else:
                    raise exception
        
        if callback is None:
            callback = updateCallback
        
        def jobCallback(*args, **kwargs):
            # add job object to the arguments (for job.status.message="")
            kwargs["job"] = job
            callback(*args, **kwargs)
        
        try:
            # get list of items to be updated
            updated = False
            errors = []
            status.message = "Getting update list."
            try:
                toBeUpdatedItemList = self.__getToBeUpdatedList(updateItemList, callback=jobCallback)
                toBeUpdatedCount = len(toBeUpdatedItemList)
                access["toBeUpdatedCount"] = toBeUpdatedCount
            except Exception, e:
                #print self.iceContext.formattedTraceback()
                errors = [str(e)]
                raise e
            print " @* asyncUpdateWorker() toBeUpdatedItemList='%s'" % str([i.relPath for i in toBeUpdatedItemList])
            # update all items in the list
            try:
                for item in toBeUpdatedItemList:
                    item.__update(callback=jobCallback)
            except Exception, e:
                #formattedTraceback = self.iceContext.formattedTraceback()
                errors = [str(e)]
                raise e
            
            updated = access["updated"]
            errors = access["errors"]
            
            if updated==toBeUpdatedCount and errors==[]:
                # completed all ok
                status.message = ""
                status.resultSummary = "Completed updating"
                if status.resultDetails.find("Rendered") <> -1:
                    status.resultDetails = ""
                if updated==0 or updated == "":
                    status.resultDetails += "\nUpdated ok"
                elif updated==1:
                    status.resultDetails += "\nUpdated 1 item ok"
                else:
                    status.resultDetails += "\nUpdated %s items ok" % updated
                print " @ asyncUpdateWorker() completed"
            else:                
                status.resultSummary = "Completed updating (%s of %s) with errors" % (updated, toBeUpdatedCount)
                status.resultError = "Updated with %s errors (see details below)" % len(errors)
                status.resultDetails = "\n".join(errors)
                if status.resultDetails=="":
                    status.resultDetails = "No errors reported but update not completed?"
                print " @ asyncUpdateWorker() %s" % status.resultSummary
                print " @ " + status.resultDetails.replace("\n", "\n @ ")
                print " @"
        except self.iceContext.IceCancelException, e:
            # "Too many errors"
            #if str(e)=="Too many errors":
            #    status.resultSummary = "Updated (%s of %s) with errors" % (updated, len(toBeUpdatedItemList))
            #    status.resultError = "Updated with %s errors (see details below)" % len(errors)
            #    status.resultDetails = "\n".join(errors)
            #else:
            if True:
                status.resultSummary = "Updated %s of %s (operation cancelled)" % (updated, toBeUpdatedCount)
                status.resultError = "Update cancelled"
                if errors!=[]:
                    status.resultError += " with %s errors (see details below)" % len(errors)
                    status.resultDetails = "\n".join(errors)
            access["exception"] = e
            access["cancelled"] = True
        except Exception, e:
            status.resultSummary = "Unexpected exception in asyncUpdate()"
            status.resultError = str(e)
            formattedTraceback = self.iceContext.formattedTraceback()
            print " @ asyncUpdateWorker unexpected exception - '%s'" % str(e)
            print formattedTraceback
            access["exception"] = e
            access["formattedTraceback"] = formattedTraceback
        return access
    
    
    #==========  COMMIT ===============
    def __getCommitItemList(self, listItem=None, searchDepth=False):
        """
          returns a tuple (listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths, updateParentAbsPaths)
        """
        if listItem is None:
            listItem = [self]
        listOfParentAddOnlyAbsPaths = []
        listOfSelfAbsPaths = []
        updateParentAbsPaths = []
        for item in listItem:
            if item.isMissing:
                continue
            parentItem = item.parentItem
            if item.isDeleted:
                if parentItem._absPath not in updateParentAbsPaths:
                    updateParentAbsPaths.append(parentItem._absPath)
            if parentItem is not None and parentItem.vcStatusStr=="added":
                listOfParentAddOnlyAbsPaths = [parentItem._absPath, 
                    parentItem.__propAbsPath, self.__fs.split(parentItem.__propAbsPath)[0]]
                listOfParentAddOnlyAbsPaths.extend(parentItem.__getCommitItemList()[0])
            if item.vcStatusStr!="normal":
                if item.isDirectory:
                    #print "*@*isDir '%s' status='%s'" % (item.relPath, item.vcStatusStr)
                    listOfSelfAbsPaths.append(item.__absPath)
                    if item.__propAbsPath is not None:
                        listOfSelfAbsPaths.append(self.__fs.split(item.__propAbsPath)[0])
                elif item.isFile:
                    #print "*@*isFile '%s' status='%s'" % (item.relPath, item.vcStatusStr)
                    listOfSelfAbsPaths.append(item.__absPath)
                    if item.__propAbsPath is not None:
                        listOfSelfAbsPaths.append(item.__propAbsPath)
                else:
                    # ???
                    pass
            elif item.isDirectory:
                if searchDepth:
                    lItems = item.listItems()
                    lItems = [i for i in lItems if not i.isIgnored]
                    p, l, u = self.__getCommitItemList(lItems, searchDepth=searchDepth)
                    listOfSelfAbsPaths.extend(l)
                    updateParentAbsPaths.extend(u)
                else:
                    listOfSelfAbsPaths.append(item.__absPath)
        return (listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths, updateParentAbsPaths)
    
    
    def __asyncCommitWorker(self, job, listItems, callback):
        errors = []
        status = job.status
        def commitCallback(item=None, displayMessage=None, step=None,
                            exception=None, method=None, **extras):
            if displayMessage is not None:
                status.message = displayMessage
            if step=="commitGettingList":
                pass
            elif step=="updating":
                pass
            elif step=="rending":
                pass
            elif step=="committing":
                pass
            if exception is not None:
                formattedTraceback = extras.get("traceback")
                if formattedTraceback is not None:
                    print formattedTraceback
        if callback is None:
            callback = commitCallback
        
        resultDict = {"errors":[], "warnings":[], "infos":[]}
        try:
            print " @ asyncCommitWorker() getting list of items to commit"
            msg = "Getting list of items to commit"
            callback(self, displayMessage=msg, step="commitGettingList")
            parentsToCommit, itemsToCommit, updateParentAbsPaths = self.__getCommitItemList(listItems)
            callback(self, step="commitGotList")
            svn = self.iceContext.rep._svnRep
            if parentsToCommit!=[]:
                print " @ asyncCommitWorker() committing parent items"
                msg = "Committing parent only items first"
                callback(self, displayMessage=msg, step="committingParents")
                iceParentPropertyDirs = [i for i in parentsToCommit if i.find("/.ice/")!=-1]
                svn.commitEmpty(parentsToCommit)
                svn.commitAll(iceParentPropertyDirs)
            print " @ asyncCommitWorker() committing..."
            msg = "Committing... (%s)" % len([i for i in itemsToCommit if not i.endswith("/.ice")])
            callback(self, displayMessage=msg, step="committingList")
            ####
            ##print "calling svn.commitAll()"
            ####
            svn.commitAll(itemsToCommit)
            for absPath in updateParentAbsPaths:
                self.__svnRep.updateEmpty(absPath)
            ####
            ##print " done svn.commitAll()"
            ####
            print " @ asyncCommitWorker() commit completed"
            msg = "Committed ok"
            callback(self, displayMessage=msg, step="committed")
        except self.iceContext.IceCancelException, e:
            print " @ asyncCommitWorker() cancelled"
            status.resultSummary = "Commit (operation cancelled)"
            status.resultError = "Commit cancelled"
            errors = resultDict.get("errors")
            if errors!=[]:
                status.resultError += " with %s errors (see details below)" % len(errors)
                status.resultDetails = "\n".join(errors)
            resultDict["cancelled"] = True
            resultDict["exception"] = e
        except Exception, e:
            print " @ asyncCommitWorker unexpected exception - '%s'" % str(e)
            status.resultSummary = "Unexpected exception in __asyncCommitWorker()"
            status.resultError = str(e)
            resultDict["exception"] = e
        return resultDict
    
    
    def _commit(self, items=None, commitMessage="commit", callback=None):
        # get commit (relPaths) list
        # get revision number for update afterwards
        # NOTE: commit recursive !!!!!!!!!!!!!   so just commit this path and properties path!!!
        # Handle conflicts e.g. added item already exists etc
        svn = self.iceContext.rep._svnRep
        if items is None:
            items = [self]
        listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths, updateParentAbsPaths = self.__getCommitItemList(items)
        if listOfParentAddOnlyAbsPaths!=[]:
            svn.commitEmpty(listOfParentAddOnlyAbsPaths, commitMessage)
        revNum = svn.commitAll(listOfSelfAbsPaths, commitMessage)
        return revNum
    
    
#    # low level (just commits the data, no pre-rendering etc)
#    def commit(self, items=None, commitMessage="commit", callback=None):
#        # get commit (relPaths) list
#        # get revision number for update afterwards
#        # NOTE: commit recursive !!!!!!!!!!!!!   so just commit this path and properties path!!!
#        # Handle conflicts e.g. added item already exists etc
#        svn = self.iceContext.rep._svnRep
#        if items is None:
#            items = [self]
#        pAddList = []
#        absPaths = []
#        for item in items:
#            listOfParentAddOnlyAbsPaths, listOfSelfAbsPaths = item.__getCommitList()
#            for p in listOfParentAddOnlyAbsPaths:
#                if p not in pAddList:
#                    pAddList.append(p)
#            absPaths.extend(listOfSelfAbsPaths)
#        if pAddList!=[]:
#            svn.commitEmpty(pAddList, commitMessage)
#        revNum = svn.commitAll(absPaths, commitMessage)
#        return revNum
    
    
    def asyncTest(self, listItems=None):
        parentsToCommit, filesToCommit, updateParentAbsPaths = self.__getCommitItemList(listItems)
        print
        print "parentsToCommit='%s'" % parentsToCommit
        print "filesToCommit="
        for file in filesToCommit:
            print "  '%s'" % file
        print
        updateList = self.__getToBeUpdatedList(listItems)
        print "toBeUpdatedList="
        for item in updateList:
            print "  '%s'" % item.relPath
        print
    
    
    #==========  SYNC ===============
    # High level commit
#    def sync(self, items=None, commitMessage="commit", reRender=True, callback=None):
#        # First do an update
#        # Then reRender
#        # Then commit
#        # Then update ??? again
#        if items is None:
#            items = [self]
#        self.updateList(items, callback=callback)
#        if reRender:
#            for item in items:
#                item.render(callback=callback)
#        revNum = self.commit(items, commitMessage, callback=callback)
#        self.updateList(items, callback=callback)
    def _sync(self, items=None, commitMessage="commit", render=True, callback=None):
        if items is None:
            items = [self]
        updateList = self.__getToBeUpdatedList(items, callback=callback)
        if render:
            for item in items:
                item.render(callback=callback)
        revNum = self._commit(items, commitMessage=commitMessage, callback=callback)
        updateList = self.__getToBeUpdatedList(items, callback=callback)
        for item in updateList:
            item.__update(callback=callback)
    
    
    def asyncSync(self, itemList=None, force=False, skipBooks=True, callback=None):
        # if force==True then try and do a force sync
        id = self.iceContext.guid()
        if itemList is None:
            itemList = [self]
        
        def worker():
            try:
                job2 = self.iceContext.getAsyncJob(id)
                self.__asyncSyncWorker(job2, itemList, force, skipBooks, callback)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
        
        job = self.iceContext.addAsyncJob(worker, 
                                        id, message="Sync")
        return job
    
    
    def __asyncSyncWorker(self, job, itemList, force, skipBooks, callback):
        # if force==True then try and do a force sync
        errors = []
        status = job.status
        def syncCallback(item=None, displayMessage=None, step=None,
                            exception=None, method=None, **extras):
            pass
        #if callback is None:
        #    callback = updateCallback
        
        # First do an update
        # Second do a render
        # Then third to the commit
        #  and last to another update
        
        try:
            print " @ asyncSyncWorker() step 1 (update)"
            # First do an update
            resultDict = self.__asyncUpdateWorker(job, itemList, callback=callback)
            if resultDict.get("cancelled"):
                raise resultDict.get("exception")
            if force==False:
                errors = resultDict.get("errors", [])
                if len(errors)>0:
                    raise self.iceContext.IceCancelException()
                if resultDict.get("exception") is not None:
                    raise self.iceContext.IceCancelException()
            # Second do a render
            if force==False:
                print " @ asyncSyncWorker() step 2 (render)"
                resultDict = self.__asyncRenderWorker(job, itemList, callback=callback,
                                                 force=False, skipBooks=False)      # defaults
                if resultDict.get("cancelled"):
                    raise resultDict.get("exception")
            # Then third to the commit
            print " @ asyncSyncWorker() step 3 (commit)"
            resultDict = self.__asyncCommitWorker(job, itemList, callback=callback)
            resultException = resultDict.get("exception")
            if resultException is not None:
                raise resultException
            # And last to another update
            print " @ asyncSyncWorker() step 4 (update)"
            #print "itemList='%s'" % [str(i) for i in itemList]
            resultDict = self.__asyncUpdateWorker(job, itemList, callback=callback)
            if resultDict.get("cancelled"):
                raise resultDict.get("exception")
            if False:
                print " @ asyncSyncWorker() step 5 (update parent(s))"
                parentItemList = self.__getParentItemList(itemList)
                print "parentItemList"
                for i in parentItemList:
                    print i
                resultDict = self.__asyncUpdateWorker(job, parentItemList, callback=callback)
                if resultDict.get("cancelled"):
                    raise resultDict.get("exception")
            print " @ asyncSyncWorker() completed ok"
            status.message = "Synchronization completed."
        except self.iceContext.IceCancelException, e:
            print " @ asyncSyncWorker() cancelled"
            status.resultSummary = "Sync (operation cancelled)"
            status.resultError = "Sync cancelled"
            if errors!=[]:
                status.resultError += " with %s errors (see details below)" % len(errors)
                status.resultDetails = "\n".join(errors)
        except Exception, e:
            print " @ asyncSyncWorker unexpected exception - '%s'" % str(e)
            status.resultSummary = "Unexpected exception in __asyncSyncWorker()"
            status.resultError = str(e)
            if str(e).find("403 Forbidden") != -1:
                status.message = "Sync failed because you don't have write access!"
            else:
                status.message = "Sync failed: %s" % str(e)
    
    def __getParentItemList(self, itemList):
        parentItemList = {}
        for item in itemList:
            pItem = item.parentItem
            if pItem is not None:
                parentItemList[pItem.relPath] = pItem
        return parentItemList.values()
    #================================
    
    
    def export(self, destAbsPath, callback=None, includeProperties=True):
        if self.__fs.exists(destAbsPath):
            raise Exception("destination already exists")
        basePath = self._absPath
        if not basePath.endswith("/"):
            basePath += "/"
        if self.__fs.isFile(basePath):
            self.__fs.copy(basePath, destAbsPath)
        else:
            for path, dirs, files in self.__fs.walk(basePath):
                if ".svn" in dirs:
                    dirs.remove(".svn")
                if includeProperties==False:
                    if ".ice" in dirs:
                        dirs.remove(".ice")
                dPath = self.__fs.join(destAbsPath, path[len(basePath):])
                self.__fs.makeDirectory(dPath)
                for file in files:
                    src = self.__fs.join(path, file)
                    dest = self.__fs.join(dPath, file)
                    self.__fs.copy(src, dest)
    
    def svnCleanup(self):
        svn = self.iceContext.rep._svnRep
        parentItem = self.parentItem
        if parentItem is not None:
            path = parentItem._absPath
        else:
            path = self._absPath
        svn.cleanup(path)
    
    
    def getStatus(self, update=False):
        #print "---\ngetStatus(update=%s) relPath='%s'" % (update, self.relPath)
        r = self.__getStatus(update)
        #print "  result='%s'\n---" % (r)
        return r
    
    def __getStatus(self, update=False):
        svnRep = self.iceContext.rep._svnRep
        itemStatus = svnRep.getStatus(self.__absPath, update=update)
        if itemStatus is None:
            itemStatus = svnRep.ItemStatus2(name=self.name, statusStr="unversioned", 
                        isDir=self.isDirectory, isFile=self.isFile,
                        isOutOfDate=False, #isVersioned=False,
                        lastChangedRevisionNumber=-1, update=False)
        if self.hasProperties and self.__propAbsPath is not None:
            propStatus = svnRep.getStatus(self.__propAbsPath, update=update, single=False)
            # If propLastChangedRevisionNumber > lastChangedRevisionNumber
            # Does this matter?
            if propStatus is not None:
                if propStatus.lastChangedRevisionNumber > itemStatus.lastChangedRevisionNumber:
                    itemStatus.lastChangedRevisionNumber = propStatus.lastChangedRevisionNumber
                if propStatus.isOutOfDate:
                    itemStatus.isOutOfDate = True
                if itemStatus.statusStr=="normal":
                    if propStatus.statusStr=="modified" or propStatus.statusStr=="added":
                        itemStatus.statusStr = "modified"
        self.__vcStatus = itemStatus
        if update==True:
            self.__setup(vcStatus=itemStatus)
        return itemStatus
    
    
    def cleanup(self):
        self.__svnRep.cleanup(self._absPath)
    
    ####################
    ####################
    
    
    def zipList(self):
        return self.__fs.zipList(self.__absPath)
    
    def extractFromZip(self, filename):
        item = None
        try:
            item = self.__fs.readFromZipFile(self.__absPath, filename)
        except: pass
        return item
    
    
    def replaceInZip(self, itemName, data):
        return self.__fs.addToZipFile(self.__absPath, itemName, data)
    
    
    def zipFromTempDir(self, absTempDir):
        absTempDir.zip(self.__absPath)
    
    
    def unzipToTempDir(self):
        absTempDir = self.__fs.unzipToTempDirectory(self.__absPath)
        return absTempDir
    
    
    
    def walk(self, filter=None, filesOnly=False):
        """ yields a 'list of items' """
        # Note: filter will need to include - 'if item.isDirectory and not item.isMissing: return True'
        #       to walk directories
        return self.__walk(self, filter, filesOnly)
    
    def __walk(self, item, filter, filesOnly):
        listItems = item.listItems()
        if callable(filter):
            listItems = [item for item in listItems if filter(item)]
        if filesOnly:
            yield [item for item in listItems if item.isFile]
        else:
            yield listItems
        dirItems = [i for i in listItems if i.isDirectory and not i.isMissing]
        for dirItem in dirItems:
            for x in self.__walk(dirItem, filter, filesOnly):
                yield x
    
    
    @property
    def isBinaryContent(self):
        r = False
        if self.isFile:
            if self.uri==self.relPath:
                r = True
            else:
                uriDiff = self.uriDiff
                # Also binary content if _files/*.jpg[/etc/]
                if uriDiff.startswith("_files/"):
                    r = True
                if uriDiff=="":
                    ext = self.__fs.splitExt(self.uri)[1]
                    if ext!=".htm":
                        r = self.hasXRendition(ext)
        else:
            uri = self.__uri
            if uri.startswith("skin/") or uri.find("/skin/")!=-1:
                r = True
        return r
    
    
    def getBinaryContent(self):
        mimeType = None
        data = None
        if not self.isFile:
            #raise Exception("Is not a binary content item!")
            return (data, "")
        if self.relPath.startswith(self.uri):
            mimeType = self.iceContext.getMimeTypeForExt(self.ext.lower())
            if mimeType is None and self.ext.lower()==".book.odt":
                mimeType = self.iceContext.getMimeTypeForExt(".odt")
            data = self.read()
            return (data, mimeType)
        # OK check for _files/ and renditions
        pPath = self.__fs.split(self.relPath)[0]
        if not pPath.endswith("/"):
            pPath += "/"
        x = self.uri[len(pPath):] + "/"
        n1, n2 = x.split("/", 2)[0:2]
        if n1.endswith("_files"):
            ext = self.__fs.splitExt(n2)[1].lower()
            mimeType = self.iceContext.getMimeTypeForExt(ext)
            data = self.getImage(n2)
        else:
            # rendition
            ext = self.__fs.splitExt(n1)[1].lower()
            mimeType = self.iceContext.getMimeTypeForExt(ext)
            if self.hasXRendition(ext):
                data = self.getRendition(ext)
        return (data, mimeType)
    
    
    def getContent(self, embed=False):
        # embed - whether the contents should be embedded in ice html
        """
        Returns a tuple of (content, mimeType)
        """
        mimeType = None
        data = None
        if embed:
            raise Exception("embed option not supported yet!")
        if self.isBinaryContent:
            return self.getBinaryContent()
        # OK ICE html
        mimeType = self.iceContext.getMimeTypeForExt(".htm")
        data = "-- ice htm data --"
        return (data, mimeType)
    
    
    def getHtmlRendition(self, embed=False): # embed = whether the contents should be embedded in ice html
        """ Returns a tuple of (htmlBody, title, page_toc, style) """
        rep = self.iceContext.rep
        
        (data, title, page_toc, style) = (None, None, "", "")
        # Is this a .slide.htm rendition or just a .htm rendition
        data = self.__getRendition(".htm", embed)
        if data:
            try:
                title = self.getMeta("title")
                if title is None:
                    title = self.name
                page_toc = self.getMeta("toc")
                style = self.getMeta("style.css")
                if style is None:
                    style = ""
            except:
                pass
            # Slide test & hack
            isSlide = False
            if self.hasSlide or True:
                slideUri = self.relPath[:-len(self.ext)] + ".slide.htm"
                if self.uri.startswith(slideUri):
                    isSlide = True
            if isSlide:        # Slide HACK
                xml = self.iceContext.Xml(data)
                div = xml.createElement("div")
                div.addChildren(xml.getNodes("//div[@class='slide']"))
                data = str(div)
                xml.close()
        return (data, title, page_toc, style)
    
    
    # only called from above 'getHtmlRendition()'
    def __getRendition(self, renditionExt, embed=False):
        """Get a rendition for a item """
        renditions = {".htm":".xhtml.body", ".html":".xhtml.body"}
        data = None
        if self.relPath.find("/skin/")!=-1:
            return None
        
        renditionType = renditions.get(renditionExt, renditionExt);
        if embed and renditionType==".xhtml.body":
            embedType = ".xhtml.embed"
            if self.hasRendition(embedType):
                renditionType = embedType
        _, ext = self.__fs.splitExt(self.relPath)
        notFoundButRenderable = not self.hasRendition(renditionType) and \
                ext in self.iceContext.rep.render.getRenderableFrom(renditionType)
        if self.needsUpdating or embed or notFoundButRenderable:
            self.render(skipBooks=False, force=notFoundButRenderable)
        
        # HACK for serving a CMA.zip file
        if renditionExt==".zip":
            documentType = self.getMeta("documentType")
            if documentType!=None and documentType=="cma":
                cmaXml = self.getMeta("cmaXml")
                zip = self.__fs.zipString()
                zip.add("cma.xml", cmaXml)
                # Get a list of all of the images
                imagePath = self.__fs.splitExt(self.__fs.split(self.relPath)[1])[0]
                imagePath += "_files/"
                images = self.getMeta("images")
                for image in images:
                    zip.add(imagePath + image, self.getImage(image))
                data = zip.getZipData()
                zip.close()
                return data
        data = self.getRendition(renditionType)
        return data

    #######################################
    #######################################
    def getRepName(self):
        # read repository name from /.ice/rep.name.txt if possible
        name = None
        absPath = self.__fs.absPath(".ice/rep.name.txt")
        name = self.__fs.read(absPath)
        return name

    def setRepName(self, name):
        absPath = self.__fs.absPath(".ice/rep.name.txt")
        self.__fs.write(absPath, name)
    #######################################
    #######################################
    
    #==============================================================
    def toString(self, full=True):
        s = "[IceItem object] name='%s', relPath='%s'" % (self.name, self.relPath)
        if full:
            s += ",\n guid='%s', uri='%s'" % (self.guid, self.uri)
            s += ",\n name='%s', relPath='%s'" % (self.name, self.relPath)
            s += ",\n _absPath='%s',\n _propAbsPath='%s'" % (self._absPath, self._propAbsPath)
            s += ",\n exists='%s', isFile='%s', isDirectory='%s'" % (self.exists, self.isFile, self.isDirectory)
            s += ",\n hasProperties='%s', isHidden='%s', " % (self.hasProperties, self.isHidden)
            s += ",\n isVersioned='%s', lastChangedRevisionNumber='%s'" % (self.isVersioned, self.lastChangedRevisionNumber)
            s += ",\n vcStatus='%s'" % (self.vcStatus)
            s += ",\n hasPdf='%s', hasHtml='%s', hasSlide='%s'" % (self.hasPdf, self.hasHtml, self.hasSlide)
            s += ",\n needsUpdating='%s', convertFlag='%s'" % (self.needsUpdating, self.convertFlag)
        return s
    
    
    def __str__(self):
        return self.toString(False)
    
    
    #========== private methods ===============
    
    @property
    def __lastRenderedMd5(self):
        return self.getMeta("_lastMD5")
    def __setLastRenderedMd5(self, value):
        self.setMeta("_lastMD5", value)
    
    
    @property
    def __meta(self):
        if self.__metaDict is None:
            data = self.__readProperty("meta")
            if data is None:
                data = {}
            else:
                try:
                    data = self.iceContext.loads(data)
                except:
                    data = {}
            if not data.has_key("_images"):
                data["_images"] = []
            if not data.has_key("_renditions"):
                data["_renditions"] = []
            if not data.has_key("_guid"):
                if not self.isMissing:
                    data["_guid"] = self.iceContext.guid()
                    #self.iceContext.writeln("prop created '%s'" % self.name)
                    self.__metaChanged = True
                else:
                    data["_guid"] = None
            self.__metaDict = data
            if self.__metaChanged:
                self.flush()
        return self.__metaDict
    
    
    def _createNewGuid(self):
        self.__createNewGuid()
    def __createNewGuid(self):
        self.__meta["_guid"] = self.iceContext.guid()
        self.__metaChanged = True
        self.flush()
    
    
    def __saveMeta(self):
        data = self.iceContext.dumps(self.__meta)
        self.__writeProperty("meta", data)
        self.__metaChanged = False
    
    
    def __read(self):
        data = None
        if self.isFile:
            data = self.__fs.readFile(self.__absPath)
        return data
    
    
    def __getPropertyName(self, name):
        if self.__propAbsPath is None:
            pass
        pName = self.__fs.join(self.__propAbsPath, name)
        return pName
    
    
    def __readProperty(self, name):
        if self.__propAbsPath is None:
            return None
        pname = self.__getPropertyName(name)
        data = None
        if self.__fs.isFile(pname):
            data = self.__fs.readFile(pname)
        return data
    
    
    def __writeProperty(self, name, data):
        svnRep = self.iceContext.rep._svnRep
        if self.__propAbsPath is None or data is None:
            return
        pname = self.__getPropertyName(name)
        self.__fs.writeFile(pname, data)
        if not pname.endswith(".tmp"):
            report = svnRep.add(pname, recurse=True)    # Note: this could be optimized!
            if report is not None:
                #print "---"  ##
                #print "IceItem.__writeProperty svn.add report='%s'" % report
                #print " pname='%s'" % pname
                toBeAdded = [pname]
                parentPath = self.__fs.split(pname)[0]
                #while parentPath.find("/.ice")!=-1:
                while True:
                    itemStatus = svnRep.getStatus(parentPath, update=False)
                    if itemStatus is None or itemStatus.isVersioned==False:
                        toBeAdded.insert(0, parentPath)
                    else:
                        break
                    parentPath = self.__fs.split(parentPath)[0]
                
                
                #print
                #print "toBeAdded='%s'" % toBeAdded
                for add in toBeAdded:
                    report = svnRep.add(add)
                    if report is not None:
                        print "IceItem.__writeProperty svn.add('%s') report='%s'" % (add, report)
                #print "---" ##
    
    
    def __deleteProperty(self, name):
        if self.__propAbsPath is None:
            return
        pname = self.__getPropertyName(name)
        self.__svnRep.delete(pname)
    
    
    def __readTags(self):
        if self.hasProperties==False:
            return []
        data = self.__readProperty("tags")
        if data is None:
            return []
        tags = data.split()
        tags.sort()
        return tags
    
    
    def __saveTags(self):
        data = "\n".join(self.__tags)
        self.__writeProperty("tags", data)
        self.__tagsChanged = False
    
    
    def __getPropAbsPath(self):
        propAbsPath = None
        if self.hasProperties:
            if self.isFile:
                absBasePath = self.__fs.split(self.__absPath)[0]
                name = self.__name
            elif self.isDirectory:
                absBasePath = self.__absPath
                name = "__dir__"
            else:
                name = None
            if name is not None:
                propAbsPath = self.__fs.join(absBasePath, ".ice", name)
        return propAbsPath
    
    
    def __dummyCallback(self, item=None, displayMessage=None, step=None,
                        exception=None, method=None, **extras):
        if exception is not None:
            name = "?"
            if callable(method):
                name = method.__name__
            print "*** exception in '%s' - '%s'" % (name, str(exception))
            print self.iceContext.formattedTraceback()
            raise exception
    
    
    def __cmp__(self, other):
        if other is None:
            return False
        r = cmp(other.isDirectory, self.isDirectory)
        if r==0:
            r = cmp(self.name, other.name)
        return r













