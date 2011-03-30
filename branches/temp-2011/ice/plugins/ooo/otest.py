#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

import socket
import os, sys, time, re
import types
from cStringIO import StringIO
#sys.path.append("/usr/lib/openoffice/program/")    # for testing only

if sys.platform == "darwin":
    if os.path.exists("/Applications/OpenOffice.org.app/Contents/program/fundamentalrc") and \
            os.getenv('URE_BOOTSTRAP') is not None and \
            os.getenv('DYLD_LIBRARY_PATH') is not None:
        sys.path.insert(0, "%s/py25-pyuno-macosx" % os.path.split(__file__)[0])

## BUG - (Windows only) on OpenOffice.org 3.0.0 only
## The following environment variable must be set as a work around
## set URE_BOOTSTRAP=file:///C:/Program%20Files/OpenOffice.org%203/program/fundamental.ini

import uno

from unohelper import Base, absolutize, systemPathToFileUrl
from com.sun.star.io import XOutputStream, IOException
from com.sun.star.beans import PropertyValue
#from com.sun.star.text import XTextFieldsSupplier, XBookmarksSupplier   # interfaces
# values for the property "UpdateDocMode"
from com.sun.star.document.UpdateDocMode import NO_UPDATE, QUIET_UPDATE, ACCORDING_TO_CONFIG, FULL_UPDATE
# value for the property "MacroExecMode"
from com.sun.star.document.MacroExecMode import NEVER_EXECUTE, FROM_LIST, ALWAYS_EXECUTE, USE_CONFIG, ALWAYS_EXECUTE_NO_WARN, USE_CONFIG_REJECT_CONFIRMATION, USE_CONFIG_APPROVE_CONFIRMATION, FROM_LIST_NO_WARN, FROM_LIST_AND_SIGNED_WARN, FROM_LIST_AND_SIGNED_NO_WARN
from com.sun.star.uno import Exception as UnoException
from com.sun.star.connection import NoConnectException
from com.sun.star.lang import IllegalArgumentException

from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, NONE, PAGE_BOTH



####################################################
#soffice "-accept=socket,host=localhost,port=2002;urp;"
#soffice "-accept=pipe,name=pypipe;urp;StarOffice.ServiceManager"     ## Pipe
####################################################


class OutputStream(Base, XOutputStream):
    def __init__(self):
        self.closed=0
    def closeOutput(self):
        self.closed = 1
    def writeBytes(self, seq):
        sys.stdout.write(seq.value)
    def flush(self):
        sys.stdout.flush()

class DataOutputStream(Base, XOutputStream):
    def __init__(self):
        self.__data = ""
        self.closed=0
    def closeOutput(self):
        self.closed = 1
    def writeBytes(self, seq):
        self.__data += seq.value
    def flush(self):
        pass
    def getData(self):
        return self.__data

class _DataClass(object):
    def __str__(self):
        s = "[_DataClass object]"
        for k, v in self.__dict__.iteritems():
            s += "\n  %s = %s" % (k, v)
        return s

class OoObject(object):
    def __init__(self, ooPort=2002, ooHost="localhost", pipeName="oooPyPipe", \
                DataClass=None, stdOut=None, stdErr=None):
        startTime = time.time()
        if DataClass is None:
            DataClass = _DataClass
        self.DataClass = DataClass
        self.stdOut = stdOut
        self.stdErr = stdErr
        #self.writelnError("ooo_automate init start")
        connectString = "uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext"
        connectString = connectString % (ooHost, ooPort)
        pipeConnectString = "uno:pipe,name=%s;urp;StarOffice.ComponentContext" % pipeName
        
        desktop = "com.sun.star.frame.Desktop"
        self.__ooPort = ooPort
        self.__ooHost = ooHost
        self.__pipeName = pipeName
        self.__ctx = None
        self.__doc = None
        try:
            # get the uno component context from the PyUNO runtime
            self.__localContext = uno.getComponentContext()
            # create UnoUrlResolver
            self.__resolver = self.__localContext.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", self.__localContext)
        except Exception, e:
            msg = str(e)
            raise Exception("OOo setup error: '%s'" % msg)
        try:
            # connect to the running office
            try:
                self.__ctx = self.__resolver.resolve(pipeConnectString)
            except NoConnectException, e:
                # Try again using a named socket instead
                self.__ctx = self.__resolver.resolve(connectString)
        except NoConnectException, e:
            raise Exception("OpenOffice process not found or not listening (%s)" % str(e))
        except IllegalArgumentException, e:
            raise Exception("The url is invalid (%s)" % str(e))
        except Exception, e:
            raise Exception("An unknown error occured: %s" % str(e))
        try:
            self.__smgr = self.__ctx.ServiceManager
            # get the centrol desktop object
            self.__desktop = self.__smgr.createInstanceWithContext(desktop, self.__ctx)
        except Exception, e:
            msg = str(e)
            raise Exception("OOo error creating instance with context. '%s'" % msg)
        #self.__doc = self.__desktop.getCurrentComponent()  #NOTE: this must not be disposed!
        self.__doc = None
        self.__text = None
        self.__cursor = None
        self.__viewCursor = None
        self.__search = None
        try:
            self.__text = self.__doc.Text
            self.__cursor = self.__text.createTextCursor()
        except:
            pass
        #self.writelnError("ooo_automate init finish %s" % (time.time() - startTime))
    
    def __del__(self):
        self.delete()
    
    def delete(self):
        self.close()
        # In case the last call is a oneway call, it must be forced out of the remote-bridge
        # caches before python exits the process.  Otherwise, the oneway call may or may not 
        # reach the target object.
        # It is done here with a cheap synchronous call (getPropertyValue).
        if self.__ctx is not None:
            self.__ctx.ServiceManager
            self.__ctx = None
    
    def close(self):
        self.__viewCursor = None
        self.__cursor = None
        self.__text = None
        self.setDoc(None)
        self.__doc = None
    
    #def getCurrentDocument(self):
    #    self.setDoc(self.__desktop.getCurrentComponent())  #NOTE: this must not be disposed!

    def setDoc(self, doc):
        if self.__doc is not None:
            #if self.__doc != self.__desktop.getCurrentComponent():
            #    #self.__doc.close(True)
            self.__doc.dispose()
        self.__doc = doc
        if doc is not None:
            try:
                self.__text = self.__doc.Text
                self.__cursor = self.__text.createTextCursor()
            except Exception:
                self.__text = None
                self.__cursor = None
        self.__viewCursor = None
        self.__search = None
    def getDoc(self):
        return self.__doc
    doc = property(getDoc)

    def getText(self):
        return self.__text
    text = property(getText)
    
    def getTextString(self):
        return self.__text.String
    textString = property(getTextString)

    def __getCursor(self):
        return self.__cursor
    def __setCursor(self, cursor):
        self.__cursor = cursor
    cursor = property(__getCursor, __setCursor)

    def __getViewCursor(self):
        if self.__viewCursor is None:
            vc = self.__doc.getCurrentController().getViewCursor()
            self.__viewCursor = vc
        return self.__viewCursor
    viewCursor = property(__getViewCursor)
    
    def __getPageNum(self):
        vc = self.viewCursor
        vc.gotoRange(self.__cursor, False)
        return vc.Page
    pageNumber = property(__getPageNum)

    def __getCursorString(self):
        return self.__cursor.String
    def __setCursorString(self, value):
        self.__cursor.String = value;
    cursorString = property(__getCursorString, __setCursorString)
    string = property(__getCursorString, __setCursorString)
    
    def createNewCursor(self):
        self.__cursor = self.__text.createTextCursor()
    
    def setViewCursorToCursor(self):
        # set the viewCursor to point at the same location (or range) as the cursor
        self.viewCursor.gotoRange(self.__cursor, False) 

    def getWordCount(self):
        return self.__doc.WordCount

    def getParagraphCount(self):
        return self.__doc.ParagraphCount

    def updateLinks(self):
        self.__doc.updateLinks()

    def reformat(self):
        self.__doc.reformat()

    def addText(self, text="-Hello World-", capture=False):
        # insert the text into the document
        self.__text.insertString(self.__cursor, text, capture)
    
    
    def getLastText(self, count=1):
        self.__cursor.gotoEnd(False)
        self.__cursor.goLeft(count, True)
        r = self.__cursor.String
        self.__cursor.gotoEnd(False)
        return r
    
    def createEnumeration(self):
        return self.__text.createEnumeration()
    
    def getParagraphs(self):
        e = self.createEnumeration()
        l = []
        while e.hasMoreElements():
            l.append(e.nextElement())
        return l
    
    def getLastParagraph(self):
        paras = self.getParagraphs()
        if paras==[]:
            return None
        else:
            return paras.pop()
        
    
    def setCursorToDefaultFormatting(self):
        """ sets the cursor location or cursor range to the default formatting """
        self.__cursor.setAllPropertiesToDefault()
    
    def getPageNumberForCursor(self):
        self.setViewCursorToCursor()
        page = self.viewCursor.Page
        return page
    
    # Cursor control
    def gotoEnd(self, capture=False):
        self.__cursor.gotoEnd(capture)

    def gotoStart(self, capture=False):
        self.__cursor.gotoStart(capture)

    def goLeft(self, count=1, capture=False):
        self.__cursor.goLeft(count, capture)

    def goRight(self, count=1, capture=False):
        self.__cursor.goRight(count, capture)

    def createCursorContentEnumeration(self):
        return self.__cursor.createContentEnumeration()

    def gotoRange(self, cursor, capture=False):
        self.__cursor.gotoRange(cursor, capture)
    def collapseToEnd(self):
        self.__cursor.collapseToEnd()
    def collapseToStart(self):
        self.__cursor.collapseToStart()
    def isCursorCollapsed(self):
        return self.__cursor.isCollapsed()

    # word
    def gotoEndOfWord(self, capture=False):
        self.__cursor.gotoEndOfWord(capture)
    def gotoStartOfWord(self, capture=False):
        self.__cursor.gotoStartOfWord(capture)
    def gotoNextWord(self, capture=False):
        self.__cursor.gotoNextWord(capture)
    def gotoPreviousWord(self, capture=False):
        self.__cursor.gotoPreviousWord(capture)
    def isEndOfWord(self):
        return self.__cursor.isEndOfWord()
    def isStartOfWord(self):
        return self.__cursor.isStartOfWord()
    # sentence
    def gotoEndOfSentence(self, capture=False):
        self.__cursor.gotoEndOfSentence(capture)
    def gotoStartOfSentence(self, capture=False):
        self.__cursor.gotoStartOfSentence(capture)
    def gotoNextSentence(self, capture=False):
        self.__cursor.gotoNextSentence(capture)
    def gotoPreviousSentence(self, capture=False):
        self.__cursor.gotoPreviousSentence(capture)
    def isEndOfSentence(self):
        return self.__cursor.isEndOfSentence()
    def isStartOfSentence(self):
        return self.__cursor.isStartOfSentence()
    # paragraph
    def gotoEndOfParagraph(self, capture=False):
        self.__cursor.gotoEndOfParagraph(capture)
    def gotoStartOfParagraph(self, capture=False):
        self.__cursor.gotoStartOfParagraph(capture)
    def gotoNextParagraph(self, capture=False):
        self.__cursor.gotoNextParagraph(capture)
    def gotoPreviousParagraph(self, capture=False):
        self.__cursor.gotoPreviousParagraph(capture)
    def isEndOfParagraph(self):
        return self.__cursor.isEndOfParagraph()
    def isStartOfParagraph(self):
        return self.__cursor.isStartOfParagraph()
    
    
    def readFromCursor(self, numOfCharToRead=1):
        s = ""
        c = self.__cursor
        self.createNewCursor()
        self.gotoRange(c)
        for x in range(numOfCharToRead):
            self.goRight(1, True)
            s += self.cursorString
            self.collapseToEnd()
        self.__cursor = c
        return s
    
    
    def addBookmark(self, bookmarkName):
        bookmark = self.__doc.createInstance("com.sun.star.text.Bookmark")
        bookmark.Name = bookmarkName
        self.__text.insertTextContent(self.__cursor, bookmark, True)
    

    def deleteBookmark(self, bookmarkName):
        bookmarks = self.__doc.getBookmarks()
        if bookmarks.hasByName(bookmarkName):
            bookmark = bookmarks.getByName(bookmarkName)
            bookmark.dispose()
    
    
    def getCursorForBookmark(self, bookmarkName):
        bookmarks = self.__doc.getBookmarks()
        if bookmarks.hasByName(bookmarkName):
            bookmark = bookmarks.getByName(bookmarkName)
            r = bookmark.getAnchor()
            self.cursor = r.Text.createTextCursorByRange(r)
            return True
        else:
            return False
    
    
    def gotoBookmark(self, bookmarkName, capture=False):
        if capture:
            c = self.__cursor
        if self.getCursorForBookmark(bookmarkName):
            if capture:
                self.gotoRange(c, True)
            return True
        else:
            return False
    
    
    def getPageNumberForBookmark(self, bookmarkName):
        c = self.cursor
        self.getCursorForBookmark(bookmarkName)
        self.setViewCursorToCursor()
        page = self.viewCursor.Page
        self.cursor = c
        return page
    
    
    # Note: The viewcursor only works if the document is viewable! (displayed)
    def copyAll(self):
        self.gotoStart()
        self.setViewCursorToCursor()
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        props = ()
        #dispatcher.executeDispatch(frame, ".uno:SelectAll", "", 0, props)
        #dispatcher.executeDispatch(frame, ".uno:SelectAll", "", 0, props)
        #dispatcher.executeDispatch(frame, ".uno:SelectAll", "", 0, props)
        dispatcher.executeDispatch(frame, ".uno:SelectAll", "", 0, props)
        dispatcher.executeDispatch(frame, ".uno:Copy", "", 0, props)
    
    
    # Note: The viewcursor only works if the document is viewable! (displayed)
    def paste(self):
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        props = ()
        dispatcher.executeDispatch(frame, ".uno:Paste", "", 0, props)
    
    
    def insertPara(self):
        self.addText("\r")
    
    
    def insertParaOld(self):
        #dispatcher.executeDispatch(document, ".uno:InsertPara", "", 0, Array())
        
        # Note: uses the viewCursor
        # set the viewCursor to point at the same location (or range) as the cursor
        self.viewCursor.gotoRange(self.__cursor, False) 
        
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        props = ()
        dispatcher.executeDispatch(frame, ".uno:InsertPara", "", 0, props)
    
    
    def updateFields(self):
        #dispatcher = self.__createDispatchHelper()
        #frame = self.__doc.getCurrentController().getFrame()
        #props = ()
        #dispatcher.executeDispatch(frame, ".uno:UpdateFields", "", 0, props)
        self.__doc.TextFields.refresh()
    
    
    def updateAll(self):
        # Same as reindexAll
        #self.reindexAll()
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        props = ()
        dispatcher.executeDispatch(frame, ".uno:UpdateAll", "", 0, props)
    
    
    # draft
    def insertPageBreak(self):
        # Note: uses the viewCursor
        # set the viewCursor to point at the same location (or range) as the cursor
        self.viewCursor.gotoRange(self.__cursor, False) 
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        props = ( PropertyValue("Kind", 0, 3, 0),
                    PropertyValue("TemplateName", 0, "", 0),
                    PropertyValue("PageNumber", 0, 0, 0)
                )
        dispatcher.executeDispatch(frame, ".uno:InsertBreak", "", 0, props)
    
    
    def insertPageBreak2(self):
        # NOTE: this always inserts the page break before the last current content (NOT what we want!)
        for elem in self.__enum(self.__cursor):
            if hasattr(elem, "createEnumeration"):
                e2 = elem.createEnumeration()
                if e2.hasMoreElements():
                    i = e2.nextElement()
                    if hasattr(i, "BreakType"):
                        i.BreakType = PAGE_BEFORE
    
    
    def enum(self, obj=None):
        if obj==None:
            obj = self.__cursor
        return self.__enum(obj)
    
    
    # draft
    def reindexCursorRange(self):
        # using the view cursor I guess?
        self.viewCursor.gotoRange(self.__cursor, False) 
        dispatcher = self.__createDispatchHelper()
        frame = self.__doc.getCurrentController().getFrame()
        dispatcher.executeDispatch(frame, ".uno:UpdateCurIndex", "", 0, tuple())
    

    def reindexAll(self):
        startTime = time.time()
        # This works but may be causing a problem when used with math types
        #self.writelnError( "ooo_automate reindexAll")
        frame = self.__doc.getCurrentController().getFrame()
        dispatcher = self.__createDispatchHelper()
        dispatcher.executeDispatch(frame, ".uno:UpdateAll", "", 0, ())
        #self.writelnError( "ooo_automate reindexAll finish %s" % (time.time() - startTime))
    
    def reindexAll2(self):
        return self.reindexFieldsAndIndexes()
    def reindexFieldsAndIndexes(self):
        self.__doc.TextFields.refresh()
        
        docIndexes = self.__doc.DocumentIndexes
        for x in range(docIndexes.Count):
            index = docIndexes.getByIndex(x)
            index.update()
    

    def regexSearch(self, pattern):
        search = self.__doc.crateSearchDescriptor()
        search.SearchRegularExpression = True
        search.SearchString = pattern
        self.__search = search
        found = self.__doc.findFirst(search)   # findNext(), findAll()
        if found:
            self.Cursor = found.Text.createCursorByRange(found)
            return True
        else:
            return False
    

    def findNext(self):
        found = self.__doc.findNext(self.__search)
        if found:
            self.Cursor = found.Text.createCursorByRange(found)
            return True
        else:
            return False
    
    
    def regexSearchAndReplaceAll(self, pattern, replacementText):
        search = self.__doc.crateSearchDescriptor()
        search.SearchRegularExpression = True
        search.SearchString = pattern
        matches = self.__doc.findAll(search)
        for found in matches:
            cursor = found.Text.createCursorByRange(found)
            cursor.String = replace    
    

    def createNewDocument(self, visible=False):
        inProps = tuple()
        #inProps = self.__getInProperties()
        # for a Bibliography factory use ".component:Bibliography/View1"
        # Target Frame = "_blank" -> Creates a new top-level frame as a child frame of the desktop
        l = [ ("MacroExecutionMode", 0, ALWAYS_EXECUTE_NO_WARN, 0) ]
        if visible==False:
            l.append( ("Hidden", 0, True, 0) )
        inProps = self.__getProps(l)   
        doc = self.__desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, inProps)
        self.setDoc(doc)
    
    
    def loadDocument(self, fromFile, visible=False):
        startTime = time.time()
        #self.writelnError( "ooo_automate loadDocumnent %s" % fromFile)
        doc = None
        fromFileUrl = self.__pathToUrl(fromFile)
        inProps = self.__getInProperties()
        if visible:
            inProps = inProps[1:]
        try:
            doc = self.__desktop.loadComponentFromURL(fromFileUrl, "_blank", 0, inProps)
            if not(doc):
                raise UnoException(
                    "Couldn't open input steam '%s' for an unknown reason" % fromFileUrl, None)
        except IOException, e:
            msg = str(e)
            raise Exception("ERROR: IO Error during conversion: %s" % msg)
        except UnoException, e:
            msg = str(e)
            raise Exception("ERROR: Error(%s) during loading: %s" % (e.__class__, msg))
        self.setDoc(doc)
        #self.writelnError( "done ooo_automate loadDocument %s %s" % (fromFile, (time.time() - startTime)))
        return True
    

    def saveDocument(self, toFile=None, toExt=None, outputStream=None):
        startTime=time.time()
        #self.writelnError( "ooo_automate saveDocument %s" % toFile)        
        result = self.DataClass()
        result.allOk = False
        result.binaryData = None
        
        if toExt is None or not(toExt.startswith(".")):
            if toFile is not None:
                toExt = os.path.splitext(toFile)[1]
            else:
                toExt = ".htm"
        if toFile is None:
            toFileUrl = "private:stream"
        else:
            toFileUrl = self.__pathToUrl(toFile)
        filterName, filterMsg = self.__getFliterName(toExt)
        result.filterName = filterName
        result.filterMsg = filterMsg
        if outputStream is None:
#            #####Original######
#            This bits being modified to fix page style problem when converting from
#            word document to open office document
#            if toFile is None:
#                outputStream = DataOutputStream()
#            else:
#                outputStream = OutputStream()       # Writes to sys.stdout
            outputStream = OutputStream()       # Writes to sys.stdout
        outProps = self.__getOutProperties(filterName, outputStream)
        if False:
            l = [   ("FilterName", 0, filterName, 0), ("Overwrite", 0, True, 0), \
                    ("OutputStream", 0, outputStream, 0), \
                    ("Unpacked", 0, True, 0), \
                ]
            outProps = self.__getProps(l)
        try:
            try:
                self.__doc.storeToURL(toFileUrl, outProps)
                result.allOk = True
            except UnoException, e:
                msg = "ERROR: UNO Execption (%s) during saving to '%s': %s"
                msg = msg % (e.__class__.__name__, toFileUrl, str(e))
                result.exception = Exception("UNO Exception")
                result.errorMessage = msg
                result.allOk = False
                #raise Exception(msg)
            except IOException, e:
                msg = "ERROR: IO Error during saving: %s" % str(e)
                result.exception = e
                result.errorMessage = msg
                result.allOk = False
                #raise Exception(msg)
        finally:
            outputStream.flush()
        if result.allOk and hasattr(outputStream, "getData"):
            result.binaryData = outputStream.getData()
        #self.writelnError( "done ooo_automate saveDocument %s %s" % (toFile, (time.time() - startTime)))
        return result
    
    
    def insertDocument(self, insertDocFile):
        startTime = time.time()
        #self.writelnError( "ooo_automate insertDocument %s " % insertDocFile)
        insertFileUrl = self.__pathToUrl(insertDocFile)
        try:
            #self.__cursor.BreakType = PAGE_BEFORE     #PAGE_BEFORE, NONE
            self.__cursor.insertDocumentFromURL(insertFileUrl, ())
            #self.writelnError( "ooo_automate insertDocument %s %s" % (insertDocFile, (time.time() - startTime)))
        except IOException, e:
            raise Exception("Error during opening (%s)" % str(e))
        except IllegalArgumentException, e:
            raise Exception("The rul is invalid (%s)" % str(e))
        except UnoException, e:
            raise Exception("Error (%s) during conversion: %s" % (e.__class__, str(e)))
    
    
    # Note: The viewcursor only works if the document is viewable! (displayed)
    def pasteDocument(self, docFile):
        o = OoObject(self.__ooPort, self.__ooHost, self.__pipeName)
        o.loadDocument(docFile, True)
        o.copyAll()
        self.paste()
        o.close()
        o = None
    
    
    def convert(self, fromFile, toFile=None, toExt=None):
        messages = []
        result = False
        try:
            result = self.loadDocument(fromFile)
        except Exception, e:
            messages.append(str(e))
        if result==True:
            messages.append("Loaded Document OK")
            try:
                result, filterMsg = self.saveDocument(toFile, toExt)
                #messages.append(filterMsg)
                messages.append("Converted OK")
            except Exception, e:
                result = False
        return result, messages

    
    def enumerateAllLinksInCursorRange(self):
        for elem in self.__enum(self.__cursor):
            for subElem in self.__enum(elem):
                if subElem.HyperLinkURL != "":
                    yield subElem
    
    
    def enumerateAllBookmarksInCursorRange(self):
        elems=[]
        subElems=[]
        startTime=time.time()
        for elem in self.__enum(self.__cursor):
            elems.append(elem)
        #self.writelnError("FINISH self.__enum(self.cursor) %s" % (time.time()-startTime))
        
        startTime=time.time()
        
        for elem in self.__enum(self.__cursor):
            for subElem in self.__enum(elem):
                bookmark = subElem.Bookmark
                if bookmark is not None:
                    yield bookmark        # bookmark.Name (property)
        #self.writelnError("FINISH self.__enum(elem) %s" % (time.time()-startTime))
    
    
    def enumerateAllXInCursorRange(self, property):
        for elem in self.__enum(self.__cursor):
            for subElem in self.__enum(elem):
                x = getattr(subElem, property)
                if x is not None:
                    yield x
    
    
    def removePageBreakAtCursor(self):
        self.removePageBreaksInCursorRange()
    def removePageBreaksInCursorRange(self):
        for elem in self.__enum(self.__cursor):
            for subElem in self.__enum(elem):
                subElem.BreakType = NONE
    
    
    def removeAllLinkedImages(self):
        removedLinkedImages = 0
        gr = self.doc.Links.Graphics
        for gName in gr.ElementNames:
            g = gr.getByName(gName)
            if g.GraphicURL.startswith("file:///"):
                g.dispose()
                removedLinkedImages += 1
        return removedLinkedImages
    
    
    def addBlankPageBefore(self):
        c = self.cursor
        self.createNewCursor()
        self.gotoRange(c)
        self.goLeft(1)
        self.setCursorToDefaultFormatting()
        #self.addText(" \r--BlankPage--")
        self.addText(" \r    ")
        self.__cursor.BreakType = PAGE_BEFORE
        self.cursor = c
    
    
    def testBook(self, title=None):
        book = "bookTestData/default.book.odt"
        one = ("bookTestData/one.odt", "bookTestData/one.htm", {"InsertPageBreak":True, "Page":"Odd"})
        two = ("bookTestData/two.odt", "bookTestData/two.htm", {"InsertPageBreak":True, "Page":"Odd"})
        three = ("bookTestData/three.odt", "bookTestData/three.odt", {"InsertPageBreak":True})
        title="BuildBook"
        urlBookmarks = self.buildBook2(book, [one, two, three], title, visible=True)
        self.saveDocument(book, toExt=".odt")
    
    
    def testReIndex (self):
        book = "C:/workspace/apps/ice/plugins/ooo/bookTestData/default.book.odt"        
        self.loadDocument(book, visible=False)
        self.reindexAll2()
        self.saveDocument(book, toExt=".odt")
    
    
    def buildBook2(self, baseBookDocument, bookDocumentsPathUrl=[], baseUrl="http://localhost",
                       title=None, visible=False):
        useCopyAndPaste=False
        if useCopyAndPaste:
            visible=True
        
        #self.writelnError( "BuildBOOK 2 FUNCTION"    )
        endOfTemplateBookmark = "_end_of_template_"
        self.loadDocument(baseBookDocument, visible)
        
        startTime=time.time()
        found = self.gotoBookmark(endOfTemplateBookmark)
        if found:
            # Get the first document's page style
            self.gotoNextParagraph()
            pageStyle = self.cursor.PageDescName
            #
            self.gotoBookmark(endOfTemplateBookmark)
            self.goRight(1)
            self.gotoEnd(True)
            self.cursorString = ""
        else:
            # Get page style
            pageStyle = "Standard"
            self.gotoEnd()
            self.gotoStartOfParagraph()
            data = self.readFromCursor(20)
            if data.lower()=="--newpagestyle--" or data=="":
                pageStyle = self.cursor.PageDescName
                self.gotoPreviousParagraph()
                self.gotoEndOfParagraph()
                self.gotoEnd(True)
            else:
                self.gotoEnd()
            
            self.cursorString = " "
            self.gotoEnd()
            self.goLeft(1)
            self.addBookmark(endOfTemplateBookmark)
        if pageStyle is None:
            pageStyle = "Standard"      # Default
        
        urls = []
        docs = []
        oriDocs = {}
        
        count=1
        for path, ori, url, props in bookDocumentsPathUrl:
            #self.writelnError ("path=%s, ori=%s, url=%s, props=%s" % (path, ori, url, props))
            urls.append(url)
            docs.append((path, props))
            dir (os.path)
            oriDocs[os.path.split(path)[1]] = [os.path.split(ori)[1], count, ori]
            count+=1
        bookmarkNames = {}
        #self.writelnError ("DOCS in buildbook2: %s, oriDocs=%s, urls=%s" % (docs, oriDocs, urls))
        
        links = []
        urlBookmarks = {}       # {url:{oldBookmarkName:newBookmarkName}, ...}
        for url in urls:
            urlBookmarks[url] = {}
            #self.writelnError ("urlBookmarks[url]: " % urlBookmarks)
        
        self.gotoEnd()
#        pageNum = self.getPageNumberForCursor()
#        if pageNum % 2:
#            self.setCursorToDefaultFormatting()
#            self.insertPara()
#            self.gotoEnd()
#            self.__cursor.BreakType = PAGE_BEFORE
#            self.gotoEnd()
        #self.writelnError("docs: %s" % docs)
#        if len(docs)==0:
#            self.gotoEnd()
#            self.setCursorToDefaultFormatting()
#            self.insertPara()
#            self.gotoEnd()
#            self.setCursorToDefaultFormatting()
#            self.__cursor.BreakType = PAGE_BEFORE
#            try:
#                self.__cursor.PageDescName=pageStyle
#            except:
#                self.__cursor.PageDescName="Standard"
#            self.__cursor.PageNumberOffset = 1
        
        startPageNumber = 0
        count = 1
        bookmarks = {}
        for doc, props in docs:
            docName = os.path.split(doc)[1]
            value = oriDocs[docName]
            #oriDocs[docName] = ([value, count])            
            
            bookmarks = urlBookmarks[urls[count-1]]
            #self.writelnError ("BBOOOKKMARKS in LOOP: %s" % bookmarks)
            self.gotoEnd()
            self.setCursorToDefaultFormatting()
            
            if count==1:
                #self.insertPageBreak()
                self.insertPara()
                self.gotoEnd()
                self.setCursorToDefaultFormatting()
                self.__cursor.BreakType = PAGE_BEFORE
                try:
                    self.__cursor.PageDescName=pageStyle
                except:
                    self.__cursor.PageDescName="Standard"
                    #raise Exception("pageStyle='%s'" % pageStyle)
                self.__cursor.PageNumberOffset = 1
            else:
                if props.get("InsertPageBreak", True):
                    self.setViewCursorToCursor()
                    self.__cursor.BreakType = PAGE_BEFORE
                    #pass
                else:
                    self.setViewCursorToCursor()
                    self.__cursor.BreakType = NONE
                    self.removePageBreakAtCursor()
            
            if useCopyAndPaste:
                tname = "_temp%s_" % count
                self.addBookmark(tname)
                self.setViewCursorToCursor()
                self.pasteDocument(doc)
            else:
                self.insertDocument(doc)
            #rename the bookmark
            #Original code: for bookmark in self.enumerateAllBookmarksInCursorRange():
            #replaced with below code as enumerate will not return bookmarks found in the table
            bookBookmarks=self.__doc.getBookmarks()
            #self.writeError("processing: %s\n" % value)
            for bookmarkElement in bookBookmarks.ElementNames:
                hasKey = False
                #self.writeError("bookBookmarksElement: %s\n bookmarkNames: %s" % (bookmarkElement, bookmarkNames))
                for key in bookmarkNames:
                    if bookmarkNames[key] == bookmarkElement:
                        hasKey = True
                #self.writelnError ("Adding new bookmark??? %s Bookmarl in element: %s" % (not hasKey, bookmarkElement))
                if not hasKey:
                    if bookmarkElement.find ("_end_of_template_") <= -1 and\
                       bookmarkElement.find ("_Start_") <= -1 and \
                       bookmarkElement.find ("_End_") <= -1:
                        
                        newName = "%s_%s" % (bookmarkElement, count)
                        
                        try:
                            #Get the bookmark object
                            bookmark = bookBookmarks.getByName(bookmarkElement)
                            bookmark.Name = newName
                        except Exception, e:
                            # Hack: to work around a strange OpenOffice/UNO renaming bookmarks bug! that may happen
                            newName = "_%s" % newName
                            try:
                                bookmark.Name = newName
                            except Exception, e:
                                self.writeError("Failed to rename bookmark.Name from '%s' to '%s' in doc='%s'\n" % (name, newName, doc))
                                raise
                        newbookmarkElement = "%s_%s" % (value[0], bookmarkElement)
#                        bookmarks[bookmarkElement] = newName
#                        bookmarkNames[bookmarkElement] = newName
                        bookmarks[newbookmarkElement] = newName
                        bookmarkNames[newbookmarkElement] = newName
                #self.writelnError ("Added bookmark: %s\n" % (bookmarkNames))
            
            for link in self.enumerateAllLinksInCursorRange():
                linkText = link.HyperLinkURL                
                if linkText.startswith("#"):
                    # rename links to bookmarks
                    link.HyperLinkURL += "_%s" % count
                    linkName = linkText[1:]
                    if bookmarks.has_key(linkName):
                        pass    #OK
                    else:    
                        # Note: the bookmark name may have been renamed when inserted
                        #   but this should be very unlikely
                        # What about links to tables etc ???
                        pass
                else: #linkText.startswith(baseUrl) or others:
                    #check if the link is based on the other documents inserted to the book
                    found=False
                    splitLinkName = linkText.split("/")
                    linkName = splitLinkName[len(splitLinkName)-1]
                    if linkName.find("#")>-1:
                        fileLinkTo = linkName.split("#")[0]
                        bookmarkName = linkName.split("#")[1]
                        
                        #check if fileLinkTo is one of the docuements inserted to the book
                        for dName in oriDocs:
                            if found==False:
                                target=oriDocs[dName][0]
                                bookmarkAssigned = oriDocs[dName][1]
                                if target == fileLinkTo:
                                    if bookmarks.has_key(bookmarkName):
                                       bookmarkName = "#%s_%s" % (bookmarkName, bookmarkAssigned)
                                       link.HyperLinkURL = bookmarkName
                                    else:
                                       bookmarkName = "#%s_%s" % (bookmarkName, bookmarkAssigned)
                                       link.HyperLinkURL = bookmarkName
                                    found=True
                                else: 
                                    found=False
                        if found==False:
                            #remove link here
                            link.HyperLinkURL = ""
                            pass 
            self.collapseToStart()
            
            #self.writelnError("InsertPageBreak property: prop=%s" % props)
            if props.get("InsertPageBreak", True):
                pageOddEven = props.get("Page", None)
                #self.writelnError ("pageOddEven=%s " % pageOddEven)
                #put new bookmark here                
                newStartBookmark="_Start_%s_%s" % (pageOddEven, count)
                oriDocs[docName].append(newStartBookmark)
                self.addBookmark(newStartBookmark)                
            else:
                newStartBookmark="_Start_%s_%s" % ("NoPageBreak", count)
                oriDocs[docName].append(newStartBookmark)
                #self.setViewCursorToCursor()
                #self.__cursor.BreakType = NONE
                #self.removePageBreakAtCursor()
                self.addBookmark(newStartBookmark)
                #self.removePageBreakAtCursor()
            #self.writelnError ("newStartBookmark=%s" %newStartBookmark)
            self.gotoEnd()
            lPara = self.getLastParagraph()
            if lPara.String=="--T--":
                #lPara.dispose()
                lPara.String = ""
            else:
                self.insertPara()
            self.gotoEnd()
            self.goLeft(1)
            self.addBookmark("_End_%s" % count)
            self.gotoEnd()                
            count += 1
        
        if title!=None:    # Change the title
            self.gotoStart()
            self.gotoEndOfParagraph(True)
            #if self.cursorString.lower().startswith("title"):
            if True:
                info = self.__doc.getDocumentInfo()
                info.Title = title
                self.cursorString = title
        #self.writelnError ("Buildbook2 urlBookmarks: %s" % urlBookmarks)
        
                
        #fix the html link bookmark
        self.gotoStart()
        self.gotoEnd(True)
        #check for the links that starts with baseurl
        #remove if it's not part of the book
        #self.writelnError( "All bookmark in bookmarkNames: %s" % bookmarkNames)
        for link in self.enumerateAllLinksInCursorRange():
            linkText = link.HyperLinkURL
            found=False
            splitLinkName = linkText.split("/")
            linkName = splitLinkName[len(splitLinkName)-1]
            if not linkText.startswith("#"):
                if linkText.find(baseUrl)>-1:
                    if linkName.find("#")>-1:
                        #e.g http://localhost:8000/rep.something/packages/mybook/chapter01.htm#bookmark
                        #e.g http://localhost:8000/rep.something/packages/mybook/chapter01.odt#bookmark
                        bookmarkName = linkName.split("#")[1]
                        linkName = linkName.split("#")[0]
                        linkName, ext = os.path.splitext(linkName)
                        
                        if ext == ".odt" or ext == ".html" or ext == ".htm":
                            #get the document fullPath
                            repPos = linkText.find("rep.") + 4
                            fileLinkTo = linkText[repPos:]
                            fileLinkTo = os.path.split(fileLinkTo)[0]                    
                            if linkName.find(".")>-1:
                                fileLinkTo += "/" + name
                            else:
                                fileLinkTo += "/" + linkName
                            #self.writelnError("if found both local and #: linkText: %s, linkName: %s, bookmark: %s, ext: %s, fileLinkTo: %s" % (linkText, linkName, bookmarkName, ext, fileLinkTo))
                            for dName in oriDocs:
                                if found==False:
                                    target = oriDocs[dName][2]
                                    bookmarkAssigned = oriDocs[dName][1]
                                    if target.find(fileLinkTo)>-1:
                                        #self.writelnError("%s_%s" % (bookmarkName, bookmarkAssigned))
                                        if bookmarkNames.has_key(bookmarkName):
                                            link.HyperLinkURL = "#%s" % bookmarkNames[bookmarkName]
                                            found = True
                                            break
                                        else:
                                            found = False
                                    else:
                                        found = False
                            if found == False:
                                link.HyperLinkURL = ""
                            #self.writelnError("linkUrl: %s" % link.HyperLinkURL)
                            #self.writelnError("------------")
                    else:
                        #e.g http://localhost:8000/rep.something/packages/mybook/chapter01.htm
                        #e.g http://localhost:8000/rep.something/packages/mybook/chapter01.odt
                        linkName, ext = os.path.splitext(linkName)
                        
                        if ext == ".odt" or ext == ".html" or ext == ".htm":
                            #get the document fullPath
                            repPos = linkText.find("rep.") + 4
                            fileLinkTo = linkText[repPos:]
                            fileLinkTo = os.path.split(fileLinkTo)[0]                    
                            if linkName.find(".")>-1:
                                fileLinkTo += "/" + name
                            else:
                                fileLinkTo += "/" + linkName
                            #self.writelnError("If found only local: Else: linkText: %s, linkName: %s, ext:%s" % (linkText, linkName, ext))
                            
                            for dName in oriDocs:
                                if found==False:
                                    target = oriDocs[dName][2]
                                    bookmarkAssigned = oriDocs[dName][3]
                                    if target.find(fileLinkTo)>-1:
                                        #point to the beginning of the document
                                        link.HyperLinkURL = "#%s" % bookmarkAssigned
                                        found = True
                                        break
                                    else:
                                        found = False
                            if found == False:
                                link.HyperLinkURL = ""
                            #self.writelnError("linkUrl: %s" % link.HyperLinkURL)
                            #self.writelnError("------------")
                
        return urlBookmarks
    
    
    def reindexIng(self, bookDocument, visible=False):
        self.loadDocument(bookDocument, visible)
        bookmarks=[]
        bookBookmarks=self.__doc.getBookmarks()
        
        startPageNumber=0
        count=0
        for bookmarkElement in bookBookmarks.ElementNames:
            #self.writelnError ("BOOKMAKRELEMELENT: %s" % bookmarkElement)
            if bookmarkElement.find("Start")>-1:
                #self.__cursor.BreakType = PAGE_BEFORE
                self.gotoBookmark(bookmarkElement)
                #self.getCursorForBookmark(bookmarkElement)
                #pageNum = self.getPageNumberForBookmark(bookmarkElement)
                pageNum = self.getPageNumberForCursor()
                isOdd = ((pageNum % 2)==1)
                if bookmarkElement.find("Odd")>-1:
                    if isOdd==False:
                        self.setViewCursorToCursor()
                        self.writelnError( "PageNumber: %s for bookmarkElement:%s isOdd=%s so insertPagebreak" % (pageNum, bookmarkElement, isOdd))
                        self.addBlankPageBefore()
                    else:
                        self.writelnError( "PageNumber: %s for bookmarkElement:%s isOdd=%s dont insertPageBreak" % (pageNum, bookmarkElement, isOdd))
                    #self.deleteBookmark(bookmarkElement)
                elif bookmarkElement.find("Even")>-1:
                    if isOdd==True:
                        self.writelnError( "PageNumber: %s for bookmarkElement:%s isOdd=%s so insertPagebreak" % (pageNum, bookmarkElement, isOdd))
                        self.setViewCursorToCursor()
                        self.addBlankPageBefore()
                    else:
                        self.writelnError( "PageNumber: %s for bookmarkElement:%s isOdd=%s dont insertPageBreak" % (pageNum, bookmarkElement, isOdd))
                    #self.deleteBookmark(bookmarkElement)                       
                elif bookmarkElement.find("NoPageBreak")>-1:
                    self.setViewCursorToCursor()
                    self.goLeft(1)
                    self.removePageBreakAtCursor()
                    #self.deleteBookmark(bookmarkElement)
            elif bookmarkElement.find("End")>-1:
                pass
                #self.deleteBookmark(bookmarkElement)
            else:
                bookmarks.append(bookmarkElement)
            if startPageNumber==0:
                startPageNumber = self.getPageNumberForCursor()
            startPageNumber+=1
            count+=1
            self.reindexAll()
        # Make sure there is an even number of pages in the book
        self.gotoEnd()
        pageNum = self.getPageNumberForCursor()
        if pageNum % 2:
            self.setCursorToDefaultFormatting()
            self.insertPara()
            self.gotoEnd()
            self.__cursor.BreakType = PAGE_BEFORE
            self.gotoEnd()
        #reindex for the last page of the book
        self.reindexAll()     
        
        #self.writelnError ("Performing saving in reindexing, bookDocument: %s" % bookDocument)
        #self.saveDocument(bookDocument, toExt=".odt")         
    
    
    def buildBook(self, baseBookDocument, bookDocumentsPathUrl=[], baseUrl="http://localhost",
                     title=None, visible=False):
        #bookDocumentsPathUrl = [ (pathToTheDocument, urlOfTheDocument), .. ]
        buildbookstartTime=time.time()
        #self.writelnError("-buildBook-")
        useCopyAndPaste = False
        if useCopyAndPaste:
            visible = True
        endOfTemplateBookmark = "_end_of_template_"
        self.loadDocument(baseBookDocument, visible)
        
        # Find the endOfTemplate bookmark
        #found = self.getCursorForBookmark(endOfTemplateBookmark)
        #if found:
        #    self.gotoEnd(True)
        #    self.cursorString = ""
        #    for b in self.enumerateAllBookmarksInCursorRange():
        #        b.dispose()
        #self.gotoEnd()
        #self.goLeft(8, True)
        #if not self.cursorString.endswith("\n"):
        #    self.gotoEnd()
        #    self.insertPara()
        #self.gotoEnd()
        #self.insertPara()
        #self.gotoEnd()
        #self.goLeft(1)
        #self.addBookmark(endOfTemplateBookmark)
        #self.gotoEnd()
        startTime=time.time()
        found = self.gotoBookmark(endOfTemplateBookmark)
        if found:
            # Get the first document's page style
            self.gotoNextParagraph()
            pageStyle = self.cursor.PageDescName
            #
            self.gotoBookmark(endOfTemplateBookmark)
            self.goRight(1)
            self.gotoEnd(True)
            self.cursorString = ""
        else:
            # Get page style
            pageStyle = "Standard"
            self.gotoEnd()
            self.gotoStartOfParagraph()
            data = self.readFromCursor(20)
            if data.lower()=="--newpagestyle--" or data=="":
                pageStyle = self.cursor.PageDescName
                self.gotoPreviousParagraph()
                self.gotoEndOfParagraph()
                self.gotoEnd(True)
            else:
                self.gotoEnd()
            #
            self.cursorString = " "
            self.gotoEnd()
            self.goLeft(1)
            self.addBookmark(endOfTemplateBookmark)
        if pageStyle is None:
            pageStyle = "Standard"      # Default
        
        urls = []
        docs = []
        for path, url, props in bookDocumentsPathUrl:
            urls.append(url)
            docs.append((path, props))
        bookmarkNames = {}
        
        links = []
        urlBookmarks = {}       # {url:{oldBookmarkName:newBookmarkName}, ...}
        for url in urls:
            urlBookmarks[url] = {}
        
        # Make an even number of pages in the TOC
        startTime=time.time()
        self.gotoEnd()
        pageNum = self.getPageNumberForCursor()
        if pageNum % 2:
            self.setCursorToDefaultFormatting()
            self.insertPara()
            self.gotoEnd()
            self.__cursor.BreakType = PAGE_BEFORE
            self.gotoEnd()
        if len(docs)==0:
            self.gotoEnd()
            self.setCursorToDefaultFormatting()
            self.insertPara()
            self.gotoEnd()
            self.setCursorToDefaultFormatting()
            self.__cursor.BreakType = PAGE_BEFORE
            try:
                self.__cursor.PageDescName=pageStyle
            except:
                self.__cursor.PageDescName="Standard"
            self.__cursor.PageNumberOffset = 1
        #self.writelnError ("finish Make an even number of pages in the TOC %s" % (time.time()-startTime))
        
        startPageNumber = 0
        count = 1
        for doc, props in docs:
            self.writeMessage("processing document #%s" % count)
            startTime=time.time()
            bookmarks = urlBookmarks[urls[count-1]]
            self.gotoEnd()
            self.setCursorToDefaultFormatting()
            if count==1:
                #self.insertPageBreak()
                self.insertPara()
                self.gotoEnd()
                self.setCursorToDefaultFormatting()
                self.__cursor.BreakType = PAGE_BEFORE
                try:
                    self.__cursor.PageDescName=pageStyle
                except:
                    self.__cursor.PageDescName="Standard"
                    #raise Exception("pageStyle='%s'" % pageStyle)
                self.__cursor.PageNumberOffset = 1
            
            if useCopyAndPaste:
                tname = "_temp%s_" % count
                self.addBookmark(tname)
                self.setViewCursorToCursor()
                self.pasteDocument(doc)
            else:
                self.insertDocument(doc)
            
            for bookmark in self.enumerateAllBookmarksInCursorRange():
                name = bookmark.Name
                # rename book marks
                newName = "%s_%s" % (name, count)
                try:
                    bookmark.Name = newName
                except Exception, e:
                    # Hack: to work around a strange OpenOffice/UNO renaming bookmarks bug! that may happen
                    newName = "_%s" % newName
                    try:
                        bookmark.Name = newName
                    except Exception, e:
                        self.writeError("Failed to rename bookmark.Name from '%s' to '%s' in doc='%s'\n" % (name, newName, doc))
                        raise
                #names.append(newName)
                bookmarks[name] = newName
            self.writeMessage("    finished renamingBookmarks %s" % (time.time()-startTime))
            
            for link in self.enumerateAllLinksInCursorRange():
                linkText = link.HyperLinkURL
                if linkText.startswith("#"):
                    # rename links to bookmarks
                    link.HyperLinkURL += "_%s" % count
                    linkName = linkText[1:]
                    if bookmarks.has_key(linkName):
                        pass    #OK
                    else:    
                        # Note: the bookmark name may have been renamed when inserted
                        #   but this should be very unlikely
                        # What about links to tables etc ???
                        pass
                elif linkText.startswith(baseUrl):
                    # leave for now, we will fixup these when when done
                    links.append(link)
            
            self.writeMessage("    finished enumeratingAllLinksInCursorRange %s" % (time.time()-startTime))
            
            self.collapseToStart()
            startTime=time.time()
            try:
                if props.get("InsertPageBreak", True):
                    self.__cursor.BreakType = PAGE_BEFORE
                    pageOddEven = props.get("Page", None)
                    
                    pageNum = self.getPageNumberForCursor()
                    if startPageNumber==0:
                        startPageNumber = pageNum
                    pageNum = pageNum - startPageNumber + 1
                    #self.writeMessage("pageOddEven='%s', pageNum='%s', %s" % (pageOddEven, pageNum, self.getPageNumberForCursor()))
                    isOdd = ((pageNum % 2)==1)
                    if pageOddEven is not None:
                        if pageOddEven=="Odd" and isOdd==False:
                            self.writeMessage("    Adding a blank page")
                            self.addBlankPageBefore()
                        elif pageOddEven=="Even" and isOdd==True:
                            self.writeMessage("    Adding a blank page")
                            self.addBlankPageBefore()
                else:
                    self.writeMessage("    No page break")
                    if count==1:
                        # always have a page break before the first document
                        self.__cursor.BreakType = PAGE_BEFORE
                    else:
                        self.__cursor.BreakType = NONE
            except:
                pass
            if startPageNumber==0:
                startPageNumber = self.getPageNumberForCursor()
            self.addBookmark("_Start_%s" % count)
            self.gotoEnd()
            #
            lPara = self.getLastParagraph()
            if lPara.String=="T":
                #lPara.dispose()
                lPara.String = ""
            else:
            #
                self.insertPara()
            #self.addText("xxx\ryyy\r")
            self.gotoEnd()
            self.goLeft(1)
            self.addBookmark("_End_%s" % count)
            self.gotoEnd()
            count += 1
            self.writeMessage("  finished added document #%s - %s" % (count, (time.time()-startTime)))
            
        # Now fixup inter document links
        #self.writeError("Warning: urlBookmarks.keys()='%s'\n" % str(urlBookmarks.keys()))
        self.writeMessage("fixing inter document links")
        startTime=time.time()
        for link in links:
            #urls
            linkText = link.HyperLinkURL
            url, bookmarkName = (linkText.split("#") + [""])[:2]
            if url.startswith(baseUrl):
                url = url[len(baseUrl):]
            if urlBookmarks.has_key(url):
                count = urls.index(url) + 1
                if bookmarkName=="":
                    link.HyperLinkURL = "#_Start_%s" % count
                    
                else:
                    #urlBookmarks
                    bookmarks = urlBookmarks[url]
                    newName = bookmarks.get(bookmarkName, bookmarkName)
                    link.HyperLinkURL = "#%s" % newName
            else:
                # Remove link?
                self.writeError("Warning: ooo_automate.buildBook() Removing link to '%s'\n" % linkText)
                link.HyperLinkURL = ""
        self.writeMessage("  finished fixing inter document links %s" % (time.time()-startTime))
        
        # Remove the 'insert page break before' that is applied to the first item.
        startTime=time.time()
        if self.getCursorForBookmark("_Start_1"):
            self.removePageBreakAtCursor()
        self.gotoEnd()
        
        if title!=None:    # Change the title
            self.gotoStart()
            self.gotoEndOfParagraph(True)
            #if self.cursorString.lower().startswith("title"):
            if True:
                info = self.__doc.getDocumentInfo()
                info.Title = title
                self.cursorString = title
        
        #self.writeMessage( "call reindex after pagebreak and link job")
        self.reindexAll()
        # Make sure there is an even number of pages in the book
        self.gotoEnd()
        pageNum = self.getPageNumberForCursor()
        if pageNum % 2:
            self.setCursorToDefaultFormatting()
            self.insertPara()
            self.gotoEnd()
            self.__cursor.BreakType = PAGE_BEFORE
            self.gotoEnd()
        self.writeMessage( "Finished building book. %s" % (time.time()-buildbookstartTime))
        #return dictionary of bookmarks
        return urlBookmarks
    

    def createParagraph(self):
        para = "com.sun.star.text.Paragraph"
        return self.doc.createInstance(para)
    
    
    def setupOoPort(self, port):
        def matchReplace(match):
            groups = match.groups()
            return groups(0) + str(port) + groups(1)
        try:
            c = self.getOoSetupConnectionURL()
            c = re.sub("(port=)(\d*)(;)", matchReplace, c)
            self.setOoSetupConnectionURL(c)
            return True
        except:
            return False
    
    
    def setupOoHost(self, host):
        def matchReplace(match):
            groups = match.groups()
            return groups(0) + str(host) + groups(1)
        try:
            c = self.getOoSetupConnectionURL()
            c = re.sub("(host=)([^,;]*)(,)", matchReplace, c)
            self.setOoSetupConnectionURL(c)
            return True
        except:
            return False
    
    
    def getOoSetupConnectionURL(self):
        # e.g. u'socket,host=localhost,port=2002;urp;StarOffice.ServiceManager'
        configAccess = self.__getConfigAccess()
        c = configAccess.ooSetupConnectionURL
        if type(c) not in types.StringTypes:
            c = u'socket,host=localhost,port=2002;urp;StarOffice.ServiceManager'
        return c
    def setOoSetupConnectionURL(self, s):
        configAccess = self.__getConfigAccess()
        configAccess.ooSetupConnectionURL = s
        configAccess.commitChanges()
    
    
    def __getConfigAccess(self):
        s = "com.sun.star.configuration.ConfigurationProvider"
        s2 = "com.sun.star.configuration.ConfigurationUpdateAccess"
        props = self.__getProps([("enableasync", 0, True, 0)])
        configProvider = self.__localContext.ServiceManager.createInstanceWithArguments(s, props)
        props = self.__getProps([ ("nodepath", 0, "/org.openoffice.Setup/Office", 0), ("lazywrite", 0, False, 0)])
        configAccess = configProvider.createInstanceWithArguments(s2,  props)
        return configAccess
        #configAccess.ooSetupConnectionURL
        #configAccess.commitChanges()
    
    
    def __createDispatchHelper(self):
        dispatchHelper = "com.sun.star.frame.DispatchHelper"
        #dispatcher = self.__smgr.createInstance(dispatchHelper)
        # or
        dispatcher = self.__smgr.createInstanceWithContext(dispatchHelper, self.__ctx)
        return dispatcher


    def __getProps(self, properties=[]):
        props = []
        for name, x, value, y in properties:
            prop = PropertyValue(name, x, value, y)
            props.append(prop)
        return tuple(props)

    
    def propertyValue(self, name, value):
        return PropertyValue(name, 0, value, 0)


    def __enum(self, obj):
        startTime=time.time()
        if hasattr(obj, "createEnumeration"):
            enum = obj.createEnumeration()
            while enum.hasMoreElements():
                yield enum.nextElement()
        #self.writelnError("create enum: %s" % (time.time()-startTime))
    

    def __pathToUrl(self, path):
        url = systemPathToFileUrl(os.path.abspath(path))
        return url


    def __getInProperties(self):
        # "AsTemplate" = True|False
        # "JumpMark" = bookmarkName
        # "DocumentBaseURL" = The base URL of the document to be used to resolve relative links
        # "DocumentTitle" = "Title"
        # "FilterName", "FilterOptions", "FilterData"
        # "InteractionHandler" = com.sun.star.task.XInteractionHandler
        # "Password"
        # "RepairPackage" = True
        # "TemplateName" or "TemplateRegionName"
        # "URL" = "url of the document"
        # "MacroExecutionMode" = ALWAYS_EXECUTE_NO_WARN(=4)  MacroExecMode.Xxx constant list
        l = [   ("Hidden", 0, True, 0), \
                ("UpdateDocMode", 0, QUIET_UPDATE, 0), \
                ("MacroExecutionMode", 0, ALWAYS_EXECUTE_NO_WARN, 0), \
            ]
        return self.__getProps(l)   

    
    def __getOutProperties(self, filterName, outputStream):
        # "Unpacked" = True
        l = [("FilterName", 0, filterName, 0), ("Overwrite", 0, True, 0), \
                ("OutputStream", 0, outputStream, 0)]
        return self.__getProps(l)
    
    
    def __getFliterName(self, toExt):
        msg = ""
        if toExt == ".htm" or toExt==".html" or toExt=="":
            if self.__text is None:
                filterName = "HTML (StarCalc)"
                msg = "CalcToHtml"
            else:
                filterName = "HTML (StarWriter)"
                msg = "ToHtml"
        elif toExt == ".doc":
            filterName = "MS Word 97"
            msg = "ToWordDoc"
        elif toExt == ".odt":
            filterName = "writer8"
            msg = "ToOdt"
        elif toExt == ".ods":
            filterName = "calc8"
            msg = "ToOds"
        elif toExt == ".sxw":
            filterName = "StarOffice XML (Writer)"
            msg = "ToSxw"
        elif toExt == ".pdf":
             if self.__text is None:
                filterName = "calc_pdf_Export"
                msg = "CalcToPdf"
             else:
                filterName = "writer_pdf_Export"
                msg = "ToPdf"
        elif toExt == ".txt":
            filterName = "Text (Encoded)"
            msg = "ToText"
        else:
            raise Exception("unsupport extension type! ext=", toExt)
        return filterName, msg
    
    
    def writeMessage(self, data):
        if self.stdOut is not None:
            self.stdOut.write(data + "\n")
            self.stdOut.flush()
    
    def writeError(self, data):
        if self.stdErr is not None:
            self.stdErr.write(data)
            self.stdErr.flush()
    
    def writelnError(self, data):
        self.writeError(data + "\n")



####################################################################

class OooAutomate(object):
    def __init__(self, DataClass=None, stdOut=None, stdErr=None):
        if DataClass is None:
            DataClass = _DataClass
        self.DataClass = DataClass
        self.stdOut = stdOut
        self.stdErr = stdErr
    
    def createOoObject(self, data):
        try:
            o = OoObject(data.oooPort, data.oooHost, DataClass=self.DataClass, 
                            stdOut=self.stdOut, stdErr=self.stdErr)
        except Exception, e:
            msg = str(e)
            if msg.startswith("OpenOffice process not found"):
                pass
            raise e
        return o
    
    def writeMessage(self, data):
        if self.stdOut is not None:
            self.stdOut.write(data + "\n")
            self.stdOut.flush()
    
    def writeError(self, data):
        if self.stdErr is not None:
            self.stdErr.write(data)
            self.stdErr.flush()
    
    def writelnError(self, data):
        self.writeError(data + "\n");
    
    
    def buildBook(self, data):
        startTime=time.time()
        #self.writelnError ("ooo_automate builbook self function start")
        result = self.DataClass()
        result.allOk = False
        result.errorMessage = None
        
        try:
            ooObj = self.createOoObject(data)
        except Exception, e:
            msg = str(e)
            if msg.startswith("OpenOffice process not found"):
                msg = "Failed to connect to OpenOffice using host='%s' & port='%s', message='%s'"
                msg = msg  % (data.oooPort, data.oooHost, str(e))
            else:
                msg = "Failed to create OpenOffice object! '%s'" % str(e)
            #raise Exception(msg)
            result.allOk = False
            result.errorMessage = msg
            return result
        
        # convert old format to new
        docs = []
        for item in data.docs:
            if len(item)<3:
                item = list(item)
                item.append({})
            docs.append(item)
        try:
            #self.writelnError ("Performing buildbook2")
            urlBookmarks = ooObj.buildBook2(data.fromBookFile, docs, \
                                        data.baseUrl, data.title)
        except Exception, e:
            import traceback
            err = "nothing"
            tb = sys.exc_info()[2]
            lines = 0
            if tb is not None:
                errLines = traceback.format_tb(tb)
                err = "\n".join(errLines[-lines:])
            
            self.writeError("ERROR: %s\n" % str(e))
            self.writeError("%s\n" % "".join(err))
            result.allOk = False
            result.errorMessage = "Exception: %s" % str(e)
            result.errorMessage += "\n" + "".join(err)
            if isinstance(e, UnoException):
                e = Exception("UNO Exception: %s \n %s" % ("".join(err), str(e)) )
            result.exception = e
            return result
        result.urlBookmarks = urlBookmarks
        #self.writelnError ("result in buildbook: %s" % result)
        # save .odt file
        #self.writelnError ("Performing saving in buildbook2")
        try:
            result.odtResult = ooObj.saveDocument(data.toBookFile, toExt=".odt")
            file = data.toBookFile
        except Exception, e:
            result.errorMessage = "saveDocument Exception -'%s'\n" % str(e)
            result.allOk = False
            return result
        #self.writelnError ("result in buildbook: %s" % result)
        ooObj.close()
        
        if result.odtResult.allOk:
            result.allOk = True
        else:
            result.allOk = False
        # can not unpickle a UnoException, so change them
        r = result.odtResult
        if hasattr(r, "exception"):
            e = r.exception
            if isinstance(e, UnoException):
                r.exception = Exception("UnoException")
        #self.writelnError ("ooo_automate builbook self function finish %s" % (time.time()-startTime))
        return result


    def convertDocumentTo(self, data):
        result = self.DataClass()
        result.allOk = False
        result.errorMessage = None
        try:
            ooObj = self.createOoObject(data)
        except Exception, e:
            msg = str(e)
            if msg.startswith("OpenOffice process not found"):
                msg = "Failed to connect to OpenOffice using host='%s' & port='%s', message='%s'"
                msg = msg  % (data.oooPort, data.oooHost, str(e))
            else:
                msg = "Failed to create OpenOffice object! '%s'" % str(e)
            result.errorMessage = msg
            result.exceptionMessage = str(e)
            return result
        try:
            try:
                ooObj.loadDocument(data.file)
            except Exception, e:
                result.errorMessage = str(e)
                return result
            try:
                if hasattr(data, "reindex") and data.reindex==True:
                    ooObj.reindexAll()
            except Exception, e:
                result.allOk = False
                result.errorMessage = str(e)
                return result
            try:
                result = ooObj.saveDocument(data.toFile, data.toExt)
            except Exception, e:
                result.errorMessage = str(e)
                return result
        finally:
            ooObj.close()
        # can not unpickle a UnoException, so change them
        if hasattr(result, "exception"):
            if isinstance(result.exception, UnoException):
                result.exception = Exception("UnoException: " + str(result.exception))
        return result


    def reIndexAll(self, data):
        result = self.DataClass()
        result.completedOK = False
        result.errorMessage = None
        try:
            ooObj = self.createOoObject(data)
        except Exception, e:
            msg = str(e)
            if msg.startswith("OpenOffice process not found"):
                msg = "Failed to connect to OpenOffice using host='%s' & port='%s', message='%s'"
                msg = msg  % (data.oooPort, data.oooHost, str(e))
            else:
                msg = "Failed to create OpenOffice object! '%s'" % str(e)
            result.errorMessage = msg
            return result
        try:
            ooObj.reindexIng(data.bookFile)
            result=ooObj.saveDocument(data.toBookFile, toExt=".odt")   
            ooObj.close()
        except Exception, e:
            result.completedOK = False
            result.errorMessage = str(e)
            return result
        return result


class Object(object): pass


def dictToObject(d):
    obj = Object()
    for k,v in d.items():
        setattr(obj, k, v)
    return obj

def objectToDict(obj):
    d = {}
    for k, v in obj.__dict__.items():
        d[k] = v
    return d

def ppTest(*args):
    print "printing: %s" % os.getcwd()
    try:
        c = StringIO()
    except: 
        print "Failed to create StringIO objects!"
    msg = "test(args='%s') called OK." % (str(args))
    return [msg, sys.version]

def ppMain(data):
    stdErr = None
    stdOut = None
    stdErr = StringIO()
    stdOut = StringIO()
    oAuto = OooAutomate(stdErr=stdErr, stdOut=stdOut)
    startTime = time.time()
    try:
        if not hasattr(data, "oooHost"):
            data.oooHost = "localhost"
        if not hasattr(data, "oooPort"):
            data.oooPort = 2002
        if data.function=="buildBook":
            result = oAuto.buildBook(data)
            #oAuto.writelnError ("data.function is buildBook %s done" % data.toBookFile)
        elif data.function=="convertDocumentTo":
            result = oAuto.convertDocumentTo(data)
        elif data.function=="reindex":
            result = oAuto.reIndexAll(data)
            #oAuto.writelnError ("data.function is reIndexAll %s done" % data.bookFile)
        else:
            result = oAuto.DataClass()
            result.allOk = False
            result.errorMessage = "Unknown function '%s'" % data.function
            oAuto.writeError("Error: Unknown function '%s'\n" % data.function)
    except Exception, e:
        result = oAuto.DataClass()
        result.allOk = False
        result.errorMessage = "Exception - %s" % str(e)
        oAuto.writeError("Exception: %s\n" % str(e))
    
    if stdOut is not None:
        outStr = stdOut.getvalue()
        result.stdOut = outStr
    if stdErr is not None:
        errStr = stdErr.getvalue()
        result.stdErr = errStr
    
    time.sleep(.05)
    return result
    

def automate(dataFile):
    from ice_data import DataClass
    stderr = StringIO()
    oAuto = OooAutomate(DataClass=DataClass, stdErr=stderr)
    try:
        f = None
        data = None
        try:
            try:
                f = open(os.path.abspath(dataFile), "rb")
                data = f.read()
            finally:
                if f is not None:
                    f.close()
        except:
            oAuto.writeError("Error reading %s" % dataFile)
        data = DataClass.decodeData(data)
        if not hasattr(data, "oooHost"):
            data.oooHost = "localhost"
        if data.function == "buildBook":
            result = oAuto.buildBook(data)
        elif data.function == "convertDocumentTo":
            result = oAuto.convertDocumentTo(data)
        elif data.function == "reindex":
            result = oAuto.reIndexAll(data)
        else:
            result = DataClass()
            result.allOk = False
            result.errorMessage = "Unknown function"
            oAuto.writeError("Error: Unknown function '%s'\n" % data.function)
    except Exception, e:
        result = DataClass()
        result.allOk = False
        result.errorMessage = "Exception: %s" % str(e)
        oAuto.writeError("Exception: %s\n" % str(e))
    
    result = "--{%s}--" % result.getEncodedData()
    if stderr is not None:
        msg = stderr.getvalue()
        if msg != "":
            msg = "stderr{-{%s}-}" % msg
    
    return result, msg

def test():
    print " ** testing **"
    o = OoObject()
    o.createNewDocument(True)
    o.addText()
    o.addText("\n\n*** TESTING ***")
    o.addText("\nJust testing.\n")
    o.addText("This window will close in \n")
    for i in range(8):
        o.addText(" %s seconds.\n" % str(8-i))
        time.sleep(1)
    o.addText("Bye..")
    time.sleep(0.2)
    o.close()
    o = None
    print "  done"
    print " --{ Testing }--\n\n"

if __name__ == "__main__":
    if len(sys.argv)<2:
        test()
    else:
        result, msg = automate(sys.argv[1])
        print result
        print msg
    time.sleep(0.05)


# Property (Props)
#   "JumpMark", "BookmarkName"  (inProps)
#   "Unpacked", True            (outProps)

# Notes:
#   If we want to access the current page number (or work with automatic page breaks) we must 
#       use the view cursor (and not the model cursor)

# Cursor object   Note: a cursor is a text range also
#   BreakType
#   PropertyXxxx
#   Start, End
#   String
#   Text
#   TextField
#   TextFrame
#   TextSection
#   Types
#   createContentEnumeration
#   #Note: bExpand=T|F to expand the cursor or not
#   gotoEnd(bExpand)
#   gotoRange(range, bExpand)
#   gotoStart(bExpand)
#   goRight/goLeft(count, bExpand)
#   gotoEndOfParagraph, gotoEndOfSentence, gotoPreviousWord
#   collapseToEnd() collapseToStart()
#   isCollapsed() - return False if this is a text range or True if not
#   hasElments()
#   insertDocumentFromURL(fileUrl, ())
#   get/setPropertyValue
#
#   HyperLinkEvents, HyperLinkName, HyperLinkTarget, HyperLinkURL
#  cursor.Text.instertString(cursor, string, bExpand)  bExpand=False

# Text
#   Start, End
#   String
#   Text
#   Types
#   createTextCursor()
#   createTextCursorByRange(range)
#   createEnumeration()
#   insetString(cursor, textStr, 0)
#   insertTextContent()
#   insertTextContentBefore/After()
#   removeTextContentBefore/After()
#   removeTextContent()

# Document (doc)
#   WordCount
#   ParagraphCount
#   Bookmarks
#   DocumentIndexes
#   EmbeddedObjects
#   EndnoteSettings
#   Endnotes
#   FootnoteSettings
#   Footnotes
#   GraphicObjects
#   Links   # link targets (types)
#   NumberFormatSettings
#   NumberFormats
#   Text
#   TextFields, TextFrames, TextSections, TextTables
#   Close
#   createInstance
#   createInstanceWithArguments
#   createLibrary
#   createReplaceDescriptor
#   createSearchDescriptor
#   dispose
#   findAll, findFirst, findNext
#   getDocumentInfo
#   getPropertyDefault, getPropertySetInfo, getPropertyState, getPropertyStates, 'getPropertyValue
#   hasLocation
#   reformat
#   render
#   replaceAll
#   updateLinks
