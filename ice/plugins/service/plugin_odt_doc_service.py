
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

pluginName = "ice.service.ooo-word"
pluginDesc = "OpenOffice.org/Word conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

Mets = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    handler = OdtDocService(iceContext)
    pluginInitialized = True
    pluginClass = OdtDocService
    global Mets
    Mets = iceContext.getPlugin("ice.mets").pluginClass
    return handler

#ModsCreator(iceContext)
#ModsCreator.createFromMeta(meta) -> xmlString

class OdtDocService(object):
    @staticmethod
    def createModsFromMeta(iceContext, meta):
        modsCreator = ModsCreator(iceContext)
        return modsCreator.createFromMeta(meta)
    
    
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
    
    exts = [".odt", ".doc", ".docx", ".rtf"]
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__includeExts = [".htm", ".odt", ".doc", ".docx", ".rtf", ".pdf", ".slide.htm"]
    
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

        #print "template='%s'" % template
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
        
        docFilePath = tmpFs.absPath(filename)
        tmpFs.writeFile(filename, document)
        OdtDocConverter = self.iceContext.getPlugin("ice.ooo.OdtDocConverter").pluginClass
        app = OdtDocConverter(self.iceContext, tmpFs, template)
        status, htmlFile, _ = app.convert(docFilePath, toDir, options)
        
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
#===============================================================================
#                Don't know why following added in the first page. 
#                it is causing the problem in ice-service rendition.
#                comment for now
#===============================================================================
#                elif href.startswith("http://"):
#                    #Handle relative link, if it's a domain leave it as what it is
#                    #if file extension existed in mime type like http://test.htm, 
#                    #treat it as a relative link, strip the http://
#                    domain = href.split("/")[2]
#                    ext = self.iceContext.fs.splitExt(domain)[1]
#                    mimeType = self.iceContext.MimeTypes.get(ext)
#                    if (mimeType == None and domain.find(".") == -1) or (mimeType != None and mimeType!=""):
#                        newHref = href[7:]
#                        node.setAttribute("href", newHref)
#                        #if content have the same name as the domain, strip the http as well
#                        if (content.strip() == href.strip()):
#                            allChild = node.getChildren()
#                            if allChild is None or allChild == []:
#                                node.setContent(newHref)
#                            else:
#                                self.__setContentToLastChild(allChild, newHref)
#===============================================================================
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
        includeSkin = self.__options.get("includeSkin",False)
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
            #name = name.replace(" ", "_")
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
            if includeSkin:
                for sFile in skinFiles:
                    if not fs.isDirectory(sFile):
                        files.append(fs.absPath(sFile))
                for fFile in fancyFiles:
                    files.append(fs.absPath(fFile))
            for oFile in otherMedia:
                files.append(fs.absPath(oFile))
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
            if sourcelink == "off" or not sourcelink:
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
                try:
                    zipFile.write(file, arcname)
                except Exception,e:
                    print "Error in zipping file - %s: %s"% (file, str(e))
            zipFile.close()

            contentFile = zipFilePath
            mimeType = self.iceContext.MimeTypes[".zip"]
            self.__response.setDownloadFilename(zipName.replace(" ", "_"))
        
        return contentFile, mimeType


class ModsCreator(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.ElementTree = self.iceContext.ElementTree
    
    def createFromMeta(self, meta, returnAsString = True):
        template = """<?xml version="1.0" encoding="UTF-8"?>
<mods:mods xmlns:mods="%s">
</mods:mods>"""
        elem = self.ElementTree.XML(template % Mets.Helper.MODS_NS)
        title = self.__createElement("title")
        title.text = meta.get("title", "")
        elem.append(title)
        for author in meta.get("authors", []):
            authorName = author.get("name", "")
            name = self.__createElement("name", {"type":"personal"})
            elem.append(name)
            displayForm = self.__createElement("displayForm")
            displayForm.text = authorName
            role = self.__createElement("role")
            name.append(role)
            roleTerm = self.__createElement("roleTerm", {"type":"text"})
            roleTerm.text = "author"
            role.append(roleTerm)
            
            affiliation = author.get("affiliation", "")
            affil = self.__createElement("affiliation")
            affil.text = affiliation
            name.append(affil)
            
            email = author.get("email", "")
            
#        for authorName, authorInfo in meta.get("authors", {}).iteritems():
#            name = self.__createElement("name", {"type":"personal"})
#            elem.append(name)
#            displayForm = self.__createElement("displayForm")
#            displayForm.text = authorName
#            name.append(displayForm)
#            role = self.__createElement("role")
#            name.append(role)
#            roleTerm = self.__createElement("roleTerm", {"type":"text"})
#            roleTerm.text = "author"
#            role.append(roleTerm)
#            for infoKey, infoValue in authorInfo.iteritems():
#                if infoKey=="affiliation":
#                    affil = self.__createElement("affiliation")
#                    affil.text = infoValue
#                    name.append(affil)
#                elif infoKey=="email":
#                    pass
        abstract = meta.get("abstract", None)
        if abstract is not None:
            if abstract.lower().startswith("abstract:"):
                abstract = abstract[len("abstract:"):].strip()
            abstractElem = self.__createElement("abstract")
            abstractElem.text = abstract
            elem.append(abstractElem)
        keywords = re.split("[,\s]+", meta.get("keywords", ""))
        if keywords!=[]:
            subject = self.__createElement("subject")
            elem.append(subject)
            for keyword in keywords:
                lKeyword = keyword.lower()
                if lKeyword=="keywords:" or lKeyword==":":
                    continue
                topic = self.__createElement("topic")
                topic.text = keyword
                subject.append(topic)
        
        if returnAsString:
            return self.__tostring(elem)
        else:
            return elem
    
    def __tostring(self, elem):
        return self.ElementTree.tostring(elem)
    
    def __createElement(self, tag, attrs={}):
        for key, value in attrs.iteritems():
            del attrs[key]
            attrs["{%s}%s" % (Mets.Helper.MODS_NS, key)] = value
        return self.ElementTree.Element("{%s}%s" % (Mets.Helper.MODS_NS, tag), attrs)



class MetsCreator(object):
    def __init__(self, iceContext, includeExts):
        self.iceContext = iceContext
        self.mets = Mets(iceContext, "ICE-METS", Mets.Helper.METS_NLA_PROFILE)
        self.__includeExts = includeExts
    
    
    def createFromMeta(self, basePath, meta, inline = True):
        fs = self.iceContext.FileSystem(basePath)
        
        creationDate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.mets.setCreateDate(creationDate)
        self.mets.setLastModDate(creationDate)
        
        self.mets.addDisseminator(Mets.Helper.MetsAgent.TYPE_INDIVIDUAL, "ICE User")
        self.mets.addCreator("ICE 2.0")
        
        fileGrp = self.mets.addFileGrp("Original")
        div1 = self.mets.addDiv("document", "dmdSec1")
        
        modsCreator = ModsCreator(self.iceContext)
        if inline:
            modsData = modsCreator.createFromMeta(meta, returnAsString = False)
            dmdSec1 = self.mets.addDmdSecWrap("dmdSec1", "MODS", modsData)
        else:
            dmdSec1 = self.mets.addDmdSecRef("dmdSec1", "URL", "MODS", fs.absPath("mods.xml"))
        
        dirs, files = fs.listDirsFiles(basePath)
        for file in files:
            _, ext = fs.splitExt(file)
            if ext in self.__includeExts:
                if fs.exists(file):
                    filePath = fs.absPath(file)
                    file1 = self.mets.addFile(fileGrp, filePath, file, dmdSec1.id,
                                              wrapped = inline)
                self.mets.addFptr(div1, file1.id)
        
        div2 = self.mets.addDiv("media", parentDiv = div1)
        for dir in dirs:
            if dir.endswith("_files"):
                for file in fs.listFiles(dir):
                    relPath = "%s/%s" % (dir, file)
                    file2 = self.mets.addFile(fileGrp, filePath, relPath,
                                              wrapped = inline)
                    self.mets.addFptr(div2, file2.id)
        
        return self.mets.getXml()
   
