
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

pluginName = "ice.extra.serverData"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = ServerData.load
    pluginClass = ServerData
    pluginInitialized = True
    return pluginFunc


class ServerData(object):
    RelDataFile = "/.ice/__serverData2__.tmp"
    RelLocalDataFile = "/.ice/__serverData__.tmp"
    
    @staticmethod
    def load(iceContext):
        data = iceContext.rep.getItem(ServerData.RelDataFile).read()
        if data is None:    # Create
            serverData = ServerData(iceContext)
            serverData.commit()
        else:
            serverData = iceContext.loads(data)
            serverData.iceContext = iceContext
        data = iceContext.rep.getItem(ServerData.RelLocalDataFile).read()
        if data is None:
            serverData.__localMeta = {}
        else:
            localMeta = iceContext.loads(data)
            serverData.__localMeta = localMeta
        return serverData
    
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__relPathsIds = {}     # keyed by relPaths
        self.__idsRelPaths = {}     # keyed by ids
        self.__meta = {}
        self.__localMeta = {}       # non-revision data (saved only locally)
        self.__idCounter = 128
        self.__change = False
        self.__localChange = False
    
    
    def commit(self):
        """ save and commit """
        change = self.__change
        self.__save()
        if change:  # commit changes
            try:
                # try and commit the changes
                pass
            except Exception, e:
                pass
    
    
    #def update(self):
    #    pass
    
    
    def __save(self):
        iceContext = self.iceContext
        self.iceContext = None      # do not serialize
        localMeta = self.__localMeta
        self.__localMeta = None     # do not serialize
        # Save
        localChange = self.__localChange
        self.__localChange = False
        if self.__change:
            self.__change = False
            data = iceContext.dumps(self)
            iceContext.rep.getItem(self.RelDataFile).write(data)
        if localChange:
            data = iceContext.dumps(localMeta)
            #print "saving localDataFile"
            item = iceContext.rep.getItem(self.RelLocalDataFile)
            item.write(data)
        # restore
        self.iceContext = iceContext
        self.__localMeta = localMeta
    
    
    def getIdForRelPath(self, relPath):        
        relPath = relPath.strip("/")
        id = self.__relPathsIds.get(relPath, None)
        if id is None:
            id = self.__idCounter
            self.__idCounter += 1
            self.__relPathsIds[relPath] = id
            self.__idsRelPaths[id] = relPath
            self.__change = True
            self.__localChange = True
            self.commit()       # save and commit
        return id
    
    
    def renameRelPath(self, oldRelPath, newRelPath):
        oldRelPath = oldRelPath.strip("/")
        if self.__relPathsIds.has_key(oldRelPath):
            id = self.__relPathsIds[oldRelPath]
            del self.__relPathsIds[oldRelPath]
            self.__idsRelPaths[id] = newRelPath
            #self.__change = True
            self.__localChange = True
            self.commit()
    
    
    def getRelPathForId(self, id):
        return self.__idsRelPaths.get(id, None)
    








