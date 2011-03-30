#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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
    from vc_rep import VCRep
except:
    VCRep = None
from ice_item3 import IceItem as IceItemNoVersionControl
from ice_item import IceItem

try:
    from svn_rep import SvnRep  #, ListItem, ItemStatus
except Exception, e:
    print "*** %s" % str(e)
    SvnRep = None
from svn_proxy_rep import SvnProxyRep


class IceRepository(object):
    """
    """
    IceItem = None
    IceItemNoVersionControl = None
    SvnRep = None
    SvnProxyRep = None
    
    # Constructor:
    #   __init__(basePath=".", repUrl=None, name="Default", svnRep=None, iceRender=)
    # Properties:
    #   name        The repository name
    #   site
    #   isSetup
    #   exportPath
    #   
    #   
    # Methods:
    #   _setup()
    #   
    #   getAbsPath(relPath)
    #   
    #   getItem(relPath)
    #   getItemForUri(uriPath)
    #   
    #   
    # =========================
    #   fileSystem usage:
    #       .absolutePath(path)
    #       .split, .splitExt, join
    #       .exists(path), isDirectory(), isFile()
    #       .makeDirecory(path)
    #       .getModifiedTime(path)
    #       .walk(path)
    #       .listDirectory(path)
    #       .readFile(path), writeFile(path, data)
    RepNamePath = "/.ice/rep.name.txt"    
    
    def __init__(self, iceContext, basePath=".", repUrl=None, name="Default", iceRender=None):
        self.iceContext = iceContext
        self.iceContext.rep = self
        self.iceContext.urlRoot = "/rep.%s/" % name
        self.__output = self.iceContext.output
        self.__basePath = self.iceContext.fs.absolutePath(basePath)
        self.__basePath = self.iceContext.normalizePath(self.__basePath)
        self.__fs = self.iceContext.fs.clone()
        self.__fs.currentWorkingDirectory = self.__basePath
        self.__repUrl = repUrl
        self.__iceLogger = iceContext.logger
        self.__rlock = self.iceContext.RLock()
        self.__name = name
        self.__configName = name

        self.__svnRep = None
        if True:
            try:
                svnRep = self.SvnRep(self.iceContext, basePath=self.__basePath, \
                                svnUrl=self.__repUrl)
                self.__svnRep = self.SvnProxyRep(self.iceContext, svnRep, self.__rlock)
            except Exception, e:
                msg = str(e)
                if self.iceContext.settings.get("noVersionControl", False) and \
                    msg.find("No svnURL")!=-1:
                        pass
                else:
                    raise e
        self.__vcRep = None
        try:
            self.__vcRep = VCRep(self.__fs,
                                ignoreFilterMethod = self.ignoreTestMethod)
        except Exception, e:
            print "Error setting up VCRep '%s'" % str(e)
            print self.iceContext.formattedTraceback()
            pass
        if self.iceContext.settings.get("noVersionControl", False):
            self.IceItem = IceRepository.IceItemNoVersionControl
        
        self.__mineCopyNamePrefix = "myChanges_"
        self.__indexPath = ".indexes"
        
        self.__hiddenDirectories = [".svn", ".ice", ".site", ".src", self.__indexPath, \
                                ".cache", "src", ".skin", "skin", ".userData", ".temp"]
        self.doNotExport = []       # or include in the ims manifest's resources
        self.doNotIncludeInToc = [] # in the manifest's content
        ##
        # doNotRenderDirectories & doNotIndexDirectories
        #  should also include doNotExport directories
        self.doNotRenderDirectories = self.__hiddenDirectories
        self.doNotIndexDirectories = self.doNotRenderDirectories 
        
        # svn ignore, and all processing ignore
        self.ignoreStartsWith = ["~$", ".nfs"]        # and self.__mineCopyNamePrefix  ??? (always ignored in walker() method )
        self.ignore = [".DS_Store", "Thumbs.db", self.__indexPath, ".cache", ".temp"]
        self.ignoreEndsWith = ["~", ".tmp", ".mime", ".prej"]
        
        self.mimeTypes = self.iceContext.MimeTypes
        
        self.__isSetup = False
        
        # The ICE site class data
        self.__siteFilename = None
        self.__siteFileDateTime = None
        self.__siteData = None
        self.__execSiteDataMethod = None
        self.__site = None
        
        ##
        self.renditions = {".htm":".xhtml.body", ".html":".xhtml.body"}
        
        if iceRender is None:
            raise self.iceContext.IceException("iceRender parameter not set in calling IceRepository constructor!")
        self.__render = iceRender
        
        self.__exportPath = ""
        self.__relativeExportPath = None
        self.__documentTemplatesPath = "/templates"
        self._testing = False
        
        self.tags = {}
        self.__loginCallbackMethod = None
        self.__authRequired = None
        self.__isAuthCache = None
        self.__indexer = None
        self.serverData = None
        
        plugin = self.iceContext.getPlugin("ice.extra.html2text")
        if plugin:
            self.HtmlToText = plugin.pluginClass()
        plugin = self.iceContext.getPlugin("ice.extra.serverData")
        if plugin:
            self.serverData = plugin.pluginClass.load(self.iceContext)
        
        #print "\nice_rep.__init__(name='%s')" % self.__name
        self.__setup(create=False, messageWriter=self.iceContext.output.write)
        # ##
        self.svnUsername = None
        self.svnPassword = None
    
    
    def _setup(self, messageWriter=None):
        messages = []
        def messageWriter2(msg):
            messages.append(msg)
        if messageWriter is None:
            messageWriter = messageWriter2 
        self.__setup(True, messageWriter)
        return messages
    
    def __setup(self, create=True, messageWriter=None):
        if messageWriter is None:
            messageWriter = self.iceContext.output.write

        if self.__svnRep is not None or \
                self.iceContext.settings.get("noVersionControl", False)==False:
            try:
                if self.__svnRep is None:
                    messageWriter("ice_rep.__setup() svnRep is not set!\n")
                    return False
                if create:
                    self.__svnRep.autoCreateCheckoutCheck(messageWriter)    ##############
                else:
                    pass
            except Exception, e:
                msg = str(e)
                messageWriter("ice_rep.setup - exception - '%s'" % msg)
                if msg.find("not authenticated")>0:
                    self.iceContext.writeln("  %s" % msg)
                    self.__authRequired = True
                    return False
                eMsg = "ice_rep.setup exception (repName='%s') - '%s'" % (self.__name, msg)
                raise self.iceContext.IceException(eMsg)
            try:
                self.__svnRep.revInfo(self.__basePath)
            except Exception, e:
                self.__name = "?"
                return False
        # else self.__svnRep is None and 'noVersionControl' is True
        
        # create indexes
        self.__indexer = self.iceContext.getRepositoryIndexer(self.__indexPath)
        
        # read repository name from /.ice/rep.name.txt if possible
        name = self.getItem("").getRepName()
        ##name = self.getItem(self.RepNamePath).read()
        if name is not None:
            self.__name = name.strip()
        else:
            if self.__name.startswith("?"):
                self.__name = self.__configName
            messageWriter("Writing repository name")
            item = self.getItem("/")
            item.guid
            item.close()
            ##self.getItem(self.RepNamePath).write(self.__name)
            self.getItem("").setRepName(self.__name)
        #
        fs = self.iceContext.fs     # Note: NOT self.__fs
        d = {}
        favIcon = "favicon.ico"
        if fs.isFile(favIcon):
            d[favIcon] = fs.readFile(favIcon)
        siteFile = "site2.1.py"
        if fs.isFile(siteFile):
            d[".site/%s" % siteFile] = fs.readFile(siteFile)
        
        if fs.isDirectory("fake.skin"):
            skin = "skin/"
            def walkerFunc(path, dirs, files):
                if ".svn" in dirs:
                    dirs.remove(".svn")
                dir = path[path.find("/")+1:]
                for file in files:
                    d[skin + dir + file] = fs.readFile(path + file)
            fs.walker("fake.skin", walkerFunc)
        self.__fs.updateFakeFiles(d)
        self.__isSetup = True
        return self.__isSetup
    
    
    @property
    def _svnRep(self):
        return self.__svnRep

    @property
    def _vcRep(self):
        return self.__vcRep
    
    @property
    def fs(self):
        return self.__fs
    
    @property
    def name(self):
        return self.__name
    
    @property
    def configName(self):
        return self.__configName
    
    @property
    def repUrl(self):
        return self.__repUrl
    
    @property
    def render(self):
        return self.__render
    
    
    @property
    def indexer(self):
        return self.__indexer
    
    
    @property
    def isSetup(self):
        return self.__isSetup
    
    
##    @property
##    def auth(self):
##        #############
##        return self.__auth
    
    
    ################################################
    @property
    def isAuthRequired(self):
        if self.__authRequired is None:
            self.__authRequired = False
        return self.__authRequired
    
    
    @property
    def isAuthenticated(self):
        """ Note: This will do a check only.  It will not cause a callback. """
        if self.__isAuthCache is not None:
            return self.__isAuthCache
        value = self.__svnRep.isAuthenticated()
        return value
    
    
    def setName(self, name):
        self.__name = name
    
    
    def checkAuthorization(self, relPath):
        relPath = relPath.lstrip("/")
        return self.__svnRep.checkAuthorization(relPath)
    
    
    def serverLogin(self):
        return self.login(self.svnUsername, self.svnPassword)
    
    
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
    ################################################
    
    
    #-----------------------------------------------
    # public methods 
    #-----------------------------------------------
    
    
    def getAbsPath(self, relPath="/"):
        if relPath==".":
            relPath = "/"
        if relPath.startswith("./"):
            relPath = relPath[2:]
        relPath = self.iceContext.normalizePath(relPath)
        relPath = relPath.lstrip("/")
        path = self.iceContext.url_join(self.__basePath, relPath)
        path = self.iceContext.normalizePath(path)
        return path
    
    
    def getUserData(self, username):
        data = {}
        try:
            pData = self.getItem("/.userData/%s" % username).read()
            if pData is None:
                data = {}
            else:
                data = self.iceContext.loads(pData)
        except Exception, e:
            print "Error reading userData for '%s' - error - '%s'" % (username, str(e))
            data = {}
        data["myTags"] = data.get("myTags", [])
        data["taggedIds"] = data.get("taggedIds", [])
        for tag in data["myTags"]:
            name = "tag-%s" % tag
            data[name] = data.get(name, [])
        for id in data["taggedIds"]:
            name = "id-%s" % id
            data[name] = data.get(name, [])
        return data
    
    
    def deleteUserData(self, username):
        ##if self.__userIndexer is not None:
        ##    self.__userIndexer.deleteIndex(username)
        self.getItem("/.userData/%s" % username).write(self.iceContext.dumps({}))
    
    
    def updateUserData(self, username, data):
        self.getItem("/.userData/%s" % username).write(self.iceContext.dumps(data))
        ##content = None
        ##if self.__userIndexer is not None:
        ##    self.__userIndexer.indexContent(content, id=username, metaItems=data)
        ##    self.__userIndexer.optimize()
    
    
    #    rep.getItem(relPath)
    #    rep.getItemForPath(relPath)  - must match extension as well (casing???)
    #    rep.getItemForUri(uri)       - will get the item that is associated with this URI
    def getItem(self, relPath):
        item = self.IceItem.GetIceItem(self.iceContext, relPath)
        return item
    
    
    def getItemForUri(self, uriPath):
        item = self.IceItem.GetIceItemForUri(self.iceContext, uriPath)
        return item

    
    #this method is added to retrieve the svn property from 1.2    
    def getSvnProp (self, name, absPath):
        if self.__svnRep._hasProperty(absPath, name):
            return self.__svnRep._getProperty(absPath, name)
        else:
            return None
    
    def deleteAllProp(self, absPath):
        return self.__svnRep._deleteAllProperties(absPath)    
    
    
    def copyx(self, file, toAbsFile):
        item = self.getItem(file)
        item.export(toAbsFile, includeProperties=False)
    
    
    def getSkinTemplates(self, paths=["/"]):   # e.g. paths=["/", "/packagePath/"]
        files = {}
        for path in paths:
            if path=="":
                continue
            try:
                path = self.iceContext.urlJoin(path, "skin/templates")
                item = self.getItem(path)
                l = [i.relPath for i in item.listItems() if i.isFile]
                files.update(dict(zip(l,l)))    # override with newer versions
            except Exception, e:
                pass
        files = [self.__fs.splitPathFileExt(f)[1] for f in files
                    if f.endswith(".xhtml") and self.__fs.splitPathFileExt(f)[1] != "slide"]
        return files
    
    # ----------------------------------------
    #             Private methods
    # ----------------------------------------
    
    def inIgnoreLists(self, filename):
        return self.__inIgnoreLists(filename)
    def __inIgnoreLists(self, filename):
        filename = self.__fs.split(filename)[1]
        if filename in self.ignore:
            return True
        for i in self.ignoreStartsWith:
            if filename.startswith(i):
                return True
        for i in self.ignoreEndsWith:
            if filename.endswith(i):
                return True
        return False


    #############################
    def ignoreTestMethod(self, relPath):
        relPath = relPath.lstrip("/")
        # ignore directories  (and/or filenames)
        ignoreNames = ["Thumbs.db"]     # or any name starting with '.' e.g.
                                        #   ".DS_Store", ".indexes", ".cache", ".temp"
        # ignore filenames
        ignoreStartingWith = ["~$", ".nfs", ".~"]
        ignoreEndingWith = ["~", ".tmp", ".mime", ".prej", ".pyc"]

        parts = relPath.split("/")
        name = parts[-1]
        for s in ignoreStartingWith:
            if name.startswith(s):
                return True
        for s in ignoreEndingWith:
            if name.endswith(s):
                return True
        if parts[0]==".site":   # do not ignore this (because it startswith .
            parts[0]="site"
        for p in parts:
            if p in ignoreNames:
                return True
            if p.startswith("."):
                return True
        return False


IceRepository.SvnRep = SvnRep
IceRepository.SvnProxyRep = SvnProxyRep
IceRepository.IceItem = IceItem
IceRepository.IceItemNoVersionControl = IceItemNoVersionControl












