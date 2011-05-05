
import os
import base64
import hmac
import httplib
import re
import sha
import sys
import time
import urllib
import urlparse
#import xml.sax
import xml.etree.ElementTree as et


""" """
# Note: requires that the environ variable 'EC2_DATA_PATH' points to
#           a folder that contains the following files:
#               'accessKeyId'  - containing the S3 aws_access_key_id
#               'secretAccessKey' - containing the S3 aws_secret_access_key


def readEc2File(file):
    path = os.environ["EC2_DATA_PATH"]
    if not path.endswith("/"):
        path += "/"
    f = open(path + file, "rb")
    data = f.read()
    f.close()
    return data.strip()


class S3Object(object):
    def __init__(self, data, metadata={}):
        self.data = data
        self.metadata = metadata


class Response(object):
    def __init__(self, httpResponse):
        self.httpResponse = httpResponse
        # you have to do this read, even if you don't expect a body, otherwise, the next request fails.
        self.body = httpResponse.read()
        self.status = httpResponse.status
        if httpResponse.status >= 300 and self.body:
            self.message = self.body
        else:
            self.message = "%03d %s" % (httpResponse.status, httpResponse.reason)


class GetResponse(Response):
    METADATA_PREFIX = "x-amz-meta-"
    def __init__(self, httpResponse):
        Response.__init__(self, httpResponse)
        responseHeaders = httpResponse.msg   # older pythons don't have getheaders
        metadata = self.__getAwsMetadata(responseHeaders)
        self.object = S3Object(self.body, metadata)
        #self.httpResponse.status, 200
        
    def __getAwsMetadata(self, headers):
        metadata = {}
        for hkey in headers.keys():
            if hkey.lower().startswith(self.METADATA_PREFIX):
                metadata[hkey[len(self.METADATA_PREFIX):]] = headers[hkey]
                del headers[hkey]
        return metadata




class S3(object):
    # regular: https://s3.amazonaws.com/bucket/key
    # subdomain: https://bucket.s3.amazonaws.com/key
    
    DEFAULT_HOST = "s3.amazonaws.com"
    #PORTS_BY_SECURITY = { True: 443, False: 80 }
    METADATA_PREFIX = "x-amz-meta-"
    AMAZON_HEADER_PREFIX = "x-amz-"
    
    __accessKeyId = readEc2File("accessKeyId")
    __secretAccessKey = readEc2File("secretAccessKey")
    __bucket = "ice-bucket"
    
    def __init__(self, accessKeyId=None, secretAccessKey=None, bucket=None, secure=True):
        if accessKeyId is not None:
            self.__accessKeyId = accessKeyId
        if secretAccessKey is not None:
            self.__secretAccessKey = secretAccessKey
        if bucket is not None:
            self.__bucket = bucket
        self.__secure = secure
        if secure:
            self.__protocol = "https"
            self.__port = 443
        else:
            self.__protocol = "http"
            self.__port = 80
        self.__host = "%s:%s" % (self.DEFAULT_HOST, self.__port)
        self.__server = "%s://%s:%s" % (self.__protocol, self.DEFAULT_HOST, self.__port)
        self.__expires_in = 60       # 60 Seconds 
        self.__expires = None
    
    @property
    def isSecure(self):
        return self.__secure
    
    def __getBucket(self):
        return self.__bucket
    def __setBucket(self, bucket):
        self.__bucket = bucket
    bucket = property(__getBucket, __setBucket)
    
    def createBucket(self, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        headers = {}
        response = Response(self.__makeRequest("PUT", bucket, "", {}, headers))
        return response.status==200, response.message
    
    def deleteBucket(self, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        response =  Response(self.__makeRequest("DELETE", bucket, "", {}, {}))
        status = response.status
        return status==200 or status==204, response.message
    
    def listMyBuckets(self):
        response = Response(self.__makeRequest("GET", "", "", {}, {}))
        if response.status != 200:
            return False, response.message
        else:
            xmlStr = response.body
            # remove the default namespace
            s = xmlStr.find("xmlns=")
            e = xmlStr.find('"', s + 10)
            xmlStr = xmlStr[:s] + xmlStr[e+1:]
            xml = et.XML(xmlStr)
            bList = []
            for b in xml.findall("Buckets/Bucket"):
                bList.append(b.find("Name").text)
            return True, bList
    
    def bucketExists(self, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        r = self.__makeRequest("HEAD", bucket, "", {}, {})
        return r.status==200
    
    def put(self, key, object, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        if not isinstance(object, S3Object):
            object = S3Object(object)
        queryArgs = {}
        headers = {}
        #headers = self.__mergeMeta({}, object.metadata)
        #result = self.__generateUrl("PUT", bucket, key, {}, headers)
        response = Response(
                self.__makeRequest("PUT", bucket, key, queryArgs, headers, object.data, object.metadata))
        return response.httpResponse.status==200, response.message
    
    def get(self, key, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        queryArgs = {}
        headers = {}
        response = GetResponse(self.__makeRequest("GET", bucket, key, queryArgs, headers))
        if response.httpResponse.status != 200:
            return False, response.message
        else:
            return True, response.object
    
    def delete(self, key, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        queryArgs = {}
        headers = {}
        response = Response(self.__makeRequest("DELETE", bucket, key, queryArgs, headers))
        return response.status==200, response.message
    
    def list(self, bucket=None):
        if bucket is None:
            bucket = self.__bucket
        options = {}
        headers = {}
        response = Response(self.__makeRequest("GET", bucket, "", options, headers))
        if response.status==200:
            class ContentItem(object):
                def __init__(self, content):
                    self.__name = content.find("Key").text
                    self.__lastModified = getTime(content.find("LastModified").text)
                    self.__size = int(content.find("Size").text)
                @property
                def name(self): return self.__name
                @property
                def lastModified(self): return self.__lastModified
                @property
                def size(self):  return self.__size
            xmlStr = response.body
            # remove the default namespace
            s = xmlStr.find("xmlns=")
            e = xmlStr.find('"', s + 10)
            xmlStr = xmlStr[:s] + xmlStr[e+1:]
            xml = et.XML(xmlStr)
            objectList = []
            for content in xml.findall("Contents"):
                objectList.append(ContentItem(content))
            xml.clear()
            return True, objectList
        else:
            return False, response.message
    
    
    def __makeRequest(self, method, bucket, key, queryArgs={}, headers={}, data="", metadata={}):        
        # build the path_argument string
        # add the ? in all cases since 
        # signature and credentials follow path args
        if bucket=="":
            path = "/%s" % (urllib.quote_plus(key))
        else:
            path = "/%s/%s" % (bucket, urllib.quote_plus(key))
        if len(queryArgs):
            path += "?" + self.__queryArgsHashToString(queryArgs)
        
        while True:
            if (self.__secure):
                connection = httplib.HTTPSConnection(self.__host)
                #print "secure server='%s'" % self.__host
            else:
                connection = httplib.HTTPConnection(self.__host)
                #print "non-secure server='%s'" % self.__host
            
            finalHeaders = self.__mergeMeta(headers, metadata);
            # add auth header
            self.__addAwsAuthHeader(finalHeaders, method, bucket, key, queryArgs)
            
            #print "host='%s', method='%s', path='%s', data='%s'" % \
            #        (self.__host, method, path, data)
            #for key in finalHeaders.keys():
            #    print " '%s':'%s'" % (key, finalHeaders[key])
            connection.request(method, path, data, finalHeaders)
            resp = connection.getresponse()
            if resp.status < 300 or resp.status >= 400:
                return resp
            
            # resp.staus = 300 to 399 (redirect)
            raise Exception("Received a redirect request! Currently cannot handle redirects!")
            # handle redirect
            location = resp.getheader('location')
            if not location:
                return resp
            # (close connection)
            resp.read()
            scheme, host, path, params, query, fragment \
                    = urlparse.urlparse(location)
            if scheme == "http":    is_secure = True
            elif scheme == "https": is_secure = False
            else: raise invalidURL("Not http/https: " + location)
            if query: path += "?" + query
            # retry with redirect
    
    def __addAwsAuthHeader(self, headers, method, bucket, key, queryArgs):
        if not headers.has_key('Date'):
            headers['Date'] = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        cString = self.__canonicalString(method, bucket, key, queryArgs, headers)
        encodedData = self.__encode(cString)
        headers['Authorization'] = \
            "AWS %s:%s" % (self.__accessKeyId, encodedData)
    
    
    def __mergeMeta(self, headers, metadata):
        finalHeaders = headers.copy()
        for k in metadata.keys():
            finalHeaders[self.METADATA_PREFIX + k] = metadata[k]
        return finalHeaders
    
    
##    def __generateUrl(self, method, bucket, key, queryArgs={}, headers={}):
##        expires = 0
##        if self.__expires_in != None:
##            expires = int(time.time() + self.__expires_in)
##        elif self.__expires != None:
##            expires = int(self.__expires)
##        else:
##            raise "Invalid expires state"
##        
##        canonicalStr = self.__canonicalString(method, bucket, key, queryArgs, headers, expires)
##        encodedCanonical = self.__encode(canonicalStr)
##        
##        url = "%s/%s/%s" % (self.__server, bucket, urllib.quote_plus(key))
##        
##        queryArgs['Signature'] = encodedCanonical
##        queryArgs['Expires'] = expires
##        queryArgs['AWSAccessKeyId'] = self.__accessKeyId
##        
##        url += "?%s" % self.__queryArgsHashToString(queryArgs)
##        
##        return url
    
    
    # builds the query arg string
    def __queryArgsHashToString(self, queryArgs):
        queryString = ""
        pairs = []
        for k, v in queryArgs.items():
            piece = k
            if v != None:
                piece += "=%s" % urllib.quote_plus(str(v))
            pairs.append(piece)
        return '&'.join(pairs)
    
    
    # computes the base64'ed hmac-sha hash of the canonical string and the secret
    # access key, optionally urlencoding the result
    def __encode(self, str, urlencode=False):
        b64_hmac = base64.encodestring(hmac.new(self.__secretAccessKey, str, sha).digest()).strip()
        if urlencode:
            return urllib.quote_plus(b64_hmac)
        else:
            return b64_hmac
    
    
    # generates the aws canonical string for the given parameters
    def __canonicalString(self, method, bucket, key="", queryArgs={}, headers={}, expires=None):
        interestingHeaders = {}
        for headerKey in headers:
            lk = headerKey.lower()
            if lk in ['content-md5', 'content-type', 'date'] or lk.startswith(self.AMAZON_HEADER_PREFIX):
                interestingHeaders[lk] = headers[headerKey].strip()
        
        # these keys get empty strings if they don't exist
        if not interestingHeaders.has_key('content-type'):
            interestingHeaders['content-type'] = ''
        if not interestingHeaders.has_key('content-md5'):
            interestingHeaders['content-md5'] = ''
        
        # just in case someone used this.  it's not necessary in this lib.
        if interestingHeaders.has_key('x-amz-date'):
            interestingHeaders['date'] = ''
        
        # if you're using expires for query string auth, then it trumps date
        # (and x-amz-date)
        if expires:
            interestingHeaders['date'] = str(expires)
        
        sortedHeaderKeys = interestingHeaders.keys()
        sortedHeaderKeys.sort()
        
        buf = "%s\n" % method
        for headerKey in sortedHeaderKeys:
            if headerKey.startswith(self.AMAZON_HEADER_PREFIX):
                buf += "%s:%s\n" % (headerKey, interestingHeaders[headerKey])
            else:
                buf += "%s\n" % interestingHeaders[headerKey]
        
        # append the bucket if it exists
        if bucket != "":
            buf += "/%s" % bucket
        
        # add the key.  even if it doesn't exist, add the slash
        buf += "/%s" % urllib.quote_plus(key)
        
        # handle special query string arguments
        if queryArgs.has_key("acl"):
            buf += "?acl"
        elif queryArgs.has_key("torrent"):
            buf += "?torrent"
        elif queryArgs.has_key("logging"):
            buf += "?logging"
        elif queryArgs.has_key("location"):
            buf += "?location"
        return buf
    


def getTime(timeStr):
    timeStr = timeStr[:timeStr.find(".")]
    ts = time.strptime(timeStr, "%Y-%m-%dT%H:%M:%S")
    t = time.mktime(ts)
    t -= time.timezone
    #s = time.ctime(t)
    return t


if __name__ == "__main__":
    print "Basic testing."
    s3 = S3()
    






