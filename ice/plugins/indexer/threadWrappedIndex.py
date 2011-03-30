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

from index import Index
from thread_util import WorkerThread, JobObject

# MainClass
# ThreadWrappedIndex            - Thread safe access to Index
#
# (the following are just supporting classes)
# ThreadWrappedDoc              - Thread safe access to a results.doc object
# ThreadWrappedSearchResults   - Thread safe access to searchResults object
#
#  Note: all work is done using the 'WorkerThread.getWorkerThread("luceneThread")' thread


class ThreadWrappedDoc(object):
    def __init__(self, doc, workerThread):
        self.__workerThread = workerThread
        self.__doc = doc
    
    def get(self, name):
        job = self.__workerThread.addJob(self.__doc.get, "index", name)
        job.join()
        if job.exception:
            raise job.exception
        return job.results
    
    def getFieldNames(self):
        job = self.__workerThread.addJob(self.__getFieldNames, "index")
        job.join()
        if job.exception:
            raise job.exception
        return job.results
    
    def __getFieldNames(self):
        fieldNames = []
        if self.__doc is not None:
            for field in self.__doc.getFields():
                name = field.name()
                fieldNames.append(name)
        return fieldNames


class ThreadWrappedSearchResults(object):
    def __init__(self, searchResults, workerThread):
        self.__workerThread = workerThread
        self.__searchResults = searchResults
        self.__closed = False
    
    @property
    def value(self):
        if hasattr(self.__searchResults, "value"):
            doc = self.__searchResults.value
            return ThreadWrappedDoc(doc, self.__workerThread)
        else:
            return None
    
    def values(self):
        # generator
        for doc in self.__searchResults.values():       # is this safe???
            yield ThreadWrappedDoc(doc, self.__workerThread)
    
    def __len__(self):
        # is this safe???
        return len(self.__searchResults)
    
    def close(self):
        if self.__closed==False:
            self.__closed = True
            self.__workerThread.addJob(self.__searchResults.close, "index")
            self.__searchResults = None
    
    def __del__(self):
        self.close()


class ThreadWrappedIndex(object):
    # Constructor:
    #   __init__(fs, indexPath, analyzer=None)
    # Properties:
    #   indexPath
    # Methods:
    #   create()        # Creates or reCreates the index  ##NOTE: for testing only. Raises an exception
    #   indexContent(content, id, metaItems={}, **kwargs)
    #   optimize()
    #   deleteIndex(id)
    #   searchContents(queryStr)            # returns a ThreadWrappedSearchResults object
    #   searchId(id)                        # returns a ThreadWrappedSearchResults object
    #   searchMeta(metaKey, metaValue)      # returns a ThreadWrappedSearchResults object
    QueryTokenizer = Index.QueryTokenizer
    #keywordAnalyzer = Index.KeywordAnalyzer
    LuceneLoadMessage = Index.LuceneLoadMessage
    
##    keywordAnalyzer = None
##    @staticmethod
##    def KeywordAnalyzer():
##        print "?????????????????????--"
##        if ThreadWrappedIndex.keywordAnalyzer is None:
##            t = WorkerThread.getWorkerThread("luceneThread")
##            job = JobObject(_function=Index.KeywordAnalyzer, _id="idKeywordAnalyzer")
##            t.jobQueue.insertJob(job)
##            job.join()      # Wait for the answer
##            if job.exception:
##                raise job.exception
##            ThreadWrappedIndex.keywordAnalyzer = job.results
##        return ThreadWrappedIndex.keywordAnalyzer
    
    
    def __init__(self, fs, indexPath, analyzer=None, analyzerName=None):
        self.__workerThread = WorkerThread.getWorkerThread("luceneThread")
        job = self.__workerThread.addJob(Index, "index", 
                                                fs, indexPath, 
                                                analyzer=analyzer,
                                                analyzerName=analyzerName)
        job.join()          # Wait for the answer
        self.__index = job.results
        if job.exception:
            raise job.exception
        self.__indexPath = fs.absolutePath(indexPath)
    
    @property
    def indexPath(self):
        return self.__indexPath
    
    def create(self):
        # JobObject(_function, _id, args, **kwargs)
        job = JobObject(_function=self.__index.create, _id="idCreate")
        self.__workerThread.jobQueue.insertJob(job)
        job.join()      # Wait for the results
        if job.exception:
            raise job.exception
        return job.results
    
    def indexContent(self, content, id, metaItems={}, **kwargs):
        self.__workerThread.addJob(self.__index.indexContent, "index", \
                                            content, id, metaItems, **kwargs)
    
    def optimize(self):
        self.__workerThread.addJob(self.__index.optimize, "index")
    
    def deleteIndex(self, id):
        self.__workerThread.addJob(self.__index.deleteIndex, "index", id)
    
    #def search(self, queryStr=None, keywordQueryStr=None, pathQueryStr=None, fileQueryStr=None):
    def search(self, queryStr=None, keywordQueryStr=None, **kwargs):
        # JobObject(_function, _id, args, **kwargs)
        job = JobObject(self.__index.search, "idSearch", queryStr, keywordQueryStr, **kwargs)
        self.__workerThread.jobQueue.insertJob(job)
        job.join()      # Wait for the answer
        if job.exception:
            raise job.exception
        searchResults = job.results
        searchResults = ThreadWrappedSearchResults(searchResults, self.__workerThread)
        return searchResults
    
    def searchId(self, id):                        # returns a SearchResults object
        # JobObject(_function, _id, args, **kwargs)
        job = JobObject(self.__index.searchId, "idSearchId", id)
        self.__workerThread.jobQueue.insertJob(job)
        job.join()      # Wait for the answer
        searchResults = job.results
        searchResults = ThreadWrappedSearchResults(searchResults, self.__workerThread)
        return searchResults
    
    def searchMeta(self, metaKey, metaValue):      # returns a SearchResults object
        # JobObject(_function, _id, args, **kwargs)
        job = JobObject(self.__index.searchMeta, "idSearchMeta", metaKey, metaValue)
        self.__workerThread.jobQueue.insertJob(job)
        job.join()      # Wait for the answer
        searchResults = job.results
        searchResults = ThreadWrappedSearchResults(searchResults, self.__workerThread)
        return searchResults















