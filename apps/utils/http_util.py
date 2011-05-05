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


import time
import string
import types
from mimetypes import guess_type
from httplib import HTTP
from urlparse import urlsplit
import urllib
import urllib2
import gzip
from cStringIO import StringIO


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
    def __init__(self, dummyHTTP=None):
        if dummyHTTP is None:
            self.__HTTP = HTTP
        else:
            self.__HTTP = dummyHTTP

    def delete(self, url, includeExtraResults=False):
        return self.get(url, includeExtraResults, method="DELETE")

    def get(self, url, queryString="", includeExtraResults=False, method="GET"):
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
        #
        urlopener = urllib._urlopener
        f = urllib.FancyURLopener()
        urllib._urlopener = f
        # Override the prompting for username/password
        def prompt_user_passwd(host, realm):
            return ("", "")
        f.prompt_user_passwd = prompt_user_passwd
        try:
            obj = urllib.urlopen(url + queryString, proxies=proxies)
            data = obj.read()
            info = obj.info()
            headers = [i.split(":", 1) for i in info.headers]
            headers = [(a, b.strip()) for a, b in headers]
            headers = dict(headers)
            if headers.get("Content-Encoding", "")=="gzip":
                #print "GZipped" 
                data = self.__ungzip(data)
            errCode = 200
            errMsg = "OK"
        except Exception, e:
            data = None
            errCode = -1
            errMsg = str(e)
            headers = {}
        urllib._urlopener = urlopener       # restore urlopener
        if includeExtraResults:
            return data, headers, errCode, errMsg
        else:
            return data
        ##
        host, path = urlsplit(url)[1:3]
        http = self.__HTTP(host)
        try:
            http.putrequest(method, path+queryString)
            http.endheaders()       # get request is sent!
            #http.send("")
            errCode, errMsg, headers = http.getreply()
            results = http.file.read()
        except Exception, e:
            results = ""
            errCode = -1
            errMsg = str(e)
        if includeExtraResults:
            results = results, errCode, errMsg
        return results

    def get2(self, url, queryString=None, headers={}):
        if False:       # proxy handling
            localNames = ["local", "localhost", "127.0.0.1"]
            hostName = urlsplit(url)[1].split(":")[0]
            proxies = None
            if hostName in localNames:
                proxies = {}
            proxy_support = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
        if False:       # basic auth handling
            passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            topLevelUrl = url
            passwordMgr.add_password(None, topLevelUrl, username, password)
            handler = urllib2.HTTPBasicAuthHandler(passwordMgr)
            opener = urllib2.build_opener(handler)  # [, proxy_support]
            #opener.open(url)
            urllib2.install_opener(opener)

        if queryString is None:
            queryString = ""
        if len(queryString)>0 and not queryString.startswith("?"):
            queryString = "?" + queryString
        try:
            req = urllib2.Request(url + queryString, None, headers)
            res = urllib2.urlopen(req)
            data = res.read()
            info = res.info()
            headers = [i.split(":", 1) for i in info.headers]
            headers = [(a, b.strip()) for a, b in headers]
            headers = dict(headers)
            if headers.get("Content-Encoding", "")=="gzip":
                #print "GZipped"
                data = self.__ungzip(data)
            res.close()
        except Exception, e:
            return False, str(e), None
        return True, data, headers
    
    
    def post(self, url, formDataList=[], includeExtraResults=False, data=None):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
            Return the server response data
        """
        return self.__putPost("POST", url, formDataList, includeExtraResults, data)
    
    def put(self, url, formDataList=[], includeExtraResults=False, data=None):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
            Return the server response data
        """
        return self.__putPost("PUT", url, formDataList, includeExtraResults, data)

    def __putPost(self, method, url, formDataList, includeExtraResults=False, data=None):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
            Return the server response data
        """
        contentType = None
        if data is None:
            # is this a multipart post or not
            fileTypes = [types.TupleType, types.FileType]
            dataTypes = [True for formName, data in formDataList if type(data) in fileTypes]
            multipart = dataTypes!=[]
            if multipart:
                contentType, data = self.__encodeMultipartFormdata(formDataList)
            else:
                contentType, data = self.__encodeFormdata(formDataList)
        return self.__putPostRequest(method, url, contentType, data, includeExtraResults)
    
    
    
    def __putPostRequest(self, method, url, contentType, data, includeExtraResults=False):
        """
            formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
            (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
            Return the server response data
        """
        host, path = urlsplit(url)[1:3]
        http = self.__HTTP(host)
        http.putrequest(method, path)
        if contentType:
            http.putheader("Content-Type", contentType)
        http.putheader("Content-Length", str(len(data)))
        http.endheaders()
        http.send(data)
        errCode, errMsg, headers = http.getreply()
        response = http.file.read()
        if includeExtraResults:
            return response, headers, errCode, errMsg
        else:
            return response
    
    
    def __encodeFormdata(self, formDataList):
        dataDict = dict(formDataList)
        data = urllib.urlencode(dataDict)
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

    def __ungzip(self, gzData):
        s = StringIO(gzData)
        gz = gzip.GzipFile(None, "rb", 9, s)
        data = gz.read()
        gz.close()
        s.close()
        return data





