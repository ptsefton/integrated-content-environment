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

import os.path
import time


class RepositoryIndexer(object):
    # Constructor:
    #   __init__(iceContext, indexRelBasePath)
    # Properties:
    ##   indexerRelBasePath
    ##   indexerAbsBasePath
    # Methods:
    #   reIndex(relPath="/", metaOnly=False)
    #   deleteIndex(id)
    #   getPathForId(id)
    #   search(queryStr, tags=[], fileName=None, path=None) -> returns a list of
    #   
    def __init__(self, iceContext, indexRelBasePath):
        self.iceContext = iceContext
        self.__rep = iceContext.rep
        self.__indexRelBasePath = indexRelBasePath
        self.__fs = iceContext.fs
        self.__indexAbsBasePath = self.__rep.getAbsPath(indexRelBasePath)
        self.__flagFile = None
        
        self.__contentIndexer = None
        self.__metaIndexer = None
        self.__contentIndexerAbsPath = self.__fs.join(self.__indexAbsBasePath, \
                                    "contentIndex")
        self.__metaIndexerAbsPath = self.__fs.join(self.__indexAbsBasePath, \
                                    "metaIndex")
        self.__indexerPlugin = self.iceContext.getPlugin("ice.indexer")
        if self.__indexerPlugin is None:
            raise self.iceContext.IceException("Error no ice.indexer plugin found!")
        try:
            self.__setup(self.__fs)
        except Exception, e:
            msg = "Error setting up indexes (in RepositoryIndexer.__setup()) - '%s'" % str(e)
            raise self.iceContext.IceException(msg)
        ##doNotIndexDirectories
    
    
##    @property
##    def indexerRelBasePath(self):
##        return self.__indexRelBasePath
##    
##    @property
##    def indexerAbsBasePath(self):
##        return self.__indexAbsBasePath
    
    
    def __setup(self, fs):
        # setup indexes
        self.__flagFile = fs.join(self.__indexRelBasePath, "reIndex")
        flagFileItem = self.__rep.getItem(self.__flagFile)
        item = self.__rep.getItem(self.__indexRelBasePath)
        if not item.isDir:
            item.makeDirectory(ignore=True)
            flagFileItem.write("If this file exists then a complete reindex is required\n")
        Indexer = self.__indexerPlugin.pluginClass
        if Indexer is None:
            raise Exception("Failed to get indexer plugin!")
        try:
            self.__contentIndexer = Indexer(fs, self.__contentIndexerAbsPath)
        except Exception, e:
            print str(e)
            raise
        
        #keywordAnalyzer = Indexer.KeywordAnalyzer()
        #self.__metaIndexer = Indexer(fs, self.__metaIndexerAbsPath, keywordAnalyzer)
        self.__metaIndexer = Indexer(fs, self.__metaIndexerAbsPath, 
                                        analyzerName="KeywordAnalyzer")
    
    
    def reIndex(self, item, metaOnly=False):
        # Todo: Handle errors
        # Todo: Also index html and text files
        if item.isFile:
            self.__reindex(item, metaOnly)
        else:
            ###
            doNotIndexDirectories = list(self.__rep.doNotIndexDirectories)
            #doNotIndexDirectories.append(self.__relativeExportPath)
            #doNotIndexDirectories.append(self.__documentTemplatesPath)
            for listItems in item.walk():
                for i in list(listItems):
                    if i.isDirectory:
                        if i.name in doNotIndexDirectories:
                            listItems.remove(i)
                            continue
                    self.__reindex(i, metaOnly)
        self.__contentIndexer.optimize()
        self.__metaIndexer.optimize()
        if item.relPath=="/":
            try:
                flagFileItem = self.__rep.getItem(self.__flagFile)
                flagFileItem.delete()
            except:
                pass
    
    
    def deleteIndex(self, id):
        if id is None:
            return
        if self.__contentIndexer is not None:
            self.__contentIndexer.deleteIndex(id)
        if self.__metaIndexer is not None:
            self.__metaIndexer.deleteIndex(id)
    
    
    def getPathForId(self, id):
        searchResults = self.__metaIndexer.searchId(id)
        return searchResults.value.get("path")
    
    def searchKeyword(self, query):
        searchResults = []
        metaResults = self.__metaIndexer.search(keywordQueryStr=query)
        for doc in metaResults.values():
            searchResults.append(doc.get("id"))
        return searchResults
    
    def search(self, queryStr, tags=[], fileName=None, path=None):
        found = []
        ## Test if a reIndex is required
        #absPath = self.__getAbsPath(".indexes")
        #flag = self.__fs.join(absPath, ".reindex")
        #if self.__fs.exists(flag):
        #    self.reIndex()
        #    self.__fs.delete(flag)
        try:
            if path is not None:
                if path.endswith("/"):
                    path = path[:-1]
                queryStr += " +path:%s/*" % path
            if fileName is not None:
                queryStr += " +file:%s*" % fileName
            if tags!=[]:
                for tag in tags:
                    if tag.strip() != "":
                        if tag.find("path:") > -1 or tag.find ("file:") > -1:
                            if tag.startswith("+"):
                                queryStr = queryStr + " " + tag
                            else:
                                queryStr = queryStr + " +" + tag
                        else:
                            queryStr += " +tags:%s*" % tag
            contentResults = []
            metaResults = []
            qt = self.__contentIndexer.QueryTokenizer(queryStr)
            tags = qt.extractTag("tags")
            pathQueryStr = " ".join(qt.extractTag("path")).strip()
            fileQueryStr = " ".join(qt.extractTag("file")).strip()
            queryStr = "".join(qt.tokens).strip()
            tagQueryStr = " ".join(tags).strip()
            if queryStr!="":
                #search(queryStr=None, keywordQueryStr=None, pathQueryStr=None)
                searchResults = self.__contentIndexer.search(queryStr)
                for doc in searchResults.values():
                    contentResults.append(doc.get("id"))
                searchResults.close()
            if tagQueryStr!="" or pathQueryStr!="" or fileQueryStr!="" :
                if pathQueryStr!="":
                    if pathQueryStr.startswith("+"):
                        tags.append("+")    # so that the code below will be trigged
                        pathQueryStr = pathQueryStr[1:]
                    pathQueryStr = pathQueryStr.replace("path:", "")
                    pass
                else:
                    pathQueryStr = None
                if tagQueryStr=="":
                    tagQueryStr = None
                if fileQueryStr=="":
                    fileQueryStr=None
                else:
                    if fileQueryStr.startswith("+"):
                        tags.append("+")
                        fileQueryStr = fileQueryStr[1:]
                    fileQueryStr = fileQueryStr.replace("file:", "")
                searchResults = self.__metaIndexer.search(tagQueryStr, \
                                        path=pathQueryStr, file=fileQueryStr)
                for doc in searchResults.values():
                    metaResults.append(doc.get("id"))
                searchResults.close()
            if ([True for t in tags if t.startswith("+")]!=[]) and \
                    (queryStr!="" and tagQueryStr!=""):
                s = set(contentResults)
                found = list(s.intersection(metaResults))
            else:
                found = contentResults + metaResults
        except Exception, e:
            print "search error - '%s'" % str(e)
            raise e
        return found

    
    def __reindex(self, item, metaOnly=False, renderIfNeeded=True):
        if item.isMissing or item.isDeleted:
            return
        file = item.relPath
        if item.needsUpdating and renderIfNeeded:
            item.render()
        if item.hasHtml:
            id = item.guid
            title = item.getMeta("title")
            if metaOnly==False:
                meta = {"metaTitle": title}
                content = item.getRendition(".text")
                if content is None:
                    msg = "Indexer can not get 'text' rendition for '%s'" % file
                    #raise Exception(msg)
                    self.iceContext.writeln("Warning: %s" % msg)
                else:
                    self.__contentIndexer.indexContent(content, id, meta, title=title)
            # Meta
            tags = item.tags
            taggedBy = []               #
            taggedBy = item.taggedBy
            links = self.__getLinks(item)
            
            ## Index (inline) annotations
            ##annotations = item.annotations.getAnnotations()
            ##commentsBy = [anno.author for anno in annotations]
            ##openComments = "\n- -\n".join([anno.message for anno in annotations \
            ##                                if anno.type=="openComment"])
            ##closedComments = "\n- -\n".join([anno.message for anno in annotations \
            ##                                if anno.type=="closedComment"])
            commentsBy = []
            openComments = ""
            closedComments = ""
            fileName = self.__fs.splitPathFileExt(file)[1]
            meta = {    "path":file,
                        "file":fileName,
                        "tags":tags,
                        "taggedBy":taggedBy,
                        "commentsBy":commentsBy,
                        "title": title,
                        "links": links,
                    }
            content = None
            content = openComments + "\n- -\n" + closedComments
            
            self.__metaIndexer.indexContent(content, id, meta, \
                        openComments=openComments, closedComments=closedComments)

    def __getLinks(self, item):
        links = []
        htmlBody, title, pageToc, style = item.getHtmlRendition()
        if htmlBody is not None:
            parentItem = item.parentItem
            doc = self.iceContext.Xml(htmlBody)
            docLinks = doc.getNodes("//*[local-name()='a']")
            for link in docLinks:
                href = link.getAttribute("href")
                if (href is not None) and not (href.startswith("#") or \
                                               href.startswith("http:") or \
                                               href.startswith("mailto:")):
                    relPath = self.iceContext.urlJoin(parentItem.relPath, href)
                    hashPos = relPath.find("#")
                    if hashPos > -1:
                        relPath = relPath[:hashPos]
                    if not relPath.startswith("/"):
                        relPath = os.path.abspath(relPath)
                    linkItem = self.iceContext.rep.getItemForUri(relPath)
                    relPath = linkItem.relPath
                    #print " ** linkItem: %s" % relPath
                    links.append(relPath)
            doc.close()
        return links





class DummyRepositoryIndexer(object):
    # Constructor:
    #   __init__(iceContext, indexRelBasePath)
    # Properties:
    ##   indexerRelBasePath
    ##   indexerAbsBasePath
    # Methods:
    #   reIndex(relPath="/", metaOnly=False)
    #   deleteIndex(id)
    #   search(queryStr, tags=[], fileName=None, path=None) -> returns a list of
    #   
    def __init__(self, iceContext, indexRelBasePath):
        self.iceContext = iceContext
        self.__rep = iceContext.rep
        self.__indexRelBasePath = indexRelBasePath
        self.__indexAbsBasePath = iceContext.rep.getAbsPath(indexRelBasePath)
        self.__flagFile = None
        self.__flagItem = None
        self.__setup(iceContext.fs)
        self.__reindexMsg = "If this file exists then a complete reindex is required (dummyIndexer)\n"
        self.dummyFlag = True
    
    
##    @property
##    def indexerRelBasePath(self):
##        return self.__indexRelBasePath
##    
##    @property
##    def indexerAbsBasePath(self):
##        return self.__indexAbsBasePath
    
    
    def __setup(self, fs):
        try:
            self.__flagFile = fs.join(self.__indexRelBasePath, "reIndex")
            self.__flagItem = self.__rep.getItem(self.__flagFile)
            item = self.__rep.getItem(self.__indexRelBasePath)
            if not item.isDir:
                item.makeDirectory(ignore=True)
                self.__flagItem.write(self.__reindexMsg)
        except Exception, e:
            self.iceContext.writeln("Warning: DummyRepositoryIndexer.__setup() error - '%s'" % str(e))
    
    
    def reIndex(self, item, metaOnly=False):
        try:
            id = item.guid
            self.__flagItem.write(self.__reindexMsg)
        except:
            pass
    
    
    def deleteIndex(self, id):
        try:
            self.__flagItem.write(self.__reindexMsg)
        except: 
            pass
    
    
    def getPathForId(self, id):
        return None
    
    def searchKeyword(self, query):
        return []
    
    def search(self, queryStr, tags=[], fileName=None, path=None):
        return []
    


class ProxyRepositoryIndexer(object):
    # Constructor:
    #   __init__(iceContext, indexRelBasePath)
    # Properties:
    #   
    # Methods:
    #   reIndex(relPath="/", metaOnly=False)
    #   deleteIndex(id)
    #   search(queryStr, tags=[], fileName=None, path=None) -> returns a list of
    #   
    def __init__(self, iceContext, indexRelBasePath=None, **kwargs):
        self.iceContext = iceContext
        self.__reIndexAll = True
        self.__reIndex = {}             # {itemId:metaOnlyFlag}
        self.__deleteIndex = {}         # {itemId:True}
        self.__repositoryIndexer = None
    
    
    def setup(self, iceContext, indexRelBasePath):
        repositoryIndexer = None
        
    
    
    def reIndex(self, item, metaOnly=False):
        if self.__repositoryIndexer is not None:
            try:
                return self.__repositoryIndexer.reIndex(item, metaOnly)
            except Exception, e:
                pass
        try:
            id = item.guid
            if self.__deleteIndex.has_key(id):
                self.__deleteIndex.pop(id)
            self.__reIndex[id] = self.__reIndex.get(id, False) or metaOnly
        except:
            pass
    
    
    def deleteIndex(self, id):
        if self.__repositoryIndexer is not None:
            return self.__repositoryIndexer.deleteIndex(id)
        self.__deleteIndex[id] = True
        if self.__reIndex.has_key(id):
            self.__reIndex.pop(id)
    
    
    def getPathForId(self, id):
        if self.__repositoryIndexer is not None:
            return self.__repositoryIndexer.getPathForId(id)
        return None
    
    
    def search(self, queryStr, tags=[], fileName=None, path=None):
        if self.__repositoryIndexer is not None:
            return self.__repositoryIndexer.search(queryStr, tags, fileName, path)
        return []
    
    
    def __getstate__(self):
        self.__repositoryIndexer = None
        d = dict(self.__dict__)
        d.pop("iceContext")
        d.pop("_%s__repositoryIndexer" % self.__class__.__name__)
        return d
    
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.__repositoryIndexer = None



