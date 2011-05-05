
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

pluginName = "ice.service.wave2mp3"
pluginDesc = "Wave to MP3 conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    handler = WaveToMp3Service(iceContext)
    return handler

class WaveToMp3Service(object):
    exts = [".wav", ".aiff"]
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def service(self, document, options, request, response):
        url = options.get("url")
        
        if document == url:
            filename = url
        else:
            filename = request.uploadFilename("file")
        
        tmpFs = self.iceContext.fs.createTempDirectory()
        _, name, _ = self.iceContext.fs.splitPathFileExt(filename)
        inputFile = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        LameEncoder = self.iceContext.getPlugin("ice.extra.lameEncoder").pluginClass
        wave = LameEncoder(self.iceContext)
        outputFile = wave.convert(inputFile)
        print "wave to mp3: %s to %s" % (inputFile, outputFile)
        
        content = tmpFs.readFile(outputFile)
        mimeType = self.iceContext.MimeTypes[".mp3"]
        response.setDownloadFilename(name.replace(" ", "_") + ".mp3")
        tmpFs.delete()
        
        return content, mimeType
    
    def options(self):
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/wav-service.tmpl")
        return tmpl.transform()
    
