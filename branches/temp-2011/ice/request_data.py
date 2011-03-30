#!/usr/bin/env python
#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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

""" ServerRequestData """


import urllib
import types
import time



class ServerRequestData(object):
    #    method       - "GET" or "POST"
    #    path
    #    keys         - returns a list of all keys
    #    has_key(key) - 
    #    remove(key)  - 
    #    value(key)   - return the first value for this key  (None if key is not found)
    #    values(key)  - returns a list of values for the key (An empty list if the key is not found) 
    count = 1
    sessions = {}
    deletedSessions = []
    def __init__(self, path="/", method="GET", args={}, sessionId=None, \
                    filenames={}, port=None, urlPath="", location=None, cookies={},
                    queryString="", acceptGzip=False, headers={}):
        if sessionId is None:
            #print "Creating sessionId"
            sessionId = "%s-%s" % (int(time.time()*1000), ServerRequestData.count)
            ServerRequestData.count += 1
        #print "sessionId='%s' %s %s" % (sessionId, method, path)
        
        self.__cookies = cookies
        sessions = ServerRequestData.sessions      # or self.sessions
        # Check for expired sessions
        expireTime = 30*60     # Seconds
        expireTime = 60*60*24  # 24Hrs
        delKeys = []
        for k, s in sessions.iteritems():
            if (s.lastRequestTime + expireTime)<time.time():
                delKeys.append(k)
        for k in delKeys:
            session = sessions[k]
            self.deletedSessions.append(session)
            if len(self.deletedSessions)>10:
                self.deletedSessions.pop(0)
            print "Session timed out!"
            session.logout()
            del(sessions[k])
        session = sessions.get(sessionId, None)
        if session is None:
            for s in self.deletedSessions:
                if s.id==sessionId:
                    print "Restoring deleted session. repName='%s'" % s.repositoryName
                    session = s
                    break
            if session is None:
                #print "Creating new Session (sessionId='%s')" % sessionId
                session = IceSession(sessionId, \
                        self.getCookie("username", ""), self.getCookie("repName", None))
            sessions[sessionId] = session
            
        session.requested()     # increases requestCount and sets lastRequestTime
        self.__path = path
        self.__method = method
        self.__args = args
        self.__session = session
        self.__sessionId = sessionId
        
        self.__filenames = filenames
        self.__port = port
        self.__unquotedPath = urllib.unquote(path)
        self.__urlPath = urlPath
        self.__location = location
        self.__queryString = queryString
        self.__acceptGzip = acceptGzip
        self.__headers = headers
    
    @property
    def port(self):
        return self.__port
    
    @property
    def urlPath(self):
        return self.__urlPath
    
    @property
    def location(self):
        return self.__location
    
    @property
    def queryString(self):
        return self.__queryString
    
    @property
    def session(self):
        return self.__session

    @property
    def headers(self):
        return self.__headers

    @property
    def args(self):
        return self.__args
    
    def setPath(self, path):
        self.__path = path
        self.__unquotedPath = path
    
    @property
    def path(self):
        return self.__path
    
    @property
    def unquotedPath(self):
        return self.__unquotedPath
    
    @property
    def method(self):
        return self.__method
    
    @property
    def sessionId(self):
        return self.__sessionId
    
    @property
    def acceptGzip(self):
        return self.__acceptGzip
    
    
    def has_key(self, key):
        return self.__args.has_key(key)
    
    
    def remove(self, key):
        del self.__args[key]
    
    
    def keys(self):
        return self.__args.keys()
    
    
    def value(self, key, defaultValue=None):
        value = self.__args.get(key, defaultValue)
        if type(value) is types.ListType and len(value)>0:
            return value[0]
        return value
    
    
    def setValue(self, key, value):
        self.__args[key]=[value]
    
    
    def values(self, key):
        r = self.__args.get(key, [])
        if type(r) is types.StringType:
            r = [r]
        return r
    
    
    def has_uploadKey(self, key):
        return self.__filenames.has_key(key)
    
    
    def uploadFileKeys(self):
        return self.__filenames.keys()
    
    
    def uploadFilename(self, key):
        fieldStorage = self.__filenames.get(key, None)
        if fieldStorage is None:
            return None
        return fieldStorage.filename
    
    
    def uploadFileData(self, key):
        # OK for twisted.web and should be OK for paste (native for paste)
        fieldStorage = self.__filenames.get(key, None)
        if fieldStorage is None:
            return None
        data = fieldStorage.file.read()
        return data
    
    
    def getCookie(self, cookieName, default=None):
        return self.__cookies.get(cookieName, default)
    

    def getHeader(self, name):
        name = name.upper()
        return self.__headers.get(name)

    def __str__(self):
        items = []
        for key, value in self.__args.iteritems():
            if key.find("password")!=-1:    # Hide the password
                items.append("'%s': %s" % (key, "'****'"))
            else:
                l = len(str(value)) 
                if l>80:
                    items.append("'%s': ...len(%s)..." % (key, l))
                else:
                    items.append("'%s': %s" % (key, value))
        username = ""
        if hasattr(self.__session, "username"):
            username = self.__session.username
        s = "%s, %s, user=%s, args={%s}" % \
                (self.__method, self.__path, username, ", ".join(items))
        return s




class mockServerRequestData(dict):
    def __init__(self, path, method, args={}, session=None, sessionId=None, filenames={}):
        dict.__init__(self)
        self.__path = method
        self.__method = path
        self.__args = args
        self.__session = session
        self.__sessionId = sessionId
        self.__filenames = filenames
        self.__unquotedPath = urllib.unquote(path)
    
    
    def __getitem__(self, key):    # override
        v = self.__args.get(self, key, None)
        if v==None:
            if key=="method":
                return self.__method
            elif key=="path":
                return self.__path
            elif key=="sessionId":
                return self.__sessionId
        if type(v) is types.ListType and len(v)>0:
            return v[0]


    def __setitem__(self, key, value):    # override
        raise Exception("this object is immutable")
    
    
    def get(self, key, *args):    # override
        return self.__args.get(key, *args)
        
    def keys(self):
        return []
        
    def value(self, key):
        return None
        
    def values(self, key):
        return []
        
    def uploadedFileKeys(self):
        return []
        
    def uploadedFilename(self, key):
        return self.__filenames.get(key, None)
        
    def uploadedFileData(self, key):
        return None


##        class Session(object):
##            def __init__(self):
##                self.timeCreated = time.time()
##                self.time = self.timeCreated
##                self.requests = 0
##            def __str__(self):
##                return "Session: requests=%s, createdTime=%s" % \
##                        (self.requests, time.ctime(self.timeCreated))
##                        #time.strftime("%H:%M.%S", time.gmtime(self.timeCreated)))

class IceSession(dict):
    def __init__(self, sessionId, username="", repName=None):
        self.__sessionId = sessionId
        self.__repName = repName
        self.__username = {repName:username}
        self.__password = {repName:""}
        self.__usingOpenId = {repName:False}
        self.__loggedIn = {repName:False}
        self.__workingOffline = {repName:True}
        self.__timeCreated = time.time()
        self.__lastRequestTime = time.time()
        self.__requests = 0
        self.logWriter = None
        self.asyncJob = None
    
    @property
    def id(self):
        return self.__sessionId
    
    @property
    def lastRequestTime(self):
        return self.__lastRequestTime
    
    @property
    def lastRequestTimeStr(self):
        lTime = time.localtime(self.__lastRequestTime)
        lTime = time.strftime("%d %H:%M:%S", lTime)
        return lTime
    
    
    def __getRepName(self):
        return self.__repName
    def __setRepName(self, value):
        self.__repName = value
    repositoryName = property(__getRepName, __setRepName)
    
    # ------------ Logged in status and WorkingOffline -------
    # __loggedIn, __workingOffline, username & password should all be (dict) based on __repName
    #   LoggedIn=True       WorkingOffline = True or False
    #   LoggedIn=False      WorkingOffline = True
    def __setLoggedIn(self, value):
        self.__loggedIn[self.__repName] = value
    def __getLoggedIn(self):
        return self.__loggedIn.get(self.__repName, False)
    loggedIn = property(__getLoggedIn, __setLoggedIn)
    
    def __setUsername(self, value):
        self.__username[self.__repName] = value
    def __getUsername(self):
        return self.__username.get(self.__repName, "")
    username = property(__getUsername, __setUsername)
    
    
    def __setPassword(self, value):
        self.__password[self.__repName] = value
    def __getPassword(self):
        return self.__password.get(self.__repName, "")
    password = property(__getPassword, __setPassword)
    
    
    def __setUsingOpenId(self, value):
        self.__usingOpenId[self.__repName] = value
    def __getUsingOpenId(self):
        return self.__usingOpenId.get(self.__repName, False)
    usingOpenId = property(__getUsingOpenId, __setUsingOpenId)
    
    def __setworkingOffline(self, value):
        self.__workingOffline[self.__repName] = value
    def __getworkingOffline(self):
        if self.loggedIn:
            return False
        return self.__workingOffline.get(self.__repName, True)
    workingOffline = property(__getworkingOffline, __setworkingOffline)
    
    
    def logout(self):
        self.__loggedIn[self.__repName] = False
        self.__password[self.__repName] = ""
    #----------------------------------------------------------
    
    
    def requested(self):
        self.__requests += 1
        self.__lastRequestTime = time.time()
    
    
    def __getattr__(self, name):
        # can not find 'name'
        return None
    
    
    def __str__(self):
        #s = "[IceSession object] id='%s', lastRequestTime='%s'"
        #s = s % (self.id, time.ctime(self.lastRequestTime))
        s = "Session username='%s', id='%s', lastRequestTime='%s'"
        s = s % (self.username, self.id, self.lastRequestTimeStr)
        return s



#======================================================================
# mockIceSession mock object for testing only
#======================================================================
class mockIceSession:
    def __init__(self):
        self.uid = md5.new(str(time.time())).hexdigest()
        self.logout()
        
    def logout(self):
        self.username = ""
        self.password = ""
        self.workingOffline = True
    
    
    def __getattr__(self, name):
        # can not find 'name'
        return None





