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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon
    
from plugin_package_copy import *
from ice_item import *
import re, types

testDataDir = "testData/"
testSvnRepZip1 = testDataDir + "iceOneRep.zip"
testSvnRepZip2 = testDataDir + "iceTwoRep.zip"
testSvnRep1 = testDataDir + "iceOneRep"
testSvnRep2 = testDataDir + "iceTwoRep"
testRep = testDataDir + "iceOneContent"
testRep2 = testDataDir + "iceTwoContent"
testRepContent = "/packages"

def setupRep(fs=None):
    if False: #set to true if need to unzip the repository
        if fs is None:
            fs = IceCommon.FileSystem(".")
        try: 
            fs.delete(fs.absolutePath(testSvnRep1))
            fs.delete(fs.absolutePath(testSvnRep2))
        except: pass
        try:
            fs.delete(fs.absolutePath(testRep))
            fs.delete(fs.absolutePath(testRep2))
        except: pass
        fs.unzipToDirectory(testSvnRepZip1, testSvnRep1)
        fs.unzipToDirectory(testSvnRepZip2, testSvnRep2)
        
    if IceCommon.system.isWindows:
        repUrl = "file:///" + fs.join(fs.absolutePath("."), testSvnRep1)
        repUrl2 = "file:///" + fs.join(fs.absolutePath("."), testSvnRep2)
    else:
        repUrl = "file://" + fs.join(fs.absolutePath("."), testSvnRep1)
        repUrl2 = "file://" + fs.join(fs.absolutePath("."), testSvnRep2)

    return repUrl, repUrl2


#This is for package copy between different rep
class MockRep(object):
    def __init__(self, iceContext, basePath, repUrl, 
                            iceRender, name):
        self.iceContext = iceContext
        self.fs = iceContext.fs.clone()
        self.fs.currentWorkingDirectory = basePath
        self.basePath = basePath
        self.repUrl = repUrl
        self.render = iceRender
        self.name = name
        
        self.iceContext.rep = self
        self.__rlock = self.iceContext.RLock()
        svnRep = self.iceContext.SvnRep(self.iceContext, basePath=self.basePath, \
                            svnUrl=self.repUrl)
        
        self._svnRep = self.iceContext.SvnProxyRep(self.iceContext, svnRep, self.__rlock)
        self.indexer = self.iceContext.getRepositoryIndexer(".indexes")
        self.doNotIndexDirectories = []
        
    #This method is for retrieving ICE1.2 svn prop
    def getSvnProp (self, name, absPath):
        if self._svnRep._hasProperty(absPath, name):
            return self._svnRep._getProperty(absPath, name)
        else:
            return None
        
    def getItem(self, relPath):
        item = IceItem.GetIceItem(self.iceContext, relPath)
        return item

    def getAbsPath(self, relPath="/"):
        if relPath==".":
            relPath = "/"
        if relPath.startswith("./"):
            relPath = relPath[2:]
        relPath = self.iceContext.normalizePath(relPath)
        relPath = relPath.lstrip("/")
        path = self.iceContext.url_join(self.basePath, relPath)
        path = self.iceContext.normalizePath(path)
        return path
#        return self.iceContext.url_join("/abspath", file)


class MockIceRender(object):
    def __init__(self, iceContext):
        self.renderMethods = {}
        self.__renderMethods = {}               # e.g. {".odt": renderMethod, ".doc": renderMethod }  
        self.__renderableTypes = {}             # e.g. {".odt":[".htm", ".pdf"], ".doc":[".htm", ".pdf"], ".odm":[".pdf"]}
        self.__renderableFromCollection = {}    # e.g. {".htm":[".odt", ".doc"] , ".pdf":[".odt", ".doc", ".odm"]}
        self.postRenderPlugin = None
    def setPostRenderPlugin(self, postRender):
        self.postRenderPlugin = postRender
    def getRenderableFrom(self, ext):
        return self.__renderableFromCollection.get(ext, [])
    def getRenderableTypes(self, ext):
        return self.__renderableTypes.get(ext, [])
    def getRenderableExtensions(self):
        return self.__renderMethods.keys()
    def isExtensionRenderable(self, ext):
        return self.__renderMethods.has_key(ext)
    def addRenderMethod(self, ext, renderMethod, renditionExts):
        #print "addRenderMethod(ext='%s', renditionExts='%s')" % (ext, renditionExts)
        self.__renderMethods[ext] = renderMethod
        self.__renderableTypes[ext] = renditionExts
        for rType in renditionExts:
            if self.__renderableFromCollection.has_key(rType):
                if ext not in self.__renderableFromCollection[rType]:
                    self.__renderableFromCollection[rType].append(ext)
            else:
                self.__renderableFromCollection[rType] = [ext]
    def render(self, rep, filesToRender, output=None):
        return "ok", []


#class BI(object):
#    bookInfo = bookInfo
#    bookDocument = bookInfo.BookDocument
#    
#    def __init__(self, iceContext):
#        self.iceContext = iceContext
#    
#    def dumps(self):
#        return self.iceContext.dumps(self)

class PackageCopyTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        self.fs = IceCommon.fs
        self.iceContext = IceCommon.IceContext
        self.bookExt = self.iceContext.bookExts
        
    def setUp(self):
        self.repUrl, self.repUrl2 = setupRep(self.fs)
    
    def getRep(self, testRep, repUrl, name):
        #reset IceContext
        self.iceContext = IceCommon.IceContext
        iceContext = self.iceContext(loadRepositories=False, loadConfig=False)
        #put temporary generated iceContext
        self.iceContext = iceContext
        testRep = self.fs.absolutePath(testRep)
        rep = MockRep(iceContext, testRep, repUrl, MockIceRender(iceContext), name)
        return rep
    
    def tearDown(self):
        pass
    
    def testInit(self):
        pass
        
    def testCopySameRep(self):
        #get the package that will be copied from iceTwo
        packageToBeCopied = "/packages/books"
        destinationToBeCopied = "/packages/bookCopy"
        rep = self.getRep(testRep2, self.repUrl2, 'iceTwo')
        destinationRep = rep
        srcItem = rep.getItem(packageToBeCopied)
        destItem = rep.getItem(destinationToBeCopied)
        
        if self.fs.isDirectory(rep.getAbsPath(destItem.relPath)):
            destItem.delete()
        
        srcItem.packageCopy(destItem)
        
        for listItems in destItem.walk(filesOnly=True):
            for item in listItems:
                #make sure that the item being versioned and being added
                #if not commited yet, the lastChangedRevisionNumber should be -1
                srcItem = rep.getItem(item.relPath.replace(destinationToBeCopied, packageToBeCopied))
                self.assertEquals(item.lastChangedRevisionNumber, srcItem.lastChangedRevisionNumber)
                self.assertTrue(item.isVersioned)
                self.assertNotEquals(item.vcStatusStr, "added")
        
        destinationPath = self.iceContext.url_join(destinationRep.getAbsPath(), destinationToBeCopied.lstrip("/"))
        
        #Call private method of PackageCopy class: __cleanUpBookInfo
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destinationRep
        packageCopy.sameRep = True
        packageCopy._PackageCopy__cleanUpBookInfo()
        
        destItemList = []
        bookLists = []
        for listItems in destItem.walk(filesOnly=True):
            for i in listItems:
                if i.ext in self.iceContext.bookExts:
                    bookLists.append(i.relPath)
                destItemList.append(i.relPath)
            
        expectedFileList = [u'/packages/bookCopy/CursorPositionTest.book.odt', u'/packages/bookCopy/manifest.xml', 
                            u'/packages/bookCopy/newBook.book.odt', u'/packages/bookCopy/study_modules.book.odt', 
                            u'/packages/bookCopy/chapters/chp1.odt', u'/packages/bookCopy/chapters/chp2.odt', 
                            u'/packages/bookCopy/chapters/chp3.odt', u'/packages/bookCopy/chapters/chp4.odt', 
                            u'/packages/bookCopy/modules/module01.odt', u'/packages/bookCopy/modules/module02.odt', 
                            u'/packages/bookCopy/modules/module03.doc', u'/packages/bookCopy/titles_in_headers/Chapter01.odt', 
                            u'/packages/bookCopy/titles_in_headers/Chapter02.odt', u'/packages/bookCopy/titles_in_headers/Chapter03.doc', 
                            u'/packages/bookCopy/titles_in_headers/title_test.book.odt'] 
        
        
        self.assertEquals(destItemList, expectedFileList)
        
        expectedBookList = [u'/packages/bookCopy/CursorPositionTest.book.odt', u'/packages/bookCopy/newBook.book.odt', 
                            u'/packages/bookCopy/study_modules.book.odt', u'/packages/bookCopy/titles_in_headers/title_test.book.odt']
        self.assertEquals(bookLists, expectedBookList)
        
        #Make sure book property in source and destination are still the same
        bookDict = {}
        relPath = ""
        for book in bookLists:
            destPath = book
            srcPath = destPath.replace(destinationToBeCopied, packageToBeCopied)
            srcBookItem = rep.getItem(srcPath) 
            destBookItem = rep.getItem(destPath)
            destBookInfo = destBookItem.bookInfo            
            srcBookInfo = srcBookItem.bookInfo
            
            self.assertEquals(destBookInfo.needsBuilding, srcBookInfo.needsBuilding)
            
            #After a package being copied, the book NEED to be rendered 
            self.assertEquals(destBookInfo.needsRendering, True)
            self.assertEquals(destBookInfo.relBasePath, srcBookInfo.relBasePath.replace(packageToBeCopied, destinationToBeCopied))
            self.assertEquals(destBookInfo.relBookFile, srcBookInfo.relBookFile.replace(packageToBeCopied, destinationToBeCopied))
            
            self.assertEquals(destBookInfo.bookTitle, srcBookInfo.bookTitle)
            self.assertEquals(destBookInfo.renderAsHtml, srcBookInfo.renderAsHtml)
            self.assertEquals(destBookInfo.pdfOnly, srcBookInfo.pdfOnly)
            self.assertEquals(destBookInfo.pageRef, srcBookInfo.pageRef)
            
            #Other properties (these should be the same since during cleanup there are no changes)
            self.assertEquals(destBookInfo._BookInfo__bookModifiedDate, srcBookInfo._BookInfo__bookModifiedDate)
            self.assertEquals(destBookInfo._BookInfo__bookMD5, srcBookInfo._BookInfo__bookMD5)
            
            #check on documents
            destDocs = destBookInfo.documents
            srcDocs = srcBookInfo.documents
            
            self.assertEquals(len(destDocs), len(srcDocs))
            
            expectedDocs = {}
            for doc in srcDocs:
                destPath = doc.path.replace(packageToBeCopied, destinationToBeCopied)
                destUrl = doc.url.replace(packageToBeCopied, destinationToBeCopied)
                destMd5 = doc.md5
                destPageBreak = doc.pageBreakType
                expectedDocs[destPath] = [destPath, destUrl, destMd5, destPageBreak]
                
            for doc in destDocs:
                docInfo = expectedDocs[doc.path]
                self.assertEquals(docInfo[0], doc.path)
                self.assertEquals(docInfo[1], doc.url)
                self.assertEquals(docInfo[2], doc.md5)
                self.assertEquals(docInfo[3], doc.pageBreakType)
        
        #fixup links check
        packageCopy.currentRep = rep.name
        packageCopy.copyToRep = rep.name
        packageCopy._PackageCopy__fixUpLinks()
        
        filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, rep)
        expected = {u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopy/modules/module01.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/modules/module03.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/modules/module03/htm'], 
                    u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopy/chapters/chp3.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm#bookmarkThis'], 
                    u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopy/chapters/chp1.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/modules/module03.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/modules/module03/htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm#bookmarkThis'], 
                    u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopy/chapters/chp4.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopy/chapters/chp2.htm#bookmarkThis']}

        self.assertEquals(filesWithLocalLinksAfterFix, expected)
        
    def testCopyFromIce1toIce2WithIce2PropertyFoundInIce1(self):
        #these ice2 property will be existed in ice one because the book has been opened using Ice2
        #get the package that will be copied from iceOne
        packageToBeCopied = "/packages/books"
        destinationToBeCopied = "/packages/bookCopyFromOldIce"
        #need to assign destRep first because the iceContext.rep will content the last rep being assigned
        destRep = self.getRep(testRep2, self.repUrl2, 'iceTwo')
        destinationRep = destRep
        
        srcRep = self.getRep(testRep, self.repUrl, 'iceOne')
        srcItem = srcRep.getItem(packageToBeCopied)
        destItem = destRep.getItem(destinationToBeCopied)
        
        destinationPath = self.iceContext.url_join(destRep.getAbsPath(), destinationToBeCopied.lstrip("/"))
        #export src to dest first
        if self.fs.isDirectory(destRep.getAbsPath(destItem.relPath)):
            destItem.delete()
        srcItem.export(destinationPath)
        
        #then in destination Add the package
        destItem.add(recurse=True)
        
        #Call private method of PackageCopy class: __cleanUpBookInfo
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destinationRep
        packageCopy.sameRep = False
        packageCopy._PackageCopy__cleanUpBookInfo()
        
        for listItems in destItem.walk(filesOnly=True):
            for item in listItems:
                #make sure that the item being versioned and being added
                #if not commited yet, the lastChangedRevisionNumber should be -1
                self.assertEquals(item.lastChangedRevisionNumber, -1)
                self.assertTrue(item.isVersioned)
                self.assertEquals(item.vcStatusStr, "added")
        
        destItemList = []
        bookLists = []
        for listItems in destItem.walk(filesOnly=True):
            for i in listItems:
                if i.ext in self.iceContext.bookExts:
                    bookLists.append(i.relPath)
                destItemList.append(i.relPath)
            
        expectedFileList =  [u'/packages/bookCopyFromOldIce/newBook.book.odt', u'/packages/bookCopyFromOldIce/manifest.xml', 
                             u'/packages/bookCopyFromOldIce/CursorPositionTest.book.odt', 
                             u'/packages/bookCopyFromOldIce/study_modules.book.odt', u'/packages/bookCopyFromOldIce/chapters/chp1.odt', 
                             u'/packages/bookCopyFromOldIce/chapters/chapter02.odt', u'/packages/bookCopyFromOldIce/chapters/chapter01.odt', 
                             u'/packages/bookCopyFromOldIce/chapters/chp2.odt', u'/packages/bookCopyFromOldIce/modules/module02.odt', 
                             u'/packages/bookCopyFromOldIce/modules/module01.odt', '/packages/bookCopyFromOldIce/modules/module03.doc']
        
        self.assertEquals(destItemList, expectedFileList)

        expectedBookList = [u'/packages/bookCopyFromOldIce/newBook.book.odt', u'/packages/bookCopyFromOldIce/CursorPositionTest.book.odt', 
                            u'/packages/bookCopyFromOldIce/study_modules.book.odt'] 
        self.assertEquals(bookLists, expectedBookList)
        
        #Make sure book property in source and destination are still the same
        bookDict = {}
        relPath = ""
        for book in bookLists:
            destPath = book
            srcPath = destPath.replace(destinationToBeCopied, packageToBeCopied)
            srcBookItem = srcRep.getItem(srcPath) 
            destBookItem = destRep.getItem(destPath)
            destBookInfo = destBookItem.bookInfo            
            srcBookInfo = srcBookItem.bookInfo
                    
            self.assertEquals(destBookInfo.needsBuilding, srcBookInfo.needsBuilding)
            
            #After a package being copied, the book NEED to be rendered 
            self.assertEquals(destBookInfo.needsRendering, True)
            self.assertEquals(destBookInfo.relBasePath, srcBookInfo.relBasePath.replace(packageToBeCopied, destinationToBeCopied))
            self.assertEquals(destBookInfo.relBookFile, srcBookInfo.relBookFile.replace(packageToBeCopied, destinationToBeCopied))
            
            self.assertEquals(destBookInfo.bookTitle, srcBookInfo.bookTitle)
            self.assertEquals(destBookInfo.renderAsHtml, srcBookInfo.renderAsHtml)
            self.assertEquals(destBookInfo.pdfOnly, srcBookInfo.pdfOnly)
            self.assertEquals(destBookInfo.pageRef, srcBookInfo.pageRef)
            
            #Other properties (these should be the same since during cleanup there are no changes)
            self.assertEquals(destBookInfo._BookInfo__bookModifiedDate, srcBookInfo._BookInfo__bookModifiedDate)
            self.assertEquals(destBookInfo._BookInfo__bookMD5, srcBookInfo._BookInfo__bookMD5)
            
            #check on documents
            destDocs = destBookInfo.documents
            srcDocs = srcBookInfo.documents
            
            self.assertEquals(len(destDocs), len(srcDocs))
            
            expectedDocs = {}
            for doc in srcDocs:
                destPath = doc.path.replace(packageToBeCopied, destinationToBeCopied)
                destUrl = doc.url.replace(packageToBeCopied, destinationToBeCopied)
                destMd5 = doc.md5
                destPageBreak = doc.pageBreakType
                expectedDocs[destPath] = [destPath, destUrl, destMd5, destPageBreak]
                
            for doc in destDocs:
                docInfo = expectedDocs[doc.path]
                self.assertEquals(docInfo[0], doc.path)
                self.assertEquals(docInfo[1], doc.url)
                self.assertEquals(docInfo[2], doc.md5)
                self.assertEquals(docInfo[3], doc.pageBreakType)
                
        #fixup links check
        packageCopy.currentRep = srcRep.name
        packageCopy.copyToRep = destRep.name
        packageCopy._PackageCopy__fixUpLinks()
        
        filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, destRep)
        expected = {u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIce/chapters/chp1.odt': 
                    ['http://localhost:8000/rep.TestContent1.2/packages/books/chapters/chp2.odt', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIce/chapters/chp2.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIce/chapters/chp2.htm#bookmarkThis'], 
                    u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIce/chapters/chapter01.odt': 
                ['http://localhost:8000/rep.sample-content/packages/mybook/chapter01.htm#same', 
                 'http://localhost:8000/rep.sample-content/packages/mybook/chapter03.htm', 
                 'http://localhost:8000/rep.sample-content/packages/mybook/chapter02.htm#another']}

        self.assertEquals(filesWithLocalLinksAfterFix, expected)
                
    def testCopyFromIce1toIce2WithOriginalIce1SvnProp(self):
        #These bookInfo from Ice1 has not been opened in Ice2 yet
        #Do not include .skin folder option
        #get the package that will be copied from iceOne
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureNoSkin"

        #need to assign destRep first because the iceContext.rep will content the last rep being assigned
        destRep = self.getRep(testRep2, self.repUrl2, 'iceTwo')
        destinationRep = destRep
        
        srcRep = self.getRep(testRep, self.repUrl, 'iceOne')
        srcItem = srcRep.getItem(packageToBeCopied)
        destItem = destRep.getItem(destinationToBeCopied)

        destinationPath = self.iceContext.url_join(destRep.getAbsPath(), destinationToBeCopied.lstrip("/"))

        #export src to dest first
        if self.fs.isDirectory(destRep.getAbsPath(destItem.relPath)):
            destItem.delete()
        srcItem.export(destinationPath)
        
        #then in destination Add the package
        destItem.add(recurse=True)
        
        #Call private method of PackageCopy class: __cleanUpBookInfo
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destinationRep
        packageCopy.sameRep = False
        packageCopy._PackageCopy__cleanUpBookInfo()
        packageCopy._PackageCopy__removeOptions(skin=False)
        
        for listItems in destItem.walk(filesOnly=True):
            for item in listItems:
                #make sure that the item being versioned and being added
                #if not commited yet, the lastChangedRevisionNumber should be -1
                self.assertEquals(item.lastChangedRevisionNumber, -1)
                self.assertTrue(item.isVersioned)
                self.assertEquals(item.vcStatusStr, "added")
        
        destItemList = []
        bookLists = []
        for listItems in destItem.walk(filesOnly=True):
            for i in listItems:
                if i.ext in self.iceContext.bookExts:
                    bookLists.append(i.relPath)
                destItemList.append(i.relPath)
            
        expectedFileList = [u'/packages/bookCopyFromOldIcePureNoSkin/study.book.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/manifest.xml', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/overview.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module10.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module09.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module08.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module07.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module06.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module05.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module04.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module03.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module02.odt', 
                            u'/packages/bookCopyFromOldIcePureNoSkin/study_modules/module01.odt']
        
        self.assertEquals(destItemList, expectedFileList)

        expectedBookList =  [u'/packages/bookCopyFromOldIcePureNoSkin/study.book.odt']
        self.assertEquals(bookLists, expectedBookList)
        
        #ice1.2 bookInfo format
        global bookInfo
        class bookInfo1_2(object):
            def __init__ (self):
                self.bookInfo = bookInfo1_2
                self.bookDocument = bookInfo1_2
        sys.modules["book_info"] = bookInfo1_2()
        
        #Make sure book property in source and destination are still the same
        bookDict = {}
        relPath = ""
        for book in bookLists:
            destPath = book
            srcPath = destPath.replace(destinationToBeCopied, packageToBeCopied)
            srcBookItem = srcRep.getItem(srcPath) 
            destBookItem = destRep.getItem(destPath)
            destBookInfo = destBookItem.bookInfo            
            srcBookInfo = srcBookItem.bookInfo
            
            self.assertEquals(srcBookInfo, None)
            srcBookInfo = srcRep.getSvnProp("meta-bookInfo", srcRep.getAbsPath(srcBookItem.relPath))
            
            self.assertTrue(destBookInfo.needsBuilding)
            
            #After a package being copied, the book NEED to be rendered 
            self.assertEquals(destBookInfo.needsRendering, True)
            self.assertEquals(destBookInfo.relBasePath, srcBookInfo._bookInfo__relBasePath.replace(packageToBeCopied, destinationToBeCopied))
            self.assertEquals(destBookInfo.relBookFile, srcBookInfo._bookInfo__relBookFile.replace(packageToBeCopied, destinationToBeCopied))
            filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, destRep)
            title = srcRep.getSvnProp("meta-title", srcRep.getAbsPath(srcBookItem.relPath))
            self.assertEquals(destBookInfo.bookTitle, title)
            renderAsHtml = srcBookInfo._bookInfo__renderAsHtml            
            self.assertEquals(destBookInfo.renderAsHtml, renderAsHtml)
            pageRef = False
            try:
                #not all v1.2 book has these
                pageRef = oldBook._bookInfo__pageRef
            except:
                pass
            self.assertEquals(destBookInfo.pageRef, pageRef)
            if not pageRef and not renderAsHtml:
                self.assertTrue(destBookInfo.pdfOnly)
            else:
                self.assertFalse(destBookInfo.pdfOnly)
            
            
            #check on documents
            destDocs = destBookInfo.documents
            srcDocs = srcBookInfo._bookInfo__documents
            
            self.assertEquals(len(destDocs), len(srcDocs))
            
            expectedDocs = {}
            for doc in srcDocs:
                destPath = doc._bookDocument__path.replace(packageToBeCopied, destinationToBeCopied)
                destUrl = doc._bookDocument__url.replace(packageToBeCopied, destinationToBeCopied)
                md5=""
                pageBreakType=""
                try:
                    md5 = doc._bookDocument__md5
                    pageBreakType = doc._bookDocument__pageBreakType
                except:
                    pass
                destMd5 = md5
                destPageBreak = pageBreakType
                expectedDocs[destPath] = [destPath, destUrl, destMd5, destPageBreak]
                
            for doc in destDocs:
                docInfo = expectedDocs[doc.path]
                self.assertEquals(docInfo[0], doc.path)
                self.assertEquals(docInfo[1], doc.url)
                self.assertEquals(docInfo[2], doc.md5)
                self.assertEquals(docInfo[3], doc.pageBreakType)
        
        #List of links need to be fixed
        packageCopy.currentRep = srcRep.name
        packageCopy.copyToRep = destRep.name
        packageCopy._PackageCopy__fixUpLinks()
        
        filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, destRep)
        expected = {u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIcePureNoSkin/study_modules/module04.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/module02.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/module02.odt'], 
                    u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIcePureNoSkin/study_modules/module01.odt': 
                    ['http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/module02.htm', 
                     'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/module02.odt']}

        self.assertEquals(filesWithLocalLinksAfterFix, expected)
        
    def testCopyFromIce1toIce2WithOriginalIce1SvnPropWithSkin(self):
        #These bookInfo from Ice1 has not been opened in Ice2 yet
        #Do not include .skin folder option
        #get the package that will be copied from iceOne
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureWithSkin"

        #need to assign destRep first because the iceContext.rep will content the last rep being assigned
        destRep = self.getRep(testRep2, self.repUrl2, 'iceTwo')
        destinationRep = destRep
        
        srcRep = self.getRep(testRep, self.repUrl, 'iceOne')
        srcItem = srcRep.getItem(packageToBeCopied)
        destItem = destRep.getItem(destinationToBeCopied)

        destinationPath = self.iceContext.url_join(destRep.getAbsPath(), destinationToBeCopied.lstrip("/"))

        #export src to dest first
        if self.fs.isDirectory(destRep.getAbsPath(destItem.relPath)):
            destItem.delete()
        srcItem.export(destinationPath)
        
        #then in destination Add the package
        destItem.add(recurse=True)
        
        #Call private method of PackageCopy class: __cleanUpBookInfo
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destinationRep
        packageCopy.sameRep = False
        packageCopy._PackageCopy__cleanUpBookInfo()
        packageCopy._PackageCopy__removeOptions(skin=True)
        
        for listItems in destItem.walk(filesOnly=True):
            for item in listItems:
                #make sure that the item being versioned and being added
                #if not commited yet, the lastChangedRevisionNumber should be -1
                self.assertEquals(item.lastChangedRevisionNumber, -1)
                self.assertTrue(item.isVersioned)
                self.assertEquals(item.vcStatusStr, "added")
        
        destItemList = []
        bookLists = []
        for listItems in destItem.walk(filesOnly=True):
            for i in listItems:
                if i.ext in self.iceContext.bookExts:
                    bookLists.append(i.relPath)
                destItemList.append(i.relPath)
            
        expectedFileList = [u'/packages/bookCopyFromOldIcePureWithSkin/study.book.odt', u'/packages/bookCopyFromOldIcePureWithSkin/manifest.xml', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/skin/pic.jpg', '/packages/bookCopyFromOldIcePureWithSkin/skin/templates/templatestemp.xhtml', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/overview.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module10.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module09.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module08.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module07.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module06.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module05.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module04.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module03.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module02.odt', 
                            u'/packages/bookCopyFromOldIcePureWithSkin/study_modules/module01.odt']
        
        self.assertEquals(destItemList, expectedFileList)

        expectedBookList =  [u'/packages/bookCopyFromOldIcePureWithSkin/study.book.odt']
        self.assertEquals(bookLists, expectedBookList)
        
        #ice1.2 bookInfo format
        global bookInfo
        class bookInfo1_2(object):
            def __init__ (self):
                self.bookInfo = bookInfo1_2
                self.bookDocument = bookInfo1_2
        sys.modules["book_info"] = bookInfo1_2()
        
        #Make sure book property in source and destination are still the same
        bookDict = {}
        relPath = ""
        for book in bookLists:
            destPath = book
            srcPath = destPath.replace(destinationToBeCopied, packageToBeCopied)
            srcBookItem = srcRep.getItem(srcPath) 
            destBookItem = destRep.getItem(destPath)
            destBookInfo = destBookItem.bookInfo            
            srcBookInfo = srcBookItem.bookInfo
            
            self.assertEquals(srcBookInfo, None)
            srcBookInfo = srcRep.getSvnProp("meta-bookInfo", srcRep.getAbsPath(srcBookItem.relPath))
            
            self.assertTrue(destBookInfo.needsBuilding)
            
            #After a package being copied, the book NEED to be rendered 
            self.assertEquals(destBookInfo.needsRendering, True)
            self.assertEquals(destBookInfo.relBasePath, srcBookInfo._bookInfo__relBasePath.replace(packageToBeCopied, destinationToBeCopied))
            self.assertEquals(destBookInfo.relBookFile, srcBookInfo._bookInfo__relBookFile.replace(packageToBeCopied, destinationToBeCopied))
            filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, destRep)
            title = srcRep.getSvnProp("meta-title", srcRep.getAbsPath(srcBookItem.relPath))
            self.assertEquals(destBookInfo.bookTitle, title)
            renderAsHtml = srcBookInfo._bookInfo__renderAsHtml            
            self.assertEquals(destBookInfo.renderAsHtml, renderAsHtml)
            pageRef = False
            try:
                #not all v1.2 book has these
                pageRef = oldBook._bookInfo__pageRef
            except:
                pass
            self.assertEquals(destBookInfo.pageRef, pageRef)
            if not pageRef and not renderAsHtml:
                self.assertTrue(destBookInfo.pdfOnly)
            else:
                self.assertFalse(destBookInfo.pdfOnly)
            
            
            #check on documents
            destDocs = destBookInfo.documents
            srcDocs = srcBookInfo._bookInfo__documents
            
            self.assertEquals(len(destDocs), len(srcDocs))
            
            expectedDocs = {}
            for doc in srcDocs:
                destPath = doc._bookDocument__path.replace(packageToBeCopied, destinationToBeCopied)
                destUrl = doc._bookDocument__url.replace(packageToBeCopied, destinationToBeCopied)
                md5=""
                pageBreakType=""
                try:
                    md5 = doc._bookDocument__md5
                    pageBreakType = doc._bookDocument__pageBreakType
                except:
                    pass
                destMd5 = md5
                destPageBreak = pageBreakType
                expectedDocs[destPath] = [destPath, destUrl, destMd5, destPageBreak]
                
            for doc in destDocs:
                docInfo = expectedDocs[doc.path]
                self.assertEquals(docInfo[0], doc.path)
                self.assertEquals(docInfo[1], doc.url)
                self.assertEquals(docInfo[2], doc.md5)
                self.assertEquals(docInfo[3], doc.pageBreakType)
        
        #List of links need to be fixed
        packageCopy.currentRep = srcRep.name
        packageCopy.copyToRep = destRep.name
        packageCopy._PackageCopy__fixUpLinks()
        
        filesWithLocalLinksAfterFix = self.filesWithLocalLinks(destItem, destRep)
        expected =  {u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIcePureWithSkin/study_modules/module01.odt': 
                     ['http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureWithSkin/module02.htm', 
                      'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureWithSkin/module02.odt'], 
                     u'/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent/packages/bookCopyFromOldIcePureWithSkin/study_modules/module04.odt': 
                     ['http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureWithSkin/module02.htm', 
                      'http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureWithSkin/module02.odt']} 

        self.assertEquals(filesWithLocalLinksAfterFix, expected)
        
        
    def testLinks(self):
        #Same Rep From links other package
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureNoSkin"
        rep = "/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent"
        repName = "iceTwo"
        destinationPath = self.iceContext.url_join(rep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = rep
        packageCopy.sameRep = False
        packageCopy.currentRep = repName
        packageCopy.copyToRep = repName
        
        href     = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceOne/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceOne/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
                
        ####
        href     = "http://localhost:8000/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceOne/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        #Different Rep links from other packages
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureNoSkin"
        srcRep = "/home/octalina/workspace/trunk/apps/ice/testData/iceOneContent"
        srcRepName = "iceOne"
        destRep = rep
        destRepName = repName
        destinationPath = self.iceContext.url_join(destRep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destRep
        packageCopy.sameRep = False
        packageCopy.currentRep = srcRepName
        packageCopy.copyToRep = destRepName
        
        href     = "http://localhost:8000/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        ####
        href     = "http://localhost:8000/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        #Same Rep From links same package
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureNoSkin"
        rep = "/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent"
        repName = "iceTwo"
        destinationPath = self.iceContext.url_join(rep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = rep
        packageCopy.sameRep = False
        packageCopy.currentRep = repName
        packageCopy.copyToRep = repName
        
        href     = "http://localhost:8000/rep.iceTwo/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceOne/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceOne/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
                
        ####
        href     = "http://localhost:8000/packages/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/packages/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceOne/packages/courseware/mgt/2201/2009/s1/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        #Different Rep links from same packages
        packageToBeCopied = "/packages/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/packages/bookCopyFromOldIcePureNoSkin"
        srcRep = "/home/octalina/workspace/trunk/apps/ice/testData/iceOneContent"
        srcRepName = "iceOne"
        destRep = rep
        destRepName = repName
        destinationPath = self.iceContext.url_join(destRep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destRep
        packageCopy.sameRep = False
        packageCopy.currentRep = srcRepName
        packageCopy.copyToRep = destRepName
        
        href     = "http://localhost:8000/rep.iceOne/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceTwo/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/packages/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
                
        ####
        href     = "http://localhost:8000/packages/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/packages/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/packages/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        ######Links without packages
        #Same Rep From links other package
        packageToBeCopied = "/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/bookCopyFromOldIcePureNoSkin"
        rep = "/home/octalina/workspace/trunk/apps/ice/testData/iceTwoContent"
        repName = "iceTwo"
        destinationPath = self.iceContext.url_join(rep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = rep
        packageCopy.sameRep = False
        packageCopy.currentRep = repName
        packageCopy.copyToRep = repName
        
        href     = "http://localhost:8000/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceTwo/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceTwo/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
                
        ####
        href     = "http://localhost:8000/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceOne/courseware/mgt/2201/2009/s1/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/courseware/mgt/2201/2009/s1/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        #Diff Rep From links other package
        packageToBeCopied = "/courseware/mgt/2201/2009/s1"
        destinationToBeCopied = "/bookCopyFromOldIcePureNoSkin"
        srcRep = "/home/octalina/workspace/trunk/apps/ice/testData/iceOneContent"
        srcRepName = "iceOne"
        destRep = rep
        destRepName = repName
        destinationPath = self.iceContext.url_join(destRep, destinationToBeCopied.lstrip("/"))
        
        packageCopy = PackageCopy(self.iceContext, forUnitTest=True)
        packageCopy.packagePath= packageToBeCopied
        packageCopy.copyToPath = destinationToBeCopied
        packageCopy.newPathName = destinationPath
        packageCopy.destinationRep = destRep
        packageCopy.sameRep = False
        packageCopy.currentRep = srcRepName
        packageCopy.copyToRep = destRepName
        
        href     = "http://localhost:8000/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceTwo/courseware/mgt/2201/2009/s1/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)

        href     = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/chapter/chapter01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
                
        ####
        href     = "http://localhost:8000/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceOne/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceTwo/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceTwo/bookCopyFromOldIcePureNoSkin/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
        href     = "http://localhost:8000/rep.iceThree/courseware/mgt/2201/2009/s1/modules/module01.htm"
        expected = "http://localhost:8000/rep.iceThree/courseware/mgt/2201/2009/s1/modules/module01.htm"
        self.assertEquals (packageCopy._PackageCopy__validLink(href), expected)
        
    def filesWithLocalLinks(self, destItem, destRep):
        #List of links need to be fixed
        fileList = {}
        for listItems in destItem.walk(filesOnly=True):
            for i in listItems:
                try:
                    nodeList = []
                    file = destRep.getAbsPath(i.relPath)
                    ext = self.fs.splitExt(file)[1]
                    if ext == ".odt" or ext == ".book.odt": 
                        tempDir = self.fs.unzipToTempDirectory(file)
                        xml = self.iceContext.Xml(tempDir.absolutePath("content.xml"), oOfficeNSList)
                        
                        nodes = xml.getNodes("//text:a[starts-with(@xlink:href, 'http://localhost')] | \
                                              //draw:a[starts-with(@xlink:href, 'http://localhost')]")
                        for node in nodes:
                            nodeList.append(node.getAttribute("href"))
                            
                        if nodeList != []:
                            fileList[file] = nodeList
                finally:
                        xml.close()
                        tempDir.delete()
        return fileList

if __name__ == "__main__":
    IceCommon.runUnitTests(locals())
    