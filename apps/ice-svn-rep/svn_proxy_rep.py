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



    

class SvnProxyRep:
    """
    === Public Property ===
    svnUrl
    === Public Methods ===
    __init__(iceContext, basePath=None, svnUrl=None)
    setGetUsernamePasswordCallback(callback)
    login(username=None, password=None, callback=None, retries=None)
    isAuthenticated()
    isSvnUrlValid(svnUrl=None)
    logout()
    autoCreateCheckoutCheck(messageWriter=None)
    
    makeDirectory(path, message="mkdir", svnIgnore=False)
    add(paths, recurse=True, actionResults=None)
    commit(paths, message="commit", recurse=True, actionResults=None, lastErrorFile=None)
    update(path, recurse=True, actionResults=None, revisionNumber=None)
    statusList(path)   -> return a list of ListItem objects
    revInfo(path, includeServer=False)
    delete(path)
    revert(path, recurse=True)
    copy(path, destinationPath)
    move(path, destinationPath)
    
    cleanup(path=None)                      ->  
    export(path, destinationPath)           ->  
    getRevision(path, includeUrl=False)     ->  
    getLogData(path, levels=None)           ->  
    """
    
    #   (self, iceContext, basePath=None, svnUrl=None):
    def __init__(self, iceContext, svnRep, rLock):
        self.iceContext = iceContext
        self.__svnRep = svnRep
        self.__rLock = rLock
        self.ItemStatus2 = svnRep.ItemStatus2
    
    @property
    def mineCopyNamePrefix(self):
        return self.__svnRep.mineCopyNamePrefix
    
    @property
    def ignoreStartsWith(self):
        return self.__svnRep.ignoreStartsWith
    
    @property
    def ignoreEndsWith(self):
        return self.__svnRep.ignoreEndsWith
    
    @property
    def ignoreFolders(self):
        return self.__svnRep.ignoreFolders
    
    def ignoreFilename(self, name):
        return self.__svnRep.ignoreFilename(name)
    
    def ignoreFoldername(self, name):
        return self.__svnRep.ignoreFoldername(name)
    
    def ignorePath(self, path):
        return self.__svnRep.ignorePath(path)
    
    def doNotAddPathTest(self, path):
        return self.__svnRep.doNotAddPathTest(path)
    
    def doNotAddNameTest(self, name, isFile=True):
        return self.__svnRep.doNotAddNameTest(name, isFile)
    
    def ignoreTest(self, name, isFile=True):
        return self.__svnRep.ignoreTest(name, isFile)
    
    @property
    def svnUrl(self):
        return self.__svnRep.svnUrl
    
    
    #-------------------------------------------------------------------    
    #makeDirectory(path, message="mkdir", svnIgnore=False)
    def makeDirectory(self, *args, **kwargs):
        self.__rLock.acquire()
        try:
            return self.__svnRep.makeDirectory(*args, **kwargs)
        finally:
            self.__rLock.release()            
    
    
    # ---  Add ---
    def add(self, *args, **kwargs):
        self.__rLock.acquire()
        try:
            return self.__svnRep.add(*args, **kwargs)
        finally:
            self.__rLock.release()            
    
    
    # ---  Commit  ---
    def commit(self, paths, message="commit", recurse=True, actionResults=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.commit(paths, message, recurse, actionResults)
        finally:
            self.__rLock.release()            
    
    ##
    def commitEmpty(self, paths, logMessage="added"):
        self.__rLock.acquire()
        try:
            return self.__svnRep.commitEmpty(paths, logMessage)
        finally:
            self.__rLock.release()
    
    def commitAll(self, paths, logMessage="commit", callback=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.commitAll(paths, logMessage, callback)
        finally:
            self.__rLock.release()
    
    
    def updateAll(self, path, revision=None, updateResolver=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.updateAll(path, revision, updateResolver)
        finally:
            self.__rLock.release()
    
    def updateFiles(self, path, revision=None, updateResolver=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.updateFiles(path, revision, updateResolver)
        finally:
            self.__rLock.release()
    
    def updateEmpty(self, path, revision=None, updateResolver=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.updateEmpty(path, revision, updateResolver)
        finally:
            self.__rLock.release()
    
    ##
    
    def update2(self, path, recurse, revision):
        self.__rLock.acquire()
        try:
            return self.__svnRep.update2(path, recurse, revision)
        finally:
            self.__rLock.release()            
    
    
    # ---  Update  ---
    def update(self, paths, recurse=False, actionResults=None, 
            revisionNumber=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.update(paths, recurse, actionResults)
        finally:
            self.__rLock.release()            
    
    
    # ---  Delete  ---
    def delete(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.delete(path)
        finally:
            self.__rLock.release()            
    
    
    # ---  Copy  ---
    def copy(self, path, destinationPath):
        self.__rLock.acquire()
        try:
            return self.__svnRep.copy(path, destinationPath)
        finally:
            self.__rLock.release()            
    
    
    # ---  Move/Rename  ---
    def move(self, path, destinationPath):
        self.__rLock.acquire()
        try:
            return self.__svnRep.move(path, destinationPath)
        finally:
            self.__rLock.release()            
    
    
    # ---  Export  ---
    def export(self, path, destinationPath):
        self.__rLock.acquire()
        try:
            return self.__svnRep.export(path, destinationPath)
        finally:
            self.__rLock.release()            
    
    
    # ---  GetLogData  ---
    def getLogData(self, path, levels=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getLogData(path, levels)
        finally:
            self.__rLock.release()            
    
    
    # ---  Revert  ---
    def revert(self, path, recurse=True):
        self.__rLock.acquire()
        try:
            return self.__svnRep.revert(path, recurse)
        finally:
            self.__rLock.release()            
    
    
    # --- Cleanup ---
    def cleanup(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.cleanup(path)
        finally:
            self.__rLock.release()            
    
    ##
    def list(self, path, update=False):
        self.__rLock.acquire()
        try:
            return self.__svnRep.list(path, update)
        finally:
            self.__rLock.release()
    
    def hasChanges(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.hasChanges(path)
        finally:
            self.__rLock.release()
    
    def getStatus(self, path, *args, **kwargs):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getStatus(path, *args, **kwargs)
        finally:
            self.__rLock.release()
    ##
    
    def statusList(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.statusList(path)
        finally:
            self.__rLock.release()            
    
    
    def ls(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.ls(path)
        finally:
            self.__rLock.release()            
    
    
    def getMissing(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getMissing(path)
        finally:
            self.__rLock.release()            
    
    
    def isDirModifiedAdded(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.isDirModifiedAdded(path)
        finally:
            self.__rLock.release()            
    
    
    def revInfo(self, path, includeServer=False):
        self.__rLock.acquire()
        try:
            return self.__svnRep.revInfo(path, includeServer)
        finally:
            self.__rLock.release()            
    
    
    def getUpdateList(self, path, recurse=True):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getUpdateList(path, recurse)
        finally:
            self.__rLock.release()            
    
    
    # ---  GetRevision  ---
    def getRevision(self, path, includeUrl=False):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getRevision(path, includeUrl)
        finally:
            self.__rLock.release()            
    
    
    # -----------------
    #------------------------------------------------------------------
    
    def autoCreateCheckoutCheck(self, messageWriter=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.autoCreateCheckoutCheck(messageWriter)
        finally:
            self.__rLock.release()            
    
    
    def getUrlForPath(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.getUrlForPath(path)
        finally:
            self.__rLock.release()            
    
    
    def isSvnUrlValid(self, svnUrl=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.isSvnUrlValid(svnUrl)
        finally:
            self.__rLock.release()            
    
    
    def setGetUsernamePasswordCallback(self, callback, retries=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.setGetUsernamePasswordCallback(callback, retries)
        finally:
            self.__rLock.release()            
    
    
    def isAuthenticated(self):
        self.__rLock.acquire()
        try:
            return self.__svnRep.isAuthenticated()
        finally:
            self.__rLock.release()            
    
    
    def login(self, username=None, password=None, callback=None, retries=None):
        self.__rLock.acquire()
        try:
            return self.__svnRep.login(username, password, callback, retries)
        finally:
            self.__rLock.release()            
    
    
    def logout(self):
        self.__rLock.acquire()
        try:
            return self.__svnRep.logout()
        finally:
            self.__rLock.release()            
    
    
    def checkAuthorization(self, path):
        self.__rLock.acquire()
        try:
            return self.__svnRep.checkAuthorization(path)
        finally:
            self.__rLock.release()            
    
#For svn properties in V1.2
#To be used in Package copy
    def _hasProperty(self, path, name):
        self.__rLock.acquire()
        try:
            return name in self.__svnRep._getPropertyList(path)
        finally:
            self.__rLock.release()
         
    
    def _getProperty(self, path, name): 
        self.__rLock.acquire()
        try:
            return self.__svnRep._getProperty(path, name)
        finally:
            self.__rLock.release() 
    
    def _deleteAllProperties(self, path):
        self.__rLock.acquire()
        try:
            self.__svnRep._deleteAllProperties(path)
        finally:
            self.__rLock.release()
    


