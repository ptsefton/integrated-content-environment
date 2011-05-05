#!/usr/bin/env python
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

""" ResponseData """


class ServerResponseData(object):
    def __init__(self):
        self.__resultData = []
        self.__headers = dict()
        self.__notFound = False
        self.__forbidden = False
        self.__redirect = False
        self.__cookies = {}
    
    def getData(self):
        self.__resultData = ["".join(self.__resultData)]
        d = self.__resultData[0]
        self.setHeader("Content-Length", str(len(d)))
        return d
    def __appendData(self, value):
        self.__resultData.append(value)
    
    def __getNotFound(self):
        return self.__notFound
    def __setNotFound(self, value):
        self.__notFound = (value==True)
    notFound = property(__getNotFound, __setNotFound)
    
    def __getForbidden(self):
        return self.__forbidden
    def __setForbidden(self, value):
        self.__forbidden = value
    forbidden = property(__getForbidden, __setForbidden)
    
    
    def __getRedirect(self):
        return self.__redirect
    def __setRedirect(self, value):
        self.__redirect = (value==True)
    redirect = property(__getRedirect, __setRedirect)
    
    @property
    def data(self):
        d = self.getData()
        return d
    
    def __getContentType(self):
        return self.__headers.get("Content-type", "text/html")
    def __setContentType(self, value):
        self.__headers["Content-type"] = value
    contentType = property(__getContentType, __setContentType)
    
    @property
    def cookies(self):
        return self.__cookies
    
    
    def write(self, data):
        if data is None:
            raise Exception("received an unexpected 'None' type!")
        self.__appendData(data)
    
    
    def setResponse(self, data, mimeType="text/html"):
        self.contentType = mimeType
        if data is None:
            raise Exception("received an unexpected data='None'!")
        self.__appendData(data)
    
    def setHeader(self, name, value):
        self.__headers[name] = value

    def getHeaders(self):
        return self.__headers
    
    def setDownloadFilename(self, filename):
        """ set header 'Content-Disposition' for downloading a file
           e.g. to force the prompt saveAs to use the correct filename. """
        self.__headers["Content-Disposition"] = "attachment; filename=%s" % filename
    
    def setRedirectLocation(self, location):
        #self.__resultData = []
        #self.__headers = dict()
        #self.__notFound = False
        #self.__redirect = False
        #self.__cookies = {}
        
        self.redirect = True
        self.setHeader("Location", location)
    
    def setCookie(self, cookieName, cookieValue):
        self.__cookies[cookieName] = cookieValue
    
    
    def setNoCacheHeaders(self):
        self.setHeader("Pragma", "no-cache")
        self.setHeader("Expires", "-1")
        self.setHeader("Cache-Control", "no-cache")
    
    
    def addNoCacheMeta(self, xhtml, elementTree):
        #<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
        #<META HTTP-EQUIV="Expires" CONTENT="-1">
        xml = elementTree.XML(xhtml)
        head = xml.find("head")
        meta = elementTree.Element("meta", {"http-equiv":"Pragma", "content":"no-cache"})
        head.append(meta)
        meta = elementTree.Element("meta", {"http-equiv":"Expires", "content":"-1"})
        head.append(meta)
        xhtml = elementTree.tostring(xml)
        return xhtml
##        xml = self.iceContext.Xml(xhtml)
##        node = xml.getNode("/html/head")
##        newNode = xml.createElement("meta")
##        newNode.setAttribute("http-equiv", "Pragma")
##        newNode.setAttribute("content", "no-cache")
##        node.addChild(newNode)
##        newNode = xml.createElement("meta")
##        newNode.setAttribute("http-equiv", "Expires")
##        newNode.setAttribute("content", "-1")
##        node.addChild(newNode)
##        xhtml = str(xml)
##        xml.close()
##        return xhtml

    
    def __str__(self):
        s = "[serverResponseData object] len(data)='%s', headers='%s', values='%s'" 
        s = s % (len(self.__resultData), self.__headers.keys(), self.__headers.values())
        if self.redirect:
            s += ", redirect=True"
        return s




class mockServerResponseData(object):
    def __init__(self):
        self.__resultData = None
        self.__headers = dict
    
    def setResultData(self, data):
        self.__resultData = data
    
    def setHeader(self, name, value):
        self.__headers[name] = value

    def getResultData(self):
        return self.__resultData
    
    def getHeaders(self):
        return self.__headers


