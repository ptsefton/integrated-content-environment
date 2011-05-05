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

pluginName = "ice.service.mediaToFlv"
pluginDesc = "audio/video conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    handler = MediaToFlvService(iceContext)
    return handler


class MediaToFlvService(object):
    exts = [".mp3", ".mp4", ".m4a", ".wma", ".wmv", ".mpg", ".mpeg", ".mov"]
    #".wav",  for now wav is coverted using lame in plugin_wav_service
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def service(self, document, options, request, response):
        url = options.get("url")
        
        if document == url:
            filename = url
        else:
            filename = request.uploadFilename("file").lower()
        
        tmpFs = self.iceContext.fs.createTempDirectory()
        _, name, _ = self.iceContext.fs.splitPathFileExt(filename)
        inputFile = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        mediaToFlvPlugin = self.iceContext.getPlugin("ice.converter.mediaToFlv").pluginClass
        mediaToFlv = mediaToFlvPlugin(self.iceContext)
        outputFile = mediaToFlv.convert(inputFile)
        print "audio to flv: %s to %s" % (inputFile, outputFile)
        
        content = tmpFs.readFile(outputFile)
        mimeType = self.iceContext.MimeTypes[".flv"]
        name = name.replace(" ", "_")  #To avoid spacing
        response.setDownloadFilename("%s.flv" % name)
        tmpFs.delete()
    
        return content, mimeType
    
    def options(self):
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/media-to-flv-service.tmpl")
        return tmpl.transform()
    
