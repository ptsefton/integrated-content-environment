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

import types
import re
from vc_rep import VCRep


class IceItem(object):
    # Constructor:
    #   __init__(iceContext, uriOrRelPath, other={})
    # Properties:
    #   guid                                            # ReadOnly
    #   
    #   
    #
    # Methods:
    #   read()                                          # FileOnly (else raise Exception)
    #   write(data)                                     # FileOnly (else raise Exception)
    #
    
    # callback method
    #  callback(item=None, displayMessage=None, step=None, exception=None, method=None, **extras)
    #           item = current working item
    #           displayMessage = message string to be displayed to user
    #           step = string - current processing step e.g. "rendering", or "done render"
    #           exception = exception if any - this may need be be raised if it can not be handled
    #           method = current method (optional)
    #           **extras = extra arguments
    #       Note: raise an IceCancelException() to cancel an opertion
    
    __mineCopyNamePrefix = "MyChanges_"
    
    @staticmethod
    def GetIceItem(iceContext, relPath):
        # Normalize path
        if relPath.find("/.ice/")!=-1:
            raise Exception("Can not get an item from a .ice folder!")
        if type(relPath) not in types.StringTypes:
            raise Exception("relPath argument is not a string type!")
        relPath = iceContext.normalizePath(relPath)
        if relPath is None:
            raise Exception("relPath can not be None!")
        item = IceItem(iceContext)
        item.__setup(relPath)
        return item
    
    
    @staticmethod
    def GetIceItemForUri(iceContext, uri):
        #print iceContext.printCallers(3)
        # Note: if uri does not start with '/skin/' but contains '/skin/' and
        #       that file does not exist then remap to the root /skin/
        if not uri.startswith("/"):
            uri = "/" + uri
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
        count = 0
        while (parentItem is not None) and ((not parentItem.exists) or parentItem.isMissing):
            if parentItem.isFile:
                parentItem.__uri = uri
                return parentItem
            item = parentItem
            parentItem = item.parentItem
            count += 1
            if count>2:
                raise Exception("OK")
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

    
    ###########################################################################
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.rep.fs
        self.__vcRep = iceContext.rep._vcRep
        self.__name = None
        self.__relPath = None
        self.__absPath = None
        self.__isFile = False
        self.__isDir = False
        self.__uri = None
        self.__uriNotFound = False

        self.__vcStatus = None
        self.__parentItem = None

        #self.__isVersioned = None
        #self.__isHidden = None
        #self.__isIgnored = None
        #self.__isMissing = False
        self.__ext = None
    
    
    def __setup(self, relPath=None, vcStatus=None):
        #print "__setup(relPath='%s')" % relPath
        fs = self.__fs
        if relPath is None:
            relPath = self.__relPath
        else:
            if relPath=="." or relPath.startswith("./"):
                relPath = relPath[1:]
            if not relPath.startswith("/"):
                relPath = "/" + relPath
            self.__uri = relPath
            relPath = relPath.strip("/")
            self.__absPath = fs.absPath(relPath)
            self.__relPath = "/" + relPath
        self.__vcStatus = vcStatus
        self.__isFile = fs.isFile(self.__absPath)
        self.__isDir = fs.isDirectory(self.__absPath)
        self.__name = fs.split(relPath)[1]
        if self.__isDir:
            if not self.__relPath.endswith("/"): # and self.__relPath!="":
                self.__relPath += "/"
            self.__absPath += "/"
        if self.__isFile==False and self.__isDir==False:
            # may be missing - check now
            if vcStatus is None:
                vcStatus = self.__vcRep.getStatus(self.__absPath)
            if vcStatus is not None:
                self.__isDir = vcStatus.isDir
                self.__isFile = vcStatus.isFile
                self.__vcStatus = vcStatus

    
    def reload(self):
        self.__setup()
    
    
    @property
    def isSkinDir(self):
        return self.__isSkinDir
    
    
    @property
    def guid(self):
        return self.__vcRep.getID(self.__absPath)
    
    
    @property
    def name(self):
        return self.__name
    
    
    @property
    def ext(self):
        if self.__ext is None:
            self.__ext = self.iceContext.iceSplitExt(self.name)[1]
        return self.__ext
    
    
    @property
    def uri(self):
        return self.__uri
    
    
    @property
    def uriDiff(self):
        # returns any extra content on the uri (after the '/')
        uri = self.__uri.strip("/")
        relPath = self.__relPath.strip("/")
        relPathParts = relPath.split("/")
        uriParts = uri.split("/")
        l = len(relPathParts)
        r = "/".join(uriParts[l:])
        if r!="" and uriParts[l-1].endswith("_files"):
            #r = "/".join(uriParts[l+1:])
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
        parent = self.__fs.split(self.__absPath)[0]
        dlist = self.__vcRep.list(parent)
        names = [n.lower() for n in dlist.keys()]
        return self.__name.lower() in names
    
    
    @property
    def isHidden(self):
        relPath = self.__relPath.strip("/")
        if relPath.startswith(".") or relPath.find("/.")!=-1:  # any file or dir starting with '.' is hidden
            return True
        if relPath.startswith("skin/"):
            return True
        if relPath=="favicon.ico":
            return True
        if relPath.endswith("imscp_rootv1p1.dtd"):
            return True
        return False
    
    
    @property
    def isIgnored(self):
        return self.__vcRep.isIgnored(self.__relPath)
    
    
    @property
    def isMyChanges(self):
        return self.__name.startswith(self.__mineCopyNamePrefix)
    
    
    @property
    def lastModifiedDateTime(self):
        if self.isFile:
            try:
                return self.__fs.getModifiedTime(self.__absPath)
            except:
                pass
        return 0
    
    
    @property
    def metaNames(self):
        names = self.__vcRep.propList(self.__absPath)
        return [n for n in names if not n.startswith("_")]
    
    
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
            if state and self.relPath.find("/media/")!=-1:
                state = False
            else:
                state = self.__getIsRenderable()
        return state
    def __setConvertFlag(self, value):
        self.setMeta("_iceDoc", value)
    convertFlag = property(__getConvertFlag, __setConvertFlag)
    
    
    @property
    def isRenderable(self):
        result = self.__getIsRenderable()
        if result==True and self.convertFlag==False:
            result = False
        return result

    def __getIsRenderable(self):    # ignores convertFlag
        result = False
        if self.isFile:  # is a file
            renderExts = self.iceContext.rep.render.getRenderableExtensions()
            if self.ext in renderExts:
                # is of a renderable extension
                result = True
        return result

    def isRenderableTo(self, ext):
        result = False
        if self.isRenderable:
            render = self.iceContext.rep.render
            result = ext in render.getRenderableFrom(self.ext)
        return result

    @property
    def needsUpdating(self):
        result = False
        if self.isFile and self.isRenderable and self.isVersioned:
            if self._lastSaved != self.lastModifiedDateTime:
                if self._getCurrentMd5()!=self.__getLastRenderedMd5():
                    result = True
                else:
                    pass
                    #self._lastSaved = self.lastModifiedDateTime
            #print "may need updating %s" % result
        return result
    
    
    @property
    def tags(self):
        return []
    
    
    @property
    def taggedBy(self):
        return []
    
   
    @property
    def inlineAnnotations(self):
        inlineAnnotations = None
        IceInlineAnnotations = self.iceContext.IceInlineAnnotations
        accessObj = self.__vcRep.getAnnotationDirAccess(self.__absPath)
        if IceInlineAnnotations is not None and accessObj is not None:
            inlineAnnotations = IceInlineAnnotations(accessObj)
        return inlineAnnotations
    
    
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
        return self.__vcRep.localPropGet(self.__absPath, "lastModified")
    def __setLastSaved(self, value):
        self.__vcRep.localPropSet(self.__absPath, "lastModified", value)
    _lastSaved = property(__getLastSaved, __setLastSaved)
    
    
    @property
    def bookInfo(self):
        data = self.__vcRep.propGet(self.__absPath, "_bookInfo")
        if data is not None:
            data = self.iceContext.loads(data)
        return data
    
    
    def setBookInfo(self, bookInfo):
        data = self.icecontext.dumps(data)
        self.__vcRep.propSet(self.__absPath, "_bookInfo", data)
        return self
    
    
    @property
    def parentItem(self):
        if self.__parentItem is None:
            relPath = self.__relPath.rstrip("/")
            if relPath!="":
                parentPath = self.__fs.split(relPath)[0]
                self.__parentItem = self.getIceItem(parentPath)
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
    def uriNotFound(self):
        return self.__uriNotFound
    
    
    #========== public methods ================
    
    def getIdUrl(self):
        rep = self.iceContext.rep
        serverData = rep.serverData
        name, ext = self.iceContext.iceSplitExt(self.__name)
        idRev = ""
        if serverData is not None:
            id = serverData.getIdForRelPath(self.relDirectoryPath)
            ## get this items revision number. NOTE: may be -1 if only Added
            rev = self.lastChangedRevisionNumber
            idRev = "_i%sr%s" % (hex(id)[2:], rev)
        return name + idRev + ext
    
    
    def getIceItem(self, relPath):
        item = IceItem(self.iceContext)
        item.__setup(relPath)
        return item
    
    
    def getNamedItem(self, name):
        """ returns an (file) item with a name only (not including ext) of 'name' or None if none found. """
        dlist = self.__vcRep.list(self.__absPath)
        for n in dlist.keys():
            if name==self.__fs.splitExt(n)[0]:
                return self.__getChildItem(n)
        return None
    
    
    def getChildItem(self, name):
        """ returns a file or directory child item with the given name (including ext)
            note: the item may not yet exist. """
        return self.__getChildItem(name)

    def __getChildItem(self, name, vcStatus=None):
        relPath = self.__fs.join(self.__relPath, name)
        item = IceItem(self.iceContext)
        item.__setup(relPath, vcStatus)
        return item

    
    def setTags(self, tags):
        """ tags can be a list of tagNames or a string of whitespace delimited tagNames """
        raise Exception("not implemented yet!")
    
    
    def setTaggedBy(self, taggedBy):
        raise Exception("not implemented yet!")
    
    
    def touch(self):
        self._lastSaved = ""
        self.__setLastRenderedMd5(None)
    
    
    def _getCurrentMd5(self):
        data = self.read()
        if data is None:
            return None
        else:
            return self.iceContext.md5Hex(data)
    
    
    def removeMeta(self, name):
        self.__vcRep.propDelete(self.__absPath, name)
    
    
    def setMeta(self, name, value):
        if value is None:
            self.removeMeta(name)
        else:
            self.__vcRep.propSet(self.__absPath, name, value)
    
    
    def getMeta(self, name, value=None):
        result = self.__vcRep.propGet(self.__absPath, name, value)
        if name=="toc" and value is None:
            result = ""
        return result
    
    
    def hasMeta(self, name):
        return self.__vcRep.propGet(self.__absPath, name)!=None
    
    
    def getRendition(self, extension):
        name = "rendition" + extension
        return self.getMeta(name)


    def _setRendition(self, extension, data):
        _renditions = self.getMeta("_renditions", [])
        if extension not in _renditions:
            _renditions.append(extension)
            self.setMeta("_renditions", _renditions)
        name = "rendition" + extension
        self.setMeta(name, data)


    def hasRendition(self, extension):
        return self.isRenderableTo(extension)
        #_renditions = self.getMeta("_renditions", [])
        #print _renditions, extension in _renditions
    
    
    def hasXRendition(self, ext):
        if ext==".mp3" and self.hasAudio:
            return True
        return self.hasRendition(ext)
    
    
    def _setImage(self, name, data):
        name = "image-" + name
        self.setMeta(name, data)
    
    
    def getImage(self, name):
        name = "image-" + name
        return self.getMeta(name)
    
    
    def setConvertedData(self, convertedData):
        # delete unused renditions, images, and (some) metaData
        renditionNames = self.getMeta("_renditions", [])
        imageNames = self.getMeta("_images", [])
        metaNames = self.metaNames

        # delete all image's that are not in the new results
        for name in set(imageNames).difference(convertedData.imageNames):
            print " todo removeMeta '%s'" % name
        # delete all rendition's that have not been regenerated
        for name in set(renditionNames).difference(convertedData.renditionNames):
            self.__vcRep.propDelete(self.__absPath, "rendition"+name)
        for name in metaNames:
            self.removeMeta(name)
        self.setMeta("_images", [])
        self.setMeta("_renditions", [])
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
            self._setRendition(name, data)

        # Update renderedMD5 and _lastSaved
        renderedFileTime = convertedData.renderedTime
        renderedFileMD5 = convertedData.renderedMD5
        if renderedFileTime is None:
            renderedFileTime = self.lastModifiedDateTime
        if renderedFileMD5 is None:
            renderedFileMD5 = self._getCurrentMd5()
        self._lastSaved = renderedFileTime
        self.__setLastRenderedMd5(renderedFileMD5)
        self.__vcStatus = None
        return self
    
    
    def flush(self, force=False):
        pass
    
    
    def close(self):
        self.flush()
    
    
    def listItems(self, update=False):     # For directories only
        # return a list of items (with status)
        dlist = self.__vcRep.list(self.__absPath)
        ## TODO: replace with filter method
        l = [i for i in dlist.values() if not i.name.startswith(".")]
        items = [self.__getChildItem(i.name, i) for i in l]
        items.sort()
        return items
    
    
    def write(self, data):
        if data is None:
            data = ""
        self.__fs.write(self.__absPath, data)
        self.__vcRep.add(self.__absPath)
        self.__setup()
        return self
    
    
    def read(self):
        return self.__fs.read(self.__absPath)
    
    
    def makeDirectory(self, message="mkdir", ignore=False):
        try:
            self.__fs.makeDirectory(self.__absPath)
            self.__vcRep.add(self.__absPath)
            self.__setup()
        except:
            pass
    
    
    def getLogData(self, levels=None):
        """ Returns a logData object or a list of logData objects if levels is given
            The logData object has the following properties:
                date -    (string)
                message - (string)
                author -  (string)
                revisionNumber - (integer)
        """
        if levels is None:
            logs = self.__vcRep.log(self.__absPath, 1)
        else:
            logs = self.__vcRep.log(self.__absPath, levels)
        logList = []
        for log in logs:
            obj = self.iceContext.Object()
            obj.author = log[0]
            obj.date = log[1]
            obj.message = log[2]
            obj.revisionNumber = log[3]
        if levels is None:
            if len(logs)==0:
                return None
            return logs[0]
        else:
            return logs
    
    
    ####################
    ####################
    
    def getCompleteStatus(self):
        status = self.vcStatus
        result = ""
        if status.isOutOfDate==True:
            result = "out-of-date"
        elif status.isOutOfDate==None:
            result = "(offline)"
        if status.status!="normal":
            result = "%s %s" % (status.status, result)
        elif result=="":
            result = "in sync"
        result = result.capitalize()
        return result.strip()
    
    
    @property
    def vcStatus(self):
        if self.__vcStatus is None:
            self.__vcStatus = self.__vcRep.getStatus(self.__absPath)
        return self.__vcStatus
    
    
    @property
    def vcStatusStr(self):
        return self.vcStatus.status
    
    
    @property
    def lastChangedRevisionNumber(self):
        return self.vcStatus.lastChangedRevNum
    @property
    def lastChangedRevNum(self):
        return self.vcStatus.lastChangedRevNum
    
    
    @property
    def isVersioned(self):
        return self.__vcRep.isVersioned(self.__absPath)
    
    
    @property
    def isMissing(self):
        return self.vcStatus.status=="missing"
    
    
    @property
    def isDeleted(self):
        return self.vcStatus.status=="deleted"
    
    
    @property
    def hasChanges(self):
        """ """
        # Note: this is a recursive method(/property)
        if self.isFile:
            return self.vcStatus.status=="normal"
        elif self.isDirectory:
            if self.__hasChanges()!="":
                return True
        else:
            return False

    def __hasChanges(self):
            # OK now check the status of this directory and all of it's children
            dlist = self.__vcRep.list(self.__absPath)
            ## TODO: replace with filter method
            for i in dlist.values():
                if i.status!="normal":
                    return "%s is %s" % (self.__fs.join(self.__relPath, i.name), i.status)
                if i.isDirectory and i.name!=".":
                    item = self.__getChildItem(i.name, i)
                    msg = item.__hasChanges()
                    if msg!="":
                        return msg
            return ""
    
    def shelve(self):
        # Can only shelve directories
        if not self.isDirectory or not self.isVersioned:
            return False, "can only shelve versioned directories"
        msg = self.__hasChanges()
        if msg!="":
            return False, msg
        self.__vcRep.shelve(self.__absPath)
    

    def add(self):
        # first make sure that my parent is added
        r = self.__vcRep.add(self.__absPath)
        self.__setup()
        return r
    
    
    def delete(self):
        r = self.__vcRep.delete(self.__absPath)
        self.__setup()
        return r
    
    
    def _remove(self):      # see/use shelve()
        # FileSystem delete NOTE: still kept under version control
        # First check that there are no changes that might be lost
        # Look for any added, modified, (deleted) etc
        raise Exception("not implemented yet!")
    
    
    def revert(self):
        r = self.__vcRep.revert(self.__absPath)
        self.__setup()
        return r
    
    
    def move(self, destItem):
        self.__vcRep.copy(self.__absPath, destItem.__absPath)
        return self.delete()
    
    
    def copy(self, destItem):
        # must also fix/update all the items guids
        self.__vcRep.copy(self.__absPath, destItem.__absPath)
        destItem.__setup()
        # OK now walk all the destItem items and give them new guids
        for itemList in destItem.walk():
            for item in itemList:
                self.__vcRep.applyNewID(item.__absPath)
    
    
    #==========  RENDER ===============
    def render(self, force=False, skipBooks=True, callback=None, **kwargs):
        # first get a list of files to be rendered
        toBeRenderedItemList = self.__getToBeRenderedList(force=force, skipBooks=skipBooks)
        count = 0
        total = len(toBeRenderedItemList)
        if not callable(callback):
            def callback(*args, **kwargs):
                pass
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

    def __render(self, force, **kwargs):
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
        return toBeRenderedList


    #==========  UPDATE ===============
    def _update(self, recurse=False, callback=None):
        # callback(absPath, depth [, question]) -> Yes/No to question
        #       question = "updateShelved?"
        self.__vcRep.update(self.__absPath, depth=recurse, callback=callback)
        self.__setup()


    #==========  COMMIT ===============
    def _commit(self, items=None, commitMessage="commit", callback=None):
        # get commit (relPaths) list
        # get revision number for update afterwards
        # NOTE: commit recursive !!!!!!!!!!!!!   so just commit this path and properties path!!!
        # Handle conflicts e.g. added item already exists etc
        if items is None:
            items = [self]
        paths = [i.__absPath for i in items]
        commitRev, emptyList, infinityList = self.__vcRep.commit(paths, commitMessage)
        return commitRev
    
    
    #==========  SYNC ===============
    # High level commit
    def _sync(self, items=None, commitMessage="commit", render=True, callback=None):
        if items is None:
            items = [self]
        if render:
            for item in items:
                item.render(callback=callback)
        for item in items:
            item._update()
        self._commit(items, commitMessage, callback)
        # reUpdate committed items
        #raise Exception("not implemented yet!")


    #================================
        
    def export(self, destAbsPath, callback=None, includeProperties=True):
        self.__vcRep.export(self.__absPath, destAbsPath,
                                includeProps=includeProperties)
    
    
    def getStatus(self, update=False):
        self.__vcStatus = self.__vcRep.getStatus(self.__absPath, includeServer=update)
        return self.__vcStatus
    
    
    def cleanup(self):
        self.__vcRep.cleanup(self.__absPath)
    
    ####################
    ####################
    
    
    def zipList(self):
        return self.__fs.zipList(self.__absPath)
    
    
    def extractFromZip(self, filename):
        data = None
        try:
            data = self.__fs.readFromZipFile(self.__absPath, filename)
        except: pass
        return data
    
    
    def replaceInZip(self, itemName, data):
        return self.__fs.addToZipFile(self.__absPath, itemName, data)
    
    
    def zipFromTempDir(self, absTempDir):
        try:
            absTempDir.zip(self.__absPath)
        except:
            self.write("")
            # and try again
            absTempDir.zip(self.__absPath)
        self.__setup()
    
    
    def unzipToTempDir(self, tempDir=None):
        absTempDir = self.__fs.unzipToTempDirectory(self.__absPath, tempDir)
        return absTempDir
    
    
    def walk(self, filter=None, filesOnly=False):
        """ yields a 'list of items' """
        # Note: filter will need to include - 'if item.isDirectory and not item.isMissing: return True'
        #       to walk directories
        return self.__walk(self, filter, filesOnly)
    def __walk(self, item, filter, filesOnly):
        if item.isFile:
            listItems = [self]
        else:
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
        uri = self.uri
        if self.isFile:
            if uri.startswith(self.relPath):
                r = True
            else:
                uriDiff = self.uriDiff
                # Also binary content if _files/*.jpg[/etc/]
                if uriDiff.startswith("_files/"):
                    r = True
                if uriDiff=="":
                    ext = self.__fs.splitExt(self.uri)[1]
                    if ext==self.ext:
                        r = True
                    elif ext!=".htm":
                        r = self.hasXRendition(ext)
        else:
            if uri.find("/skin/")!=-1:
                r = True
        return r
    
    
    def getBinaryContent(self):
        # return a tuple (data, mimeType)
        data = None
        mimeType = ""
        if self.isBinaryContent:
            #
            if self.uri.startswith(self.relPath):
                ext = self.ext.lower()
                if ext==".book.odt":
                    ext = ".odt"
                mimeType = self.iceContext.getMimeTypeForExt(ext)
                data = self.read()
            else:
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
        else:
            print "This is not a binary content item! relPath='%s'" % self.relPath
            pass
            #raise Exception("Is not a binary content item!")
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
    
    
    ############
    ############
    def packageCopy(self, destItem):
        # Note: This needs to be refactored
        raise Exception("not implemented yet!")


    def __getLastRenderedMd5(self):
        return self.__vcRep.propGet(self.__absPath, "_lastMD5")
    def __setLastRenderedMd5(self, md5=None):
        if md5 is None:
            md5 = self._getCurrentMd5()
        self.__vcRep.propSet(self.__absPath, "_lastMD5", md5)
    

    #==============================================================
    #==============================================================

    #==========  async Update ===============
    def asyncUpdate(self, updateItemList=None):
        if updateItemList is None:
            updateItemList = [self]
        id = self.iceContext.guid()
        job = None
        def worker():
            try:
                job = self.iceContext.getAsyncJob(id)
                status = job.status
                self.__asyncUpdateWorker(status, updateItemList)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
                print self.iceContext.formattedTraceback()
        job = self.iceContext.addAsyncJob(worker, id, message="Update")
        return job
    
    #==========  async Render ===============
    def asyncRender(self, itemList=None, force=False, skipBooks=False):
        if itemList is None:
            itemList = [self]
        id = self.iceContext.guid()
        job = None
        def worker():
            try:
                job = self.iceContext.getAsyncJob(id)
                status = job.status
                self.__asyncRenderWorker(status, itemList, force=force,
                                        skipBooks=skipBooks)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
                print self.iceContext.formattedTraceback()
        job = self.iceContext.addAsyncJob(worker, id, message="Render")
        return job


    #==========  async Sync ===============
    def asyncSync(self, itemList=None, force=False, skipBooks=True):
        if itemList is None:
            itemList = [self]
        id = self.iceContext.guid()
        job = None
        def worker():
            try:
                job = self.iceContext.getAsyncJob(id)
                status = job.status
                self.__asyncSyncWorker(status, itemList, force, skipBooks)
                self.iceContext.removeAsyncJob(id)
            except Exception, e:
                print "** Error '%s'" % str(e)
                print self.iceContext.formattedTraceback()
        job = self.iceContext.addAsyncJob(worker, id, message="Sync")
        return job


    
    #==============================================================
    def __asyncUpdateWorker(self, status, updateItemList, callback=None):
        resultDict = {}
        status.message = "Updating..."
        print " @ asyncUpdateWorker()"
        if callback is None:
            # callback(msg, absPath, depth [, question]) -> Yes/No to question
            #       question = "updateShelved?"
            def callback(msg, **kwargs):
                absPath = kwargs.get("absPath")
                depth = kwargs.get("depth")
                question = kwargs.get("question")
                r = None
                relPath = absPath[len(self.__fs.absPath()):]
                if relPath=="":
                    relPath = "/"
                if question=="updateShelved?":
                    r = relPath in [item.relPath for item in updateItemList]
                    if r==False:
                        return r
                print "@ Updating '%s' depth=%s" % (relPath, depth)
                status.message = "Updating '%s'" % relPath
                return r
        for item in updateItemList:
            try:
                item._update(recurse=True, callback=callback)
            except Exception, e:
                msg = "Failed to update '%s' - %s" % (item.relPath, str(e))
                resultDict["errors"] = [msg]
                resultDict["exception"] = e
                resultDict["cancelled"] = True
                break
        return resultDict
    


    #==============================================================
    def __asyncRenderWorker(self, status, itemList, force=False, skipBooks=False, callback=None):
        # callback used locally only
        if callback is None:
            def callback(id, **kwargs):
                #item = kwargs.get("item")
                displayMessage = kwargs.get("displayMessage")
                step = kwargs.get("step")
                exception = kwargs.get("exception")
                #method = kwargs.get("method")
                if step=="renderGettingList":
                    pass
                elif step=="rendering":
                    pass
                elif step=="rendered":
                    pass
                if displayMessage is not None:
                    status.message = displayMessage
                if exception is not None:
                    formattedTraceback = kwargs.get("traceback")
                    if formattedTraceback is not None:
                        print formattedTraceback

        toBeRenderedCount = 0
        renderingCount = 0
        renderedCount = 0
        errors = []
        resultDict = {}
        try:
            msg = "Getting render list..."
            print " @ asyncRenderWorker() %s" % msg
            # get list of items that need to be rendered
            callback("Rendering", item=self, displayMessage=msg, step="renderGettingList")
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
                    callback("Rendering", item=self, displayMessage=msg, step="rendering")
                    item.__render(force=force)
                    item.flush()
                    renderedCount += 1
                    callback("Rendering", item=self, step="rendered")
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


    def __asyncSyncWorker(self, status, itemList, force, skipBooks, callback=None):
        # if force==True then try and do a force sync
        errors = []
        if callback is None:
            def callback(id, **kwargs):
                pass
        # First do an update
        # Second do a render
        # Then third to the commit
        #  and last to another update
        try:
            print " @ asyncSyncWorker() step 1 (update)"
            # First do an update
            resultDict = self.__asyncUpdateWorker(status, itemList)
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
                resultDict = self.__asyncRenderWorker(status, itemList, 
                                                 force=False, skipBooks=False)      # defaults
                if resultDict.get("cancelled"):
                    raise resultDict.get("exception")
            # Then third to the commit
            print " @ asyncSyncWorker() step 3 (commit)"
            resultDict = self.__asyncCommitWorker(status, itemList)
            resultException = resultDict.get("exception")
            if resultException is not None:
                raise resultException
            # And last to another update
            print " @ asyncSyncWorker() step 4 (update)"
            #print "itemList='%s'" % [str(i) for i in itemList]
            resultDict = self.__asyncUpdateWorker(status, itemList)
            if resultDict.get("cancelled"):
                raise resultDict.get("exception")
            if False:
                print " @ asyncSyncWorker() step 5 (update parent(s))"
                parentItemList = self.__getParentItemList(itemList)
                print "parentItemList"
                for i in parentItemList:
                    print i
                resultDict = self.__asyncUpdateWorker(status, parentItemList, callback=callback)
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


    #=========== Commit Worker ==============
    def __asyncCommitWorker(self, status, listItems, callback=None):
        errors = []
        if callback is None:
            def callback(id, **kwargs):
                displayMessage = kwargs.get("displayMessage")
                exception = kwargs.get("exception")
                #step = kwargs.get("step")
                if displayMessage is not None:
                    status.message = displayMessage
                if exception is not None:
                    formattedTraceback = kwargs.get("traceback")
                    if formattedTraceback is not None:
                        print formattedTraceback

        resultDict = {"errors":[], "warnings":[], "infos":[]}
        try:
            msg = "Committing..."
            print " @ asyncCommitWorker() %s" % msg
            callback("Committing", item=listItems, displayMessage=msg, step="committing")
            self._commit(listItems)

            #parentsToCommit, itemsToCommit, updateParentAbsPaths = self.__getCommitItemList(listItems)
            #callback("Committing", item=self, step="commitGotList")
            #svn = self.iceContext.rep._svnRep
            #if parentsToCommit!=[]:
            #    print " @ asyncCommitWorker() committing parent items"
            #    msg = "Committing parent only items first"
            #    callback("Committing", item=self, displayMessage=msg, step="committingParents")
            #    iceParentPropertyDirs = [i for i in parentsToCommit if i.find("/.ice/")!=-1]
            #    svn.commitEmpty(parentsToCommit)
            #    svn.commitAll(iceParentPropertyDirs)
            #print " @ asyncCommitWorker() committing..."
            #msg = "Committing... (%s)" % len([i for i in itemsToCommit if not i.endswith("/.ice")])
            #callback("Committing", item=self, displayMessage=msg, step="committingList")
            ####
            ##print "calling svn.commitAll()"
            ####
            #svn.commitAll(itemsToCommit)
            #for absPath in updateParentAbsPaths:
            #    self.__svnRep.updateEmpty(absPath)
            ####
            ##print " done svn.commitAll()"
            ####
            print " @ asyncCommitWorker() commit completed"
            msg = "Committed ok"
            callback("Committing", item=self, displayMessage=msg, step="committed")
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


#    def __asyncUpdateWorker2(self, job, updateItemList, callback):
#        status = job.status
#        status.message = "Updating..."
#        print " @ asyncUpdateWorker()"
#
#        toBeUpdatedItemList = []
#        toBeUpdatedCount = 0
#        # Note: python closures can not write to closed variables (so access via a dict object)
#        access = {"updateCount":0, "updated":0, "errors":[]}
#
#        def updateCallback(item=None, displayMessage=None, step=None,
#                            exception=None, method=None, **extras):
#            #print " @@ updateCallback(step='%s')" % step
#            errors = []
#            job = extras.get("job")
#            if displayMessage is not None:
#                job.status.message = displayMessage
#            if step=="updating":
#                access["updateCount"] += 1
#                msg = "Updating %s of %s - '%s'" % \
#                        (access["updateCount"], toBeUpdatedCount, item.relPath)
#                errors = access["errors"]
#                if errors!=[]:
#                    msg += " (%s error(s) received)" % len(errors)
#                job.status.message = msg
#            elif step=="updated":
#                access["updated"] += 1
#            if exception is not None:
#                errorMsg = str(exception)
#                print "   @@ updateCallback exception='%s'" % errorMsg
#                formattedTraceback = extras.get("traceback")
#                if formattedTraceback is not None:
#                    print formattedTraceback
#                if step=="update":
#                    error = "Error updating '%s', error '%s'" % (item.relPath, errorMsg)
#                    errors = access["errors"]
#                    errors.append(error)
#                    if len(errors)>10:
#                        raise self.iceContext.IceCancelException("Too many errors")
#                else:
#                    raise exception
#
#        if callback is None:
#            callback = updateCallback
#
#        def jobCallback(*args, **kwargs):
#            # add job object to the arguments (for job.status.message="")
#            kwargs["job"] = job
#            callback(*args, **kwargs)
#
#        try:
#            # get list of items to be updated
#            updated = False
#            errors = []
#            status.message = "Getting update list."
#            try:
#                toBeUpdatedItemList = self.__getToBeUpdatedList(updateItemList, callback=jobCallback)
#                toBeUpdatedCount = len(toBeUpdatedItemList)
#                access["toBeUpdatedCount"] = toBeUpdatedCount
#            except Exception, e:
#                #print self.iceContext.formattedTraceback()
#                errors = [str(e)]
#                raise e
#            print " @* asyncUpdateWorker() toBeUpdatedItemList='%s'" % str([i.relPath for i in toBeUpdatedItemList])
#            # update all items in the list
#            try:
#                for item in toBeUpdatedItemList:
#                    item.__update(callback=jobCallback)
#            except Exception, e:
#                #formattedTraceback = self.iceContext.formattedTraceback()
#                errors = [str(e)]
#                raise e
#
#            updated = access["updated"]
#            errors = access["errors"]
#
#            if updated==toBeUpdatedCount and errors==[]:
#                # completed all ok
#                status.message = ""
#                status.resultSummary = "Completed updating"
#                if status.resultDetails.find("Rendered") <> -1:
#                    status.resultDetails = ""
#                if updated==0 or updated == "":
#                    status.resultDetails += "\nUpdated ok"
#                elif updated==1:
#                    status.resultDetails += "\nUpdated 1 item ok"
#                else:
#                    status.resultDetails += "\nUpdated %s items ok" % updated
#                print " @ asyncUpdateWorker() completed"
#            else:
#                status.resultSummary = "Completed updating (%s of %s) with errors" % (updated, toBeUpdatedCount)
#                status.resultError = "Updated with %s errors (see details below)" % len(errors)
#                status.resultDetails = "\n".join(errors)
#                if status.resultDetails=="":
#                    status.resultDetails = "No errors reported but update not completed?"
#                print " @ asyncUpdateWorker() %s" % status.resultSummary
#                print " @ " + status.resultDetails.replace("\n", "\n @ ")
#                print " @"
#        except self.iceContext.IceCancelException, e:
#            # "Too many errors"
#            #if str(e)=="Too many errors":
#            #    status.resultSummary = "Updated (%s of %s) with errors" % (updated, len(toBeUpdatedItemList))
#            #    status.resultError = "Updated with %s errors (see details below)" % len(errors)
#            #    status.resultDetails = "\n".join(errors)
#            #else:
#            if True:
#                status.resultSummary = "Updated %s of %s (operation cancelled)" % (updated, toBeUpdatedCount)
#                status.resultError = "Update cancelled"
#                if errors!=[]:
#                    status.resultError += " with %s errors (see details below)" % len(errors)
#                    status.resultDetails = "\n".join(errors)
#            access["exception"] = e
#            access["cancelled"] = True
#        except Exception, e:
#            status.resultSummary = "Unexpected exception in asyncUpdate()"
#            status.resultError = str(e)
#            formattedTraceback = self.iceContext.formattedTraceback()
#            print " @ asyncUpdateWorker unexpected exception - '%s'" % str(e)
#            print formattedTraceback
#            access["exception"] = e
#            access["formattedTraceback"] = formattedTraceback
#        return access

    ########
    @property
    def displaySourceType(self):
        return self.getMeta("_displaySourceType", False)
    
    @property
    def hasProperties(self):
        names = self.__vcRep.propList(self.__absPath)
        return len(names)>1

    def getRepName(self):
        # read repository name from /.ice/rep.name.txt if possible
        name = None
        absPath = self.__fs.absPath(".ice/rep.name.txt")
        name = self.__fs.read(absPath)
        return name

    def setRepName(self, name):
        absPath = self.__fs.absPath(".ice/rep.name.txt")
        self.__fs.write(absPath, name)
    
    #==============================================================
    def toString(self, full=True):
        s = "[IceItem2 object] name='%s', relPath='%s'" % (self.name, self.relPath)
        if full:
            s += ",\n guid='%s', uri='%s'" % (self.guid, self.uri)
            s += ",\n name='%s'" % (self.name)
            s += ",\n relPath='%s', _absPath='%s'" % (self.relPath, self._absPath)
            s += ",\n exists='%s', isFile='%s', isDirectory='%s'" % (self.exists, self.isFile, self.isDirectory)
            s += ",\n isVersioned='%s', lastChangedRevisionNumber='%s'" % (self.isVersioned, self.lastChangedRevisionNumber)
            s += ",\n vcStatus='%s'" % (self.vcStatus)
            s += ",\n hasPdf='%s', hasHtml='%s', hasSlide='%s'" % (self.hasPdf, self.hasHtml, self.hasSlide)
            s += ",\n needsUpdating='%s', convertFlag='%s'" % (self.needsUpdating, self.convertFlag)
        return s
    
    
    def __str__(self):
        return self.toString(False)
    
    def __cmp__(self, other):
        if other is None:
            return -1
        r = cmp(other.isDirectory, self.isDirectory)
        if r==0:
            r = cmp(self.name, other.name)
        return r
    











