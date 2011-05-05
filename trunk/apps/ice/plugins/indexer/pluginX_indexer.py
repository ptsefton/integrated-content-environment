
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
import time

try:
    # Hack: to work around a Java 'Segmentaion fault' error that may happend (e.g. ice-one)
    import uno
except Exception, e:
    pass
try:
    from threadWrappedIndex import ThreadWrappedIndex
    IceIndexer = ThreadWrappedIndex
    IceIndexerQueryTokenizer = ThreadWrappedIndex.QueryTokenizer
except Exception, e:
    print "Failed to get threadWrappedIndex - '%s'" % str(e)
    IceIndexer = None
    IceIndexerQueryTokenizer = None

pluginName = "ice.indexer"
pluginDesc = "indexer"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceIndexer
    #pluginClass = ProxyIndexer         # For testing only
    pluginInitialized = True
    if IceIndexer is None:
        return None
    else:
        return pluginClass


class ProxyIndexer(object):
    # IceIndexer == ThreadWrappedIndex
        # Constructor:
        #   __init__(fs, indexPath, analyzer=None)
        # Properties:
        #   indexPath
        # Methods:
        #   indexContent(content, id, metaItems={}, **kwargs)
        #   optimize()
        #   deleteIndex(id)
        #   searchContents(queryStr)            # returns a ThreadWrapppedSearchResults object
        #   searchId(id)                        # returns a ThreadWrapppedSearchResults object
        #   searchMeta(metaKey, metaValue)      # returns a ThreadWrapppedSearchResults object
    
    def __init__(self, fs, indexPath, analyzer=None):
        print "ice.indexer ProxyIndexer.__init__(indexPath='%s')" % indexPath
        self.__indexPath = indexPath
        pass
    
    
    def indexContent(self, content, id, metaItems={}, **kwargs):
        print "ice.indexer ProxyIndexer.indexContent(id='%s')" % id
    
    
    def optimize(self):
        print "ice.indexer ProxyIndexer.optimize()"
    
    
    def deleteIndex(self, id):
        print "ice.indexer ProxyIndexer.deleteIndex(id='%s')" % id
    
    
    def searchContents(self, queryStr):            # returns a ThreadWrapppedSearchResults object
        print "ice.indexer ProxyIndexer.searchContents(queryStr='%s')" % queryStr
        return ProxySearchResults()
    
    
    def searchId(self, id):                        # returns a ThreadWrapppedSearchResults object
        print "ice.indexer ProxyIndexer.searchId(id='%s')" % id
        return ProxySearchResults()
    
    
    def searchMeta(self, metaKey, metaValue):      # returns a ThreadWrapppedSearchResults object
        print "ice.indexer ProxyIndexer.searchMeta(metaKey='%s', metaValue='%s')" % (metaKey, metaValue)
        return ProxySearchResults()



class ProxySearchResults(dict):
    def __init__(self, searcher):
        dict.__init__(self)
        self.__closed = False
    
    def close(self):
        if self.__closed==False:
            self.__closed = True
    
    def __del__(self):
        self.close()



