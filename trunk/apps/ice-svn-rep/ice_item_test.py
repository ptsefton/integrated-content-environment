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

import os, sys
import types, string
import re
import time
sys.path.append("../ice")
from ice_common import IceCommon


from ice_item import IceItem
from ice_rep2 import IceRepository



testDataDir = "testData/"
testSvnRepZip = testDataDir + "svnTestRep.zip"
testSvnRep = testDataDir + "svnTempRep"
testRep = testDataDir + "tempRep"
testOdt = "testData/test.odt"


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
    

class MockIceRender(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.renderMethods = {".txt":self.__textRender}
        self.postRenderPlugin = None
    
    def __textRender(self, item):
        #print "__textRender()"
        convertedData = self.iceContext.ConvertedData()
        convertedData.addMeta("title", "testingTitle")
        convertedData.addMeta("absFile", item._absPath)
        convertedData.addMeta("renderWith", "__textRender")
        return convertedData
    
    def getRenderableFrom(self, ext):
        return []
    
    def getRenderableTypes(self, ext):
        return []
    
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
        self.fs = IceCommon.fs
    
    
    def setUp(self):
        pass
    
    
    def tearDown(self):
        pass
    
    
    def getRep(self):
        iceContext = IceCommon.IceContext(None)
        output = iceContext.output
        iceContext.output = None
        setupRep(self.fs)
        rep = IceRepository(iceContext, testRep, repUrl=repUrl, 
                            iceRender=MockIceRender(iceContext))
        iceContext.output = output
        return rep
    
    
    def getItem(self, rep=None, relPath="/"):
        if rep is None:
            rep = self.getRep(self.fs)
        item = rep.getItem(relPath)
        return item
    
    
    def testRootItemProperties(self):
        rep = self.getRep()
        
        item = self.getItem(rep, relPath="/")
        #print item.toString()
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
        self.assertEquals(len(content), 3682)
    
    
    def testProperties(self):
        rep = self.getRep()
        item = self.getItem(rep, relPath="testDir/test.odt")
        data = IceCommon.fs.readFile(testOdt)
        item.write(data)
        self.assertEquals(item.relPath, "/testDir/test.odt")
        self.assertTrue(item._propAbsPath.endswith("/testDir/.ice/test.odt"))
        self.assertEquals(len(item.guid), 32)
        self.assertFalse(item.convertFlag)
        self.assertFalse(item.hasPdf)
        self.assertFalse(item.hasHtml)
        self.assertEquals(item.hasSlide, None)
        self.assertFalse(item.needsUpdating)
        self.assertEquals(item.tags, [])
        self.assertEquals(item.inlineAnnotations, None)
        self.assertEquals(item.bookInfo, None)
        self.assertEquals(item.lastChangedRevisionNumber, -1)
        self.assertFalse(item.isRenderable)
        parent = item.parentItem
        #setConvertedData()
        cd = item.iceContext.ConvertedData()
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


    def testTags(self):
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
        dirITem = None
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
        self.assertTrue(item._propAbsPath.endswith("/tempRep/.ice/__dir__"))
        
        item = self.getItem(rep, relPath="oneLevel")
        self.assertTrue(item._propAbsPath is None)
        self.assertFalse(item.exists)
        item.makeDirectory()
        self.assertTrue(item._propAbsPath.endswith("/tempRep/oneLevel/.ice/__dir__"))
        self.assertTrue(item.isDirectory)
        
        # make two or more levels test
        item = self.getItem(rep, relPath="one/two/three/")
        self.assertFalse(item.exists)
        self.assertTrue(item._propAbsPath is None)
        item.makeDirectory()
        self.assertTrue(item.isDirectory)
        self.assertEquals(item.relPath, "/one/two/three/")
        self.assertEquals(item.name, "three")
        self.assertTrue(item._propAbsPath.endswith("/tempRep/one/two/three/.ice/__dir__"))
        item = self.getItem(rep, relPath="one/two")
        self.assertTrue(item.isDirectory)
        self.assertTrue(item._propAbsPath.endswith("/tempRep/one/two/.ice/__dir__"))
        item = self.getItem(rep, relPath="one/")
        self.assertTrue(item.isDirectory)
        self.assertTrue(item._propAbsPath.endswith("/tempRep/one/.ice/__dir__"))
        
        # test making directories as a result of creating a new file
        item = self.getItem(rep, relPath="/sdir/one/test.txt")
        self.assertFalse(item.exists)
        item.write("Testing")
        self.assertTrue(item.isFile)
        self.assertTrue(item._propAbsPath.endswith("/tempRep/sdir/one/.ice/test.txt"))
        item = self.getItem(rep, relPath="/sdir")
        self.assertTrue(item.isDirectory)
        self.assertTrue(item._propAbsPath.endswith("/tempRep/sdir/.ice/__dir__"))
    
    
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
        #    print i.name, i.exists, i.relPath
    
    
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
        #    print i.name, i.vcStatusStr, i.isVersioned, i.lastChangedRevisionNumber
        self.assertEquals(items[0].lastChangedRevisionNumber, 2)
        self.assertEquals(items[1].lastChangedRevisionNumber, 3)
        self.assertEquals(items[2].lastChangedRevisionNumber, -1)
        
        item = self.getItem(rep, relPath="/one")
        self.assertEquals(item.lastChangedRevisionNumber, 3)
    
    
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
        self.assertTrue(rootItems[0].isDirectory)
        self.assertTrue(rootItems[0].isMissing)
        #for i in rootItems:
        #    print i, i.isDirectory, i.isMissing
        #print
        
        itemOne = self.getItem(rep, relPath="one")
        self.assertTrue(itemOne.isDirectory)
        self.assertTrue(itemOne.isMissing)
        #print itemOne, itemOne.isDirectory
        
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
        item = self.getItem(rep, relPath="one/two/three/test.txt").write("test")
        item = self.getItem(rep, relPath="one/two/test.txt").write("test")
        l = []
        for listItems in rootItem.walk():
            for i in listItems:
                #print i.relPath, i.name
                l.append(i.name)
        self.assertEquals(l, ["one", "two", "test.txt", "three", "test.txt"])
        
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
    
    
    def testGetUpdateList(self):
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
        l = item2._getToBeUpdatedList()
        self.assertEquals(len(l), 0)
        #for i in l:
        #    print i.name
        item1.write("Testing one")
        item1._commit()
        self.getItem(rep, relPath="/one/dir3/test.txt").write("test")._commit()
        #print "---"
        l = item2._getToBeUpdatedList()
        self.assertEquals(len(l), 3)
        #print "--"
        #for i in l:
        #    print i.relPath, i.name
        l = item2._getToBeUpdatedList(includeMissing=True)
        self.assertEquals(len(l), 4)
        
        l = item2._getToBeUpdatedList(includeMissing=False)
        for i in l:
            i._update()
        l = item2._getToBeUpdatedList(includeMissing=True)
        self.assertEquals(len(l), 1)
        
        for i in l:
            i._update()
        l = item2._getToBeUpdatedList(includeMissing=True)
        self.assertEquals(len(l), 0)
    
    
    def testRender(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("testing text")
        item1.render()
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
    
    
    def testRemove(self):
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
        item.remove()
        
        item1 = self.getItem(rep, relPath="one")
        #for i in item1.listItems(): print i
    
    
    def testDelete(self):
        rep = self.getRep()
        item1 = self.getItem(rep, relPath="one/two/three/test1.txt")
        item1.write("test")
    
    
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
    
    
    def testRootSkinFake(self):
        skin = "skin/"
        d = {skin+"test1.txt":"One", skin+"subDir/test2.txt":"Two"}
        rep = self.getRep()
        fs = rep.fs
        fs.updateFakeFiles(d)
        self.assertTrue(fs.exists(skin))
        self.assertTrue(fs.isDirectory(skin))
        self.assertEquals(fs.list(skin), ["test1.txt", "subDir/"])
        
        skinItem = self.getItem(rep, skin)
        self.assertTrue(skinItem.exists)
        self.assertTrue(skinItem.isDirectory)
        
        print "---"
        print [i.relPath for i in skinItem.listItems()]
        
        item1 = self.getItem(rep, skin+"test1.txt")
        item2 = self.getItem(rep, skin+"subDir/test2.txt")
        print item1.relPath, item1.isFile, item1.read()
        print item2.relPath, item2.isFile, item2.read()
    
    
    def xtestX(self):
        rep = self.getRep()





if __name__ == "__main__":
    IceCommon.runUnitTests(locals())
