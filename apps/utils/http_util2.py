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


import time
import string
import types
from mimetypes import guess_type
from urlparse import urlsplit
from httplib2 import Http as Http2
from urllib import urlencode


class Http(object):
    # Constructor:
    #   __init__(dummyHTTP=None)    # dummyHTTP is for testing
    # Properties:
    #   
    # Methods:
    #   get(url, queryString="", includeExtraResults=False)
    #       -> returns the result as a string or if includeExtraResult==True
    #           returns a tuple of (results, headers, errCode, errMsg)
    #   post(url, formDataList)
    #          formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
    #          (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
    #        -> return the server response data
    def __init__(self, dummyHTTP=None, cachePath=None):
        if dummyHTTP is None:
            self.__HTTP = Http2(cachePath)
            self.__HTTP.force_exception_to_status_code = True
        else:
            self.__HTTP = dummyHTTP
    
    
    def get(self, url, queryString="", includeExtraResults=False):
        # Hack to by pass proxies for localhost (for the MAC)
        localNames = ["local", "localhost", "127.0.0.1"]
        hostName = urlsplit(url)[1].split(":")[0]
        proxies = None
        if hostName in localNames:
            proxies = {}
        #
        if queryString is None:
            queryString = ""
        if len(queryString)>0 and not queryString.startswith("?"):
            queryString = "?" + queryString
        response, content = self.__HTTP.request(url + queryString, "GET")
        if includeExtraResults:
            return content, response, response.status, response.reason
        return content
    
    
    def post(self, url, formDataList, includeExtraResults=False):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
            Return the server response data
        """
        headers = {}
        # is this a multipart post or not
        
        # is this a multipart post or not
        fileTypes = [types.TupleType, types.FileType]
        dataTypes = [True for formName, data in formDataList if type(data) in fileTypes]
        multipart = dataTypes!=[]
        if multipart:
            contentType, data = self.__encodeMultipartFormdata(formDataList)
        else:
            print "NOT multipart"
            contentType, data = self.__encodeFormdata(formDataList)
        
        headers["Content-Type"] = contentType
        headers["Content-Length"] = str(len(body))
        response, content = self.__HTTP.request(url, "POST", body=body, headers=headers)
        if includeExtraResults:
            return content, response, response.status, response.reason
        return content
    
    
    def request(self, uri, method="GET", body=None, headers={}):
        if body is not None or type(body) in types.StringTypes:
            pass
        else:
            body = self.__encodeMultipartFormdata(body)
        response, content = self.__HTTP(uri, method, body, headers)
        return response, content
    
    
    def addCredentials(self, name, password, domain=None):
        self.__HTTP.add_credentials(name, password, domain)
        return self
    
    
    def addCertificate(self, key, cert, domain):
        self.__HTTP.add_certificate(key, cert, domain)
        return self
    
    
    def clearCredentials(self):
        self.__HTTP.clear_credintials()
        return self
    
    
    def __encodeFormdata(self, formDataDict):
        dataDict = dict(formDataList)
        data = urlencode(dataDict)
        contentType = "application/x-www-form-urlencoded"
        return contentType, data
    
    
    def __encodeMultipartFormdata(self, formDataList):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
        """
        boundary = str(time.time()).replace(".", "_").rjust(32, "-")
        
        lines = []
        for formName, data in formDataList:
            lines.append("--" + boundary)
            if type(data) is types.StringType:
                cd = "Content-Disposition: form-data; name=\"%s\"" % formName
                lines.append(cd)
            else:
                dataType = type(data)
                if dataType is types.TupleType:
                    filename, data = data
                elif dataType is types.FileType:
                    filename = data.name
                    data = data.read()
                else:
                    print "Ignoring unsupported data type: %s" % dataType
                    continue
                cd = "Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" % (formName, filename)
                lines.append(cd)
                lines.append("Content-Type: %s" % self.__getFileContentType(filename))
            lines.append("")
            lines.append(data)
        lines.append("--" + boundary + "--")
        lines.append("")
        data = string.join(lines, "\r\n")
        contentType = "multipart/form-data; boundary=%s" % boundary
        return contentType, data
    
    
    def __getFileContentType(self, filename):
        return guess_type(filename)[0] or 'application/octet-stream'






