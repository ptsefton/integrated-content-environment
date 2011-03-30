
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


from modsMetsCreator import ModsCreator, MetsCreator

pluginName = "ice.converter.odtDoc"
pluginDesc = "OpenOffice.org/Word converter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None




def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = OtdDocConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc


class OdtDocConverter(object):
    exts = [".odt", ".doc"]

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__includeExts = [".htm", ".odt", ".doc", ".pdf", ".slide.htm"]
        self.__OdtDocConverter = self.iceContext.getPlugin("ice.ooo.OdtDocConverter").pluginClass


    @property
    def isAvaliable(self):
        return True


    def convert(self, fromToObj, **options):
        """

        """
        # Note: 'templateString' is deprecated but still in use by Moodle
        template = options.get("template", options.get("templateString", None))
        if template == None or template == "":
            # make sure there is a default template
            # TODO check if template was uploaded
            template = None
            options["template"] = None
        options["includetitle"] = bool(options.get("includetitle", False))
        options["toc"] = bool(options.get("toc", False))

        fs = fromToObj.getToFileSystem()
        fromFile = fromToObj.getFromFile()


        app = self.__OdtDocConverter(self.iceContext, fs, template)
        status, htmlFile, _ = app.convert(fromFile, str(fs), options)

        if status == "ok":
            self.__removeLocalhostLinks(htmlFile, app.meta)
            contentFile, mimeType = self.__createPackage(fs, fromFile, app.meta)
            if contentFile == None:
                contentFile = htmlFile
                mimeType = self.iceContext.getMimeTypeForExt(".html")
        else:
            raise self.iceContext.IceException(status)

        return fs.readFile(contentFile), mimeType


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









