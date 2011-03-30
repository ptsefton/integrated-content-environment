#!/usr/bn/env python
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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
sys.path.append("../ice")
from ice_common import IceCommon

from svn_rep import *
ListItem.IceCommon = IceCommon      # temp

import tempfile


docNotes = """
=== Public Methods ===
__init__(basePath=None, svnUrl=None)
setGetUsernamePasswordCallback(callback)
login(username=None, password=None, callback=None, retries=None)
isAuthenticated()
logout()
createSvnFileRep(fileUrl)
checkoutRep(repUrl, destPath)
cleanup(path=None)

revert(path, recurse=True)
delete(path)
mkdir(path, message="mkdir")
move(sourcePath, destinationPath)
copy(sourcePath, destinationPath)
export(sourcePath, destinationPath)

list(path, recurse=False, update=False, ignore=False)
add(path, recurse=True)
update(path, recurse=True)
commit(path, recurse=True, message="commit")
"""

fs = IceCommon.FileSystem(".")
testFSRepZip = "testFSRep.zip"
tempFSRep = "tempFSRep"
tempFSRepUrl = ""
if IceCommon.system.isWindows:
    tempFSRepUrl = "file:///" + IceCommon.fs.join(IceCommon.fs.absolutePath("."), tempFSRep)
else:
    tempFSRepUrl = "file://" + IceCommon.fs.join(IceCommon.fs.absolutePath("."), tempFSRep)
tempRepPath = "tempRep"

# TempRep directories (content)
# course_content/
#       Study_Schedule.odt
# subDir/
#       subSubDir/
#               Test1.txt
#       Test1.txt
#       Test2.txt
# test.jpg
# Test.txt
    
def createTempFSRep():
    IceCommon.fs.unzipToDirectory(testFSRepZip, tempFSRep)

def removeTempRep():
    if not IceCommon.system.isWindows:
        IceCommon.fs.delete(tempRepPath)
    else:
        try:
            IceCommon.fs.delete(tempRepPath)
        except:
            pass

def removeTempFSRep():
    IceCommon.fs.delete(tempFSRep)


class MockRep(object):
    def __init__(self, fs):
        self.fs = fs
#        self.basePath = basePath
#        self.repUrl = repUrl
#        self.render = iceRender
#        self.name = name


class SvnRepTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        self.sRep = None
        self.client = None
        self.fs = None
        self.recreateFSRep = True
        self.recreateTempRep = True
        self.cleanup = False
    
    def setUp(self):
        # Make/setup self.sRep (with a basePath of tempRepPath)
        # Also set self.__fs to tempRepPath
        if self.recreateFSRep:
            removeTempFSRep()
            createTempFSRep()
        
        if IceCommon.system.isWindows:
            global tempRepPath
            tempRepPath = tempfile.mkdtemp()
        
        self.client = pysvn.Client()
        if self.recreateTempRep:
            removeTempRep()
            self.client.checkout(url=tempFSRepUrl + "/TestRep", path=tempRepPath, recurse=True)
        iceContext = IceCommon.IceContext
        self.rep = MockRep(IceCommon.FileSystem(tempRepPath))
        iceContext.rep = self.rep
        self.sRep = SvnRep(iceContext, basePath=tempRepPath, 
                        svnUrl=tempFSRepUrl + "/TestRep")
        if self.recreateTempRep==False:
            self.revert()
        self.fs = IceCommon.FileSystem(tempRepPath)
    
    def tearDown(self):
        if self.cleanup:
            if self.recreateFSRep:
                removeTempFSRep()
            if self.recreateTempRep:
                removeTempRep()
        self.recreateFSRep = True
        self.recreateTempRep = True
    
    def revert(self):
        # Quick cleanup (but only if no commits have been done)
        self.client.revert(tempRepPath, recurse=True)
    
    # Helper method
    def getListItem(self, path):
        absPath = self.fs.absolutePath(path)
        listItem = self.sRep.statusList(absPath)[-1]
        return listItem
    
    
    def testStatusList(self):
        #statusList(path)
        r = self.sRep
        #basePath = "testRep"
        okPath = "one/test.txt"
        ignoreFilename = "test1.tmp"
        self.rep.fs.writeFile(okPath, "test")
        self.rep.fs.writeFile(ignoreFilename, "test")
        self.rep.fs.writeFile("newAdded.txt", "test")
        self.rep.fs.writeFile("subDir/test1.txt", "one1")
        self.rep.fs.delete(self.rep.fs.absolutePath("test.jpg"))
        self.client.add(self.fs.absolutePath("newAdded.txt"))
        absBasePath = self.rep.fs.absolutePath()
        listItems = r.statusList(absBasePath)
        self.assertEquals(len(listItems), 10)
        self.assertEquals(listItems[-1].name, ".")
        self.assertTrue(listItems[0].isIgnored)
        self.assertFalse(listItems[3].isVersioned)
        self.assertEquals(str(listItems[4].status), "Added")
        
        # Test statusList for an item that is not a working copy 
        #   e.g. in a directory that is not under version control
        self.rep.fs.writeFile("newPath/test.txt", "testing")
        listItems = r.statusList(self.fs.absolutePath("newPath/test.txt"))
        status = listItems[-1]   # or [0] - should be the same
        self.assertFalse(status.isVersioned)
        self.assertEquals(status.status, ItemStatus.NONE)
        
        #print absBasePath
        #for listItem in listItems:
        #    print listItem
    
    
    def xtestRevStatus(self):
        #revInfo(path, includeServer=False)
        time.sleep(0.5)
        r = self.sRep
        test = self.fs.absolutePath("Test.txt")
        revInfo = r.revInfo(test)
        #print revInfo
        revInfo = r.revInfo(test, True)
        self.assertEquals(revInfo.lastChangedRevNum, 1)
        self.fs.writeFile("Test.txt", "Changed")
        r.commit(test)
        revInfo = r.revInfo(test, True)
        self.assertEquals(revInfo.lastChangedRevNum, 8)
        
        #print revInfo
        
        # includeServer=True
        # subDir/
        #       subSubDir/
        #               Test1.txt
        #       Test1.txt
        #       Test2.txt
        self.fs.copy("subDir", "subDirB")           # make two checked out repositories
        file1 = "subDir/Test1.txt"
        file2 = "subDir/Test2.txt"
        fileB1 = "subDirB/Test1.txt"
        fileB2 = "subDirB/Test2.txt"
        absFile1 = self.fs.absolutePath(file1)
        absFile2 = self.fs.absolutePath(file2)
        absFileB1 = self.fs.absolutePath(fileB1)
        absFileB2 = self.fs.absolutePath(fileB2)
        
        revInfo = r.revInfo(absFile1, True)
        self.assertEquals(revInfo.revNum, 7)
        self.assertEquals(revInfo.lastChangedRevNum, 2)
        self.assertEquals(revInfo.reposLastChangedRevNum, 2)
        self.assertFalse(revInfo.isOutOfDate)
        # Now change the B copy & commit it
        self.fs.writeFile(absFileB1, "changesB1\n")
        r.commit(absFileB1)
        revInfo = r.revInfo(absFileB1, True)
        self.assertEquals(revInfo.revNum, 9)
        self.assertEquals(revInfo.reposRevNum, 9)
        self.assertEquals(revInfo.lastChangedRevNum, 9)
        self.assertEquals(revInfo.reposLastChangedRevNum, 9)
        # Now check 'original' again
        revInfo = r.revInfo(absFile1, True)
        self.assertEquals(revInfo.revNum, 7)
        self.assertEquals(revInfo.reposRevNum, 9)
        self.assertEquals(revInfo.lastChangedRevNum, 2)
        self.assertEquals(revInfo.reposLastChangedRevNum, 9)
        self.assertTrue(revInfo.isOutOfDate)
        # Update 'original' and check again
        r.update(absFile1)
        revInfo = r.revInfo(absFile1, True)
        self.assertEquals(revInfo.revNum, 9)
        self.assertEquals(revInfo.reposRevNum, 9)
        self.assertEquals(revInfo.lastChangedRevNum, 9)
        self.assertEquals(revInfo.reposLastChangedRevNum, 9)
        self.assertFalse(revInfo.isOutOfDate)
        #
        absPath = self.fs.absolutePath("subDirB")
        revInfo = r.revInfo(absPath, True)
        self.assertEquals(revInfo.reposRevNum, 9)
        self.assertEquals(revInfo.lastChangedRevNum, 2)
        self.assertEquals(revInfo.reposLastChangedRevNum, 9)
        self.assertTrue(revInfo.isOutOfDate)
        #print revInfo
    
    def testAdd(self):
        r = self.sRep
        ignorePath = "one/.cache/test.txt"
        ignoreFilename = "one/test.tmp"
        okPath = "one/test.txt"
        self.fs.writeFile(ignorePath, "test")
        self.fs.writeFile(ignoreFilename, "test")
        self.fs.writeFile(okPath, "test")
        basePath = "one"
        absBasePath = self.fs.absolutePath(basePath)
        resultReport = r.add(absBasePath)
        #if successfully added
        self.assertEqual(len(resultReport), 1)
        #self.assertTrue(resultReport[0], ["Added 'c:/docume~1/octalina/locals~1/temp/tmpauw5rt/one'"])
        revInfo = r.revInfo(absBasePath, True)
        self.assertEquals(revInfo.revNum, 0)
        self.assertEquals(revInfo.reposRevNum, -1)
        self.assertEquals(revInfo.lastChangedRevNum, -1)
        self.assertEquals(revInfo.reposLastChangedRevNum, -1)
        self.assertFalse(revInfo.isOutOfDate)
        
        self.revert()
        resultReport = r.add([self.fs.absolutePath(ignorePath), 
                                self.fs.absolutePath(ignoreFilename), 
                                self.fs.absolutePath(okPath)], results=[])
        self.assertEqual(len(resultReport), 2)
        self.assertTrue(resultReport[0].startswith("Added parent "))
        
        # Add children
        absPath1 = self.fs.absolutePath("subDir")
        self.fs.writeFile("subDir/one/two.txt", "two")
        childFileAbs = self.fs.absolutePath("subDir/one/two.txt")
        resultReport = r.add(absPath1)
        self.assertEqual(len(resultReport), 2)  #the child will be automatically added
        #self.assertEqual(resultReport[0], "Added 'c:/docume~1/octalina/locals~1/temp/tmprbageh/subDir/one'")
        #check if child is versioned and added
        childRevInfo = r.revInfo(childFileAbs)
        self.assertEqual(childRevInfo.revNum, 0)
        self.assertEqual(childRevInfo.lastChangedRevNum, -1)
        self.assertEqual(childRevInfo.reposRevNum, -1)
        self.assertEqual(childRevInfo.reposLastChangedRevNum, -1)
        listItem = self.getListItem("subDir/one/two.txt")
        self.assertTrue(listItem.isVersioned)
        self.assertEquals(str(listItem.status), "Added")

        # adding add sub item in a already versioned folder
        self.fs.writeFile("subDir/one/three.txt", "three")
        resultReport = r.add(absPath1)
        self.assertEqual(len(resultReport), 3)
        listItem = self.getListItem("subDir/one/three.txt")
        self.assertTrue(listItem.isVersioned)
        self.assertEquals(str(listItem.status), "Added")
        
        # Add children - children
        absPath2 = self.fs.absolutePath("subDir2")
        self.fs.writeFile("subDir2/one/two.txt", "two")
        resultReport = r.add(absPath2)
        self.assertEqual(len(resultReport), 4)
        # Add parent - parent
        self.fs.writeFile("subDir3/one/two.txt", "two")
        self.fs.writeFile("subDir3/two.txt", "two")     #make sure this is not added when parent is added
        absPath3 = self.fs.absolutePath("subDir3/one/two.txt")
        resultReport = r.add(absPath3, results=[])
        self.assertEqual(len(resultReport), 3)
        #check the unversioned file
        listItem = self.getListItem("subDir3/two.txt")
        self.assertFalse(listItem.isVersioned)
        self.assertEquals(str(listItem.status), "Unversioned")
        
        self.recreateFSRep = False      # Test optimizing (no need to recreate the FSRepositiory
        #self.recreateTempRep = False    # Test optimizing (no need to re-checkout, just a revert will do)
    
    
    def testCommit(self):
        # Note: you must add any items that are to be committed 
        #   (unversioned items are not to be committed)
        #commit(paths, message="commit", recurse=True, actionResults=None)
        #   Note: commits only items that have been added or have been modified.
        r = self.sRep
        
        # Commit an added item and added parents
        itemPath = "new/one/test.txt"
        self.fs.writeFile(itemPath, "test")
        absItemPath = self.fs.absolutePath(itemPath)
        resultReport = r.add(absItemPath, results=[])
        self.assertEquals(len(resultReport), 3)
        resultReport = r.commit(absItemPath)
        self.assertTrue(resultReport.isAllOK)
        listItems = r.statusList(absItemPath)
        self.assertEquals(len(listItems), 1)
        listItem = listItems[0]
        self.assertTrue(listItem.status, ItemStatus.Normal)
        
        # Commit a modified item
        self.fs.writeFile(itemPath, "testing")
        listItem = r.statusList(absItemPath)[0]
        self.assertEquals(listItem.status, ItemStatus.Modified)
        resultReport = r.commit(absItemPath)
        listItem = r.statusList(absItemPath)[0]
        self.assertEquals(listItem.status, ItemStatus.Normal)
        
        # Commit a missing item
        self.fs.delete(self.fs.absolutePath(itemPath))
        resultReport = r.commit(absItemPath)
        self.assertTrue(resultReport.isAllOK)
        
        # Make sure that a non-added item is not committed
        self.fs.makeDirectory("new")
        r.add(self.fs.absolutePath("new"), results=[], recurse=False)
        itemPath = "new/one/test2.txt"
        self.fs.writeFile(itemPath, "test")
        absItemPath = self.fs.absolutePath(itemPath)
        resultReport = r.commit(self.fs.absolutePath("new"), recurse=False)
        listItem = r.statusList(absItemPath)[0]
        resultReport = r.commit(absItemPath) #will fail as the item is not added yet
        listItem = r.statusList(absItemPath)[0]
        self.assertFalse(listItem.isVersioned)
    
    
    def testDelete(self):
        #self.cleanup = False
        r = self.sRep
        file = "subDir/Test1.txt"
        absFile = self.fs.absolutePath(file)
        r.delete(absFile)
        status = self.getListItem(file)
        self.assertEqual(str(status.status), "Deleted")
        
        # delete directory
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        r.delete(absPath)
        status = self.getListItem(path)
        self.assertEqual(str(status.status), "Deleted")
        
        file = "subDir/Test2.txt"
        absFile = self.fs.absolutePath(file)
        status = self.getListItem(file)
        self.assertEqual(str(status.status), "Deleted")
    
    
    def testRevert(self):
        #self.cleanup = False
        r = self.sRep
        file = "subDir/Test2.txt"
        absFile = self.fs.absolutePath(file)
        r.delete(absFile)
        r.revert(absFile)
        status = self.getListItem(file)
        self.assertEqual(str(status.status), "Normal")
        data1 = self.fs.readFile(file)
        self.fs.writeFile(file, "Testing revert")
        r.revert(absFile)
        data2 = self.fs.readFile(file)
        self.assertEqual(data2, data1)
        
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        r.delete(absPath)
        r.revert(absFile)
        data2 = self.fs.readFile(file)
        self.assertEqual(data2, data1)
    
    
    def testUpdate(self):
        #self.cleanup = False
        r = self.sRep
        # subDir/
        #       subSubDir/
        #               Test1.txt
        #       Test1.txt
        #       Test2.txt
        self.fs.copy("subDir", "subDir2")           # make two checked out repositories
        
        # Simple update test
        absPath1 = self.fs.absolutePath("subDir")
        absPath2 = self.fs.absolutePath("subDir2")
##        self.fs.writeFile("subDir/one/one.txt", "one")
##        self.assertTrue(r.add(absPath1).isAllOK)
##        self.assertTrue(r.commit(absPath1).isAllOK)
##        resultReport = r.update(absPath2)
##        self.assertTrue(resultReport.isAllOK)
##        
##        # Test update (non-added) conflicting file
##        absPath1 = self.fs.absolutePath("subDir")
##        absPath2 = self.fs.absolutePath("subDir2")
##        self.fs.writeFile("subDir/one/two.txt", "two")
##        self.fs.writeFile("subDir2/one/two.txt", "two2")
##        # Add & commit
##        actionReport = r.add(absPath1)
##        self.assertTrue(actionReport.isAllOK)
##        self.assertTrue(r.commit(absPath1).isAllOK)
##        r.add(absPath2)
##        listItem = self.getListItem("subDir/one/two.txt")
##        self.assertEqual(listItem.status, ItemStatus.Normal)
##        
##        resultReport = r.update(absPath2)
##        self.assertTrue(resultReport.isWarning)
##        self.assertFalse(resultReport.isError)
##        self.assertFalse(resultReport.isAllOK)
##        action = resultReport.actions[0]
##        #print action
##        renamedTo = action.info.get("renamedTo", "")
##        self.assertEquals(renamedTo, "myChanges_two.txt")
        
        # Test update (added) conflicting file
        ## /one
        self.fs.writeFile("subDir/three.dat", "three")
        self.fs.writeFile("subDir2/three.dat", "three3")
        self.assertTrue(len(r.add(absPath1)))
        self.assertTrue(len(r.add(absPath2)))
        self.assertTrue(r.commit(absPath1).isAllOK)
        listItem = self.getListItem(absPath1)
        self.assertEqual(str(listItem.status), "Normal")
        
        resultReport = r.update(absPath2)
        self.assertEqual(resultReport.count, 2)
        self.assertTrue(resultReport.isWarning)
        self.assertFalse(resultReport.isError)
        
        # Test update and then 'modified' conflict file
        self.fs.writeFile("subDir/three.dat", "three mod")
        self.fs.writeFile("subDir2/three.dat", "three3 mod")
        listItem = self.getListItem("subDir/three.dat")
        self.assertEqual(str(listItem.status), "Modified")
        listItem = self.getListItem("subDir2/three.dat")
        self.assertEqual(str(listItem.status), "Modified")
        self.assertTrue(r.commit(absPath1).isAllOK)
        time.sleep(1)
        listItem = self.getListItem("subDir/three.dat")
        self.assertEqual(str(listItem.status), "Normal")
        #
        self.fs.delete(self.fs.absolutePath("subDir2/myChanges_three.dat"))
        listItem = self.getListItem("subDir2/three.dat")
        resultReport = r.update(absPath2)           # update modified conflict
        self.assertEquals(self.fs.readFile("subDir2/myChanges_three.dat"), "three3 mod")
        self.assertEqual(resultReport.count, 2)
        self.assertTrue(resultReport.isWarning)
        self.assertFalse(resultReport.isError)
        action = resultReport.actions[0]
        renamedTo = action.info.get("renamedTo", "")
        self.assertEquals(renamedTo, "myChanges_three.dat")
        
        # Test update (added) conflicting directory
        self.fs.writeFile("subDir/dir/three.dat", "three")
        self.fs.writeFile("subDir2/dir/three.dat", "three3")
        self.assertTrue(len(r.add(absPath1)))
        listItem = self.getListItem("subDir/dir/three.dat")
        self.assertEqual(str(listItem.status), "Added")
        self.assertTrue(len(r.add(absPath2)))
        self.assertTrue(r.commit(absPath1).isAllOK)
        listItem = self.getListItem("subDir/dir/three.dat")
        self.assertEqual(str(listItem.status), "Normal")
        
        #print "Updating"
        resultReport = r.update(absPath2)
        #print resultReport
        self.assertEqual(resultReport.count, 1)
        #self.assertTrue(resultReport.isError)
        self.assertFalse(resultReport.isError)
        self.assertFalse(resultReport.isWarning)
    
    
    
    
    
    
    def testCopy(self):
        #self.cleanup = False
        r = self.sRep
        file = "Test.txt"
        absFile = self.fs.absolutePath(file)
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        tFile = "toFile.txt"
        absTFile = self.fs.absolutePath(tFile)
        tPath = "subDirTo"
        absTPath = self.fs.absolutePath(tPath)
        
        r.copy(absFile, absTFile)
        status = r.getStatus(absTFile)
        self.assertEqual(str(status.statusStr), "added")
        status = self.getListItem(absTFile)
        self.assertEqual(str(status.status), "Added")
        
        r.copy(absPath, absTPath)
        listItems = r.list(absPath)
        listItems2 = r.list(absTPath)
        self.assertEqual(len(listItems), len(listItems2))
    
    
    def testMove(self):
        #self.cleanup = False
        r = self.sRep
        file = "subDir/Test2.txt"
        absFile = self.fs.absolutePath(file)
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        
        # Move file
        mFile = "subDir/TestM2.txt"
        absMFile = self.fs.absolutePath(mFile)
        r.move(absFile, absMFile)
        status = r.getStatus(absFile)
        self.assertTrue(str(status.statusStr), "Deleted")
        status = r.getStatus(absMFile)
        self.assertTrue(str(status.statusStr), "added")
        
        # Move directory
        mPath = "mSubDir/TestM2.txt"
        absMPath = self.fs.absolutePath(mPath)
        r.move(absPath, absMPath)
        listItems = r.list(absPath) #, recurse=True)
        self.assertEquals(listItems, [u'Test1.txt', u'Test2.txt', u'subSubDir/', u'./'])
        for listItem in listItems:
            status = r.getStatus(self.fs.join(absPath, listItem))
            self.assertTrue(status, "Deleted")
        #print "---"
        listItems = r.list(absMPath) #, recurse=True)
        self.assertEqual(len(listItems), 5)
        expected = [("Test1.txt", "Normal"), ("Test2.txt", "Deleted"), ("subSubDir/", "Normal"), 
                    ("TestM2.txt", "Added"), ("./", "Added"), \
                        ]
        statusList = []
        for listItem in listItems:
            status = r.getStatus(self.fs.join(absMPath, listItem))
            statusList.append((listItem, status))
        for x in range(5):
            self.assertEqual(statusList[x][0], expected[x][0])
            self.assertEqual(str(statusList[x][1]), (expected[x][1]).lower())
    
    def testCleanup(self):
        #self.cleanup = False
        r = self.sRep
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        r.cleanup(absPath)
    
    
    def testExport(self):
        #self.cleanup = False
        r = self.sRep
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        exPath = "export"
        absExPath = self.fs.absolutePath(exPath)
        r.export(absPath, absExPath)
        listItems = r.list(absExPath, recurse=True)
        for listItem in listItems:
            #print listItem.path, listItem.isversioned
            self.assertFalse(listItem.isversioned)
    
    
    def testGetRevision(self):
        #self.cleanup = False
        r = self.sRep
        path = "subDir"
        absPath = self.fs.absolutePath(path)
        rev = r.getRevision(absPath)
        self.assertEqual(rev, 7)
        #print "rev='%s'" % rev
        
        # IncludeUrl Revision info.
        #rev = (urlLastRev>rev.number(outOfDate), rev.number, urlLastRev, urlRev)
        outOfDate, rev, urlLastRev, urlRev = r.getRevision(absPath, includeUrl=True)
        #print outOfDate, rev, urlLastRev, urlRev
        self.assertFalse(outOfDate)
        self.assertEqual(rev, 7)
        self.assertEqual(urlLastRev, 2)
        self.assertEqual(urlRev, 7)
        
        self.fs.writeFile("subDir/newFile.txt", "testing")
        r.add(absPath)
        r.commit(absPath)
        outOfDate, rev, urlLastRev, urlRev = r.getRevision(absPath, includeUrl=True)
        #print outOfDate, rev, urlLastRev, urlRev
        self.assertTrue(outOfDate)
        self.assertEqual(rev, 7)
        self.assertEqual(urlLastRev, 8)
        self.assertEqual(urlRev, 8)
        
        r.update(absPath)
        outOfDate, rev, urlLastRev, urlRev = r.getRevision(absPath, includeUrl=True)
        #print outOfDate, rev, urlLastRev, urlRev
        self.assertFalse(outOfDate)
        self.assertEqual(rev, 8)
        self.assertEqual(urlLastRev, 8)
        self.assertEqual(urlRev, 8)
    
    

    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





