
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

pluginName = "ice.service.svg"
pluginDesc = "Scalable Vector Graphics conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    handler = SvgService(iceContext)
    return handler


class SvgService(object):
    exts = [".svg"]
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def service(self, document, options, request, response):
        url = options.get("url")
        format = options.get("format", None)
        if format is None:
            options.update({"format": "png"})
            format = "png"
            
        sessionId = options.get("sessionid")
        if sessionId == None:
            raise self.iceContext.IceException("No session ID")
        
        tmpFs = self.iceContext.FileSystem(sessionId)
        if document == url:
            _, filename = tmpFs.split(document)
            http = self.iceContext.Http()
            document, _, errCode, msg = http.get(url, includeExtraResults=True)
            if errCode == -1:
                raise self.iceContext.IceException("Failed to get %s (%s)" % (url, msg))
        else:
            filename = request.uploadFilename("file")
        
        svgFilePath = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        svgConvert = self.iceContext.getPlugin("ice.extra.SVGConverter").pluginFunc
        content = svgConvert(svgFilePath, options)
        mimeType = self.iceContext.MimeTypes["." + format]
        
        
        if format in ["pdf", "ps"]:
            _, name, _ = tmpFs.splitPathFileExt(filename)
            response.setDownloadFilename(name.replace(" ", "_") + "." + format)
        
        return content, mimeType
    
    def options(self):
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/svg-service.tmpl")
        return tmpl.transform()
    