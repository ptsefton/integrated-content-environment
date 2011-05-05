
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
#import course_link_check
from urlparse import urlparse
import urllib
import types
from html_cleanup import HtmlCleanup
import re

class LocalhostLinkError(Exception): pass
class BadPageUrlError(Exception): pass


pluginName = "ice.function.check_links"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = check_links
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


# Check links
def check_links(self, callingFunction=None):
    path = self.packagePath
    self.isDocContentView = False
    if path!="":
        
        #__refresh(self, path)
        path = self.packagePath
        if path=="":
            path = self.path
        item = self.rep.getItem(path)
        result = item.render(force=False, skipBooks=True)
        clc = CourseLinkCheck(self.iceContext)
        if callingFunction:
            return clc.report(path)
        else:
            self["statusbar"] = "Check links"
            self["body"] = clc.report(path)
            self["title"] = "Check links"
    else:
        self._toc_htm_function()
        self["statusbar"] = "Error: Not within a package"
def isPackage(self):
    return self.isPackage
check_links.options={"toolBarGroup":"publish", "position":42, "postRequired":False,
                        "label":"Check _links", "title":"Check all links with a package",
                        "displayIf":isPackage}


# Repository usage:
#   .read(file)
#   .getMeta(file, "links")
#   
#   Also used by links class - which only passes it on to the link class
#   (link class usage:)
#       isValid if item.exists and item.isHidden==False
#   .itemExists(path)
#   .itemHidden(path)


class CourseLinkCheck:
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   
    # Methods:
    #   report(fromPath)
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.rep = iceContext.rep
        self.HtmlParser = HtmlCleanup

    def report(self, fromPath):
        #print "courceLinkCheck.report(fromPath=%s)" % fromPath
        if not fromPath.endswith("/"):
            fromPath += "/"
        packageItem = self.rep.getItem(fromPath) 
        packageRelPath = packageItem.relPath
        
        manifest = packageItem.getMeta("manifest")
        
        if manifest is None:
            print "Error: no manifest found in the '%s' package path: " % packageRelPath
            return
        
        allManifestItems = manifest.allManifestItems
        if allManifestItems != {} or allManifestItems is not None:
            ls = Links(self.iceContext, packageRelPath)
            for item in allManifestItems:
                itemRenditionName = item.renditionName
                path = self.__fs.join(packageRelPath, itemRenditionName)
                data = ""
                if (itemRenditionName.endswith(".htm") or \
                        itemRenditionName.endswith(".html")) and \
                        itemRenditionName!="toc.htm" and \
                        itemRenditionName!="default.htm":
                    iceItem = self.rep.getItemForUri(path)
                    name = iceItem.name
                    if name is None:
                        continue
                    linkDict = iceItem.getMeta("links")
                    
                    if linkDict is None:
                        linkDict = []
                        if iceItem.ext in [".html", ".htm"]:
                            #if it is a standard html/htm file, check if there is any links
                            linkDict = self.__checkLinkForHtm(iceItem)
                            #print "linkDict='%s'" % linkDict

                    try:
                        if linkDict is None:
                            linkDict = {}
                        elif type(linkDict) is types.ListType:
                            d = {}
                            for url, text in linkDict:
                                d[url] = text
                            linkDict = d
                        for url, linkText in linkDict.iteritems():
                            if url in ["../", "../toc.htm", "../default.htm"]:
                                pass
                            elif url.startswith("javascript:") or url.startswith("email:"):
                                pass
                            else:
                                ls.addLink(url, path, linkText)
                    except Exception, e:
                        print "Error (checklinks): for path '%s' - links is of type-'%s'" % (path, type(linkDict))
                        print "  links='%s'" % str(linkDict)
        return ls.htmlReportOnBadLinks()


    def __checkLinkForHtm(self, fileItem):
        links = []
        try:
            data = fileItem.read()
            if data is None:
                print "NONE - fileItem.relPath='%s', exists=%s" % (fileItem.relPath, fileItem.exists)
                return links
            html = self.HtmlParser.convertHtmlToXml(data)
            if html=="":
                return links
            xml = self.iceContext.Xml(html)
            
            refNodes = xml.getNodes("//*[@href]")
            
            for ref in refNodes:
                url = ref.getAttribute("href")                
                if url.startswith("http://localhost"):
                    url = self.__relativePath(url)
                elif not url.startswith("/"):
                    #other external
                    if not url.endswith("/"):
                        url = url + "/"
                linkText = ""
                nodes = ref.getNodes("*|text()")
                for node in nodes:
                    #ignore link especially from foot notes or endnotes
                    if node.getName() != "a":
                        linkText += str(node)
                links.append([url, linkText])
            xml.close()
        except Exception, e:
            print
            print self.iceContext.formattedTraceback(3)
            print "Error (checklinks): for path '%s' - '%s'" % (fileItem.relPath, str(e))
            return links
        return links

    
    def __relativePath(self, url):
        repPath = url.find("rep.")
        packagePath = url.find("packages")
        
        if repPath > -1:
            url = url[repPath:]
            urlSplit = url.split("/")
            curRepName = "rep." + self.rep.name
            if urlSplit[0] == curRepName:
                url = url[len(curRepName):]
        elif packagePath > -1:
            url = url[packagePath-1:]
        
        return url



class Link(object):
    count = 0
    def __init__(self, iceContext, fullUrl, page, linkText, packagePath=None):
        #print "Link fullUrl='%s', linkText='%s'" % (fullUrl, linkText)
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.rep = iceContext.rep
        self.url = fullUrl
        urlParts = urlparse(fullUrl)
        self.protocol = urlParts[0]
        self.domain = urlParts[1]
        self.urlPath = urlParts[2]
        self.anchor = urlParts[5]
        self.urlPath = urllib.unquote_plus(self.urlPath)
        if self.urlPath=="":
            self.urlPath=page
            self.url = page
        if not page.startswith("/"):
            raise BadPageUrlError()
        self.pages = {page:[linkText]}
        self.isValid = None
        if (self.protocol=="" or self.protocol=="http") and \
            (self.domain.startswith("localhost") or self.domain==""):
            self.isInternal = True
        else:
            self.isInternal = False
        if self.domain.startswith("localhost:"):
            # Why? - should have been changed to a relative link!
            #print "Warning: possible localhost link problem: url='%s', path='%s'" % (fullUrl, page)
            #print "  should have been changed to a relative link! (is the port # correct?)"
            pass
            #raise LocalhostLinkError("Link error: url='%s' page='%s' " % (fullUrl, page))
        if self.isInternal and not(self.urlPath.startswith("/")):
            self.urlPath = self.normalizeUrlPath(self.urlPath, page)
            self.url = self.urlPath
        self.externalPackageLink = False
        if packagePath is not None:
            maxPackageParents = len(page.split("/")) - len(packagePath.split("/"))
            if self.__getParents(fullUrl)>maxPackageParents:
                self.externalPackageLink = True
                #print " ExternalPackageLink"
#        print "link  url='%s', domain='%s'" % (self.url, self.domain)
#        print "  urlParts='%s'" % str(urlParts)
#        print "  isInternal=%s" % self.isInternal
#        print "  urlPath='%s', url='%s'" % (self.urlPath, self.url)
#        print
    
    
    def addPage(self, page, linkText):
        if self.pages.has_key(page):
            self.pages[page].append(linkText)
        else:
            self.pages[page] = [linkText]
    
    
    def normalizeUrlPath(self, urlPath, page):
        path = self.__fs.split(page)[0] 
        urlPath = self.__fs.normPath(self.__fs.join(path, urlPath)).replace("\\", "/")
        return urlPath
    
    
    def validate(self):
        if self.isValid==None:
            if self.isInternal:
                item = self.rep.getItemForUri(self.url) 
                if self.url.endswith(".htm") or self.url.endswith(".html"):
                    self.isValid = item.exists and not item.uriNotFound
                else:
                    #for those link that pointing to odt, pdf or other documents
                    self.isValid = item.exists 
                if self.isValid==False:
                    print
                    print "Invalid Link found! '%s'" % self.url
            else:
                #ToDo: check external links
                return True
        return self.isValid


    def __getParents(self, link):
        c = 0
        while link.startswith("../"):
            link = link[3:]
            c += 1
        return c


class Links(dict):
    def __init__(self, iceContext, packagePath=None, fileSystem=None):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.rep = iceContext.rep
        self.packagePath = packagePath
    
    
    def addLink(self, url, page, linkText):
        #print "addLink url='%s', linkText='%s'" % (url, linkText)
        l = Link(self.iceContext, url, page, linkText, packagePath=self.packagePath)
        
        #Note: after being change to url = l.url + ", " + linkText
        #the link will not displayed as:
        ## /packages/check_links/missing.htm in these pages:
            #* links.htm with the link text "http://localhost:8000/packages/check_links/missing.htm" and 
            #"http://localhost:8000/packages/check_links/missing.htm". 
        #This changes are to be made to support the anchor the badLink, the outPut will be two seperate
        #links
        url = l.url
        if type(l.url).__name__ == 'unicode':
            url = l.url.encode('utf8')
        url = "%s, %s" % (l.url.encode('utf8'), linkText) #  l.url + ", " + linkText

        
        if self.has_key(url):
            self[url].addPage(page, linkText)
        else:
            self[url] = l
    
    def checkLinks(self):
        self.invalid = []
        self.toOtherPackages = []
        for l in self.values():
            if not l.validate():
                self.invalid.append(l)
            if l.externalPackageLink:
                self.toOtherPackages.append(l)
    
    
    def htmlReportOnBadLinks(self):
        self.checkLinks()
        #if len(self.invalid) == 0:
        #    return "<div class='ice-report'><p>ok</p></div>"
        html = "<div class='ice-report'>\n<h1>Invalid internal links</h1>\n"
        if len(self.invalid)==0:
            html += "No invalid internal links"
        else:
            html += "<ol>\n"
            count = 1
            for l in self.invalid:
                html += "<li><a href='%s'>%s</a> in these pages: " % \
                    (self.textToHtml(l.url).replace("'", "&apos;"), self.textToHtml(l.url))
                if len(l.pages.items()):
                    html += "<ul>"
                    for p, linkText in l.pages.items():
                        #just get the first linkText for anchor
                        eLinkText = '"' + linkText[0] + '"'
                        linkText = '"' + '", "'.join(linkText) + '"'        # list to quoted csv list
                        linkText = " and".join(linkText.rsplit(",", 1))     # replace the last ',' with ' and'
                        eLinkText = self.iceContext.xmlEscape(eLinkText)
                        href = "%s?linkText=%s&amp;linkHref=%s" % \
                                (p, eLinkText, l.url)
                        href = "'%s'" % (href.replace("'", "&apos;"))
                        text = "with the link text %s. " % linkText
                        html += "<li><a href=%s>%s</a> %s</li>" % \
                            (href, self.textToHtml(self.__fs.split(p)[1]), text)
                    html += "</ul>"
                html += "</li>\n"
            html += "</ol>"

        if False:
        #if len(self.toOtherPackages)>0:
            html += "<h1>Warning: links to other packages (these will be invalid when exported!)</h1>"
            html += "<ol>\n"
            for l in self.toOtherPackages:                
                html += "<li><a href='%s'>%s</a> in these pages: " % \
                    (self.textToHtml(l.url).replace("'", "&apos;"), self.textToHtml(l.url))
                html += "<ul>"
                for p, linkText in l.pages.items():
                    linkText = '"' + '", "'.join(linkText) + '"'        # list to quoted csv list
                    linkText = " and".join(linkText.rsplit(",", 1))     # replace the last ',' with ' and'
                    eLinkText = linkText
                    text = "with the link text %s. " % linkText
                    href = "%s?linkText=%s&amp;linkHref=%s" % \
                            (self.textToHtml(p), eLinkText, self.textToHtml(l.url))
                    href = "'%s'" % (href.replace("'", "&apos;"))
                    html += "<li><a href=%s>%s</a> %s</li>" % \
                        (href, self.textToHtml(self.__fs.split(p)[1]), text)
                html += "</ul></li>\n"
            html += "</ol>"
        html += "\n<h1>External links</h1>\n"
        
        externalLinks = ""
        html += "<ol>\n"
        for l in self.keys():
            if not self[l].isInternal:
                url = self[l].url
                url =  url[:url.find("?embedmedia")]
                externalLinks += "<li><a href='%s'>%s</a> in these pages: <ul>" % \
                    (self.textToHtml(url), self.textToHtml(self[l].url))
                for lk, linkText in self[l].pages.items():
                    eLinkText = '"' + linkText[0] + '"'
                    linkText = '"' + '", "'.join(linkText) + '"'        # list to quoted csv list
                    linkText = " and".join(linkText.rsplit(",", 1))     # replace the last ',' with ' and'
                    eLinkText = linkText
                    text="with the link text %s. " % linkText
                    href = "'%s?linkText=%s&amp;linkHref=%s'" % (self.textToHtml(lk), self.textToHtml(eLinkText), self.textToHtml(self[l].url))
                    ##
                    #if self[l].test:
                    text = re.sub("\\<img .*?\\/\\>", "[image]", text)
                    x = "<li><a href=%s>%s</a> %s</li>" % (href, self.textToHtml(self.__fs.split(lk)[1]), text)
                    ##
                    externalLinks += x
                    #externalLinks += "<li><a href=%s>%s</a> %s</li>" % \
                    #    (href, self.textToHtml(self.__fs.split(lk)[1]), text)
                externalLinks += "</ul></li>\n"
        if externalLinks=="":
            html += "No external links found"
        else:
            html += externalLinks
        html += "</ol>"
        html += "\n</div>"
        return html
    
    def textToHtml(self, text):
        return self.iceContext.textToHtml(text)











