#!/usr/bin/env python
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

import sys
import time
import types
import string
import re
from cStringIO import StringIO

sys.path.append("../ice")
from ice_common import IceCommon


from ice_item2 import IceItem
from ice_rep2 import IceRepository  ####
IceRepository.IceItem = IceItem

from vc_rep import VCRep



testDataDir = "testData/"
testSvnRepZip = testDataDir + "svnTestRep.zip"
testSvnRep = testDataDir + "svnTempRep"
testRep = testDataDir + "tempRep"
testRep2 = testDataDir + "tempRep2"
testOdt = "testData/test.odt"
repUrl = None


def setupRep(fs=None):
    global repUrl
    if fs is None:
        fs = IceCommon.FileSystem(".")
    try:
        fs.delete(testSvnRep)
    except: pass
    try:
        fs.delete(testRep)
    except: pass
    if IceCommon.system.isWindows:
        repUrl = "file:///" + fs.join(fs.absolutePath("."), testSvnRep)
    else:
        repUrl = "file://" + fs.join(fs.absolutePath("."), testSvnRep)
    repUrl += "/testRep"
    fs.unzipToDirectory(testSvnRepZip, testSvnRep)
    # checkout testSvnRep to testRep
    VCRep.checkout(repUrl, fs.absPath(testRep))

def setupRep2():
    # note: setupRep must have been called first
    global repUrl
    if repUrl is None:
        raise Exception("setupRep2() must be called first!")
    fs = IceCommon.FileSystem(".")
    try:
        fs.delete(testRep2)
    except: pass
    VCRep.checkout(repUrl, fs.absPath(testRep2))
    

class MockIceRender(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.renderMethods = {".txt":self.__textRender}
        self.postRenderPlugin = None
        self.renderedExtensions = [".htm", ".pdf"]
    
    def __textRender(self, item):
        convertedData = self.iceContext.ConvertedData()
        convertedData.addMeta("title", "testingTitle")
        convertedData.addMeta("absFile", item._absPath)
        convertedData.addMeta("renderedWith", "__textRender")
        convertedData.addRenditionData(".xhtml.body", "<html>%s</html>" % item.relPath)
        #convertedData.addMeta("toc", "Test-TOC")
        return convertedData
    
    def getRenderableFrom(self, ext):
        #print "mock getRenderableForm ext='%s'" % ext
        if ext==".txt":
            return [".pdf", ".htm"]
        return []
    
    def getRenderableTypes(self, ext):
        #print "mock getRenderableTypes ext='%s'" % ext
        return [".txt"]

    def getRenderableExtensions(self):
        return self.renderMethods.keys()
    
    def isExtensionRenderable(self, ext):
        return ext in self.renderMethods.keys()
    
    def render(self, item, output=None):
        ext = item.ext
        renderMethod = self.renderMethods.get(ext, None)
        if callable(renderMethod):
            return renderMethod(item)
    


#class MockIceContext(object):
#    def __init__(self, rep, fs):
#        self.rep = rep
#        self.fs = fs


# Notes:
#  IceItem object(s) are always created from an IceRepository object.
#    rep.getItemForPath(relPath)  - must match extension as well (casing???)
#    rep.getItemForUri(uri)       - will get the item that is associated with this URI
#                                   e.g. x.odt for x.htm or x_files/images/x.gif etc
#


class IceItemTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        self.iceContext = IceCommon.IceContext(None)
        self.fs = self.iceContext.fs
    
    
    def setUp(self):
        pass
    
    
    def tearDown(self):
        pass
    
    
    def getRep(self):
        iceContext = self.iceContext
        output = iceContext.output
        def write(data):
            pass    # ignore output messages
        iceContext.output = iceContext.Object()
        iceContext.output.write = write
        setupRep(self.fs)
        ##
        fs = iceContext.fs
        if fs.exists(testRep)==False:
            raise Exception("rep does not exist yet!")
        ##
        iceContext.loadPlugins("../ice/plugins/render/plugin_convertedData.py")
        iceContext._ConvertedData = iceContext.getPluginClass("ice.convertedData")
        iceContext.loadPlugins("../ice/plugins/required/plugin_mimeTypes.py")
        iceContext.MimeTypes = iceContext.getPluginClass("ice.mimeTypes")(iceContext)
        iceContext.loadPlugins("../ice/plugins/extras/plugin_inline_annotate.py")
        iceContext.IceInlineAnnotations = iceContext.getPluginClass("ice.extra.inlineAnnotate")
        rep = IceRepository(iceContext, testRep, repUrl=repUrl,
                            iceRender=MockIceRender(iceContext))
        iceContext.output = output
        return rep


    def getRep2(self):
        iceContext = self.iceContext.clone()

        def write(data):
            pass    # ignore output messages
        iceContext.output = iceContext.Object()
        iceContext.output.write = write

        setupRep2()
        rep2 = IceRepository(iceContext, testRep2, repUrl=repUrl,
                            iceRender=MockIceRender(iceContext))
        return rep2

    
    def getItem(self, rep=None, relPath="/"):
        if rep is None:
            rep = self.getRep()
        item = rep.getItem(relPath)
        return item
    
    
    def testRootItemProperties(self):
        rep = self.getRep()
        
        item = self.getItem(rep, relPath="/")

        self.assertEquals(item.name, "")
        self.assertEquals(item.relPath, "/")
        self.assertEquals(item.uri, "/")
        guid = item.guid
        self.assertEquals(len(guid), 32)
        self.assertTrue(item.isVersioned)
        
        item = self.getItem(rep, relPath="")
        self.assertEquals(item.guid, guid)
        item = self.getItem(rep, relPath="./test/..")
        self.assertEquals(item.guid, guid)
        item = self.getItem(rep, relPath="./test/../")
        self.assertEquals(item.guid, guid)
    
    
    def testFileItemProperties(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="test.ext")
        self.assertFalse(item.exists)
        item.write("Testing")
        self.assertTrue(item.exists)
        self.assertTrue(item.isFile)
        self.assertEquals(item.metaNames, [])
        item.setMeta("one", "One")
        item.setMeta("two", "Two")
        self.assertEquals(item.metaNames, ["two", "one"])
        item.setMeta("two", None)
        self.assertEquals(item.metaNames, ["one"])
        item.removeMeta("one")
        self.assertEquals(item.metaNames, [])
    
    
    def testDirItemProperties(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="subdir")
        self.assertFalse(item.exists)
        item.makeDirectory()
        self.assertTrue(item.exists)
        self.assertTrue(item.isDirectory)
    
    
    def testOdtFileItem(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="testDir/test.odt")
        data = IceCommon.fs.readFile(testOdt)
        item.write(data)
        content = item.extractFromZip("content.xml")
        self.assertEquals(len(content), 13797)


    def testAnnotations(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="testDir/testA")
        item.write("Annotation test file")
        ann = item.inlineAnnotations
        self.assertEquals(ann.rootAnnotations, [])
        # Note: the following line may print out data
        div = ann.addAnnotation(username="testuser", paraId="paraID",
                        text="some text", html="html", parentId=None)
        self.assertEquals(len(ann.rootAnnotations), 1)

    
    def testProperties(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="/testDir/test.odt")
        data = IceCommon.fs.readFile(testOdt)
        item.write(data)
        self.assertEquals(item.relPath, "/testDir/test.odt")
        self.assertEquals(len(item.guid), 32)
        self.assertFalse(item.convertFlag)
        self.assertFalse(item.hasPdf)
        self.assertFalse(item.hasHtml)
        self.assertEquals(item.hasSlide, None)
        self.assertFalse(item.needsUpdating)
        self.assertEquals(item.tags, [])
        #self.assertEquals(item.inlineAnnotations, None)
        self.assertEquals(item.bookInfo, None)
        self.assertEquals(item.lastChangedRevisionNumber, -1)
        self.assertFalse(item.isRenderable)
        parent = item.parentItem
        cd = self.iceContext.ConvertedData()
        cd.addMeta("title", "TestTitle")
        cd.addRenditionData(".xhtml.body", "<div><p>TestPara</p></div>")
        cd.addRenditionData(".pdf", "[PDF-DATA]")
        item.setConvertedData(cd)
        #item.hasHtml, item.hasPdf  still both False
        self.assertEquals(item.metaNames, ["title"])
        self.assertEquals(item.getMeta("title"), "TestTitle")
        self.assertEquals(item.getRendition(".pdf"), "[PDF-DATA]")
        rep.serverData = IceCommon.Object()
        def getIdForRelPath(relPath):
            return 0x555
        rep.serverData.getIdForRelPath = getIdForRelPath
        self.assertEquals(item.getIdUrl(), "test_i555r-1.odt")


    def xtestTags(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="testDir/tags.txt")
        item.write("Tag test file")
        self.assertEquals(item.tags, [])
        item.setTags("one two three")
        self.assertEquals(item.tags, ["one", "three", "two"])
        item.setTags("one three four")
        self.assertEquals(item.tags, ["four", "one", "three"])
        t = item.lastModifiedDateTime
    
    
    
    
    #===============================================================
    
    def testReadWrite(self):
        rep = self.getRep()
        data = "testing one"
        item = self.getItem(rep, relPath="sdir/test1.txt")
        item.write(data)
        self.assertTrue(item.isFile)
        guid = item.guid
        item = None
        #Read
        item = self.getItem(rep, relPath="sdir/test1.txt")
        self.assertTrue(item.isFile)
        self.assertEquals(item.guid, guid)
        self.assertEquals(item.read(), data)
    
    
    def testSetGetMeta(self):
        rep = self.getRep()
        data = "testing one"
        fileItem = self.getItem(rep, relPath="sdir/test1.txt")
        fileItem.write(data)
        dirItem = self.getItem(rep, relPath="/sdir")
        fileItem.setMeta("meta1", "MetaOneFile")
        dirItem.setMeta("meta1", "MetaOneDir")
        fileItem.close()
        dirItem.close()
        fileItem = None
        dirItem = None
        # getMeta
        fileItem = self.getItem(rep, relPath="sdir/test1.txt")
        dirItem = self.getItem(rep, relPath="/sdir")
        self.assertEquals(fileItem.getMeta("meta1"), "MetaOneFile")
        self.assertEquals(dirItem.getMeta("meta1"), "MetaOneDir")

    
    def testMakeDirectory(self):
        rep = self.getRep()
        # make one level only directory
        item = self.getItem(rep, relPath="/")
        self.assertTrue(item.isDirectory)
        
        item = self.getItem(rep, relPath="/oneLevel")
        self.assertFalse(item.exists)
        item.makeDirectory()
        self.assertTrue(item.isDirectory)
        
        # make two or more levels test
        item = self.getItem(rep, relPath="/one/two/three/")
        self.assertFalse(item.exists)
        item.makeDirectory()
        self.assertTrue(item.isDirectory)
        self.assertEquals(item.relPath, "/one/two/three/")
        self.assertEquals(item.name, "three")
        item = self.getItem(rep, relPath="/one/two")
        self.assertTrue(item.isDirectory)
        item = self.getItem(rep, relPath="/one/")
        self.assertTrue(item.isDirectory)
        
        # test making directories as a result of creating a new file
        item = self.getItem(rep, relPath="/sdir/one/test.txt")
        self.assertFalse(item.exists)
        item.write("Testing")
        self.assertTrue(item.isFile)
        item = self.getItem(rep, relPath="/sdir")
        self.assertTrue(item.isDirectory)
    
    
    def testListItems(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/two/three/test.txt").write("test")
        item = self.getItem(rep, relPath="one/two/test.txt").write("test")
        item = self.getItem(rep, relPath="one/two")
        items = item.listItems()
        #for i in items:
        #    print i.name
        self.assertEquals(len(items), 2)
        path = rep.getAbsPath(".")
        rep._svnRep.commitAll(path)
        
        items = item.listItems()
        self.assertEquals(len(items), 2)
        
        path = rep.getAbsPath("one/two/three")
        self.fs.delete(path)
        items = item.listItems()
        #for i in items:
        #    print i.name, i.vcStatusStr
        self.assertEquals(len(items), 2)
        self.assertEquals(items[0].vcStatusStr, "missing")
    
    
    def testStatus(self):
        # vcStatus
        # vcStatusStr
        # lastChangedRevisionNumber
        # isVersioned
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/two/three/test.txt")
        item.write("test")
        item.close()
        item = self.getItem(rep, relPath="one/two/one.txt")
        item.write("test")
        path = rep.getAbsPath(".")
        rep._svnRep.commitAll(path)     # revision 2
        
        item2 = self.getItem(rep, relPath="one/two/one.txt")
        item2.setMeta("test", "Testing")
        item2.flush()
        rep._svnRep.commitAll(path)     # revision 3
        rep._svnRep.updateAll(path)     # update what has been committed (to update lastChangedRevisionNumber)
        
        self.getItem(rep, relPath="one/two/two.txt").write("test")
        item = self.getItem(rep, relPath="one/two")
        item2.write("changed")
        items = item.listItems()
        
        items.sort()
        #for i in items:
        #    print i.name, i.vcStatusStr, i.isVersioned, i.lastChangedRevNum
        self.assertEquals(items[0].lastChangedRevNum, 2)
        self.assertEquals(items[1].lastChangedRevNum, 3)
        self.assertEquals(items[2].lastChangedRevNum, -1)
        
        item = self.getItem(rep, relPath="/one")
        self.assertEquals(item.lastChangedRevNum, 3)
    
    
    def testPartialUpdate(self):
        rep = self.getRep()
        rootItem = self.getItem(rep, relPath="/")
        item = self.getItem(rep, relPath="one/two/three/test.txt").write("test")
        item = self.getItem(rep, relPath="one/two/test.txt").write("test")
        path = rep.getAbsPath(".")
        rep._svnRep.commitAll(path)             # ~ 1 Second
        rootItem = self.getItem(rep, relPath="/")
        rootItems = rootItem.listItems()
        self.assertEquals(len(rootItems), 1)
        self.assertTrue(rootItems[0].isDirectory)
        self.assertFalse(rootItems[0].isMissing)
        #for i in rootItems:
        #    print i, i.isDirectory, i.isMissing
        #print "\n---"
        
        path = rep.getAbsPath("one")
        self.fs.delete(path)
        rootItem = self.getItem(rep, relPath="/")
        rootItems = rootItem.listItems()
        self.assertEquals(len(rootItems), 1)
        self.assertTrue(rootItems[0].isMissing)
        self.assertTrue(rootItems[0].isDirectory)
        #for i in rootItems:
        #    print i, i.isDirectory, i.isMissing
        #print

        itemOne = self.getItem(rep, relPath="one")
        self.assertTrue(itemOne.isMissing)
        self.assertTrue(itemOne.isDirectory)
        
        itemOne._update()                           # ~ 2 Seconds
        self.assertTrue(itemOne.isDirectory)
        self.assertFalse(itemOne.isMissing)
        items = itemOne.listItems()
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].name, "two")
        self.assertTrue(items[0].isMissing)
        #for i in items:
        #    print i, i.isDirectory, i.isMissing
        itemTwo = items[0]
        itemTwo._update()                           # ~ 2 Seconds
        items = itemTwo.listItems()
        items.sort()
        #for i in items:
        #    print i, i.isDirectory, i.isMissing
        self.assertEquals(len(items), 2)
        self.assertEquals(items[0].name, "three")
        self.assertTrue(items[0].isDirectory)
        self.assertTrue(items[0].isMissing)
        self.assertEquals(items[1].name, "test.txt")
        self.assertFalse(items[1].isDirectory)
        #self.assertFalse(items[1].isMissing)
    
    
    def testWalk(self):
        rep = self.getRep()
        rootItem = self.getItem(rep, relPath="/")
        item = self.getItem(rep, relPath="/one/two/three/test.txt").write("test")
        item = self.getItem(rep, relPath="/one/two/test.txt").write("test")
        l = []
        for listItems in rootItem.walk():
            for i in listItems:
                #print i.relPath, i.name
                l.append(i.name)
        self.assertEquals(l, ["one", "two", "three", "test.txt", "test.txt"])
        
        #print
        l = []
        def filter(item):
            if item.isDirectory and not item.isMissing: return True
            return item.name.endswith(".txt")
        for listItems in rootItem.walk(filter=filter, filesOnly=True):
            for i in listItems:
                #print i.relPath, i.name
                l.append(i.relPath)
        self.assertEquals(l, ["/one/two/test.txt", "/one/two/three/test.txt"])
    
    
    def testCommit(self):
        rep = self.getRep()
        self.getItem(rep, relPath="one/two/three/test.txt").write("test")
        self.getItem(rep, relPath="one/two/test.txt").write("test")
        item2 = self.getItem(rep, relPath="one/two")
        list1 = item2.listItems()
        #for item in list1:
        #    print item.relPath, item.vcStatus
        revNum = item2._commit()
        #print "revNum='%s'" % revNum
        item = self.getItem(rep, relPath="one/two/three/test.txt")
        #print item._absPath
        self.getItem(rep, relPath="one/two/test.txt").write("test2")
        self.fs.delete(item._absPath)
        revNum = item2._commit()
        #print "revNum='%s'" % revNum
        list2 = item2.listItems()
        for item in list2:
            #print item.relPath, item.vcStatus
            self.assertEquals(item.vcStatusStr, "normal")
    
    
    def xtestGetUpdateList(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/two/three/test.txt").write("test")
        item = self.getItem(rep, relPath="one/two/test.txt").write("test")
        path = rep.getAbsPath(".")
        rep._svnRep.commitAll(path)             # ~ 1 Second
        pathOne = self.fs.join(path, "one")
        pathTwo = self.fs.join(path, "two")
        self.fs.copy(pathOne, pathTwo)
        item2 = self.getItem(rep, relPath="two")
        l = item2._getToBeUpdatedList()
        self.assertEquals(l, [])
        
        item = self.getItem(rep, relPath="one/two/three/test.txt").write("test1")
        item = self.getItem(rep, relPath="one/two/test.txt").write("test1")
        item = self.getItem(rep, relPath="one/three/four/test.txt").write("test1")
        rep._svnRep.commitAll(path)             # ~ 1 Second
        l = item2._getToBeUpdatedList()
        l = [i.relPath for i in l]
        self.assertEquals(l, 
            ['/two/two/three/test.txt', '/two/two/three/', '/two/two/test.txt', 
             '/two/two/', '/two/'])
        
        item2 = self.getItem(rep, relPath="two/two")
        l = item2._getToBeUpdatedList()
        l = [i.relPath for i in l]
        self.assertEquals(l, ['/two/two/three/test.txt', '/two/two/three/', 
                            '/two/two/test.txt', '/two/two/'])
        
        def callback(item, displayMessage=None, step=None, exception=None, **extras):
            print "callback relPath='%s', message='%s', step='%s'" % (item.relPath, displayMessage, step)
            #print "  item.vcStatus.isOutOfDate='%s'" % item.getStatus(True).isOutOfDate
        l = item2._getToBeUpdatedList(callback=callback)
        l = [i.relPath for i in l]
    
    
    def testUpdate(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/dirTwo/one.txt")
        item1.write("test")
        item = self.getItem(rep, relPath=".")
        item._commit()
        path = rep.getAbsPath(".")
        pathOne = self.fs.join(path, "one")
        pathTwo = self.fs.join(path, "two")
        self.fs.copy(pathOne, pathTwo)
        item2 = self.getItem(rep, relPath="two")
        #
        item1.write("Testing one")
        item1._commit()
        item = self.getItem(rep, relPath="/one/dir3/test.txt")
        item.write("test")
        item._commit()

        item = self.getItem(rep, relPath="/one")
        revNum = item._commit()
        
    
    
    def testRender(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("testing text")
        self.assertTrue(item1.isRenderable)
        self.assertTrue(item1.needsUpdating)
        def callback(item, step="", displayMessage="", *args, **kwargs):
            #print "testRender callback() called step='%s'" % step
            pass
        item1.render(callback=callback)
        self.assertEquals(item1.getMeta("title"), "testingTitle")
        self.assertEquals(item1.getMeta("absFile"), item1._absPath)
    
    
    def testSync(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("testing text")
        item = self.getItem(rep, relPath="one/two")
        l = []
        for l2 in item.walk(filesOnly=True):
            l.extend(l2)
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0].vcStatusStr, "added")
        
        item._sync()
        
        l = []
        for l2 in item.walk(filesOnly=True):
            l.extend(l2)
        self.assertEquals(len(l), 1)
        self.assertEquals(l[0].vcStatusStr, "normal")
        #self.assertEquals()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        self.assertEquals(item1.getMeta("title"), "testingTitle")
    
    
    def testDelete(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("test")


    def testShelve(self):
        # only if item is upto date (so that no changes are lost!)
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("test")
        guid1 = item1.guid
        item2 = self.getItem(rep, relPath="one/two/test2.txt")
        item2.write("test")
        guid2 = item2.guid
        item = self.getItem(rep, relPath="one/two")

        rep._svnRep.commitAll(rep.getAbsPath("."))
        item.shelve()

        item1 = self.getItem(rep, relPath="one")
        #for i in item1.listItems(): print i
    
    
    def testMoveDir(self):
        rep = self.getRep()
        guid1 = self.getItem(rep, relPath="one/two/three/test1.txt").write("one").guid
        guid2 = self.getItem(rep, relPath="one/two/test.txt").write("two").guid
        # Move before committing (added only)
        item = self.getItem(rep, relPath="one/two")
        moveToItem = self.getItem(rep, relPath="/one/three")
        item.move(moveToItem)
        self.assertFalse(self.getItem(rep, relPath="one/two").exists)
        self.assertFalse(self.getItem(rep, relPath="one/two/three/test1.txt").exists)
        self.assertFalse(self.getItem(rep, relPath="one/two/test.txt").exists)
        self.assertEquals(self.getItem(rep, relPath="one/three/three/test1.txt").guid, guid1)
        self.assertEquals(self.getItem(rep, relPath="one/three/test.txt").guid, guid2)
        
        # Move committed data
        self.getItem(rep, relPath="one")._commit()
        item = self.getItem(rep, relPath="one/three")
        moveToItem = self.getItem(rep, relPath="/one/four")
        item.move(moveToItem)
        deletedItem = self.getItem(rep, relPath="one/three")
        self.assertEquals(deletedItem.vcStatusStr, "deleted")
        self.assertEquals(self.getItem(rep, relPath="one/four/three/test1.txt").guid, guid1)
        self.assertEquals(self.getItem(rep, relPath="one/four/test.txt").guid, guid2)
        
        # Move committed and added only data
        self.getItem(rep, relPath="one")._commit()
        item = self.getItem(rep, relPath="one/four")
        guid3 = self.getItem(rep, relPath="/one/four/four/four.txt").write("44").guid
        moveToItem = self.getItem(rep, relPath="/one/five")
        item.move(moveToItem)
        deletedItem = self.getItem(rep, relPath="one/four")
        self.assertEquals(deletedItem.vcStatusStr, "deleted")
        self.assertEquals(self.getItem(rep, relPath="one/five/three/test1.txt").guid, guid1)
        self.assertEquals(self.getItem(rep, relPath="one/five/test.txt").guid, guid2)
        self.assertEquals(self.getItem(rep, relPath="one/five/four/four.txt").guid, guid3)

    
    def testMoveFile(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt")
        guid1 = item.write("one").guid
        # Move before committing (added only)
        moveToItem = self.getItem(rep, relPath="/one/two/test2.txt")
        item.move(moveToItem)
        self.assertFalse(self.getItem(rep, relPath="one/test1.txt").exists)
        self.assertEquals(self.getItem(rep, relPath="one/two/test2.txt").guid, guid1)
        
        # Move committed data
        item = self.getItem(rep, relPath="one/two/test2.txt")
        item._commit()
        moveToItem = self.getItem(rep, relPath="/one/three/test3.txt")
        item.move(moveToItem)
        deletedItem = self.getItem(rep, relPath="one/two/test2.txt")
        self.assertEquals(deletedItem.vcStatusStr, "deleted")
        self.assertEquals(self.getItem(rep, relPath="one/three/test3.txt").guid, guid1)
    
    
    def testCopyDir(self):
        # Note: must create a new Guid
        rep = self.getRep()
        guid1 = self.getItem(rep, relPath="one/two/three/test3.txt").write("one").guid
        guid2 = self.getItem(rep, relPath="one/two/test.txt").write("two").guid
        guid3 = self.getItem(rep, relPath="one/two/three").guid
        # Copy before committing (added only)
        item = self.getItem(rep, relPath="one/two")
        copyItem1 = self.getItem(rep, relPath="one/three")
        item.copy(copyItem1)
        
        cItem1 = self.getItem(rep, relPath="one/three/three/test3.txt")
        self.assertTrue(cItem1.isFile)
        self.assertTrue(cItem1.guid!=guid1)
        cItem2 = self.getItem(rep, relPath="one/three/test.txt")
        self.assertTrue(cItem2.isFile)
        self.assertTrue(cItem2.guid!=guid2)
        cItem3 = self.getItem(rep, relPath="one/three/three/")
        self.assertTrue(cItem3.isDirectory)
        self.assertTrue(cItem3.guid!=guid3)
        
        # Copy committed data
        item._commit()
        copyItem2 = self.getItem(rep, relPath="one/four")
        item.copy(copyItem2)
        
        cItem1 = self.getItem(rep, relPath="one/four/three/test3.txt")
        self.assertTrue(cItem1.isFile)
        self.assertTrue(cItem1.guid!=guid1)
        cItem2 = self.getItem(rep, relPath="one/four/test.txt")
        self.assertTrue(cItem2.isFile)
        self.assertTrue(cItem2.guid!=guid2)
        cItem3 = self.getItem(rep, relPath="one/four/three/")
        self.assertTrue(cItem3.isDirectory)
        self.assertTrue(cItem3.guid!=guid3)
        
        # Copy committed and added only data
        # should be ok
    
    
    def testCopyFile(self):
        # Note: must create a new Guid
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt")
        guid1 = item.write("one").guid
        copyItem1 = self.getItem(rep, relPath="one/two/test2.txt")
        # Copy before committing (added only)
        item.copy(copyItem1)
        item = self.getItem(rep, relPath="one/test1.txt")
        copyItem1 = self.getItem(rep, relPath="one/two/test2.txt")
        self.assertTrue(copyItem1.isFile)
        self.assertTrue(copyItem1.guid != guid1)
        self.assertEquals(copyItem1.vcStatusStr, "added")
        self.assertTrue(item.isFile)
        self.assertEquals(item.guid, guid1)
        self.assertEquals(item.vcStatusStr, "added")

        # Copy committed data
        item._commit()
        item.reload()
        copyItem2 = self.getItem(rep, relPath="one/three/test3.txt")
        item.copy(copyItem2)
        copyItem2.reload()
        self.assertTrue(copyItem2.isFile)
        self.assertTrue(copyItem2.guid != guid1)
        self.assertEquals(copyItem2.vcStatusStr, "added")
        self.assertTrue(item.isFile)
        self.assertEquals(item.guid, guid1)
        self.assertEquals(item.vcStatusStr, "normal")
    
    
    def testExport(self):
        rep = self.getRep()
        self.getItem(rep, relPath="one/two/three/test3.txt").write("one")
        self.getItem(rep, relPath="one/two/test2.txt").write("two")
        item = self.getItem(rep, relPath="one/two")
        destPath = testDataDir + "export/"
        absDestPath = self.fs.absolutePath(destPath)
        self.fs.delete(absDestPath)
        item.export(absDestPath)
        self.assertEquals(self.fs.readFile(destPath+"test2.txt"), "two")
        self.assertEquals(self.fs.readFile(destPath+"three/test3.txt"), "one")
        self.assertTrue(self.fs.isFile(destPath+".ice/__dir__/meta"))
        self.assertTrue(self.fs.isFile(destPath+".ice/test2.txt/meta"))
        self.assertTrue(self.fs.isFile(destPath+"three/.ice/__dir__/meta"))
        self.assertTrue(self.fs.isFile(destPath+"three/.ice/test3.txt/meta"))
        
        destPath = testDataDir + "export2/"
        absDestPath = self.fs.absolutePath(destPath)
        self.fs.delete(absDestPath)
        item.export(absDestPath, includeProperties=False)
        self.assertEquals(self.fs.readFile(destPath+"test2.txt"), "two")
        self.assertEquals(self.fs.readFile(destPath+"three/test3.txt"), "one")
        self.assertFalse(self.fs.isDirectory(destPath+".ice/"))
        self.assertFalse(self.fs.isDirectory(destPath+"three/.ice/"))
    
    
    def testConflicts(self):
        # Test Conflict Handling
        # Update conflicts
        # Commit conflicts
        pass
        ##################
    
    
    def testRootSkinFake(self):
        skin = "skin/"
        d = {skin+"test1.txt":"One", skin+"subDir/test2.txt":"Two"}
        rep = self.getRep()
        fs = rep.fs
        fs.updateFakeFiles(d)
        self.assertTrue(fs.exists(skin))
        self.assertTrue(fs.isDirectory(skin))
        self.assertEquals(fs.list(skin), ["test1.txt", "subDir"])
        
        skinItem = self.getItem(rep, skin)
        self.assertTrue(skinItem.exists)
        self.assertTrue(skinItem.isDirectory)

        skinItems = skinItem.listItems()
        self.assertEquals(len(skinItems), 2)
        #print "--- skin='%s'" % skin
        #print [i.relPath for i in skinItems]
        
        item1 = self.getItem(rep, skin+"test1.txt")
        item2 = self.getItem(rep, skin+"subDir/test2.txt")
        #print item1.relPath, item1.isFile, item1.read()
        #print item2.relPath, item2.isFile, item2.read()
        self.assertEquals(item1.read(), "One")
        self.assertEquals(item2.read(), "Two")
    

    def testIsHidden(self):
        # any file or dir starting with '.'
        # any top level directory called 'skin'
        # any top level file called 'favicon.ico'
        # any file called "imscp_rootv1p1.dtd"
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt")
        self.assertFalse(item.isHidden)
        item = self.getItem(rep, relPath="one/.test1")
        self.assertTrue(item.isHidden)
        item = self.getItem(rep, relPath=".one/test1")
        self.assertTrue(item.isHidden)
        item = self.getItem(rep, relPath="skin/test")
        self.assertTrue(item.isHidden)
        item = self.getItem(rep, relPath="favicon.ico")
        self.assertTrue(item.isHidden)
        item = self.getItem(rep, relPath="one/imscp_rootv1p1.dtd")
        self.assertTrue(item.isHidden)

    def testIsIgnored(self):
        # "Thumbs.db" or starting with '.' (but not '.site/etc')
        #   endswith ".tmp", startswith "~$"
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/ok").write("ok")
        self.assertFalse(item.isIgnored)
        item = self.getItem(rep, relPath="one/Thumbs.db/x").write("x")
        self.assertTrue(item.isIgnored)
        item = self.getItem(rep, relPath="one/.test").write("test")
        self.assertTrue(item.isIgnored)
        item = self.getItem(rep, relPath="one/~$test").write("x")
        self.assertTrue(item.isIgnored)
        item = self.getItem(rep, relPath="one/test.tmp").write("x")
        self.assertTrue(item.isIgnored)

    def testIsDeleted(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("x")
        item._commit()
        item.delete()
        #print item.vcStatusStr, item.isDeleted
        self.assertTrue(item.isDeleted)
        item = self.getItem(rep, relPath="one/test1.txt")
        #print item.vcStatusStr, item.isDeleted
        self.assertTrue(item.isDeleted)

    def testIsMyChanges(self):
        rep = self.getRep()
        rep2 = self.getRep2()
        file1 = "one/test.txt"
        item = self.getItem(rep, relPath=file1).write("testing one")
        item._commit()
        item2r = self.getItem(rep2)
        item2r._update(1)
        item2 = self.getItem(rep2, relPath=file1)
        item.write("mychanges one")
        item2.write("testing two")
        item2._commit()
        item._update()
        itemc = self.getItem(rep, relPath="one/MyChanges_test.txt")
        self.assertEquals(item.read(), "testing two")
        self.assertEquals(itemc.read(), "mychanges one")
        self.assertTrue(itemc.isMyChanges)

    def testHasChanges(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("x")
        item2 = self.getItem(rep, relPath="one/two/test").write("y")
        one = self.getItem(rep, relPath="one")
        one._commit()
        #self.assertFalse(one.hasChanges)
        item2.write("YY")
        self.assertTrue(one.hasChanges)
        one._commit()
        self.assertFalse(one.hasChanges)
        one.setMeta("d", 1)
        self.assertTrue(one.hasChanges)
        one._commit()
        self.getItem(rep, relPath="one/two/test").setMeta("p1", "x")
        self.assertTrue(one.hasChanges)

    def testSameNameAlreadyExists(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("x")
        item2 = self.getItem(rep, relPath="one/Test1.txt")
        self.assertTrue(item2.sameNameAlreadyExists)

    def testGetNamedItem(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("x")
        one = self.getItem(rep, relPath="one")
        item = one.getNamedItem("test1")
        self.assertEquals(item.relPath, "/one/test1.txt")

    def testGetChildItem(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt")
        one = self.getItem(rep, relPath="one")
        item = one.getChildItem("test1.txt")
        self.assertEquals(item.relPath, "/one/test1.txt")

    def testGetLogData(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("1")
        item._commit(commitMessage="log1")
        item = self.getItem(rep, relPath="one/test1.txt").write("2")
        item._commit(commitMessage="log2")
        logData = item.getLogData()
        self.assertEquals(logData[2], "log2")
        logData = item.getLogData(3)
        self.assertEquals(logData[1][2], "log1")
        item2 = self.getItem(rep, relPath="one/test2.txt").write("2")
        logData = item2.getLogData()
        self.assertEquals(logData, None)

    def testGetIceItemForUri(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.htm")
        self.assertTrue(uItem!=None)
        self.assertEquals(uItem.relPath, "/one/test1.txt")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.htm/test?q=d")
        self.assertTrue(uItem!=None)
        self.assertEquals(uItem.relPath, "/one/test1.txt")

        uItem = item.GetIceItemForUri(item.iceContext, "one/test1_files/test.pic")
        self.assertTrue(uItem!=None)
        self.assertEquals(uItem.relPath, "/one/test1.txt")

    def testUriDiff(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.htm/extra/stuff?x=5")
        self.assertEquals(uItem.uriDiff, "extra/stuff?x=5")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1_files/test.pic/pextra?x=5")
        self.assertEquals(uItem.uriDiff, "_files/test.pic/pextra?x=5")

    def testUriNotFound(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        item._setRendition(".pdf", "PDF-data")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.htmx")
        self.assertTrue(uItem.uriNotFound)
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1x")
        self.assertTrue(uItem.uriNotFound)
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.htm/test")
        self.assertFalse(uItem.uriNotFound)
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.pdf/test")
        self.assertFalse(uItem.uriNotFound)

    def testHasRendition(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        item._setRendition(".pdf", "PDF-data")
        self.assertTrue(item.hasRendition(".pdf"))

    def testHasXRendition(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        item._setRendition(".pdf", "PDF-data")
        ext = ".mp3"
        self.assertFalse(item.hasAudio)
        self.assertFalse(item.hasXRendition(ext))
        self.assertTrue(item.hasXRendition(".htm"))
        self.assertTrue(item.hasXRendition(".pdf"))
        item.setMeta("_renderAudio", True)
        self.assertFalse(item.hasAudio)
        self.assertFalse(item.hasXRendition(ext))
        item._setRendition(".mp3", "data")
        self.assertTrue(item.hasAudio)
        self.assertTrue(item.hasXRendition(ext))

    def testIsBinaryContent(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.pic", "Pic")
        item._setRendition(".pdf", "PDF-data")
        uItem = item.GetIceItemForUri(item.iceContext, "/one")
        self.assertFalse(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1.txt")
        self.assertTrue(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1.htm")
        self.assertFalse(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1.htm/test")
        self.assertFalse(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1.txt/extra")
        self.assertTrue(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1_files/test.pic/testing")
        self.assertTrue(uItem.isBinaryContent)
        uItem = item.GetIceItemForUri(item.iceContext, "/one/test1.pdf")
        self.assertTrue(uItem.isBinaryContent)

    def testGetBinaryContent(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test data")
        item._setImage("test.png", "Pic")
        item._setRendition(".pdf", "PDF-data")
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.txt/extra")
        self.assertEquals(uItem.getBinaryContent(), ("test data", "text/plain"))
        #
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1_files/test.png/x")
        self.assertEquals(uItem.getBinaryContent(), ("Pic", "image/png"))
        #
        uItem = item.GetIceItemForUri(item.iceContext, "one/test1.pdf")
        self.assertEquals(uItem.getBinaryContent(), ("PDF-data", "application/pdf"))

    def testGetContent(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("test")
        content, mimeType = item.getContent()
        self.assertEquals(mimeType, "text/plain")
        # Note: This method has not yet been finished. Also not currently used
        #self.assertEquals(content, "-- ice htm data --")


    def testGetHtmlRendition(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt").write("x")
        #item._setRendition(".xhtml.body", "<html>data</html>")
        result = item.getHtmlRendition()
        htmlBody, title, page_toc, style = result
        #print "'%s', '%s', '%s', '%s'" % (htmlBody, title, page_toc, style)
        self.assertEquals(result, ("<html>/one/test1.txt</html>", "testingTitle", "", ""))

    def _zipFromTempDir(self, rep):
        item = self.getItem(rep, relPath="one/test.zip")
        fs = self.fs
        tempDir = fs.createTempDirectory()
        tempDir.write("one.txt", "One")
        tempDir.write("two.txt", "Two")
        item.zipFromTempDir(tempDir)
        tempDir.delete()

    def testZipFromTempDir(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test.zip")
        fs = self.fs
        tempDir = fs.createTempDirectory()
        tempDir.write("one.txt", "One")
        tempDir.write("two.txt", "Two")
        item.zipFromTempDir(tempDir)
        tempDir.delete()

    def testUnzipToTempDir(self):
        fs = self.fs
        rep = self.getRep()
        self._zipFromTempDir(rep)
        item = self.getItem(rep, relPath="one/test.zip")
        tempDir = item.unzipToTempDir()
        self.assertEquals(tempDir.list(), ["one.txt", "two.txt"])
        self.assertEquals(tempDir.read("one.txt"), "One")
        tempDir.delete()

    def testZipList(self):
        rep = self.getRep()
        self._zipFromTempDir(rep)
        item = self.getItem(rep, relPath="one/test.zip")
        self.assertEquals(item.zipList(), ["one.txt", "two.txt"])

    def testExtractFromZip(self):
        rep = self.getRep()
        self._zipFromTempDir(rep)
        item = self.getItem(rep, relPath="one/test.zip")
        self.assertEquals(item.extractFromZip("one.txt"), "One")

    def testReplaceInZip(self):
        replacementData = "Testing 1 replacement"
        rep = self.getRep()
        self._zipFromTempDir(rep)
        item = self.getItem(rep, relPath="one/test.zip")
        item.replaceInZip("one.txt", replacementData)
        item = self.getItem(rep, relPath="one/test.zip")
        self.assertEquals(item.extractFromZip("one.txt"), replacementData)

    def testIsPackageRoot(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="packages/one/subDir/test1.txt").write("x")
        self.getItem(rep, relPath="packages/one").setMeta("manifest", "dummy manifest")
        self.assertFalse(item.isPackageRoot)
        itemOne = self.getItem(rep, relPath="packages/one/")
        self.assertTrue(itemOne.isPackageRoot)
        item = self.getItem(rep, relPath="packages/one/subDir")
        self.assertFalse(item.isPackageRoot)
        item = self.getItem(rep, relPath="packages/")
        self.assertFalse(item.isPackageRoot)

    def testInPackage(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="packages/one/subDir/test1.txt").write("x")
        self.getItem(rep, relPath="packages/one").setMeta("manifest", "dummy manifest")
        self.assertTrue(item.inPackage)
        itemOne = self.getItem(rep, relPath="packages/one/")
        self.assertTrue(item.inPackage)
        item = self.getItem(rep, relPath="packages/one/subDir")
        self.assertTrue(item.inPackage)
        item = self.getItem(rep, relPath="packages/")
        self.assertFalse(item.inPackage)

    def testPackageCopy(self):      #?????????????
        rep = self.getRep()
        item = self.getItem(rep, relPath="one/test1.txt")

    def testIndexesNotVersioned(self):
        rep = self.getRep()
        #item = self.getItem(rep, relPath="test1.txt").write("x")
        item = self.getItem(rep, relPath=".indexes/test.txt").write("x")
        item = self.getItem(rep, relPath=".indexes")
        self.assertFalse(item.isVersioned)

    def testGetCompleteStatus(self):
        rep = self.getRep()
        rep2 = self.getRep2()
        item = self.getItem(rep, relPath="packages/test1.txt").write("x")
        item.setMeta("p", "1")
        item.getStatus(False)
        #item._commit()
        self.getItem(rep, relPath=".")._commit()
        
        item2 = self.getItem(rep2, relPath=".")
        item2._update(1)
        item2 = self.getItem(rep2, relPath="packages/test1.txt")
        #item2.write("two")     # should pickup any property changes as well
        item2.setMeta("p", "2")
        item2._commit()
        itemt = self.getItem(rep2, relPath="packages/test2.txt").write("2")
        itemt._commit()

        item = self.getItem(rep, relPath="packages/test1.txt")
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "Out-of-date")
        item.write("xxx")
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "Modified out-of-date")
        self.getItem(rep, relPath="packages")._update(1)
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "Modified")
        item._commit()
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "In sync")

        # Test getCompleteStatus for directories as well
        item = self.getItem(rep, relPath="packages/")
        item._commit()
        item._update(1)
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "In sync")

        itemt = self.getItem(rep2, relPath="packages/")
        itemt.setMeta("dMeta", "2")
        itemt._commit()

        item = self.getItem(rep, relPath="packages/")
        item._commit()
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "Out-of-date")

        item.setMeta("p2", "2")
        item.getStatus(True)
        s = item.getCompleteStatus()
        self.assertEquals(s, "Modified out-of-date")


        # self.getItem(rep, relPath="packages/one").setMeta("manifest", "dummy manifest")
        # self.assertFalse(item.isPackageRoot)
        # self.assertTrue(item.inPackage)
    def testAsyncUpdate(self):
        # asyncUpdate(updateItemList):
        rep = self.getRep()
        rep2 = self.getRep2()
        self.getItem(rep2, "dir/one.txt").write("one")
        self.getItem(rep2, "dir/two.txt").write("one")
        # package
        self.getItem(rep2, relPath="packages/one/test.txt").write("data")
        # packages/one is a package
        self.getItem(rep2, relPath="packages/one").setMeta("manifest", "dummy manifest")
        self.getItem(rep2, "")._commit()
        
        item = self.getItem(rep, "")
        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out        # comment out this line to see feedback
        job = item.asyncUpdate()
        item = self.getItem(rep, "")        ##
        while not job.isFinished: pass
        sys.stdout = stdout
        #print "read='%s'" % out.getvalue()

        paths = []
        for i in item.listItems():
            #print i
            paths.append(i.relPath)
            for i in i.listItems():
                #print "  %s" % i
                paths.append(i.relPath)
                for i in i.listItems():
                    #print "    %s" % i
                    paths.append(i.relPath)
        expected = ["/dir/", "/dir/one.txt", "/dir/two.txt", "/packages/", \
                    "/packages/one/", "/packages/one/test.txt"]
        self.assertEquals(paths, expected)

    
    def testAsyncRender(self):
        # asyncRender(itemList=None, force=False, skipBooks=False)
        rep = self.getRep()
        #rep2 = self.getRep2()
        item1 = self.getItem(rep, "one/one.txt").write("x")
        item2 = self.getItem(rep, "one/two.txt").write("x")
        item = self.getItem(rep, "one")
        self.assertEquals((item1.needsUpdating, item2.needsUpdating), (True, True))

        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out        # comment out this line to see feedback
        job = item.asyncRender(force=False, skipBooks=False)
        while not job.isFinished: pass
        sys.stdout = stdout
        #print "read='%s'" % out.getvalue()

        self.assertEquals((item1.needsUpdating, item2.needsUpdating), (False, False))
        #job = item.asyncRender(force=False, skipBooks=False)
        #while not job.isFinished: pass

    def testAsyncSync(self):
        # asyncSync(itemList=None, force=False, skipBooks=True)
        rep = self.getRep()
        rep2 = self.getRep2()
        self.getItem(rep2, "dir/one.txt").write("x")
        item2 = self.getItem(rep2, "")
        item = self.getItem(rep, "dir")
        item2._commit()
        item._update()
        self.getItem(rep2, "dir/two.txt").write("x")
        item2._commit()
        self.getItem(rep2, "dir/subDir/two.txt").write("x")
        self.getItem(rep2, "dir2/test.txt").write("x")

        self.getItem(rep, "dir/one.txt").write("y")     # modified confict
        self.getItem(rep, "dir/two.txt").write("y")     # added confict
        self.getItem(rep, "dir/three.txt").write("y")   # The only item to be rendered
        
        stdout = sys.stdout
        out = StringIO()
        sys.stdout = out        # comment out this line to see feedback
        job = item.parentItem.asyncSync()
        while not job.isFinished: pass
        for i in item.listItems():
            print i, i.isVersioned, i.getStatus()
            if i.isVersioned:
                self.assertEquals(i.getStatus().status, "normal")
            else:
                self.assertTrue(i.name.startswith("MyChanges_"))        
        sys.stdout = stdout
        #print "read='%s'" % out.getvalue()

    def testX(self):
        rep = self.getRep()
        rep2 = self.getRep2()
        self.getItem(rep2, "dir/one.txt").write("x")
        item2 = self.getItem(rep2, "")
        item2._commit()
        self.getItem(rep2, "dir/two.txt").write("x")
        item = self.getItem(rep, "")
        item._update(1)
        self.assertEquals(item.getStatus().status, "normal")



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())
