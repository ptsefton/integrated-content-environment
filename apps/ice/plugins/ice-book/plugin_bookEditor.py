
#    Copyright (C) 2006/2008  Distance and e-Learning Centre, 
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
import sys
from file_browser import FileBrowser


pluginName = "ice.book.bookEditor"
pluginDesc = "book editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

path = None


def pluginInit(iceContext, **kwargs):
    print "-- bookEditor plugin init()"
    global pluginFunc, pluginClass, pluginInitialized
    global path
    path = iceContext.fs.split(__file__)[0]
    path = iceContext.fs.absolutePath(path)

    FileBrowser.TemplateFile = iceContext.fs.join(path, FileBrowser.TEMPLATE_FILENAME)

    pluginFunc = None
    pluginClass = BookEditor
    pluginInitialized = True
    iceContext.ajaxHandlers["bookEditor"] = ajaxCallback
    return pluginFunc


def ajaxCallback(iceContext):
    mimeType = "text/html"
    path = iceContext.path
    bookFileItem = iceContext.rep.getItemForUri(path)
    data = "<div>BookEditor Ajax result path='%s'</div>" % path
    toc = None
    requestData = iceContext.requestData
    cmd = requestData.value("cmd", "")
    arg1 = requestData.value("arg1", "")
    arg2 = requestData.value("arg2", "")
    #print "-bookEditor ajax call (cmd='%s')" % cmd
    #print "-BookEditor Ajax callback cmd='%s', arg1='%s', arg2='%s'" % (cmd, arg1, arg2)

    if cmd=="changePath":
        data = FileBrowser(iceContext).render(arg1)
    else:
        # get packageRoot
        pItem = bookFileItem
        while pItem is not None and not pItem.isPackageRoot:
            pItem = pItem.parentItem
        packageItem = pItem

        try:
            arg1i = int(arg1)
        except:
            arg1i = 0
        bookSection = BookSection(iceContext, bookFileItem, packageItem)
        if cmd=="remove":
            try:
                bookSection.removeDocument(arg1i)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="addFile":
            try:
                bookSection.insertFile(index=arg1i, relPath=arg2)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="refresh":
            pass
        elif cmd=="bookTitle":
            bookSection.setBookTitle(arg1)
            toc = bookSection.getLeftHandToc()
        elif cmd=="editBook":
            try:
                bookSection.editBook()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="renderAsHtml":
            try:
                bookSection.renderAsHtml()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="pageRef":
            try:
                bookSection.pageRef()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="pdfOnly":
            try:
                bookSection.pdfOnly()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="rebuildBook":     # feedback required
            try:
                bookSection.rebuildBook()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="renderBook":     # feedback
            try:
                bookSection.renderBook()
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="editDoc":
            try:
                bookSection.editDoc(index=arg1i)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="changePageBreakType":
            try:
                bookSection.changePageBreakType(arg1i, arg2)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="changePageOrientation":
            try:
                bookSection.changePageOrientation(arg1i, arg2)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        elif cmd=="moveDoc":
            try:
                arg2i = int(arg2)
                bookSection.moveDocument(arg1i, arg2i)
            except Exception, e:
                bookSection.message = "Error: %s" % str(e)
        else:
            bookSection.message = "Received unknown command '%s'" % cmd
        bookSection.saveBook()

        data = bookSection.render()
        if toc is not None:
            data = "<div>%s%s</div>" % (data, toc)

    return data, mimeType



class BookEditor(object):
    # BookEditor class
    #    edit()
    #    
    
    #BookInfo = None                 # Injected Data
    TEMPLATE_FILE = None
    
    def __init__(self, iceContext, formData, bookFileItem, packageItem=None):
        self.iceContext = iceContext

        #BookEditor.BookInfo = self.iceContext.getPlugin("ice.book.bookInfo").pluginClass
        BookEditor.TEMPLATE_FILE = self.iceContext.fs.join(path, "bookEditor.tmpl")
        self.__fileBrowserPath = bookFileItem.relDirectoryPath
        self.__bookSection = BookSection(iceContext, bookFileItem, packageItem)
        self.__bookSection._convertBookProp()
    
    
    def edit(self):         # Render
        #print "BookEditor.edit()"
        bookSection = self.__bookSection.render()
        fileBrowserSection = FileBrowser(self.iceContext).render(
                self.__fileBrowserPath, display=False)
        
        htmlTemplate = self.iceContext.HtmlTemplate(templateFile=self.TEMPLATE_FILE, allowMissing=True)
        dataDict = {
                    "textToHtml":self.iceContext.textToHtml,
                    "isServer":self.iceContext.isServer,
                    "bookSection":bookSection,
                    "fileBrowserSection": fileBrowserSection,
                   }
        html = htmlTemplate.transform(dataDict)
        return html
    
    






class BookSection(object):
    BookInfo = None
    BookFilesTemplate = None

    def __init__(self, iceContext, bookFileItem, packageItem=None):
        self.iceContext = iceContext
        BookSection.BookInfo = self.iceContext.getPlugin("ice.book.bookInfo").pluginClass
        BookSection.BookSectionTemplate = self.iceContext.fs.join(path, "bookSection.tmpl")
        
        fileSystem = self.iceContext.FileSystem(".")
        self.__fs = fileSystem
        self.__rep = self.iceContext.rep
        self.__fileBrowser = False
        self.__fileBrowserPath = ""
        
        self.__bookItem = bookFileItem
        self.__bookFile = bookFileItem.relPath
        self.__bookFileName = self.__fs.split(self.__bookFile)[1]
        self.__packageItem = packageItem
        self.__manifest = None
        self.__bookInfo = self.__bookItem.bookInfo
        self.__changed = False
        self.message = ""

        if packageItem is not None:
            self.__manifest = packageItem.getMeta("manifest")
        if not self.__bookItem.isFile:
            raise Exception("bookFileRelPath is not valid!")
        if self.__bookInfo is None:
            self.__bookInfo = self.BookInfo(self.iceContext, self.__bookFile)
        else:
            # update bookFile path incase it has changed
            self.__bookInfo.relBookFile = self.__bookFile


    ##
    def getLeftHandToc(self):
        packageItem = self.__packageItem
        item =  self.__bookItem
        getContextToc = self.iceContext.getPlugin("ice.contextToc").pluginFunc
        return getContextToc(self.iceContext, packageItem, item)
    ##

    def render(self):
        htmlTemplate = self.iceContext.HtmlTemplate(
                templateFile=self.BookSectionTemplate, allowMissing=True)
        docs = []
        count = 1
        for doc in self.__bookInfo.iterDocuments():
            d = self.iceContext.Object()
            d.count = count
            d.name = self.iceContext.getRelativeLink(self.__bookFile, doc.path)
            d.title = d.name
            #
            dItem = self.iceContext.rep.getItem(doc.path)
            if dItem is not None and self.__manifest is not None:
                mItem = self.__manifest.getManifestItem(dItem.guid)
                if mItem is not None:
                    if mItem.manifestTitle is not None:
                        d.title = mItem.manifestTitle
                    else:
                        d.title = mItem.title
                else:
                    title = dItem.getMeta("title")
                    if title is not None and title!="":
                        d.title = title
            d.title = self.iceContext.cleanUpString(d.title)
            d.pageBreakType = doc.pageBreakType
            d.pageOrientation = doc.pageOrientation
            d.missing = doc.isMissing(self.__rep)
            docs.append(d)
            count += 1
        
        renderAsHtml = self.__bookInfo.renderAsHtml
        pageRef = self.__bookInfo.pageRef
        if not renderAsHtml and not pageRef:
            pdfOnly = True
            self.__bookInfo.pdfOnly = pdfOnly
        pdfOnly = self.__bookInfo.pdfOnly
        pdfLink = self.__fs.splitExt(self.__bookFile)[0] + ".pdf"
        htmlLink = self.__fs.splitExt(self.__bookFile)[0] + ".htm"
        bookUri = self.__fs.join(self.iceContext.urlRoot, self.__bookFile[1:])
        if self.iceContext.isServer:
            bookUri = self.__fs.split(bookUri)[0]
            bookUri = self.__fs.join(bookUri, self.__bookItem.getIdUrl())
        title = self.iceContext.cleanUpString(self.getBookTitle())
        
        dataDict = {
                    "textToHtml":self.iceContext.textToHtml,
                    "message":self.message,
                    "isServer":self.iceContext.isServer,
                    "bookFileName":self.__bookFileName,
                    "pdfLink":pdfLink,
                    "htmlLink":htmlLink,
                    "docs":docs,
                    "title":title,
                    "bookFile":self.__bookFile,
                    "bookUri":bookUri,
                    "renderAsHtml":renderAsHtml,
                    "pdfOnly":pdfOnly,
                    "pageRef":pageRef,
                    "needsBuilding":self.__bookInfo.needsBuilding,
                    "needsRendering":self.__bookInfo.needsRendering,
                   }

        html = htmlTemplate.transform(dataDict)
        return html


    def renderAsHtml(self):
        self.__bookInfo.renderAsHtml = True
        self.__bookInfo.pageRef = False
        self.__bookInfo.pdfOnly = False
        self.__changed = True

    def pageRef(self):
        self.__bookInfo.pageRef = True
        self.__bookInfo.renderAsHtml = False
        self.__bookInfo.pdfOnly = False
        self.__changed = True

    def pdfOnly(self):
        self.__bookInfo.pdfOnly = True
        self.__bookInfo.renderAsHtml = False
        self.__bookInfo.pageRef = False
        self.__changed = True

    def rebuildBook(self):
        #print "rebuildBook"
        try:
            msg = self.__bookInfo.buildBook()
            if msg!="":
                self.message = msg
                print "Error: One or more of the documents may be empty"
                print "  message='%s'" % msg
            else:
                print "Success in building book"
        except Exception, e:
            self.message = "Error: Make sure the book is not opened or locked by other process"
            print self.message
            print "  exception message='%s'" % str(e)
            err = self.iceContext.formattedTraceback()
            print "Traceback error: ", err

    def renderBook(self):
        #print "*** renderBook ***"
        self.__bookItem.render(force=False, skipBooks=False)
        # Need to update bookInfo because it gets recreated from pickled data (not the same object)
        self.__bookInfo = self.__bookItem.bookInfo
        #print " done rendering book"

    def editBook(self):
        if self.iceContext.isServer:
            # Download
            print "editBook - download (server)"
        else:
            absFilePath = self.__bookItem._absPath
            self.__EditFile(absFilePath)
    
    def changePageOrientation(self, index, pageOrientation):
        doc = self.__bookInfo.documents[index - 1]
        #print "Changed pageOrientation='%s' " % (pageOrientation)
        doc.pageOrientation = pageOrientation
        self.__bookInfo.touch()
        self.__changed = True
    
    def changePageBreakType(self, index, pageBreakType):
        doc = self.__bookInfo.documents[index - 1]
        #print "Changed pageBreakType='%s' path='%s'" % (pageBreakType, doc.path)
        doc.pageBreakType = pageBreakType
        self.__bookInfo.touch()
        self.__changed = True

    def editDoc(self, index):
        doc = self.__bookInfo.documents[index - 1]
        #data = doc.path.strip("/")
        #absFilePath = self.__rep.getAbsPath(self.__bookFile)
        #if data!="":
        #    absPath = self.__fs.split(absFilePath)[0]
        #    absFilePath = self.__fs.join(absPath, data)
        absFilePath = self.__rep.getAbsPath(doc.path)
        self.__EditFile(absFilePath)

    def insertFile(self, relPath, index=9999):
        url = self.__fs.splitExt(relPath)[0] + ".htm"
        self.__bookInfo.insertDocument(index-1, relPath, url)
        if index>9990: index = -1
        doc = self.__bookInfo.documents[index]
        #doc.makeRelative(self.__bookInfo.relBasePath, "")
        self.__changed = True

    def removeDocument(self, index):
        self.__bookInfo.removeDocument(index-1)
        self.__changed = True

    def moveDocument(self, index, insertBeforeIndex=9999):
        self.__bookInfo.moveDocument(index-1, insertBeforeIndex-1)
        self.__changed = True

    def getBookTitle(self):
        title = None
        if self.__manifest is not None:
            mItem = self.__manifest.getManifestItem(self.__bookItem.guid)
            if mItem is not None and mItem.manifestTitle is not None:
                title = mItem.manifestTitle
        if title is None:
            title = self.__bookItem.getMeta("title")
            if title is None:
                title = "[Untitled] '%s'" % self.__bookFileName
        return title

    def setBookTitle(self, title):
        if self.__manifest is not None:
            mItem = self.__manifest.getManifestItem(self.__bookItem.guid)
            if mItem is None:
                self.__manifest.updateItems(self.__packageItem)
                mItem = self.__manifest.getManifestItem(self.__bookItem.guid)
            if mItem is not None:
                if mItem.manifestTitle != title:
                    mItem.manifestTitle = title
                    self.__packageItem.flush(True)  # to save the changes to the manifest
        self.__bookItem.setMeta("title", title)
        self.__bookItem.flush()
        self.__changed = True
        self.saveBook()

    def saveBook(self):
        if self.__changed:
            #print "Book changed"
            self.__bookInfo._save(self.__bookItem)

    
    def __EditFile(self, absFilePath):
        appsExts = {}
        if self.iceContext.system.isLinux:
            oooPath = self.iceContext.settings.get("oooPath")
            soffice = "soffice"
            if oooPath!="":
                soffice = self.iceContext.url_join(oooPath, "program", soffice)
            appsExts = {soffice:[self.iceContext.oooDefaultExt, self.iceContext.wordExt, \
                                self.iceContext.oooMasterDocExt, self.iceContext.bookExts, \
                                self.iceContext.word2007Ext, self.iceContext.wordDotExt]}
        self.iceContext.system.startFile(absFilePath, appsExts=appsExts)


    def _convertBookProp(self):
        #convert old book(v 1.2) svn property to new book property (v 2.0)
        class bookInfo1_2(object):
            def __init__ (self):
                self.bookInfo = bookInfo1_2
                self.bookDocument = bookInfo1_2
        sys.modules["book_info"] = bookInfo1_2()
        svnBookProp = self.__rep.getSvnProp("meta-bookInfo", self.__rep.getAbsPath(self.__bookFile))
        if svnBookProp is None:
            return False
        else:
            #if have 2.0 property, delete 1.2 prop if exist
            newBookProp = self.__rep.getItem(self.__bookFile)
            if newBookProp.bookInfo is None:
                title = self.__rep.getSvnProp("meta-title", self.__rep.getAbsPath(self.__bookFile))
                if title is None:
                    title="Untitled"
                newProp = self.BookInfo(self.iceContext, self.__bookFile)
                newProp._BookInfo__setBookTitle(title)

                newProp._BookInfo__relBasePath = svnBookProp._bookInfo__relBasePath
                newProp._BookInfo__setRelBookFile(svnBookProp._bookInfo__relBookFile)
                if svnBookProp._bookInfo__changes:
                    newProp._BookInfo__changes = svnBookProp._bookInfo__changes
                else:
                    newProp._BookInfo__changes = True
                renderAsHtml = svnBookProp._bookInfo__renderAsHtml
                newProp._BookInfo__setRenderAsHtml(renderAsHtml)
                pageRef = False
                try:
                    #not all v1.2 book has these
                    pageRef = oldBook._bookInfo__pageRef
                except:
                    pass

                if not renderAsHtml and not pageRef:
                    newProp._BookInfo__setPdfOnly(True)
                else:
                    newProp._BookInfo__setPdfOnly(False)

                newProp._BookInfo__setPageRef(pageRef)
                newProp._BookInfo__tempDir = None

                newProp._BookInfo__documents = []
                for doc in svnBookProp._bookInfo__documents:
                    path = doc._bookDocument__path
                    url = doc._bookDocument__url
                    md5=""
                    pageBreakType=""
                    pageOrientation =""
                    try:
                        md5 = doc._bookDocument__md5
                        pageBreakType = doc._bookDocument__pageBreakType
                        pageOrientation = doc._bookDocument__pageOrientation
                    except:
                        pass
                    newDoc = newProp.BookDocument(path, url)
                    newDoc._BookDocument__setMd5(md5)
                    newDoc._BookDocument__setPageBreakType(pageBreakType)
                    newDoc._BookDocument__setPageOrientation(pageOrientation)
                    newProp._BookInfo__documents.insert(9999, newDoc)

                ####
                item = self.__rep.getItem(self.__bookFile)
                item.flush()
                item.setBookInfo(newProp)
                item.close()
                self.__bookItem = self.__rep.getItem(self.__bookFile)           ####
                self.__bookInfo = self.__bookItem.bookInfo
                ####
            else:
                pass
            #delete the old svn prop




