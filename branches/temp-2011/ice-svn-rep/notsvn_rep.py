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


class NotSvnRep:
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
        
        self.__username = None
        self.__password = None        # note optional
        self.__getUsernamePasswordCallback = None    # must return a tuple(username, password) and take a single argument (user)
        
        self.__basePath = basePath
        self.__svnUrl = svnUrl
        
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
    
    
    @property
    def svnUrl(self):
        return self.__svnUrl
    
    
    #-------------------------------------------------------------------    
    # ---  Add ---
    def add_New_Not_Working_Fine(self, paths, recurse=False):
        return None
    
    def add(self, paths, recurse=True, results=[]):
        return None
    
    # ---  Commit  ---
    #####
    def commitEmpty(self, paths, message="added"):
        """
          commit the path(s)/item(s) only does not recurse.
          for committing added directories only
          Note: should/must also add/commit the .ice and .ice/__dir__ directories as well
        """
        pass

    
    def commitAll(self, paths, message="commit", callback=None):
        """
        """
        pass

    
    def commit(self, paths, message="commit", recurse=True, actionResults=None):
        """
            commit only items that have been added or have been modified.
        """
        #    actionResults = self.iceContext.ActionResults("svn commit paths=%s %s" % \
        #        (repr(paths).strip("[]"), r))
        return self.iceContext.ActionResult("committed")

    
    # ---  Update  ---
    def updateAll(self, path, revision=None, updateResolver=None):
        pass
    
    
    def updateFiles(self, path, revision=None, updateResolver=None):
        pass
    
    
    def updateEmpty(self, path, revision=None, updateResolver=None):
        pass


    def _updateBasic(self, path):
        # Required because pysvn.update with depth=infinity argument behaves diffenetly!!!
        #  This will ('delete')/remove missing content from the working copy (only).
        pass
    
    
    def update2(self, path, recurse, revision):
        """ return (WarningMessage, ErrorMessage) ("", "") for OK """
        return "", ""

    
    
    # ---  Update  ---
    def update(self, paths, recurse=False, actionResults=None, 
            revisionNumber=None):
        # Note: do not call with a large list
        #   e.g. is a path is directory other than ./ice/item/ then should not be recursive
        return self.iceContext.ActionResult("updated")
    
    
    # ---  MakeDirectory  ---
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
    def delete(self, path):
        return True
    
    
    # ---  Copy  ---
    def copy(self, path, destinationPath):
        pass
    
    # ---  Move/Rename  ---
    def move(self, path, destinationPath):
        pass
    
    #workaround for the item status is added
    def moveSubCopy(self, path, destinationPath):
        pass
            
    
    # ---  Export  ---
    def export(self, path, destinationPath):
        """ Copy a given file or dir from the repository to another location
        (not related to the repository)
        """
        pass
    
    
    # ---  GetLogData  ---
    def getLogData(self, path, levels=None):
        # Returns a logData object or a list of logData objects levels is given
        # The logData object has the following properties:
        #    date -    (string)
        #    message - (string)
        #    author -  (string)
        #    revisionNumber - (integer)
        return []
    
    
    #
    # ---  Cleanup  ---
    def cleanup(self, path=None):
        pass
    
    
    # ---  Revert  ---
    def revert(self, path, recurse=True):
        pass
    
    
    def info(self, path, single=True):
        # uses pysvn.info2()
        # return a dictionary/object
        #   .name,  .kind,  .URL,   .last_changed_author
        #   .rev,  .last_changed_rev
        #   .wc_info  (.schedule + working file(s) names)
        return {}
        
    
    def list(self, path, update=False):
        return []
    
    
    def hasChanges(self, path):
        return False
    
    
    def getStatus(self, path, update=False, single=True):
        # uses both pysvn.status() and pysvn.list() methods
        # returns an ItemStatus2 object
        itemStatus = None
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
        listItems = []
        return listItems
    
    
    def ls(self, path):
        l = []
        return l
    
    
    def getMissing(self, path):
        return []
    
    
    def isDirModifiedAdded(self, path):
        """ recursively checks a directory for any added, modified, deleted content """
        return False
    
    
    def revInfo(self, path, includeServer=False):
        # path can be a directory or a file
        # returns an RevInfo
        return revInfo
    
    
    def getUpdateList(self, path, recurse=True):
        l = []
        return l
    
    # ---  GetRevision  ---
    def getRevision(self, path, includeUrl=False):
        return 0
    
    
    # -----------------
    




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


    


    
    
