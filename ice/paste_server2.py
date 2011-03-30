#!/usr/bin/python
#
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

"""
    Python Paste ICE Server
"""

import types
import sys
import threading

try:
    from paste import httpserver
    from paste.request import parse_formvars, construct_url
    from paste.evalexception import EvalException
except Exception, e:
    raise Exception("Can not load the 'paste' module!")



class PasteServer(object):
    """ 
        A class that serves HTTP requests using paste
    """
    
    
    def __init__(self, iceContext, host, port, serverRequestDataClass, serverResponseDataClass):
        print "--- Starting the Paste ICE Web server on port='%s', host='%s' ---" % (port, host)
        self.iceContext = iceContext
        self.__host = host
        self.__port = port
        self.ServerRequestData = serverRequestDataClass
        self.ServerResponseData = serverResponseDataClass
        
        self.__iceRenderMethod = None        # takes two arguments - requestData, responseData - None return
        self.__icePreRenderMethod = None
        self.__icePostRenderMethod = None
    
    
    def serve(self, iceRenderMethod, icePreRenderMethod=None, icePostRenderMethod=None):
        self.__iceRenderMethod = iceRenderMethod
        self.__icePreRenderMethod = icePreRenderMethod
        self.__icePostRenderMethod = icePostRenderMethod
        
        app = self.__app
        if self.iceContext.settings.get("paste.profiling", False):
            from paste.debug.profile import ProfileMiddleware
            app = ProfileMiddleware(self.__app)
        
        httpserver.serve(app, host=self.__host, port=self.__port)


    def __app(self, environ, start_response):
        requestContext = self.iceContext.Object()
        ##iceContext = self.iceContext.clone()
        requestData = self.__createRequestData(environ)
        responseData = self.ServerResponseData()
        requestContext.requestData = requestData
        requestContext.responseData = responseData
        session = requestData.session
        requestContext.session = session
        requestContext.path = requestData.unquotedPath
        requestContext.method = requestData.method
        
        currentThread = threading.currentThread()
        threadName = currentThread.getName()
        requestContext.threadName = threadName
        if session.logWriter is None:
            logWriter = self.iceContext.LogWriter()
            session.logWriter = logWriter
        self.iceContext.threadLogWriter.setThreadLogWriter(threadName, session.logWriter)
        
        if callable(self.__icePreRenderMethod) and \
            (self.__icePreRenderMethod(self.iceContext, requestContext)==False):
                pass
        else:
            rContext = self.__iceRenderMethod(requestContext)
            if callable(self.__icePostRenderMethod):
                self.__icePostRenderMethod(rContext)
        
        contentType = responseData.contentType
        data = responseData.data
        headers = [("Content-type", contentType),
                   ("Set-Cookie", "SESSION=%s; path=/" % requestData.sessionId)]
        for cookieName, cookieValue in responseData.cookies.iteritems():
            headers.append( ("Set-Cookie", "%s=%s" % (cookieName, cookieValue)) )
        headers.extend((k, v) for k, v in responseData.getHeaders().iteritems()
                                       if k.lower() != "content-type")
        if data.startswith("Not found") or responseData.notFound:
            start_response("404 Not Found", headers)
        elif data.startswith("Forbidden") or responseData.forbidden:
            start_response("403 Forbidden", headers)
        elif responseData.redirect:
            start_response("303 Redirect", headers)
        elif data.find("ice-error")>-1:
            start_response("500 Internal Server Error", headers)
        else:
            start_response("200 OK", headers)
        return [data]
    
    
    def __createRequestData(self, environ):
        fields = parse_formvars(environ)
        acceptEncoding = environ.get("HTTP_ACCEPT_ENCODING", "")
        acceptGzip = acceptEncoding.find("gzip")!=-1;
        userAgent = environ.get("HTTP_USER_AGENT", "")
        method = environ["REQUEST_METHOD"]
        path = (environ.get("SCRIPT_NAME", "") + environ.get("PATH_INFO", ""))
        options = environ.get("options", {})
        host = environ["SERVER_NAME"]
        port = environ["SERVER_PORT"]
        location = environ["REMOTE_ADDR"]
        errors = environ["wsgi.errors"]
        urlScheme = environ.get("wsgi.url_scheme", "http")
        httpHost = environ.get("HTTP_HOST", "")
        urlPath = "%s://%s%s" % (urlScheme, httpHost, path)
        queryString = environ.get("QUERY_STRING", "")
        cookies = environ.get("HTTP_COOKIE", "")
        headers = {}
        for k, v in environ.iteritems():
            if k.startswith("HTTP_"):
                headers[k[5:]] = v
        #print "cookies='%s'" % cookies
        args = fields.mixed()
        filenames = {}
        for k, v in args.iteritems():
            if type(v) is types.InstanceType:
                #change the file name
                if v.filename.find("\\"):
                    v.filename = v.filename.replace("\\","/")
                    arr = v.filename.split("/")
                    v.filename = arr[len(arr)-1]
                filenames[k] = v
        
        # Read cookies
        if cookies.find("=")!=-1:
            cookies = dict([cookie.split("=", 1) for cookie in cookies.split("; ")])
        else:
            cookies = {}
        sessionId = cookies.get("SESSION", None)
        
        # create requestData and responseData objects
        requestData = self.ServerRequestData(path=path, method=method, args=args, \
                        sessionId=sessionId, filenames=filenames, port=port, \
                        urlPath=urlPath, location=location, cookies=cookies,
                        queryString=queryString, acceptGzip=acceptGzip, headers=headers)
        return requestData




class SafeEvalException(EvalException):
    def __init__(self, app):
        self.__app = app
        
    def __call__(self, environ, start_response):
        host = environ["HTTP_HOST"]
        #host = environ["SERVER_NAME"]
        #port = environ["SERVER_PORT"]
        if host=="localhost:8000":
            return EvalException(self.__app)(environ, start_response)
        return self.__app(environ, start_response)



class AuthMiddleWare(object):
    def __init__(self, wrapApp):
        self.__wrapApp = wrapApp
        self.__authReqired = "401 Authentication Required"
        self.__contentType = ('Content-type', 'text/html')
        self.__wwwAuth = ("WWW-Authenticate", 'Basic realm="Ice"') #Header to send
        #self.__authHeader = "Authorization"    # ("Authorization", "Basic base64Encoded_Username:Password")
        #self.__httpAuth = "HTTP_AUTHORIZATION"
        self.__html = "<html><head><title>Authentication Required</title></head><body>" + \
            "<h1>Authentication Required</h1> If you can't get in, then stay out. </body></html>"
    
    def __call__(self, environ, start_response):
        authHeader = environ.get("HTTP_AUTHORIZATION")
        if not self.authorized(authHeader):
            start_response(self.__authReqired, [self.__contentType, self.__wwwAuth])
            return [self.__html]    #Note: this is displayed only if the user
                                    #       selects the cancel button.
        # auth OK, so just pass every thing through
        environ["USERNAME"] = self.__username
        return self.__wrapApp(environ, start_response)

    def authorized(self, authHeader):
        if authHeader:
            authType, encodedData = authHeader.split(None, 1)  # split in 2 on whitespace
            if authType.lower()=='basic':
                data = encodedData.decode('base64')
                username, password = data.split(':', 1)
                self.__username = username
                return username==password   # Just for testing
        return False







