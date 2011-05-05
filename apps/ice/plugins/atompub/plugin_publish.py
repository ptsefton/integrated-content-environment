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

""" This plugin is used to publish the atom feed
This plugin will call ice.atompub plugin
@requires: plugins/atompub/plugin_atompub.py
"""

import sys
import atom
from atomsvc import APP_NS
import urllib
import re

pluginName = "ice.atom.publish"
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
    pluginClass = AtomPublish
    pluginInitialized = True
    #path = iceContext.fs.split(__file__)[0]
    AtomPublish.APP_NS = APP_NS
    AtomPublish.APP_NAMESPACE = atom.APP_NAMESPACE
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



class AtomPublish(object):
    """ Base class for AtomPublish to publish Atom feed
    """
    InvalidUrlException = InvalidUrlException
    RequestException = RequestException
    BadAuthentication = BadAuthentication

    @staticmethod
    def parseEntry(entry):
        """ to get the feed from the given entry
        @param entry: Entry
        @type entry: String
        @rtype: ElementTree._Element, or xml_wrapper.ElementWrapper
        @return: atom entry
        """
        return atom.EntryFromString(entry)

    def __init__(self, iceContext, filename, getMedia = None, saveResponse = None, output = None):
        """ Atom Publish Constructor method
        @param iceContext: current ice context
        @type iceContext: IceContext
        @param filename: filename to be published
        @type filename: String
        @param getMedia: method to get the media list
        @type getMedia: python method
        @param saveResponse: method to save the response returned by server
        @type saveResponse: python method
        @param output: standard output
        @type output: standard output
        """
        self.iceContext = iceContext
        self.__filename = filename
        self.__getMedia = getMedia
        self.__saveResponse = saveResponse
        if output is None:
            output = sys.stdout
        self.__output = output
        self.__fs = self.iceContext.fs




    def publish(self, content, options, entryXml = None):
        """ to publish the atom feed to the server through ice.atompub plugin
        @param content: Content to be publised
        @type content: String
        @param options: options list
        @type options: dict
        @param entryXml: Optional entry xml
        @type entryXml: atom element

        @rtype: (String, String, String)
        @return: success status, response and publishedUrl
        """
        ##
#        content = self.__hackContent(content)
        #raise Exception("Testing")
        ##
        url = options.get("atompuburl", None)
        authType = options.get("authtype", "None").lower()
        username = options.get("username", None)
        password = options.get("password", None)
        author = options.get("author", username)
        title = options.get("title", None)
        summary = options.get("summary", title)
        categories = options.get("categories","")
        urlTitle = urllib.unquote(options.get("urlencodedtitle", ""))
        urlSummary = urllib.unquote(options.get("urlencodedsummary", ""))
        if urlTitle != "":
            title = urlTitle
        if urlSummary!="":
            summary = urlSummary
        draft = options.get("draft", "True")
        if type(draft) == bool:
            draft = str(draft).lower()
        elif draft.strip() == "on":
            draft = "true"
        if type(categories) == str:
            categories = categories.split(";")
        if categories ==[]:
            categories[0]="Uncategorized"
        draft = draft.lower() == "true"
        print "*** categories='%s'" % categories
        try:
            plugin = self.iceContext.getPlugin("ice.atompub")
            if plugin is None:
                raise Exception("Cannot find plugin 'ice.atompub'!")
            iceAtomPub = plugin.pluginClass(url, authType, username, password)
            print "*** Published ***"
            content = self.__processMedia(iceAtomPub, content)
            content = self.__hackContent(content)
            successes = []
            responses = []
            publishedUrls = []
            for category in categories:
                response = iceAtomPub.post(author, title, summary, content, category, draft, entryXml)
                #response = self.__cleanupResponse(response)
                publishedUrl = self.__getPublishedUrl(response, draft)
                success = response is not None
                #if there is not atompub. then html is returned
                if publishedUrl == None and not draft:
                    success = False
                    response = "Unexpected server response."
                print "publishedUrl : ", publishedUrl
                print "success: ", success
                if success:
                    if callable(self.__saveResponse) and authType != "blogger":
                        publishedCategory = self.__getPublishedCategory(response)
                        self.__saveResponse(response,publishedCategory)
                    response = "Published OK"
                successes.append(success)
                responses.append(response)
                publishedUrls.append(publishedUrl)
            return successes, responses, publishedUrls
        except Exception, e:
            self.__output.write("Failed to publish: %s \n" % e)
            raise e

    def __hackContent(self, content):
        """ Hack the content for embedded object
        @param content: content to be published
        @type content: String
        @rtype: String
        @return: content
        """
        et = self.iceContext.ElementTree
        xml = et.XML(content)
#        print
#        print et.tostring(xml)
        # add parents
        def addParent(e):
            for c in e.findall("*"):
                c.parent = e
                addParent(c)
        addParent(xml)
        divs = xml.findall(".//div")
        divs = [div for div in divs if div.get("class", "")=="embedded-html"]
        for div in divs:
            # get index of div
            pos = div.parent.getchildren().index(div)
            e = et.Element("span", xxxxx="*********")
            div.parent.insert(pos, e)
            div.parent.remove(div)
#        print
        content = et.tostring(xml)
#        print content
#        print
        return content

    def __processMedia(self, iceAtomPub, content):
        """ process the Media url found in the content to be published
        e.g. all files in _files folder
        @param iceAtomPub: Current atom feed
        @type iceAtomPub: IceAtomPub
        @param content: content to be published
        @type content: String
        @rtype: String
        @return: content
        """
        # get media and upload them
        _, baseName, _ = self.__fs.splitPathFileExt(self.__filename)
        if iceAtomPub.supportsMedia() and callable(self.__getMedia):
            mediaList = self.__getMedia()
            print "mediaList='%s'" % str(mediaList)
            for mediaEntry in mediaList:
                try:
                    mediaData = self.__getMedia(mediaEntry)
                    _, mediaTitle, ext = self.__fs.splitPathFileExt(mediaEntry)
                    ## HACK just use image/(ext) instead of proper mimetype so wordpress accepts it
                    #mimeType = "image/" + ext[1:]
                    if self.iceContext.MimeTypes.has_key(ext):
                        mimeType = self.iceContext.MimeTypes[ext]
                    if mimeType == "application/pdf":
                        #for wordpress, the pdf has to pretend to be the image. 
                        mimeType = "image/pdf"  
                    #print "mimetype:",mimeType
                    #print "postMedia(mediaTitle='%s', mediaData=%s(len), mimeType='%s')" % (mediaTitle, len(mediaData), mimeType)
                    mediaResponse = iceAtomPub.postMedia(mediaTitle, mediaData, mimeType)
                    mediaEntryXml = atom.EntryFromString(mediaResponse)
                    src = "%s_files/%s" % (baseName, mediaEntry)
                    #print " src='%s'" % src
                    if content.find(src) == -1:
                        # most likely not an image
                        src = mediaEntry
                        print "did not find content!"
                    newSrc = mediaEntryXml.content.src
                    if newSrc is None or newSrc=="":
                        raise Exception("Unknown content @src=None)")
                    content = content.replace(src, newSrc)
                    print "Uploaded %s to %s" % (src, newSrc)
                except Exception, e:
                    self.__output.write("Failed to upload image: %s (%s)\n" % (mediaEntry, e))
            #print "----pp"
        return content

    def __getPublishedCategory(self,response):
        """ To get the published category
        @param response: Response returned by server
        @type response: String
        @rtype: String
        @return: category in which the content is published
        """
        publishedCategory = "Uncategorized"
        try:
            response = unicode(str(response), "utf-8")
            entry = atom.EntryFromString(response)
            if entry != None:
                publishedCategory=  entry.category[0].term
        except Exception, e:
            self.__output.write("Failed parsing response: %s\n" % str(e))
            #self.__output.write(" response='%s'\n" % response)
        return publishedCategory
    

    def __getPublishedUrl(self, response, draft):
        """ To get the published url
        @param response: Response returned by server
        @type response: String
        @param draft: type of the content
        @param draft: Boolean
        @rtype: String
        @return: url where the content is published
        """
        publishedUrl = None
        try:
            response = unicode(str(response), "utf-8")
            entry = atom.EntryFromString(response)
            if entry != None:
                altLink = entry.GetAlternateLink()
                if altLink is None:
                    # no alternate link so just get the first link
                    for link in entry.link:
                        if link.rel == None:
                            altLink = link
                            break
                if not draft and altLink is not None:
                    publishedUrl = altLink.href
        except Exception, e:
            self.__output.write("Failed parsing response: %s\n" % str(e))
            #self.__output.write(" response='%s'\n" % response)
        return publishedUrl
    
