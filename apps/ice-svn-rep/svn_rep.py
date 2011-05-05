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


import string
import types
import re
import pysvn
import time


# Raise expection warning about incorrect version of pysvn
msg = None
if pysvn.version[0]==1 and pysvn.version[1] < 6:
    msg = "*** ERROR: pysvn version 1.6 or greater required to run ICE2 ***"
if pysvn.svn_version[0]==1 and pysvn.svn_version[1] < 5:
    msg = "*** ERROR: pysvn version 1.6 or greater and pysvn svn version 1.5 or greater required to run ICE2 ***"
if msg is not None:
    raise Exception(msg)


def SvnErrorWrap(func):
    def wrapper(*args, **kargs):
        try:
            return func(*args, **kargs)
        except pysvn.ClientError, e:
        #except Exception, e:
            raise FixupSvnException(e)
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper
    
def FixupSvnException(e):
    msg = str(e)
    lmsg = msg.lower()
    if msg.find("PROPFIND ")>-1:
        m = re.search("PROPFIND of '(.*)': authorization failed", msg)
        if m is not None:
            v = m.groups()[0]
            eMsg = "Access denied (SVN) '%s'" % v
            return Exception(eMsg)
    if lmsg.find("locked")!=-1 and lmsg.find("not locked")==-1:
        eMsg = "(SVN) Lock error: Try doing a 'SVN cleanup' first. (under advanced options of the File view)"
        return Exception(eMsg)
    return e


class SvnRep:
    pysvnClient = staticmethod(pysvn.Client)      # Can be changed for unit testing
    #    .callback_ssl_server_trust_prompt
    #    .callback_get_login
    #    .callback_cancel
    #    .callback_notify
    #    .set_auth_cache(False)
    #    .set_interactive(False)
    #    .set_store_passwords(False)
    #   .status(path, recurse=True, get_all=False) .status(path)
    #   .status(path, recurse=True, get_all=True, update=False, ignore=False)
    #   .add(path, recurse=False, force=False)
    #   .propset("svn:mime-type", "application/octet-stream", path)
    #   .checkin(paths, log_message=message, recurse=recurse)
    #   .revert(item.path, recurse=False)
    #   .update(path, recurse=recurse, revision=revision)
    #   .mkdir(path, message)
    #   .remove(path, force=True)
    #   .copy(path, destinationPath, src_revision=rev)
    #   .export(path, destinationPath, force=True, revision=rev)
    #   .move(path, destinationPath, force=True)
    #   .log(path, revision_start=workingRev)
    #   .cleanup(path)
    #   .info2(path, recurse=False)
    #   .ls(url),   .ls(svnUrl, recurse=False)
    #   .cat(url)
    #   .info(defaultRep)
    #   .checkin(path=path, log_message="Created", recurse=True)
    #   .is_url(repUrl)
    #   .propget("svn:ignore", path).values()
    #   .propset("svn:ignore", value, path)

    
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
    
    
    def __init__(self, iceContext, basePath=None, svnUrl=None):
                #iceLogger=False, output=False, fs=None):
        self.iceContext = iceContext
        iceLogger = self.iceContext.logger
        self.__iceLogger = iceLogger
        output = self.iceContext.output
        self.__output = output
        if iceContext.rep is None:
            if basePath is None:
                #raise Exception("basePath is not set")
                fs = None
            else:
                fs = self.iceContext.fs.clone()
                fs.currentWorkingDirectory = basePath
        else:
            fs = self.iceContext.rep.fs
        self.__fs = fs
        
        # reset by logout()
        if basePath is not None:
            self.__pysvnClientPath = basePath
            if self.__pysvnClientPath.endswith("/"):
                self.__pysvnClientPath = self.__pysvnClientPath[:-1]
            self.__pysvnClientPath = self.__fs.join(self.__pysvnClientPath, ".ice")
        else:
            self.__pysvnClientPath = ""
        self.__client = self.__createClient()
        self.__loginRetries = 3
        
        self.__username = None
        self.__password = None        # note optional
        self.__getUsernamePasswordCallback = None    # must return a tuple(username, password) and take a single argument (user)
        
        if svnUrl=="":
            svnUrl = None
        if svnUrl==None and basePath!=None:
            svnUrl = self.getUrlForPath(basePath)
        
        if basePath!=None:      # and svnUrl!=None:
            urlFromPath = self.getUrlForPath(basePath)
            if urlFromPath!=None:
                if svnUrl is None:
                    svnUrl = urlFromPath
                else:
                    if urlFromPath!=svnUrl:
                        msg = "ERROR: The supplied repository path is not setup to use the supplied repository URL"
                        msg += "\n\tEither the supplied repository path or the supplied repository URL is incorrect!"
                        raise self.iceContext.IceException(msg)
        self.__basePath = basePath
        self.__svnUrl = svnUrl
        if svnUrl is None:
            msg = "No svnURL given or found!"
            msg += "\n\tThe given repository path is not valid or has not yet been checked out!"
            raise self.iceContext.IceException(msg)
        
        self.__mineCopyNamePrefix = "myChanges_"
        # svn ignore
        self.__ignoreStartsWith = ["~$", ".nfs", self.__mineCopyNamePrefix]        # and self.__mineCopyNamePrefix  ??? (always ignored in walker() method )
        self.__ignoreEndsWith = ["~", ".tmp", ".mime", ".prej"]
        self.__ignoreFolders = [".DS_Store", "Thumbs.db", ".cache", ".indexes", ".userData", ".temp"]
        
        pattern = ""
        for name in self.__ignoreFolders:
            pattern += "((^|/)%s(/|$))|" % name
        pattern = pattern.rstrip("|")
        self.__reIgnorePaths = re.compile(pattern)
        #self.setIgnoreTest(self.__inIgnoreLists)
        
        ####
        self.__rLock = self.iceContext.RLock()
        self.__authCache = [0, False]
        ####
        self.__cache = {}
    
    
    @property
    def mineCopyNamePrefix(self):
        return self.__mineCopyNamePrefix
    
    @property
    def ignoreStartsWith(self):
        return self.__ignoreStartsWith
    
    @property
    def ignoreEndsWith(self):
        return self.__ignoreEndsWith
    
    @property
    def ignoreFolders(self):
        return self.__ignoreFolders
    
    #def setIgnoreTest(self, ignoreTestFunction):
    #    if callable(ignoreTestFunction):
    #        self.__ignoreTestMethod = ignoreTestFunction
    
    def ignoreFilename(self, name):
        for i in self.__ignoreStartsWith:
            if name.startswith(i):
                return True
        for i in self.__ignoreEndsWith:
            if name.endswith(i):
                return True
    
    def ignoreFoldername(self, name):
        return name in self.__ignoreFolders
    
    def ignorePath(self, path):
        if self.__reIgnorePaths.search(path):
            return True
        filename = self.__fs.split(path)[1]
        return self.ignoreFilename(filename)
    
    def doNotAddPathTest(self, path):
        if self.__fs.exists(path):
            filename = None
            if self.__fs.isDirectory(path):
                path, filename = self.__fs.split(path)
            if self.ignorePath(path):
                return True
            if filename is not None:
                if filename.startswith(self.__mineCopyNamePrefix):
                    return True
                return self.ignoreFilename(filename)
            return False
        return True
    
    def doNotAddNameTest(self, name, isFile=True):
        if name.startswith(self.__mineCopyNamePrefix):
            return False
        return self.ignoreTest(name, isFile)
    
    def ignoreTest(self, name, isFile=True):
        if isFile:
            return self.ignoreFilename(name)
        else:
            return self.ignoreFoldername(name)
    
#    # Ignore list       # The default __ignoreTestMethod
#    def __inIgnoreLists(self, filename):
#        if self.__reIgnorePaths.search(filename):
#            return True
#        filename = self.__fs.split(filename)[1]
#        for i in self.__ignoreStartsWith:
#            if filename.startswith(i):
#                return True
#        for i in self.__ignoreEndsWith:
#            if filename.endswith(i):
#                return True
#        return False
    
    
    # *** loginCallback ***
    # def getLogin(realm, username, password, maySave):
    #   return OK, username, password, False
    #   #Note: this will be kept being called until OK is False or username/password is OK
    def __createClient(self):
        client = self.pysvnClient(self.__pysvnClientPath)
        client.callback_ssl_server_trust_prompt = self.__callback_ssl_server_trust_prompt
        client.callback_get_login               = self.__loginCallback
        client.callback_cancel                  = None  # self.__client.callback_cancel
        client.callback_notify                  = None  # self.__client.callback_notify
        client.set_auth_cache(False)
        client.set_interactive(False)
        client.set_store_passwords(False)
        self.__clearCache()
        return client
    
    
    @property
    def svnUrl(self):
        return self.__svnUrl
    
    
    #-------------------------------------------------------------------    
    # ---  Add ---
    @SvnErrorWrap
    def add_New_Not_Working_Fine(self, paths, recurse=False):
        self.__clearCache()
        report = []
        if type(paths) in types.StringTypes:
            paths = [paths]
        depth = pysvn.depth.empty
        if recurse:
            depth = pysvn.depth.infinity
        for path in paths:
            try:
                #print "adding path='%s'" % path
                self.__client.add(path, force=True, ignore=True, depth=depth)
            except Exception, e:
                report.append("Error in svn_rep.add(): '%s'" % str(e))
        if report==[]:
            return None
        return report
    
    @SvnErrorWrap
    def add(self, paths, recurse=True, results=[]):
        """ returns a ActionResults """
        # add
        #print "add(path='%s', recurse=%s)" % (paths, recurse)
        returnError = False
        if type(paths) in types.StringTypes:
            paths = [paths]
        if results==None:
            r = ""
            if recurse: 
                r = " recurse=True"
            results = results.append("Svn add paths=%s %s" % \
                (repr(paths).strip("[]"), r))
        
        for path in paths:
            if self.doNotAddPathTest(path):
                #results.addAction("not adding '%s' (in ignoreList)" % path)
                continue
            self.__addItem(path, results)
            if recurse==True and self.__fs.isDirectory(path):
                try:
                    # look for all unversioned items to possible add
                    statusList = self.statusList(path)
                    # Filter statusList
                    statusList = [s for s in statusList \
                                        if (s.isVersioned==False or s.isDir) and 
                                            not self.doNotAddNameTest(s.name, s.isFile)]
                    paths2 = [status.path for status in statusList if status.path!=path]
                    self.add(paths2, recurse=recurse, results=results)
                except Exception, e:
                    self.__write("Error in: svn_rep.add() %s\n" % str(e))
                    results.append("Error in: svn_rep.add()")
                    returnError = True
        if results==[] or not returnError:
            return None
        return results

    @SvnErrorWrap
    def __addItem(self, path, results, isParent=False):
        """ add a signal item """
        #print "svn_rep.__addItem(path='%s', isParent=%s)" % (path, isParent)
        try:
            info={"path":path, "action":"addItem"}
            if not self.__fs.exists(path):
                results.append("Add path='%s' does not exist!" % path)
                return False
            statusList = self.statusList(path)
            if statusList==[]:
                results.append("Can not add '%s'!" % path)
                return False
            status = statusList[-1]
            if status.isVersioned==False or status.status==ItemStatus.Deleted:
                if status.status==ItemStatus.NONE:
                    if path.find("/skin/")!=-1:
                        return False
                    # then add parent and get status again
                    parentPath = self.__fs.split(path)[0]
                    self.__addItem(parentPath, results, isParent=True)
                    # get the status again
                    statusList = self.statusList(path)
                    status = statusList[-1]
                    if status.status==ItemStatus.NONE:
                        print "Failed to add parent path for '%s'" % path
                        results.append("Failed to add parent, path-'%s'" % path)
                        return False
                # OK add it
                if isParent:
                    self.__client.add(path, ignore=True, force=True, depth=pysvn.depth.empty)
                else:
                    self.__client.add(path, ignore=True, force=True, depth=pysvn.depth.infinity)
                 
                if not path.endswith(".txt") and self.__fs.isFile(path):
                    # do not try and merge this file
                    self.__client.propset("svn:mime-type", "application/octet-stream", path)
                if isParent:
                    results.append("Added parent '%s'" % path)
                else:
                    results.append("Added '%s'" % path)
            if status==ItemStatus.Ignored:
                return False
            return True
        except Exception, e:
            #print "** Error '%s'" % str(e)
            results.append("Failed to add '%s'" % path)
            return False
    
    
    # ---  Commit  ---
    #####
    @SvnErrorWrap
    def commitEmpty(self, paths, message="added"):
        """
          commit the path(s)/item(s) only does not recurse.
          for committing added directories only
          Note: should/must also add/commit the .ice and .ice/__dir__ directories as well
        """
        self.__clearCache()
        try:
            r = self.__client.checkin(paths, log_message=message, depth=pysvn.depth.empty)
            return r.number
        except pysvn.ClientError, e:
            msg = str(e)
            if msg.find(" 403 Forbidden ")>-1:
                msg = "Commit: write access forbidden! (ReadOnly)"
                e2 = Exception(msg)
            e2 = Exception(msg)
            raise e2
        except Exception, e:
            raise e
    
    @SvnErrorWrap
    def commitAll(self, paths, message="commit", callback=None):
        """
        """
        self.__clearCache()
        errCount = 0
        if paths==[]:           ## svn BUG - if given an empty list svn crashes!!!
            return
        while True:
            try:
                r = self.__client.checkin(paths, log_message=message, depth=pysvn.depth.infinity)
                if r is None:
                    return None
                return r.number
            except pysvn.ClientError, e:
                errCount += 1
                if errCount>10:
                    raise e
                msg = str(e)
                if msg.find(" 403 Forbidden ")>-1:
                    msg = "Commit: write access forbidden! (ReadOnly)"
                    raise Exception(msg)
                if msg.find(" is out of date;")>0:
                    pass
                if msg.find("' is missing")>0:
                    # So that we can commit a folder with 'missing'/shelved folders in it
                    m = re.search("Directory '(.*?)' is missing", msg)
                    if m:
                        path = m.groups(0)[0]
                        pPath = self.__fs.split(path)[0]
                        if pPath in paths:
                            self._updateBasic(pPath)
                            continue
                match = re.search("Can't .* '([^']*)'.*No such file or directory", msg) or \
                    re.search(".* '(.*/\.ice/.*)' remains in conflict", msg)
                if match:       # if an item is missing try to revert it and try again
                    missingFile = match.groups(0)[0]
                    self.revert(missingFile)
                    # try again
                else:
                    print "   ====="
                    print msg
                    print "   ====="
##Commit failed (details follow):
##File or directory '_lastModified.tmp' is out of date; try updating
##The version resource does not correspond to the resource within the transaction.
##  Either the requested version resource is out of date (needs to be updated),
##   or the requested version resource is newer than the transaction root (restart the commit).                    
                    raise e
            except Exception, e:
                raise e
        
    
    @SvnErrorWrap
    def commit(self, paths, message="commit", recurse=True, actionResults=None):
        """
            commit only items that have been added or have been modified.
        """
        self.__clearCache()
        #print "svn_rep.commit(paths='%s', recurse=%s)" % (paths, recurse)
        # Note: you must add any items that are to be committed (unversioned items are not committed)
        _lastErrorFile = None
        if message is None or message=="":
            message = " "
        if type(paths) is types.StringType:
            paths = [paths]
        if actionResults==None:
            r = ""
            if recurse: r = " recurse=True"
            actionResults = self.iceContext.ActionResults("svn commit paths=%s %s" % \
                (repr(paths).strip("[]"), r))
        try:
            while True:
                #print "calling __commit()"
                actionResult = self.__commit(paths, message=message, recurse=recurse)
                #print "actionResult='%s'" % actionResult
                if actionResult.isError:
                    errMsg = actionResult.exceptionMessage
                    print "\nerrMsg='%s'" % errMsg
                    match = re.search("Can't .* '([^']*)'.*No such file or directory", errMsg)
                    if match:       # if an item is missing try to revert it and try again
                        errorFile = match.groups(0)[0]
                        print "'%s' is missing" % errorFile
                        if errorFile!=_lastErrorFile:     
                            statusList = self.statusList(errorFile)
                            if statusList is not []:
                                status = statusList[-1]
                                if str(status.status)=="Missing":
                                    self.__write("commit attempt failed: '%s' missing - reverting missing item and trying again.\n" % errorFile)
                                    self.revert(errorFile)
                                    _lastErrorFile = errorFile
                                    # Try Again
                                    continue
                    actionResults.addAction(actionResult)
                break
        except Exception, e:
            raise e
        return actionResults
    
    @SvnErrorWrap
    def __commit(self, paths, message, recurse):
        paths = self.__addAnyRequiredParents(paths)
        info = {"paths":paths, "action":"commit", "recurse":recurse}
        try:
            #print "__client.checkin(paths='%s')" % str(paths)
            self.__client.checkin(paths, log_message=message, recurse=recurse)
            return self.iceContext.ActionResult(
                        "Committed %s" % (repr(paths).strip("[]")), info=info)
        except pysvn.ClientError, e:
            msg = str(e)
            if msg.find(" 403 Forbidden ")>-1:
                msg = "Commit: write access forbidden! (ReadOnly)"
                return self.iceContext.ActionResult(
                            msg, exception=e, info=info)
            else:
                return self.iceContext.ActionResult(
                            "Commit ", exception=e, info=info)
    
    
    def __addAnyRequiredParents(self, paths):
        # get a list all the parents
        parentPaths = {}
        for path in paths:
            parentPath = self.__fs.split(path)[0]
            parentPaths[parentPath] = None
        parentPaths = parentPaths.keys()
        # now filter it to only include those that have been added
        parentPaths = [path for path in parentPaths 
                if self.statusList(path)[-1].status==ItemStatus.Added]
        if parentPaths!=[]:
            parentPaths = self.__addAnyRequiredParents(parentPaths)
        parentPaths.extend(paths)
        return parentPaths
    
    
    
    # ---  Update  ---
    def updateAll(self, path, revision=None, updateResolver=None):
        self.__clearCache()
        if revision is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.head)
        while True:
            try:
                self.__client.update(path, revision=revision, depth=pysvn.depth.infinity)
                break
            except pysvn.ClientError, ce:
                if callable(updateResolver):
                    updateResolver(str(ce), path, ce)
                else:
                    raise ce
            except Exception, e:
                raise e
    
    
    def updateFiles(self, path, revision=None, updateResolver=None):
        self.__clearCache()
        if revision is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.head)
        while True:
            try:
                self.__client.update(path, revision=revision, depth=pysvn.depth.files)
                break
            except pysvn.ClientError, ce:
                if callable(updateResolver):
                    updateResolver(str(ce), path, ce)
                else:
                    raise ce
            except Exception, e:
                raise e
    
    
    def updateEmpty(self, path, revision=None, updateResolver=None):
        print "updateEmpty(path='%s')" % path
        self.__clearCache()
        if revision is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.head)
        while True:
            try:
                self.__client.update(path, revision=revision, depth=pysvn.depth.empty)
                break
            except pysvn.ClientError, ce:
                if callable(updateResolver):
                    updateResolver(str(ce), path, ce)
                else:
                    raise ce
            except Exception, e:
                raise e


    def _updateBasic(self, path):
        # Required because pysvn.update with depth=infinity argument behaves diffenetly!!!
        #  This will ('delete')/remove missing content from the working copy (only).
        self.__clearCache()
        try:
            self.__client.update(path, recurse=True)
        except Exception, e:
            raise e
    
    
    @SvnErrorWrap
    def update2(self, path, recurse, revision):
        """ return (WarningMessage, ErrorMessage) ("", "") for OK """
        self.__clearCache()
        maxRetries = 3
        if revision is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.head)
        while True:    # keep trying until all conflicts are resolved
            try:
                self.__update2(path, recurse, revision=revision)
                break
            except Exception, e:
                maxRetries -= 1
                if maxRetries < 1:
                    msg = "svn_rep.update2() Error: too many conflicts or unable to resolve a conflict!"
                    msg += " path='%s'" % path
                    return path, msg
                if hasattr(e, "path"):
                    #print "** conflicting item '%s'" % e.path
                    if e.path.find("/.ice/")>0:
                        print "Conflict in .ice folder. reverting to previous revision"
                        # OK revert conflicting .ice file
                        self.__client.revert(e.path)
                        if str(e).find(" add "):
                            self.__fs.delete(e.path)
                        continue
                    resultErr, resultMsg = self.__resolveConflictingItem(e.path)
                    if resultErr:
                        return e.path, resultMsg
                    else:
                        pos = resultMsg.find("been renamed to ")
                        if pos>0:
                            renamedTo = resultMsg[pos + len("been renamed to "):]
                        return resultMsg, ""
                else:
                    return "Eror", "Unexpected exception in __update2 '%s'" % str(e)
        
        #check for conflicts
        conflicts = [item for item in self.__client.status(path, recurse=True, get_all=True, update=False, ignore=False) \
                     if item.text_status==pysvn.wc_status_kind.conflicted or \
                      item.prop_status==pysvn.wc_status_kind.conflicted]
        for item in conflicts:
            if item.path.find("/.ice/")!=-1:
                # property conflict
                print "Conflict in .ice folder. reverting to previous revision"
                self.__client.revert(item.path, recurse=False)  # revert to the server's copy
                #if item.path.endswith("/tags"):
                #    # Merge the tags changes (mergeTags)
                #    self.__resolveConflictingTags(item.path)
                #else:
                #    self.__client.revert(item.path, recurse=False)  # revert to the server's copy
            else:
                # ok we need to rename to myChanges_
                resultErr, resultMsg = self.__resolveConflictingItem(item.path)
                if resultErr:
                    return item.path, resultMsg
                else:
                    pos = resultMsg.find("been renamed to ")
                    if pos>0:
                        renamedTo = resultMsg[pos + len("been renamed to "):]
                    return resultMsg, ""
        return "", ""
    
    def __update2(self, path, recurse, revision, _tryagain=True):
        try:
            #self.__client.update(path, recurse=recurse, revision=revision)
            if recurse:
                self.__client.update(path, revision=revision, depth=pysvn.depth.infinity)
            else:
                print "__update2 files - path='%s'" % path
                self.__client.update(path, revision=revision, depth=pysvn.depth.files)
        except pysvn.ClientError, e:
            msg = str(e)
            
            match = re.search("'([^']*)' locked", msg)
            if match!=None:
                path = match.group(1)
                if _tryagain:    # Try once again after doing a cleanup
                    self.cleanup(path)
                    return self.__update2(path, recurse, revision, False)
                else:
                    raise e
            
            # Failed to add file 'path/file': object of the same name already exists
            match = re.search("Failed to add file '(.*?)':", msg)
            if match!=None:
                path = match.group(1)
                error = Exception("Repository update failed to add file: " + msg)
                error.path = path
                raise error
            
            match = re.search("Failed to add directory '(.*?)':", msg)
            if match!=None:
                path = match.group(1)
                #error = SvnUpdateFailedToAddDir(msg)
                error = Exception("Respository update failed to add directory: " + msg)
                error.path = path
                raise error
            
            match = re.search("is not the same repository as", msg)
            if match!=None:
                # Is not the same repository!
                pass
            # ELSE
            error = Exception("Unexcepted client error in svn_rep.update() - " + msg)
            raise error
        except Exception, e:
            msg = str(e)
            self.__write("Unexcepted update error: %s\n" % msg)
            raise e
    
    # ---  Update  ---
    @SvnErrorWrap
    def update(self, paths, recurse=False, actionResults=None, 
            revisionNumber=None):
        # Note: do not call with a large list
        #   e.g. is a path is directory other than ./ice/item/ then should not be recursive
        
        self.__clearCache()
        if type(paths) is types.StringType:
            paths = [paths]
        if actionResults==None:
            r = ""
            if recurse: r = " recurse=True"
            actionResults = self.iceContext.ActionResults("svn update paths=%s %s" % \
                (repr(paths).strip("[]"), r))
        
        # get revision to update to
        if revisionNumber is not None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.number, revisionNumber)
        else:
            revision = pysvn.Revision(pysvn.opt_revision_kind.head)
        
        for path in paths:
            # update one item at a time
            info = {"path":path, "action":"update"}
            try:
                maxRetries = 3
                while True:    # keep trying until all conflicts are resolved
                    try:
                        self.__update(path, recurse, revision=revision)
                        break
                    except Exception, e:
                        maxRetries -= 1
                        if maxRetries < 1:
                            msg = "svn_rep.update() Error: too many conflicts or unable to resolve a conflict!"
                            raise Exception(msg)
                        if hasattr(e, "path"):
                            #print "** conflicting item '%s'" % e.path
                            if e.path.find("/.ice/")>0:
                                # OK revert conflicting .ice file
                                self.__client.revert(e.path)
                                continue
                            resultErr, resultMsg = self.__resolveConflictingItem(e.path)
                            if resultErr:
                                actionResults.addAction("resolveConflictingItem", exception=resultMsg, 
                                        info={"path":e.path})
                                break
                            else:
                                info = {"path":e.path}
                                pos = resultMsg.find("been renamed to ")
                                if pos>0:
                                    renamedTo = resultMsg[pos + len("been renamed to "):]
                                    info["renamedTo"] = renamedTo
                                actionResults.addAction("resolveConflictingItem", resultMsg, 
                                        isWarning=True, info=info)
                                # ok try again
                                continue
                        else:
                            actionResults.addAction("Unexpected exception in __update", exception=e, info=info)
                            break
                
                #check for conflicts
                conflicts = [item for item in self.__client.status(path, recurse=True, get_all=True, update=False, ignore=False) \
                             if item.text_status==pysvn.wc_status_kind.conflicted or \
                              item.prop_status==pysvn.wc_status_kind.conflicted]
                for item in conflicts:
                    if item.path.find("/.ice/")>-1:
                        # property conflict
                        self.__client.revert(item.path, recurse=False)  # revert to the server's copy
                        #if item.path.endswith("/tags"):
                        #    # Merge the tags changes (mergeTags)
                        #    self.__resolveConflictingTags(item.path)
                        #else:
                        #    self.__client.revert(item.path, recurse=False)  # revert to the server's copy
                    else:
                        # ok we need to rename to myChanges_
                        resultErr, resultMsg = self.__resolveConflictingItem(item.path)
                        if resultErr:
                            actionResults.addAction("resolveConflictingItem", exception=resultMsg, 
                                    info={"path":item.path})
                        else:
                            info = {"path":item.path}
                            pos = resultMsg.find("been renamed to ")
                            if pos>0:
                                renamedTo = resultMsg[pos + len("been renamed to "):]
                                info["renamedTo"] = renamedTo
                            actionResults.addAction("resolveConflictingItem", resultMsg, 
                                    isWarning=True, info=info)
                actionResults.addAction("Updated '%s'" % path, info=info)
            except Exception, e:
                actionResults.addAction("update", exception=e, info=info)
        return actionResults
    
    @SvnErrorWrap
    def __update(self, path, recurse, revision, _tryagain=True):
        try:
            #print "__client.update(path='%s')" % path
            self.__client.update(path, recurse=recurse, revision=revision)
        except pysvn.ClientError, e:
            msg = str(e)
            match = re.search("'([^']*)' locked", msg)
            if match!=None:
                path = match.group(1)
                if _tryagain:    # Try once again after doing a cleanup
                    self.cleanup(path)
                    return self.__update(path, recurse, revision, False)
                else:
                    raise e
            # Failed to add file 'path/file': object of the same name already exists
            match = re.search("Failed to add file '(.*?)':", msg)
            if match!=None:
                path = match.group(1)
                error = Exception("Repository update failed to add file: " + msg)
                error.path = path
                raise error
            match = re.search("Failed to add directory '(.*?)':", msg)
            if match!=None:
                path = match.group(1)
                #error = SvnUpdateFailedToAddDir(msg)
                error = Exception("Respository update failed to add directory: " + msg)
                error.path = path
                raise error
            match = re.search("is not the same repository as", msg)
            if match!=None:
                # Is not the same repository!
                pass
            # ELSE
            error = Exception("Unexcepted client error in svn_rep.update() - " + msg)
            raise error
        except Exception, e:
            msg = str(e)
            self.__write("Unexcepted update error: %s\n" % msg)
            raise e
    
    
    # ---  MakeDirectory  ---
    @SvnErrorWrap
    def makeDirectory(self, path, message="mkdir", svnIgnore=False):
        self.__clearCache()
        if self.__fs.isDirectory(path):
            pass
        else:
            parentPath = self.__fs.split(path)[0]
            if not self.__fs.isDirectory(parentPath):
                self.makeDirectory(parentPath, message)
            try:
                #self.__client.mkdir(path, message)
                if svnIgnore:
                    parent, pattern = self.__fs.split(path)
                    self.__addSvnIgnore(parent, pattern)
                    self.__fs.makeDirectory(path)
                else:
                    self.__client.mkdir(path, message)
            except Exception, e:
                raise e
    
    
    # ---  Delete  ---
    @SvnErrorWrap
    def delete(self, path):
        self.__clearCache()
        try:
            self.__client.remove(path, force=True)
        except Exception, e2:
            try:
                try:
                    self.revert(path)
                except:
                    pass
                self.__client.remove(path, force=True)
            except Exception, e:
                msg = str(e)
                if msg.find(" is not a working copy")!=-1:
                    return False
                if msg.endswith(" does not exist"):
                    return True
                raise e
        return True
    
    
    # ---  Copy  ---
    @SvnErrorWrap
    def copy(self, path, destinationPath):
        self.__clearCache()
        try:
            self.__client.copy(path, destinationPath)
##            # Added items must be committed before copying
##            # Or else revert(unAdd) and then do a file system copy
##            listItems = self.statusList(path)
##            if listItems == []:
##                pass
##            elif listItems[-1].status==ItemStatus.Added:
##                if self.__fs.isFile(path):
##                    self.__fs.copy(path, destinationPath)
##                    self.add(destinationPath)
##                else:
##                    self.__fs.copy(path, destinationPath, excludingDirectories=[".svn"])
##                    self.add(destinationPath)
##            else:
##                # Note: setting src_revision explicitly because there appears to be a bug
##                #    in pysvn.Client.copy() - it should be using 'working' when path is a path!
##                rev = pysvn.Revision(pysvn.opt_revision_kind.working)
##                try:
##                    self.__client.copy(path, destinationPath, src_revision=rev)
##                except Exception, e:
##                    msg = str(e)
##                    if msg.find(" into its own child ")>0:
##                        self.__client.export(path, destinationPath, force=True, revision=rev)
##                        self.add(destinationPath)
##                    else:
##                        raise e
        except Exception, e:
            raise e
    
    # ---  Move/Rename  ---
    @SvnErrorWrap
    def move(self, path, destinationPath):
        self.__clearCache()
        try:
            # First make sure that the destinationPath (parent path) exists
            self.makeDirectory(self.__fs.split(destinationPath)[0])
            
            if False:        # Workaround is not longer needed
                # Added items must be committed before moving or renaming
                # or else do os move and svn delete --force and svn add
                #   and copy any properties too
                item = self.statusList(path)[-1]
                if item.status==ItemStatus.Added:
                    #workaround for the item status is added
                    if self.__fs.isDirectory(path):
                        self.moveSubCopy(path, destinationPath)
                    else:
                        self.__fs.copy(path, destinationPath)
                    self.add(destinationPath)
                    self.__client.remove(path, force=True)
                else:
                    self.__client.move(path, destinationPath, force=True)
            else:
                self.__client.move(path, destinationPath, force=True)
        except Exception, e:
            print "*** svn_rep.move error - '%s'" % str(e)
            raise e
    
    #workaround for the item status is added
    def moveSubCopy(self, path, destinationPath):
        def callback(path, dirs, files):
            for dir in dirs:
                dirPath = "%s/%s" % (path.rstrip("/"), dir)
                if dirPath.find(".svn")==-1:
                    rFiles.append(dir)
            for file in files:
                filePath = "%s/%s" % (path.rstrip("/"), file)
                if filePath.find(".svn")==-1:
                    rFiles.append(file)
        rFiles = []
        self.__fs.walker(path, callback)
    
        try:
            for file in rFiles:
                oriPath = "%s/%s" % (path.rstrip("/"), file)
                destPath = "%s/%s" % (destinationPath.rstrip("/"), file)
                self.__fs.copy(oriPath, destPath)
        except Exception, e:
            raise e
            
    
    # ---  Export  ---
    @SvnErrorWrap
    def export(self, path, destinationPath):
        """ Copy a given file or dir from the repository to another location
        (not related to the repository)
        """
        try:
            if self.__fs.isFile(path):
                bPath = self.__fs.split(destinationPath)[0]  #path = os path.dirname(destinationPath)
                if not self.__fs.exists(bPath):
                    self.__fs.makeDirectory(bPath)       #os mkdir(path)
                f = open(path, "rb")
                data = f.read()
                f.close()
                f = open(destinationPath, "wb")
                f.write(data)
                f.close()
            else:
                self.__client.export(path, destinationPath, force=True)
        except Exception, e:
            raise e
    
    
    # ---  GetLogData  ---
    @SvnErrorWrap
    def getLogData(self, path, levels=None):
        # Returns a logData object or a list of logData objects levels is given
        # The logData object has the following properties:
        #    date -    (string)
        #    message - (string)
        #    author -  (string)
        #    revisionNumber - (integer)
        localtime = self.iceContext.localtime
        class _logData:
            def __init__(self, svnlog):
                date = localtime(svnlog["date"])
                self.date = "%s-%s-%s %s:%s" % (date[0], date[1], date[2], date[3], ("0"+str(date[4]))[-2:])
                self.message = svnlog["message"]
                self.author = svnlog["author"]
                self.revisionNumber = svnlog["revision"].number
            def __str__(self):
                tmp = "Revision#: %s, " % str(self.revisionNumber)
                tmp += "Date: %s, " % self.date
                tmp += "Author: '%s', " % self.author
                tmp += "Message: '%s'" % self.message
                return tmp
        
        try:
            workingRev = pysvn.Revision(pysvn.opt_revision_kind.working)
            svnlogs = self.__client.log(path, revision_start=workingRev)
            if levels==None:
                if len(svnlogs)<1:
                    return None
                return _logData(svnlogs[0])
            else:
                logs = []
                count = 0
                for svnlog in svnlogs:
                    logs.append(_logData(svnlog))
                    count += 1
                    if count>=levels:
                        break
                return logs
        except Exception, e:
            raise e
    
    
    #
    # ---  Cleanup  ---
    @SvnErrorWrap
    def cleanup(self, path=None):
        self.__clearCache()
        if path==None:
            path = self.__basePath
        if not self.__fs.isDirectory(path):
            raise Exception("no valid path given to cleanup()")
        self.__client.cleanup(path)
    
    
    # ---  Revert  ---
    @SvnErrorWrap
    def revert(self, path, recurse=True):
        self.__clearCache()
        try:
            r = self.__client.revert(path, recurse=recurse)
        except Exception, e:
            raise e
    
    
    def info(self, path, single=True):
        # uses pysvn.info2()
        # return a dictionary/object
        #   .name,  .kind,  .URL,   .last_changed_author
        #   .rev,  .last_changed_rev
        #   .wc_info  (.schedule + working file(s) names)
        if single:
            l = self.__client.info2(path, depth=pysvn.depth.empty)
            l[0][1]["name"] = l[0][0]
            return l[0][1]
        else:
            l = self.__client.info2(path, depth=pysvn.depth.immediates)
            for a, b in l:
                b["name"] = a
            l = [b for a,b in l]
            return l
    
    ############
    ## list(path)
    ## getStatus(path, update=False)
    ## getStatusList(path, update=False)  ## Not yet (optimized)
    
    # pysvn.status(update, depth=files|immediates|infinity|empty)  empty=selfOnly, immediates
    #       -> StatusList  (text_status*, repos_text_status, is_versioned, path, entry*)
    #           (entry -> kind, is_absent, commit_author, url, is_deleted, revision, commit_revision)
    # pysvn.list(depth=immediates, dirent_fields=pysvn.SVN_DIRENT_KIND | pysvn.SVN_DIRENT_LAST_AUTHOR)
    #       *For missing items
    #       -> List  (kind, path, repos_path, last_author
    # pysvn.info2(depth=immediates|empty)
    #       -> Info  (kind, rev, last_changed_rev, URL, last_changed_author, wc_info)
    #               (wc_info - schedule + work/reject file info)
    
    class ItemStatus2(object):
        def __init__(self, name="", statusStr="", isDir=False, isFile=False,
                        isOutOfDate=False, 
                        lastChangedRevisionNumber=-1, update=False):
            self.name = name
            self.statusStr = statusStr
            self.isMissing = statusStr=="missing"
            self.isDir = isDir
            self.isFile = isFile
            self.isOutOfDate = isOutOfDate
            self.isVersioned = statusStr!="unversioned"
            self.lastChangedRevisionNumber = lastChangedRevisionNumber
            self.update = update
        def getCompleteStatus(self):
            result = "in sync"
            offline = ""
            outOfDate = ""
            if self.update:
                if self.isOutOfDate:
                    outOfDate = " out-of-date"
            else:
                offline = " (offline)"
            if self.statusStr=="normal":
                result = offline
            else:
                result = self.statusStr + offline
            if result.startswith("normal"):
                result = result[len("normal"):]
            result += outOfDate
            if result=="":
                result = "in sync"
            if not result.startswith("m"):
                result = result.capitalize()
            return result
        def __str__(self):
            return self.statusStr
    
    
    def list(self, path, update=False):
        try:
            l = self.__svnListImmediates(path)      #self.__client.list(path, depth=pysvn.depth.immediates)
            if l!=[]:
                l = l[1:]
            l = [a for a, b in l]
            for i in l:
                i.name = self.__fs.split(i.path)[1]
                if i.kind==pysvn.node_kind.dir:
                    i.name += "/"
            l = [i.name for i in l]
        except pysvn.ClientError, ce:
            l = []
        try:
            sl = self.__client.status(path, update=update, depth=pysvn.depth.immediates)
            if sl!=[]:
                sl = sl[1:]
            for i in sl:
                if i.entry is None:
                    p = i.path
                    s = self.getStatus(p, update)
                    if s is not None:
                        name = s.name
                        if s.isDir:
                            name += "/"
                    else:
                        continue
                else:
                    name = i.entry.name
                    if i.entry.kind==pysvn.node_kind.dir:
                        name += "/"
                if name not in l:
                    l.append(name)
        except pysvn.ClientError, ce:
            pass
        dirs, files = self.__fs.listDirsFiles(path)
        dirs = [unicode(d + "/") for d in dirs if d!=".svn"]
        files = [unicode(f) for f in files]
        for d in dirs:
            if d not in l:
                if d.rstrip("/") in l:
                    l.remove(d.rstrip("/"))
                l.append(d)
        for file in files:
            if file not in l:
                l.append(file)
        return l
    
    
    def hasChanges(self, path):
        status = pysvn.wc_status_kind
        states = [status.added, status.deleted, status.modified, 
                    status.replaced, #status.unversioned,
                    status.merged, status.incomplete]
        try:
            s = self.__client.status(path, update=False, depth=pysvn.depth.infinity)
            for i in s:
                if i.text_status in states:
                    print "svn_rep.hasChanges because '%s'" % i.text_status
                    print " ", i.path
                    return True
            return False
        except pysvn.ClientError, ce:
            return False
    
    
    def getStatus(self, path, update=False, single=True):
        # uses both pysvn.status() and pysvn.list() methods
        # returns an ItemStatus2 object
        pPath, name = self.__fs.split(path)
        if single:
            depth = pysvn.depth.empty
        else:
            depth = pysvn.depth.infinity
        try:
            s = self.__client.status(path, update=False, depth=depth)
        except pysvn.ClientError, ce:
            #print "status ClientError '%s'" % str(ce)
            #return None
            s = []
        if s==[]:
            #print "getStatus() may be missing"
            # may be missing
            if update:  # get url for pPath
                reposLastChangedRevsionNumber = None
                reposKind = None
                try:
                    s = self.__client.status(pPath, update=False, depth=pysvn.depth.empty)
                except pysvn.ClientError, ce:
                    s = []
                if s==[]:
                    return None
                s = s[0]
                if s.entry is not None:
                    url = s.entry.url
                    if url is not None:
                        url = url + "/" + name
                        try:
                            i = self.__client.info2(url, depth=pysvn.depth.empty)
                            if len(i)>0:
                                i = i[0][1]
                                reposLastChangedRevsionNumber = i.last_changed_rev.number
                                reposKind = i.kind
                        except pysvn.ClientError, ce:
                            pass
            try:
                # Note: reading from PARENT directory
                l = self.__svnListImmediates(pPath)     #self.__client.list(pPath, depth=pysvn.depth.immediates)     # SLOW
            except pysvn.ClientError, ce:
                #print "list ClientError '%s'" % str(ce)
                return None
            # now filter out the path object
            l = [a for a, b in l if a.path.endswith("/" + name)]
            if l == []:
                if update and reposKind is not None: 
                    itemStatus = SvnRep.ItemStatus2(name, "missing", 
                                isDir=reposKind==pysvn.node_kind.dir, 
                                isFile=reposKind==pysvn.node_kind.file, update=update)
                    itemStatus.isOutOfDate = True
                else:
                    itemStatus = None
            else:
                l = l[0]
                itemStatus = SvnRep.ItemStatus2(name, "missing", 
                            isDir=l.kind==pysvn.node_kind.dir, 
                            isFile=l.kind==pysvn.node_kind.file, 
                            update=pysvn.depth.empty)
                itemStatus.isOutOfDate = True
        else:
            slist = s
            s = slist[-1]
            isVersioned = s.is_versioned
            statusStr = str(s.text_status)
            if statusStr=="normal":
                k = pysvn.wc_status_kind
                checkList = [k.added, k.deleted, k.incomplete, k.merged, k.modified, k.replaced]
                for i in slist:
                    if i.text_status in checkList:
                        statusStr = "modified"
            if s.entry is None:
                isDir = self.__fs.isDirectory(path)
                isFile = self.__fs.isFile(path)
                itemStatus = SvnRep.ItemStatus2(name, statusStr, isDir=isDir, \
                                isFile=isFile, update=update)
            else:
                isDir = s.entry.kind==pysvn.node_kind.dir
                isFile = s.entry.kind==pysvn.node_kind.file
                itemStatus = SvnRep.ItemStatus2(name, statusStr, isDir=isDir, \
                                isFile=isFile, update=update)
                # now get lastChangedRevisionNumber
                i = self.__client.info2(path, depth=depth)[0][1]
                revNum = i.last_changed_rev.number
                itemStatus.lastChangedRevisionNumber = revNum
            if update:
                # not get repository lastChangedRevisionNumber
                if s.entry is None:
                    itemStatus.isOutOfDate = True
                else:
                    url = s.entry.url
                    if url is not None:
                        try:
                            i = self.__client.info2(url, depth=depth)
                            if len(i)>0:
                                i = i[0][1]
                                rRevNum = i.last_changed_rev.number
                                if rRevNum > revNum:
                                    itemStatus.isOutOfDate = True
                        except pysvn.ClientError, ce:
                            pass
                            itemStatus.isOutOfDate = True       # ??? assume
                    else:
                        itemStatus.isOutOfDate = True
            if itemStatus.isOutOfDate and itemStatus.statusStr=="unversioned":
                itemStatus.isOutOfDate = False
        return itemStatus
    
    
    def getStatusList(self, path, update=False):
        # for optimization.  NOTE: You will have to merge in property statuses as well (inc. dir prop status)
        # returns a list of ItemStatus2 objects
        pass
    
    ############
    
    
    def statusList(self, path):
        """ returns a list of ListItem objects """
        #  ListItem object properties
        #    path              filepath
        #    name              filename
        #    isFile            boolean
        #    isDir             boolean
        #    isLocked          boolean
        #    isVersioned       boolean 
        #    isIgnored         boolean
        #    revision          integer               or -1
        #    commitRevision    integer               or -1
        #    commitAuthor      commit author string  or None
        #    status            ItemStatus object     or None
        #    statusStr         str(status)
        #NOTE:
        #   If you want the status of a directory only (not it's contents)
        #   just retrive the last item in the list e.g. listItems[-1]
        class myList(list):
            def sort(self):
                return list.sort(self, self.__sort)
            def __sort(self, a, b):
                r = cmp(a.isFile, b.isFile)
                if r==0: r = cmp(a.name, b.name)
                return r
        listItems = myList()
        try:
            for s in self.__client.status(path, recurse=False, get_all=True, \
                                            update=False):
                listItem = ListItem(self.iceContext.fs, s, self.ignoreTest)
                listItems.append(listItem)
        except pysvn.ClientError, ce:
            msg = str(ce)
            if msg.find("is not a working copy")>0:
                listItem = ListItem(self.iceContext.fs, path=path, ignoreTest=self.ignoreTest)
                listItems.append(listItem)
            else:
                raise ce
        except Exception, e:
            raise e
        if self.__fs.isDirectory(path):
            if len(listItems)>0:
                listItem = listItems[-1]
                listItem.name = "."
        # Note: '.' and  '.ice' folders
        return listItems
    
    
    def ls(self, path):
        l = []
        try:
            for i in self.__client.ls(path, recurse=False):
                l.append(i.get("name", None))
        except:
            pass
        return l
    
    
    def getMissing(self, path):
        slist = self.__client.status(path, recurse=False, get_all=True, update=False)
        list2 = self.__client.list(path, recurse=False)
        slist = [self.__fs.split(i["path"])[1] for i in slist]
        list2 = [self.__fs.split(i[0]["path"])[1] for i in list2]
        return [i for i in list2 if i not in slist]
    
    
    def isDirModifiedAdded(self, path):
        """ recursively checks a directory for any added, modified, deleted content """
        try:
            for svn_status in self.__client.status(path, recurse=True, get_all=True, update=False):
                textStatus = svn_status.text_status
                if textStatus==pysvn.wc_status_kind.added:
                    return True
                elif textStatus==pysvn.wc_status_kind.deleted:
                    return True
                elif textStatus==pysvn.wc_status_kind.modified:
                    return True
        except Exception, e:
            msg = str(e)
            if msg.find("is not a working copy")!=-1:
                return False
            else:
                raise e
        return False
    
    
    def revInfo(self, path, includeServer=False):
        # path can be a directory or a file
        # returns an RevInfo
        class RevInfo(object):
            def __init__(self):
                self.revNum = -1
                self.lastChangedRevNum = -1
                self.isLocked = False
                self.kind = "NONE"
                self.reposRevNum = -1
                self.reposLastChangedRevNum = -1
                self.reposKind = "NONE"
            @property
            def isOutOfDate(self):
                return self.lastChangedRevNum!=self.reposLastChangedRevNum
            def __str__(self):
                s = "rev=%s, lastChangeRev=%s, kind=%s, reposRev=%s, reposLastChangedRev=%s, reposKind=%s, outofDate-%s" % \
                    (self.revNum, self.lastChangedRevNum, self.kind, 
                        self.reposRevNum, self.reposLastChangedRevNum, self.reposKind,
                        self.isOutOfDate)
                return s
        
        revInfo = RevInfo()
        try:
            info = self.__client.info2(path, recurse=False)[0][1]
            revInfo.revNum = info.rev.number
            revInfo.lastChangedRevNum = info.last_changed_rev.number
            revInfo.isLocked = bool(info.lock)
            revInfo.kind = str(info.kind)
        except Exception, e:
            msg = str(e)
            if msg.find("Cannot read entry for ")>-1:
                pass
                includeServer = False
            else:
                raise e
        if includeServer:
            try:
                urlInfo = self.__client.info2(info.URL, recurse=False)[0][1]
                revInfo.reposRevNum = urlInfo.rev.number
                revInfo.reposLastChangedRevNum = urlInfo.last_changed_rev.number
                revInfo.reposKind = str(urlInfo.kind)
            except Exception, e:
                msg = str(e)
                if msg.find(" non-existent in revision ")>-1:
                    pass
                else:
                    raise e
        return revInfo
    
    
    @SvnErrorWrap
    def getUpdateList(self, path, recurse=True):
        l = []
        if False:
            # This fails to list out-of-date directories
            l = self.__client.status(path, recurse=recurse, update=True, get_all=False)
            ignore = [pysvn.wc_status_kind.normal, pysvn.wc_status_kind.none, 
                        pysvn.wc_status_kind.ignored, pysvn.wc_status_kind.unversioned]
            l = [i for i in l if i.repos_text_status not in ignore or
                                                i.repos_prop_status not in ignore]
            #
            info = self.__client.info2(path, recurse=False)[0][1]
            if info.kind == pysvn.node_kind.dir:
                try:
                    urlInfo = self.__client.info2(info.URL, recurse=False)[0][1]
                    if urlInfo.last_changed_rev.number > info.last_changed_rev.number:
                        o = self.iceContext.Object()
                        o.path = path
                        l.append(o)
                except Exception, e:
                    pass
        else:
            ##
            infos = self.__client.info2(path, recurse=recurse)
            #if infos[0][1].kind == pysvn.node_kind.dir:
            if True:
                url = infos[0][1].URL
                infos = [i for n, i in infos]
                d = {}
                for i in infos:
                    p = i.URL.replace(url, path)
                    d[p] = i
                try:
                    urlInfos = self.__client.info2(url, recurse=recurse)
                    urlInfos.reverse()
                    for n, urlInfo in urlInfos:
                        p = urlInfo.URL.replace(url, path)
                        info = d.get(p, None)
                        if info is None:
                            o = self.iceContext.Object()
                            o.path = p
                            l.append(o)
                        else:
                            if urlInfo.last_changed_rev.number > info.last_changed_rev.number:
                                o = self.iceContext.Object()
                                o.path = p
                                l.append(o)
                except Exception, e:
                    pass
            ##
        return l
    
    # ---  GetRevision  ---
    @SvnErrorWrap
    def getRevision(self, path, includeUrl=False):
        items= self.__client.info2(path, recurse=False)
        info = items[0][1]
        rev = info["rev"]
        if includeUrl:
            url = info["URL"]
            items= self.__client.info2(url, recurse=False)
            info = items[0][1]
            urlLastRev = info["last_changed_rev"].number
            urlRev = info["rev"].number
            return urlLastRev>rev.number, rev.number, urlLastRev, urlRev
        return rev.number
    
    
    # -----------------
    
    def __refresh(self):
        try:
            # HACK: to work around a svn problem where it is caching properties
            password = self.__password
            self.logout()
            self.login(self.__username, password, retries=3)
            if self.isAuthenticated()==False:
                self.__write("Failed to login again for user: %s\n" % self.__username)
        except Exception, e:
            pass
    
    
    def __resolveConflictingTags(self, path):
        # MergeTags
        print "__resolveConflictingTags path='%s'" % path
        try:
            s = self.__client.status(path)[0]
            entry = s["entry"]
            cWork = entry["conflict_work"]
            cNew = entry["conflict_new"]
            cOld = entry["conflict_old"]
            # get myTags, serverTags and the oldTags
            bPath = self.__fs.split(path)[0]
            if cWork is not None:
                myFile = self.__fs.join(bPath, cWork)
            else:
                myFile = path
            newFile = self.__fs.join(bPath, cNew)
            oldFile = self.__fs.join(bPath, cOld)
            print "myFile='%s'" % myFile
            print "newFile='%s'" % newFile
            #print "oldFile='%s'" % oldFile
            myTags = self.__fs.readFile(myFile)
            newTags = self.__fs.readFile(newFile)
            oldTags = self.__fs.readFile(oldFile)
            print "myTags=%s   %s" % (myTags.replace("\n", " "), type(myTags))
            print "newTags=%s" % newTags.replace("\n", " ")
            #print "oldTags=%s" % oldTags
            #self.__client.resolved(path, recurse=False)
            self.__client.revert(path)
        except Exception, e:
            # if all else fails revert to the servers copy
            self.__client.revert(path, recurse=False)  # revert to the server's copy
    
    
    def __resolveConflictingItem(self, path):
        """ returns a tuple (resultErr, resultMsg) """
        self.__write("svn_rep.__resolveConflictionItem(path='%s')\n" % path)
        resultErr = True
        resultMsg = ""
        info = {"path":path, "action":"update"}
        if self.__fs.isDirectory(path):
            resultMsg = "Can not resolve a conflicting directory '%s' please rename/move and try again." % path
            resultErr = True
        else:
            self.__write("--- Request to resolve conflict file='%s' ---\n" % path)
            # deside what type of conflict this is and then call the apporiate method below to handle it.
            try:
                s = self.__client.status(path)[0]
            except Exception, e:
                resultMsg = "Failed to get the status of '%s'" % path
                resultErr = True
                s = None
            if s is None:
                pass
            # if text 'unversioned'
            elif s.text_status==pysvn.wc_status_kind.unversioned:
                newName = self.__copyConflictingFile(path)
                if newName is not None:
                    self.__fs.delete(path)
                    resultMsg = "Conflicting 'unversioned' file '%s' has been renamed to %s" % \
                                (path, newName)
                    resultErr = False
            # if text 'added'
            elif s.text_status==pysvn.wc_status_kind.added:
                newName = self.__copyConflictingFile(path)
                if newName is not None:
                    self.__client.remove(path, force=True)
                    resultMsg = "Conflicting 'added' file '%s' has been renamed to %s" % \
                                (path, newName)
                    resultErr = False
            # if text 'conflicted'
            elif s.text_status==pysvn.wc_status_kind.conflicted:
                bPath = self.__fs.split(path)[0]
                if s.entry.conflict_work!=None:
                    myFile = self.__fs.join(bPath, s.entry.conflict_work)
                else:
                    myFile = self.__fs.join(bPath, s.entry.name)
                newFile = self.__fs.join(bPath, s.entry.conflict_new)
                # rename myFile to myChanges_x and newFile to path
                myChanges = self.__copyConflictingFile(path, fromFile=myFile)
                self.__copyFile(newFile, path)
                self.__client.resolved(path, recurse=False)
                resultMsg = "Conflicting file '%s' has been renamed to %s" % \
                            (path, myChanges)
                resultErr = False
            # if property 'conflicted'
            elif s.prop_status==pysvn.wc_status_kind.conflicted:
                self.__client.revert(path, recurse=False)  # revert to the server's copy
                resultMsg = "Conflicting properties for file '%s'. Properties have been updated with the server's copy." % \
                                path
                resultErr = False
            # else unhandled conflict!
            else:
                resultMsg = "Unresolve conflict path='%s', text_status='%s', prop_status='%s'" % \
                            (path, s.text_status, s.prop_status)
                resultErr = True;
        return resultErr, resultMsg
    
    
    def __copyConflictingFile(self, path, fromFile=None, _count=1):
        """ Returns the new filename or None if failed to copy """
        if fromFile is None:
            fromFile = path
        if not self.__fs.isFile(fromFile):
            raise Exception("__copyConflictingFile() '%s' is not a file!" % fromFile)
        basePath, name = self.__fs.split(path)
        copyToName = self.__mineCopyNamePrefix + name
        #if _count==1:
        #    copyToName = self.__mineCopyNamePrefix + name
        #else:
        #    copyToName = self.__mineCopyNamePrefix + str(count) + "_" + name
        copyToFile = self.__fs.join(basePath, copyToName)
        #if self.__fs.exists(copyToFile):
        #    return self.__copyConflictingFile(path, _count=_count+1)
        self.__copyFile(fromFile, copyToFile)
        return copyToName
    
    
    def __ResolveConflictingFileX(self, file, reportItem):
        print "svn_rep.__ResolveConflictionFile(file='%s')" % file
        self.__write("__ResolveConflictingFile file='%s'\n" % file)
        """ rerurn True for completed OK """
        # deside what type of conflict this is and then call the apporiate method below to handle it.
        if not self.__fs.isFile(file):
            if self.__fs.isDirectory(file):
                reportItem.error = Exception("Can not resolve a conflicting directory '%s'!" % file)
                reportItem.message += "Can not resolve a conflicting directory! (This is an unexpected Error!)"
            else:
                reportItem.error = Exception("'%s' is not a file!" % file)
                reportItem.message += "Can not resolve conflict file '%s' not found!" % file
            return False
        self.__write("--- Request to resolve conflict file='%s' ---\n" % file)
        
        if self.__fs.isFile(file):
            path = self.__fs.split(file)[0]
        elif self.__fs.isDirectory(file):
            path = file
        self.__addSvnIgnore(path, self.__mineCopyNamePrefix + "*")    #NOTE: Ignores files only
        
        try:
            s = self.__client.status(file)[0]
        except Exception, e:
            raise e
        if s.text_status==pysvn.wc_status_kind.unversioned:
            if self.__copyConflictingFile(file, reportItem):
                self.__fs.delete(file)      #os remove(file)
                reportItem.message += "Conflicting 'unversioned' file '%s' has been renamed to myChanges_%s" % (file, self.__fs.split(file)[1])
                return True
        elif s.text_status==pysvn.wc_status_kind.added:
            if self.__copyConflictingFile(file, reportItem):
                self.__client.remove(file, force=True)
                reportItem.message += "Conflicting 'added' file '%s' has been renamed to myChanges_%s" % (file, self.__fs.split(file)[1])
                return True
        elif s.text_status==pysvn.wc_status_kind.conflicted:
            if s.entry.conflict_work!=None:
                file_mine = self.__fs.join(path, s.entry.conflict_work)
            else:
                file_mine = self.__fs.join(path, s.entry.name)
            file_new = self.__fs.join(path, s.entry.conflict_new)
            if self.__copyConflictingFile(file_mine, reportItem, file):
                self.__copyFile(file_new, file)
                self.__client.resolved(file, recurse=False)
                reportItem.message += "Conflicting file '%s' has been renamed to myChanges_%s" % (file, self.__fs.split(file)[1])
                return True
        elif s.prop_status==pysvn.wc_status_kind.conflicted:
            #self.__client.resolved(file, recurse=False)
            self.__client.revert(file, recurse=False)  # revert to the server's copy
            reportItem.message += "Conflicting properties for file '%s'. \nProperties have been updated with the server's copy." % file
            return True
        msg = "Unresolve conflict filename='%s', text_status='%s', prop_status='%s'" % (file, s.text_status, s.prop_status)
        reportItem.error = Exception(msg)
        reportItem.message += "Unresolve conflict filename='%s'" % file
        return False
    
    
    def __copyConflictingFileX(self, file, reportItem, copyToName=None):
        """ Returns True for completed OK """
        if not self.__fs.isFile(file):
            raise Exception("'%s' is not a file!" % file)
        if copyToName==None:
            path, name = self.__fs.split(file)
        else:
            path, name = self.__fs.split(copyToName)
        copyToName = self.__mineCopyNamePrefix + name
        copyToFile = self.__fs.join(path, copyToName)
        reportItem.myChangesFile = copyToFile
        self.__copyFile(file, copyToFile)
        return True
    



    #------------------------------------------------------------------
    
    def autoCreateCheckoutCheck(self, messageWriter=None):
        if messageWriter is None:
            messageWriter = self.iceContext.output.write
        basePath = self.__basePath
        svnUrl = self.__svnUrl
        if basePath==None or svnUrl==None:
            return "Nothing to do"
        if self.__fs.exists(basePath):
            urlFromPath = self.getUrlForPath(basePath)
            if urlFromPath==None:
                raise Exception("ERROR: The given repository path is not valid!")
            else:
                if urlFromPath!=svnUrl:
                    raise Exception("ERROR: The supplied repository path is not setup to use the supplied repository URL")
                else:
                    # OK already checked out
                    return "Already checked out OK"
        else:
            messageWriter("\n")
            if self.isSvnUrlValid(svnUrl):
                # OK checkit out
                messageWriter("* Checking out the repository from '%s'" % svnUrl)
                self.__checkoutRep(svnUrl, basePath, messageWriter=messageWriter)
                messageWriter("* Check out completed *")
                return "Checked out OK"
            elif svnUrl.startswith("file:///"):
                # svnUrl is a file URL and it is not a valid svnUrl
                #   either it does not yet exist or it is just invalid!
                if self.iceContext.system.isWindows:
                    svnFilePath = svnUrl[len("file:///"):]
                else:
                    svnFilePath = svnUrl[len("file://"):]
                if self.__fs.exists(svnFilePath):
                    raise Exception("File svnURL is not valid because svn file path already exists and is not a valid svn repository!")
                # OK, now try and create a new file repository
                # First make it's parent directories
                self.__fs.makeDirectory(self.__fs.split(svnFilePath)[0])
                messageWriter("* Creating svn file repository.  Please wait...")
                try:
                    self.__createSvnFileRep(svnUrl)
                except Exception, e:
                    msg = "svnURL='%s'" % (svnUrl)
                    raise Exception("Not a valid SVN file repository URL! %s" % msg)
                messageWriter("* Checking out")
                self.__checkoutRep(svnUrl, basePath, messageWriter=messageWriter)
                messageWriter("*")
                self.__fs.makeDirectory(self.__fs.join(basePath, "packages"))
                ####
                if False:
                    ####
                    defaultRep = "defaultRep"
                    if not self.__fs.isDirectory(defaultRep):
                        defaultRep = "../../sample-content"
                        if not self.__fs.isDirectory(defaultRep):
                            msg = "Can not create a svn file repository. The 'defaultRep' directory does not exist!\n"
                            raise Exception(msg)
                    try:
                        self.__client.info(defaultRep)
                        messageWriter("* Exporting...")
                        self.__client.export(self.__fs.join(defaultRep, ".site"), self.__fs.join(self.__basePath, ".site"), force=True)
                        self.__client.export(self.__fs.join(defaultRep, "skin"), self.__fs.join(self.__basePath, "skin"), force=True)
                        messageWriter("* Exported.")
                    except:
                        # if we can not export (because defaultRep is not a svn repository) just copy
                        #   the contents instead
                        messageWriter("* Copying...")
                        self.__fs.copy(defaultRep, self.__basePath)
                        messageWriter("* Copied.")
                    path = self.__basePath
                    if not path.endswith("/"): path += "/"
                    messageWriter("path = '%s'" % path)
                    
                    messageWriter("Adding '%s'" % (path + "skin"))
                    self.add(paths=[path + "skin"], recurse=True)
                    
                    messageWriter("Adding '%s'" %  (path + ".site"))
                    self.add(paths=[path + ".site"], recurse=True)
                    
                    messageWriter("Adding '%s'" % (path + "packages"))
                    self.__client.mkdir(url_or_path=path + "packages", log_message="Added packages directory")
                    
                    messageWriter("Updating...")
                    self.__client.checkin(path=path, log_message="Created", recurse=True)
                    ####
                messageWriter("* All done *")
                return "Created a new SVN file repository OK"
            else:
                msg = "svnURL='%s'" % (svnUrl)
                raise Exception("Not a valid SVN repository URL! %s" % msg)
    
    
    def getUrlForPath(self, path):
        result = None
        try:
            info = self.__client.info(path)
            result = info.url
        except Exception, e:
            result = None
        return result
    
    
    def isSvnUrlValid(self, svnUrl=None):
        """ NOTE: This may require a login!"""
        result = False
        if svnUrl is None:
            svnUrl = self.__svnUrl
        try:
            self.__client.ls(svnUrl, recurse=False)
            result = True
        except Exception, e:
            if str(e).find("authorization failed")>0:
                result = True
            else:
                result = False
        return result
    
    
    def setGetUsernamePasswordCallback(self, callback, retries=None):
        """ sets the callback that will be called to get the login username, password.
            this callback must take a single argument (realm, user) and 
            return a tuple(username, password, retcode)"""
        if retries!=None:
            self.__loginRetries = retries
        self.__getUsernamePasswordCallback = callback
    
    
    def isAuthenticated(self):
        self.__clearCache()
        # temp disable callback while testing
        t = int(self.iceContext.now())
        if (self.__authCache[0]+8) > t:
            return self.__authCache[1]
        #print "svn.isAuthenticated() called"        ####
        self.__authCache[0] = t
        self.__rLock.acquire()
        try:
            tmp = self.__getUsernamePasswordCallback
            self.__getUsernamePasswordCallback = None
            result = self.__checkAuthentication()
            self.__getUsernamePasswordCallback = tmp
            return result
        finally:
            self.__authCache[1] = result
            self.__rLock.release()
    
    
    def login(self, username=None, password=None, callback=None, retries=None):
        self.logout()           # logout first
        result = False
        self.__username = username
        self.__password = password
        if self.__password!=None and self.__loginRetries<1:
            self.__loginRetries = 1
        if retries!=None:
            self.__loginRetries = retries
        
        if self.__loginRetries<1:
            result = False
        else:
            if callable(callback):
                self.setGetUsernamePasswordCallback(callback)
            result = self.__checkAuthentication()
            if callable(callback):
                self.setGetUsernamePasswordCallback(None)
        return result
    
    
    def logout(self):
        """ logout of pysvn """  #Note pysvn caches auth info, so just create a new pysvn.Client object
        client = self.__createClient()
        self.__client = client
        self.__password = None
        # and reset login retries
        self.__loginRetries = 3
    
    
    def __write(self, str):
        if self.__output is not None and hasattr(self.__output, "write"):
            self.__output.write(str)
    
    
    def __createSvnFileRep(self, fileUrl):
        """ create a SVN file repository using the given file URL """
        try:
            if not fileUrl.startswith("file://"):
                raise Exception("fileUrl argument is not a valid file URL!")
            path = fileUrl[len("file://"):]
            if self.iceContext.system.isWindows:
                path = fileUrl[len("file:///"):]
            if self.__fs.exists(path):
                raise Exception("The given path already exists!")
            r, msg = self.iceContext.system.execute("svnadmin", "create", path)
            if not self.__fs.isDirectory(path):
                raise Exception("Failed to create the file repository! path=", path)
        except Exception, e:
            print "*** __createSvnFileRep(fileUrl='%s') error - '%s'" % (fileUrl, str(e))
            raise


    def __checkoutRep(self, repUrl, destPath, messageWriter=None):
        """ checkout the given repositoryURL to the destPath """
        # check out all of .ice, skin/.skin, .site, templates, .userData
        if messageWriter is None:
            messageWriter = self.iceContext.output.write
        if not self.__client.is_url(repUrl):
            raise Exception("Can not checkout the given repUrl. It is not a valid URL!", repUrl)
        try:
            ls = self.__client.ls(repUrl)
        except Exception, e:
            if str(e).find("authorization failed")>0:
                raise Exception("Can not checkout the given repUrl, not authenticated!")
            raise Exception("Can not checkout the given repUrl.  It is not a valid SVN URL", repUrl)
            
        try:
            messageWriter("Checking out the repository. Please wait...\n")
            #self.__client.checkout(url=repUrl, path=destPath, recurse=True)
            allList = [".ice/", ".site/", ".skin/", "skin/", "templates/", ".userData/"]
            self.__client.checkout(url=repUrl, path=destPath, depth=pysvn.depth.files)
            l = self.list(destPath)
            if "./" in l:
                l.remove("./")
            for i in l:
                if i in allList:
                    messageWriter("  adding '%s' (all)\n" % i)
                    self.updateAll(self.__fs.join(destPath, i))
                elif i.endswith("/"):
                    if False:
                        messageWriter("  adding '%s'\n" % i)
                        self.updateFiles(self.__fs.join(destPath, i))
                        try:
                            self.updateAll(self.__fs.join(destPath, i, ".ice"))
                        except:
                            pass
            messageWriter("Done checkout.\n")
        except Exception, e:
            msg = "Failed to checkout the repository - Error: %s\n" % str(e)
            messageWriter(msg)
            raise Exception(msg)


    def __callback_ssl_server_trust_prompt(self, trust_dict):
        """ trust all """
        realm = trust_dict["realm"]        # e.g. https://some.url.com.au:8000
        retcode = True
        accepted_failures = 3
        save = False
        return retcode, accepted_failures, save


    def __loginCallback(self, realm, user, maysave):
        #print "svn_rep.__logingCallback()"
        retcode = False
        username = ""
        password = ""
        save = False
        
        if self.__loginRetries > 0:
            if self.__password!=None:
                #print "  has password"
                username = self.__username
                password = self.__password
                #self.__password = None
                retcode = True
            if callable(self.__getUsernamePasswordCallback):
                try:
                    #print "  trying callback"
                    username, password, retcode = self.__getUsernamePasswordCallback(realm, user)
                    #print "  used callback"
                    self.__username = username
                except Exception, e:
                    raise Exception("Error in getUsernamePassword callback as set by svn_rep.setGetUsernamePasswordCallback() - ", str(e))
                    retcode = False
            if retcode==True:
                self.__loginRetries -= 1
            #print "  result='%s'" % retcode
        return retcode, username, password, save
    
    
    def __checkAuthentication(self):
        # do a simple svn operation that requires authentication to test authentication
        # Note: This will trigger the self__loginCallback() method to be called if NOT already logged in or login is not required.
        ##print "svn.__checkAuthentication()"             ####
        try:
            ls = self.__client.ls(self.__svnUrl)
            return True
        except Exception, e:
            return False
    
    @SvnErrorWrap
    def checkAuthorization(self, path):     # read check only
        try:
            url = self.__fs.join(self.__svnUrl, path)
            ls = self.__client.ls(url)
            return True
        except Exception, e:
            return False
    
    
    #-----------------------
    # private svn methods   
    #-----------------------
    

    def __addSvnIgnore(self, path, pattern):
        value = ""
        values = self.__client.propget("svn:ignore", path).values()
        if len(values)>0:
            value = values[0]
        l = value.split("\n")
        if pattern not in l:
            l.append(pattern)
            value = string.join(l, "\n")
            self.__client.propset("svn:ignore", value, path)
    
    
    def __copyFile(self, fromFile, toFile):
        self.__fs.copy(fromFile, toFile)
    
    def __clearCache(self):
        self.__cache = {}
    
    def __svnListImmediates(self, path):
        if False:
            l = self.__client.list(path, depth=pysvn.depth.immediates)
        else:
            cl = self.__cache.get("list")
            if cl is None:
                self.__cache["list"] = {}
            l = self.__cache["list"].get(path)
            if l is None:
                l = self.__client.list(path, depth=pysvn.depth.immediates)     # SLOW
                #print "list update"
                self.__cache["list"][path] = l
        return l
    
#For svn properties in V1.2
#To be used in Package copy
    def _hasProperty(self, path, name): 
        propList = self._getPropertyList(path) 
        return name in propList 
    
    def _getProperty(self, path, name):
#        from cPickle import loads
        try:
           #values = self.__client.propget("_propList_", path).values() 
           values = self.__client.propget(name, path).values()
        except:
           return None
        if len(values)>0: 
           value = values[0]
           value = self.iceContext.loads(value)
           return value 
        else: 
           return None 
       
    def _getPropertyList(self, path): 
        # this method is only needed to work around a bug with 
        # the pysvn.proplist() method
#        l = self.__client.propget("_propList_", path).values()
        l = self._getProperty(path, "_propList_")
        if l == None: 
            l = []
        return l 
    
    def _deleteAllProperties(self, path): 
        l = self._getPropertyList(path) 
        try: 
            for name in l: 
                self.__client.propdel(name, path) 
        except Exception, e: 
             raise e 
        self._setPropertyList(path, [])
        
    def _setPropertyList(self, path, propList): 
        self.setProperty(path, "_propList_", propList)  
    
    def setProperty(self, path, name, value): 
        from cPickle import dumps
        try: 
            value = dumps(value) 
            self.__client.propset(name, value, path) 
            l = self._getPropertyList(path) 
            if not (name in l) and name!="_propList_": 
                l.append(name) 
                self._setPropertyList(path, l) 
        except Exception, e: 
            raise e  




class ListItem(object):
    """
        path              filepath
        name              filename
        isFile            boolean
        isDir             boolean
        isLocked          boolean
        isVersioned       boolean 
        isIgnored         boolean
        revision          integer               or -1
        commitRevision    integer               or -1
        commitAuthor      commit author string  or None
        status            ItemStatus object     or None
        statusStr         str(status)
    """
    #
    #
    #
    def __init__(self, fs, svn_status=None, ignoreTest=None, path=None):
        """ Constructed with svn_status & ignoreTest or path & ignoreTest """
        self.__fs = fs
        if svn_status is not None:
            path = str(svn_status.path).replace("\\", "/")
        
        self.path = path
        self.name = self.__fs.split(path)[1]
        self.isFile = None
        self.isDir = None
        self.isLocked = False
        self.isVersioned = False
        self.isIgnored = True
        self.revision = None
        self.commitRevision = None
        self.commitAuthor = None
        self.status = ItemStatus.NONE
        self.revInfo = None
        
        if svn_status is not None:
            self.isLocked = bool(svn_status.is_locked)
            self.isVersioned = bool(svn_status.is_versioned)
            # STATUS
            self.status = ItemStatus.getItemStatus(svn_status.text_status)
            
            entry = svn_status.entry        
            if entry!=None:
                self.commitAuthor = str(entry.commit_author)
                self.commitRevision = entry.commit_revision.number
                self.isFile = False
                self.isDir = False
                if entry.kind==pysvn.node_kind.file:
                    self.isFile=True
                elif entry.kind==pysvn.node_kind.dir:
                    self.isDir=True
                self.revision = entry.revision.number
        if self.isFile==None:
            self.isFile = self.__fs.isFile(self.path)
        if self.isDir==None:
            self.isDir = self.__fs.isDirectory(self.path)
        if self.isDir:
            self.isIgnored = ignoreTest(self.name, isFile=False)
        elif self.isFile:
            self.isIgnored = ignoreTest(self.name, isFile=True)
        self.statusStr = str(self.status)
    
    def getCompleteStatus(self):
        result = "In sync"
        offline = ""
        outOfDate = ""
        if self.revInfo is None:
            offline = " (offline)"
        else:
            if self.revInfo.isOutOfDate:
                outOfDate = " out-of-date"
            
        if self.status==ItemStatus.Normal:
            result = offline
        else:
            result = str(self.status) + offline
        if result.startswith("Normal"):
            result = result[len("Normal"):]
        if result.startswith("Ignored"):
            result = result[len("Ignored"):]
        result += outOfDate
        if result=="":
            result = "In sync"
        return result
    
    def setStatus(self, itemStatus):
        self.status = itemStatus
        self.statusStr = str(itemStatus)
    
    def setPropModified(self):
        if self.status==ItemStatus.Normal:
            self.setStatus(ItemStatus.PropModified)
    
    def __cmp__(self, other):
        r = cmp(other.isFile, self.isFile)
        if r==0:
            r = cmp(self.name, other.name)
        return r
    
    def __str__(self):
        s = ""
        if self.isFile:
            s = " [FILE]"
        elif self.isDir:
            s = " [DIR]"
        i = ""
        if self.isIgnored:
            i = "[isIgnored], "
        s = "listItem name=%s, %sisVersioned=%s, status=%s" % (\
                self.name+s, i, self.isVersioned, str(self.status))
        return s


class ItemStatus:
    """ An enumeration object
        NONE
        Unversioned
        Normal
        Added
        Missing
        Deleted
        Replaced
        Modified
        Merged
        Conflicted
        Ignored
        Obstructed
        InComplete
        PropModified
        
        Unknown
    """
#    * none - does not exist
#    * unversioned - is not a versioned thing in this wc
#    * normal - exists, but uninteresting.
#    * added - is scheduled for addition
#    * missing - under v.c., but is missing
#    * deleted - scheduled for deletion
#    * replaced - was deleted and then re-added
#    * modified - text or props have been modified
#    * merged - local mods received repos mods
#    * conflicted - local mods received conflicting repos mods
#    * ignored - a resource marked as ignored
#    * obstructed - an unversioned resource is in the way of the versioned resource
#    * external - an unversioned path populated by an svn:external property
#    * incomplete - a directory doesn't contain a complete entries list
    #
    class __status:
        def __init__(self, state):
            self.__state = state
        def __call__(self):
            return self.__state
        def __str__(self):
            return self.__state
    NONE = __status("NONE")
    Normal = __status("Normal")
    Unversioned = __status("Unversioned")
    Added = __status("Added")
    Missing = __status("Missing")
    Deleted = __status("Deleted")
    Replaced = __status("Replaced")
    Modified = __status("Modified")
    Merged = __status("Merged")
    Conflicted = __status("Conflicted")
    Ignored = __status("Ignored")
    Obstructed = __status("Obstructed")
    InComplete = __status("InComplete")
    PropModified = __status("PropModified")
    Unknown = __status("Unknown")
    
    @staticmethod
    def getItemStatus(textStatus):
        s = None
        if textStatus==pysvn.wc_status_kind.none:
            s = ItemStatus.NONE
        elif textStatus==pysvn.wc_status_kind.normal:
            s = ItemStatus.Normal
        elif textStatus==pysvn.wc_status_kind.added:
            s = ItemStatus.Added
        elif textStatus==pysvn.wc_status_kind.deleted:
            s = ItemStatus.Deleted
        elif textStatus==pysvn.wc_status_kind.incomplete:
            s = ItemStatus.InComplete
        elif textStatus==pysvn.wc_status_kind.missing:
            s = ItemStatus.Missing
        elif textStatus==pysvn.wc_status_kind.modified:
            s = ItemStatus.Modified
        elif textStatus==pysvn.wc_status_kind.unversioned:
            s = ItemStatus.Unversioned
        elif textStatus==pysvn.wc_status_kind.ignored:
            s = ItemStatus.Ignored
        elif textStatus==pysvn.wc_status_kind.conflicted:
            s = ItemStatus.Conflicted
        elif textStatus==pysvn.wc_status_kind.merged:
            s = ItemStatus.Merged
        elif textStatus==pysvn.wc_status_kind.obstructed:
            s = ItemStatus.Obstructed
        elif textStatus==pysvn.wc_status_kind.replaced:
            s = ItemStatus.Replaced
        elif textStatus==pysvn.wc_status_kind.external:
            s = ItemStatus.Unknown
        else:
            s = ItemStatus.Unknown
        return s


    


    
    
