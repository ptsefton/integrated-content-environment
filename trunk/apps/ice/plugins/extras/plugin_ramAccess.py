
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
import time

pluginName = "ice.ramAccess"
pluginDesc = "RAM Access"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = RamAccess
    pluginInitialized = True
    return pluginFunc

sampleXmlRamRequestResult = """<accesses repo="SVN" user="http://testuser@myopenid.com">
<access path="/" read="read" write="write"/>
<access path="/noAccessTest"/>
<access path="/projects" read="read" write="write"/>
<access path="/projects/readonly" read="read"/>
<access path="/readonlyTest" read="read"/>
</accesses>"""

class RamAccess(object):
    @staticmethod
    def test(iceContext, requestContext):
        responseData = requestContext.responseData
        ramAccess = RamAccess(iceContext, 
                "http://139.86.4.47/ice-ram/api/getuseraccess.php", "SVN")
        accessControl = ramAccess.getAccessControlFor("http://ronward@myopenid.com")
        s = str(accessControl) + "\n"
        testPaths = ["/testing", "/projects/readonly", "/noAccessTest", ["/projects/readonly", "/"]]
        for path in testPaths:
            s += "%s - read=%s, write=%s\n" % (path, 
                    accessControl.hasReadAccess(path), accessControl.hasWriteAccess(path))
        print s
        responseData.setResponse(s, "text/plain")
        #print accessList.checkAccess(["/projects/readonly", "/"])
    
    
    def __init__(self, iceContext, ramAccessUri, repId):
        # ramAccessUri = e.g. http://server/ice-ram/api/getuseraccess.php"
        self.iceContext = iceContext
        self.__ramAccessUri = ramAccessUri
        self.__repId = self.iceContext.urlQuote(repId)
        self.__et = iceContext.ElementTree
        self.__http = iceContext.Http()
    
    
    def getAccessControlFor(self, user):
        accessList = None
        queryString = "repo=%s&user=%s" % (self.__repId, 
                    self.iceContext.urlQuote(user))
        def updateAccessControl(addAccess):
            retries = 3
            try:
                while True:
                    result = self.__http.get(self.__ramAccessUri, queryString)
                    if result: break
                    if retries<1:
                        raise Exception("Failed to get a response from RamAccessUri -%s" % self.__ramAccessUri)
                    retries -= 1
                #print result
                try:
                    x = self.__et.XML(result)
                except Exception, e:
                    if result.find("Authorization Required"):
                        raise Exception("Authorization Required!")
                    raise e
                # assert
                if x.get("user")!=user or x.get("repo")!=self.__repId:
                    raise Exception("Received incorrect user or repId")
                for a in x.findall("access"):
                    path = a.get("path")
                    read = a.get("read")=="read"
                    write = a.get("write")=="write"
                    addAccess(path, read, write)
            except Exception, e:
                print str(e)
                raise e
        accessControl = _AccessControl(user, self.__repId, updateAccessControl)
        try:
            accessControl.updateAccessList()
        except Exception, e:
            print "-- ram access error - '%s'" % str(e)
            pass
        return accessControl
    
    
class _AccessControl(object):
    def __init__(self, userId, repId, updateAccessControl=None):
        self.__userId = userId
        self.__repId = repId
        self.__accessPaths = {}
        self.__sortedPaths = None
        self.__updateAccessControl = updateAccessControl
        self.__lastUpdateTime = 0
    
    @property
    def userId(self):
        return self.__userId
    
    @property
    def repId(self):
        return self.__repId
    
    @property
    def _paths(self):
        if self.__sortedPaths is None:
            self.__sortedPaths = self.__accessPaths.keys()
            self.__sortedPaths.sort(self.__sortByLength)
        return self.__sortedPaths
    
    @property
    def lastUpdateTime(self):
        return self.__lastUpdateTime
    
    
    def updateAccessList(self):
        self.__accessPaths = {}
        self.__addAccess("/", False, False)
        if callable(self.__updateAccessControl):
            self.__updateAccessControl(self.__addAccess)
            self.__lastUpdateTime = time.time()
    
    
    def checkAccess(self, paths):
        default = (False, False)
        def checkPath(path):
            if not path.endswith("/"):
                path += "/"
            for p in self._paths:
                if path.startswith(p):
                    return self.__accessPaths.get(p, default)
            return default
        if not type(paths) is types.ListType:
            return checkPath(paths)
        else:
            result = [True, True]
            for path in paths:
                r = checkPath(path)
                result[0] = result[0] and r[0]
                result[1] = result[1] and r[1]
                if result==default:
                    break
            return result
    
    
    def hasReadAccess(self, paths):
        a = self.checkAccess(paths)
        return a[0]
    
    
    def hasWriteAccess(self, paths):
        a = self.checkAccess(paths)
        return a[1]
    
    
    def __addAccess(self, path, read, write):
        self.__sortedPaths = None
        access = ""
        if not path.endswith("/"):
            path += "/"
        self.__accessPaths[path] = (read, write)
    
    def __sortByLength(self, a, b):
        return cmp(len(b), len(a))
    
    def __str__(self):
        s = "AccessControl userId='%s', repId='%s'\n" % (self.userId, self.repId)
        for path in self._paths:
            s += "  '%s' - '%s'\n" % (path, self.__accessPaths.get(path))
        return s



