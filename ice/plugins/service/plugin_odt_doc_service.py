
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
import subprocess


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
        self.__includeExts = [".htm", ".odt", ".doc", ".docx", ".rtf", ".pdf", ".slide.htm", ".epub"]
    
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
	epub = self.__options.get("epub", False)
        mets = self.__options.get("mets", False)
        mods = self.__options.get("mods", mets)    # MODS always created with METS
        dc = self.__options.get("dc", False)
        rdf = self.__options.get("rdf", False)
        sourcelink = self.__options.get("sourcelink", "off")
        slidelink = self.__options.get("slidelink", "off")
	epub = self.__options.get("epub", False)
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
      	
	if epub:
		print "Running calibre"
		_, name, _ = fs.splitPathFileExt(filename)
		htmlFile = "%s.htm" % fs.absPath(name)
		epubFile = "%s.epub" % fs.absPath(name)
		command = """ebook-convert %s.htm %s.epub --chapter "//*[name()='h1']" --max-levels 0 """ % (htmlFile, epubFile) 
		print command
		retcode = subprocess.call([command] , shell=True)  
		if not(zip):
			return epubFile, "application/epub+zip"

        if zip or epub:
            _, name, _ = fs.splitPathFileExt(filename)
	    mainFile = None
            #name = name.replace(" ", "_")
            zipext = "zip"
            if epub:
 		zipext = "epub"
		
            zipName = "%s.%s" % (name, zipext)
           
            zipFilePath = fs.absPath(zipName)
            
            mediaFiles = fs.glob("%s/%s_files/*" % (toDir, name))
            skinFiles = fs.glob("%s/skin/*" % (toDir))
            fancyFiles = fs.glob("%s/skin/fancyzoom/*" % (toDir))
            otherMedia = fs.glob("%s/media/*" % (toDir))
            compoundMedia = fs.glob("%s/media/compound/*" % (toDir))
            files = []
            for mFile in mediaFiles:
                files.append(fs.absPath(mFile))
            if includeSkin and not(epub):
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
		if epub and ext == ".htm":
			html = fs.absPath(includeFile)
			xhtml = fs.absPath(includeFile) + ".xhtml"
			print "Running tidy"
			retcode = subprocess.call(["tidy", "-asxml", "-m", '-n', html])
			
		 	ds = DocSplitter(toDir,html,meta)
			contentDocs = ds.splitIt()
			
                elif fs.exists(includeFile):
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
            if slidelink == "off" or epub: #Hey why are we REMOVING stuff here? (ptsefton)
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
            if epub:
		#First file in the Zip must be mimetype and it must not be compressed
	    	zipFile.writestr("mimetype", "application/epub+zip")
                zipFile.getinfo("mimetype").compress_type = zipfile.ZIP_DEFLATED
                #Todo META-INF
	
		zipFile.writestr("META-INF/container.xml" ,"""<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>""")
 		

            epubFiles = []
            for file in files:
                arcname = file.split(toDir + "/")[1]
                if epub:
			epubFiles.append(arcname)
			arcname = "OEBPS/%s" % arcname
			
                try:
                    zipFile.write(file, arcname)
                except Exception,e:
                    print "Error in zipping file - %s: %s"% (file, str(e))
	    if epub:
		for i in range(0, len(contentDocs)):
			plainFileName = contentDocs[i][0].split(toDir + "/")[1]
			fullFilePath = contentDocs[i][0]
			epubFiles.append(plainFileName) #for manifest
			contentDocs[i][0] = plainFileName #for Toc
			arcname = "OEBPS/%s" % plainFileName
 			try:
                   		zipFile.write(fullFilePath, arcname)
                	except Exception,e:
                    		print "Error in zipping file - %s: %s"% (file, str(e))
			
		
	    #TODO - call the epub maker and get toc etc
	    if epub:
		mimeTypePluginClass = self.iceContext.getPluginClass("ice.mimeTypes")
		
		ep = EpubMaker(files=epubFiles, mimetypes=mimeTypePluginClass(), contentDocs=contentDocs, metadata=meta)
		zipFile.writestr("/OEBPS/content.opf", ep.content)	
		zipFile.writestr("/OEBPS/toc.ncx", ep.toc)
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

class EpubMaker(object):
	def __init__(self, files=[], metadata={}, mimetypes=None, contentDocs=["index.html"]):
		self.files = files
		self.meta = metadata
		self.mimetypes = mimetypes 
		self.contentDocs = contentDocs
		self.createToc()
        	
       		
	def createToc(self):
                
        
       		#### Creating toc.ncx ####
       		tocXml = ElementTree.Element("ncx", {"version": "2005-1", "xml:lang":"en", "xmlns":"http://www.daisy.org/z3986/2005/ncx/"})
		#tocXml = ElementTree.XML("""<ncx version="2005-1" xml:lang="en"></ncx>""")
		#tocXml.set("xmlns": "http://www.daisy.org/z3986/2005/ncx/")
		
		headNode = ElementTree.Element("head")
		tocXml.append(headNode)
		
		headNode.append(ElementTree.Element("meta", {"name": "dtb:uid", "content": "1"}))
		headNode.append(ElementTree.Element("meta", {"name": "dtb:depth", "content": "1"}))
		headNode.append(ElementTree.Element("meta", {"name": "dtb:totalPageCount", "content": "1"}))
		headNode.append(ElementTree.Element("meta", {"name": "dtb:maxPageNumber", "content": "1"}))
		headNode.append(ElementTree.Element("meta", {"name": "dtb:generator", "content": "ICE v2"}))
		
		#docTitle
		title = self.meta.get("title", "Untitled")
		print "Title: " + title
		docTitle = ElementTree.Element("docTitle")
		textNode = ElementTree.Element("text")
		textNode.text = title
		docTitle.append(textNode)
		tocXml.append(docTitle)
		
		#docAuthor
		
		
		#navMap
		navMap = ElementTree.Element("navMap")
		tocXml.append(navMap)
		

		#### Creating content.opf ####
		contentXml = ElementTree.Element("package", {"version": "2.0", "xmlns":"http://www.idpf.org/2007/opf",
		                                             "unique-identifier":"BookId"})
		
		metadataNode = ElementTree.Element("metadata", {"xmlns:dc": "http://purl.org/dc/elements/1.1/", 
		                                                "xmlns:opf": "http://www.idpf.org/2007/opf"})
		contentXml.append(metadataNode)
		
		#metadata information
		metadata = ElementTree.Element("dc:title")
		metadata.text = title
		metadataNode.append(metadata)
		
		metadata = ElementTree.Element("dc:language")
		metadata.text = "en-AU"
		metadataNode.append(metadata)
		
		for author in self.meta.get("authors", []):
			auth = author.get("name", "")
			print "Author: " + auth
			#content
			metadata = ElementTree.Element("dc:creator", {"opf:role":"aut"})
			metadata.text = auth
			metadataNode.append(metadata)
			#toc
			docAuthor = ElementTree.Element("docAuthor")
			textNode = ElementTree.Element("text")
			textNode.text = auth
			docAuthor.append(textNode)
			tocXml.append(docAuthor)
		
		metadata = ElementTree.Element("dc:publisher")
		metadata.text = "Publisher unknown"
		metadataNode.append(metadata)
		
		metadata = ElementTree.Element("dc:identifier", {"id":"BookId"})
		metadata.text = str(uuid.uuid1())
		metadataNode.append(metadata)
		
		#manifest
		manifest = ElementTree.Element("manifest")
		contentXml.append(manifest)
		
		spine = ElementTree.Element("spine", {"toc":"ncx"})
		
		playOrder = 1
		for c in self.contentDocs:
			print "CONTENT:" + repr(c)
			itemRef = ElementTree.Element("itemref", {"idref":c[0]})
			spine.append(itemRef)
			navPoint = ElementTree.Element("navPoint", {"id":c[0], "playOrder":repr(playOrder)})
			navLabel = ElementTree.Element("navLabel")	
			navPoint.append(navLabel)
			text = ElementTree.Element("text")
			text.text = c[1]
			navLabel.append(text)
			content = ElementTree.Element("content", {"src": c[0]})
			navPoint.append(content)
			playOrder = playOrder + 1
			navMap.append(navPoint);
		contentXml.append(spine)
		item = ElementTree.Element("item", {"id":"ncx", "href":"toc.ncx", "media-type":"application/x-dtbncx+xml"})
		manifest.append(item)

		#Don't think we need these - ptsefton
		#css = ElementTree.Element("item", {"id":"style", "href":"epub.css", "media-type":"text/css"})
		#manifest.append(css)
		for f in self.files:
			ext = os.path.splitext(f)[1]
			
			mime = self.mimetypes.get(ext)
                       
			item = ElementTree.Element("item", {"id":f, "href":f, "media-type":mime})
			manifest.append(item)


		self.content = ElementTree.tostring(contentXml)
		self.toc = ElementTree.tostring(tocXml)

class DocSplitter(object):
	def __init__(self, workingPath, docPath, meta):
		html = ElementTree.parse(docPath)
		print html
		
		divs = html.findall("//{http://www.w3.org/1999/xhtml}div")
		for div in divs:
			if div.get("class") == "body":
				self.body  = div.find("{http://www.w3.org/1999/xhtml}div")
			
		self.meta = meta	
		self.workingPath = workingPath
		self.epubTitlePageTemplate = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Title Page</title>
</head>
<body>
  
    

    <h1>Sample Book</h1>

    <h2>By Yoda47</h2>
 
</body>
</html>"""


		self.epubChapterTemplate = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Chapter 1</title>
</head>
<body>
  
</body>
</html>

"""
		
		self.docs = [] 
		self.anchors = dict()

	def splitIt(self, firstPass = True):
		
		
		def returnChapter(chapterTemplate = self.epubChapterTemplate):
			chapter = ElementTree.ElementTree(ElementTree.fromstring(chapterTemplate))
               		return (chapter, chapter.find("{http://www.w3.org/1999/xhtml}body"))

		def saveChapter(chbody, title, chapterNum):
			chFileName = "chapter%s.xhtml" % repr(chapterNum)
			chFilePath = os.path.join(self.workingPath,chFileName )
			chapter.find("//{http://www.w3.org/1999/xhtml}title").text = title
			if firstPass:
				#Find and remember anchors
				for a in chapter.findall("//{http://www.w3.org/1999/xhtml}a"):
					
					name = a.get("name")
					
					if name:
						self.anchors["#%s" % name] = chFileName
						print "Remembering name: " + name
				#Remove redundant Foonotes
				for s in chapter.findall("//{http://www.w3.org/1999/xhtml}span"): 
					if s.get("class") == "footnote-text":
						s.clear() #TODO figure out how to remove
					

			else:
				#rewrite links
				for a in chapter.findall("//{http://www.w3.org/1999/xhtml}a"): 
					href= a.get("href")
					
					if href != None and href.startswith("#") and self.anchors.has_key(href):
						newhref = "./%s%s" % (self.anchors[href], href)
						a.set("href", newhref)
						print "Changing link to name: " + newhref
				chapter.write(chFilePath)
				self.docs.append([chFilePath,title])
			

		
		chapterNum = 0	
		#First make a title page - content goes into this until we hit a heading
		(chapter, chbody) = returnChapter(self.epubTitlePageTemplate);
		
		title = self.meta.get("title", "Untitled")
		chbody.find("{http://www.w3.org/1999/xhtml}h1").text = title
		authorNames = []
		for author in self.meta.get("authors", []):
			auth = author.get("name", "")
			authorNames.append(auth)
		chbody.find("{http://www.w3.org/1999/xhtml}h2").text = ", ".join(authorNames)
		#TODO - Add metadata to our title page
			
		print "Starting split"
		for elementOfSomeKind in self.body.findall("*"):
			elementOfSomeKind.set("xmlns", "http://www.w3.org/1999/xhtml")
			if elementOfSomeKind.tag == "{http://www.w3.org/1999/xhtml}h1": #TODO: How to get text from title?
				
				saveChapter(chapter, title, chapterNum)
                                chapterNum = chapterNum + 1
				#HACK - probably need to change this all over to a better XML library
				r = re.compile("<.*?>")
				title = ElementTree.tostring(elementOfSomeKind)
				title = r.sub("", title)
				(chapter, chbody) = returnChapter();
			else:	
				#HACK serialize and parse to get the thing into the right namespace. Yes, yuck.
				#xhtmlElement = ElementTree.XML(ElementTree.tostring(elementOfSomeKind))
				chbody.append(elementOfSomeKind)

		saveChapter(chapter, title, chapterNum)
		#Do it again - this time writing out files
		if firstPass:
			self.splitIt(False)
		return self.docs

		
		
		
    
