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


import types
import string
import re



class IceSite(object):
    HtmlTemplate = None     #iceContext.HtmlTemplate
    _defaultXhtmlTemplateFilename = "template.xhtml"
    
    #
    # Notes:
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   iceContext
    #   defaultXhtmlTemplateFilename                    # ReadOnly
    #   rep                                             # ReadOnly
    #   session
    #   path
    #   packagePath
    #   
    #
    # Methods:
    #   clone()
    #   
    #   serve()
    #     __serve()
    #       __serveIceContent(path)
    
    def __init__(self, iceContext, *args, **kwargs):
        #print "IceSite.__init__()"
        self.iceContext = iceContext
        if self.HtmlTemplate is None:
            self.HtmlTemplate = iceContext.HtmlTemplate
        self.logger = iceContext.logger
        
        self._isTocPage = False
        self._isDefaultPage = False
        self._defaultPageEquals = None        # path/item.htm, BUT not if there is a SPLASH Page.
        self.includeSource = False
        self.exportVersion = False
        self.noContextLink = False
        self.addNbspToEmptyTableCells = True #Set to true to better represent the word processor behaviour
        
        self.fs = iceContext.fs
        self.__rep = iceContext.rep
        if self.__rep.iceContext.iceSite is None:
            self.__rep.iceContext.iceSite = self
        
        self.preRenderCallback = None
        self.__mf = None
        self.__manifest = None
        self.isFileView = False
        self.isDocContentView = not self.isFileView
        self.__session = iceContext.session
        if self.__session is None:
            username = ""
        else:
            username = self.__session.username
        if username=="":
            username="Anonymous"
        self.username = username
        self.item = None
        self.displayItem = None         # Normal equals self.item (but for home page etc)
        self.formData = None
        self.fileManager = None
        self.packageItem = None
        self.__message = ""
        self.__directory = ""
        self.__title = None
        self.__body = None
        self.__templateDict = {}
        self["username"] = username
        self["appStyleCss"] = ""
        self["javascript-files"] = []
        self["javascripts"] = []
    
    
    @property
    def defaultXhtmlTemplateFilename(self):
        return self._defaultXhtmlTemplateFilename
    
    @property 
    def isDocView(self):
        r = not self.isFileView and self.isDocContentView and not self._isTocPage
        if r and self.path.endswith("/editManifest"):
            r = False
        return r 
    
    @property
    def rep(self):
        return self.__rep
    
    
    def getImsManifest(self, packageItem=None):
        # from a manifest.xml fileItem
        def getImsManifestFromFileItem(mfItem, includeSource=False, forceCreate=False):
            imsManifest = None
            plugin = self.iceContext.getPlugin("ice.ims.manifest")
            imsManifest = plugin.pluginClass.getManifest(self.iceContext, \
                            mfItem, includeSource, forceCreate)
            return imsManifest
        #
        if packageItem is None:
            if self.__mf is not None:
                return self.__mf
            packageItem = self.packageItem
        if packageItem is None:
            print "self.packageItem is '%s'" % self.packageItem
            print "  '%s'" % self.packagePath
            return None
        #print "getImsManifest() packageItem='%s'" % packageItem
        #if True:   ## Regenerate the manifest object again!
        #    packageItem.setMeta("manifest", None)
        #    packageItem.flush()
        manifest = packageItem.getMeta("manifest")
        if manifest is None:
            # OK try and find the old manifest.xml item
            imsMfItem = packageItem.getChildItem("manifest.xml")
            if imsMfItem.exists==False or imsMfItem.isMissing:
                raise Exception("No ims manifest.xml file found!")
            self.__mf, created = getImsManifestFromFileItem(imsMfItem, 
                    includeSource=False, forceCreate=False)
            if self.__mf is None:
                raise Exception("No ims manifest found!")
            else:
                # ok now create an (ice) manifest object from the IMS manifest
                manifest = self.iceContext.getPlugin("ice.manifest").pluginClass(self.iceContext)
                manifest.updateItems(packageItem)
                manifest.title = self.__mf.title
                # create structure
                org = self.__mf.defaultOrganization
                count = 0
                mItems = manifest.allManifestItems
                allItems = dict(zip([i.renditionName for i in mItems], mItems))
                m = allItems.get("manifest.xml")
                if m is not None:
                    m.manifestTitle = "IMS Manifest"
                    m.isHidden = True
                def x(item, count):
                    for i in item.items:
                        count += 1
                        href = i.href
                        if href.endswith(".book.pdf"):
                            href = href[:-len(".book.pdf")] + ".pdf"
                        if href not in allItems.keys():
                            if href not in ["toc.htm", "default.htm"]:
                                print "  %s '%s' not found in allItems" % (count, href)
                        else:
                            pHref = i.parentItem.href
                            if pHref is not None:
                                if pHref.endswith(".book.pdf"):
                                    pHref = pHref[:-len(".book.pdf")] + ".pdf"
                                pmi = allItems[pHref]
                                pguid = pmi.itemGuid
                            else:
                                pguid = None
                            mi = allItems[href]
                            mguid = mi.itemGuid
                            manifest.moveItem(mguid, pguid)
                            mi.isHidden = not i.isVisible
                            mi.manifestTitle = i.title
                            count = x(i, count)
                    return count
                count = x(org, count)
                print "+++ getImsManifest() setting self.__manifest"
                self.__manifest = manifest
                if False:
                    print count
                    print manifest
                    print "---"
                    def imsDisplay(item, d=0):
                        c = 0
                        for i in item.items:
                            c += 1
                            print "  " * d + str(c) + "    " + i.href
                            imsDisplay(i, d+1)
                    def mDisplay(mItem, d=0):
                        c = 0
                        for i in mItem.children:
                            c += 1
                            print "  " * d + str(c) + "    " + i.renditionName
                            mDisplay(i, d+1)
                    imsDisplay(org)
                    print "===="
                    mDisplay(manifest)
        else:
            plugin = self.iceContext.getPlugin("ice.ims.manifest")
            self.__mf = plugin.pluginClass.createImsManifest(
                            self.iceContext, packageItem, manifest, 
                            includeSource=False, includeSkin=True)
        return self.__mf
    
    
    @property
    def manifest(self):
        if self.__manifest is not None:
            return self.__manifest
        if self.packageItem is None:
            return None
        self.__manifest = self.packageItem.getMeta("manifest")
        if self.__manifest is None:
            #print "meta 'manifest' is None!"
            imsMfItem = self.packageItem.getChildItem("manifest.xml")
            if imsMfItem.exists and imsMfItem.isMissing==False:
                #print "created new manifest from old IMS manifest.xml file"
                imsManifest = self.getImsManifest()
                # remove the old manifest.xml file
                imsMfItem.delete()
            else:
                # Create a new manifest object
                #print "*** creating a new manifest object!"
                manifest = self.iceContext.getPlugin("ice.manifest").pluginClass(self.iceContext)
                manifest.updateItems(self.packageItem)
                self.__manifest = manifest
            if self.__manifest is None:
                raise Exception("manifest is None but in a package!")
            # Save newly created manifest
            self.packageItem.setMeta("manifest", self.__manifest)
            self.packageItem.flush()
        return self.__manifest
    
    
    def updateManifest(self):
        self.__mf = None
        manifest = self.manifest
        if manifest is not None:
            manifest.updateItems(self.packageItem)
            self.packageItem.setMeta("manifest", manifest)
            self.packageItem.flush(True)
        return manifest
    
    
    @property
    def manifestTitle(self):
        title = None
        manifest = self.manifest
        if manifest is not None:
            title = manifest.manifestTitle
        return title
    
    
    def __getSession(self):
        return self.__session
    def __setSession(self, value):
        self.__session = value
    session = property(__getSession, __setSession)

    
    @property
    def uri(self):
        return self.item.uri
    # The following path property is to be refactored out
    @property
    def path(self):
        return self.item.uri.rstrip("/")
    
    @property
    def packagePath(self):
        if self.packageItem is None:
            return ""
        else:
            return self.packageItem.relPath
    def __setPackagePath(self, packagePath):
        if packagePath is None or packagePath=="":
            self.packageItem = None
            packagePath = ""
        else:
            pPItem = self.rep.getItem(packagePath)
            if not pPItem.isDirectory:
                pPItem = None
            self.packageItem = pPItem
        self.__templateDict["package-path"] = packagePath
    
    @property
    def isInPackage(self):
        return self.packageItem is not None
    
    
    #@property
    def __getDirectory(self):
        return self.__directory
    def __setDirectory(self, value):
        self.__directory = value
        self["directory"] = value
    directory = property(__getDirectory, __setDirectory)
    
    
    #@property
    def __getTitle(self):
        return self.__title
    def __setTitle(self, value):
        self.__title = value
        self["title"] = value
    title = property(__getTitle, __setTitle)
    
    
    #@property
    def __getBody(self):
        return self.__body
    def __setBody(self, value):
        self.__body = value
        self["body"] = value
    body = property(__getBody, __setBody)
    
    
    def __getitem__(self, name):
        return self.__templateDict.get(name, "")
    
    def get(self, name, default=None):
        return self.__templateDict.get(name, default)
    
    
    def __setitem__(self, name, value):
        if name=="body":
            self.__body = value
        elif name=="title":
            self.__title = value
            if value is None:
                value = ""
        self.__templateDict[name] = value
    
    
    def clone(self):
        # Note: does not keep username, workingOffline state
        klass = self.__class__
        try:
            c = klass(self.iceContext)
            c.item = self.item
            c.__setPackagePath(self.packagePath)
        except:
            raise Exception("Failed to clone self (ice_site)!")
        return c
    
    
    # public - Main method -
    def serve(self, item, formData=None, session=None, test=False):
        """ returns a tuple (data, mimeType, downloadFilename) """
        self.__test = test                  # For testing (only)
        if item is None:
            raise Exception("item is None!")
        self.item = item
        self.displayItem = self.item        # default
        if formData is None:
            formData = self.iceContext.requestData
        self.formData = formData
        if session is None:
            session = self.iceContext.session
        self.session = session
        self.__manifest = None

        if self.formData.value("search") is not None:
            self.formData.setValue("func", "search")
        if self.formData.value("exportVersion", "")!="":
            # Note: can only set (can not reset) via formData
            self.exportVersion = True
        if self.formData.value("exportVersion", "")=="noContextLink":
            self.noContextLink = True
        startTime = self.iceContext.now()
        #
        try:
            r = self.__serveIceContent()                    # ==========
        except self.iceContext.RedirectException, e:
            raise e
        except Exception, e:
            msg="Unexpected error in ice_site.serve()"
            self.logger.exception(msg)
            html = self.iceContext.getHtmlFormattedErrorMessage(e, msg=msg)
            r = [html, "text/html", None]
        #
        mimeType = r[1]
        if mimeType=="text/html":    # Only time request for non-binary content
            totalTime = str(round(self.iceContext.now()-startTime,4))
            self.iceContext.gTime.isHtmlPage = True
            #print "Done %s\n" % totalTime
        return r
    
    
    def __serveIceContent(self):
        """ returns a tuple (data, mimeType, downloadFilename) """
        # For only serving ice rendered dat
        htmlMimeType = "text/html"
        
        self.__setup()
        # Run the mapPath() to test
        contentDict = self.__templateDict
        nodeMapper = self.iceContext.NodeMapper(self.item.uri, contentDict)
        title, packagePath = self.mapPath(nodeMapper)
        self.title = title
        self.__setPackagePath(packagePath)
        
        if self.isInPackage:    #  Load the IMS manifest
            self.manifest           # check that there is a manifest
            if self.title is None:
                self.title = self.manifestTitle
            self["coursetitle"] = self.iceContext.textToHtml(self.manifestTitle, includeSpaces=False)
            self["packagetitle"] = self.iceContext.textToHtml(self.manifestTitle, includeSpaces=False)
        
        ##
        try:
            defaultFunctionName = None
            if self.item.isDirectory:
                defaultFunctionName = "default.htm"
            # Note: can change the title, self.body etc
            r = self.__executeFunction(defaultFunctionName=defaultFunctionName)
            if type(r) is types.TupleType:
                return r
        except self.iceContext.RedirectException, e:
            raise e
        except self.iceContext.AjaxException, e:
            return (e.data, htmlMimeType, None)
        except Exception, e:
            self.logger.exception("Ice site severIceContent __executeFunction() Exception")
            html = self.iceContext.getHtmlFormattedErrorMessage(e, msg="Error in icesite.__executeFunction()")
            return (html, htmlMimeType, None)
        ##
        
        if self.body is None:
            # Assert
            if self.item.isFile and self.item.hasHtml==False:
                if self.item.ext == ".book.odt":
                    #raise self.iceContext.IceException("This book does not have any html rendition")
                    h = "<div>This book does not have a HTML rendition. Please try the <a href='%s'>PDF version.</a></div>"
                    pdfName = self.item.name[:-len(self.item.ext)] + ".pdf"
                    self.body = h % (self.item.relDirectoryPath + pdfName)
                else:
                    raise self.iceContext.IceException("FileItem as no html rendition, so it must be a binary item!")
            else:
                # Get the items contents
                self.__getFileHtmlRendition()
        
        try:
            # Create Toolbar
            if not self.exportVersion:
                self.__createToolbar()
            if self.isInPackage:
                # left-hand context TOC
                self["context-toc"] = self.__getContextToc()
                self["nav-buttons"] = self.__getNavButtons(self._isTocPage)
            # Render
            # preRender
            if callable(self.preRenderCallback):
                self.preRenderCallback(self)
            self.preRender()
            # render
            xhtmlTemplateFilename = self.session.get("xhtmlTemplateFilename", self.defaultXhtmlTemplateFilename)
            html = self.render(self.iceContext, xhtmlTemplateFilename)
            # postRender
            html = self.postRender(html)
            #x = self.iceContext.now()
            #print "rendered in %smS" % int((self.iceContext.now()-x)*1000)
        except Exception, e:
            self.logger.exception("Error in ice_site.render()")
            html = self.iceContext.getHtmlFormattedErrorMessage(e, msg="Error in ice_site.render()")
        return (html, htmlMimeType, None)
    
    
    #===================================
    # Private
    
    
    def __setup(self):
        self.__mf = None
        self.title = None
        self.body = None
        self["css"] = "<link rel='stylesheet' href='skin/css.txt'/>"
        self["statusbar"] = "--- Status bar ---"
        
        # Reset
        self["style-css"] = ""
        self["toolbar"] = ""
        self["context-toc"] = ""        # Left-hand TOC
        self["page-toc"] = ""
        self["nav-buttons"] = "<!-- -->"
        self["argPath"] = ""
        
        self._isTocPage = False
        self._isDefaultPage = False
        self._defaultPageEquals = None
        self.directory = self.item.relDirectoryPath
    
    
    def __getFileHtmlRendition(self):
        if self.item.isFile and self.item.hasHtml:
            # Get the items contents
            embed = self.formData.has_key('embed')      # whether the contents should be embedded in ice html
            html = ""
            title = ""
            page_toc = ""
            body_style = ""
            try:
                html, title, page_toc, body_style = self.item.getHtmlRendition(embed=embed)
            except Exception,e:
                msg = "Error in getting HTML Rendition - '%s'" % str(e)
                print msg
                #raise(e)
                html = self.iceContext.textToHtml(msg)
                html = "<div>%s</div>" % html
                title = "Error"
                page_toc = ""
                body_style = ""
            if self.body is None and html != "":
                self.body = html
            if title is not None:
                self.title = title
            self["page-toc"] = page_toc
            self["style-css"] = body_style
            if self.item.ext in self.iceContext.bookExts and self.manifest is not None:
                # if it is a book then we always use the manifest item's title
                mItem = self.manifest.getManifestItem(self.item.guid)
                if mItem is not None:
                    self.title = mItem.title
        if self.body is None:
            # should only get in here for invalid paths
            msg = "***  body content not set? item.relPath='%s' uri='%s'"
            msg = msg % (self.item.relPath, self.item.uri)
            self.iceContext.writeln(msg)
            self.__message = "%s - NOT FOUND!" % self.item.uri
            #print "  item.relPath='%s' isFile=%s" % (self.item.relPath, self.item.isFile)
            self.__executeFunction("default.htm")
            if self.body is None:   # if still none
                self.body = "<div>-- NONE --</div>"
    
    
    def __executeFunction(self, funcName=None, defaultFunctionName=None):
        """ returns a tuple (data, mimeType, downloadFilename) 
            or returns False or (the result of the function)
        """
        if funcName is None:
            funcName = self.__getFunctionName()
            if funcName is None:
                funcName = defaultFunctionName
        if funcName is None:
            return False
        if self.iceContext.iceFunctions.allFunctions.has_key(funcName):
            func = self.iceContext.iceFunctions.allFunctions[funcName]
            if func.postRequired and self.formData.method!="POST":
                self.body = "A POST is required!"
                self["statusbar"] = "A POST is required!"
                return False
            else:
                if funcName == "changeRepository":
                    #For changing of repository, set back the template to default
                    self.session["xhtmlTemplateFilename"] = "template.xhtml"
                r = func._execute(self)
                # e.g. changeRepository function still needs to call the "default.htm" or "toc.htm" function
                if r is None and (self.body is None or self.body==""):
                    if self.formData.has_key("func"):
                        self.formData.remove("func")
                        r = self.__executeFunction(defaultFunctionName=defaultFunctionName)
                        return r
                return r
        elif funcName=="default.htm":
            return self.__default_htm_function()
        elif funcName=="toc.htm":
            return self._toc_htm_function()
        elif funcName=="file_manager" or funcName=="fileManager":
            #self._isDefaultPage = True
            return self.__fileManager_function()
        elif funcName=="_test":
            print "_test"
            data = "<html>_test  TESTING</html>"
            return (data, "text/html", None)
        elif funcName=="_getList":
            data = "_getList\n"
            arg = (self.item.uriDiff+"/").split("/")[1]
            for i in self.item.listItems():
                if i.isDirectory:
                    data += i.name + "/\n"
                else:
                    data += i.name + "\n"
            return (data, "text/plain", None)
        elif funcName=="_getLists":
            print "_getLists"
            def getLists(item):
                d = {}
                for i in item.listItems():
                    d[i.name] = None
                    if i.isDirectory:
                        d[i.name] = getLists(i)
                return d
            def formatD(d, level=0):
                data = ""
                for k, v in d.iteritems():
                    data += "  "* level + k + "\n"
                    if v is not None:
                        data += formatD(v, level+1)
                return data
            arg = (self.item.uriDiff+"/").split("/")[1]
            d = getLists(self.item)
            if arg=="json":
                data = str(d)
                return (data, "application/json", None)
            else:
                data = "_getLists\n" + formatD(d)
                return (data, "text/plain", None)
        elif funcName=="_zipped":
            #responseData.setHeader("Content-Encoding", "gzip")
            if self.item.isFile:
                self.iceContext.responseData.setHeader("Content-Encoding", "gzip")
                data = self.iceContext.gzip(self.item.read(), self.item.name)
                return (data, "application/zip", None)
            else:
                data = "'%s' is not a valid file" % self.item.relPath
                return (data, "text/plain", None)
        else:
            pass
            #print "** funcName '%s' not found!" % funcName
            #print "  ** self.item='%s'" % self.item
        return False
    
    
    def __getFunctionName(self):
        """check for and get function name if it exists"""
        funcName = None
        if self.formData.has_key("func"):
            funcName = self.formData.value("func")
        else:
            funcName = self.item.uriDiff.split("/", 1)[0]
        if funcName is not None:
            funcName = funcName.replace("-", "_")
            if funcName=="":
                funcName = None
        return funcName
    
    
    def __default_htm_function(self):
        self._isDefaultPage = True
        
        if self.exportVersion:
            if self.isInPackage:
                return self.__default_htm()
            else:
                self._isTocPage = True
                return self.__dirNav_function()
        else:
            try:
                return self.__fileManager_function()
            except self.iceContext.AjaxException, e:
                raise e
    
    # default.htm
    def __default_htm(self):
        # In a package
        # may be toc (same as toc.htm) or defaultItem or a splash page
        content = None
        self.body = ""
        defaultItem = self.manifest.homePageItem
        #print
        #print "-- default.htm --"
        #print defaultItem
        if defaultItem is None:
            # may be a splash page!
            if self.packageItem.getMeta("manifest") is None:
                self.packageItem.setMeta("manifest", self.manifest)
            return self._toc_htm_function()
        else:
            #print "++ defaultItem = '%s'" % defaultItem
            #print " ++ self.item='%s'" % self.item
            #print " ++ self.manifest='%s' %s" % (self.manifest, self.manifest== defaultItem)
            homeItem = self.__rep.getItem(self.packagePath + defaultItem.relPath)
            embed = self.formData.has_key('embed')      # whether the contents should be embedded in ice html
            content, title, page_toc, body_style = homeItem.getHtmlRendition(embed=embed)
            if body_style is None:
                body_style = ""
            if content is not None:
                self.title = title
                self["page-toc"] = page_toc
                self["style-css"] = body_style
                self.displayItem = homeItem
                pathDiff = homeItem.relDirectoryPath[len(self.item.relDirectoryPath):]
                def changeUriMethod(uri):
                    if uri.find("://")!=-1 or uri.startswith("/"):  # absolute
                        return uri
                    return pathDiff + uri
                content = self.__changeLinks(content, changeUriMethod)
                self.body = content
            return
    
    
    def __changeLinks(self, content, changeUriMethod):
        try:
            xml = self.iceContext.Xml(content)
            linkNodes = xml.getNodes("//*[@href or @src]")
            for n in linkNodes:
                href = n.getAttribute("href")
                src = n.getAttribute("src")
                if href:
                    n.setAttribute("href", changeUriMethod(href))
                if src:
                    n.setAttribute("src", changeUriMethod(src))
            content = str(xml.getRootNode())
            xml.close()
        except Exception, e:
            xml.close()
            raise str(e)
        return content
    
    
    def __fixUpLinks(self, content, path):
        try:
            xml = self.iceContext.Xml(content)
            refNodes = xml.getNodes("//*[@href]")
            for ref in refNodes:
                url = ref.getAttribute("href")
                if url.find("//")<0:
                    url = self.iceContext.urlJoin(path, url)
                ref.setAttribute("href", url)
                
                if ref.getAttribute("onclick") is not None:
                    replaced = ref.getAttribute("onclick").replace(replaceStr, url)
                    ref.setAttribute("onclick", replaced)
                
            srcNodes = xml.getNodes("//*[@src]")
            for src in srcNodes:
                url = src.getAttribute("src")
                if url.find("//")<0:
                    url = self.iceContext.urlJoin(path, url)
                src.setAttribute("src", url)
                
            dataNodes = xml.getNodes("//object[@data]")
            for data in dataNodes:
                url = data.getAttribute("data")
                if url.find("//")<0:
                    url = self.iceContext.urlJoin(path, url)
                data.setAttribute("data", url)
            
            dataNodes = xml.getNodes("//object/param[@name='url' or @name='movie']")
            for data in dataNodes:
                url = data.getAttribute("value")
                if url.find("//")<0:
                    url = self.iceContext.urlJoin(path, url)
                data.setAttribute("value", url)
            content = str(xml)
            xml.close()
        except Exception, e:
            xml.close()
            raise str(e)
        return content
    
    
    # Protected
    def _toc_htm_function(self):         # called from plugin_check_links
        self._isTocPage = True
        if not self.isInPackage or self.packageItem.getMeta("manifest") is None:
            self._isDefaultPage = True
            return self.__dirNav_function()
## ORE - rdflib
#        # ORE - ignore if exporting
#        if not self.exportVersion:
#            OREResourceMap = self.iceContext.getPluginClass("ice.extra.ORE")
#            if OREResourceMap is not None:
#                rem = OREResourceMap(self.iceContext)
#                rdfPath = self.fs.splitExt(self.uri)[0] + ".rdf"
#                resMapUrl = rem.getBaseUri() + rdfPath
#                self["style-css"] += "<link rel='resourcemap' type='application/rdf+xml' href='%s'/>" % resMapUrl
#            else:
#                self.iceContext.output.writeln("Foresite toolkit required for ORE")
        #
        tocFunc = self.iceContext.getPlugin("ice.fullToc").pluginFunc
        self.title, self.body = tocFunc(self.iceContext, self.packageItem)
    
    
    # Directory navigation for exportVersion and when in a none-package-directory
    def __dirNav_function(self):
        excludeFiles = ["imscp_rootv1p1.dtd", "favicon.ico"]
        ## Not Found 
        ## make all links relative to item.uri (and not item.relPath as is currently)
        item = self.item
        if item.isDir:
            html = "<ul>"
            if item.relPath=="/":
                html += "<li class='app-parent-inactive'><span class='app-parent-inactive' "
                html +=   "title='Parent folder'><span>..</span></span></li>" 
            else:
                href = "../default.htm"
                html += "<li class='app-parent'><a href='%s' class='app-parent' " % href
                html +=   "title='Parent folder'><span>../</span></a></li>"
            for i in item.listItems():
                if i.name in excludeFiles:
                    continue
                if i.name.startswith("."):
                    continue
                if item.relPath=="/" and i.name in ["templates", "skin"]:
                    continue
                rawFile, ext = self.fs.splitExt(i.relPath)
                itemName = i.getMeta('title')
                if itemName is None:
                    itemName = i.name
                #else:
                #    itemName += " (" + i.name + ")"
                if ext == self.iceContext.oooDefaultExt:
                    ext = '.htm'
                    itemPath = rawFile + ext
                    i = self.rep.getItem(itemPath)
                if i.hasHtml:
                    itemPath = self.fs.splitExt(i.relPath)[0] + ".htm"
                if i.isDir:
                    html += "<li><a href='%sdefault.htm'>%s</a></li>" % (i.relPath, itemName)
                elif self.rep.mimeTypes.has_key(ext):
                    html += "<li><a href='%s'>%s</a></li>" % (i.relPath, itemName)
                else:
                    html += "<li>%s</li>" % i
            html += "</ul>"
            if self.body is not None:
                self.body += html
            else:
                self.body = html
            title = item.relPath
            if self.title is not None:
                self.title += " :- %s" % title
        if self.title is None:
            self.title = title
    
    
    def __fileManager_function(self):
        #print "__fileManager_function()"
        message = self.__message
        self.isFileView = True
        try:
            fileManager = self.iceContext.FileManager(self, self.fs, message)
            self.fileManager = fileManager
            if fileManager.isAjax:
                e = self.iceContext.AjaxException("isAjax")
                e.data = fileManager.ajaxData
                raise e
            
            if fileManager.editBook:
                file = fileManager.editBookFile
                bookFileItem = self.rep.getItem(file)
                BookEditor = self.iceContext.getPlugin("ice.book.bookEditor").pluginClass
                bookEditor = BookEditor(self.iceContext, self.formData, 
                                            bookFileItem, self.packageItem)
                html = bookEditor.edit()
                if html is not None:
                    self.title = "Book editor"
                    self.body = html
                    return None
                return fileManager
            self.body = fileManager.getContent()
            self["appStyleCss"] += fileManager.includeStyle
            self.title = fileManager.title
            return fileManager
        except self.iceContext.AjaxException, e:
            raise e
        except Exception, e:
            if str(e).startswith("Access denied (SVN)"):
                msg = "<div class='app-err-msg'>%s</div><div class='app-err-info'>%s</div>" 
                msg = msg % (str(e), "You do not have permission to access this page online, click logout to view the page offline.")
                self.title = "File manager"
                self.body =  msg
            else:
                raise 
    

    #-----------------------------------
    # test methods for IceFunctions
    #-----------------------------------
    @property
    def isPackage(self):
        return self.isInPackage
    
    @property
    def isPackageRoot(self):
        path = self.uri.rstrip("/")
        if path.endswith("/toc.htm"):
            path = path[:-len("/toc.htm")]
        if path.endswith("/default.htm"):
            path = path[:-len("/default.htm")]
        return self.packagePath==path and path!=""
    
    
    def requireLogin(self):
        return self.rep.requireLogin
    
    #--------------------------------------------------
    def getPackagePathFor(self, path):
        """ returns the rootPackagePath for the given path 
            or None if the given path does not point to a package path """
        packagePath = None
        nodeMapper = self.iceContext.NodeMapper(path, {})
        title, packagePath = self.mapPath(nodeMapper)
        if packagePath=="":
            packagePath = None
        return packagePath
    
    
    def setup(self):                                # access point
        pass
    
    
    def mapPath(self, nodeMapper):      # access point
        # returns (title, packagePath)
        title = "Ice web application"
        packagePath = ""
        packageNode = False
        # while it is not 'package', 'Package', 'packages' or 'Packages' - skip  
        while nodeMapper.renode("^(?!(P|p)ackages?$).*$", "parent"): pass
        if nodeMapper.node('packages') or nodeMapper.node('Packages'):
            title = "Packages"
            if nodeMapper.renode('^.*$', 'code'):
                packagePath = nodeMapper.pathToHere
        elif nodeMapper.node('package') or nodeMapper.node('Package'):
            title = "Package"
            ##nodeMapper["code"] = ""       # not valid
            packagePath = nodeMapper.pathToHere
        return (title, packagePath)
    
    
    def preRender(self):                            # access point
        pass
    
    
    def postRender(self, html):                     # access point
        #xhtmlTemplateFilename = self.session.get("xhtmlTemplateFilename", self.defaultXhtmlTemplateFilename)
        #xhtmlTemplateFilename = "/skin/%s.post.py" % self.fs.splitExt(xhtmlTemplateFilename)[0]
        #print "xhtmlTemplateFilename='%s'" % xhtmlTemplateFilename
        #i = self.__rep.getItem(xhtmlTemplateFilename)
        #data = i.read()
        #if data is not None:
        #    print len(data)
        return html
    
    
    def render(self, iceContext, xhtmlTemplateFilename=None):
        if self["html"]!="":
            return self["html"]
        if self.body is None:
            self.__getFileHtmlRendition()
        content = iceContext.DictionaryObject(defaultValue="")
        for key in self.__templateDict.keys():
            content[key] = self.__templateDict[key]
        self.content = content
        content.url = self.item.uri
        #content.name = self.item.name                          # ?
        content.isTocPage = self._isTocPage                     # ?
        content.isDefaultPage = self._isDefaultPage             # ?
        content.defaultPageEquals = self._defaultPageEquals     # ?
        content.packagePath = self.packagePath
        
        isSlidePage = self.uri.endswith(".slide.htm")
        content.isSlidePage = isSlidePage
        # Get TemplateInfo
        if xhtmlTemplateFilename is None:
            xhtmlTemplateFilename = self.session.get("xhtmlTemplateFilename",
                                            self.defaultXhtmlTemplateFilename)
        try:
            iceTemplateInfo = self.iceContext.getIceTemplateInfo( 
                        xhtmlTemplateFilename, isSlidePage, self.packagePath)
        except:
            xhtmlTemplateFilename = self.defaultXhtmlTemplateFilename
            iceTemplateInfo = self.iceContext.getIceTemplateInfo( 
                        xhtmlTemplateFilename, isSlidePage, self.packagePath)
        #Test for SplashPage (splash page)
        if iceTemplateInfo.hasSplashData and self._isDefaultPage:
            self._defaultPageEquals = None
            if self.item.name!="toc.htm":
                self._isTocPage = False
            content.defaultPageEquals = self._isDefaultPage
            content.isTocPage = self._isTocPage
        
        # support file view with splash page
        if self.formData is not None:
            fileView = self.formData.has_key('fileview') or \
                (iceTemplateInfo.hasSplashData and not self.formData.path.endswith("default.htm"))
            if fileView:
                self._isDefaultPage = False
                content.isDefaultPage = False
        
        content.defaultPageEquals = self._defaultPageEquals
        content.altUrls = self.__getAltUrls()
        # preRender here ???
        iceSiteRender = self.iceContext.getIceSiteRender()
        contextList = self.__getContextList(self.manifest, self.item)
        html = iceSiteRender.render(content, iceTemplateInfo, self.displayItem, \
                    contextList, self.manifest, 
                    self.includeSource, self.addNbspToEmptyTableCells, \
                    exportVersion=self.exportVersion,
                    noContextLink=self.noContextLink)
        return html
    
    
    def __getContextList(self, manifest, item):
        # Context-Link
        contextList = []        # list of tuples (name, url)
        spath = item.uri
        if manifest is not None:
            mItem = manifest.getManifestItem(item.guid)
            packagePath = self.packagePath
            while mItem is not None and mItem.relPath!="":
                contextList.insert(0, (mItem.title, packagePath+mItem.renditionName))
                mItem = manifest.getParentOf(mItem)
            contextList.insert(0, ("Contents", packagePath+"toc.htm"))
        else:
            path = spath
            if path.endswith("/default.htm"):
                path = path[:-len("/default.htm")]
            path = path.rstrip("/")
            cpath = path.strip("/")
            parts = cpath.split("/")
            repPropName = item.name
            cLink = "/"
            contextList.append(("/", cLink))
            cLink = cLink.rstrip("/")
            for part in parts:
                cLink = "%s/%s" % (cLink.rstrip("/"), part)
                #cLink += "/" + part
                if part=="default.htm":
                    #part = "Home"
                    continue
                if part.find(".htm")==-1:  #this is for folder
                    cLink = "%s/" % cLink.rstrip("/")
                contextList.append((part, cLink))
        return contextList
    
    
    def __getAltUrls(self):
        thisUrl = self.item.thisUri
        altUrls = []
        if self.item.isFile:
            altUrls = [thisUrl]
        elif self.item.isDirectory:
            if self._isTocPage:
                altUrls.append(thisUrl+"toc.htm")
            if self._isDefaultPage:
                altUrls.append(thisUrl+"default.htm")
                altUrls.append(thisUrl)
                if self._defaultPageEquals is not None:
                    altUrls.append(self._defaultPageEquals)
        if self.displayItem!=self.item:
            if self.displayItem.hasHtml:
                displayUri = self.displayItem.thisUri[:-len(self.displayItem.ext)] + ".htm"
                altUrls.append(displayUri)
        return altUrls
    #------------------------------------
    
    
    def __createToolbar(self):
        createToolbar = self.iceContext.getPlugin("ice.createToolbar").pluginFunc
        return createToolbar(self.iceContext, self.item, self)
    
    
    ###########################################################################
    
    def __getContextToc(self):
        iceContext = self.iceContext
        packageItem = self.packageItem
        item = self.item
        getContextToc = iceContext.getPlugin("ice.contextToc").pluginFunc
        return getContextToc(iceContext, packageItem, item)
    
    
    def __getNavButtons(self, isTocPage):
        iceContext = self.iceContext
        manifest = self.manifest
        item = self.item
        packagePath = self.packagePath
        getNavButtons = iceContext.getPlugin("ice.navButtons").pluginFunc
        return getNavButtons(iceContext, manifest, item.guid, isTocPage, packagePath)
    
    
    #--------------------------------------------------    
    





