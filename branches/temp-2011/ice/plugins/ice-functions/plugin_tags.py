
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

pluginName = "ice.function.tags"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = myTags
    pluginClass = None
    pluginInitialized = True
    return pluginFunc




def update(self, obj):
    obj.taggedWith, obj.myTaggedWith, obj.myTags = getTags(self)
extras = {"update":update}


def getTags(self):
    userData = self.rep.getUserData(self.username)
    myTags = userData.get("myTags", [])
    id = self.item.guid
    myTaggedWith = userData.get("id-%s" % id, [])
    myTaggedWith = self.iceContext.Tags.normCase(myTaggedWith, myTags)
    taggedWith = self.item.tags
    taggedWith = self.iceContext.Tags.normCase(taggedWith, myTags)          # norm case to user's tags
    return taggedWith, myTaggedWith, myTags


##################
def myTags(self):
    #
    taggedWith, myTaggedWith, myTags = getTags(self)
    newTags = self.formData.value("myTags").replace(",", " ")
    newTags = newTags.split()
    tagWork = TagWork(self.iceContext, self.item, self.username, 
                            taggedWith, myTaggedWith, myTags, newTags)
    tagWork.update()
myTags.options = {"toolBarGroup":"tag", "position":63, "postRequired":True,
                "label":"myTags", "title":"myTags", 
                "extras":extras}
##################


# userData.get("myTags") - list of myTags
# userData.get("id-$id") - list of myTags applied to this item (document or folder) (should be lowercase)
# 
# prop.tags - list  & prop.setTags(tags)
# prop.taggedBy  & prop.setTaggedBy()
class TagWork(object):
    def __init__(self, iceContext, prop, username, taggedWith, myTaggedWith, myTags, 
                    newTags, output=None):
        self.iceContext = iceContext
        self.prop = prop
        self.rep = self.iceContext.rep
        self.username = username
        self.id = "id-%s" % prop.guid
        self.userData = self.rep.getUserData(self.username)
        self.taggedWith = taggedWith
        self.myTaggedWith = myTaggedWith
        self.myTags = myTags
        self.newTags = newTags
        self.addedTags = []
        self.deletedTags = []
        self.deletedSharedTags = []
        self.taggedIds = []
        
        self.addedTags, self.deletedTags = iceContext.Tags.getAddedDeleted(self.myTaggedWith, \
                                    iceContext.Tags.normCase(self.newTags, self.myTaggedWith))
        # get deleted sharedTags
        self.deletedSharedTags = [t.lower() for t in self.deletedTags if t.startswith("_")]
        #self.userData["myTags"] = iceContext.Tags.merge(self.myTaggedWith, self.newTags)      # Currently add only
        self.taggedIds = self.userData.get("taggedIds", [])
        self.myTags = iceContext.Tags.normCase(self.myTags, self.newTags)       
        self.userData["myTags"] = self.myTags
        if output is not None:
            output.write("newTags='%s'\n" % str(self.newTags))
            output.write("addedTags='%s'\n" % str(self.addedTags))
            output.write("deletedTags='%s'\n" % str(self.deletedTags))
            output.write("deletedSharedTags='%s'\n" % str(self.deletedSharedTags))
        
    
    def update(self):
        if self.myTaggedWith!=self.newTags:
            self._update()
            # Save the changes
            self.rep.updateUserData(self.username, self.userData)
            self.prop.flush()
            # also reMetaIndex this (if it has changed!)
            self.rep.indexer.reIndex(self.prop, metaOnly=True)
            # finished
    
    def _update(self):
        if self.newTags==[]:                                          # All tags have been removed
            self._removeUserHavingTaggedThisItem()
        else:                                                   #
            self._weHaveTaggedThisItem()
        if self.deletedTags!=[]:                                     # Deleted tags
            self._removeDeletedTags()
        if self.addedTags!=[]:                                       # Added tags
            self._addAddedTags()
    
    def _removeUserHavingTaggedThisItem(self):
        userData = self.userData
        # remove this
        id = self.id
        if userData.has_key(id):
            userData.pop(id)
        if id in self.taggedIds:
            self.taggedIds.remove(id)
        # remove this id from the property's list of taggedBy
        taggedBy = self.prop.taggedBy
        if self.username in taggedBy:
            taggedBy.remove(self.username)
            self.prop.setTaggedBy(taggedBy)
    
    def _weHaveTaggedThisItem(self):
        id = self.id
        # We have tagged this item
        self.userData[id] = self.newTags
        if str(id) not in self.taggedIds:
            self.taggedIds.append(id)
        # add this id to the property's list of taggedBy (if not already)
        taggedBy = self.prop.taggedBy
        if self.username not in taggedBy:
            taggedBy.append(self.username)
            self.prop.setTaggedBy(taggedBy)
    
    def _addAddedTags(self):
        self.myTaggedWith = self.iceContext.Tags.normCase(self.myTaggedWith, self.myTags)
        # Update myTaggedWith
        self.myTaggedWith = self.iceContext.Tags.merge(tags=self.myTaggedWith, updateList=self.addedTags)
        self.userData[self.id] = self.myTaggedWith
        # Update myTags
        self.myTags = self.iceContext.Tags.merge(tags=self.myTags, updateList=self.myTaggedWith)
        self.userData["myTags"] = self.myTags
        # Check and see if we need to add this tag to the property's tags list
        tags = self.prop.tags
        tags = self.iceContext.Tags.merge(tags, self.iceContext.Tags.normCase(self.myTaggedWith, tags)) #normCase from second argument
        self.prop.setTags(tags)
    
    def _removeDeletedTags(self):
        id = self.id
        usedTags = {}
        for i in self.taggedIds:
            tags = self.userData.get(i, [])
            tags = [t.lower() for t in tags]
            usedTags.update(zip(tags, tags))
        removeTags = [t for t in self.deletedTags if t not in usedTags]
        #print "tags to be removed = '%s'" % str(removeTags)
        self.userData["myTags"] = self.iceContext.Tags.remove(self.userData["myTags"], removeTags)
        
        # Also check if any tags need to be removed from property's tags list
        # Get a list of all used tags
        usedTags = {}
        for user in self.prop.taggedBy:
            if user==self.username:
                uData = self.userData
            else:
                uData = self.rep.getUserData(user)
            tags = uData.get(id, [])
            # # Deleted Shared Tags
            ltags = [tag.lower() for tag in tags]
            if False:   ## Shared tags
                delSharedTags = [t for t in self.deletedSharedTags if t in ltags]
                if delSharedTags!=[]:
                    for t in delSharedTags:
                        i = ltags.index(t)
                        ltags.pop(i)
                        tags.pop(i)
                    if tags==[]:
                        uData.pop(id)
                    else:
                        uData[id] = tags
                    self.rep.updateUserData(user, uData)
            # #
            usedTags.update(zip(ltags, tags))
        usedTags = self.iceContext.Tags.normCase(usedTags.values(), self.prop.tags)
        self.prop.setTags(usedTags)
        #print "usedTags='%s'" % str(usedTags)
 












