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

import zipfile

pluginName = "ice.service.pdfToHtml"
pluginDesc = "Converting pdf to html"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    handler = PdfToHtmlService(iceContext)
    return handler

class PdfToHtmlService(object):
    exts = [".pdf"]
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def service(self, document, options, request, response):
        url = options.get("url")
        
        if document == url:
            filename = url
        else:
            filename = request.uploadFilename("file")
        
        sessionId = options.get("sessionid")
        
        if sessionId == None:
            raise self.iceContext.IceException("No session ID")
        
        tmpFs = self.iceContext.FileSystem(sessionId)
        toDir = tmpFs.absPath()
        _, oriName, _ = self.iceContext.fs.splitPathFileExt(filename)
        #name = name.replace(" ", "_")
        inputFile = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        pdfToImagePlugin = self.iceContext.getPlugin("ice.converter.pdfTohtml").pluginClass
        pdfPlugin = pdfToImagePlugin(self.iceContext)
        status, htmlPage = pdfPlugin.convert(inputFile, toDir, options)
        
        if status=="ok":
            zipName = "%s.zip" % oriName
            name = oriName.replace(" ", "_")
            #zipFilePath = self.iceContext.fs.absPath(zipName)
            zipFilePath = tmpFs.absPath(zipName)
            #print "toDir = %s" % toDir
            mediaFiles = tmpFs.glob("%s/%s_files/*" % (toDir, name))
            files = []
            for mFile in mediaFiles:
                files.append(tmpFs.absPath(mFile))
            if htmlPage:
                self.iceContext.fs.write(tmpFs.absPath(oriName+".htm"), htmlPage)
                files.append(tmpFs.absPath(oriName+".htm"))
            
            zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            for file in files:
                arcname = file.split(toDir + "/")[1]
                zipFile.write(file, arcname)
            zipFile.close()
            
            contentFile = zipFilePath
            mimeType = self.iceContext.MimeTypes[".zip"]
            response.setDownloadFilename(zipName.replace(" ", "_"));
            
            if contentFile == None:
                contentFile = htmlPage
                mimeType = self.iceContext.MimeTypes[".html"]
        else:
            raise self.iceContext.IceException(status)
        return tmpFs.readFile(contentFile), mimeType
    
    def options(self):
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/pdf-to-html.tmpl")
        return tmpl.transform()
