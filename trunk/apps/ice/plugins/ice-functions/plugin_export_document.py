
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

from request_data import ServerRequestData
from response_data import ServerResponseData

pluginName = "ice.function.exportDocument"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    global templatePath
    path = iceContext.fs.split(__file__)[0]
    templatePath = iceContext.fs.join(path, "export-document.tmpl")
    pluginFunc = exportDocument
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


def exportDocument(self):
    self.isDocContentView = False
    downloadFilename = None
    item = self.item
    d = {"docBody": self["body"],
         "docTitle": item.getMeta('title', 'untitled'),
         "__rep": self.rep}
    d["templates"] = self.rep.getSkinTemplates(["/", self.packagePath]) 
    self.title = "Export '%s'" % d.get("docTitle", "Untitled")
    postback = self.formData.has_key("postback")
    if postback:
        name = item.name
        d["file"] = name
        d["argPath"] = item.relPath
        
        template = self.formData.value("template")
        if template == "default":
            template = "template.xhtml"
        else:
            template = "templates/%s.xhtml" % template
        template = self.iceContext.urlJoin(self.packagePath, "skin", template)
        templateData = self.rep.getItem(template).read()
        d["template"] = templateData.strip()
        
        d["includeSkin"]=self.formData.has_key("skin")
        d["pdflink"] = self.formData.has_key("pdflink")
        d["slidelink"] = self.formData.has_key("slidelink")
        d["toc"] = self.formData.has_key("toc")
        d["includetitle"] = self.formData.has_key("title")
        d["sourcelink"] = self.formData.has_key("sourcelink")
        #d["mods"] = self.formData.has_key("mods")
        d["mets"] = self.formData.has_key("mets")
        d["dc"] = self.formData.has_key("dc")
        d["rdf"] = self.formData.has_key("rdf")
        
        exportDoc = ExportDocument(self)
        zipPath, response = exportDoc.export(item.relPath, d)
        success = zipPath is not None
        if success:
            downloadFilename = zipPath
            self["title"] = d.get("docTitle", "Untitled")
        else:
            self["error"] = response.data
        d["success"] = success
    else:
        d["success"] = False
    self["page-toc"] = ""
    htmlTemplate = self.iceContext.HtmlTemplate(templatePath)
    self.body = htmlTemplate.transform(d, allowMissing=True)
    if downloadFilename is not None:
        return (None, None, downloadFilename)
    return None


def isDocView(self):
    return self.isDocView


exportDocument.options = {"toolBarGroup":"publish",
                          "position":54,
                          "postRequired":True,
                          "label":"Export document",
                          "title":"Export current document to a ZIP file",
                          "enableIf": isDocView}


class ExportDocument(object):
    def __init__(self, site):
        self.iceContext = site.iceContext
        self.__site = site
        self.__iceServices = self.iceContext.iceServices
        self.__loadPlugins()
    
    
    def export(self, path, options):
        zipPath = None
        item = self.__site.rep.getItemForUri(path)
        name = item.name
        filename = self.iceContext.fs.split(name)[1]
        fileData = item.read()
        
        class FileStorage(object):  # to mock paste's fieldStorage object
            def __init__(self, filename, data):
                self.filename = filename
                self.__data = data
                self.file = self
            def read(self):
                return self.__data
        
        options["zip"] = True
        filenames = {"file": FileStorage(filename, fileData)}
        request = ServerRequestData(path="/api/convert",
                                    method="POST",
                                    args=options,
                                    filenames=filenames)
        response = ServerResponseData()
        self.__iceServices.convert(request, response)
        if response.contentType == self.iceContext.MimeTypes[".zip"]:
            baseName  = self.iceContext.fs.splitExt(filename)[0]
            baseName = baseName.replace(" ", "_")
            zipName = baseName + ".zip"
            tmpFs = self.iceContext.FileSystem(self.__site.rep.exportPath)
            try:
                tmpFs.writeFile(zipName, response.data)
            except Exception,e:
                print "Error in zipping : '%s'" % str(e)
            zipPath = tmpFs.absPath(zipName)
        return zipPath, response
    
    
    def __loadPlugins(self):
        for servicePlugin in self.iceContext.getPluginsOfType("ice.service."):
            service = servicePlugin.pluginInit(self.iceContext)
            service.name = servicePlugin.pluginName
            service.description = servicePlugin.pluginDesc
            for ext in service.exts:
                self.__iceServices.addServicePlugin(ext, service)



















