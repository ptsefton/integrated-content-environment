
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
import string
import types

pluginName = "ice.relativeLinker"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = RelativeLinker
    pluginInitialized = True
    return pluginFunc


class RelativeLinker:
    # Constructor:
    #   __init__(iceContext, baseUrl)
    # Properties:
    #   baseUrl
    #   
    # Methods:
    #   getRelativeLink(relativeTo, url)
    #   makeUrlRelativeTo(url, relativeTo)
    #   makeRelative(xml, path)
    #   nullLinks(xml, path)
    #   
    
    def __init__(self, iceContext, baseUrl):
        self.iceContext = iceContext
        if not baseUrl.endswith("/"):
            baseUrl += "/"
        self.baseUrl = baseUrl
        #self.urlRoot = self.iceContext.urlRoot     # not setup yet!
    
    
    def getRelativeLink(self, relativeTo, url):     # Only by plugin_bookEditor.py
        # if it does not starts with the baseUrl and it has a base then it is absolute.
        url1 = url.split("?")[0]
        local = self.iceContext.isNetlocLocal(url1)
        
        if not local and not url1.startswith(self.baseUrl) and url1.find(":") > 0:    # "://" or "mailto:"
            return url
        
        if local:
          url =  self.__makeUriRelativeTo(url, relativeTo)
          return url 
        elif url.startswith(self.baseUrl):        # if url startswith baseUrl then it is an absolute url
            url = url[len(self.baseUrl)-1:]
        elif not url.startswith("/"):           # else if it does NOT startwith a / then it is already a relative link
            return url
        
        url = self.__filterRepName(url)
        result = self.makeUrlRelativeTo(url, relativeTo)
        return result
    
    
    def makeUrlRelativeTo(self, url, relativeTo):
        """ Makes the given 'url' argument into a url that is relative to the 'relativeTo' arguemnt.
            Note: will raise an exception if the relativeTo url argument is not an absolute url."""
        # Note: does not use self.baseUrl at all.  (can be made static if required)
        relTo = relativeTo.replace("//", "/")
        relTo = self.iceContext.fs.split(relTo)[0]
        if relTo.startswith("/"):
            relTo = relTo[1:]
        else:
            raise Exception("Not relative to a root directory")
        if relTo=="":
            relativeParts = []
        else:
            relativeParts = relTo.split("/")
        
        if url.startswith("/"):
            url = url[1:]
        else:
            # This url is just appended to the current url
            # therefore it is already relative
            return url
        urlParts = url.split("/")
        
        if relativeParts==urlParts:
            return "."
        
        # catch cases where link is to its own parent
        if url==relTo:
            return "../" + self.iceContext.fs.split(relTo)[1]
        
        while(len(urlParts)>0 and len(relativeParts)>0):
            if urlParts[0]==relativeParts[0]:
                urlParts.pop(0)
                relativeParts.pop(0)
            else:
                break
        
        if len(relativeParts) == 0:
            relativeUrl = ""            # same as "./"
        else:
            relativeUrl = "../" * len(relativeParts)
        relativeUrl += string.join(urlParts, "/")
        return relativeUrl
    
    
    def makeRelative(self, xml, path):
        #print
        #print "makeRelative()"
        #print "  path='%s'" % path
        #
        if type(xml)==types.StringType:
            dom = self.iceContext.Xml(xml)
        elif isinstance(xml, self.iceContext.Xml):
            dom = xml
        else:
            raise Exception("The xml argument must be a xml string or an xml object!")

        dom.addNamespaceList([("x", "http://www.w3.org/1999/xhtml")])
        urlNodes = dom.getNodes("//@href[not(ancestor::*/@class='searchResults')] | \
                                 //@src | \
                                 //object/@data | \
                                 //object/param[@name='src' or @name='movie' or @name='url']/@value | \
                                 //applet/param[@name='load' or @name='filename']/@value | \
                                 //applet/@archive | \
                                 //x:object/@data | \
                                 //x:object/x:param[@name='src' or @name='movie' or @name='url']/@value | \
                                 //x:applet/x:param[@name='load' or @name='filename']/@value | \
                                 //x:applet/@archive")
        self.__processNodes(path, urlNodes)
        
        if type(xml)==types.StringType:
            result = str(dom.getRootNode())
            dom.close()
        else:
            result = dom
        return result
    
    
    def nullLinks(self, xml, path, hrefNodes=None):
        if type(xml) is types.StringType:
            dom = self.iceContext.Xml(xml)
        elif isinstance(xml, self.iceContext.Xml):
            dom = xml
        else:
            raise Exception("The xml argument must be a xml string or an xml object!")
        
        # Replace link to self and change the link to bold text
        if hrefNodes is None:
            hrefNodes = dom.getNodes("//*[local-name()='a'][@href='%s']" % self.__escapeXml(path))
        # Replace link text with bold text (removing the link)
        self.__nullLinks(dom, hrefNodes)
            
        if type(xml)==types.StringType:
            result = str(dom.getRootNode())
            dom.close()
        else:
            result = dom
        return result
    
    
    def __nullLinks(self, dom, hrefNodes):
        for hrefNode in hrefNodes:
            newNode = dom.createElement("span", style="font-weight:bold;")
            span = dom.createElement("span")     #, elementContent=selfHrefNode.getContent()
            span.addChildren(hrefNode.getChildren())
            span.setAttribute("class", "current-url")
            newNode.addChild(span)
            hrefNode.replace(newNode)
            hrefNode.delete()
    
    
    def __processNodes(self, relativeTo, nodes):
        relativeToPaths = self.__getRelativeToPaths(relativeTo)
        #print "  relativeToPaths='%s'" % relativeToPaths
        for node in nodes:
            url = node.getContent()
            if relativeTo is None:
                nUrl = self.makeUrlRelativeTo(url, self.baseUrl)
            else:
                nUrl = self.__makeUriRelativeTo(url, relativeTo, relativeToPaths)
                #print 'url: %s and nUrl: %s' % (url, nUrl)
            node.setContent(nUrl)
        return nodes
    
    
    def __makeUriRelativeTo(self, uri, relativeToUri, relativeToPaths=None):    #New
        #print 'url: %s relativeToUri: %s' % (uri, relativeToUri)
        if relativeToUri=="/":
            if uri.startswith("/"):
                nUri = uri.lstrip("/")
                if nUri=="":
                    nUri = "."
                return nUri
        uriParts = list(self.iceContext.urlparse(uri))
        uriPath = uriParts[2]
        if uriPath=="":
            return uri
        if uriParts[0]!="" and uriParts[0]!="http":
            return uri
        uriPath = self.iceContext.normalizePath(uriPath)
        if uriParts[2].endswith("/") and not uriPath.endswith("/"):
            uriPath += "/"
        # urlRoot
        if uriPath.startswith("/rep."):
            uriPath = "/" + uriPath.split("/", 2)[-1]
            #if uriPath.startswith(self.iceContext.urlRoot):
            #    uriParts[0], uriParts[1] = "", ""
            #    uriPath = uriPath[len(self.iceContext.urlRoot)-1:]
        #
        #print "  %s - %s" % (uriParts[1], self.iceContext.isNetlocLocal(uriParts[1]))
        #if uriParts[1].startswith("localhost") or uriParts[1].startswith("127.0.0.1"):
        #isLocal = self.iceContext.isNetlocLocal(uriParts[1])
        isLocal = self.iceContext.isLocalUrl(uri)
        if isLocal:
            uriParts[0], uriParts[1] = "", ""
        if uriParts[0]=="" and uriPath.startswith("/"):     # OK make relative
            relPath = ""
            done = False
            if relativeToPaths is None:
                relativeToPaths = self.__getRelativeToPaths(relativeToUri)
            for p in relativeToPaths:
                if uriPath == p:
                    relPath += "."
                    done = True
                    break
                elif uriPath.startswith(p):
                    relPath += uriPath[len(p):]
                    done = True
                    break
                else:
                    relPath += "../"
            if not done:
                relPath += uriPath[1:]
            #print "- makeRelative '%s' - '%s'" % (uriPath, relPath)
            uriPath = relPath
        uriParts[2] = uriPath
        nUri = self.iceContext.urlunparse(uriParts)
        return nUri
    
    
    def __getRelativeToPaths(self, relativeToUri):                              # New
        """ Note: will raise an exception if the relativeToUri argument is not an absolute url."""
        if not relativeToUri.startswith("/"):
            raise self.iceContext.IceException("relativeToUri argument is not an absolute path!")
        if relativeToUri.endswith("/"):
            relativeToUri = self.iceContext.normalizePath(relativeToUri)
            if not relativeToUri.endswith("/"):
                relativeToUri += "/"
        else:
            relativeToUri = self.iceContext.normalizePath(relativeToUri)
        if not relativeToUri.endswith("/"):
            relativeToUri = self.iceContext.fs.split(relativeToUri)[0]
            if not relativeToUri.endswith("/"):
                relativeToUri += "/"
        relativeToParts = relativeToUri.strip("/").split("/")
        prev = "/"
        relativeToPaths = []
        for part in relativeToParts:
            prev += part
            if not prev.endswith("/"):
                prev += "/"
            relativeToPaths.insert(0, prev)
        return relativeToPaths
    
    
    def __escapeXml(self, s):
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        return s.replace("'", "&apos;")
    
    
    def __filterRepName(self, url):
        if url.startswith("/rep."):
            startPos = url.find("/", 1)
            if startPos > -1:
                url = url[startPos:]
            else:
                url = "/"
        return url











