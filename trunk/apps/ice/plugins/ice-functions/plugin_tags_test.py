#!/usr/bin/env python
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(".") 
    os.chdir("../../")
    from ice_common import IceCommon
# XmlTestCase        # self.assertSameXml


from plugin_tags import *


class MockProperty(object):
    def __init__(self):
        self.guid = 1234
        self.relPath = "relPath/"
        self.taggedBy = ["tst", "test"]
        self.tags = ["one", "two", "three", "four"]
    
    def setTaggedBy(self, taggedBy):
        self.taggedBy = taggedBy
    
    def setTags(self, tags):
        self.tags = tags
    
    def flush(self):
        pass

class MockRep(object):
    def __init__(self):
        self.userDatas = {
                        "tst":{"myTags":["three"], "id-1234":["three"]},
                        "test":{"myTags":["one", "TWO", "five"], "id-1234":["one", "two"],
                            "id-1235":["two", "five"], "taggedIds":["id-1234", "id-1235"]},
                        }
    
    def getUserData(self, username):
        return self.userDatas.get(username, [])
    
    def updateUserData(self, username, userData):
        self.userDatas[username] = userData
    
    def reIndex(self, relPath, metaOnly=True):
        pass
    


class TagWorkTests(IceCommon.TestCase):
    def setUp(self):
        self.prop = MockProperty()
        self.rep = MockRep()
        self.username = "test"
        self.taggedWith = self.prop.tags
        self.userData = self.rep.getUserData("test")
        self.myTaggedWith = self.userData.get("id-%s" % self.prop.guid, [])
        self.myTags = self.userData.get("myTags", [])
    
    def tearDown(self):
        pass
    
    def testInit(self):
        newTags = []
        output = sys.stdout
        output = None
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        self.assertEqual(tagWork.addedTags, [])
        self.assertEqual(tagWork.deletedTags, ["two", "one"])
        
        newTags = ["one", "six"]
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        self.assertEqual(tagWork.addedTags, ["six"])
        self.assertEqual(tagWork.deletedTags, ["two"])
        #tagWork.update()
    
    def testClearAll(self):
        newTags = []
        output = sys.stdout
        output = None
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        if True:
            tagWork.update()
        else:
            tagWork._removeUserHavingTaggedThisItem()
            tagWork._removeDeletedTags()
        #print "prop.tags='%s'" % self.prop.tags
        #print "prop.taggedBy='%s'" % self.prop.taggedBy
        #print "userData='%s'" % str(self.userData)
        self.assertEqual(self.prop.tags, ['three'])
        self.assertEqual(self.prop.taggedBy, ['tst'])
        self.assertEqual(self.userData, 
                {'taggedIds': ['id-1235'], 'id-1235': ['two', 'five'], 'myTags': ['TWO', 'five']})
    
    def testTagging(self):
        # first remove cleanup
        self.testClearAll()
        self.taggedWith = self.prop.tags
        self.userData = self.rep.getUserData("test")
        self.myTaggedWith = self.userData.get("id-%s" % self.prop.guid, [])
        self.myTags = self.userData.get("myTags", [])
        
        newTags = ["newOne", "newTwo", "three", "two"]
        output = sys.stdout
        output = None
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        if True:
            tagWork.update()
        else:
            tagWork._weHaveTaggedThisItem()
            tagWork._addAddedTags()
        #print "prop.tags='%s'" % self.prop.tags
        #print "prop.taggedBy='%s'" % self.prop.taggedBy
        #print "userData='%s'" % str(self.userData)
        self.assertEqual(self.prop.tags, ['newOne', 'newTwo', 'three', 'two'])
        self.assertEqual(self.prop.taggedBy, ['tst', 'test'])
        self.assertEqual(self.userData, 
                {'taggedIds': ['id-1235', 'id-1234'], 
                    'id-1235': ['two', 'five'], 
                    'id-1234': ['newOne', 'newTwo', 'three', 'two'], 
                    'myTags': ['five', 'newOne', 'newTwo', 'three', 'two']})
    
    
    def testAddingTags(self):
        newTags = ["one", "Two", "Six"]
        output = sys.stdout
        output = None
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        tagWork.update()
        #print "prop.tags='%s'" % self.prop.tags
        #print "prop.taggedBy='%s'" % self.prop.taggedBy
        #print "userData='%s'" % str(self.userData)
        self.assertEqual(self.prop.tags, ['Six', 'four', 'one', 'three', 'two'])
        self.assertEqual(self.prop.taggedBy, ['tst', 'test'])
        self.assertEqual(self.userData, 
                {'taggedIds': ['id-1234', 'id-1235'],
                    'id-1235': ['two', 'five'], 
                    'id-1234': ['Six', 'Two', 'one'], 
                    'myTags': ['Six', 'Two', 'five', 'one']})
    
    def testRemovingTags(self):
        newTags = ["Two"]
        output = sys.stdout
        output = None
        tagWork = TagWork(self.prop, self.rep, self.username, 
                        self.taggedWith, self.myTaggedWith, self.myTags, 
                        newTags, output)
        tagWork.update()
        #print "prop.tags='%s'" % self.prop.tags
        #print "prop.taggedBy='%s'" % self.prop.taggedBy
        #print "userData='%s'" % str(self.userData)
        self.assertEqual(self.prop.tags, ['three', 'two'])
        self.assertEqual(self.prop.taggedBy, ['tst', 'test'])
        self.assertEqual(self.userData, 
            {'taggedIds': ['id-1234', 'id-1235'], 
                'id-1235': ['two', 'five'], 
                'id-1234': ['Two'], 
                'myTags': ['Two', 'five']})

if __name__ == "__main__":
    IceCommon.runUnitTests(locals())




