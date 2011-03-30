
#    Copyright (C) 2009  Distance and e-Learning Centre,
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



pluginName = "ice.web.converter.handler"             ## /api/converter handler
pluginDesc = "Handler for web (api) convertion requests"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None




def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = WebConverterHandler
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc


class WebConverterHandler(object):
    basePath = "/api/converter"

    def __init__(self, iceContext):
        self.iceContext = iceContext

    
    def processRequest(self, request, response):        # requestData, responseData
        # iceContext.getPluginObject()
        # iceContext.getPluginSingletonObject()
        # iceContext.getMimeTypeFor(), .getMimeTypeForExt()
        path = request.path
        if path==self.basePath:
            relPath = ""
        elif path.startswith(self.basePath + "/"):
            relPath = path[len(self.basePath)+1:]
        else:
            data = "<h3>Error can not handle request for '%s'</h3>" % path
            response.setResponse(data, "text/html")
            return

        print "\n ice.web.converter.handler - relPath='%s'" % relPath

        if request.method=="GET":
            self.__getHandler(request, response)
        elif request.method=="POST":
            self.__postHandler(request, response)
        else:
            raise self.iceContext.IceException("405 Method Not Allowed")



    def __getHandler(self, request, response):
        requestPath = request.unquotedPath
        mimeType = "text/html"                  # default
        data = "<h2>API Converter</h2>"         # default
        ####
        # interactive form if no session id, otherwise preview
        #if request.has_key(self.SESSION_ID):        # self.SESSION_ID="sessionid"
        if False:
            sessionId = request.value(self.SESSION_ID)
            tmpFs = self.iceContext.FileSystem(sessionId)
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
            mimeType = self.iceContext.getMimeTypeForExt(ext)
        else:
            #if plugin == None:
            #    options = None
            #else:
            #    options = plugin.options
            #sessionId = self.__createSession()
            tmpl = self.iceContext.HtmlTemplate(templateFile = "ice-api.tmpl")
            #htmlForm = tmpl.transform({"sessionId": sessionId,
            #                           "pathExt": pathExt,
            #                           "options": options,
            #                           "plugins": self.__pluginToExts})
            htmlForm = tmpl.transform({"sessionId": "id",
                                       "pathExt": "pathExt",
                                       "options": {},
                                       "plugins": {}})
            data = htmlForm
            mimeType = self.iceContext.getMimeTypeForExt(".html")
        ####
        response.setResponse(data, mimeType)


    def __postHandler(self, reqest, response):
        tempDirFS = self.__getTempDirFS()

        mimeType = "text/html"
        content = "<h2>API Converter</h2>"
        ####
        # call the appropriate service handler based on document extension
        docName, docData = self.__getUploadedFile(request)
        _, _, ext = self.__fs.splitPathFileExt(docName)
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
            if mimeType == self.iceContext.getMimeTypeForExt(".html"):
                content = self.__fixPreviewLinks(content, sessionId)
            response.setResponse(content, mimeType)
        else:
            raise self.iceContext.IceException("Unsupported extension %s" % ext)
        ####
        response.setResponse(content, mimeType)

    
    def __getTempDirFS(self):
        session = request.session
        tempDirFS = session.get("tempDirFS")
        if tempDirFS is None:
            tempDirFS = self.iceContext.fs.createTempDirectory(persist=True)    # ? persist=False should be OK
            session["tempDirFS"] = tempDirFS
        return tempDirFS


    def __getUploadedFile(self, request):
        """
            returns 'uploaded' filename, filedata
        """
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


    ###########################################################################
    ###########################################################################
    def __fixPreviewLinks(self, html, sessionId):
        # process links to include the sessionId
        et = self.iceContext.ElementTree.XML(html)
        postfix = "?%s=%s" %(self.SESSION_ID, sessionId)
        self.__updatePreviewLinks(et, "a", "href", postfix)
        self.__updatePreviewLinks(et, "img", "src", postfix)
        self.__updatePreviewLinks(et, "link", "href", postfix)
        self.__updatePreviewLinks(et, "script", "src", postfix)
        return self.iceContext.ElementTree.tostring(et)


    def __updatePreviewLinks(self, tree, tagName, attrName, postfix):
        for elem in tree.findall(".//" + tagName):
            attr = elem.get(attrName)
            if attr != None and attr.find("://") == -1 and not attr.startswith("#"):
                elem.set(attrName, attr + postfix)







