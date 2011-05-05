#
#
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

    

class IceProxyRepository:
    """
    """
    # Constructor:
    #   __init__(iceRespository, svnRep=None)
    # Properties:
    #   name        The repository name
    #   site
    #   isSetup
    #   isAuthRequired
    #   isAuthenticated
    #   exportPath
    #   
    # Methods:
    #   setup()
    #   setExecDataMethod(method)
    #   login(username=None, password=None, retries=None)
    #   loginCallback(callback, retries=None)
    #   logout()
    #   
    #   getAbsPath(relPath)
    #   
    #   
    #   getItem(relPath)
    #
    def __init__(self, rep):
        self.__rep = rep
        self.__svnRep = rep.getNewSvnRep()
        
        self.__loginCallbackMethod = None
        self.__authRequired = False     # True
        self.__isAuthCache = None
    
    @property
    def iceContext(self):
        return self.__rep.iceContext
    
    #@property
    def __getDocumentTemplatesPath(self):
        return self.__rep.documentTemplatesPath
    def __setDocumentTemplatesPath(self, value):
        self.__rep.documentTemplatesPath = value
    documentTemplatesPath = property(__getDocumentTemplatesPath, __setDocumentTemplatesPath)
    
    @property
    def mimeTypes(self):
        return self.__rep.mimeTypes
    
    @property
    def name(self):
        return self.__rep.name

    @property
    def _svnRep(self):
        return self.__svnRep
    
    @property
    def indexer(self):
        return self.__rep.indexer
    
    @property
    def metaIndexer(self):
        return self.__rep.metaIndexer
    
    @property
    def userIndexer(self):
        return self.__rep.userIndexer
    
    #@property
    def __getExportPath(self):
        return self.__rep.exportPath
    def __setExportPath(self, value):
        self.__rep.exportPath = value
    exportPath = property(__getExportPath, __setExportPath)
    
    @property
    def relativeExportPath(self):
        return self.__rep.relativeExportPath
    
    
    def _setup(self):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep._setup()
        finally:
            self.__rep.release()
    
    
    @property
    def site(self):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep.site
        finally:
            self.__rep.release()
    

    @property
    def isSetup(self):
        return self.__rep.isSetup
    
    
    @property
    def isAuthRequired(self):
        return self.__authRequired
    
    
    @property
    def isAuthenticated(self):
        """ Note: This will do a check only.  It will not cause a callback. """
        if self.__isAuthCache is not None:
            return self.__isAuthCache
        value = self.__svnRep.isAuthenticated()
        return value
    
    
    def checkAuthorization(self, relPath):
        relPath = relPath.lstrip("/")
        return self.__svnRep.check
    
    
    def login(self, username=None, password=None, retries=None):
        """ Try and login with the given username and password if given else will call callback to get username/password.
          Returns True if logged in OK else False """
        value = self.__svnRep.login(username=username, password=password, retries=retries)
        self.__isAuthCache = value
        return value

        
    def loginCallback(self, callback, retries=None):
        """ Try and login using the given callback method to obtain the username and password.
            Optionaly try upto 'retries' number of times.
            Returns True if logged in OK else False.
         callback signature: e.g.
            getUsernamePassword(realm, user):
                return username, password, OK    # OK=True or False if cancel login attempts.
        """
        self.__loginCallbackMethod = callback
        callback = self.__loginCallbackProxy
        return self.__svnRep.setGetUsernamePasswordCallback(callback=callback, retries=retries)
    
    
    def __loginCallbackProxy(self, realm, user):
        print "loginCallback called"
        username, password, ok = self.__loginCallbackMethod(realm, user)
        return username, password, ok
    
    
    def logout(self):
        self.__isAuthCache = None
        self.__svnRep.logout()
    
    
    #-----------------------------------------------
    # public methods 
    #-----------------------------------------------
    
    def getAbsPath(self, relPath):
        return self.__rep.getAbsPath(relPath)
    
    
    def deleteUserData(self, username):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep.deleteUserData(username)
        finally:
            self.__rep.release()
    
    
    def getUserData(self, username):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep.getUserData(username)
        finally:
            self.__rep.release()

    
    def updateUserData(self, username, data):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep.updateUserData(username, data)
        finally:
            self.__rep.release()
    
    
    def getItem(self, relPath):
        self.__rep.acquire(self.__svnRep)
        try:
            return self.__rep.getItem(relPath)
        finally:
            self.__rep.release()










