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

""" Extra Plugin to resize/cropping images in ICE conversion
service
This plugin will call image resize plugin 
@requires: plugins/extras/plugin_image_resize.py
"""

pluginName = "ice.service.imageResize"
pluginDesc = "Resizing/Cropping images service"
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
    handler = ImageResizeService(iceContext)
    return handler

class ImageResizeService(object):
    """ Base class for ImageResize Service
    @ivar exts: Supported extension list 
    """ 
    exts = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    
    def __init__(self, iceContext):
        """ Image Resize Service Constructor method 
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
        
        if document == url:
            filename = url
        else:
            filename = request.uploadFilename("file") #.lower()
        
        sessionId = options.get("sessionid")
        if sessionId == None:
            raise self.iceContext.IceException("No session ID")
        
        # Create a temporary directory based on sessionId
        tmpFs = self.iceContext.FileSystem(sessionId)
        toDir = tmpFs.absPath()
        
        _, name, ext = self.iceContext.fs.splitPathFileExt(filename)
        inputFile = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        imageResizePlugin = self.iceContext.getPlugin("ice.converter.imageResize").pluginClass
        imagePlugin = imageResizePlugin(self.iceContext)
        outputFile = imagePlugin.convert(inputFile, options, toDir)
        
        #if options.has_key("multipleImageOptions") and options.get("multipleImageOptions") != {}:
            #return zip file
        #    pass
        if self.iceContext.fs.isDirectory(outputFile):
            #remove the original
            self.iceContext.fs.delete(inputFile)
            tempDir = self.iceContext.fs.createTempDirectory()
            zipFile = tempDir.absPath("%s.zip" % name)
            self.iceContext.fs.zip(zipFile, toDir)
            mimeType = self.iceContext.MimeTypes[".zip"]
            content = tempDir.read("%s.zip" % name)
        elif options.get("mode") == "download":
            mimeType = self.iceContext.MimeTypes[".jpg"]
            content = tmpFs.readFile(outputFile)
            name = name.replace(" ", "_")  #To avoid spacing
            response.setDownloadFilename("%s.jpg" % name)
        else:
            mimeType = self.iceContext.MimeTypes[ext]
            f = open(outputFile, "rb")
            content = f.read()
            f.close()
    
        return content, mimeType
    
    def options(self):
        """ 
        @rtype: String
        @return: transformed images options in html format
        """
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/resize-image-service.tmpl")
        return tmpl.transform()
