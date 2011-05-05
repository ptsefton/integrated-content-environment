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

""" Atompub plugin to process atom feed
@requires: atomsvc   from plugins/atompub/atomsvc.py
@requires: base64, os, urllib, urllib2, urlparse, sgmllib, atom
"""

import atomsvc

import base64, os
import urllib, urllib2
from urlparse import urlparse
from sgmllib import SGMLParser

import atom
from atom.service import AtomService


pluginName = "ice.atompub"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceAtomPub
    pluginInitialized = True
    return pluginFunc


class InvalidUrlException(Exception):
    """ Base class InvalidUrlException
    """
    pass

class RequestException(Exception):
    """ Base class RequestException
    """
    pass

class BadAuthentication(Exception):
    """ Base class BadAuthentication
    """
    pass

class AtomLinkParser(SGMLParser):
    """ Base class AtomLinkParser """
    def reset(self):
        """ reset method to reset SGMLParser and url
        @rtype: void 
        """
        SGMLParser.reset(self)
        self.url = None
    
    def start_link(self, attrs):
        """ start_link method setting the first found href link to the url
        @param attrs: attribute lists
        @type attrs: list
        @rtype: void
        """
        postLink = [v for k, v in attrs if k == "rel" and v in ["service.post", "introspection"]]
        if len(postLink) > 0:
            href = [v for k, v in attrs if k == "href"]
            self.url = href[0]

class IceAtomPub(object):
    """ Base class AtomLinkParser """
    InvalidUrlException = InvalidUrlException
    RequestException = RequestException
    BadAuthentication = BadAuthentication
    def __init__(self, url, auth, username, password):
        """ IceAtomPub Constructor method
        @param url: url where the feed is going to be posted
        @type url: String
        @param auth: The authentication method e.g. basic/blogger
        @type auth: String
        @param username: Username to login to the url
        @type username: String
        @param password: Password used for login to the url
        @type password: String
        @rtype: void
        """
        self.__http_proxy = os.environ.get("http_proxy")
        self.__auth = auth.lower()
        self.__username = username
        self.__password = password
        self.__setup(url)
    
    def __setup(self, url):
        """ to setup the connection to the server
        @param url: url where the feed is going to be posted
        @type url: String
        @rtype: void
        """
        self.__checkNoProxy(url)
        # initialise the atom service
        netloc = urlparse(url)[1]
        self.service = None
        self.authHeaders = {}
        self.entryUri = url
        self.atomService = AtomService(server = netloc)
        if self.__auth == "basic":
            self.atomService.UseBasicAuth(self.__username, self.__password)
            print " basicAuth login"
        elif self.__auth == "blogger":
            self.__googleBloggerLogin(self.__username, self.__password)
            print " blogger login"
        self.__getServiceUrls(url, self.__username, self.__password)
        self.__resetProxy()
    
    def supportsMedia(self):
        """ 
        @rtype: boolean
        @return: boolean if has service
        """
        return self.hasServiceDocument
    
    @property
    def hasServiceDocument(self):
        """ has service property
        @rtype: void
        """
        return self.service != None
    
 
        
    def post(self, author, title, summary, content, category, draft, entryXml=None):
        """ to post the content to the server
        @param author: Author name
        @type author: String
        @param title: Title of the content
        @type title: String
        @param summary: Summary of the content
        @type summary: String
        @param content: Content 
        @type content: String
        @param draft: Type of the document:
        @type draft: boolean
        @param entryXml: extra entry
        @type entryXml: String
        @rtype: String
        @return: response result from server
        """
        entry, httpResponse = self.__post(author, title, summary, content, category, draft, entryXml)
        # handle the server response
        status = httpResponse.status
        if status == 302:
            # Moved Temporarily -  try post to the new URL
            location = httpResponse.getheader("Location", None)
            if location is not None:
                print "302: Reposting to %s..." % location
                self.__setup(location)
                entry, httpResponse = self.__post(author, title, summary, content, category, draft, entryXml)
                status = httpResponse.status
        if not (status == 200 or status == 201):
            raise RequestException, "%s %s" % (status, httpResponse.reason)
        response = httpResponse.read()
        contentLength = len(response)
        if contentLength <= 0:
            response = entry.ToString()
        return response
    
    def __post(self, author, title, summary, content, category, draft, entryXml):
        """ to post the content to the server
        @param author: Author name
        @type author: String
        @param title: Title of the content
        @type title: String
        @param summary: Summary of the content
        @type summary: String
        @param content: Content 
        @type content: String
        @param draft: Type of the document:
        @type draft: boolean
        @param entryXml: extra entry
        @type entryXml: String
        
        @rtype: (Atom Entry, String)
        @return: entry, httpResponse
        """
        # create/update the atom entry
        if entryXml == None:
            entry = atom.Entry()
            entryUri = self.entryUri
            
        else:
            entry = atom.EntryFromString(entryXml)
            entryUri = entry.GetEditLink().href
        entry.author = [atom.Author(text = author)]
        entry.title = atom.Title(text = title)
        entry.summary = atom.Summary(text = summary)
        entry.content = atom.Content(content_type = "html",
                                     text = unicode(content, "utf-8"))
        if category!="":
            entry.category = atom.Category(term=category)
        if draft:
            entry.control = atom.Control(draft = atom.Draft(text = "yes"))
        else:
            entry.control = atom.Control(draft = atom.Draft(text = "no"))
        # setup the http headers for authorisation
        extraHeaders = {"Slug": title}
        extraHeaders.update(self.authHeaders)
        # use POST or PUT depending on whether it is a new entry or an update
        if entryXml != None:
            publishFunc = self.atomService.Put
        else:
            publishFunc = self.atomService.Post
        self.__checkNoProxy(entryUri);
        httpResponse = publishFunc(data = entry, uri = entryUri,
                                   extra_headers = extraHeaders)
        self.__resetProxy()
        return entry, httpResponse
    
    def postMedia(self, title, data, type, extraHeaders={}, mediaUri=None):
        """ to post the media to the server
        @param title: Title of the content
        @type title: String
        @param data: Content 
        @type data: String
        @param type: type of the content 
        @type type: String
        @param extraHeaders: Extra header that needs to be included
        @type extraHeaders: dict
        @param mediaUri: Uri for the media
        @type mediaUri: String
        
        @rtype: String
        @return: response from server
        """
        if mediaUri is None:
            if self.service is None:
                print "Atom service document not specified. Media not supported."
                return None
            mediaUri = self.service.getUrlForType(type)
            if mediaUri is None:
                print "No collection accepts MIME type: %s" % type
                return None
        extraHeaders.update({"Slug": title})
        extraHeaders.update(self.authHeaders)
        self.__checkNoProxy(mediaUri);
        #print "post len(data)=%s, uri=%s, extra_headers=%s, content_type=%s" % \
        #        (len(data), mediaUri, extraHeaders, type)
        httpResponse = self.atomService.Post(data=data, uri=mediaUri,
                        extra_headers=extraHeaders, content_type=type)
        self.__resetProxy()
        status = httpResponse.status
        if not (status==200 or status==201):
            print "HTTP Response:"
            print httpResponse.read()
            raise RequestException, "%s %s" % (status, httpResponse.reason)
        response = httpResponse.read()
        return response
    
    
    def __getServiceUrls(self, url, username, password):
        """ Get the available service url
        @param url: url where the feed is going to be posted
        @type url: String
        @param username: Username to login to the url
        @type username: String
        @param password: Password used for login to the url
        @type password: String
        
        @raise BadAuthentication: if wrong userid/password
        @rtype: void
        """
        # check if this is a regular HTML page or Atom enabled server
        try:
            request = urllib2.Request(url)
            auth = base64.encodestring('%s:%s' % (username, password))[:-1]
            if self.authHeaders.has_key("Authorization"):
                #for Google blogger
                request.add_header("Authorization",self.authHeaders["Authorization"])
            else: 
                request.add_header("Authorization", "Basic %s" % auth)
            request.add_header("Accept-encoding", "gzip")
            fp = urllib2.urlopen(request)
            # read the response body
            data = fp.read()
            fp.close()
            # check for compressed data
            if fp.headers.get('Content-Encoding') == "gzip":
                import gzip, StringIO
                compressed = StringIO.StringIO(data)
                gzipper = gzip.GzipFile(fileobj = compressed)
                data = gzipper.read()
            contentType = fp.headers['Content-Type']
            if contentType.startswith("application/atom+xml"):
                # Valid Atom URL
                self.entryUri = url
            elif contentType.startswith("application/atomsvc+xml"):
                # Valid Atom Service document
                self.service = atomsvc.AtomPubService(data)
                if self.service != None:
                    self.entryUri = self.service.getUrlForEntry()
            elif contentType.startswith("text/html"):
                # Regular HTML - check for service.post link
                parser = AtomLinkParser()
                parser.feed(data)
                parser.close()
                if parser.url != None:
                    # 2nd pass to check for a service document
                    self.entryUri = parser.url
                    self.__getServiceUrls(parser.url, username, password)
        except urllib2.HTTPError, e:
            # error connecting to specified url. this could be because the doc
            # has already been posted as a draft or is simply an invalid url.
            # in either case, just ignore and use the url as-is
            print "Warning: Atom URL detection could not be performed, no media support."
            print "         Failed to connect to %s (%s)" % (url, e)
            if e.code == 401:
                raise BadAuthentication, "Incorrect username or password"
    
    def __googleBloggerLogin(self, username, password):
        """ Logging to google blogger
        @param username: Username to login to the url
        @type username: String
        @param password: Password used for login to the url
        @type password: String
        
        @raise BadAuthentication: if wrong userid/password
        @rtype: void
        """
        authUri = "https://www.google.com"
        params = {"Email": username,
                  "Passwd": password,
                  "accountType": "HOSTED_OR_GOOGLE",
                  "service": "blogger",
                  "source": "USQ-ICE-2.0"}
        requestBody = urllib.urlencode(params)
        try:
            connection, _ = self.atomService._PrepareConnection(authUri)
            connection.putrequest("POST", "/accounts/ClientLogin")
            connection.putheader("Content-Type", "application/x-www-form-urlencoded")
            connection.putheader("Content-Length", str(len(requestBody)))
            connection.endheaders()
            connection.send(requestBody)
            response = connection.getresponse()
        except:
            headers = {"Content-Type":"application/x-www-form-urlencoded", "Content-Length":str(len(requestBody))}
            authUri = authUri + "/accounts/ClientLogin"
            response = self.atomService.http_client.request("POST", authUri, requestBody, headers)
        if response.status == 200:
            body = response.read()
            lines = body.splitlines()
            if len(lines)!= 0 :
                for line in lines:
                    if line.startswith("Auth="):
                        print "ere"
                        self.authHeaders["Authorization"] = \
                            "GoogleLogin auth=%s" % line.lstrip("Auth=")
        elif response.status == 403:
            body = response.read()
            for line in body.splitlines():
                if line.startswith("Error="):
                    errorLine = line
            if errorLine == "Error=BadAuthentication":
                raise BadAuthentication, "Incorrect username or password"
    
    def __checkNoProxy(self, url):
        """ to check for the proxy and disable if necessary
        @param url: url where the feed is going to be posted
        @type url: String
        @rtype: void
        """
        #FIXME assumes only 1 host
        no_proxy = os.environ.get("no_proxy")
        if no_proxy is not None:
            no_proxies = no_proxy.split(",")
            for noproxy in no_proxies:
                noproxy = noproxy.strip()
                index = url.find(noproxy)
                if index > -1:
                    # disable proxy settings for urllib
                    proxy_support = urllib2.ProxyHandler({})
                    opener = urllib2.build_opener(proxy_support)
                    urllib2.install_opener(opener)
                    if os.environ.has_key("http_proxy"):
                        print "disabling proxy..."
                        del os.environ["http_proxy"]
                    break

    def __resetProxy(self):
        """ to reset the proxy
        @rtype: void
        """
        urllib2.install_opener(None)
        if self.__http_proxy is not None:
            print "resetting proxy to %s..." % self.__http_proxy
            os.environ["http_proxy"] = self.__http_proxy
    
