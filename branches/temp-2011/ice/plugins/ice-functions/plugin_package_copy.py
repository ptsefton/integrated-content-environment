
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

from html_cleanup import HtmlCleanup
import re

oOfficeNSList = [ \
            ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"), \
            ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"), \
            ("xlink", "http://www.w3.org/1999/xlink"), \
            ("dc", "http://purl.org/dc/elements/1.1/"), \
            ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"), \
            ("ooo", "http://openoffice.org/2004/office"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"), \
         ]

  

pluginName = "ice.function.packageCopy"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = None
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    pluginFunc = packageCopy
    PackageCopy.myPath    = path
    PackageCopy.HtmlTemplate = iceContext.HtmlTemplate
    return pluginFunc


def isPackage(self):    
    return self.isPackage    


def packageCopy(self):
    d = {}        #to be removed
    reps = []    #to be removed
    
    packagePath = self.packagePath
    print "*** packageCopy() plugin ***"
    
    packageCopyObj = PackageCopy(self.iceContext)
    self["title"] = "Copy Package"
    self["body"] = "<h2>Package Copy Testing</h2>"
    self["body"] = packageCopyObj.packageCopy(packagePath, self.formData, self.rep)
    
    return
packageCopy.options={"toolBarGroup":"advanced", "position":16, "postRequired":False,
                         "enableIf":isPackage, "label":"Copy package", "title":"Copying package"} 




class PackageCopy(object):
    myPath    = ""
    packageCopyTemplateName = 'package-copy-template.tmpl'
    HtmlTemplate = None             # injected data
    HtmlParser = None
    bookInfo = None

    def __init__(self, iceContext, forUnitTest=False): 
        self.iceContext = iceContext
        self.__rep = self.iceContext.rep
        self.__fs = iceContext.fs
        if not forUnitTest:
            settings = iceContext.settings
            self.__settings = iceContext.settings
            self.__system = iceContext.system
            self.__requestData = None
            self.__homePath = iceContext.system.getOsHomeDirectory()
            if self.__settings is not None:
                try:
                    self.repList = self.__settings.repositories #using config.xml
                except:
                    self.repList = self.iceContext.config.repositories  #using config2.xml for server
            
            #self.IceRender = iceContext.IceRender
            self.HtmlParser = HtmlCleanup
            
            self.d = {}
            
            self.repositoriesList = self.__getRepositoriesList()
            
            self.currentRep = ""
    
    
    def packageCopy(self, packagePath, requestData, rep, configFile=None):
        if self.__rep is None:
            self.__rep = rep
        
        self.currentRep = self.__rep.name
        self.packagePath = packagePath
        self.__requestData = requestData
        self.argPath = self.__requestData.value("argPath")
        self.newSubject = ""
        self.newPathName = ""
        self.newPackageTitle = ""
        html=""
        self.d["message"] = ""
        self.hasSkin = False
        packageSkinPath = self.__rep.getAbsPath(packagePath)+"/skin"
        if self.__fs.exists(packageSkinPath):
            self.hasSkin = True
        self.d["hasSkin"]= self.hasSkin
        if self.__requestData.has_key("ispostback"):
            self.copyToPath = self.__requestData.value("copyToPath", "").strip()
            self.copyToRep  = self.__requestData.value("copyToRep", "").strip()
            self.newSubject = self.__requestData.value("newSubject", "").strip()
            self.includeAnnot = self.__requestData.value("annotation")
            self.includeSkin  = self.__requestData.value("skin")
            self.newPackageTitle = self.__requestData.value("newPackageTitle", "").strip()
            copied=False
            self.sameRep = True
            try:
                copyToRepPath = ""
                for rep in self.repositoriesList:
                    if rep.name == self.copyToRep:
                        copyToRepPath = rep.getAbsPath()                        
                        self.destinationRep = rep
                        break
                
                if self.copyToPath.endswith("/"):
                    self.copyToPath = self.copyToPath[:-1]
                stripPath = self.copyToPath.lstrip("/")
                self.newPathName = self.iceContext.url_join(copyToRepPath, stripPath)
                self.newPathName = self.newPathName.replace("\\", "/")
                
                #Same Directory
                if self.copyToPath!=self.packagePath \
                        and self.copyToPath!="" \
                        and self.copyToRep==self.currentRep:
                    packageItem = self.__rep.getItem(self.packagePath)
                    destItem = self.__rep.getItem(self.copyToPath)
                    packageItem.copy(destItem, annotation=self.includeAnnot)
                    if True:
                        copyLinks = self.iceContext.getPluginClass("ice.copyLinks")(self.iceContext)
                        copyLinks.convert(copyFrom=packageItem.relPath, copyTo=destItem.relPath)
                        # Find all book documents and fix up there links also
                        for listItems in destItem.walk(filesOnly=True):
                            for item in listItems:
                                if item.ext in self.iceContext.bookExts:
                                    bookInfo = item.bookInfo
                                    if bookInfo is not None:
                                        bookInfo.relBookFile = item.relPath
                                        bookInfo.makeRelative(packageItem.relPath, destItem.relPath)
                                        bookInfo.save(self.iceContext.rep)
                    self.sameRep = True    
                    copied=True
                elif self.copyToPath!="" and self.copyToRep!=self.currentRep: #different directory
                    #check if directory is existed
                    if not self.__fs.isDirectory(self.newPathName):
                        packageItem = self.__rep.getItem(self.packagePath)
                        packageItem.export(self.newPathName)
                        packageItem = self.destinationRep.getItem(self.copyToPath)
                        packageItem.add(recurse=True)
                        self.sameRep = False
                        copied=True
                    else:
                        html = "<div>Error: Path '%s' already exists, Try 'Synchronizing' first!</div>" % self.newPathName
                if copied:
                    if self.includeAnnot is None:
                        self.__removeOptions(annotation="inline-annotations", skin=self.includeSkin)
                    elif self.includeSkin is None:
                        self.__removeOptions(skin=self.includeSkin)
                    
                    html = "<div class='searchResults'>Success: %s is copied to " % self.packagePath
                    
                    copyToPath = self.copyToPath
                    if not copyToPath.endswith("/"):
                        copyToPath = "%s/" % self.copyToPath.lstrip('/')
#                    if self.sameRep:
#                        html += "<a href='%s'>%s</a>" % (copyToPath, self.copyToPath)
#                    else:
                    html += "<a href='%srep.%s/%s'>%s</a>" % (self.iceContext.siteBaseUrl, self.copyToRep, copyToPath, self.copyToPath)
                    
                    if self.newSubject!="":
                        html += self.__changeSubject()
                    
                    if self.newPackageTitle!="":
                        html += self.__changePackageTitle()

                    if self.newSubject!="":
                        html += "<div style='color:orange'><b>Warning</b> : Subject cannot be changed in Microsoft Word Documents(*.doc).</div>"
                    #Do book property clean up 
                    self.__cleanUpBookInfo()
                        
                    #fixup links in new copied packages
                    self.__fixUpLinks()
                    html += "</div>"
                self.d["message"] = html 
            except Exception, e:
                html = "<div>Error: " + str(e) + ""
                html += ", <b>Try 'Synchronizing' first!</b></div>"
                print self.iceContext.formattedTraceback()
                self.d["message"] = html
        if self.__requestData.value("copyToPath") is None or self.__requestData.value("copyToPath") == "":
            self.copyToPath = self.packagePath
        else:
            self.copyToPath = self.__requestData.value("copyToPath")
        return self.__getPackageCopyFrom()


    def __cleanUpBookInfo(self):
        import sys
        global bookInfo
        bookInfo = self.iceContext.getPlugin("ice.book.bookInfo").pluginClass
        
        class BI(object):
            bookInfo = bookInfo
            bookDocument = bookInfo.BookDocument
            
            def __init__(self, iceContext):
                self.iceContext = iceContext
            
            def dumps(self):
                return self.iceContext.dumps(self)
        
        class bookInfo1_2(object):
            def __init__ (self):
                self.bookInfo = bookInfo1_2
                self.bookDocument = bookInfo1_2
        
        item = self.__rep.getItem(self.packagePath)
        for listItems in item.walk(filesOnly=True):
            for i in listItems:
                if i.ext not in self.iceContext.bookExts:
                    continue
                sys.modules["book_info"] = bookInfo1_2()
                bookInfoInd = i
                if bookInfoInd.bookInfo is None: 
                    bookInfoInd = self.__rep.getSvnProp("meta-bookInfo", self.__rep.getAbsPath(i.relPath))
                    if bookInfoInd is not None:
                        oldBook = bookInfoInd
                        newPath = self.__newBookPath(i.relPath)
                        newBookInfo = bookInfo(self.iceContext, newPath)
                        sys.modules["book_info"] = newBookInfo
                        newBookInfo._BookInfo__relBasePath = self.__newBookPath(oldBook._bookInfo__relBasePath) 
                        newBookInfo._BookInfo__setRelBookFile(self.__newBookPath(oldBook._bookInfo__relBookFile))
                        newBookInfo._BookInfo__changes = oldBook._bookInfo__changes
                        renderAsHtml = oldBook._bookInfo__renderAsHtml
                        newBookInfo._BookInfo__setRenderAsHtml(renderAsHtml)
                        pageRef = False
                        try:
                            #not all v1.2 book has these
                            pageRef = oldBook._bookInfo__pageRef
                        except:
                            pass
                        if not renderAsHtml and not pageRef:
                            newBookInfo._BookInfo__setPdfOnly(True)
                        else:
                            newBookInfo._BookInfo__setPdfOnly(False)
                        
                        newBookInfo._BookInfo__setPageRef(pageRef)
                        newBookInfo._BookInfo__tempDir = None
                        
                        title = self.__rep.getSvnProp("meta-title", self.__rep.getAbsPath(i.relPath))
                        
                        if title is not None and title!="":
                            newBookInfo._BookInfo__setBookTitle(title)
                            
                        newBookInfo._BookInfo__documents = []
                        for doc in oldBook._bookInfo__documents:      
                            path = self.__newBookPath(doc._bookDocument__path)
                            url = self.__newBookPath(doc._bookDocument__url)
                            md5=""
                            pageBreakType=""
                            try:
                                md5 = doc._bookDocument__md5
                                pageBreakType = doc._bookDocument__pageBreakType
                            except:
                                pass
                            newDoc = bookInfo.BookDocument(path, url)
                            newDoc._BookDocument__setMd5(md5)
                            newDoc._BookDocument__setPageBreakType(pageBreakType)
                            newBookInfo._BookInfo__documents.insert(9999, newDoc)
                            
                        item = self.destinationRep.getItem(newPath)
                        item.flush()
                        item.setBookInfo(newBookInfo)
                        item.close()
                else:
                    #found new version bookProp
                    bookProp = bookInfoInd.bookInfo
                    newPath = self.__newBookPath(i.relPath)
                    bookProp._BookInfo__relBasePath = self.__newBookPath(bookProp._BookInfo__relBasePath)                    
                    bookProp._BookInfo__setRelBookFile(self.__newBookPath(bookProp._BookInfo__getRelBookFile()))
                    bookProp._BookInfo__changes = bookProp._BookInfo__changes
#                    bookProp._BookInfo__setRenderAsHtml(bookProp._BookInfo__renderAsHtml)
                                                       
                    for doc in bookProp._BookInfo__documents:
                        path = self.__newBookPath(doc._BookDocument__path)
                        url = self.__newBookPath(doc._BookDocument__url)
                        doc._BookDocument__setPath(path)
                        doc._BookDocument__setUrl(url)
                    bookItem = self.destinationRep.getItem(newPath)
                    bookItem.flush()
                    bookItem.setBookInfo(bookProp)
                    bookItem.close()  

                    destinationItem = self.destinationRep.getItem(self.copyToPath)
                    
                    manifest = destinationItem.getMeta("manifest")
                    manifest.updateItems(destinationItem)
                    destinationItem.flush(True)
                    
    def __newBookPath(self, path):
        if self.packagePath!=self.copyToPath:
            packagePath = self.packagePath.rstrip("/")
            copyToPath = self.copyToPath.rstrip("/")
            return path.replace(packagePath, copyToPath)
        return path

    def __removeOptions(self, annotation=None, skin=True):        
        removeAnnot = False
        removeSkin  = False
        if annotation is not None:
            removeAnnot=True
        
        if not skin:
            removeSkin=True
        def callback(path, dirs, files):
            packagePath = path.find(self.copyToPath)
            filePath = path[packagePath:]
            if removeAnnot:
                for dir in dirs:
                    if dir == annotation:
                        rDir.append(filePath + dir)
                    if removeSkin:
                        if dir=="skin" or dir==".skin":
                            rDir.append(filePath + dir)
                    else: #rename .skin to skin
                        if dir==".skin":
                            renameDir[filePath + dir] = (filePath + "skin")                                
            elif removeSkin: 
                for dir in dirs:
                    if dir == "skin" or dir==".skin":
                        rDir.append(filePath + dir)
            elif not removeSkin: #rename .skin to skin
                for dir in dirs:
                    if dir==".skin":
                        renameDir[filePath + dir] = (filePath + "skin")
            for file in files:
                if self.sameRep:
                    if removeAnnot:
                        if file==annotation:
                            rFiles.append(filePath + file)
                    if file == "tags":
                        rFiles.append(filePath + file)
                else:
                    if removeAnnot:
                        if file==annotation:
                            rFiles.append(path + file)
                    if file == "tags":
                        rFiles.append(path + file)

        rFiles = []    
        rDir = []
        renameDir = {}
        self.__fs.walker(self.newPathName, callback)
        if rFiles != []:
            for file in rFiles:
                try:
                    if self.sameRep:
                        self.__rep.getItem(file).delete()
                    else:
                        if self.destinationRep is not None:
                            self.destinationRep.getItem(file).delete()
                        else:
                            self.__fs.delete(file)     #export does not export svn prop
                except Exception, e:
                    pass
        
        if rDir != []:
            for dir in rDir:                
                try:
                    if self.sameRep:
                        self.__rep.getItem(dir).delete()
                    else:                        
                        if self.destinationRep is not None:
                            self.destinationRep.getItem(dir).delete()
                        else:
                            self.__fs.delete(dir)      #export does not export svn prop
                except Exception, e:
                    pass
                
        if renameDir != {}:
            for dir in renameDir:
                try:
                    renameTo = renameDir[dir]
                    if self.sameRep:
                        dirItem = self.__rep.getItem(dir)
                        renameItem = self.__rep.getItem(renameTo)
                        dirItem.move(renameItem)
                        dirItem.delete()
                        renameItem.add(recurse=True)
                    else:
                        if self.destinationRep is not None:
                            dirItem = self.destinationRep.getItem(dir)
                            renameItem = self.destinationRep.getItem(renameTo)
                            dirItem.move(renameItem)
                            dirItem.delete()
                            renameItem.add(recurse=True)
                        else:
                            self.__fs.move(dir, renameDir[dir])
                except Exception, e:
                    pass
            
        
    def __getPackageCopyFrom(self):
        file = self.__fs.join (self.myPath, self.packageCopyTemplateName)
        
        htmlTemplate = self.HtmlTemplate(templateFile=file)
        
        self.d["copyToPath"] = self.copyToPath
        self.d["reps"] = self.repositoriesList
        self.d["currentRepositoryName"] = self.currentRep
        self.d["argPath"] = self.argPath
        html = htmlTemplate.transform(self.d, allowMissing=True)
    
        return html
        
    def __fixUpLinks(self):
        def callback(path, dirs, files):
            for file in files:
                ext = self.__fs.splitExt(file)[1]
                if ext == ".odt" or ext == ".book.odt":
                    rFiles.append(path + file)
                if ext == ".html" or ext == ".htm":
                    rHtmlFiles.append(path + file)
                    
        rFiles = []
        rHtmlFiles = []
        self.__fs.walker(self.newPathName, callback)

        for file in rFiles:
            try:
                tempDir = self.__fs.unzipToTempDirectory(file)
                xml = self.iceContext.Xml(tempDir.absolutePath("content.xml"), oOfficeNSList)
                
                nodes = xml.getNodes("//text:a[@xlink:href] | \
                                      //draw:a[@xlink:href]")
                for node in nodes:
                    href = node.getAttribute("href")
                    isLocal = self.iceContext.isLocalUrl(href)
                    if isLocal:
                        href = self.__validLink(href)
                        node.setAttribute("href", href)
                xml.saveFile()
                xml.close()
                tempDir.zip(file)
                tempDir.delete()
            except Exception, e:
                xml.close()
                tempDir.delete()
            
        #fixing html files link
        for file in rHtmlFiles:
            links={}
            try:
                data = self.__fs.readFile(file)
                html = self.HtmlParser.convertHtmlToXml(data)
                xml = self.iceContext.Xml(html)
                
                nodes = xml.getNodes("//@href | //@src | //@HREF | //@Href | //@SRC | //@Src | //object/@data | \
                                 //object/param[@name='src' or @name='movie' or @name='url']/@value | \
                                 //applet/param[@name='load' or @name='filename']/@value | \
                                 //applet/@archive" )
                for node in nodes:
                    href = node.getContent()
                    if self.iceContext.isLocalUrl(href):
                        validHref = self.__validLink(href)
                        links[href] = validHref
                self.__fs.writeFile(file, str(xml.getRootNode()))
                xml.close()
                
                #replaceAllLinks
                if links != {}:
                    data = self.__fs.readFile(file)
                    for key in links:
                        #data = data.replace(key, links[key])
                        rk = re.escape(key).replace("&", "&(amp;)?")
                        rt = self.iceContext.textToHtml(links[key])
                        data = re.sub(rk, rt, data)
                    self.__fs.writeFile(file, data)
            except Exception, e:
                xml.close()


    def __stripEncodedText(self, s):
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        return s


    def __validLink(self, href):
        currentRep = "/rep.%s" % (self.currentRep)
        copyToRep = "/rep.%s" % (self.copyToRep)
        currentPath = "%s" % (self.packagePath.rstrip("/"))
        copyToPath = "%s" % (self.copyToPath.rstrip("/"))
        
        #to make it similar
        if not copyToPath.startswith("/") and currentPath.startswith("/"):
            copyToPath = "/%s" % copyToPath
        elif copyToPath.startswith("/") and not currentPath.startswith("/"):
            copyToPath = copyToPath.lstrip("/")
#        print "__________"
#        print "base: ", self.iceContext.siteBaseUrl
#        print "href: ", href
#        print "currentRep: ", currentRep
#        print "copyToRep: ", copyToRep
#        print "currentPath: ", currentPath
#        print "copyToPath: ", copyToPath
        
        repPos = href.find("rep.")
        if repPos>-1:
            hrefContent = href[repPos:].split("/")
            linkRepName = "/%s" % hrefContent[0]
            if linkRepName == copyToRep:
                #Only fix when the currentPath is exist
                if href.find(currentPath)>-1:
                    href = href.replace(currentPath, copyToPath)
            elif linkRepName == currentRep:
                #change to copyToRep
                if href.find(currentPath)>-1:
                    href = href.replace(currentPath, copyToPath)
                href = href.replace(currentRep, copyToRep)
            else: 
                #fix it here
                pass
        else:
            packagePos = href.find("packages")
            if packagePos>-1:                
                if href.find(currentPath)>-1:
                    href = href.replace(currentPath, "%s%s" % (copyToRep, copyToPath))
                else:
                    href = href.replace("/packages", "%s/packages" % (copyToRep))
                pass
            else:
                #without packages
                if href.find(currentPath)>-1:
                    href = href.replace(currentPath, "%s%s" % (copyToRep, copyToPath))
        return href


    def __changeSubject(self):       
        html = ""
        tempDir = None
        def callback(path, dirs, files):
            for file in files:
                ext = self.__fs.splitExt(file)[1]
                if ext == ".odt" or ext == ".book.odt":
                    rFiles.append(path + file)
                if ext == ".docx":
                   wFiles.append(path + file)
            
        rFiles = []
        wFiles = []
        self.__fs.walker(self.newPathName, callback)
        
        for file in rFiles:            
            try:
                tempDir = self.__fs.unzipToTempDirectory(file)
                xml = self.iceContext.Xml(tempDir.absolutePath("meta.xml"), oOfficeNSList)
                node = xml.getNode("//dc:subject")
                
                if node is not None:
                    node.content = self.newSubject
                else:                    
                    node = xml.getNode("//office:meta")
                    newNode = xml.createElement("dc:subject")     
                    newNode.setContent(self.newSubject)
                    node.addChild(newNode)
                xml.saveFile()
                xml.close()
                tempDir.zip(file)
                tempDir.delete()
                html = "<br/>New subject for this package: %s" % self.newSubject 
            except Exception, e:
                html = "<div>Error: " + str(e) + ""
                html += ", <b>In changing subject of %s to: new subject</b></div>" % (self.newPathName)
                tempDir.delete()
        if wFiles != []:        
            for file in wFiles:
                #word docx files
                try:
                    tempDir = self.__fs.unzipToTempDirectory(file)
                    filePath = tempDir.absolutePath("docProps/core.xml")
                    xml = self.iceContext.Xml(tempDir.absolutePath("docProps/core.xml"), oOfficeNSList)
                    node = xml.getNode("//dc:subject")
                    if node is not None:
                        node.content = self.newSubject
                    xml.saveFile()
                    xml.close()
                    tempDir.zip(file)
                    tempDir.delete()
                except Exception, e:
                    html = "<div>Error in word document: " + str(e) + "<br/>"
                    html += ", <b>In changing subject of %s to: new subject</b></div>" % (self.newPathName)
                    tempDir.delete()
        return html
    
    def __changePackageTitle(self):
        try:
            destinationItem = self.destinationRep.getItem(self.copyToPath)
            manifest = destinationItem.getMeta("manifest")
            manifest.title = self.newPackageTitle
            destinationItem.flush(True)
            html = "<br /> New Package Title for this package: %s" % self.newPackageTitle
        except  Exception, e:
            html = "<br/> Error : " + str(e)
            html += ", In <b> changing package title to new title</b>"
        return html
    
    def __getRepositoriesList(self):
        repositories = self.iceContext.reps.names
        reps = []
        for name in repositories:
            reps.append(self.iceContext.reps.getRepository(name))
        return reps
    
