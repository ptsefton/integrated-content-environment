
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

""" This plugin is used to support Open Office Presentation/Power Point Presentation
documents conversion in ICE conversion server.
This plugin will call OdpPptConverter plugin
@requires: plugins/extras/plugin_odp_ppt_converter.py
"""

import re
import zipfile
from time import gmtime, strftime

pluginName = "ice.service.odp-ppt"
pluginDesc = "OpenOffice.org/Power point conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = OdpPptConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc



class OdpPptConverter(object):
    """ Base class for OdpPpt Service
    default extensions are .odp and .ppt
    """
    
    exts = [".odp", ".ppt"]
    
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
    #-------------------------------------------------------------
    @staticmethod
    def createModsFromMeta(iceContext, meta):
        modsCreator = ModsCreator(iceContext)
        return modsCreator.createFromMeta(meta)


    def __init__(self, iceContext):
        """ Office Presentation/Power Point Presentation Service Constructor method
        @param iceContext: Current ice context
        @type iceContext: IceContext
        """
        self.iceContext = iceContext
        self.__includeExts = [".htm", ".odp", ".ppt", ".pdf", ".slide.htm"]


    @property
    def isAvaliable(self):
        return True


    def convert(self, fromToObj, **options):
        """

        """
        pass


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

        @return: content and mimeType in String
        """
        self.__options = options
        self.__request = request
        self.__response = response

        options["slidelink"] = "on"
        options["pdflink"] = "on"
        options["sourcelink"] = "off"
        options["zip"] = True

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

        pptFilePath = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)

        OdpPptConverter = self.iceContext.getPlugin("ice.ooo.OdpPptConverter").pluginClass
        app = OdpPptConverter(self.iceContext, tmpFs, template)
        status, htmlFile, _ = app.convert(pptFilePath, toDir, options)
        if status == "ok":
            #self.__removeLocalhostLinks(htmlFile, app.meta)
            contentFile, mimeType = self.__createPackage(tmpFs, filename, app.meta)
            if contentFile == None:
                contentFile = htmlFile
                mimeType = self.iceContext.MimeTypes[".html"]
        else:
            raise self.iceContext.IceException(status)

        return tmpFs.readFile(contentFile), mimeType

    def options(self):
        """ options method
        @return: transformed odp/ppt document in html format
        """
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/odt-doc-service.tmpl")
        return tmpl.transform({"template": self.defaultTemplate})

    def __createPackage(self, fs, filename, meta):
        """ createPackage private method
        @param fs: FileSystem type
        @param filename: filename of the original document
        @param meta: metadata of the document
        @return: contentFile path to the zip file
                 mimeType mimetype of the zip file
        """
        zip = self.__options.get("zip", False)
        mets = self.__options.get("mets", False)
        mods = self.__options.get("mods", mets)    # MODS always created with METS
        dc = self.__options.get("dc", False)
        rdf = self.__options.get("rdf", False)
        sourcelink = self.__options.get("sourcelink", "off")
        slidelink = self.__options.get("slidelink", "off")
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
                dcXml = dc.getDocumentDC(meta)
                fs.writeFile("dc.xml", dcXml)
                contentFile = fs.absPath("dc.xml")
                mimeType = self.iceContext.MimeTypes[".xml"]

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
            skinFiles = fs.glob("%s/skin/*" % (toDir))
            fancyFiles = fs.glob("%s/skin/fancyzoom/*" % (toDir))
            otherMedia = fs.glob("%s/media/*" % (toDir))
            compoundMedia = fs.glob("%s/media/compound/*" % (toDir))
            files = []
            for mFile in mediaFiles:
                files.append(fs.absPath(mFile))
            for sFile in skinFiles:
                files.append(fs.absPath(sFile))
            for oFile in otherMedia:
                files.append(fs.absPath(oFile))
            for fFile in fancyFiles:
                files.append(fs.absPath(fFile))
            for cFile in compoundMedia:
                files.append(fs.absPath(cFile))

            for ext in self.__includeExts:
                includeFile = name + ext
                if fs.exists(includeFile):
                    files.append(fs.absPath(includeFile))
            if mods: files.append(fs.absPath("mods.xml"))
            if mets: files.append(fs.absPath("mets.xml"))
            if dc:   files.append(fs.absPath("dc.xml"))
            if rdf:  files.append(fs.absPath("rdf.xml"))

            #pdfLink
            if not self.__options.get("pdflink"):
                pdfFile = "%s/%s.pdf" % (toDir, name)
                if pdfFile in files:
                    files.remove(pdfFile)

            #sourcefile
            if sourcelink == "off":
                sourceFile = "%s/%s" % (toDir, filename)
                if sourceFile in files:
                    files.remove(sourceFile)

            #slidelink
            if slidelink == "off":
                slideFile = "%s/%s.slide.htm" % (toDir, name)
                slidetemplate = "%s/%s_files/slide.xhtml" % (toDir, name)
                slidejs = "%s/%s_files/slideous.js" % (toDir, name)
                slidecss = "%s/%s_files/slide.css" % (toDir, name)

                if slideFile in files:
                    files.remove(slideFile)
                if slidetemplate in files:
                    files.remove(slidetemplate)
                if slidejs in files:
                    files.remove(slidejs)
                if slidecss in files:
                    files.remove(slidecss)


            zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            for file in files:
                arcname = file.split(toDir + "/")[1]
                zipFile.write(file, arcname)

            zipFile.close()

            contentFile = zipFilePath
            mimeType = self.iceContext.MimeTypes[".zip"]
            self.__response.setDownloadFilename(zipName.replace(" ", "_"))

        return contentFile, mimeType











