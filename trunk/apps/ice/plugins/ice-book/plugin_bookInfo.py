
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
from urllib import quote


pluginName = "ice.book.bookInfo"
pluginDesc = "book info"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    #print "bookinfo plugin init"
    
    pluginFunc = None
    pluginClass = BookInfo
    pluginInitialized = True
    return pluginFunc



class BookDocument(object):
    """ bookDocument objects are used by the bookInfo class """
    
    def __init__(self, path, url, md5=None):
        self.__path = path
        self.__url = url
        self.__md5 = md5
        self.__pageBreakType = "Odd"        # "PageBreak"  | "" | "Even" | "Odd"
        self.__pageOrientation = ""
    
    def __getPath(self):
        return self.__path
    def __setPath(self, path):
        self.__path = path
    path = property(__getPath, __setPath)
    
    def __getUrl(self):
        return self.__url
    def __setUrl(self, url):
        self.__url = url
    url = property(__getUrl, __setUrl)
    
    def __getMd5(self):
        return self.__md5
    def __setMd5(self, value):
        self.__md5 = value
    md5 = property(__getMd5, __setMd5)
    
    def __getPageBreakType(self):
        try:
            r = self.__pageBreakType
        except:
            r = ""
            self.__pageBreakType = r
        return r
    def __setPageBreakType(self, pageBreakType):
        self.__pageBreakType = pageBreakType
    pageBreakType = property(__getPageBreakType, __setPageBreakType)
    
    def __getPageOrientation(self):
        try:
            r = self.__pageOrientation 
        except:
            r = ""
            self.__pageOrientation = r
        return r
    def __setPageOrientation(self,value):
        self.__pageOrientation = value
    pageOrientation = property(__getPageOrientation, __setPageOrientation)
    
    def currentMd5(self, rep):        # ???
        item = rep.getItem(self.__path)
        return item._getCurrentMd5()
    
    def isMissing(self, rep):
        return not rep.getItem(self.__path).isFile
    
    def hasChanged(self, rep):
        item = rep.getItem(self.__path)
        if item is None:
            return False
        if item.needsUpdating==False:
            md5 = item.getMeta("lastMD5")
        else:
            md5 = self.currentMd5(rep)
        if md5!=self.__md5:
            return True
        else:
            return False
        
    def updateMd5(self, rep):
        #print "doc.updateMd5() path=", self.__path
        item = rep.getItem(self.__path)
        if item.needsUpdating:
            #print " needs updating"
            md5 = self.currentMd5(rep)
        else:
            #print " has changed (and been rerendered)"
            md5 = item.getMeta("lastMD5")
        if md5!=self.__md5:
            pass
        self.__md5 = md5
    
    def makeRelative(self, fromPath, toPath):
        #self.__path, self.__url, self.__md5
        l = len(fromPath)
        if self.__path.startswith(fromPath):
            self.__path = toPath + self.__path[l:]
        if self.__url.startswith(fromPath):
            self.__url = toPath + self.__url[l:]



class BookInfo(object):
    BookDocument = BookDocument
    
    # static renderMethod(file, absFile, rep)
    # Constructor (path, title)
    # Properties
    #    filePath               # the repRelative path to the book file
    #    bookTitle              # the book's Title
    # Methods
    #    iterDocuments()        # iterate over all of the documents in the book (inoder)
    #    removeDocument(path)
    #    addDocument(path, url)
    #    insertDocument(index, path, url)
    #    moveDocument(path, newIndex)
    #
    
    @staticmethod
    def renderMethod(iceContext, bookItem, convertedData, **kwargs):
        force = kwargs.get("force", False)
        bookInfo = bookItem.bookInfo
        if bookInfo is None:
            bookInfo = BookInfo(iceContext, bookItem.relPath, "Untitled Book")
            bookInfo._save(bookItem)
        #if force:
        #    bookInfo.buildBook()
        convertedData = bookInfo.renderBook(convertedData, bookItem=bookItem)
        bookItem.flush()
        return convertedData
    
    
    def __init__(self, iceContext, relBookFile=None, title=None):
        #print "BookInfo __init__()"
        self.iceContext = iceContext
        self.bookItem = None
        self.__documents = []        # list of document objects
        self.__changes = True
        # render properties
        self.__bookTitle = title
        self.__renderAsHtml = False
        self.__pageRef = False
        self.__pdfOnly = False
        self.__renderPropChanges = True
        
        self.__bookModifiedDate = 0
        self.__bookMD5 = None
        
        if relBookFile:
            self.__relBookFile = relBookFile
            self.__relBasePath = self.iceContext.fs.split(relBookFile)[0]
        #print "BookInfo.__init__()"
        self.__oOfficeNSList = self.iceContext.OOoNS.items()
    
    
    def __getstate__(self):
        #print "writing __getstate__ '%s'" % self.__relBookFile
        #print " self.__renderPropChanges=%s" % self.__renderPropChanges
        d = dict(self.__dict__)
        #className = self.__class__.__name__
        d.pop("iceContext")
        d.pop("bookItem")
        return d
    
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        #print "reading __setstate__() '%s'" % self.__relBookFile
        #print "  self.__renderPropChanges=%s" % self.__renderPropChanges
        self.bookItem = None
        try:
            x = self.__renderPropChanges
        except Exception, e:
            #print "Setting renderPropChanges '%s'" % str(e)
            self.__renderPropChanges = True
        try:
            x = self.__bookMD5
        except Exception, e:
            self.__bookMD5 = None
        try:
            x = self.__bookModifiedDate
        except Exception, e:
            self.__bookModifiedDate = 0
    
    
    def __del__ (self):
        pass
    
    
    @property
    def needsBuilding(self):
        # needs reBuilding if any of it's documents (or template) files have changed 
        #   (or changed order/position)
        if self.__changes:                  # any changes e.g. order etc
            #print "needs building because of changes"
            return True
        rep = self.iceContext.rep
        for doc in self.__documents:        # any documents have changed
            if doc.hasChanged(rep):
                msg = "book is not upto date because book document '%s' has changed" % doc.path
                self.iceContext.writeln(msg)
                self.__changes = True
                return True
        return self.__changes
    
    
    @property
    def needsRendering(self):
        # if any render properties have changed - or has been reBuilt since last render
        #   or the book document has been changed
        #  also needs rendering if it needsBuilding
        if self.needsBuilding:
            return True
        if self.__renderPropChanges:
            return True
        # if the book file itself has been changed
        bookItem = self.iceContext.rep.getItem(self.relBookFile)
        if bookItem.lastModifiedDateTime!=self.__bookModifiedDate:
            # ok check if it has been changed
            if bookItem._getCurrentMd5()!=self.__bookMD5:
                #print "--needsRendering because book MD5 differs"
                self.__renderPropChanges = True
            else:
                self.__bookModifiedDate = bookItem.lastModifiedDateTime
        return self.__renderPropChanges
    
    
    @property
    def relBasePath(self):
        return self.__relBasePath
    
    
    @property
    def documents(self):
        return self.__documents
    
    
    def __getRelBookFile(self):
        return self.__relBookFile
    def __setRelBookFile(self, relBookFile):
        if relBookFile!=self.__relBookFile:
            self.__relBookFile = relBookFile
    relBookFile = property(__getRelBookFile, __setRelBookFile)
    
    
    def __getBookTitle(self):
        return self.__bookTitle
    def __setBookTitle(self, value):
        if value!=self.__bookTitle:
            self.__bookTitle = value
            self.__renderPropChanges = True
    bookTitle = property(__getBookTitle, __setBookTitle)
    
    
    @property
    def title(self):
        title = self.iceContext.rep.getItem(self.relBookFile).getMeta("title")
        if title is None:
            title = "[Untitled]"
        return title
    
    
    def __getRenderAsHtml(self):
        try:
            #return self.__renderAsHtml and self.pageRef==False
            return self.__renderAsHtml
        except:
            return False
    def __setRenderAsHtml(self, value):
        if value!=self.renderAsHtml and value==True:
            self.__renderPropChanges = True
        self.__renderAsHtml = value
    renderAsHtml = property(__getRenderAsHtml, __setRenderAsHtml)
    
    
    def __getPdfOnly(self):
        try:
            return self.__pdfOnly
        except:
            return False
    def __setPdfOnly(self, value):
        if value!=self.pdfOnly and value==True:
            pass
            #self.__renderPropChanges = True
        self.__pdfOnly = value
    pdfOnly = property(__getPdfOnly, __setPdfOnly)
    
    
    def __getPageRef(self):
        try:
            return self.__pageRef
        except:
            return False
    def __setPageRef(self, value):
        if value!=self.pageRef:
            self.__changes = True
            self.__renderPropChanges = True
        self.__pageRef = value        
    pageRef = property(__getPageRef, __setPageRef)
    
    
    def buildBook(self):
        print " building book"
        file = self.relBookFile
        tmpBookFile = "tempBook.odt"
        tmpDir = self.iceContext.fs.createTempDirectory()
        absToFile = tmpDir.absolutePath(tmpBookFile)
        absFromFile = self.iceContext.rep.getAbsPath(file)
        #absToFile = absFromFile
        msg = self.__buildBook(absFromFile, absToFile, \
                        baseUrl="http://localhost:8000")
        if msg=="": # OK
            if self.pageRef:
                # add optional page referencing
                self.__pageRefBook(tmpDir, tmpBookFile)
            # Fix up lists in books
            self.__fixBookLists(tmpDir, tmpBookFile)
            
            tmpDir.copy(tmpBookFile, absFromFile)
            self.__changes = False
            self.__renderPropChanges = True
            bookItem = self.iceContext.rep.getItem(self.relBookFile)
            self._save(bookItem)
        tmpDir.delete()
        tmpDir = None
        print "done building book"
        return msg
    
    
    def renderBook(self, convertedData, doNotBuild=False, bookItem=None):
        ok = True
        msg = ""
        file = self.relBookFile
        if self.needsBuilding and not doNotBuild:
            # Then first build the book before rendering it
            msg = self.buildBook()
        #print " rendering book"
        if msg=="":
            if self.renderAsHtml:
                print " rendering book as HTML & PDF"         
                convertedData = self.iceContext.odtBookRenderMethod(file, convertedData)
                #print "convertedData=", str(convertedData)
            else:
                print " rendering book as PDF only"
                # odt/BaseConverter.renderPdfOnlyMethod
                reindex = True
                convertedData = self.iceContext.odtBookRenderMethod(file, \
                                    convertedData, reindex=reindex, pdfOnly=True)
            if not convertedData.error:
                if bookItem is None:
                    bookItem = self.iceContext.rep.getItem(self.relBookFile)
                self.__bookModifiedDate = bookItem.lastModifiedDateTime
                self.__bookMD5 = bookItem._getCurrentMd5()
                self.__renderPropChanges = False
                self._save(bookItem)
        else:
            convertedData.addErrorMessage(msg)
        return convertedData
    
    
    def makeRelative(self, fromPath, toPath):
        for doc in self.iterDocuments():
            doc.makeRelative(fromPath, toPath)
    
    
    def iterDocuments(self):
        for doc in self.__documents:
            yield doc
    
    
    def touch(self):
        self.__changes = True
    
    
    def removeDocument(self, index):
        print "removeDocument(index='%s')" % index
        try:
            self.__documents.pop(index)
            self.__changes = True
            return True
        except:
            return False
    
    
    def addDocument(self, path, url=None):
        if path==self.relBookFile:
            raise Exception("Can not add self to self")
        if url==None:
            base, ext = self.iceContext.fs.splitExt(path)
            if ext in [".odt", ".doc", ".docx"]:
                url = base + ".htm"
        self.insertDocument(9999, path, url)
        self.__changes = True
    
    
    def insertDocument(self, index, path, url):
        doc = BookDocument(path, url)
        self.__documents.insert(index, doc)
        self.__changes = True
    
    
    def moveDocument(self, index, newIndex):
        try:
            self.__changes = True
            doc = self.__documents[index]
            self.__documents.insert(newIndex, doc)
            if newIndex<index: index += 1
            self.__documents.pop(index)
            return True
        except:
            return False

    
    def __buildBook(self, absFromBookFile, absToBookFile, \
                        baseUrl="http://localhost:8000"):
        """ return (True, Title) or (False, ErrorMessage) """
        rep = self.iceContext.rep
        docs = []
        oooConverter = self.iceContext.getOooConverter()
        tmpDir = self.iceContext.fs.createTempDirectory()
        tempDir = oooConverter.getTempDirectory()
        # First convert any word documents to openOffice documents
        count=0
        try:
            for doc in self.__documents:
                if not doc.isMissing(rep):
                    url = quote(doc.url)
                    path = doc.path
                    path = rep.getAbsPath(path)
                    
                    ######
                    invalidWordConversion=False
                    if path.endswith(self.iceContext.wordExt) or path.endswith(self.iceContext.word2007Ext):
                        #print "Word file '%s' in Book." % path
                        name = self.iceContext.fs.split(path)[1]
                        toOdtFile = self.iceContext.url_join(str(tmpDir), name) + ".odt"
                        try:
                            #print "start to convert toOdtFile: ", toOdtFile
                            result = self.iceContext.getDocConverter().convertDocToOdt(path, toOdtFile)
                            #print "done in converting result: ", result
                            if result == "Word document is Invalid":
                                invalidWordConversion=True
                            path = toOdtFile
                        except Exception, e:
                            result = "ERROR - " + str(e)
                        path = toOdtFile
                    if invalidWordConversion:
                        errMsg = "Error in building book: failed to convert Word file '%s' (may be empty)" % doc.path
                        return (False, errMsg)
                    ######
                    
                    props = {}
                    if doc.pageBreakType=="PageBreak":
                        props["InsertPageBreak"] = True
                    elif doc.pageBreakType=="Odd":
                        props["InsertPageBreak"] = True
                        props["Page"] = "Odd"
                    elif doc.pageBreakType=="Even":
                        props["InsertPageBreak"] = True
                        props["Page"] = "Even"
                    else:
                        props["InsertPageBreak"] = False
                    
                    try:
                        props["Orientation"] = doc.pageOrientation
                    except:
                        props["Orientation"] = ""
                    
                    #Add add a temp paragraph to the end of the document
                    count = count+1
                    
                    toFile = tempDir.absolutePath("temp%s%s" % (count, self.iceContext.fs.splitExt(path)[1]))
                    r = self.__addTempParagraphToDocument(path, toFile)
                    if r == "Invalid Open Office Document":
                        errMsg = "Error in building book: %s file '%s'" % (r, doc.path)
                        return (False, errMsg)
                    else:
                        docs.append( [ path, rep.getAbsPath(doc.path), \
                                        self.iceContext.url_join(baseUrl, url), props ] )
                        doc.updateMd5(rep)                
                else:
                    print "  Warning: book file '%s' is missing!" % doc.path
                    doc.updateMd5(rep)
            
            try:
                if oooConverter.convertBaseDirectory!="":
                    tempToBookFile = tempDir.absolutePath("toBook.odt")
                    tempFromBookFile = tempDir.absolutePath("fromBook.odt")
                    self.iceContext.fs.copy(absFromBookFile, tempFromBookFile)
                    result = oooConverter.buildBook(tempFromBookFile, docs, \
                                                    tempToBookFile,  baseUrl=baseUrl, \
                                                    tempDir=tempDir)
                    self.iceContext.fs.copy(tempToBookFile, absToBookFile)
                else:
                    result = oooConverter.buildBook(absFromBookFile, docs, \
                                                    absToBookFile,  baseUrl=baseUrl)
            except Exception, e:
                print " exception - '%s'" % str(e)
                raise
            
            # Repair (lists etc) in odt file
            ooRepair = self.iceContext.getPlugin("ice.ooo.repair").pluginClass(self.iceContext)
            #ooRepair.repair(rep.getItem(absToBookFile)) #can't use rep to get temporary file item
            ooRepair.repair(tmpFile=absToBookFile)
        finally:
            if tempDir is not None and tempDir.isTempDirectory:
                tempDir.delete()
                tempDir = None
            if tmpDir is not None:
                tmpDir.delete()
                tmpDir = None
        if result.allOk:
            return ""
        else:
            if result.errorMessage is not None:
                if result.errorMessage.startswith("Failed to connect to OpenOffice"):
                    errMsg = "Failed to connect to OpenOffice, please make sure that OpenOffice is running (else restart) and try again!"
                else:
                    errMsg = result.errorMessage
            else:
                errMsg = "???"
                if hasattr(result, "odtResult"):
                    errMsg = result.odtResult.errorMessage
            print "Error =", errMsg
            return errMsg
    
    
    def save(self, r=None):
        bookItem = self.iceContext.rep.getItem(self.relBookFile)
        return self._save(bookItem)
    
    def _save(self, bookItem):
        iceContext = self.iceContext
        self.iceContext = None
        bookItem.setBookInfo(self)
        bookItem.close()
        self.iceContext = iceContext
        self.bookItem = None
        try:
            # This will fail if the book is open!
            bookItem.replaceFileInZipFile("lastTimeTouched", str(time.time()))
        except:
            pass
    
    
    def __addTempParagraphToDocument(self, fromFile, toFile):
        try:
            tempFs = self.iceContext.fs.unzipToTempDirectory(fromFile)
            try:
                xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), self.__oOfficeNSList)
                node = xml.getNode("//office:text")
                
                #newNodeStr= """<text:p text:style-name="p"></text:p>"""
                newNode = xml.createElement("text:p")
                newNode.setAttribute("text:style-name", "p")     
                newNode.setContent("T")
                node.addChild(newNode)
                
                xml.saveFile()
                xml.close()
                
                tempFs.zip(self.iceContext.fs.absolutePath(toFile))
            finally:
                tempFs.delete()       
            return ""
        except Exception, e:
            print "Exception - '%s'" % str(e)
            return  "Invalid Open Office Document"
    
    
    def testRender(self, rep):
        self.__changes = False
    

    def __fixBookLists(self, tmpDir, bookFile):
        xmlStr = tmpDir.readFromZipFile(bookFile, "content.xml")
        xml = self.iceContext.Xml(xmlStr, self.__oOfficeNSList)

        officeNode = xml.getNode("/office:document-content")
        if officeNode.getAttribute("version")=="1.2":
            #print "__fixBookList(tmpDir='%s', bookFile='%s')" % (tmpDir, bookFile)
            #print " This is a version '1.2' office document"
            xpath = "/office:document-content/office:body/office:text//text:list"
            xpath = "/office:document-content/office:body/office:text/text:list"
            listNodes = xml.getNodes(xpath)
            count = 0
            styleNames = {}
            for listNode in listNodes:
                count += 1
                id = listNode.getAttribute("xml:id")
                if id is None:
                    listNode.setAttribute("xml:id", "list%s" % count)
                styleName = listNode.getAttribute("style-name")
                l = styleNames.get(styleName, [])
                l.append(listNode)
                styleNames[styleName] = l
            for styleName, l in styleNames.iteritems():
                #print " styleName='%s' %s" % (styleName, len(l))
                prevNode = None
                for node in l:
                    if prevNode is not None:
                        continueList = node.getAttribute("continue-list")       # xml:id
                        continueNum = node.getAttribute("continue-numbering")   # true|false
                        if continueList is None and continueNum is not None:
                            if continueNum=="true":
                                prevId = prevNode.getAttribute("xml:id")
                                node.setAttribute("text:continue-list", prevId)
                                #node.removeAttribute("continue-numbering")
                    prevNode = node

        xmlStr = str(xml)
        xml.close()
        tmpDir.addToZipFile(bookFile, "content.xml", xmlStr)


    # Optionally add page number references.  e.g. (p.45)
    def __pageRefBook(self, tmpDir, bookFile):
        xmlStr = tmpDir.readFromZipFile(bookFile, "content.xml")
        xml = self.iceContext.Xml(xmlStr, self.__oOfficeNSList)
        xpath = "/office:document-content/office:body/office:text//text:a" + \
                "[@xlink:type='simple'][starts-with(@xlink:href, '#')]"
        nodes = xml.getNodes(xpath)
        #print "len(nodes)=%s" % len(nodes)
        
        for node in nodes:
            href = node.getAttribute("href")
            content = node.content
            #print "node = %s, %s" % (content, href)
            refNode = xml.createElement("text:bookmark-ref")
            refNode.setAttribute("text:reference-format", "page")
            refNode.setAttribute("text:ref-name", href[1:])
            refNode.content = "0"
            #print str(refNode)
            t1 = xml.createText(" (p. ")
            t2 = xml.createText(") ")
            node.addNextSibling(t1)
            t1.addNextSibling(refNode)
            refNode.addNextSibling(t2)
        
        ## Testing
        #xpath = "/office:document-content/office:body/office:text"
        #node = xml.getNode(xpath)
        #print str(node)
        ## test
        
        xmlStr = str(xml)
        xml.close()
        tmpDir.addToZipFile(bookFile, "content.xml", xmlStr)
    
    
    def __getTitle(self, absFile):
        meta = self.iceContext.fs.readFromZipFile(absFile, "meta.xml")
        xml = self.iceContext.Xml(meta, self.__oOfficeNSList)
        title = ""
        node = xml.getNode("//office:meta/dc:title")
        if node!=None:
            title = node.getContent()
        xml.close()
        return title
    
    
    def __str__(self):
        s = "[BookInfo Object]\n"
        s += " relBookFile='%s'\n" % self.relBookFile
        s += " relBasePath='%s'\n" % self.relBasePath
        for doc in self.documents:
            s += "    doc.path='%s'\n" % doc.path
        return s


##    #needsUpdate(self):
##    def isUptoDate(self, rep, uptoDate=None):
##        # Note:
##        #   if uptoDate==None:  check if the book itself has changed
##        #   if uptoDate==False: just return False
##        #   if uptoData==True:  only check if dependent documents are all upto date and self is built
##        #print "plugin_bookInfo.is UptoDate(uptoDate='%s') and changes: %s and havehtml: %s" % (uptoDate, self.__changes, self.renderAsHtml)
##        item = rep.getItem(self.__relBookFile)
##        if uptoDate==False:
##            print "book is not upto date because the main book file has changed"
##            return False
##        if uptoDate is None and item.needsUpdating:
##            uptoDate = False
##        if self.__changes:
##            print "book is not upto date because of changes"
##            uptoDate = False        
##        for doc in self.__documents:
##            if doc.hasChanged(rep):
##                print "book is not upto date because book document '%s' has changed" % doc.path
##                uptoDate = False
##        if uptoDate is None:
##            uptoDate = True
##        return uptoDate











