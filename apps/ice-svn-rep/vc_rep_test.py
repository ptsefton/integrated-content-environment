#!/usr/bin/env python
#
#    Copyright (C) 2009  Distance and e-Learning Centre,
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
sys.path.append("../ice")
from ice_common import IceCommon
import time
import pysvn

from vc_rep import VCRep

testDir = "tempTest"
testDataDir = "testData"


class VCRepTest(IceCommon.TestCase):
    #def __init__(self, name):
    #    IceCommon.TestCase.__init__(self, name)

    def setUp(self):
        fs = IceCommon.fs.clone(testDir + "/test")
        fs2 = IceCommon.fs.clone(testDir + "/test2")
        fs.delete("..")
        fs2.delete("..")
        zipFile = fs.absPath("../../%s/emptySvnRep.zip" % testDataDir)
        self.__repDir = fs.absPath("../SvnRep")
        fs.unzipToDirectory(zipFile, self.__repDir)
        client = pysvn.Client()
        client.checkout(url="file://"+self.__repDir, path=fs.absPath())
        self.vcRep = VCRep(fs)
        try:
            self.vcRep.getID(".")
            self.vcRep.commit(["."], "setup")
        except Exception, e:
            pass
        self.fs = fs
        self.fs2 = fs2
        self.__client = client

    def tearDown(self):
        pass

    def getTest2(self):
        self.__client.checkout(url="file://"+self.__repDir, path=self.fs2.absPath())
        self.vcRep2 = VCRep(self.fs2)
        return self.vcRep2

    
    #   add(path, depth=0)
    def testAdd(self):
        fs = self.fs
        rep = self.vcRep
        file1 = "one.txt"
        file2 = "subDir/two.txt"
        fs.writeFile(file1, "One")
        fs.writeFile(file2, "Two")
        rep.add(file1)
        rep.add(file2)
        fileStatus = rep.getStatus(file2)
        self.assertTrue(fileStatus.isFile, "Excepted it to be a file!")
        self.assertEquals(fileStatus.status, "added", "A status of added was excepted!")
        # What if the properties directory already exists?
        # e.g. someone has done a svn delete of the file (but not the properties and via versa)
        #       before and after these changes have been committed.
        #rep.commit([file1], "")  # will be recorded as deleted
        c = pysvn.Client()
        absPath = rep._absPath(file1)
        propAbsPath = rep._getPropDir(absPath)
        def test(commit=False):
            if commit: rep.commit([file1], "")
            id = rep.getID(file1)
            c.remove(absPath, force=True)
            if commit: c.checkin(absPath, " ")
            fs.write(file1, "data")
            rep.add(file1)
            fileStatus = rep.getStatus(file1)
            self.assertEquals(id, rep.getID(file1))
            self.assertEquals("added", fileStatus.status)
            c.remove(propAbsPath, force=True)
            if commit: c.checkin(propAbsPath, " ")
            rep.add(file1)
            self.assertTrue(id != rep.getID(file1))
        test()
        # same again but commit (checkin)
        test(True)


    def testAdd2(self):
    #   _absPath(path)
    #   _isVersioned(absPath)
    #   _getPropDir(absPath)
    #   _list(absPath, includeServer=False, _depth=None)
        fs = self.fs
        rep = self.vcRep
        # test adding parent directories and all property directories
        fs.writeFile("sDir/ssDir/one.txt", "One")
        rep.add("sDir/ssDir/one.txt")
        self.assertTrue(rep.isVersioned("sDir"))
        self.assertTrue(rep.isVersioned("sDir/.ice/__dir__"))
        self.assertTrue(rep.isVersioned("sDir/ssDir"))
        self.assertTrue(rep.isVersioned("sDir/ssDir/one.txt"))

        # test adding children and all property directories
        fs.writeFile("sDir2/ssDir/one.txt", "One")
        rep.add("sDir2")
        self.assertTrue(rep.isVersioned("sDir2"))
        self.assertTrue(rep.isVersioned("sDir2/ssDir"))
        self.assertTrue(rep.isVersioned("sDir2/ssDir/one.txt"))
        


    #   isVersioned(path)       # including .ice?
    def testIsVersioned(self):
        fs = self.fs
        rep = self.vcRep
        fs.writeFile("one.txt", "data")
        fs.writeFile("two.txt", "data")
        rep.add("one.txt")
        self.assertTrue(rep.isVersioned("one.txt"))
        self.assertFalse(rep.isVersioned("two.txt"))


    #   commit(paths, log_message)   depth=files, immediates, *empty, *infinity
    def testCommit(self):
        fs = self.fs
        rep = self.vcRep
        file = "subDir/one.txt"
        if True:
            fs.writeFile(file, "data")
            rep.add(file)
            rep.commit(file, "testing")
            statusList = rep.list("subDir/one.txt")
            fileStatus = rep.getStatus(file)
            self.assertEquals(fileStatus.status, "normal")
            # test/.ice test/.ice/__dir__
            self.assertEquals(rep._getStatusStr(".ice"), "normal")
            self.assertEquals(rep._getStatusStr(".ice/__dir__"), "normal")
        #
        dir = "subDir2"
        file = dir + "/test.one"
        fs.write(file, "one")
        rep.add(file)
        rep.commit([file], "")
        fileStatuses = rep.list(dir)
        for fileStatus in fileStatuses.values():
            self.assertEquals(fileStatus.status, "normal")
        #
        # Invalid state recovery test.
        if False:       ## currently I do not know how to recover from this!
                        ##  - with out the possibility of losing data.
            dir = "subDir3"
            file1 = dir + "/test.one"
            file2 = dir + "/test.two"
            fs.write(file1, "one")
            rep.add(file1)
            rep.commit([dir], "")
            # remove "subDir3/.ice"
            fs.delete(dir + "/.ice")
            fs.write(file2, "two")
            rep.add(file2)
            rep.commit([dir], "")
            fileStatuses = rep.list(dir)
            for fileStatus in fileStatuses.values():
                #self.assertEquals(fileStatus.status, "normal")
                pass

    #   update(paths, depth [,revision])
    def testUpdate(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        file = "subDir/one.txt"
        fs.writeFile(file, "data")
        rep.add(file)
        rep.commit([file], "testing")

        rep2.update(["."], depth=1)
        fs2.writeFile(file, "data2")
        rep2.commit([file], "testing")

        rep.update([file], depth=0)
        data = fs.readFile(file)
        self.assertEquals(data, "data2")
        # testing committing and updating of properties
        rep2.propSet(file, "p1", "pTest")
        rep2.commit([file], "testing")
        rep.update([file], depth=0)
        self.assertEquals(rep2.propGet(file, "p1"), "pTest")
        self.assertEquals(rep.propGet(file, "p1"), "pTest")


    #   revert(path)
    def testRevert(self):
        # Test reverting of properties as well
        fs = self.fs
        rep = self.vcRep
        file = "one.txt"
        fs.writeFile(file, "data")
        rep.add(file)
        rep.propSet(file, "p1", "v1")
        rep.commit([file], "testing")
        fs.writeFile(file, "data2")
        rep.propSet(file, "p1", "xxx")
        rep.propSet(file, "p2", "2")
        rep.revert(file)
        data = fs.readFile(file)
        self.assertEquals(data, "data")
        self.assertEquals(rep.propGet(file, "p1"), "v1")
        self.assertEquals(rep.propGet(file, "p2"), None)


    #   shelve(path)       # Shelve
    def testShelve(self):
        fs = self.fs
        rep = self.vcRep
        dir = "dir"
        file = dir + "/one.txt"
        fs.writeFile(file, "data")
        rep.add(dir)
        rep.propSet(file, "p1", "pv1")
        rep.commit([file], "testing")
        #    # list is not showing 'normal' status items!!!!!!!!!
        fileStatusList = rep.list(".")
        self.assertEquals(fileStatusList[dir].status, "normal")
        #
        rep.shelve(dir)
        # Note: must only be able to remove directories
        fileStatusList = rep.list(".")
        #for fileStatus in fileStatusList.values():
        #    print fileStatus
        self.assertEquals(fileStatusList[dir].status, "shelved")
        rep.update([dir], 1)
        self.assertEquals(fs.read(file), "data")
        fileStatusList = rep.list(".")
        self.assertEquals(fileStatusList[dir].status, "normal")
        p1 = rep.propGet(file, "p1")
        self.assertEquals(p1, "pv1")


    #   delete(path)
    def testDelete(self):
        fs = self.fs
        rep = self.vcRep
        fs.writeFile("one.txt", "data")
        rep.add("one.txt")
        rep.commit(["one.txt"], "testing")
        rep.delete("one.txt")
        fileStatus = rep.getStatus("one.txt")
        self.assertEquals(fileStatus.status, "deleted")
        # test deleting of properties as well


    #   copy(srcPath, destPath)     # Note: does not change IDs
    #   move(srcPath, destPath) ??? # copy & delete
    def testCopy(self):
        fs = self.fs
        rep = self.vcRep
        ############
        ############
        ############
        ############
        # check the copying of properties as well


    #   export(srcPath, destPath, includeProp=False)
    def testExport(self):
        fs = self.fs
        rep = self.vcRep
        file1 = "subDir/one.txt"
        file2 = "subDir/ssDir/two.txt"
        fs.writeFile(file1, "data")
        fs.writeFile(file2, "data")
        rep.getID("subDir")     # add to version control
        self.assertTrue(rep.isVersioned(file2))
        xfs = fs.clone("../export1")
        rep.export("subDir", xfs.absPath())
        self.assertTrue(xfs.isDirectory("."))
        self.assertEquals(xfs.listDirsFiles(), (["ssDir"], ["one.txt"]))
        self.assertEquals(xfs.listDirsFiles("ssDir"), ([], ["two.txt"]))

        xfs = fs.clone("../export2")
        rep.export("subDir", xfs.absPath(), includeProps=True)
        self.assertTrue(xfs.isDirectory("."))
        self.assertEquals(xfs.listDirsFiles(), ([".ice", "ssDir"], ["one.txt"]))
        self.assertEquals(xfs.listDirsFiles("ssDir"), ([".ice"], ["two.txt"]))
        self.assertEquals(xfs.listDirsFiles("ssDir/.ice/two.txt"), ([], ["meta"]))


    #   log(path, limit)
    def testLog(self):
        fs = self.fs
        rep = self.vcRep
        fs.writeFile("one.txt", "data")
        rep.add("one.txt")
        rep.commit(["one.txt"], "test one")
        fs.writeFile("one.txt", "data2")
        rep.commit(["one.txt"], "test two")
        fs.writeFile("one.txt", "data3")
        rep.commit(["one.txt"], "test three")
        messages = rep.log("one.txt", 2)
        self.assertEquals(len(messages), 2)
        self.assertEquals(messages[0][2], "test three")
        self.assertEquals(messages[1][2], "test two")
        messages = rep.log("one.txt", 3)
        self.assertEquals(len(messages), 3)
        messages = rep.log("one.txt", 6)
        self.assertEquals(len(messages), 3)
        self.assertEquals(messages[2][2], "test one")


    def testPropAccessAutoAdds(self):
        fs = self.fs
        rep = self.vcRep
        file = "dir/one.txt"
        fs.writeFile(file, "data")
        rep.getID(file)
        self.assertTrue(rep.isVersioned(file))


    #   propGet(path, name, default=None)
    #   propSet(path, name, value, ownFile=False)
    #   propList(path)
    def testPropGetSetDeleteList(self):
        fs = self.fs
        rep = self.vcRep
        file = "dir/one.txt"
        fs.writeFile(file, "data")
        names = rep.propList(file)
        self.assertEquals(names, ["_guid"])
        self.assertEquals(rep.propGet(file, "test", "?"), "?")
        rep.propSet(file, "test", "data")
        self.assertEquals(rep.propGet(file, "test", "?"), "data")
        names = rep.propList(file)
        self.assertEquals(names, ["test", "_guid"])
        file = "dir/"
        names = rep.propList(file)
        self.assertEquals(names, ["_guid"])
        self.assertEquals(rep.propGet(file, "test", "?"), "?")
        rep.propSet(file, "test", "data")
        self.assertEquals(rep.propGet(file, "test", "?"), "data")
        names = rep.propList(file)
        self.assertEquals(names, ["test", "_guid"])


    def testPropFileGetSetDelete(self):
        fs = self.fs
        rep = self.vcRep
        file = "dir/one.txt"
        data = "testData"
        # rendition.X, image-X properties and annotations ('inline-annotations')
        #   .ice/name/inline-annotations/md5s
        def test(renditionName, data, delTest=True):
            fs.write(file, data)
            propPath = rep._getPropDir(fs.absPath(file))
            rep.propSet(file, renditionName, data)
            renditionFile = fs.join(propPath, renditionName)
            self.assertTrue(fs.isFile(renditionFile))
            self.assertTrue(rep.isVersioned(renditionFile))
            self.assertEquals(rep.propGet(file, renditionName), data)
            if delTest:
                rep.propDelete(file, renditionName)
                self.assertFalse(rep.isVersioned(renditionFile))
        test("rendition.pdf", data)
        test("image-one.gif", data)
        test("inline-annotations/x", data)
        test("inline-annotations/x", data, False)
        test("inline-annotations/y", "two", False)
        d = rep.propGet(file, "inline-annotations")
        self.assertEquals(len(d), 2)
        self.assertEquals(d["x"], data)
        self.assertEquals(d["y"], "two")


    #   localPropGet(path, name, default=None)
    #   localPropSet(path, name, value)
    def testLocalPropGetSet(self):
        fs = self.fs
        rep = self.vcRep
        file = "dir/one.txt"
        fs.writeFile(file, "data")
        self.assertEquals(rep.localPropGet(file, "lastModified", "?"), "?")
        rep.localPropSet(file, "lastModified", "data")
        self.assertEquals(rep.localPropGet(file, "lastModified", "?"), "data")


    #   getStatus(path, includeServer=False)
    def testGetStatus(self):
        fs = self.fs
        rep = self.vcRep
        file = "one.txt"
        fs.writeFile(file, "data")
        fileStatus = rep.getStatus(file)
        self.assertEquals(fileStatus.status, "unversioned")
        self.assertFalse(fileStatus.isVersioned)
        rep.add(file)
        fileStatus = rep.getStatus(file)
        self.assertEquals(fileStatus.status, "added")
        self.assertTrue(fileStatus.isVersioned)
        rep.commit([file], "msg")
        fileStatus = rep.getStatus(file)
        self.assertEquals(fileStatus.status, "normal")
        self.assertTrue(fileStatus.isFile)
        self.assertEquals(fileStatus.revNum, 2)
        self.assertEquals(fileStatus.commitRevNum, 2)
        rep.delete(file)
        fileStatus = rep.getStatus(file)
        self.assertEquals(fileStatus.status, "deleted")


    #   getID(path)
    def testGetID(self):
        fs = self.fs
        rep = self.vcRep
        id = rep.getID("one.txt")
        self.assertEquals(id, None)
        fs.writeFile("one.txt", "data")
        id = rep.getID("one.txt")
        self.assertTrue(id!=None, "id='%s'" % id)
        #
        fs.write("dir/one.txt", "data")
        id = rep.getID("dir/one.txt")
        pPath = rep._getPropDir(fs.absPath("dir"))
        self.assertTrue(rep._isVersioned(pPath))


    #   applyNewID(path)
    def testApplyNewID(self):
        fs = self.fs
        rep = self.vcRep
        fs.writeFile("one.txt", "data")
        id = rep.getID("one.txt")
        rep.applyNewID("one.txt")
        id2 = rep.getID("one.txt")
        self.assertTrue(id!=id2)


    #   list(path, includeServer=False)
    def testList(self):
        fs = self.fs
        rep = self.vcRep
        file = "subDir/one.txt"
        fs.makeDirectory("subDir")
        fileStatusList = rep.list("subDir")
        self.assertEquals(len(fileStatusList), 1)
        self.assertEquals(fileStatusList["."].name, ".")
        # unversioned
        fs.write(file, "data")
        fileStatusList = rep.list("subDir")
        self.assertTrue(fileStatusList.has_key("one.txt"), "not showing unversioned (yet) item")
        self.assertEquals(fileStatusList["one.txt"].status, "unversioned")
        # added
        rep.add(file)
        fileStatusList = rep.list("subDir")
        self.assertTrue(fileStatusList.has_key("one.txt"))
        self.assertEquals(fileStatusList["one.txt"].status, "added")
        # normal
        rep.commit([file], "")
        fileStatusList = rep.list("subDir")
        self.assertTrue(fileStatusList.has_key("one.txt"))
        self.assertEquals(fileStatusList["one.txt"].status, "normal")
        # modifed
        # Note: a delay of 2 seconds may be required here
        #time.sleep(2)
        fs.write(file, "modified")
        fileStatusList = rep.list("subDir")
        self.assertTrue(fileStatusList.has_key("one.txt"))
        self.assertEquals(fileStatusList["one.txt"].status, "modified")
        # missing
        fs.delete(file)
        fileStatusList = rep.list("subDir")
        self.assertTrue(fileStatusList.has_key("one.txt"))
        self.assertEquals(fileStatusList["one.txt"].status, "missing")
        # shelved
        rep.shelve("subDir")
        fileStatusList = rep.list(".")
        #print fileStatusList
        self.assertEquals(fileStatusList["subDir"].status, "shelved")


    def testUpdateConflicts(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file = dir + "/test.one"
        fs.write(file, "one")
        rep.add(file)
        rep.commit(dir)
        rep2.update("", 1)
        fs.write(file, "one1")
        fs2.write(file, "one2")
        rep2.commit(dir)
        rep.update("", 1)
        fileStatuses = rep.list(dir)
        self.assertEquals(fileStatuses["MyChanges_test.one"].status, "unversioned")
        self.assertEquals(fileStatuses["test.one"].status, "normal")
        self.assertEquals(fs.read(dir + "/MyChanges_test.one"), "one1")
        self.assertEquals(fs.read(file), "one2")


    def testUpdatePropConflicts(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file = dir + "/test.one"
        fs.write(file, "one")
        rep.propSet(file, "p1", "one")
        rep.commit(dir)
        rep2.update("", 1)
        self.assertEquals(rep2.propGet(file, "p1"), "one")
        rep.propSet(file, "p2", "test1")
        rep2.propSet(file, "p2", "test2")
        rep2.commit(file)
        rep.update(file)
        self.assertEquals(rep.propGet(file, "p2"), "test2")
        fileStatuses = rep.list(file)
        self.assertEquals(fileStatuses.values()[0].status, "normal")
        fileStatuses = rep.list(dir + "/.ice/test.one")
        self.assertEquals(fileStatuses["meta"].status, "normal")
        self.assertEquals(fileStatuses["."].status, "normal")
        self.assertEquals(len(fileStatuses), 2)


    def testAddConflicts(self):
        # Add & Update an item that has been previously already committed
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file1 = dir + "/test1.one"
        file2 = dir + "/test2.two"
        file3 = dir + "/three.tst"
        rep.fs.write(file1, "data")
        rep.add(file1)
        rep.commit(file1)
        rep2.update("", 1)
        rep2.fs.write(file2, "two2")
        rep2.propSet(file2, "p", "pd")
        rep2.fs.write(file3, "three")
        rep2.getID(file3)
        rep2.commit("")
        # ok now try the same on rep
        rep.fs.write(file2, "mydata1")
        rep.propSet(file2, "p", "myprop")
        self.assertEquals(rep.list(dir)["test2.two"].status, "added")
        if True:
            rep.update(dir, 0)          # NOTE: this is preventing the .ice properties from being updated!!!!
            statusList = rep.list(dir)
            self.assertEquals(statusList["three.tst"].status, "missing")
            self.assertEquals(statusList["test2.two"].status, "added")       # Still displays as 'added'!

        # Note: This is not updating out-of-date sub-folders, because it self is upto date
        #print "xtest file2=%s" % file2
        rep.update(".", 1)      # does not update known 'missing' items also does not update/replace
                                #   added items (if they have already been added to the repository)
        # OK now get a infinity status list
        statusList = rep.list(dir)
        for s in statusList.values():
            #print s
            pass
        myChanges = statusList.pop("MyChanges_" + file2.split("/")[-1])
        self.assertEquals(myChanges.status, "unversioned")
        self.assertEquals(rep.fs.read(dir + "/MyChanges_" + file2.split("/")[-1]), "mydata1")
        self.assertEquals(rep.fs.read(file2), "two2")
        self.assertEquals(rep.propGet(file2, "p"), "pd", "property should also be updated")
        self.assertEquals(statusList["three.tst"].status, "normal")
        for s in statusList.values():
            self.assertEquals(s.status, "normal")
    


    def testCommitConflicts(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file1 = dir + "/test.one"
        file2 = dir + "/test.two"
        rep.fs.write(file1, "1")
        rep.propSet(file1, "p", "value1--")
        rep.commit(".")

        rep2.update(".", 1)
        rep2.fs.write(file1, "one2")
        rep2.propSet(file1, "p", "value2-1")
        rep2.fs.write(file2, "two2")
        rep2.propSet(file2, "p", "value2-2")
        rep2.commit(".")

        rep.propSet(file1, "p", "value1-1")
        rep.fs.write(file2, "two1")
        rep.propSet(file2, "p", "value1-2")
        try:
            rep.commit(".")
            self.fail("Expected an 'out of date' exception!")
        except Exception, e:
            msg = str(e)
            if msg.find("out-of-date")==-1:
                self.fail("Expected an 'out of date' exception!")
        rep.update(".", 1)
        #
        statusList = rep.list(dir)
        #
        commitRev, emptyList, infinityList = rep.commit(".")         # Note: should now not do any thing
        #print "emptyList=%s, infinityList=%s" %(emptyList, infinityList)

        statusList = rep.list(dir)
        for s in statusList.values():
            if s.status!="normal" and not s.name.startswith("MyChanges_"):
                self.fail("expected status to be 'normal'")
        self.assertEquals(rep.fs.read(file1), "one2")
        self.assertEquals(rep.propGet(file1, "p"), "value2-1")
        self.assertEquals(rep.fs.read(file2), "two2")
        self.assertEquals(rep.propGet(file2, "p"), "value2-2")


    def testOtherConflicts(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file = dir + "/test.one"


    def testPropStatus(self):
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file = dir + "/test.one"
        rep.fs.write(file, "data")
        rep.propSet(file, "p", "p1")
        rep.commit(".")

        rep.propSet(file, "p", "p2")
        statusList = rep.list(dir)
        for s in statusList.values():
            #print s
            pass
        self.assertEquals(statusList["test.one"].status, "modified")

        rep.commit(".")
        rep.propSet(file, "image-one.gif", "test-data")
        statusList = rep.list(dir)
        self.assertEquals(statusList["test.one"].status, "modified")

        rep.commit(".")
        rep.propDelete(file, "image-one.gif")
        statusList = rep.list(dir)
        self.assertEquals(statusList["test.one"].status, "modified")

        rep.commit(".")
        statusList = rep.list(dir)
        self.assertEquals(statusList["test.one"].status, "normal")

    
    def testOutOfDate(self):  # out-of-date with the server (or needs updating)
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "subDir"
        file1 = dir + "/test.one"
        file2 = dir + "/test.two"
        rep.fs.write(file1, "1")
        rep.propSet(file1, "p", "value1--")
        rep.commit(".")

        rep2.update(".", 1)
        rep2.fs.write(file1, "one2")
        rep2.propSet(file1, "p", "value2-1")
        rep2.fs.write(file2, "two2")
        rep2.propSet(file2, "p", "value2-2")
        rep2.commit(".")

        statusList = rep.list(dir, includeServer=True)
        self.assertEquals(statusList.pop("test.two").status, "none")
        for s in statusList.values():
            #print s
            self.assertEquals(s.status, "normal")


    def testDepthUpdate(self):
        # out-of-date with the server at a sub-depth only (that needs updating)
        fs = self.fs
        fs2 = self.fs2
        rep = self.vcRep
        rep2 = self.getTest2()
        dir = "dir"
        subDir = dir + "/subDir"
        file1 = subDir + "/test.one"
        file2 = subDir + "/test.two"
        rep.fs.write(file1, "1")
        rep.propSet(file1, "p", "value1--")
        rep.commit(".")

        rep2.update(".", 1)
        rep2.fs.write(file1, "one2")
        rep2.propSet(file1, "p", "value2-1")
        rep2.fs.write(file2, "two2")
        rep2.propSet(file2, "p", "value2-2")
        rep2.commit(".")

        # Now update dir (depth=0) only
        rep.update(dir, 0)
        # Now do a depth update
        rep.update(dir, 1)

        statusList = rep.list(subDir, includeServer=True)
        for status in statusList.values():
            self.assertEquals(status.status, "normal")
        self.assertEquals(rep.propGet(file1, "p"), "value2-1")
        self.assertEquals(rep.fs.read(file1), "one2")
        self.assertEquals(rep.fs.read(file2), "two2")
        self.assertEquals(rep.propGet(file2, "p"), "value2-2")
        



# What if's
# What if some (file) deletes the .ice folder or a .ice/Xxxx directory?
#       check for this (and/or catch this) and state that you must login to fix this!
#           or if already logged in update the .ice or .ice/Xxxx folder.
#
# What if



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())


## FileSystem
# Properties:
#    currentWorkingDirectory
#    isTempDirectory
#    fakeFiles
#
# Methods:
#    absolutePath(path=".")
#    normPath(path)
#    join(*args)
#    split(path)
#    splitExt(path)
#    splitPathFileExt(path)
#    exists(path)
#    isFile(path)
#    isDirectory(path)
#    makeDirectory(path)
#    delete(path=None)
#    copy(fromPath, toPath)
#    move(fromPath, toPath)
#    walk(path, filterFunc=None)
#    walker(path, func)
#    createTempDirectory()
#    writeFile(path, data)
#    readFile(path)
#    md5OfFile(path)            - returns the md5 of a file as a HexString
#    zip(toZipFile, path="./")
#    unzipToTempDirectory(zipFile)
#    unzipToDirectory(zipFile, path)
#    readFromZipFile(zipFile, filename)
#    zipList(zipFile)
#    addToZipFile(zipFile, filename, data)
#    list(path=".")
#    glob(matchPattern, path=".")
#    listFiles(path=".")
#    listDirectories(path=".")
#    listDirsFiles(path=".")    - return a tuple of dirs and files
#    getModifiedTime(path)
#    touch(path, mtime=None)
#    chmod(path, number)
#    zipString()



