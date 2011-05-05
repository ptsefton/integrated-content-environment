
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
import time
import re
import string
import base64
from cPickle import loads, dumps


pluginName = "ice.fileManager"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    path = iceContext.fs.split(__file__)[0]
    FileManager.TEMPLATE_FILE = iceContext.fs.join(path, "file-manager.tmpl")
    pluginFunc = None
    FileManager.HtmlTemplate = iceContext.HtmlTemplate
    pluginClass = FileManager
    pluginInitialized = True
    return pluginFunc



class FileManager:
    TEMPLATE_FILE = "file-manager.tmpl"
    HtmlTemplate = None             # injected data
    
    odtDefaultTemplateFilename = "Default.odt"
    docDefaultTemplateFilename = "Default.doc"
    bookDefaultTemplateFilename = "Default.odt"
    
    @staticmethod
    def GetAddTemplates(iceContext, rep, fs, templateDirectory=None):
        # Returns a list of tuples
        if templateDirectory is None:
            templateDirectory = str(rep.documentTemplatesPath)
        
        if fs.isDirectory(templateDirectory):
            #absolute dir - list files
            templateDirList = fs.listFiles(templateDirectory)
        else:
            #relative to current rep - list items
            templateDirItem = rep.getItem(templateDirectory)
            templateDirList = [item.name for item in templateDirItem.listItems() \
                               if item.isFile]
        
        splitExt = iceContext.iceSplitExt
        
        wordList = [file for file in templateDirList \
                    if fs.splitExt(file)[1]==iceContext.wordExt]
        wordList.sort()
        wordNames = [splitExt(i)[0] + " (doc)" for i in wordList]
        
        word2007List = [file for file in templateDirList \
                        if fs.splitExt(file)[1]==iceContext.word2007Ext]
        word2007List.sort()
        word2007Names = [splitExt(i)[0] + " (docx)" for i in word2007List]
        
        odtList = [file for file in templateDirList \
                   if splitExt(file)[1]==iceContext.oooDefaultExt]
        odtList.sort()
        odtNames = [splitExt(i)[0] + " (odt)" for i in odtList]
        
        bookList = [file for file in templateDirList \
                    if splitExt(file)[1] in iceContext.bookExts]
        bookList.sort()
        bookNames = [splitExt(i)[0] + " (book)" for i in bookList]
        
        wordNames.sort()
        word2007Names.sort()
        odtNames.sort()
        bookNames.sort()
        
        names = odtNames + wordNames + word2007Names + bookNames
        values = odtList + wordList + word2007List + bookList

        return zip(names, values)
    
    
    def __init__(self, iceSite, fileSystem, message=""):
        self.iceContext = iceSite.iceContext
        self.__fs = fileSystem
        self.__session = iceSite.session
        self.__workingOffline = self.__session.workingOffline
        self.__packagePath = ""
        self.__manifest = iceSite.manifest
        self.__inPackage = self.__manifest is not None
        
        if self.__inPackage:
            self.__packagePath = iceSite.packageItem.relPath
        self.__rep = iceSite.rep
        self.__item = iceSite.item
        self.__directory = iceSite.item.relPath
        if not self.__directory.endswith("/"):
            self.__directory += "/"
        formData = iceSite.formData
        
        self.__templateDirectory = str(self.__rep.documentTemplatesPath)
        #check if absolute template path exists
        if self.__fs.isDirectory(self.__templateDirectory):
            fullTemplateDirectory = self.__templateDirectory
        else:
            fullTemplateDirectory = self.__rep.getAbsPath(self.__templateDirectory)
        
        #check the available default template (ignore the case)
        if self.__fs.isDirectory(fullTemplateDirectory):
            files = self.__fs.listFiles(fullTemplateDirectory)
            for file in files:
                ext = self.iceContext.iceSplitExt(file)[1]
                if (ext == ".odt"):
                    if (str(file).upper() == "DEFAULT.ODT"):
                        self.odtDefaultTemplateFilename = file
                        self.bookDefaultTemplateFilename = file
                if (ext == ".doc"):
                    if (str(file).upper() == "DEFAULT.DOC"):
                        self.docDefaultTemplateFilename = file
        
        self.__templateBooksDirectory = self.iceContext.url_join(self.__templateDirectory, "books")
        self.__odtDefaultTemplateFile = self.iceContext.url_join(self.__templateDirectory, self.odtDefaultTemplateFilename)
        self.__docDefaultTemplateFile = self.iceContext.url_join(self.__templateDirectory, self.docDefaultTemplateFilename)
        self.__bookDefaultTemplateFile = self.iceContext.url_join(self.__templateBooksDirectory, self.bookDefaultTemplateFilename)
        self.__isPostBack = False
        self.__selected = []
        self.__uploadedFilenameDatas = []
        self.__renameId = ""
        self.__ignoreStartswith = []
        self.__ignoreEndswith = [".DS_Store"]
        
        self.__message = message
        self.__resultSummary = ""
        self.__resultDetails = ""
        self.__resultWarning = ""
        self.__resultError = ""
        self.__title = "ICE file view"      # default only
        self.__newFolderName = ""
        self.__addNewFolderMessage = ""
        
        # All and any needed data from formData
        if formData.has_key("ispostback") and formData.method=="POST":
            self.__isPostBack = True
            self.__selected = formData.values("selected")
            
            for uploadFileKey in formData.uploadFileKeys():
                filename = formData.uploadFilename(uploadFileKey)
                filename = self.__fs.split(filename)[1]
                data = formData.uploadFileData(uploadFileKey)
                if filename!="":
                    self.__uploadedFilenameDatas.append((filename, data))
        
        actType = formData.value("actType", "")
        actSubType = formData.value("actSubType", "")
        actData = formData.value("actData", "")
        self.__all = formData.value("all", "")!=""
        self.__isAjax = bool(formData.value("ajx", False))
        self.__ajaxData = "ajax data"
        showStatus = formData.value("showStatus", "")
        if not self.__workingOffline and showStatus!="":
            self.__session["serverStatus"] = showStatus.lower()=="true"
        self.__logComment = formData.value("logComment", "").strip()
        self.__postCount = int(formData.value("postCount", "0"))
        # restore state
        self.__state = self.__session.get("FileManagerState", None)
        if self.__state is None:
            self.__state = _State()
            self.__session["FileManagerState"] = self.__state
        ##self.__updateStateInfo()
        
        itemStatus = None
        self.__dirItem = self.__rep.getItem(self.__directory)
        if self.__dirItem.isVersioned==False:
            self.__dirItem.add()
        
        self.message = ""
        
        # check templates file names
        if not self.__rep.getItem(self.__odtDefaultTemplateFile).isFile:
            self.__odtDefaultTemplateFile = self.__odtDefaultTemplateFile.lower()
        if not self.__rep.getItem(self.__docDefaultTemplateFile).isFile:
            self.__docDefaultTemplateFile = self.__docDefaultTemplateFile.lower()
        
        self.enablePaste = False
        self.enablePaste = False
        self.__editBookFile = None
        self.downloadFile = None
        self.downloadData = None
        self.__processAction(actType, actSubType, actData, self.__all)
        if self.__isAjax and formData.value("func", "")=="fileManager":
            self.__ajaxData = self.getContent()
    
    
    @property
    def title(self):
        return self.__title
    
    @property
    def isAjax(self):
        return self.__isAjax
    
    @property 
    def ajaxData(self):
        return self.__ajaxData
    
    @property
    def editBook(self):
        return self.__editBookFile is not None
    
    @property 
    def editBookFile(self):
        return self.__editBookFile
    
    def getAddTemplates(self):
        # Returns a list of tuples
        return FileManager.GetAddTemplates(self.iceContext, self.__rep, \
                            self.__fs, self.__templateDirectory)
##    
##        templateDirItem = self.__rep.getItem(self.__templateDirectory)
##        wordList = [item.name for item in templateDirItem.listItems() \
##                    if item.isFile and item.ext==self.iceContext.wordExt]
##        wordList.sort()
##        wordNames = [self.__fs.splitExt(i)[0] + " (doc)" for i in wordList]
##        
##        odtList = [item.name for item in templateDirItem.listItems() \
##                    if item.isFile and item.ext==self.iceContext.oooDefaultExt]
##        odtList.sort()
##        odtNames = [self.__fs.splitExt(i)[0] + " (odt)" for i in odtList]
##        
##        bookList = [item.name for item in templateDirItem.listItems() \
##                    if item.isFile and item.ext in self.iceContext.bookExts]
##        bookList.sort()
##        bookNames = [self.__fs.splitExt(i)[0] + " (book)" for i in bookList]
##        
##        wordNames.sort()
##        odtNames.sort()
##        bookNames.sort()
##        names = odtNames + wordNames + bookNames
##        values = odtList + wordList + bookList
##        return zip(names, values)
    
    
    def getOdtTemplates(self): 
        templateDirItem = self.__rep.getItem(self.__templateDirectory)
        odtList = []
        odtNames = []
        
        templateItems = templateDirItem.listItems()
        if templateItems != []:
            #This only for the template exist in the same rep
            for item in templateDirItem.listItems():
                templateDirPath = self.__rep.getAbsPath(templateDirItem.relPath)
                if item.isFile and item.ext==self.iceContext.oooDefaultExt:
                    odtList.append(self.__fs.join(templateDirPath, item.name))
    #        odtList = [item.name for item in templateDirItem.listItems() \
    #                    if item.isFile and item.ext==self.iceContext.oooDefaultExt]
        else:
            #try to use absolute path to get the template files that exist in different rep
            if self.__fs.isDirectory(self.__templateDirectory):
                templateDirList = self.__fs.listFiles(self.__templateDirectory)
                templateDirAbsPath = self.__fs.absolutePath(self.__templateDirectory)
                for file in templateDirList:
                    fileAbsPath = self.__fs.join(templateDirAbsPath, file)
                    ext = self.iceContext.iceSplitExt(file)[1]
                    if self.__fs.isFile(fileAbsPath) and ext==self.iceContext.oooDefaultExt:
                        odtList.append(fileAbsPath)
                    
        odtList.sort()
        odtNames = [self.__fs.splitPathFileExt(i)[1] for i in odtList]
        return zip(odtNames, odtList), self.__session.get("repairTemplate", "")
    
    
    # Main worker method
    def getContent(self):
        mark = self.iceContext.gTime.mark
        html = ""
        # Current (linked) path
        path = "/"
        pathParts = [(path, path)]
        tmpDir = self.iceContext.urlJoin(self.iceContext.urlRoot, self.__directory)
        for item in tmpDir.split("/"):
            if item != "":
                path = self.iceContext.urlJoin(path, item)
                pathParts.append((path + "/", item + "/"))
        self.__title = "ICE file view - %s" % path
        
        job = self.__session.asyncJob
        if job is not None and not job.isFinished:
            html = "<div class='app-file-manager'><div>&#160;</div></div>" 
            self.includeStyle = ""
            self.enablePaste = self.__state.savedFor!=""
            return html
        
        htmlTemplate = self.HtmlTemplate(templateFile=self.TEMPLATE_FILE, allowMissing=True)
        repName = self.__rep.name
        
        # setup dataDict
        dataDict = {"toHtmlStr":self.iceContext.HtmlStr}
        dataDict["pathParts"] = pathParts
        dataDict["resultError"] =  self.__resultError
        dataDict["resultWarning"] = self.__resultWarning
        dataDict["resultSummary"] = self.__resultSummary
        dataDict["resultDetails"] = self.__resultDetails
        dataDict["hasProperties"] = self.__item.hasProperties
        dataDict["message"] = self.__message
        dataDict["isVersioned"] = self.__item.isVersioned
        #dataDict["isVersioned"] = True
        if self.isAjax and job is not None and job.status.resultSummary!="":
            status = job.status
            dataDict["resultSummary"] = status.resultSummary
            dataDict["resultDetails"] = status.resultDetails
            dataDict["resultError"] = status.resultError
            status.resultSummary = ""
        
        dataDict["postCount"] = str(self.__session.get("postCount", 0))
        dataDict["newFolderName"] = self.__newFolderName
        dataDict["addNewFolderMessage"] = self.__addNewFolderMessage
        dataDict["isServer"] = self.iceContext.isServer
        
        tmp = ""
        for link, name in pathParts:
            if link == self.__directory:
                tmp += "<span class='current-url'>%s</span>" % name
            else:
                tmp += "<a href='%s'>%s</a>" % (link, name)
        
        dataDict["currentLinkedPath"] = self.iceContext.HtmlStr(tmp)
        dataDict["path"] = path
        dataDict["workingOffline"] = self.__workingOffline
        if self.iceContext.isServer:
            dataDict["workingOffline"] = False
        dataDict["copied"] = self.__state.savedFor!=""
        dataDict["odtTemplate"] = self.__rep.getItem(self.__odtDefaultTemplateFile).isFile
        dataDict["docTemplate"] = self.__rep.getItem(self.__docDefaultTemplateFile).isFile
        dataDict["bookTemplate"] = self.__rep.getItem(self.__bookDefaultTemplateFile).isFile
        dataDict["inPackage"] = self.__inPackage
        dataDict["logComment"] = self.__logComment
        parentDirectory = self.__fs.split(self.__item.relPath.rstrip("/"))[0]
        if not parentDirectory.endswith("/"):
            parentDirectory += "/"
        dataDict["parentDirectory"] = parentDirectory
        showServerStatus = self.__session.get("serverStatus", False)
        dataDict["showStatus"] = showServerStatus
        entries = self.__getEntries(self.__directory)
        dataDict["entries"] = entries
        dataDict["renameId"] = self.__renameId
        dataDict["directory"] = self.__directory
        dataDict["splitExt"] = self.__fs.splitExt
        dataDict["repName"] = repName
        dataDict["target"] = ""
        dataDict["all"] = self.__all

        dataDict["textToSpeechServiceAva"] = False
        def getTtsPluginObj():
            tts = None
            TtsPlugin = self.iceContext.getPluginClass("ice.extra.textToSpeech")
            if TtsPlugin is not None:
                tts = TtsPlugin(self.iceContext)
            return tts
        tts = self.iceContext.getObjectFromCache("textToSpeech", getTtsPluginObj)
        ##print "plugin_file_manager.py 381 - tts='%s' %s" % (tts, tts and tts.isTextToSpeechAvailable)
        if tts is not None:
            dataDict["textToSpeechServiceAva"] = tts.isTextToSpeechAvailable
        
        # -- Apply TEMPLATE --
        html = htmlTemplate.transform(dataDict)
        if htmlTemplate.missing!=[]:
            print "----"
            print "Missing items from template='%s'" % str(htmlTemplate.missing)
            print "----"
        self.includeStyle = htmlTemplate.includeStyle
        self.enablePaste = self.__state.savedFor!=""
        return html
    
    
    def __getEntries(self, path, level=1):
        entries = []
        ##
        session = self.__session
        showServerStatus = session.get("serverStatus", False)
        online = not self.__workingOffline
        update = online and showServerStatus
        
        listItems = self.__dirItem.listItems(update)
        listItems.sort()
        for listItem in listItems:
            if update:
                listItem.getStatus(update=update)
            if not listItem.isVersioned:
                if not listItem.isIgnored:
                    listItem.add()
                    listItem.getStatus(update=update)
            if listItem.isHidden and listItem.name!="src":
                continue
            path = listItem.relPath
            name = listItem.name
            if name==".":
                continue
            isDir = listItem.isDir
            iceExt = self.iceContext.iceSplitExt(name)[1]
            
            entry = _Entry(self.iceContext, name)
            entry.fullPath = path
            entry.url = self.iceContext.urlQuote(path)
            entry.idUrl = entry.url
            entry.isDir = isDir
            if path.endswith(".zip"):
                title = "unzip %s" % name 
                title = self.iceContext.urlQuote(title)
                option = {"class":"unzip", "title":title, "name":"Unzip"}
                entry.extraOptions.append(option)
            
            entry.status = listItem.getCompleteStatus()
            entry.canRevert = entry.status.lower().find("added")==-1
            entry.hidden = listItem.isHidden
            
            try:
                t = listItem.lastModifiedDateTime
            except Exception, e:
                t = 0
            entry.setLastModified(t)
            if isDir:
                entry.title = entry.name
                if not entry.fullPath.endswith("/"):
                    entry.fullPath += "/"
                #if idKey in self.__state.expandedList:
                #    entry.subEntries = self.__getEntries(fullPath, level+1)
            else:
                #print listItem.name
                #print "  title='%s'" % listItem.getMeta("title", "")
                if listItem.exists==False:
                    entry.title = ""
                else:
                    entry.title = listItem.getMeta("title", "")
                # use manifest title if available and not for src items
                if listItem.parentItem.name != "src":
                    if self.__manifest is not None:
                        mItem = self.__manifest.getManifestItem(listItem.guid)
                        if mItem is not None:
                            mTitle = mItem.manifestTitle
                            if mTitle is not None:
                                entry.title = mTitle
                if listItem.exists and not listItem.isMyChanges:
                    #print "*Entry - '%s' (%s)" % (entry.name, iceExt)
                    renderExts = [".odt", ".doc", ".book.odt", ".html", ".png", ".jpg", ".gif", ".ppt", ".odp"]
                    renderExts.extend(self.iceContext.rep.render.getRenderableExtensions())
                    if iceExt in renderExts:
                        entry.isIceDisplayable = True
                    if iceExt in [".odt", ".doc", ".ods", ".ppt", ".odp", ".docx"]:
                        entry.displaySourceTypeOption = True
                    if iceExt in [".odt", ".doc", ".book.odt"]:
                        entry.linkAsEndnoteOption = True
                        entry.tocLevels = str(listItem.getMeta("_tocLevels", 2))
                    else:
                        entry.linkAsEndnoteOption = False
                    if iceExt in [".odt", ".doc", ".book.odt", ".html", ".txt"]:
                        entry.renderAudioOption = True
                        if listItem.inPackage:
                            entry.glossaryOption = True
                            entry.glossaryTermsOption = True
                    else:
                        entry.renderAudioOption = False
                        entry.glossaryOption = False
                        entry.glossaryTermsOption = False
                    
                    entry.displaySourceType = listItem.getMeta("_displaySourceType", False)
                    if True:
                        if listItem.getMeta("_convertLinksToEndNote"):
                            entry.endNoteselected = True
                        if listItem.getMeta("_renderAudio") and listItem.convertFlag:
                            entry.renderAudioSelected = True
                        if listItem.getMeta("_glossary"):
                            entry.glossarySelected = True
                        if listItem.getMeta("_glossary_terms"):
                            entry.glossaryTermsSelected = True
                        entry.iceContent = listItem.convertFlag
                        if listItem.hasHtml:
                            entry.viewAs = "html"
                            entry.link = self.__fs.splitExt(path)[0] + ".htm"
                        elif listItem.hasPdf:
                            entry.viewAs = "pdf"
                            entry.link = self.__fs.splitExt(path)[0] + ".pdf"
                            entry.link = path[:-len(listItem.ext)] + ".pdf"
                        elif listItem.name=="manifest.xml":
                            entry.viewAs = "manifest"
                            #entry.link = self.__fs.split(path)[0] + "/edit_manifest"  # organizer
                            entry.link = path       # view the xml content
                        else:
                            if self.__rep.mimeTypes.has_key(iceExt):
                                entry.viewAs = iceExt[1:]
                                entry.link = path
                        ## entry.idUrl
                        entry.idUrl = self.iceContext.urlQuote(listItem.getIdUrl())
            if entry.filename in self.__selected:
                entry.selected = True
            # Editable
            ext = self.__fs.splitExt(entry.name)[1]
            entry.isEditable = (ext==self.iceContext.oooDefaultExt or ext==self.iceContext.wordExt or \
                    ext==self.iceContext.oooMasterDocExt or ext in self.iceContext.bookExts or \
                    ext==self.iceContext.wordDotExt or ext==self.iceContext.word2007Ext)
            entry.title = self.iceContext.textToHtml(entry.title)
            entry.title = self.iceContext.cleanUpString(entry.title)
            entries.append(entry)
        return entries    
    
    
    def __processAction(self, actType, actSubType, actData, all=False):
        tmp = None
        if actType=="":
            return
        print "actType='%s', actSubType='%s', actData='%s'" % (actType, actSubType, actData)
        if actType=="add":
            if actSubType=="folder":
                self.__addFolder(actData)
            else:
                self.__createNewFile(actSubType, actData)
        elif actType=="upload":                         # Upload a file
            self.__uploadFile()
        elif actType=="deselect":
            self.__deselect()
        elif actType=="copy":                           # Copy
            self.__resultSummary = "Copied item"
            self.__copy([actData])
        elif actType=="copySelected":                   # Copy selected files
            self.__resultSummary = "Copied selected items"
            self.__copy(self.__selected)
        elif actType=="cut":                            # Cut
            self.__resultSummary = "Cut item"
            self.__cut([actData])
        elif actType=="cutSelected":                    # Cut selected files
            self.__resultSummary = "Cut selected items"
            self.__cut(self.__selected)
        elif actType=="delete":                         # Delete
            files = [self.__directory + file for file in [actData]]
            self.__delete(files)
        elif actType=="deleteSelected":                 # Delete selected files
            files = [self.__directory + file for file in self.__selected]
            self.__delete(files)
        elif actType=="revert":                         # Revert
            self.__resultSummary = "reverted item"
            self.__revert([actData])
        elif actType=="revertSelected":                 # revert selected files
            self.__resultSummary = "reverted selected item(s)"
            if all:
                self.__revert([""])
            else:
                self.__revert(self.__selected)
        elif actType=="sync":                           # Sync
            if self.iceContext.session.loggedIn:
                self.__resultSummary = "Sync'ed item"
                self.__sync([actData])
            else:
                self.__resultSummary = "Synchronization failed. Please log in"
                self.__ajaxData = self.getContent()
        elif actType=="syncSelected":                   # sync selected files
            if self.iceContext.session.loggedIn:
                self.__resultSummary = "Sync'ed selected item(s)"
                if all or self.__selected == []:
                    self.__sync([""])
                else:
                    self.__sync(self.__selected)
            else:
                self.__resultSummary = "Synchronization failed. Please log in"
                self.__ajaxData = self.getContent()
        elif actType=="forceSyncSelected":              # force sync selected files
            self.__resultSummary = "(Forced) Sync'ed selected item(s)"
            self.__sync(self.__selected, force=True)
        elif actType=="update":
            self.__resultSummary = "Updated item"
            self.__update([actData])
        elif actType=="updateSelected":                 # update selected files
            self.__resultSummary = "Updated selected item(s)"
            if all:
                self.__update([""])
            else:
                self.__update(self.__selected)
        elif actType=="testSelected":
            s = self.__selected
            if all: s = [""]
            self.__testSelected(s)
        elif actType=="reRenderSelected":               # reRender selected files
            self.__resultSummary += "Rendered"
            self.__reRender(self.__selected, False)
        elif actType=="forceReRenderSelected":          # force reRender selected files
            self.__resultSummary += "Force rendered"
            self.__reRender(self.__selected, True)
        elif actType=="convertSelectedToOOo":           # convert selected files to writer
            self.__convertTo(self.__selected, self.iceContext.oooDefaultExt)
        elif actType=="convertSelectedToWord":          # convert selected files to writer
            self.__convertTo(self.__selected, self.iceContext.wordExt) 
        #elif actType=="repairSelectedToWord":           # repair selected files
        elif actType=="repairSelected":
            self.__session["repairTemplate"] = actSubType            
            repairTemplateFile = actSubType
            if repairTemplateFile == "":
                repairTemplateFile = None
            self.__repair(self.__selected, repairTemplateFile)
        elif actType=="paste":                        # paste
            self.__paste(actData)
        elif actType=="rename":                       # rename
            #print "renameTo('%s', '%s')" % (actData, actSubType)
            self.__renameTo(actData, actSubType)        
        elif actType=="log":
            self.__log(actData)
        elif actType=="shelve":
            files = [self.__directory + file for file in [actData]]
            self.__shelve(files)
        elif actType=="edit":
            self.__edit(actData)
        elif actType=="download":
            self.__download(actData, actSubType)
        elif actType=="editBook":
            tmp = self.__editBook(actData)         #
        elif actType=="svnCleanup":
            self.__svnCleanup()
        elif actType=="display-source-type":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.setMeta("_displaySourceType", newState)
            sState = item.getMeta("_displaySourceType")
            item.close()
            if sState:
                self.__ajaxData = "1"
            else:
                self.__ajaxData = "0"
        elif actType=="ice-content":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.convertFlag = newState
            sState = item.convertFlag
            item.close()
            if sState:
                self.__ajaxData = "1"
            else:
                self.__ajaxData = "0"
        elif actType=="links-as-endnotes":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.setMeta("_convertLinksToEndNote", newState)
            item.touch()
            sState = item.getMeta("_convertLinksToEndNote")
            item.close()
            if sState:
                self.__ajaxData = "1"
            else:
                self.__ajaxData = "0"
        elif actType=="render-audio":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.setMeta("_renderAudio", newState)
            item.touch()
            sState = item.getMeta("_renderAudio")
            item.close()
            if sState:
                self.__ajaxData = "1"
            else:
                self.__ajaxData = "0"
        elif actType=="glossary":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.setMeta("_glossary", newState)
            item.touch()
            sState = item.getMeta("_glossary")
            item.close()
            packageItem = item.packageRootItem
            glossaryItems = packageItem.getMeta("glossary-items")
            if glossaryItems is None:
                items = set([item.relPath])
            else:
                items = set(loads(glossaryItems))
            if sState:
                self.__ajaxData = "1"
                items.add(item.relPath)
                print " @ adding '%s' to glossary items" % item.relPath
            else:
                self.__ajaxData = "0"
                items.remove(item.relPath)
                print " @ removing '%s' from glossary items" % item.relPath
            packageItem.setMeta("glossary-items", dumps(items))
            packageItem.close()
        elif actType=="glossary-terms":
            newState = actSubType.lower()=="true"
            item = self.__rep.getItem(self.__directory + actData)
            item.setMeta("_glossary_terms", newState)
            item.touch()
            sState = item.getMeta("_glossary_terms")
            item.flush()
            if sState:
                self.__ajaxData = "1"
                item.touch()
            else:
                self.__ajaxData = "0"
        elif actType=="tocLevels":
            levels = 2      # default
            try:
                levels = int(actSubType)
            except:
                pass
            item = self.__rep.getItem(self.__directory + actData)
            print "** tocLevels - %s" % levels
            item.touch()
            item.setMeta("_tocLevels", levels)
            item.flush()
            self.__ajaxData = str(levels)
        elif actType=="unzip":
            item = self.__rep.getItem(self.__directory + actData)
            self.__unzip(item)
        elif actType=="refresh":
            pass
        elif actType=="":
            pass
        elif actType!="disabled":
            print "Unknown actType '%s'" % actType
            self.__resultSummary += "Unknown actType '%s'?" % actType
        return tmp
    
    
    def __addFolder(self, folderName):
        self.__resultSummary = ""
        folderName = folderName.strip()
        if folderName!="":
            fullPath = self.iceContext.url_join(self.__directory, folderName)
            if self.__rep.getItem(fullPath).exists:
                self.__resultSummary = "'%s' already exists" % fullPath
            elif re.search("[^a-z A-Z 0-9_\\.-]", folderName):
                # does not contain invalid characters
                self.__resultSummary = "Failed to add new folder '%s' invalid character(s)" % (folderName)
            else:
                item = self.__rep.getItem(fullPath)
                item.makeDirectory()
        self.__newFolderName = folderName
        self.__addNewFolderMessage = self.__resultSummary
    
    
    def __createNewFile(self, fromFile, toFile):
        fromExt = self.iceContext.iceSplitExt(fromFile)[1]
        fromFile = self.__fs.join(self.__templateDirectory, fromFile)
        toName, toExt = self.iceContext.iceSplitExt(toFile)
        #print "__createNewFile(fromFile='%s', toFile='%s')" % (fromFile, toFile)
        #print "  fromExt='%s', toExt='%s', toName='%s'" % (fromExt, toExt, toName)
        if toExt!=fromExt:
            toFile += fromExt
        # check if toName is OK to use
        result, reason = self.__isFilenameOK(toFile)
        if result==False:
            self.__resultSummary = "Failed to add new file '%s' %s" % (toFile, reason)
        else:
            # filename is OK
            fromFile = self.iceContext.url_join(self.__templateDirectory, fromFile)
            toFile = self.iceContext.url_join(self.__directory, toFile)
            self.__copyFiles([fromFile], toFile)
            #print "fromFile='%s', toFile='%s'" % (fromFile, toFile)
            if self.__resultError=="":
                self.__resultSummary = ""
    
    def __copy(self, files):
        print "Copied '%s'" % str(files)
        self.__state.saveForCopy(files, self.__directory, self.__rep)
        self.__ajaxData = str(len(files))
    
    
    def __cut(self, files):
        print "Cut '%s'" % str(files)
        self.__state.saveForCut(files, self.__directory, self.__rep)
        self.__ajaxData = str(len(files))
    
    def __deselect(self):
        print "deselected cut/copy"
        self.__state.clearSaveFor()
        self.__ajaxData = "0"
    
    def __delete(self, files):
        sourceRep = self.__state.sourceRep
        if sourceRep is None:
            sourceRep = self.__rep
        for file in files:
            #print "would have Deleted '%s'" % file
            #continue
            try:
                item = sourceRep.getItem(file)
                try:
                    # remove from package glossary items
                    packageItem = item.packageRootItem
                    if packageItem is not None:
                        glossaryItems = packageItem.getMeta("glossary-items")
                        if glossaryItems is not None:
                            items = set(loads(glossaryItems))
                            items.discard(item.relPath)
                            packageItem.setMeta("glossary-items", dumps(items))
                            packageItem.close()
                            print " @ removed '%s' from glossary items" % item.relPath
                except Exception, e:
                    print "Error - '%s'" % str(e)
                item.delete()
                self.__resultDetails += "Deleted '%s' \n" % file
            except Exception, e:
                msg = "Error deleting '%s'" % file
                print "Error='%s'" % str(e)
                self.__resultDetails += msg + "\n"
                if self.__resultSummary=="":
                    self.__resultSummary = msg
                else:
                    self.__resultSummary = "Error deleting files"
                self.__resultError += "\n  Error trying to delete '%s' - error message: %s" % (file, str(e))
                self.__resultError += "<br /> "
        if self.__resultError=="":
            self.__resultSummary = "Deleted file(s)"
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __shelve(self, files):
        for file in files:
            item = self.__rep.getItem(file)
            if item.isDirectory:
                print "__shelve()"
                print "__shelve relPath='%s', hasChanges=%s" % (item.relPath, item.hasChanges)
                if item.hasChanges:
                    self.__resultWarning = "Cannot 'shelve' '%s' because it " + \
                        "currently has changes that have not been synchronized. " + \
                        " Please 'synchronize' changes first, or revert changes, before trying again."
                    self.__resultWarning = self.__resultWarning % item.relPath
                else:
                    try:
                        item.shelve()
                    except self.iceContext.IceException, e:
                        if str(e)=="Cannot remove modified content!":
                            self.__resultWarning = "Cannot 'shelve' '%s' because it " + \
                                "currently has changes that have not been synchronized. " + \
                                " Please 'synchronize' changes first, or revert changes, before trying again."
                            self.__resultWarning = self.__resultWarning % item.relPath
                        else:
                            raise
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __revert(self, files):
        for file in files:
            file = self.__directory + file
            #print "would have Reverted '%s'" % file
            #continue
            try:
                item = self.__rep.getItem(file)
                item.revert()
                self.__resultDetails += "Reverted '%s' \n" % file
            except Exception, e:
                self.__resultDetails += "Error reverting '%s'" % file
                if self.__resultSummary=="":
                    self.__resultSummary = "Error reverting '%s'" % file
                else:
                    self.__resultSummary = "Error reverting files"
                match = re.search("' to '(.*?)': Access is denied.", str(e))
                if match!=None:
                    path = match.group(1)
                    self.__resultError += "Error reverting '%s'\n - file '%s' is not accessable! (close the program that is accessing this file and try again)\n" % (file, path)
                else:    
                    self.__resultError += "Error reverting '%s' - error message: %s. \n" % (file, str(e))
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __testSelected(self, files):
        files = [self.__directory + f for f in files]
        if False:
            print "test - files='%s'" % str(files)
            pairs = self.__rep.getUpdatePairs(files, True)
            for pair in pairs:
                print str(pair)
            print " ---"
            print
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __sync(self, files, force=False):
        commitMsg = self.__logComment
        files = [self.__directory + file for file in files]
        items = [self.__rep.getItem(file) for file in files]
        if items!=[]:
            job = items[0].asyncSync(itemList=items, force=force, skipBooks=False)
            self.iceContext.session.asyncJob = job
        self.__selected = []
        self.__state.clearSaveFor()
        self.__ajaxData = self.getContent()
    
    
    def __update(self, files):
        # the new async update
        files = [self.__directory + f for f in files]
        items = [self.__rep.getItem(file) for file in files]
        if items!=[]:
            job = items[0].asyncUpdate(items)
            self.iceContext.session.asyncJob = job
        self.__selected = []
        self.__state.clearSaveFor()
        self.__ajaxData = self.getContent()
    
    
    def __reRender(self, files, force=False):
        # the new async update
        files = [self.__directory + f for f in files]
        items = [self.__rep.getItem(file) for file in files]
        if items!=[]:
            job = items[0].asyncRender(items, force=force, skipBooks=False)
            self.iceContext.session.asyncJob = job
        self.__selected = []
        self.__state.clearSaveFor()
        self.__ajaxData = self.getContent()
    
    
    def __convertTo(self, files, ext):
        if ext==self.iceContext.wordExt:
            toWord = True
        elif ext==self.iceContext.oooDefaultExt:
            toWord = False
        else:
            self.__resultSummary = "Unsupport to conversion type '%s'" % ext
            return
        if toWord:
            fromExt = [self.iceContext.oooDefaultExt, self.iceContext.oooSxwExt]
            toExt = self.iceContext.wordExt
        else:
            fromExt = [self.iceContext.wordExt, self.iceContext.word2007Ext]
            toExt = self.iceContext.oooDefaultExt
        # filter out only file with the fromExt
        files = [file for file in files if self.__fs.splitExt(file)[1] in fromExt]
        
        for file in files:
            #print "converting selected %s files to %s" % (fromExt, toExt)
            file = self.__directory + file
            data = self.__rep.getItem(file).read()
            if self.__convertFileToExt(file, toExt)==True:
                try:
                    name, ext = self.__fs.splitExt(file)
                    renameTo = name + toExt
                    fileItem = self.__rep.getItem(file)
                    fileItem.move(self.__rep.getItem(renameTo))
                except Exception, e:
                    msg = "Failed to rename file from '%s' to '%s'" % (file, renameTo)
                    self.__resultError += msg + "\n"
                    self.__rep.getItem(file).write(data)    # Restore the file data
            else:
                self.__rep.getItem(file).write(data)    # Restore the file data
                self.__resultDetails += "Failed to convert '%s'\n" % self.__fs.split(file)[1]
        
        if self.__resultError=="":
            self.__resultSummary += "Converted all selected files OK"
        else:
            self.__resultSummary += "Error in converting files"
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __convertFileToExt(self, file, toExt):
        file = self.__rep.getAbsPath(file)
        toFile = file + ".tmp"
        tf, data = self.iceContext.getOooConverter().convertDocumentTo(\
                        absFilePath=file, toAbsFilePath=toFile, toExt=toExt)
        if tf==False:
            self.__resultError += data + "\n"
        self.__fs.copy(toFile, file)
        self.__fs.delete(toFile)
        return tf
    

    def __paste(self, actData):
        saveFor = self.__state.savedFor
        files = self.__state.savedFiles
        #print "would have %s pasted '%s'" % (saveFor, str(files))
        #return
        print "__paste(actData='%s')" % actData
        if actData=="":
            # then destination is the current path
            destPath = self.__directory
        else:
            destPath = self.__directory + actData
        if saveFor=="copy":
            self.__copyFiles(files, destPath)
        elif saveFor=="cut":
            # copy first and then delete
            self.__copyFiles(files, destPath)
            self.__delete(files)
        if self.__resultError=="":
            self.__resultSummary = "Pasted %s file(s)" % len(files)
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __copyFiles(self, files, dest):
        print "** copy", files, dest
        sourceRep = self.__state.sourceRep
        if sourceRep is None:
            sourceRep = self.__rep
        #if sourceRep != self.__re
        for file in files:
            try:
                destName = dest
                if self.__rep.getItem(dest).isDir: 
                    dName = self.__fs.split(file)[1]
                    destName = self.iceContext.url_join(dest, dName)
                    count = 1
                    while self.__fs.exists(self.__rep.getAbsPath(destName)):
                        destName = self.__getCopyOfName(self.iceContext.url_join(dest, dName), count)
                        count += 1
                destItem = self.__rep.getItem(destName)
                fileItem = sourceRep.getItem(file)
                if fileItem.exists:
                    if sourceRep==self.__rep and fileItem.exists:
                        try:
                            fileItem.copy(destItem)
                        except Exception, e:
                            self.__exportFile(sourceRep, file, destName)
                    else:
                        self.__exportFile(sourceRep, file, destName)
                else:
                    self.__fs.copy(file, destItem._absPath)
                self.__resultDetails += "Copied '%s' to '%s'\n " % (file, destName.replace("./", ""))
            except Exception, e:
                msg = "Error copying file '%s'" % file
                self.__resultDetails += msg + "\n"
                if self.__resultSummary=="":
                    self.__resultSummary = msg
                else:
                    self.__resultSummary = "Error copying files!"
                self.__resultError += "Error copying file '%s' - error message: %s\n" % (file, str(e))
        if self.__resultError=="":
            self.__resultSummary = "Copied file(s) OK"
    
    
    def __exportFile(self, sourceRep, file, destName):
        destItem = self.__rep.getItem(destName)
        fileAbsPath = sourceRep.getAbsPath(file)
        if not self.__fs.exists(fileAbsPath):
            fileAbsPath = self.__fs.absPath(file)
        destAbsPath = self.__rep.getAbsPath(destName)
        sourceItem = sourceRep.getItem(file)
        sourceItem.export(destAbsPath)
        destItem.add()
    
    
    def __getCopyOfName(self, path, count):
        path, name = self.__fs.split(path)
        name, ext = self.__fs.splitExt(name)
        if not name.startswith("copy_of_"):
            name = "copy_of_" + name
        if count>1:
            name += "(%s)" % count
        return self.iceContext.url_join(path, name + ext)
    
    
    def __renameTo(self, file, renameTo):
        print "__renameTo(file='%s', renameTo='%s')" % (file, renameTo)
        renameTo = renameTo.strip()
        if file is None or renameTo=="":
            return
        file = self.__directory + file
        # check if renameTo is OK to use
        result, reason = self.__isFilenameOK(renameTo)
        if result==False:
            self.resultSummary = "Cannot rename to '%s'.  %s" % (renameTo, reason)            
            self.__ajaxData = self.resultSummary
            return
        try:
            renameTo = self.__directory + renameTo
            #print "adding directory __renameTo(file='%s', renameTo='%s')" % (file, renameTo)
            fileItem = self.__rep.getItem(file)
            fileItem.move(self.__rep.getItem(renameTo))
            self.__resultDetails += "Renamed '%s' to '%s'" % (file, renameTo)
        except Exception, e:
            msg = "Error trying to rename '%s' to '%s' - %s" % (file, renameTo, str(e))
            print msg
            print self.iceContext.formattedTraceback()
            self.__resultError += "Error renaming '%s' to '%s' - error message: %s\n" % (file, renameTo, str(e))
            self.__resultSummary += "Failed to rename '%s' to '%s'" % (file, renameTo)
    
    def __log(self, file):
        if file is None:
            return
        file = self.__directory + file
        
        try:
            item = self.__rep.getItem(file)
            logs = item.getLogData(levels=3)
            logData = ""
            for log in logs:
                h, m = str(log).split(", Message: ", 1)
                h = self.iceContext.textToHtml(h)
                m = self.iceContext.textToHtml(m).replace("&#160;", " ")
                logData += "<div><span>%s</span><div> Message: %s</div></div>" % (h, m)
                
        except Exception, e:
            msg = str(e)
            if msg.startswith("File not found"):
                logData = "No log data found."
            else:
                logData = "Error: getting log data - " + msg
        self.__ajaxData = "<div class='log-data'>%s</div>" % logData
    
    
    def __edit(self, file):
        # check for browser refresh reposting
        print "__edit(%s)" % file
        sessionPostCount = self.__session.get("postCount", 0)
        postCount = self.__postCount
        self.__session["postCount"] = postCount
        if sessionPostCount==postCount:
            print "sessionPostCount=%s, postCount=%s" % (sessionPostCount, postCount)
            return
        if file=="manifest.xml":
            # redirect to edit_manifest
            redirectUrl = self.__fs.join(self.iceContext.urlRoot, 
                                        self.__directory.strip("/"), "edit_manifest")
            self.__ajaxData = "redirectUrl=%s" % redirectUrl
            return
        file = self.__directory + file
        absFilePath = self.__rep.getAbsPath(file)
        appsExts = {}
        if self.iceContext.system.isLinux:
            oooPath = self.iceContext.settings.get("oooPath")
            soffice = "soffice"
            if oooPath!="":
                soffice = self.iceContext.url_join(oooPath, "program", soffice)
            appsExts = {soffice:[self.iceContext.oooDefaultExt, self.iceContext.wordExt, \
                                self.iceContext.oooMasterDocExt, self.iceContext.bookExts, \
                                self.iceContext.odsExt, self.iceContext.odpExt, \
                                self.iceContext.xlsExt, self.iceContext.pptExt, \
                                self.iceContext.word2007Ext, self.iceContext.wordDotExt]}
        self.iceContext.system.startFile(absFilePath, appsExts=appsExts)
    
    
    def __download(self, file, name):       # download file to the client
        data = self.__rep.getItem(self.__directory + file).read()
        self.downloadFile = name
        self.downloadData = data
    
    
    def __editBook(self, file):
        # check for browser refresh reposting
        sessionPostCount = self.__session.get("postCount", 0)
        postCount = self.__postCount
        self.__session["postCount"] = postCount
        if sessionPostCount==postCount:
            print " sessionPostCount=%s, postCount=%s" % (sessionPostCount, postCount)
            return
        self.__editBookFile = self.__directory + file
    
    
    def __repair(self, files, repairTemplateFile):
        #raise Exception("Repair code needs updating!")
        if repairTemplateFile=="selected":
            repairTemplateFile = self.__directory + self.__selected[0]
        for file in files:
            item = self.__rep.getItem(self.__directory + file)
            try:
                if self.__repairFile(item, repairTemplateFile):
                    self.__resultDetails += "Repaired '%s' \n" % item.relPath
            except Exception, e:
                msg = str(e)
                print "Error repairing files - ", msg
                if self.__resultSummary=="":
                    self.__resultSummary += "Error repairing '%s'" % item.relPath
                else:
                    self.__resultSummary += "Error repairing files"
                self.__resultError += "Error repairing '%s' - error message: %s. \n" % (item.relPath, msg)
        if self.__resultError=="":
            self.__resultSummary += "Repaired selected items"
        self.__selected = []
        self.__state.clearSaveFor()
    
    
    def __repairFile(self, item, repairTemplateFile):
#        raise Exception("Repair code needs updating!")
        if item.isDir:
            result = True
            for listItems in item.walk(filesOnly=True):
                for i in listItems:
                    if i.name.endswith(self.iceContext.oooDefaultExt):
                        if self.__repairFile(i, repairTemplateFile)==False:
                            result = False
            return result
        if item.name.endswith(self.iceContext.oooDefaultExt):
            print "Repairing file - ", item.relPath
            ooRepair = self.iceContext.getPlugin("ice.ooo.repair").pluginClass(self.iceContext)
            ooRepair.repair(item)
             
            if repairTemplateFile is not None:
                rt = ooRepair.RepairTemplate(self.iceContext, repairTemplateFile)
                ok, results = rt.repairFiles([item.relPath])
                if ok==False:
                    errMsg = results[0][1]
                    print errMsg
                    return False
            return True
        else:
            return False
    
    
    def __test(self):
        path = self.__directory
        print "__test() path=", path
        print "---"
        self.__isFilenameOK("", path)
    
    def __isFilenameOK(self, filename, path=None):
        # checks to see if the given filename is valid and does not already exist in the given directory (ignoring the file extension)
        # return (True, "") or (False, reasonMessage)
        if path==None:
            path = self.__directory
        # ignore case
        filename = filename.lower()
        # is not longer than 32 characters
        if len(filename)>32:
            return False, "too long"
        # is not a hidden/ignore name/extension
        if self.__rep.inIgnoreLists(filename):
            return False, "invalid name"
        # does not already exist (ignoring the file extension)
        item = self.__rep.getItem(path)
        fileAndDirNames = [i.name.lower() for i in item.listItems()]   
        if filename in fileAndDirNames:
            return False, "a file or directory with this name already exists"
        if filename.startswith("."):
            return False, "cannot start with a '.'"
        filename = self.__fs.splitExt(filename)[0]
        if filename=="":
            return False, ""
        for file in fileAndDirNames:
            if self.__fs.splitExt(file)[0] == filename:
                return False, "already exists"
        # does not contain invalid characters
        if re.search("[^\&a-z 0-9_\\.-]", filename):
            return False, "invalid character(s)"
        # else it must be OK
        return True, ""
    
    
    def __uploadFile(self):
        self.__resultSummary = ""
        self.__resultDetails = ""
        self.__resultError = ""
        for filename, fileData in self.__uploadedFilenameDatas:
            uploadFilename = filename
            match = re.search("(.*?)_i([0-9a-fA-F]+)r(\-?\d+)(-[0-9]+)?(\s?\(.*?\))?(\..*)", filename)
            serverData = self.__rep.serverData
            if (match is not None) and (serverData is not None):
                name, pathId, revNum, ignore1, ignore2, ext = match.groups()
                filename = name + ext.lower()
                pathId = string.atoi(pathId, 16)
                revNum = string.atoi(revNum)
                path = serverData.getRelPathForId(pathId)
                if path is None:
                    msg = "Error: unknown pathId or wrong repository!"
                    print msg
                    self.__resultError = "Some problems encountered uploading file(s). Please see details below."
                    self.__resultDetails += "Error: uploading '%s' - unknown pathId\n" % uploadFilename
                else:
                    relPath = self.__fs.join(path, filename)
                    item = self.__rep.getItem(relPath)
                    if item.lastChangedRevisionNumber > revNum:
                        msg = "Uploaded file '%s' is out of date!" % filename
                        print msg
                        self.__resultDetails += msg + "\n"
                        self.__resultError = "Some problems encountered uploading file(s). Please see details below."
                    else:
                        ##
                        item.write(fileData)
                        self.__resultDetails += "Uploaded file '%s' as '%s' OK.\n" % (uploadFilename, filename)
                        if item.hasHtml:
                            # redirect
                            redirectUrl = self.__fs.join(self.iceContext.urlRoot, item.relPath[:-len(item.ext)] + ".htm")
                            print "redirectUrl = '%s'" % redirectUrl
                            raise self.iceContext.RedirectException(redirectUrl=redirectUrl)
            else:
                path = self.__directory
                if filename!="":
                    resultDetail = ""
                    name, ext = self.__fs.splitExt(filename)
                    filename = "%s%s" % (name, ext.lower())
                    ok, reason = self.__isFilenameOK(filename)
                    if reason.find("already exists") > -1:
                        ok = True
                    if reason.find("too long") > -1:
                        file, ext = self.__fs.splitExt(filename)
                        filename = file[:28].strip() + ext
                        resultDetail = ". Filename is being truncated to: '%s'" % filename
                        ok = True
                    if reason.find("invalid character(s)") > -1:
                        filename = "UploadedFile" + self.__fs.splitExt(filename)[1]
                        ok = True
                    fullpath = self.iceContext.url_join(path, filename)
                    name, ext = self.__fs.splitExt(filename)
                    count = 2
                    if not self.iceContext.isServer:
                        while self.__fs.exists(self.__rep.getAbsPath(fullpath)):
                            fullpath = self.iceContext.url_join(path, "%s(%s)%s" % (name, count, ext))
                            count += 1
                    if ok:
                        self.__rep.getItem(fullpath).write(fileData)
                        self.__resultDetails += "Uploaded file '%s' OK%s\n" % (filename, resultDetail)
                        
                    else:
                        self.__resultError = "Some problems encountered uploading file(s). Please see details below."
                        self.__resultSummary = "Failed to create file '%s' reason: %s\n" % (filename, reason)
        if self.__resultSummary=="":
            if self.__resultError=="":
                self.__resultSummary = "Uploaded file(s) OK"
            else:
                self.__resultSummary = self.__resultError
    
    
    def __svnCleanup(self):
        relPath = self.__directory
        item = self.__rep.getItem(relPath)
        item.cleanup()
    
    
    def __getDriveList(self):
        l = []
        for drive in [chr(i)+":/" for i in range(65+2, 65+26)]:
            if self.__fs.exists(drive):
                l.append(self.__fs.abspath(drive))
        return l
    
    
    def __unzip(self, item):
        pItem = item.parentItem
        zipList = item.zipList()
        zipList = [self.__fs.normPath(i) for i in zipList]
        zipList = [i for i in zipList if i[0] not in [".", "/", "\\"]]
        print "UnZipping '%s'" % item.relPath
        for filename in zipList:
            data = item.extractFromZip(filename)
            if data is not None:
                cItem = pItem.getChildItem(filename)
                print "  unzipping to '%s'" % cItem.relPath
                cItem.write(data)
        print " finished unzipping"



class _State:
    def __init__(self):
        #print "*** _State.__init__()"
        self.__idCount = 0
        self.__savedFiles = []
        self.__sourceRep = None
        self.__savedFor = ""        # 'copy' or 'cut' (move)
    
    @property
    def savedFor(self):
        return self.__savedFor
    
    @property
    def savedFiles(self):
        return self.__savedFiles
    
    @property
    def sourceRep(self):
        return self.__sourceRep
    
    def saveForCopy(self, selectedFiles, directory, sourceRep):
        self.clearSaveFor()
        self.__saveSelectedFiles(selectedFiles, directory, sourceRep)
        self.__savedFor = "copy"
    
    def saveForCut(self, selectedFiles, directory, sourceRep):
        self.clearSaveFor()
        self.__saveSelectedFiles(selectedFiles, directory, sourceRep)
        self.__savedFor = "cut"
    
    def clearSaveFor(self):
        self.__savedFiles = []
        self.__sourceRep = None
        self.__savedFor = ""
    
    def __saveSelectedFiles(self, selectedFiles, directory, sourceRep):
        self.__savedFiles = []
        self.__sourceRep = sourceRep
        for filename in selectedFiles:
            if filename is not None:
                self.__savedFiles.append(directory + filename)



def getState(str):
    """ decode and recreate the state object """
    str = base64.decodestring(str)
    return loads(str)
    
def objectToEncodedStr(obj):
    """ serialize and encode the given object (state) """
    str = dumps(obj)
    str = base64.encodestring(str)
    return str
    
    
class _Entry(object):
    """ class to represent a single file or directory entry """
    def __init__(self, iceContext, name, id=None, level=1):
        self.iceContext = iceContext
        if id is None:
            id = "fId_" + name
        self.level = level
        self.isDir = False
        self.filename = name
        self.__name = name
        self.__id = id
        self.canRevert = True
        self.lastModified = "?"
        self.selected = False
        self.__link = None
        self.viewAs = None    # e.g. "html" , "pdf", or "manifest"
        self.endNoteselected = False
        self.renderAudioSelected = False
        self.glossarySelected = False
        self.glossaryTermsSelected = False
        self.iceContent = False
        self.isIceDisplayable = False
        self.x = False
        self.name = self.iceContext.escapeXmlAttribute(self.__name)
        self.id = self.iceContext.escapeXmlAttribute(self.__id)
        self.__xmlSafeLink = None
        self.linkAsEndnoteOption = False
        self.renderAudioOption = False
        self.displaySourceTypeOption = False
        self.displaySourceType = False
        self.glossaryOption = False
        self.tocLevels = False
        
        self.isBook = False
        self.isOdt = False
        self.isDoc = False
        ext = self.iceContext.iceSplitExt(self.__name)[1]
        if ext in self.iceContext.bookExts:
            self.isBook = True
        if ext==self.iceContext.oooDefaultExt:
            self.isOdt = True
        if ext==self.iceContext.wordExt or ext==self.iceContext.word2007Ext:
            self.isDoc = True
        self.extraOptions = []
    
    def __getLink(self):
        return self.__xmlSafeLink
    def __setLink(self, value):
        self.__link = value
        self.__xmlSafeLink = self.iceContext.escapeXmlAttribute(value)
    link = property(__getLink, __setLink)
    
    
    def setLastModified(self, t):
        ts = time.localtime(t)
        self.lastModified = str(ts[0]) + "-" + str(ts[1]).rjust(2, "0") + "-" + str(ts[2]).rjust(2, "0")
        
    def hasSubEntries(self):
        return len(self.subEntries)>0
    
    def getImageSrc(self):
        if self.isDir:
            if self.hasSubEntries():
                return "/skin/FolderOpen.gif"
            else:
                return "/skin/FolderClosed.gif"
        else:
            return "/skin/File.gif"
        
    def getImageAlt(self):
        if self.isDir:
            return "Folder"
        else:
            return "File"

    def getImageTitle(self):
        if self.isDir:
            return ""
        else:
            return "Click to view as HTML"

    def __cmp__(self, other):
        return cmp(self.__getCmpName(), other.__getCmpName())
        
    def __getCmpName(self):
        if self.isDir:
            return "D" + self.name
        else:
            return "F" + self.name












