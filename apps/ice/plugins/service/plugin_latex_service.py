
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

""" This plugin is used to support latex conversion in ICE 
conversion server. 
This plugin will call LaTeXConverter plugin 
@requires: plugins/extras/plugin_latex_converter.py
"""

import zipfile
from glob import glob

pluginName = "ice.service.latex"
pluginDesc = "LaTeX conversion service"
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
    handler = TexService(iceContext)
    return handler


class TexService(object):
    """ Base class for Latex Service 
    default extension is .tex
    @ivar exts: Supported extension list
    @ivar defaultTemplate: default html template layout  
    """ 
    defaultTemplate = """<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>Default Template</title>
    <style type="text/css">
      .rendition-links { text-align: right; }
      .body table td { vertical-align: top; }
    </style>
    <style class="sub style-css" type="text/css"></style>
  </head>
  <body>
    <div class="rendition-links">
      <span class="ins pdf-rendition-link"></span>
    </div>
    <h1 class="ins title"></h1>
    <div class="ins page-toc"></div>
    <div class="ins body"></div>
  </body>
</html>"""
    
    exts = [".tex"]
    
    def __init__(self, iceContext):
        """ LaTeX Service Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext  
        @rtype: void
        """
        self.iceContext = iceContext
    
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
        template = options.get("template")
        if template == None or template == "":
            # make sure there is a default template
            # TODO check if template was uploaded
            template = self.defaultTemplate
            options.update({"template": template})
        
        sessionId = options.get("sessionid")
        if sessionId == None:
            raise self.iceContext.IceException("No session ID")
        
        tmpFs = self.iceContext.FileSystem(sessionId)
        toDir = tmpFs.absPath()
        
        if document == url:
            _, filename = tmpFs.split(document)
            http = self.iceContext.Http()
            document, _, errCode, msg = http.get(url, includeExtraResults=True)
            if errCode == -1:
                raise self.iceContext.IceException("Failed to get %s (%s)" % (url, msg))
        else:
            filename = request.uploadFilename("file").lower()
        
        texFilePath = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        
        LaTeXConverter = self.iceContext.getPlugin("ice.extra.LaTeXConverter").pluginClass
        conv = LaTeXConverter(self.iceContext, htmlTemplate = template)
        status, htmlFile, _ = conv.tex4html(texFilePath, toDir, options)
        mimeType = self.iceContext.MimeTypes[".html"]
        
        if status == "ok":
            if options.get("zip", False):
                _, name, _ = tmpFs.splitPathFileExt(filename)
                zipName = "%s.zip" % name
                zipFilePath = tmpFs.absPath(zipName)
                
                imageFiles = glob("%s/*.png" % toDir)
                files = []
                if len(imageFiles) > 0:
                    files = imageFiles
                files.append(tmpFs.absPath(name + ".html"))
                files.append(tmpFs.absPath(name + ".pdf"))
                zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
                for file in files:
                    _, arcname = tmpFs.split(file)
                    zipFile.write(file, arcname)
                zipFile.close()
                
                content = tmpFs.readFile(zipName)
                mimeType = self.iceContext.MimeTypes[".zip"]
                response.setDownloadFilename(zipName.replace(" ", "_"))
            else:
                content = tmpFs.readFile(htmlFile)
        else:
            content = status
            log = tmpFs.readFile(htmlFile)
            if log is not None:
                content += "\n\nLog file contents:\n" + log
            mimeType = self.iceContext.MimeTypes[".txt"]
        
        return content, mimeType
    
    def options(self):
        """ 
        @rtype: String
        @return: transformed latex document in html format
        """
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/tex-service.tmpl")
        return tmpl.transform({"template": self.defaultTemplate})
    
