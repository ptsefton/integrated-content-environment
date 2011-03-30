 #!/usr/bin/env python
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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
from queryTokenizer import QueryTokenizer       # our own query tokenizer

LuceneLoadMessage = ""

try:
    # look for java runtme on windows in the standard location
    import os, sys
    if sys.platform=="win32":
        import _winreg as wreg
        reg = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
        key = wreg.OpenKey(reg, r"SOFTWARE\JavaSoft\Java Runtime Environment")
        v,t = wreg.QueryValueEx(key, "CurrentVersion")
        key = wreg.OpenKey(reg, r"SOFTWARE\JavaSoft\Java Runtime Environment\%s" % v)
        javaHome,t = wreg.QueryValueEx(key, "JavaHome")
        reg.Close()
        if javaHome:
            loc = os.path.join(javaHome, "bin", "client")
            os.environ["PATH"] = os.pathsep.join(os.environ["PATH"].split(os.pathsep) + [loc,])
        else:
            print "WARNING: Java not found"
    import lucene
    try:
        classpath = lucene.CLASSPATH
        # if running compiled version
        if hasattr(sys, "frozen"):
            if sys.platform=="win32":
                classpath = ";".join([os.path.abspath(os.path.join("lucene", jarFile)) \
                                      for jarFile in os.listdir("lucene")])
        lucene.initVM(classpath)
        LuceneLoadMessage += "Using lucene/JCC v%s" % lucene.VERSION
    except Exception, e:
        LuceneLoadMessage += "Error trying to using lucene/JCC v%s '%s'" % (lucene.VERSION, str(e))
        print LuceneLoadMessage
except:
    #import PyLucene as lucene
    #sys.modules["lucene"] = PyLucene
    #LuceneLoadMessage += "Using PyLucene/GCJ v%s" % lucene.VERSION
    ## NOTE: Must also use a use the PyLucene's Thread module instead of the Python's threading.Thread module
    raise 
from lucene import QueryParser, IndexSearcher, Document, Field, Token,\
            StandardAnalyzer, SimpleAnalyzer, KeywordAnalyzer, WhitespaceAnalyzer, \
            IndexWriter, IndexReader, FSDirectory, Term, TermQuery, \
            PhraseQuery, PrefixQuery, TermQuery, RAMDirectory, VERSION
print LuceneLoadMessage


class SearchResults(dict):
    def __init__(self, searcher):
        dict.__init__(self)
        self.__searcher = searcher
        self.__closed = False
    
    def close(self):
        if self.__closed==False:
            self.__searcher.close()
            self.__closed = True
    
    def __del__(self):
        self.close()



class Index(object):
    # Constructor:
    #   __init__(fs, indexPath, analyzer=None)
    # Properties:
    #   indexPath
    # Methods:
    #   create()        # Creates or reCreates the index  ##NOTE: for testing only. Raises an exception
    #   indexContent(content, id, metaItems={}, **kwargs)
    #   optimize()
    #   deleteIndex(id)
    #   searchContents(queryStr)            # returns a SearchResults object
    #   searchId(id)                        # returns a SearchResults object
    #   searchMeta(metaKey, metaValue)      # returns a SearchResults object
    QueryTokenizer = QueryTokenizer
    StandardAnalyzer = StandardAnalyzer
    KeywordAnalyzer = KeywordAnalyzer
    SimpleAnalyzer = SimpleAnalyzer
    WhitespaceAnalyzer = WhitespaceAnalyzer
    LuceneLoadMessage = LuceneLoadMessage
    
    def __init__(self, fs, indexPath, analyzer=None, analyzerName=None):
        self.__fs = fs
        self.__indexPath = fs.absolutePath(indexPath)
        if VERSION<"2.2":
            raise Exception("Unsupport version of lucene used!")
            self.__store = FSDirectory.getDirectory(self.__indexPath, False)
        if VERSION>"2.3":
            lucene.getVMEnv().attachCurrentThread()
            self.__store = FSDirectory.getDirectory(self.__indexPath)
        if analyzer is None:
            if analyzerName and analyzerName.lower()=="keywordanalyzer":
                analyzer = self.KeywordAnalyzer()
            else:
                analyzer = self.StandardAnalyzer()
        self.__analyzer = analyzer
        try:
            writer = IndexWriter(self.__store, self.__analyzer, False)
            writer.close()
        except Exception, e:
            #print "index __init__() e='%s'" % str(e)
            self.create()
    
    @property
    def indexPath(self):
        return self.__indexPath
    
    
    def __del__(self):
        pass
    
    
    def create(self):
        """ Only need for testing. """
        msg = "index.create() called! (new index created)"
        writer = IndexWriter(self.__store, self.__analyzer, True)
        writer.close()
        #raise Exception(msg)
    
    
    def indexContent(self, content, id, metaItems={}, **kwargs):
        term = None
        self.__writer = None
        if self.__hasId(id):
            term = Term("id", id)
            if VERSION<"2.2":
                self.__deleteTerm(term)
            else:
                self.__writer = IndexWriter(self.__store, self.__analyzer, False)
                self.__writer.deleteDocuments(term)
        if self.__writer is None:
            self.__writer = IndexWriter(self.__store, self.__analyzer, False)
        self.__writer.setMaxFieldLength(1048576)
        doc = Document()
        if content is not None:
            if kwargs.has_key("title"):     # Add title to contents (for easier searching)
                content = kwargs.get("title", "") + "\n" + content
            doc.add(Field("content", content,
                                   Field.Store.YES,     # or NO
                                   Field.Index.TOKENIZED))
        for key, value in kwargs.iteritems():
            doc.add(Field(key, value,
                                Field.Store.YES,        # or NO
                                Field.Index.TOKENIZED))
        metaItems["id"] = id
        for key, value in metaItems.iteritems():
            if type(value) is types.ListType:
                for tag in value:
                    doc.add(Field(key, tag,
                           Field.Store.YES,                 # always YES
                           Field.Index.TOKENIZED))
            else:
                doc.add(Field(key, value,
                       Field.Store.YES,                 # always YES
                       Field.Index.UN_TOKENIZED))
        self.__writer.addDocument(doc)
        #self.__writer.optimize()
        self.__writer.close()
    
    
    def __deleteTerm(self, term):       # only need for version before 2.2.x.x
        self.__reader = IndexReader.open(self.__store)
        self.__reader.deleteDocuments(term)
        self.__reader.close()
    
    
    def optimize(self):
        self.__writer = IndexWriter(self.__store, self.__analyzer, False)
        self.__writer.optimize()
        self.__writer.close()
    
    
    def deleteIndex(self, id):
        term = Term("id", id)
        if term is not None:
            if VERSION<"2.2":
                self.__deleteTerm(term)
            else:
                writer = IndexWriter(self.__store, self.__analyzer, False)
                writer.deleteDocuments(term)
                writer.close()
    
    
    def searchContents(self, queryStr):
        return self.search(queryStr=queryStr)
    #def searchContents(self, queryStr):
    #    searcher = IndexSearcher(self.__indexPath)
    #    query = QueryParser("content", self.__analyzer).parse(queryStr)
    #    hits = searcher.search(query)
    #    #print hits.length()
    #    
    #    searchResults = SearchResults(searcher)
    #    for i, doc in hits:
    #        searchResults[doc.get("id")] = doc
    #    return searchResults
    
    
    def search(self, queryStr=None, keywordQueryStr=None, **kwargs):
        # Note: keywordQueryStr is case-sensitive (and does not allow wild cards etc)
        #   pathQueryStr is case-sensitive and can optionally end with a '*'
        if (queryStr is None) and (keywordQueryStr is None) and kwargs=={}:
            raise Exception("Error search requests at least one non None argument!")
        
        searcher = IndexSearcher(self.__indexPath)
        query=None
        if queryStr is not None:
            try:
                query = QueryParser("content", self.__analyzer).parse(queryStr)
            except Exception, e:
                raise e
        if keywordQueryStr is not None:
            # Note: all analyzers uses LowerCaseFilter except KeywordAnalyzer()
            #analyzer = WhitespaceAnalyzer()     # uses LowerCaseFilter
            analyzer = KeywordAnalyzer()         #
            keywordQuery = QueryParser("content", analyzer).parse(keywordQueryStr)
            #keywordQuery = PrefixQuery(Term("one", "oNe"))
            if query is None:
                query = keywordQuery
            else:
                query.combine(keywordQuery)
                
        if kwargs !={}:
            pathQuery = None
            for key in kwargs:
                keyValue = kwargs[key]
                if keyValue is not None:
                    if keyValue.endswith("*"):
                        term = Term(key, keyValue[:-1])
                        pathQuery = PrefixQuery(term)
                    else:
                        term = Term(key, keyValue)
                        pathQuery = TermQuery(term)
            if query is None:
                query = pathQuery
            else:
                query.combine([pathQuery])
        searchResults = self.__getSearchResults(searcher, query)
        return searchResults
    
    
    def searchId(self, id):
        searchResults = self.searchMeta("id", id)
        if len(searchResults)>0:
            searchResults.value = searchResults.values()[0]
        else:
            searchResults.value = None
        return searchResults
    
    
    def searchMeta(self, metaKey, metaValue):
        searcher = IndexSearcher(self.__indexPath)
        term = Term(metaKey, metaValue)
        query = TermQuery(term)
        return self.__getSearchResults(searcher, query)
    
    
    def __getSearchResults(self, searcher, query):
        hits = searcher.search(query)
        searchResults = SearchResults(searcher)
        if VERSION<"2.3":
            for i, doc in hits:
                searchResults[doc.get("id")] = doc
        else:
            for hit in hits:
                hit = lucene.Hit.cast_(hit)
                doc = hit.getDocument()
                searchResults[doc.get("id")] = doc
        return searchResults
    
    
    def __hasId(self, id):
        searcher = IndexSearcher(self.__indexPath)
        term = Term("id", id)
        num = searcher.docFreq(term)
        searcher.close()
        #print "__hasId num='%s'" % num
        if num==0:
            return False
        else:
            return True
    
    
    def test(self, test):
        class _analyzer(object):
            def tokenStream(self, fieldName, reader):
                class _tokenStream(object):
                    def __init__(self, fieldName, reader):
                        self.__TOKENS =     ["1", "2", "3", "4", "5"]
                        self.__INCREMENTS = [ 1,   2,   1,   0,   1] 
                        self.__INCREMENTS = [ 1,   1,   1,   0,   1] # 3-4 False, 2-4 True, 3-5 True 
                            # All zero all False, All ones then all sequences True
                        self.__i = 0
                        #print "__init__ fieldName='%s', reader.read()='%s'" % (fieldName, reader.read())
                    def next(self):
                        #print "next"
                        i = self.__i
                        if i>=len(self.__TOKENS):
                            return None
                        token = Token(self.__TOKENS[i], i, i)
                        #token.setPositionIncrement(self.__INCREMENTS[i])
                        self.__i = i + 1
                        return token
                return _tokenStream(fieldName, reader)
                #return StandardAnalyzer().tokenStream(fieldName, reader)   # does not work!
        analyzer = _analyzer()
        store = RAMDirectory()
        writer = IndexWriter(store, analyzer, True)
        doc = Document()
        field = Field("field1", "bogusText", Field.Store.YES, Field.Index.TOKENIZED)
        doc.add(field)
        writer.addDocument(doc)
        writer.optimize()
        writer.close()
        
        searcher = IndexSearcher(store)
        
        def qTest(one, two, expected=0):
            query = PhraseQuery()
            query.add(Term("field1", one))
            query.add(Term("field1", two))
            hits = searcher.search(query)
            #print "'%s', '%s' - result = %s  (%s)" % (one, two, len(hits), expected==len(hits))
            #test.assertEqual(expected, len(hits))
        
        qTest("1", "2", 0)
        qTest("2", "3", 1)
        qTest("3", "4", 0)
        qTest("4", "5", 1)
        #print
        qTest("2", "4", 1)
        qTest("3", "5", 1)
        qTest("2", "5", 0)
        #print
        #print "===="
        query = QueryParser("field1", analyzer).parse("2")
        hits = searcher.search(query)
        #print "hits=%s" % len(hits)
        #print self.__analyzer.STOP_WORDS














