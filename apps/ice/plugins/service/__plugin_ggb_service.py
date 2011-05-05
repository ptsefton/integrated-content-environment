
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

""" This plugin is used to support Geogebra conversion in ICE 
conversion server. 
This plugin will call geoGebraExport plugin 
@requires: plugins/extras/plugin_ggb_export.py
"""

pluginName = "ice.service.geogebra"
pluginDesc = "GeoGebra conversion service"
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
    handler = GgbService(iceContext)
    return handler


class GgbService(object):
    """ Base class for Geogebra Service 
    default extension is .ggb
    @ivar exts: Supported extension list 
    """ 
    exts = [".ggb"]
    
    def __init__(self, iceContext):
        """ Geogebra Service Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @rtype: void
        """
        self.iceContext = iceContext
    
    def service(self, document, options, request, response):
        """ method that accepts request and returns rendered result
        @param document: document path to be rendered
        @type document: String
        @param options: list of options 
        @type options: dict
        @param request: request data information
        @type request: serverRequestData
        @param response: response data information
        @type response: serverResponseData
        
        @rtype: String
        @return: content and mimeType
        """
        url = options.get("url")
        mode = options.get("mode", "image")
        format = options.get("format", "png")
        width = options.get("width", "300")
        height = options.get("height", "300")
        
        GeoGebraExport = self.iceContext.getPlugin("ice.extra.geoGebraExport").pluginClass

        if mode == "image":
            export = GeoGebraExport(self.iceContext, self.iceContext.settings.get("convertUrl"))
            content = export.createPreviewImage(document, format, width, height)
            mimeType = self.iceContext.MimeTypes["." + format.lower()]
        else:
            uploadFileName = request.uploadFilename("file")
            if uploadFileName != document:
                sessionId = options.get("sessionid","")
                if sessionId.endswith("/"):
                    sessionId = sessionId[:-1]
                filePath = sessionId + "/"+ uploadFileName
                self.iceContext.fs.writeFile(filePath,document)
                document = filePath
            elif document != url:
                document = request.uploadFilename("file")
            if document.find("://") ==-1:
                document = "file://"+document
            
            archive = self.iceContext.system.environment.get("GEOGEBRA_HOME", "")
            if archive == "":
                content =  GeoGebraExport.getAppletHtml(document, width, height)
            else:
                if archive.endswith("/"):
                    archive = archive[:-1]
                archive = "file://"+archive+"/geogebra.jar"
                content =  GeoGebraExport.getAppletHtml(document, width, height,archive)
            mimeType = self.iceContext.MimeTypes[".html"]
        
        return content, mimeType
    
    def options(self):
        """ 
        @rtype: String
        @return: transformed ggb options in html format
        """
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/ggb-service.tmpl")
        return tmpl.transform()
    
