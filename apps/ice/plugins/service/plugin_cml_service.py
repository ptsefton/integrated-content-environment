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

""" This plugin is used to support Chemical Markup Language conversion in ICE 
conversion server. 
This plugin will call cmlUtil plugin to convert .cml to SVG, PNG or JMOL, CDX, JPG
@requires: plugins/extras/plugin_cmlUtil.py
"""

pluginName = "ice.service.cml"
pluginDesc = "Chemical Markup Language conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized, CmlUtil
    CmlUtil = iceContext.getPlugin("ice.extras.cmlUtil").pluginClass
    handler = CmlService(iceContext)
    pluginClass = CmlService
    pluginInitialized = True
    return handler

class CmlService(object):
    """ Base class for Chemical Markup Language Service 
    default extension is .cml
    @ivar exts: Supported extension list
    """ 
    exts = [".cml"]
    
    def __init__(self, iceContext):
        """ Chemical Markup Language Service Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @rtype: void
        """
        self.iceContext = iceContext
        self.params = None
    
    def service(self, document, options, request, response):
        """ method that accepts request and returns rendered result
        @param document: document path to be rendered
        @type document: Strinmg
        @param options: list of options 
        @type options: dict
        @param request: request data information
        @type request: serverRequestData
        @param response: response data information
        @type response: serverResponseData
        
        @rtype: (String, String)
        @return: content and mimeType
        """
        url = options.get("url")
        mode = options.get("mode", "preview")
        format = options.get("format", "svg")
        width = options.get("width", "300")
        height = options.get("height", "300")
        reload = options.has_key("reload")
        params = options.get("params", CmlUtil.getJumboDefaults())
        self.params = {"params": params}
        
        if document == url:
            filename = url
        else:
            filename = request.uploadFilename("file").lower()
        
        util = CmlUtil(self.iceContext, self.iceContext.settings.get("convertUrl"))
        if mode == "preview":
            content = util.createPreviewImage(document, format, width, height, params)
            mimeType = self.iceContext.MimeTypes["." + format.lower()]
        elif mode == "extract":
            _, name, ext = self.iceContext.fs.splitPathFileExt(filename)
            content = util.extractChemDraw(document, name = name + ext)
            mimeType = self.iceContext.MimeTypes[".zip"]
            response.setDownloadFilename("media.zip")
        elif mode == "applet":
            appletHtml = CmlUtil.getAppletHtml(filename, width, height)
            content = "<div><pre>%s</pre></div>" % appletHtml
            mimeType = self.iceContext.MimeTypes[".html"]
        else:
            raise Exception("Unknown mode: %s" % mode)
        
        if reload:
            self.params = None
        
        return content, mimeType
    
    
    def options(self):
        """ 
        @rtype: String
        @return: transformed cml document in html format
        """
        if self.params is None:
            self.params = {"params": CmlUtil.getJumboDefaults()}
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/cml-service.tmpl")
        return tmpl.transform(self.params)


