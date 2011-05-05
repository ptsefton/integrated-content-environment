
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

import types

pluginName = "ice.auth.server"
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
        self.isServer = iceContext.isServer
        self.__openId = None
        #
        settings = iceContext.settings
        enableOpenId = settings.get("enableOpenId", False)
        ramAccessUrl = settings.get("ramAccessUrl")
        ramAccessRepId = settings.get("ramAccessRepId")
        authentication = settings.get("authentication", "").upper()
        #print "--Auth--"
        #print "  openId='%s'" % enableOpenId
        #print "  ramAccessUrl='%s'" % ramAccessUrl
        #print "  ramAccessRepId='%s'" % ramAccessRepId
        if enableOpenId:
            OpenId = iceContext.getPluginClass("ice.openid")
            if OpenId is not None:
                self.__openId = OpenId(iceContext)
        if authentication=="LDAP":
            AuthLDAP = iceContext.getPluginClass("ice.auth.ldap")
            authLDAP = AuthLDAP(iceContext)
            def checkAuthentication(userId, password):
                return authLDAP.checkAuthentication(userId, password)
            self._checkAuthentication = checkAuthentication
        else:
            if settings.get("noVersionControl", False):
                def checkAuthentication(userId, password):
                    raise Exception("No authentication method setup!")
            else:
                # SVN login for now
                def checkAuthentication(userId, password):
                    r = False
                    if password=="":
                        r = False
                    else:
                        #####
                        r = iceContext.rep.login(username=username, password=password)
                        #####
                    return r
            self._checkAuthentication = checkAuthentication

        #
        if ramAccessUrl is not None and ramAccessRepId is not None:
            RamAccess = iceContext.getPluginClass("ice.ramAccess")
            if RamAccess is not None:
                #print "  ramAccessUrl='%s', ramAccessRepId='%s'" % (ramAccessUrl, ramAccessRepId)
                ramAccess = RamAccess(iceContext, ramAccessUrl, ramAccessRepId)
                getAccessControlFor = ramAccess.getAccessControlFor
        #
        if getAccessControlFor is None:
            if settings.get("noVersionControl", False):
                getAccessControlFor = dummyGetAccessControlFor
            else:
                getAccessControlFor = SvnAccessControl(iceContext, "").getAccessControlFor
        self.__getAccessControlFor = getAccessControlFor


    
    def isAuthenticated(self, session):
        #if session.workingOffline:
        #    return True
        return session.loggedIn
    
    
    def hasReadAccess(self, session, path):
        #print "hasReadAccess(path='%s')" % path
        accessControl = self.__getAccessControl(session)
        return accessControl.hasReadAccess(path)
    
    
    def hasWriteAccess(self, session, path):
        accessControl = self.__getAccessControl(session)
        return accessControl.hasWriteAccess(path)
    
    
    def checkForLogin(self, iceContext):
        """ returns True if login is required """
        requestData = iceContext.requestData
        session = iceContext.session
        if self.isServer:
            session.workingOffline = False
            if session.loggedIn:                            ## per repository session data
                return False
            if requestData.has_key("login"):
                return True
            username = session.username
            password = session.password
            if password is None or password=="":
                r = False
            else:
                rep = iceContext.rep
                r = rep.login(username=username, password=password)
            session.loggedIn = r
            return (requestData.has_key("login") or session.loggedIn==False)
        else:
            r = (requestData.has_key("login") or requestData.has_key("login2") or \
                (self.isAuthenticated(session)==False and self.isWorkingOffline(session)==False))
            if (session.username=="" or session.username is None):
                session.username = iceContext.system.username
            #print "session.username='%s'" % session.username
            return r
    
    
    def login(self, iceContext, username="", password="", openIdUri=""):
        """ return a tuple (True, username) on success or
                (False, reason) on failure or
                None for redirect (openId) """
        if password is None:
            password = ""
        if openIdUri is None:
            openIdUri = ""
        if password=="" and openIdUri=="":
            return (False, "")
        if openIdUri!="":
            if self.__openId is None:
                raise Exception("attempting an OpenID login without ice.openid plugin installed")
            # Authenticate using OpenID
            requestData = iceContext.requestData
            login = requestData.value("login", "")
            if login=="oidResult":
                r, d = self.__openId.complete(requestData)
                message = d.get("message", "?")
                if r==True and (message=="OK"):
                    username = d.get("id")
                    print "OPENID username='%s'" % username
                    return (True, username)
                else:
                    reason = message
                    if reason.lower().find("lost session store, try again")!=-1:
                        pass
                    else:
                        print "OpenID failed reason - '%s'" % reason
                        return (False, reason)
            urlPath = requestData.urlPath
            returnUrl = urlPath + "?login=oidResult&openIdUri=%s" % openIdUri
            urlParts = self.iceContext.urlparse(requestData.urlPath)
            realm = "%s://%s/" % urlParts[:2]
            redirectUrl = self.__openId.getRedirectUrlFor(requestData.session, \
                        openIdUri, returnUrl, realm)
            if redirectUrl is not None:
                iceContext.responseData.setRedirectLocation(redirectUrl)
                return None
        # Else
#        if True:
#            # SVN login for now
#            if password=="":
#                r = False
#            else:
#                #####
#                r = iceContext.rep.login(username=username, password=password)
#                #####
        try:
            r = self._checkAuthentication(username, password)
        except Exception, e:
            return (False, str(e))
        if r==True:
            return (True, username)
        else:
            return (False, "Invalid username/password")
    
    
    def logout(self, iceContext):
        iceContext.logger.iceInfo("LOGOUT")
        iceContext.session.logout()
        iceContext.rep.logout()


    def __getAccessControl(self, session):
        accessControl = session.get("accessControl")
        if accessControl is None:
            accessControl = self.__getAccessControlFor(session.username)
            session["accessControl"] = accessControl
        return accessControl



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
    
    def hasReadAccess(self, path):
        return True
    
    def hasWriteAccess(self, path):
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
    
    def hasReadAccess(self, path):
        rep = self.iceContext.rep
        r = rep.checkAuthorization(path)
        if r==False:
            #print "hasReadAccess(path='%s')==False" % path
            r = True
        return r
    
    def hasWriteAccess(self, path):
        return self.hasReadAccess(path)




