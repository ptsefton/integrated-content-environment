#
#    Copyright (C) 2009  Distance and e-Learning Centre,
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

import types
import re
import pysvn
import time
from threading import RLock
from hashlib import md5
#from uuid import uuid4      # uuid4().hex
from cPickle import dumps, loads, HIGHEST_PROTOCOL      #dumps(obj, HIGHEST_PROTOCOL)


    #   .status(path, recurse=True, get_all=False) .status(path)
    #   .status(path, recurse=True, get_all=True, update=False, ignore=False)
    #   .info2(path, recurse=False)
    #   .ls(url),   .ls(svnUrl, recurse=False)
    #   .info(defaultRep)
    #   .cleanup(path)

    #   .add(path, recurse=False, force=False)
    #   .checkin(paths, log_message=message, recurse=recurse)
    #   .revert(item.path, recurse=False)
    #   .update(path, recurse=recurse, revision=revision)
    #   .mkdir(path, message)
    #   .remove(path, force=True)
    #   .copy(path, destinationPath, src_revision=rev)
    #   .export(path, destinationPath, force=True, revision=rev)
    #   .move(path, destinationPath, force=True)
    #   .log(path, revision_start=workingRev)
    #   .propset("svn:mime-type", "application/octet-stream", path)
    #   .propget("svn:ignore", path).values()
    #   .propset("svn:ignore", value, path)


# threadSafe method decorator
def threadSafeMethod(method):
    def threadSafeWrapper(*args, **kwargs):
        self = args[0]
        self._rLock.acquire()
        try:
            return method(*args, **kwargs)
        finally:
            self._rLock.release()
    return threadSafeWrapper

# threadSafe class decorator
def threadSafeClass(klass):
    for mName in [mName for mName in klass.__dict__.keys() \
                if not mName.startswith("__")]:
        method = klass.__dict__[mName]
        if callable(method):
            klass.__dict__[mName] = threadSafeMethod(method)
    return klass


class VCRep(object):
    # Notes:
    #   Currently does not include checking out
    #
    # Constructor:
    #   VCRep(fileSystem, basePath=None)
    # Properties:
    #   fs
    # Methods:
    #   add(path, depth=0)
    #   commit(paths, log_message)   depth=files, immediates, *empty, *infinity
    #   update(paths, depth=0 [,revision])
    #   revert(path)
    #   shelve(path)       # Shelve  # NOTE: Unsafe - this does not do any syncing or update checking first
    #   delete(path)
    #   copy(srcPath, destPath)     # Note: does not change IDs
    #   move(srcPath, destPath) ??? # copy & delete
    #   export(srcPath, destPath, includeProp=False)
    #   log(path, limit)
    #   propList(path)
    #   propGet(path, name, default=None)
    #   propSet(path, name, value)
    #   propDelete(path, name)
    #   localPropGet(path, name, default=None)
    #   localPropSet(path, name, value)
    #   localPropDelete(path, name)
    #   getStatus(path, includeServer=False)
    #   list(path, includeServer=False)         -> returns a dictionary of name:fileStatus
    #   getID(path)
    #   applyNewID(path)
    #   isVersioned(path)      
    #
    #   _absPath(path)
    #   _isVersioned(absPath)
    #   _getPropDir(absPath)
    #   _list(absPath, includeServer=False, _depth=None)
    # ----
    #   depth=infinity=1  or depth=empty=0


    @staticmethod
    def checkout(url, absPath):
        #print "checkout url='%s', absPath='%s'" % ( url, absPath )
        c = pysvn.Client()
        c.checkout(url, absPath)

    def __init__(self, fileSystem, basePath=None,
                    createGuidMethod=None,
                    ignoreFilterMethod=None,
                    shouldHavePropertiesMethod=None,
                    myChangesPrefix="MyChanges_"):
        self._rLock = RLock()
        self.__fs = fileSystem
        if basePath is None:
            basePath = fileSystem.currentWorkingDirectory
        self.__basePath = basePath
        self.__client = pysvn.Client()
        self.__myChangesPrefix = myChangesPrefix
        if createGuidMethod is None:
            idCount = [0]
            def guid():
                idCount[0] += 1
                str = "%s-%s" % (time.time(), idCount[0])
                return md5(str).hexdigest()
            createGuidMethod = guid
        self.__createGuidMethod = createGuidMethod
        if ignoreFilterMethod is None:
            def ignoreFilter(filename):
                # Note: .ice is a special case and should not be included here
                if filename.endswith(".tmp"):
                    return True
                return False        # do not ignore
            ignoreFilterMethod = ignoreFilter
        self.__ignoreFilterMethod = ignoreFilterMethod
        if shouldHavePropertiesMethod is None:
            def shouldHaveProperties(filepath):
                return True
            shouldHavePropertiesMethod = shouldHaveProperties
        self.__shouldHavePropertiesMethod = shouldHavePropertiesMethod
        #
        self.__dirUpdateStatusMap = {}  # to keep a list of known (shelved/)status/out-of-date directories etc
                                        #  and know lastChanged/current rev list
        # cache
        self.__propCacheSize = 32
        self.__propCacheList = []
        self.__propCache = {}           # absPath: metaDictObject
        #
        self.__readRepLocalData()


    @property
    def fs(self):
        return self.__fs
    
    @threadSafeMethod
    def isIgnored(self, path):
        return self.__ignoreFilterMethod(path)

    @threadSafeMethod
    def cleanup(self, path):
        absPath = self.__fs.absPath(path)
        self._cleanup(absPath)

    @threadSafeMethod
    def _cleanup(self, absPath):
        self.__client.cleanup(absPath)

    @threadSafeMethod
    def add(self, path):
        # do not add ignored items
        if self.isIgnored(path):
            return
        absPath = self.__fs.absPath(path)
        if self._isVersioned(absPath) and self.__fs.exists(absPath):
            propDir = self._getPropDir(absPath)
            if propDir is not None:
                if not self._isVersioned(propDir):
                    # add properties directory
                    self._addPropertyDirFor(absPath)
        else:
            self._add(absPath)
    
    @threadSafeMethod
    def _add(self, absPath, recurse=True):
        while True:
            try:
                self.__client.add(absPath, depth=pysvn.depth.empty, force=True)
                break
            except pysvn.ClientError, ce:
                errMsg = str(ce)
                if errMsg.find(" is not a working copy")>0:
                    parent = self.__fs.parent(absPath)
                    if parent==self.__basePath:
                        raise Exception(" can not add basePath")
                    self._add(parent, False)
                elif errMsg.find(" not found"):
                    m = re.search("'([^']+)' not found", errMsg)
                    notFoundItem = m.groups()[0]
                    raise Exception("Failed to add '%s' - not found" % notFoundItem)
                else:
                    print "  errMsg='%s'" % errMsg
                    raise
        if True:
            try:
                propDir = self._getPropDir(absPath)
                if propDir is not None:
                    self._addPropertyDirFor(absPath)
            except pysvn.ClientError, ce:
                errMsg = str(ce)
                if errMsg.find(" is not a working copy")>0:
                    m = re.search("'([^']*)' is not a working copy", errMsg)
                    if m:
                        fileItem = m.groups()[0]
                        self.revert(fileItem)
                    parent = self.__fs.parent(absPath)
                    if parent==self.__basePath:
                        print " basePath='%s'" % self.__basePath
                        print " errMsg='%s'" % errMsg
                        raise Exception(" can not add basePath")
                    self._add(parent, False)
                else:
                    raise
        if recurse:
            # ok now add all (non-ignored) children items if any
            for fileStatus in self._list(absPath).values():
                if fileStatus.isVersioned==False:
                    name = fileStatus.name
                    if name=="." or name.startswith(self.__myChangesPrefix) or \
                            self.__ignoreFilterMethod(name) or name==".ice":
                        # ignore
                        pass
                    else:
                        self._add(self.__fs.join(absPath, name), recurse)


    @threadSafeMethod
    def _addPropertyDirFor(self, absPath, tryAgain=True):
        # make sure that the propDir exists
        propDir = self._getPropDir(absPath)
        #print "_addPropertyDirFor absPath='%s', propDir='%s'" % (absPath, propDir)
        if propDir is not None:
            id = self._getID(absPath)
            parent = self.__fs.parent(propDir)
            if self._isVersioned(parent)==False:
                self._add(parent, False)
            try:
                self.__client.add(propDir, depth=pysvn.depth.empty, force=True)
                self.__client.propset("svn:ignore", "*.tmp", propDir)
                self.__client.add(propDir, depth=pysvn.depth.infinity, force=True)
            except Exception, e:
                if tryAgain==False:
                    raise
                if self.__getFromCache(absPath) is not None:
                    # remove from the cache and try again
                    self.__removeFromCache(absPath)
                    return self._addPropertyDirFor(absPath, tryAgain=False)
                raise

    
    @threadSafeMethod
    def isVersioned(self, path):
        absPath = self.__fs.absPath(path)
        return self._isVersioned(absPath)

    
    @threadSafeMethod
    def _isVersioned(self, absPath):
        try:
            statusList = self.__client.status(absPath, update=False, depth=pysvn.depth.empty)
        except:
            return False
        # statusList is a list of PysvnStatus objects.
        #  PysvnStatus -  entry (PysvnEntry), is_versioned, text_status, repos_text_status, is_locked
        if statusList==[]:
            try:
                # Check if it is a missing item
                path, name = self.__fs.split(absPath)
                sList = self.__client.list(path, depth=pysvn.depth.immediates)
                sList = [s.path for s, n in sList]
                return (absPath in sList)
            except Exception, e:
                print "-- %s --" % str(e)
                pass
            return False
        return bool(statusList[0]["is_versioned"])


    @threadSafeMethod
    def commit(self, paths, log_message=" "):
        """ Can raise a 'out-of-date - Part of commit list is out of date' exception. """
        commitRev = None
        if type(paths) is not types.ListType:
            if type(paths) in types.StringTypes:
                paths = [paths]
            else:
                raise Exception("The first argument 'paths' must by of a list type!")
        if log_message is None or log_message=="":
            log_message = " "
        absPaths = [self.__fs.absPath(path) for path in paths]
        infinityList = self.__getCommitList(absPaths)
        emptyList, iList = self.__getCommitListParents(absPaths)
        infinityList.extend(iList)
        #print "emptyList=%s, infinityList=%s" % (emptyList, infinityList)
        if emptyList!=[]:   # emptyList should be just uncommitted parents
            try:
                commitRev = self.__client.checkin(emptyList, log_message=log_message, \
                            depth=pysvn.depth.empty)
            except Exception, e:
                msg = str(e)
                if msg.find(" is out of date")>0:
                    raise Exception("out-of-date - Part of the commit list is out of date")
                else:
                    print "commit infinityList failed - '%s'" % msg
                    raise e
        if infinityList!=[]:
            try:
                commitRev = self.__client.checkin(infinityList, log_message=log_message, \
                            depth=pysvn.depth.infinity)
            except Exception, e:
                msg = str(e)
                if msg.find(" is out of date")>0:
                    raise Exception("out-of-date - Part of the commit list is out of date")
                else:
                    print "commit infinityList failed - '%s'" % msg
                    raise e
        return commitRev, emptyList, infinityList

    def __getCommitList(self, absPaths):
        s = set()
        infinityList = []
        for absPath in absPaths:
            infinityList.append(absPath)
            propDir = self._getPropDir(absPath)
            if propDir is not None:
                if propDir.endswith("/__dir__"):
                    # if we are committing a directory then commit all of the
                    #   directory files properties as well.
                    infinityList.append(self.__fs.split(propDir)[0])
                    # note: not need because it's parent is in the 'infinity' commit list anyway
                else:
                    infinityList.append(propDir)
        return infinityList

    def __getCommitListParents(self, absPaths):
        # returns an 'depth.empty' commit list and a 'depth.infinity' commit list
        if absPaths == []:
            return [], []
        parents = set()
        for absPath in absPaths:
            parent = self.__fs.parent(absPath)
            if len(parent)>len(self.__basePath):
                parents.add(parent)
        # NOTE: assuming all parents should have properties
        #    else: if self._getPropDir(absPath) is None:
        iceParents = [self.__fs.join(parent, ".ice") for parent in parents]
        iceParents = [parent for parent in iceParents \
                            if self._getStatusKind(parent)==pysvn.wc_status_kind.added]
        parents = [parent for parent in parents if self._getStatusKind(parent)==pysvn.wc_status_kind.added]
        iList = [self.__fs.join(p, "__dir__") for p in iceParents]
        emptyList, infinityList = self.__getCommitListParents(parents)
        emptyList.extend(parents)
        emptyList.extend(iceParents)
        infinityList.extend(iList)
        return emptyList, infinityList


    @threadSafeMethod
    def update(self, paths, depth=0, revision=None, callback=None):
        # callback(msg, absPath, depth [, question]) -> Yes/No to question
        #       question = "updateShelved?"
        if type(paths) is not types.ListType:
            if type(paths) in types.StringTypes:
                paths = [paths]
            else:
                raise Exception("The first argument 'paths' must by of a list type!")
        absPaths = [self.__fs.absPath(path) for path in paths]

        # does not update known 'missing' items also does not update/replace
        #   added items (if they have already been added to the repository)
        self._update(absPaths, depth, revision, callback=callback)

        if depth:       # now update known 'missing items
            addedMissingAbsPaths = []
            for absPath in absPaths:
                addedMissingAbsPaths.extend(self._listAddedMissing(absPath))
            if addedMissingAbsPaths!=[]:
                #print "  * missingAbsPaths=%s" % addedMissingAbsPaths
                self._update(addedMissingAbsPaths, depth, callback=callback)


    @threadSafeMethod
    def _update(self, absPaths, depth=0, revision=None, callback=None):
        shelvedDict = self.__getRepLocalData("shelved", {})
        pysvnDepth = pysvn.depth.empty
        if depth:
            pysvnDepth = pysvn.depth.infinity
        fs = self.__fs
        for absPath in absPaths:
            # if was previously shelved then
            relParentPath, name = fs.split(absPath[len(fs.absPath())+1:])
            shelved = shelvedDict.get(relParentPath, None)
            if shelved is not None:
                if shelved.has_key(name):
                    if callable(callback):
                        if callback("Updating", absPath=absPath, \
                                depth=depth, question="updateShelved?")!=True:
                            continue
                    # was previously shelved
                    fs.delete(absPath)
                    # remove from shelved list
                    shelved.pop(name)
                    # save changes
                    self.__saveRepLocalData()
            if callable(callback):
                try:
                    callback("Updating", absPath=absPath, depth=depth)
                except Exception, e:
                    pass
            rev = self.__client.update(absPath, depth=pysvnDepth)
            if rev[0].number==-1:     # failed to update
                continue
                #parent = fs.split(absPath)[0]
                #if self._isVersioned(parent)==False:
                #    gparent = fs.split(parent)[0]
                #    if self._isVersioned(gparent):
                #        self._update([parent, gparent])
                #        self._update([absPath], depth)
            # any conflicts?
            self.__fixupUpdateConflicts(absPath, pysvnDepth)
            if True: 
                propPath = self._getPropDir(absPath)
                if propPath is not None:
                    if propPath.endswith("/__dir__"):
                        pPath = self.__fs.split(propPath)[0]
                        self.__client.update(pPath, depth=pysvn.depth.empty)
                        self.__fixupUpdateConflicts(pPath, pysvn.depth.infinity)
                    self.__client.update(propPath, depth=pysvn.depth.infinity)
                    # any conflicts?
                    self.__fixupUpdateConflicts(propPath, pysvn.depth.infinity)
        # clear the cache
        self.__clearCache()

    def __fixupUpdateConflicts(self, absPath, pysvnDepth):
        fs = self.__fs
        statuses = self.__client.status(absPath, depth=pysvnDepth)
        added = [s for s in statuses if s.text_status==pysvn.wc_status_kind.added]
        statuses = [status for status in statuses \
                        if status.text_status==pysvn.wc_status_kind.conflicted]
        for s in statuses:
            cItem = s.path
            path, name = fs.split(cItem)
            if cItem.find("/.ice/")==-1:
                fs.move(fs.join(path, s.entry.conflict_work),
                        fs.join(path, self.__myChangesPrefix + name))
            self.__client.revert(cItem, depth=pysvn.depth.empty)
            self.__client.resolved(cItem, depth=pysvn.depth.empty)
        if False: ################################ ?????????????????
            # Only top most level items
            addedPaths = [s.path for s in added]
            addedPaths.sort()
            for p in addedPaths:
                added = [s for s in added if not (s.path.startswith(p) and s.path!=p)]
            for s in added:
                if s.path.endswith("/.ice") or s.path.find("/.ice/")!=-1:
                    self.__client.remove(s.path, force=True)
                    self.__client.update(s.path, depth=pysvn.depth.infinity)
                    print "-- %s" % s.path
                else:
                    path, name = fs.split(s.path)
                    fs.move(s.path, fs.join(path, self.__myChangesPrefix + name))
                    self.__client.update(s.path, depth=pysvn.depth.infinity)

    @threadSafeMethod
    def revert(self, path):
        absPath = self.__fs.absPath(path)
        paths = [absPath]
        propDir = self._getPropDir(absPath)
        if propDir is not None:
            paths.append(propDir)
            self.__removeFromCache(absPath)
        self.__client.revert(paths, depth=pysvn.depth.infinity)


    @threadSafeMethod
    def shelve(self, path):
        # Note: can only remove a directory and that is under version control
        absPath = self.__fs.absPath(path)
        if self.__fs.isDirectory(absPath):
            self.__fs.delete(absPath)
            self.__client.update(absPath, depth=pysvn.depth.empty)
            # add to shelved list
            shelved = self.__getRepLocalData("shelved", {})
            relPath = absPath[len(self.__fs.absPath())+1:]
            relParentPath, name = self.__fs.split(relPath)
            d = shelved.get(relParentPath, {})
            d[name] = True
            shelved[relParentPath] = d
            self.__setRepLocalData("shelved", shelved)
            #
            return True
        return False


    @threadSafeMethod
    def delete(self, path):
        absPath = self.__fs.absPath(path)
        self.__client.remove(absPath, force=True)
        #############
        # Properties as well
        #############
        propDir = self._getPropDir(absPath)
        if propDir is not None:
            self.__client.remove(propDir, force=True)


    @threadSafeMethod
    def copy(self, srcPath, destPath):     # Note: does not change IDs
        fs = self.__fs
        destParentPath = fs.split(destPath)[0]
        if not self.__fs.exists(destParentPath):
            self.__fs.makeDirectory(destParentPath)
            self.add(destParentPath)
        try:
            self.__client.copy(srcPath, destPath)
            srcPropPath = self._getPropDir(srcPath)
            destPropPath = self._getPropDir(destPath)
            if destPropPath.endswith("/.ice/__dir__"):
                return
            if srcPropPath is not None and destPropPath is not None:
                self.__client.copy(srcPropPath, destPropPath)
        except Exception, e:
            raise


    #def move(self, srcPath, destPath):  # ??? # copy & delete
    #    pass


    @threadSafeMethod
    def export(self, srcPath, destPath, includeProps=False):
        fs = self.__fs
        absSrcPath = fs.absPath(srcPath)
        absDestPath = fs.absPath(destPath)
        l = len(absSrcPath) + 1
        def func(path, dirs, files):
            if dirs.count(".svn"):
                dirs.remove(".svn")
            if includeProps==False and dirs.count(".ice"):
                dirs.remove(".ice")
            destPath = fs.join(absDestPath, path[l:])
            fs.makeDirectory(destPath)
            for file in files:
                src = fs.join(path, file)
                dest = fs.join(destPath, file)
                fs.copy(src, dest)
        self.__fs.walker(absSrcPath, func)


    @threadSafeMethod
    def log(self, path, limit):
        """ returns a list of tuples of (author, dateTimeInt, logMessage) """
        absPath = self.__fs.absPath(path)
        try:
            logMessages = self.__client.log(absPath, limit=limit)
            logMessages = [(log.author, int(log.date), log.message, log.revision.number) \
                            for log in logMessages]
        except:
            logMessages = []
        return logMessages


    @threadSafeMethod
    def propList(self, path):
        absPath = self.__fs.absPath(path)
        metaDict = self._getMetaDictObject(absPath)
        return metaDict.keys()


    @threadSafeMethod
    def propGet(self, path, name, default=None):
        absPath = self.__fs.absPath(path)
        #
        if name.startswith("rendition.") or name.startswith("image-") or \
                name=="tags" or name.startswith("inline-annotations"):
            if name.startswith("inline-annotations"):
                if name=="inline-annotations":
                    # return a dict of all annotations
                    pPath = self.__fs.join(self._getPropDir(absPath), "inline-annotations")
                    d = {}
                    for file in self.__fs.listFiles(pPath):
                        data = self.__fs.read(self.__fs.join(pPath, file))
                        d[file]=data
                    return d
                else:
                    name = name[len("inline-annotations/"):]
                    pPath = self.__fs.join(self._getPropDir(absPath), "inline-annotations", name)
            else:
                pPath = self.__fs.join(self._getPropDir(absPath), name)
            try:
                data = self.__fs.read(pPath)
                return data
            except Exception, e:
                raise e
        else:
            pass
        #
        metaDict = self._getMetaDictObject(absPath)
        return metaDict.get(name, default)


    @threadSafeMethod
    def propSet(self, path, name, value):
        absPath = self.__fs.absPath(path)
        #
        try:
            if name.startswith("rendition.") or name.startswith("image-") or \
                    name=="tags" or name.startswith("inline-annotations"):
                if name.startswith("inline-annotations"):
                    pPath = self.__fs.join(self._getPropDir(absPath),
                            "inline-annotations", name[len("inline-annotations/"):])
                else:
                    pPath = self._getPropDir(absPath)
                    if pPath is None:
                        raise Exception("Failed to get prop directory for '%s'" % path)
                    pPath = self.__fs.join(pPath, name)
                self.__fs.write(pPath, value)
                if not self._isVersioned(pPath):
                    try:
                        self.__client.add(pPath, depth=pysvn.depth.empty, force=True)
                    except:
                        self._getID(absPath)
                        if name.startswith("inline-annotations"):
                            self.__client.add(self.__fs.parent(pPath),
                                    depth=pysvn.depth.empty, force=True)
                        self.__client.add(pPath, depth=pysvn.depth.empty, force=True)
            else:
                metaDict = self._getMetaDictObject(absPath)
                metaDict[name] = value
                self._saveMetaDictObject(absPath, metaDict)
        except Exception, e:
            if self.__fs.exists(absPath)==False:
                raise Exception("Can not set a property on an item does not exist!")
            else:
                raise

    @threadSafeMethod
    def propDelete(self, path, name):
        absPath = self.__fs.absPath(path)
        if name.startswith("image-") or name.startswith("rendition.") \
                or name=="tags" or name.startswith("inline-annotations"):
            if name.startswith("inline-annotations"):
                name = name[len("inline-annotations/"):]
                pPath = self.__fs.join(self._getPropDir(absPath), "inline-annotations", name)
            else:
                pPath = self.__fs.join(self._getPropDir(absPath), name)
            try:
                self.__client.remove(pPath, force=True)
                return True
            except Exception, e:
                raise e
        else:
            metaDict = self._getMetaDictObject(absPath)
            if metaDict.has_key(name):
                del metaDict[name]
                self._saveMetaDictObject(absPath, metaDict)
                return True
        return False


    @threadSafeMethod
    def localPropGet(self, path, name, default=None):
        if name!="lastModified":
            return default
        absPath = self.__fs.absPath(path)
        propDir = self._getPropDir(absPath)
        filename = self.__fs.join(propDir, "_lastModified.tmp")
        data = self.__fs.readFile(filename)
        if data is None:
            return default
        else:
            return loads(data)

    
    @threadSafeMethod
    def localPropSet(self, path, name, value):
        if name!="lastModified":
            raise Exception("unsupported (currently) local prop name!")
        absPath = self.__fs.absPath(path)
        propDir = self._getPropDir(absPath)
        filename = self.__fs.join(propDir, "_lastModified.tmp")
        data = dumps(value, HIGHEST_PROTOCOL)
        self.__fs.writeFile(filename, data)


    @threadSafeMethod
    def localPropDelete(self, path, name):
        if name!="lastModified":
            return False
        absPath = self.__fs.absPath(path)
        propDir = self._getPropDir(absPath)
        filename = self.__fs.join(propDir, "_lastModified.tmp")
        self.__fs.delete(filename)
    

    @threadSafeMethod
    def getStatus(self, path, includeServer=False):
        absPath = self.__fs.absPath(path)
        return self._getStatus(absPath, includeServer)


    @threadSafeMethod
    def list(self, path, includeServer=False):
        absPath = self.__fs.absPath(path)
        return self._list(absPath, includeServer)


    @threadSafeMethod
    def getID(self, path):
        absPath = self.__fs.absPath(path)
        return self._getID(absPath)

    @threadSafeMethod
    def _getID(self, absPath):
        metaDict = self._getMetaDictObject(absPath)
        return metaDict.get("_guid")


    @threadSafeMethod
    def applyNewID(self, path):
        absPath = self.__fs.absPath(path)
        metaDict = self._getMetaDictObject(absPath)
        metaDict["_guid"] = self.__createGuidMethod()
        # save changes
        self._saveMetaDictObject(absPath, metaDict)
        return metaDict.get("_guid")


    @threadSafeMethod
    def _absPath(self, path):
        return self.__fs.absPath(path)


    @threadSafeMethod
    def _isVersionable(self, absPath):
        path, name = self.__fs.split(absPath)
        if self.__ignoreFilterMethod(name) or name==".ice":
            return False
        return (self.__shouldHavePropertiesMethod(absPath) and absPath.find("/.ice/")==-1)
    
    @threadSafeMethod
    def _getPropDir(self, absPath):
        propDir = None
        if self._isVersionable(absPath):
            if self.__fs.isFile(absPath):
                parent, name = self.__fs.split(absPath)
                propDir = self.__fs.join(parent, ".ice", name)
            elif self.__fs.isDirectory(absPath):
                propDir = self.__fs.join(absPath, ".ice/__dir__")
            else: # does not exist
                propDir = None
        return propDir


    @threadSafeMethod
    def _saveMetaDictObject(self, absPath, metaDict):
        propPath = self._getPropDir(absPath)
        if propPath is None:
            return
        data = dumps(metaDict, HIGHEST_PROTOCOL)
        self.__fs.writeFile(self.__fs.join(propPath, "meta"), data)


    @threadSafeMethod
    def _getMetaDictObject(self, absPath):
        metaDict = self.__getFromCache(absPath)
        if metaDict is None:
            propPath = self._getPropDir(absPath)
            if propPath is None:
                return {}
            try:
                metaData = self.__fs.readFile(self.__fs.join(propPath, "meta"))
                metaDict = loads(metaData)
            except:
                if not self._isVersioned(absPath):          # DO NOT automatically add unversioned items
                    return {}                               ####
                metaDict = {"_guid":self.__createGuidMethod()}
                # save
                self._saveMetaDictObject(absPath, metaDict)
                # add to svn if not versioned
                if not self._isVersioned(absPath):
                    self._add(absPath)
                if not self._isVersioned(propPath):
                    self._addPropertyDirFor(absPath)
            # add to cache
            self.__addToCache(absPath, metaDict)
        else:
            # update cache
            self.__updateCache(absPath)
        return metaDict


    def __getFromCache(self, absPath):
        return self.__propCache.get(absPath, None)

    def __addToCache(self, absPath, metaDict):
        self.__propCache[absPath] = metaDict
        if self.__propCacheList.count(absPath)==0:
            self.__propCacheList.insert(0, absPath)
        while len(self.__propCacheList)>self.__propCacheSize:
            self.__removeFromCache(self.__propCacheList[-1])

    def __removeFromCache(self, absPath):
        if self.__propCacheList.count(absPath):
            self.__propCacheList.remove(absPath)
        v = self.__propCache.pop(absPath)

    def __updateCache(self, absPath):
        try:
            self.__propCacheList.remove(absPath)
            self.__propCacheList.insert(0, absPath)
        except: pass

    def __clearCache(self):
        self.__propCacheList = []
        self.__propCache.clear()

    @threadSafeMethod
    def _getStatus(self, absPath, includeServer=False):
        depth = pysvn.depth.empty
        if self.__fs.isFile(absPath):
            depth = pysvn.depth.immediates
        ilist = self._list(absPath, includeServer, depth).values()
        if ilist==[]:
            try:
                path, name = self.__fs.split(absPath)
                dlist = self._list(path, includeServer, pysvn.depth.immediates)
                return dlist.get(name)
            except Exception, e:
                pass
            return None
        return ilist[0]

    @threadSafeMethod
    def _getStatusKind(self, absPath):
        status = None
        try:
            status = self.__client.status(absPath, update=False, depth=pysvn.depth.empty)[0]
        except:
            pass
        if status is None:
            return pysvn.wc_status_kind.unversioned
        else:
            return status.text_status

    @threadSafeMethod
    def _getStatusStr(self, path):
        absPath = self.__fs.absPath(path)
        statusKind = self._getStatusKind(absPath)
        return str(statusKind)
    
    @threadSafeMethod
    def _list(self, absPath, includeServer=False, _depth=None):
        """ returns a dict of VCRepFileStatus """
        assert1 = False
        if _depth is None:
            _depth = pysvn.depth.immediates
        name = None
        shelved = self.__getRepLocalData("shelved", {})
        relPath = absPath[len(self.__fs.absPath())+1:]
        shelved = shelved.get(relPath, {})
        statusDict = {}
        if includeServer:
            self.__getServersLastChangeRevNum(absPath)
        try:
            statusList = self.__client.status(absPath, update=includeServer, depth=_depth)
        except Exception, e:
            msg = str(e)
            if msg.find(" is not a working copy")!=-1:
                statusList = []
            else:
                raise e
        # statusList is a list of PysvnStatus objects.
        #  PysvnStatus
        #   entry (PysvnEntry), is_versioned, text_status, repos_text_status, is_locked
        #  PysvnEntry
        #   commit_revision, is_absent, is_deleted, [is_valid], kind, name, revision, [uuid]
        #    [conflict_new, conflict_old, conflict_work]
        for pysvnStatus in statusList:
            isVersioned = bool(pysvnStatus.get("is_versioned"))
            textStatus = pysvnStatus.get("text_status")
            isOutOfDate = None
            #repTextStatus = pysvnStatus.get("repos_text_status")    # note: may be None
            #if repTextStatus is not None:
            #    repTextStatus = str(repTextStatus)
            #    if repTextStatus!="none":
            #        isOutOfDate = (repTextStatus!="normal")
            if includeServer:
                isOutOfDate = self.__getIsOutOfDate(absPath)
            isLocked = pysvnStatus.get("is_locked")
            entry = pysvnStatus.get("entry")
            if entry is None:
                isAbsent = False
                isDeleted = False
                isDir = False
                name = self.__fs.split(pysvnStatus.path)[-1]
                if len(statusList)==1:
                    name = "."
                    assert1 = True
                #print "no entry '%s'  %s %s" % (name, isVersioned, textStatus)
                commitRev = None
                rev = None
            else:
                isAbsent = entry.get("is_absent")
                isDeleted = entry.get("is_deleted")
                isDir = entry.get("kind")==pysvn.node_kind.dir
                name = entry.get("name")  # This is getting the wrong name?
                name = pysvnStatus.path[len(absPath):].strip("/")
                if name=="":
                    name = "."
                commitRev = entry.get("commit_revision")
                if commitRev is not None:
                    commitRev = commitRev.number
                rev = entry.get("revision")
                if rev is not None:
                    rev = rev.number
            status = str(textStatus)
            if status=="none":
                status = "missing"
            elif status=="normal" and shelved.has_key(name):
                #print "%s has been shelved" % name
                status = "shelved"
            fileStatus = VCRepFileStatus(name, isDir, isVersioned, status,
                            rev, lastChangedRev=None, commitRev=commitRev,
                            isOutOfDate=isOutOfDate)
            statusDict[name] = fileStatus
        
        ## Revision Number checking/testing
        d = self.__dictLastChangedRevNum(absPath, _depth)
        for path, lastRev in d.iteritems():
            s = statusDict.get(path)
            if s is not None:
                s.setLastChangedRevNum(lastRev)

        # check the .ice properties for changes as well
        mList = (pysvn.wc_status_kind.added, pysvn.wc_status_kind.modified, pysvn.wc_status_kind.deleted)
        absPropPath = self._getPropDir(absPath)
        if absPropPath is not None:
            if absPropPath.endswith("/__dir__"):
                if _depth==pysvn.depth.immediates:
                    absPropPath = absPropPath[:-len("/__dir__")]
                    d = self.__dictLastChangedRevNum(absPropPath, _depth)
                    for path, lastRev in d.iteritems():
                        s = statusDict.get(path)
                        if s is not None:
                            if lastRev > s.lastChangedRevNum:
                                s.setLastChangedRevNum(lastRev)
                    try:
                        statusList = self.__client.status(absPropPath, update=False, \
                                        depth=pysvn.depth.infinity)
                    except:
                        statusList = []
                    statusList = [s for s in statusList if s.text_status in mList]
                    for s in statusList:
                        # name = the part after /.ice/
                        if not s.path.endswith("/.ice"):
                            name = s.path.split("/.ice/")[1].split("/")[0]
                            vcStatus = statusDict.get(name)
                            if vcStatus is not None:
                                vcStatus.setPropModified()
                else:
                    # Just get the statusList for this directory
                    statusList = self.__client.status(absPropPath, update=False, \
                                    depth=pysvn.depth.infinity)
                    statusList = [s for s in statusList if s.text_status in mList]
                    if len(statusDict)==1:
                        if statusList!=[]:
                            statusDict.values()[0].setPropModified()
                    else:
                        print " expected statusDict size to be 1 but was %" % len(statusDict)
            else:
                # Just get the statusList for this 'file' item
                if len(statusDict)==1:
                    statusList = self.__client.status(absPropPath, update=False, \
                                            depth=pysvn.depth.infinity)
                    statusList = [s for s in statusList if s.text_status in mList]
                    if statusList!=[]:
                        statusDict.values()[0].setPropModified()
                    if includeServer:
                        isOutOfDate = self.__getIsOutOfDate(absPropPath)
                        if isOutOfDate:
                            statusDict.values()[0].setIsOutOfDate()
                else:
                    if self.fs.isFile(absPath):     # fakeSkin
                        isDir = False
                        isVersioned = False
                        status = "unversioned"
                        rev = -1
                        name = self.fs.split(absPath)[-1]
                        fileStatus = VCRepFileStatus(name, isDir, isVersioned, status,
                                    rev, lastChangedRev=None, commitRev=-1, isOutOfDate=False)
                        statusDict[name] = fileStatus
                        assert1 = True
                    else:
                        print " expected statusDict size to be 1 but was %s" % len(statusDict)
                        print "  for absPath '%s'" % absPath
        #
        # Find 'missing' items
        try:
            self.__client = pysvn.Client()
            sList = self.__client.list(absPath, depth=_depth)
            for iList, lockInfo in sList:
                # .kind, path (=/name), [size, last_author, create_rev, has_props, repos_path]
                name = iList.path
                if name==absPath:
                    name = "."
                else:
                    name = self.__fs.split(name)[-1]
                s = statusDict.get(name)
                if not statusDict.has_key(name):
                    isDir = iList.kind==pysvn.node_kind.dir
                    fileStatus = VCRepFileStatus(name=name, isDir=isDir,
                                    isVersioned=True, statusStr="missing", rev=-1)
                    statusDict[name] = fileStatus
        except Exception, e:
            msg = str(e)
            if msg.find(" is not a working copy")!=-1:
                pass
            elif msg.find(" has no URL")!=-1:
                # Missing
                pass
            elif msg.startswith("Unable to find repository location for"):
                # ? Why is svn giving this error message?
                # It does exist and other svn commands do not have a problem with it.
                pass
            elif (not msg.startswith("URL ")) and (msg.find(" is not under version control")==-1):
                print "Error - in _list() list section '%s'" % msg

        # Add unversioned items
        if len(statusDict)==0:
            dirs, files = self.__fs.listDirsFiles(absPath)
            for dir in dirs:
                fileStatus = VCRepFileStatus(dir, True, False, "unversioned",
                        -1, lastChangedRev=None, commitRev=-1)
                statusDict[dir] = fileStatus
            for file in files:
                fileStatus = VCRepFileStatus(file, False, False, "unversioned",
                        -1, lastChangedRev=None, commitRev=-1)
                statusDict[file] = fileStatus
        elif len(statusDict)==1:
            s = statusDict.values()[0]
            if not s.isVersioned:
                if assert1==False:
                    print "vc_rep._list assertion assert1 failed!"
                    print "  %s" % absPath
                dirs, files = self.__fs.listDirsFiles(absPath)
                for dir in dirs:
                    fileStatus = VCRepFileStatus(dir, True, False, "unversioned",
                            -1, lastChangedRev=None, commitRev=-1)
                    statusDict[dir] = fileStatus
                for file in files:
                    fileStatus = VCRepFileStatus(file, False, False, "unversioned",
                            -1, lastChangedRev=None, commitRev=-1)
                    statusDict[file] = fileStatus

        # Apply filter  - should this be done here or in def list() ??
        if False:
            if self.__ignoreFilterMethod(name) or name==".ice":
                pass
            else:
                pass
        return statusDict

    def __getIsOutOfDate(self, absPath):
        try:
            lastChangedRevNum, serverLastChangedRevNum = self.__getServersLastChangeRevNum(absPath)
            return serverLastChangedRevNum > lastChangedRevNum
        except:
            return None

    def __getServersLastChangeRevNum(self, absPath):
        try:
            info = self.__client.info2(absPath)[0][1]
            lastChangedRevNum = info.last_changed_rev.number
            sInfo = self.__client.info2(info.URL)[0][1]
            serverLastChangedRevNum = sInfo.last_changed_rev.number
            return lastChangedRevNum, serverLastChangedRevNum
        except Exception, e:
            msg = str(e) 
            if msg.find(" non-existent in revision ")!=-1:
                return -1,-1
            elif msg.find(" is not under version control")!=-1:
                return -1,-1
            print "Warning: received the following error while trying to get server info. '%s'" % msg
            raise

    def __dictLastChangedRevNum(self, absPath, depth):
        d = {}
        try:
            entryList = self.__client.info2(absPath, depth=depth)
            #entryList is a list of tuple of pathName and infoDict
            #  infoDict
            #   rev, kind, last_change_rev, [wc_info]
            for pathName, infoDict in entryList:
                path = pathName[len(absPath):].strip("/")
                if path=="":
                    path = "."
                lastChangedRevNum = infoDict.last_changed_rev.number
                d[path] = lastChangedRevNum
        except Exception, e:
            msg = str(e)
            if msg.find(" is not a working copy")!=-1 or \
                msg.find(" is not under version control")!=-1 or \
                msg.find(" is missing")!=-1:
                pass
            else:
                print " __dictLastChangedRevNum svn.info2 error - '%s'" % msg
                raise e
        return d


    @threadSafeMethod
    def _listAddedMissing(self, absPath, recurse=True):
        depth = pysvn.depth.infinity
        if recurse==False:
            depth = pysvn.depth.immediates
        statusList = self.__client.status(absPath, depth=depth)
        paths = [status.path for status in statusList if status.get("text_status") in \
                (pysvn.wc_status_kind.added, pysvn.wc_status_kind.missing) and \
                status.path.find("/.ice")==-1]
        s = set([s.path for s in statusList])
        try:
            sList = self.__client.list(absPath, depth=depth)
            for iList, lockInfo in sList:
                name = iList.path
                if name==absPath or name.find("/.ice")>-1:
                    pass
                else:
                    if name not in s:
                        paths.append(name)
        except Exception, e:
            pass
        return paths


    def __getDirTree(self):
        # dictionary of all directory (relative) paths with "" being the root.
        # directory object
        #    current revision number, shelved children, shelved(self), known missing children
        #
        return self.__getRepLocalData("dirTree", {})

    def __saveDirTree(self):
        self.__saveRepLocalData()

    def __getRepLocalData(self, name, default=None):
        o = self.__repLocalData.get(name)
        if o is None and default is not None:
            o = default
            self.__setRepLocalData(name, default)
        return o

    def __setRepLocalData(self, name, data):
        self.__repLocalData[name] = data
        self.__saveRepLocalData()

    def __readRepLocalData(self):
        data = None
        self.__repLocalData = {}
        p = self.__getRepLocalDataPath()
        if p is not None:
            data = self.__fs.read(p)
        if data is not None:
            try:
                self.__repLocalData = loads(data)
            except:
                pass
        return self.__repLocalData


    def __saveRepLocalData(self):
        data = dumps(self.__repLocalData, HIGHEST_PROTOCOL)
        p = self.__getRepLocalDataPath()
        self.__fs.write(p, data)


    def __getRepLocalDataPath(self):
        propPath = self._getPropDir(self.__fs.absPath())
        if propPath is None:
            return None
        if not self.__fs.isDirectory(propPath):
            self.getID(".")
        p = self.__fs.join(propPath, "repData.tmp")
        return p


    @threadSafeMethod
    def getAnnotationDirAccess(self, path):
        obj = None
        absPath = self.__fs.absPath(path)
        propPath = self._getPropDir(absPath)
        if propPath is not None:
            aPath = self.__fs.join(propPath, "inline-annotations")
            obj = self.__getDirOnlyAccessObject(aPath)
        return obj


    def __getDirOnlyAccessObject(self, absPath):
        svnClient = self.__client
        fs = self.__fs.clone(absPath)
        class DirOnlyAccess(object):
            # writeFile(), readFile(), exists() (isDirectory), listFiles(), path
            def writeFile(self, filename, data):
                fs.writeFile(filename, data)
                try:
                    svnClient.add(fs.absPath(filename), depth=pysvn.depth.empty, force=True)
                except pysvn.ClientError, ce:
                    msg = str(ce)
                    if msg.find(" is not a working copy")!=-1:
                        svnClient.add(fs.absPath(), depth=pysvn.depth.empty, force=True)
                        svnClient.add(fs.absPath(filename), depth=pysvn.depth.empty, force=True)
            def readFile(self, filename):
                return fs.readFile(filename)
            def deleteFile(self, filename):
                svnClient.remove(fs.absPath(filename), force=True)
            def exists(self):
                return fs.isDirectory()
            def listFiles(self):
                return fs.listFiles()
            def __str__(self):
                return "[DirOnlyAccess Object] absPath='%s'" % fs.absPath()
        dirOnlyAccess = DirOnlyAccess()
        return dirOnlyAccess


    @threadSafeMethod
    def flush(self, path):
        absPath = self.__fs.absPath(path)
        # flush any cached data for this path


class DirectoryNode(object):
    @staticmethod
    def treeBuilder(self, vcRep):
        pass

    
    def __init__(self, name=""):
        self.name = name                    # "" for root
        self.children = {}
        self.currentRevisionNumber = -1
        self.isUptoDate = False
        self.shelved = False                # self is shelved or not
        self.shelvedChildren = []           # list of names
        self.missingChildren = []           # list of names
        self.addedChildren = []             # list of names


    def addChild(self, dirNode):
        self.children[dirNode.name] = dirNode

    def removeChild(self, name):
        if self.children.has_key(name):
            return self.children.pop(name)

    def getAllAddedChildren(self):
        l = list(self.addedChildren)
        for child in self.children.values():
            l.extend(["%s/%s" % (self.name, n) for n in child.getAllAddedChildren()])
        return l

    def getAllMissingChildren(self):
        l = list(self.missingChildren)
        for child in self.children.values():
            l.extend(["%s/%s" % (self.name, n) for n in child.getAllMissingChildren()])
        return l



###############################################################################
###############################################################################

class VCRepFileStatus(object):
    def __init__(self, name, isDir, isVersioned, statusStr, rev,
                lastChangedRev=None, commitRev=None, isOutOfDate=False):
        self.__name = name
        self.__statusStr = statusStr
        self.__isVersioned = isVersioned
        self.__isDir = isDir
        self.__rev = rev
        self.__lastChangedRev = lastChangedRev
        self.__commitRev = commitRev
        self.__isOutOfDate = isOutOfDate

    @property
    def name(self):
        return self.__name
    
    @property
    def isDir(self):
        return self.__isDir
    @property
    def isDirectory(self):
        return self.__isDir

    @property
    def isFile(self):
        return not self.__isDir

    @property
    def status(self):
        return self.__statusStr

    @property
    def isVersioned(self):
        return self.__isVersioned

    @property
    def isDeleted(self):
        return self.__statusStr=="deleted"

    @property
    def isMissing(self):
        return self.__statusStr=="missing"

    @property
    def revNum(self):
        return self.__rev

    @property
    def lastChangedRevNum(self):
        return self.__lastChangedRev

    @property
    def commitRevNum(self):
        return self.__commitRev

    @property
    def isOutOfDate(self):
        return self.__isOutOfDate

    def setLastChangedRevNum(self, num):
        self.__lastChangedRev = num

    def setPropModified(self):
        if self.__statusStr=="normal":
            self.__statusStr = "modified"

    def setIsOutOfDate(self):
        self.__isOutOfDate = True

    def __str__(self):
        s = "[FileStatus] name='%s', isDir=%s, status='%s'"
        s = s % (self.__name, self.__isDir, self.__statusStr)
        if self.__isOutOfDate:
            s += ", isOutOfDate"
        return s

    def __cmp__(self, other):
        if self.__isDir != other.__isDir:
            return cmp(other.__isDir, self.__isDir)
        return cmp(self.name, other.name)










