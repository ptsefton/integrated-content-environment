#!/usr/local/bin/python
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

""" Module to server HTTP requests via the twisted.web module. """



try:
    from twisted.web import server, resource, http
    from twisted.internet import reactor
except Exception, e:
    print str(e)
    raise Exception("Can not load twisted.web module!")


import types         # ListType
import urllib        # unquote
import re            # search
from urlparse import urlparse


class TwistedServer(resource.Resource):
    """ 
        A class that serves HTTP requests using twisted.web
    """
    isLeaf = True
    
    
    def __init__(self, iceContext, host, port, serverRequestDataClass, serverResponseDataClass):
        print "--- Starting the Twisted ICE Web server on port='%s' ---" % port
        resource.Resource.__init__(self)
        
        self.__iceContext = iceContext
        self.__host = host      # not used for the twisted server
        self.__port = port
        self.ServerRequestData = serverRequestDataClass
        self.ServerResponseData = serverResponseDataClass
        
        self.__iceRenderMethod = None        # takes two arguments - requestData, responseData - None return
        self.__icePreRenderMethod = None
        self.__icePostRenderMethod = None
        self.__sessionIdCount = 0
    
    
    def serve(self, iceRenderMethod, icePreRenderMethod=None, icePostRenderMethod=None):
        self.__iceRenderMethod = iceRenderMethod
        self.__icePreRenderMethod = icePreRenderMethod
        self.__icePostRenderMethod = icePostRenderMethod
        
        #""" Listen on the given port (on a single thread) for HTTP requests. """
        site = server.Site(self)
        reactor.listenTCP(self.__port, site)
        reactor.run()
    
    
    def render(self, request):
        """ Handle a HTTP request and return a response. """
        iceContext = self.__iceContext.clone()
        iceContext.requestData = self.__createRequestData(request)
        iceContext.responseData = self.ServerResponseData()
        
        if callable(self.__icePreRenderMethod) and \
            (self.__icePreRenderMethod(iceContext)==False):
                pass
        else:
            self.__iceRenderMethod(iceContext, iceContext.requestData, iceContext.responseData)
            if callable(self.__icePostRenderMethod):
                self.__icePostRenderMethod(iceContext)
        
        data = responseData.getData()
        if data.startswith("Not found") or responseData.notFound:
            request.setResponseCode(http.NOT_FOUND)
        for name, value in responseData.getHeaders().iteritems():
            request.setHeader(name, value)
        #request.setHeader("Content-type", responseData.contentType)
        request.write(data)
        request.finish()
        
        return server.NOT_DONE_YET
    
    
    def __createRequestData(self, request):
        path = urllib.unquote(request.path)
        urlPath = request.URLPath()
        reqHeaders = request.received_headers
        #print "-- Headers --"
        #for key, value in reqHeaders.iteritems():
        #    print " %s=%s" % (key, value)
        
        #location = urlparse(urlPath)[1]
        location = urlPath.netloc
        
        urlPath = str(urlPath)[:-1] + path
        #print "urlPath='%s', path='%s', location='%s'" % (urlPath, path, location)
        
        method = request.method
        args = request.args
        
        # hack to pass parameters with no value e.g. ?embed
        query = urlparse(request.uri)[4]
        if query != '':
            params = query.split('&')
            for p in params:
                ps = p.split('=')
                if len(ps) == 1:
                    args.update({ps[0]: ['']})
        
        #session = request.getSession()
        #sessionId = session.uid
        #session.expire()
        sessionId = request.getCookie("sessionId")
        if sessionId is None:
            import time
            self.__sessionIdCount += 1
            sessionId = "%s-%s" % (int(time.time()*1000), self.__sessionIdCount)
            print "Creating sessionId='%s'" % sessionId
            request.addCookie("sessionId", sessionId)
        
        filenames = self.__getTwistedUploadedFilenames(request)
        #requestData = ServerRequestData(path, method, args, session, sessionId, filenames)
        class FileStorage(object):      # to mock paste's fieldStorage object
            def __init__(self, filename, data):
                self.filename = filename
                self.__data = data
                self.file = self
            def read(self):
                return self.__data
        for key, value in filenames.iteritems():
            filename = value
            data = args.get(key)
            if type(data) is types.ListType and len(data)>0:
                data = data[0]
            filenames[key] = FileStorage(filename, data)
        requestData = self.ServerRequestData(path, method, args, sessionId, filenames,
                    urlPath=urlPath, location=location)
        return requestData
    
    
    def __getTwistedUploadedFilenames(self, request):
        ## Get upload (file) filename's
        filenames = dict()
        ##   Search for 'Content-Disposition: form-data; name="x"; filename="y"
        #request.content.reset()
        request.content.seek(0L)
        lines = request.content.readlines()
        if len(lines)>0:
            delimiterLine = lines[0]
            l = len(lines)-2
            x = 0
            while x<l:
                if lines[x]==delimiterLine:
                    line = lines[x+1].rstrip("\r\n")
                    line += ";"
                    i = line.find("filename=")
                    if i>0:
                        try:
                            name = re.search(" name=\"([^\\\"]+)\";", line).groups(1)[0]
                            #print "name: ", name
                            filename = line[i+len('filename="'):]
                            filename = filename[:filename.find('";')]
                            #Just for Window (IE)
                            if filename.find("\\") > -1:
                                filename = filename.replace("\\","/")
                                arr = filename.split("/")
                                filename = arr[len(arr)-1]
                            
                            #print "fileName: ", filename
                            filenames[name] = filename
                        except Exception, e:
                            print "error parsing [web].request.content for uploaded filename: " + str(e)
                            pass
                x += 1
        return filenames





