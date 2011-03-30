#!/usr/bin/python
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

""" """


AvaiableWebServers = {}
try:
    from paste_server2 import PasteServer
    AvaiableWebServers["paste"] = PasteServer
    AvaiableWebServers["default"] = PasteServer
except Exception, e:
    print "Error loading PasteServer - '%s'" % str(e)
    PasteServer = None

TwistedServer = None
#try:
#    from twisted_server2 import TwistedServer
#    AvaiableWebServers["twisted"] = TwistedServer
#    AvaiableWebServers["default"] = TwistedServer
#except Exception, e:
#    print "Error loading TwistedServer - '%s'" % str(e)



class IceServer(object):
    def __init__(self, iceContext, IceRequest, ServerRequestData, ServerResponseData):
        """ 
            iceContext
            IceRequest class - The class/object that handles the requests
            ServerRequestData class - Used to create the requstedData objects with
            ServerResponseData class - Used to create the responseData objects with
        """
        self.iceContext = iceContext
        self.IceRequest = IceRequest
        self.ServerRequestData = ServerRequestData
        self.ServerResponseData = ServerResponseData
    
    
    def serve(self):
        """ start listening for requests """
        #print "IceServer.server()"
        port = self.iceContext.config.port
        host = self.iceContext.config.hostAddress
        serverName = self.iceContext.settings.get("webserver", "default").lower()
        
        # Setup/init the request handlering object
        iceRequest = self.IceRequest(self.iceContext)
        
        # Find what web server that we are going to use
        Server = AvaiableWebServers.get(serverName, None)
        if Server is None:
            Server = AvaiableWebServers.get("default", None)
        if Server is None:
            print "*** No '%s' or 'default' Server found! ***" % serverName
            return
        
        # create the web server
        server = Server(self.iceContext, host=host, port=port, 
                            serverRequestDataClass=self.ServerRequestData, 
                            serverResponseDataClass=self.ServerResponseData)
        if server is not None:
            iceRenderMethod = iceRequest.processRequest
            # serve
            server.serve(iceRenderMethod, self.__preRender, self.__postRender)
    
    
    
    def __preRender(self, iceContext, requestContext):
        asServiceOnly = iceContext.settings.get("asServiceOnly", False)
        externalAccess = iceContext.settings.get("enableExternalAccess", False)
        requestData = requestContext.requestData
        path = requestContext.path
        location = requestData.location
        #print "path='%s', asServiceOnly='%s', externalAccess='%s'" % (path, asServiceOnly, externalAccess)
        if True: # local requests only          ## location & path
            if (location=="localhost" or location.startswith("localhost:") or \
                location=="127.0.0.1" or location.startswith("127.0.0.1:")):
                # OK from a local address
                pass
            elif asServiceOnly:
                if path.startswith("/api/"):
                    pass
                else:
                    html = "<h2>No external access allowed! (except as service)</h2>"
                    requestContext.responseData.write(html)
                    return False
            elif externalAccess:
                pass
            else:
                print "location='%s'" % location
                requestContext.responseData.write("<h2>No external access allowed!</h2>")
                return False
        iceContext.gTime.setup()
        iceContext.gTime.mark("Start request")
        # return False to cancel any more processing (rendering)


    def __postRender(self, iceContext):
        iceContext.gTime.stopAll()
        if iceContext.gTime.isHtmlPage:
            if iceContext.gTime.enabled:
                print iceContext.gTime
            else:
                #print "Done."
                print "IceRequest completed in %s\n" % (int(iceContext.gTime.totalTime*1000+0.5)/1000.0)




