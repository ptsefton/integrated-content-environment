
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

pluginName = "ice.auth.local"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Auth
    pluginInitialized = True
    return pluginFunc


class Auth(object):
    def __init__(self, iceContext, getAccessControlFor=None):
        self.iceContext = iceContext
    
    
    def isAuthenticated(self, session):
        return session.loggedIn
    
    
    def isWorkingOffline(self, session):
        return session.workingOffline
    
    
    def hasReadAccess(self, session, paths):
        return True
    
    
    def hasWriteAccess(self, session, paths):
        return True
    
    
    def checkForLogin(self, iceContext):
        """ returns True if login is required """
        session = iceContext.session
        requestData = iceContext.requestData
        
        r = (requestData.has_key("login") or requestData.has_key("login2") or \
            (self.isAuthenticated(session)==False and self.isWorkingOffline(session)==False))
        if (session.username=="" or session.username is None):
            session.username = iceContext.system.username
        #print "session.username='%s'" % session.username
        return r
    
    
    def login(self, iceContext, username=None, password=None, **kwargs):
        """ return a tuple (True, username) on success or
                (False, reason) on failure or
                None for redirect (openId) """
        # SVN login for now
        r = iceContext.rep.login(username=username, password=password)
        if r==True:
            iceContext.logger.iceInfo("LOGIN")
            iceContext.session.loggedIn = True
            return (True, username)
        else:
            return (False, "Invalid username/password")
    
    
    def logout(self, iceContext):
        iceContext.logger.iceInfo("LOGOUT")
        iceContext.session.logout()
        iceContext.rep.logout()




def dummyGetAccessControlFor(username):
    return DummyAccessControl(username)

class DummyAccessControl(object):
    def __init__(self, userId):
        self.__userId = userId
    
    @property
    def userId(self):
        return self.__userId
    
    def updateAccessList(self):
        pass
    
    def hasReadAccess(self, paths):
        return True
    
    def hasWriteAccess(self, paths):
        return True


class SvnAccessControl(object):
    def __init__(self, iceContext, userId):
        self.iceContext = iceContext
        self.__userId = userId
    
    def getAccessControlFor(self, userId):
        return SvnAccessControl(self.iceContext, userId)
    
    @property
    def userId(self):
        return self.__userId
    
    def updateAccessList(self):
        pass
    
    def hasReadAccess(self, paths):
        rep = self.iceContext.rep
        return rep.checkAuthorization(paths)
    
    def hasWriteAccess(self, paths):
        return self.hasReadAccess(paths)


