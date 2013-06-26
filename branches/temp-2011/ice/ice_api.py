#!/usr/bin/python
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

import re

class IceServices(object):
    CONVERT_PATH = "/api/convert"
    CONVERT_PATH_SLASH = "/api/convert/"
    SESSION_ID = "sessionid"
    
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__extToPlugin = {}
        self.__pluginToExts = {}
    
    
    def addServicePlugin(self, ext, servicePlugin):
        self.__extToPlugin[ext] = servicePlugin
        self.__pluginToExts[servicePlugin] = servicePlugin.exts
    
    
    def convert(self, request, response):
        print "\nICE Service API - request=%s" % request
        requestPath = request.unquotedPath
        path, name, ext = self.__fs.splitPathFileExt(requestPath)
        if request.has_key("pathext"):
            pathExt = request.value("pathext")
            if pathExt == "":
                pathExt = None
        elif requestPath in [self.CONVERT_PATH, self.CONVERT_PATH_SLASH]:
            pathExt = None
        else:
            pathExt = "." + name
        if pathExt and not pathExt.startswith("."):
            pathExt = "." + pathExt
        plugin = self.__extToPlugin.get(pathExt, None)
        if name=="query":
            if plugin:
                data = "OK"
            else:
                data = "Not supported"
            response.setResponse(data, self.iceContext.MimeTypes[".html"])
            return
        if request.method == "GET":
            # interactive form if no session id, otherwise preview
            if request.has_key(self.SESSION_ID):
                sessionId = request.value(self.SESSION_ID)
                tmpFs = self.iceContext.FileSystem(sessionId)
                self.__delayDelete(str(tmpFs))
                splitPath = path.split(self.CONVERT_PATH_SLASH)
                if len(splitPath) > 1:
                    relPath = splitPath[1] + "/"
                else:
                    relPath = ""
                if tmpFs.isFile(relPath + name + ext):
                    data = tmpFs.readFile(relPath + name + ext)
                    # HACK for slides
                    if name.endswith(".slide") and ext == ".htm":
                        data = self.__fixPreviewLinks(data, sessionId)
                else:
                    data = ""
                response.setResponse(data, self.iceContext.MimeTypes[ext.lower()])
            else:
                if plugin == None:
                    options = None
                else:
                    options = plugin.options
                sessionId = self.__createSession()
                tmpl = self.iceContext.HtmlTemplate(templateFile = "ice-api.tmpl")
                htmlForm = tmpl.transform({"sessionId": sessionId,
                                           "pathExt": pathExt,
                                           "options": options,
                                           "plugins": self.__pluginToExts})
                response.setResponse(htmlForm, self.iceContext.MimeTypes[".html"])
        elif request.method == "POST":
            # call the appropriate service handler based on document extension
            docName, docData = self.__getDocument(request)
            _, _, ext = self.__fs.splitPathFileExt(docName)
            ext = ext.lower()
            if plugin == None:
                # plugin was not found via request path, guess from filename
                plugin = self.__extToPlugin.get(ext, None)
            if plugin != None:
                content = None
                mimeType = None
                if pathExt != ext:
                    if pathExt == None:
                        print "Converting as '%s'" % ext
                    else:
                        print "Force convert '%s' as '%s'" % (pathExt, ext)
                # populate the options - excluding uploaded files
                options = dict([(k, request.value(k))
                               for k in request.keys()
                               if not request.has_uploadKey(k)])
                # no session id so most likely a remote conversion call
                sessionId = request.value(self.SESSION_ID)
                if sessionId == None or sessionId == "":
                    options.update({self.SESSION_ID: self.__createSession()})
                try:
                    content, mimeType = plugin.service(docData, options, request, response)
                except Exception, e:
                    print str(e)
                    print self.iceContext.formattedTraceback()
                    raise self.iceContext.IceException(str(e))
                if mimeType == self.iceContext.MimeTypes[".html"]:
                    content = self.__fixPreviewLinks(content, sessionId)
		   
                response.setResponse(content, mimeType)
            else:
                raise self.iceContext.IceException("Unsupported extension %s" % ext)
        else:
            raise self.iceContext.IceException("405 Method Not Allowed")
    
    
    def __createSession(self):
        tmpDir = self.__fs.createTempDirectory(persist=True).absPath()
        self.__delayDelete(tmpDir)
        return tmpDir

    def __delayDelete(self, absPath):
        plugin = self.iceContext.getPlugin("ice.delay.cleanup")
        delayCleanup = plugin.pluginFunc(self.iceContext)
        delayCleanup.delPath(absPath, 60*60)     # auto cleanup in 1 Hour
        #delayCleanup.delPath(absPath, 15)     # for testing only - 15 Seconds
    
    def __getDocument(self, request):
        # Note: 'documentUrl' and 'document' are deprecated but still in use by Moodle
        if request.has_uploadKey("file"):
            fileKey = "file"
        else:
            fileKey = "document"
        
        urlValue = request.value("url", request.uploadFilename("documentUrl"))
        fileValue = request.uploadFilename(fileKey)
        
        if urlValue != None and urlValue != "":
            name = data = urlValue
        elif fileValue != None and fileValue != "":
            name = fileValue
            data = request.uploadFileData(fileKey)
        else:
            raise self.iceContext.IceException("Nothing to do!")
        
        return name, data
    
    
    def __fixPreviewLinks(self, html, sessionId):
        # process links to include the sessionId
	try:
		#et = self.iceContext.ElementTree.XML(html)
		xhtml = self.iceContext.Xml(html, parseAsHtml=True)
		postfix = "?%s=%s" %(self.SESSION_ID, sessionId)
		self.__updatePreviewLinks(xhtml, "a", "href", postfix)
		self.__updatePreviewLinks(xhtml, "img", "src", postfix)
		self.__updatePreviewLinks(xhtml, "link", "href", postfix)
		self.__updatePreviewLinks(xhtml, "script", "src", postfix)
		html = str(xhtml)
                html = re.sub("</(img|br|meta)>","",html)
		html = re.sub("(<(img|br|meta).*?)/?>","\\1/>",html)
		return html
 	except Exception, e:
			print "WARNING - Unable to fix preview links"
			print str(e)
			print self.iceContext.formattedTraceback()
			return html
  
    def __updatePreviewLinks(self, tree, tagName, attrName, postfix):
        for elem in tree.getNodes("//" + tagName):
            attr = elem.getAttribute(attrName)
            if attr != None and attr.find("://") == -1 and not attr.startswith("#"):
                elem.setAttribute(attrName, attr + postfix)

