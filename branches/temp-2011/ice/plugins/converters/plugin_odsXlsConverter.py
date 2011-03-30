
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


import re
import zipfile
from time import gmtime, strftime

pluginName = "ice.converter.odsExcel"
pluginDesc = "OpenOffice.org/Excel conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None

Mets = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = OdsExcelConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc



#ModsCreator(iceContext)
#ModsCreator.createFromMeta(meta) -> xmlString

class OdsExcelConverter(object):
    exts = [".ods", ".xls", ".xlsx"]

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
      <span class="ins source-link"></span>
      <span class="ins slide-link"></span>
      <span class="ins pdf-rendition-link"></span>
    </div>
    <h1 class="ins title"></h1>
    <div class="ins page-toc"></div>
    <div class="ins body"></div>
  </body>
</html>"""

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__includeExts = [".htm", ".ods", ".xls",  ".xlsx", ".pdf", ".slide.htm"]


    @property
    def isAvaliable(self):
        return True


    def convert(self, fromToObj, **kwargs):
        """

        """

    def service(self, document, options, request, response):
        self.__options = options
        self.__request = request
        self.__response = response

        # Note: 'templateString' is deprecated but still in use by Moodle
        url = options.get("url")
        template = options.get("template", options.get("templateString", None))
        if template == None or template == "":
            # make sure there is a default template
            # TODO check if template was uploaded
            template = self.defaultTemplate
            options.update({"template": template})

        if options.has_key("includetitle"):
            options.update({"includetitle": False})
        if not options.has_key("toc"):
            options.update({"toc": False})

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
            if request.has_uploadKey("file"):
                fileKey = "file"
            else:
                # Note: 'document' is deprecated but still in use by Moodle
                fileKey = "document"
            filename = request.uploadFilename(fileKey)

        xlsFilePath = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)

        OdsXlsConverter = self.iceContext.getPlugin("ice.ooo.OdsXlsConverter").pluginClass
        app = OdsXlsConverter(self.iceContext, tmpFs, template)
        status, htmlFile, _ = app.convert(xlsFilePath, toDir, options)

        if status == "ok":
            self.__removeLocalhostLinks(htmlFile, app.meta)
            contentFile, mimeType = self.__createPackage(tmpFs, filename, app.meta)
            if contentFile == None:
                contentFile = htmlFile
                mimeType = self.iceContext.MimeTypes[".html"]
        else:
            raise self.iceContext.IceException(status)

        return tmpFs.readFile(contentFile), mimeType

    def options(self):
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/odt-doc-service.tmpl")
        return tmpl.transform({"template": self.defaultTemplate})

    def __removeLocalhostLinks(self, htmlFile, meta):
        xml = self.iceContext.Xml(htmlFile)
        nodes = xml.getNodes("//a")
        for node in nodes:
            href = node.getAttribute("href")
            content = node.getContent()
            if href is not None:
                if href.startswith("http://localhost/") or \
                   href.startswith("http://localhost:") or \
                   href.startswith("file://") or href.startswith("/"):
                    #NOTE: open office treat file:/// as / in the content.xml,
                    #just strip off the link
                    if node.getPrevSibling() is None:
                        node.getParent().addChildren(node.getChildren())
                    else:
                        node.getPrevSibling().addChildren(node.getChildren())
                    node.remove()
                elif href.startswith("http://"):
                    #Handle relative link, if it's a domain leave it as what it is
                    #if file extension existed in mime type like http://test.htm,
                    #treat it as a relative link, strip the http://
                    domain = href.split("/")[2]
                    ext = self.iceContext.fs.splitExt(domain)[1]
                    mimeType = self.iceContext.MimeTypes.get(ext)
                    if (mimeType == None and domain.find(".") == -1) or (mimeType != None):
                        newHref = href[7:]
                        node.setAttribute("href", newHref)
                        #if content have the same name as the domain, strip the http as well
                        if (content.strip() == href.strip()):
                            allChild = node.getChildren()
                            if allChild is None or allChild == []:
                                node.setContent(newHref)
                            else:
                                self.__setContentToLastChild(allChild, newHref)
        xml.saveFile()
        xml.close()

    def __setContentToLastChild(self, nodeList, content):
        #Find the last node in the node to maintain the style and formatting
        for node in nodeList:
            if len(node.getChildren()) > 0:
                self.__setContentToLastChild(node.getChildren(), content)
            else:
                node.setContent(content)

    def __createPackage(self, fs, filename, meta):
        zip = self.__options.get("zip", False)
        mets = self.__options.get("mets", False)
        mods = self.__options.get("mods", mets)    # MODS always created with METS
        dc = self.__options.get("dc", False)
        rdf = self.__options.get("rdf", False)

        contentFile = None
        mimeType = None

        toDir = fs.absPath()
        if mods:
            modsCreator = ModsCreator(self.iceContext)
            modsData = modsCreator.createFromMeta(meta)
            fs.writeFile("mods.xml", modsData)

        if mets:
            metsCreator = MetsCreator(self.iceContext, self.__includeExts)
            metsData = metsCreator.createFromMeta(toDir, meta, inline = not zip)
            fs.writeFile("mets.xml", metsData)
            contentFile = fs.absPath("mets.xml")
            mimeType = self.iceContext.MimeTypes[".xml"]

        if dc:
            DublinCore = self.iceContext.getPluginClass('ice.extra.DublinCore')
            if DublinCore is not None:
                dc = DublinCore(self.iceContext)
                try:
                    dcXml = dc.getDocumentDC(meta)
                    if dcXml is not None:
                        File("dc.xml", dcXml)
                        contentFile = fs.absPath("dc.xml")
                        mimeType = self.iceContext.MimeTypes[".xml"]
                    else:
                        print "Error in exporting DC"
                except :
                    dc = False
                    print "Error in exporting DC"

#        if rdf:
#            OREResourceMap = self.iceContext.getPluginClass("ice.extra.ORE")
#            if OREResourceMap is not None:
#                rem = OREResourceMap(self.iceContext)
#                ##item = self.__rep.getItemForUri(file)  err item? ########
#                class MItem(object):
#                    def __init__(self, relPath):
#                        self.relPath=relPath
#                        self.hasSlide = False
#                        self.meta = {}
#                    def getMeta(self, name):
#                        return self.meta.get(name)
#                mItem = MItem(filename)
#                mItem.meta = dict(meta)
#                dirs = fs.listDirectories()
#                if dirs!=[]:
#                    imageDir = dirs[0]
#                    imageFiles = fs.listFiles(imageDir)
#                    mItem.meta["images"] = imageFiles;
#                rdf = rem.getDocumentRdfXml(mItem)
#                fs.writeFile("rdf.xml", rdf)
#                contentFile = fs.absPath("rdf.xml")
#                mimeType = self.iceContext.MimeTypes[".xml"]

        if zip:
            _, name, _ = fs.splitPathFileExt(filename)
            zipName = "%s.zip" % name
            zipFilePath = fs.absPath(zipName)

            mediaFiles = fs.glob("%s/%s_files/*" % (toDir, name))
            files = []
            for mFile in mediaFiles:
                files.append(fs.absPath(mFile))
            for ext in self.__includeExts:
                includeFile = name + ext
                if fs.exists(includeFile):
                    files.append(fs.absPath(includeFile))
            if mods: files.append(fs.absPath("mods.xml"))
            if mets: files.append(fs.absPath("mets.xml"))
            if dc:   files.append(fs.absPath("dc.xml"))
            if rdf:  files.append(fs.absPath("rdf.xml"))
            zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            for file in files:
                arcname = file.split(toDir + "/")[1]
                zipFile.write(file, arcname)
            zipFile.close()

            contentFile = zipFilePath
            mimeType = self.iceContext.MimeTypes[".zip"]
            self.__response.setDownloadFilename(zipName.replace(" ", "_"))

        return contentFile, mimeType


