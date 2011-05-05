
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

""" """
import re
import os
from datetime import datetime
from request_data import ServerRequestData
from urlparse import urlparse, urlunparse
import zipfile, hashlib


pluginName = "ice.function.export.epub"
pluginDesc = "Export to Epub"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

Mets = None

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = exportEpub
    pluginClass = IceExportEpub
    pluginInitialized = True
    plugin = iceContext.getPlugin("ice.mets")
    global Mets
    Mets = plugin.pluginClass
    return pluginFunc

def isPackage(self):    
    return self.isPackage   

# Export
def exportEpub(self, exportBaseName=None, exportCallback=None, toZipFile=None):
    print "--- Export to ePub --- "
    downloadFilename = None
    fileName = None
    toRepository = False
    fullFileName = None
    currentTemplate = None
    
    path = self.packagePath
    if path=="":
        path = self.path
     
    templateName = "epub"
    currentTemplate = "template.xhtml"
    if self.session.has_key("xhtmlTemplateFilename"):
        currentTemplate = self.session["xhtmlTemplateFilename"]
    self.session["xhtmlTemplateFilename"] = "templates/" + templateName + ".xhtml"
    
    if self.iceContext.isServer and toZipFile is None:
        tempDir = self.iceContext.getTimedTempDirectory(hours=24)
        fileName = self.iceContext.fs.split(path.rstrip("/"))[1]
        fileName += "_" + templateName + ".zip"
        fileName = fileName.lower()
        toZipFile = self.iceContext.fs.join(str(tempDir), fileName)
        print "Server export - '%s'" % toZipFile
        downloadFilename = toZipFile
    item = self.rep.getItem(path)
    result = item.render(force=False, skipBooks=False)
    
    if toZipFile is not None and toZipFile.endswith(".zip"):
        fullFileName = toZipFile
    
    if fullFileName is None:
        if self.packagePath!="":
            print "Package Export"
            newPath = self.packagePath.lower()
            if newPath.find("packages/") > -1:
                newPath = path.split("packages/")[1]
            if newPath.find("package/") > -1:
                newPath = path.split("package/")[1]
            print
            if exportBaseName!=None:
                fileName = exportBaseName
            else:
                #fileName = self.iceContext.fs.split(path)[1]
                fileName = newPath.strip("/").replace("/", "_")
            fileName += "_" + templateName + ".zip"
            if (fileName==None) or (fileName==""):
                fileName = "export"
            fileName = fileName.lower()
            toRepository = True
            # toRepository is True, so keep the path relative
            fullFileName = self.iceContext.fs.join(self.rep.exportPath, fileName)
            
        else:
            print "Site Export"
            path = "/"    # if not inside a package then export from the root of the site (else self.path)
            fileName = self.rep.name
            if fileName is None or fileName=="":
                fileName = "export"        
            fileName = fileName.lower()
            toRepository = False    
            # toRepository is False, so we need an absolute path
            fullFileName = self.iceContext.fs.join(self.rep.exportPath, fileName)
            fullFileName = self.iceContext.fs.absPath(fullFileName)
    
    print " fileName=", self.iceContext.fs.splitExt(fileName)[0] + ".epub"
    print " (from:) path=", path
    print " (to:) toRepository=%s, fullFileName='%s'" % (toRepository, self.iceContext.fs.splitExt(fullFileName)[0] + ".epub")
    
    ex = IceExportEpub(self)
    ex.export(fromPath=path, to=fullFileName, toRepository=toRepository, \
                        exportCallback=exportCallback, templateName=templateName, get=self.get)
    
    #check_links(self)
    check_links = self.iceContext.getPlugin("ice.function.check_links")
    #check_links = self.iceContext.plugins.get("ice.function.check_links")
    if check_links is not None and check_links.pluginInitialized:
        check_links.pluginFunc(self)
    else:
        print "Warning: check_links not found or initialized!"
    
    self["title"] = "Exported"
    self["statusbar"] = "Exported <a href='%s'>%s</a>" % (fullFileName, fileName)
    print
    print "Exported to '%s.epub'" % self.iceContext.fs.splitExt(fullFileName)[0]
    if downloadFilename is not None:
        print " downloadFilename='%s'" % downloadFilename
        r = (None, None, downloadFilename)
    else:
        r = fullFileName
    print
    self.session["xhtmlTemplateFilename"] = currentTemplate
    return r

def isPackage(self):
    return self.isPackage

exportEpub.options = {"toolBarGroup":"publish", "position":60, "postRequired":True,
                "label":"Export to ePub", "title":"Export this package to ePub", "enableIf":isPackage,
                "destPath":"%(package-path)s"}




class IceIO(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__rep = iceContext.rep
    
    @property
    def rep(self):
        return self.__rep
    
    def abspath(self, path):
        return self.__fs.absPath(path)
    
    def join(self, *args):
        return self.__fs.join(*args).replace("\\", "/")
    
    def split(self, path):
        return self.__fs.split(path)
    
    def splitExt(self, path):
        return self.__fs.splitExt(path)
    
    def isFile(self, path):
        return self.__fs.isFile(path)
    
    def exists(self, path):
        return self.__fs.exists(path)
        
    def makeDirs(self, path):
        return self.__fs.makeDirectory(path)    
    
    def list(self, path):
        return self.__fs.list(path)
    
    def walk(self, path):
        return self.__fs.walk(path)
    
    def removeDir(self, path):
        return self.__fs.delete(path)
    
    def remove(self, file):
        try:
            self.__fs.delete(file)
            #print " deleted - '%s'" % file
        except:
            print " failed to delete - '%s'" % file
    
    def createTempDir(self):
        return self.__fs.createTempDirectory()
    
    def zipAll(self, to, fromPath):
        return self.__zip(to, fromPath)
    
    def __zip(self, toZipFile, path="./"):
        ### part of epub requirement, the mimetype need to be the first entry of the zip file
        """ zip all of the content of the given path """
        dir = self.abspath(path)
        toZipFile = self.abspath(toZipFile)
        zf = zipfile.ZipFile(toZipFile, "w", zipfile.ZIP_DEFLATED)
        dir = dir.rstrip("/\\")
        for root, dirs, files in os.walk(dir):
            root = root.replace("\\", "/")
            #print "root: ", root
            for filename in files:
                #print "filename: ", filename
                zf.write(os.path.join(root, filename), \
                         os.path.join(root[len(dir)+1:], filename))
        zf.close()

    def copy(self, fileName, srcPath, destPath):
        data = self.__rep.getItem(self.join(srcPath, fileName)).read()
        if data!=None:
            self.write(self.join(destPath, fileName), data)

    def write(self, fileName, data):
        if fileName.endswith("/skin/images"):
            print "\n\n++++++++++++++"
            print " fileName='%s'" % fileName
        try:
            dir = self.split(fileName)[0]
            if not(self.exists(dir)):
                self.makeDirs(dir)
            #print "Writing file " + fileName
            f = open(fileName, "wb")
            f.write(data)
            f.close()
        except Exception, e:
            print "********** ERROR failed to write file '%s' %s *********" % (fileName, str(e))
            print " dir='%s'" % dir
            print "  %s, %s" % (self.exists(dir), self.isFile(dir))
    
    def read(self, fileName):
        f = open(fileName, "rb")
        data = f.read()
        f.close()
        return data
    


class IceExportEpub:
    """ iceExport Epub class. """
    def __init__(self, iceSite):
        # iceSite usage:
        #    iceSite.rep
        #    iceSite.clone()
        #    iceSite.preRenderCallback
        #    iceSite.serve(item)
        #    and maybe its dictionary e.g. iceSite["toolbar"] = "<span/>"
        self.iceContext = iceSite.iceContext
        self.io = IceIO(iceSite.iceContext)
        self.rep = iceSite.iceContext.rep
        self.iceSite = iceSite.clone()
        self.iceSite.exportVersion = True
        self.includeSource = iceSite.includeSource
        self.objectFixup = FixupObjectUrls(self.io)
        self.__makeObjectUrlLocal = False
    
    def __getMakeObjectUrlLocal(self):
        return self.__makeObjectUrlLocal
    def __setMakeObjectUrlLocal(self, value):
        self.__makeObjectUrlLocal = value
    makeObjectUrlLocal = property(__getMakeObjectUrlLocal, __setMakeObjectUrlLocal)
    
    def export(self, fromPath, to, toRepository=False, exportCallback=None, deleteFirst=True, templateName=None, get=None):
        #print "*EXPORT export(fromPath='%s', to='%s', toRepository=%s, exportCallback='%s', deleteFirst=%s" \
        #        % (fromPath, to, toRepository, exportCallback, deleteFirst)
        self.iceSite.preRenderCallback = self.__preRenderMethod
        try:
            print "\n--- Export(fromPath='%s', toPath='%s') ---" % (fromPath, self.iceContext.fs.splitExt(to)[0] + ".epub")
            tempDir = None
            if toRepository and not to.lower().endswith(".zip"):
                to += ".zip"
            if self.io.splitExt(to)[1]==".zip":
                tempDir = self.io.createTempDir()
                toPath = str(tempDir)
            else:
                toPath = to
            if not fromPath.endswith("/"):
                fromPath += "/"
            
            if deleteFirst:
                self.io.removeDir(toPath)
            if not(self.io.exists(toPath)):
                self.io.makeDirs(toPath)
            
            if callable(exportCallback):
                try:
                    obj = exportCallback(self.iceSite, toPath)
                    if obj is not None and hasattr(obj, "makeObjectUrlLocal"):
                        self.makeObjectUrlLocal = obj.makeObjectUrlLocal
                except Exception, e:
                    print "##########################"
                    print "ERROR in exportCallback - " + str(e)
                    print "##########################"
            
            #------------------------------
            #          Export
            self.__export(fromPath, toPath, templateName=templateName) 
            #------------------------------
                
            #------------------
            # Clean up
            #------------------
            if tempDir!=None:
                print "zipping exported data:", self.iceContext.fs.splitExt(to)[0] + ".epub"
#                if toRepository:
#                    self.rep.getItem(to).zipFromTempDir(tempDir)
#                else:
                    #print " zipping from toPath='%s', to='%s'" % (toPath, to)
                self.io.write(to, "")
                self.io.zipAll(to, fromPath=toPath)
                self.iceContext.fs.move(to, self.iceContext.fs.splitExt(to)[0] + ".epub")
                tempDir.delete()
                print "finished zipping exported data"
            print "--- Finished exporting ---\n"
            
            if not self.iceContext.isServer:
                try:
                    absPath = self.rep.exportPath
                    if hasattr(os, "startfile"):
                        if self.iceContext.isWindows:
                            os.startfile(absPath.replace("/", "\\"))
                        else:
                            os.startfile(absPath)
                    elif self.iceContext.isLinux:
                        command = "nautilus \"%s\" &" % absPath
                        os.system(command)
                    elif self.iceContext.isMac:
                        os.system("open \"%s\"" % absPath)
                except Exception, e:
                    pass
           
        except Exception, e:
            self.iceSite.preRenderCallback = None
            raise
        self.iceSite.preRenderCallback = None

    def __getManifestItem(self, manifestXml):
        itemRefDict = {}
        orderedItem = []
        
        packageTitleNode = manifestXml.getNode("//x:organization/x:title")
        packageTitleStr = "[Untitled]"
        if packageTitleNode:
            packageTitleStr = packageTitleNode.getContent() 
        
        itemNodes = manifestXml.getNodes("//x:item")
        for itemNode in itemNodes:
            isVisible = itemNode.getAttribute("isvisible")
            if isVisible=="true":
                identifierref = itemNode.getAttribute("identifierref")
                
                itemTitle = "[Untitled]"
                for child in itemNode.getChildren():
                    if child.getName() == "title":
                        itemTitle = child.getContent()
                
                fileNode = manifestXml.getNode("//x:resource[@identifier='%s']" % identifierref)
                href = fileNode.getAttribute("href")
                
                itemRefDict[href] = itemTitle, identifierref, fileNode
                orderedItem.append(href)
        
        return packageTitleStr, itemRefDict, orderedItem

    
    def __createMetaINF(self, containerFileName):
        containerStr = """<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
        xml = self.iceContext.Xml(containerStr)
        self.io.write(containerFileName, str(xml))
        xml.close()
        
    def __epub(self, toPath, manifestXmlStr):
        mimeTypePluginClass = self.iceContext.getPluginClass("ice.mimeTypes")
        mimeTypePluginClass = mimeTypePluginClass()
        
        #Try to use element tree
        from xml.etree import ElementTree as ElementTree
        
        manifestXml = self.iceContext.Xml(manifestXmlStr, [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
        packageTitle, fileNodeDict, orderedItem = self.__getManifestItem(manifestXml)
        
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
        docTitle = ElementTree.Element("docTitle")
        textNode = ElementTree.Element("text")
        textNode.text = packageTitle
        docTitle.append(textNode)
        tocXml.append(docTitle)
        
        #docAuthor
        docAuthor = ElementTree.Element("docAuthor")
        textNode = ElementTree.Element("text")
        textNode.text = "ICE v2"
        docAuthor.append(textNode)
        tocXml.append(docAuthor)
        
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
        metadata.text = packageTitle
        metadataNode.append(metadata)
        
        metadata = ElementTree.Element("dc:language")
        metadata.text = "en-AU"
        metadataNode.append(metadata)
        
        metadata = ElementTree.Element("dc:creator", {"opf:role":"aut"})
        metadata.text = "ICE"
        metadataNode.append(metadata)
        
        metadata = ElementTree.Element("dc:publisher")
        metadata.text = "University of Southern Queensland"
        metadataNode.append(metadata)
        
        metadata = ElementTree.Element("dc:identifier", {"id":"BookId"})
        metadata.text = packageTitle
        metadataNode.append(metadata)
        
        #manifest
        manifest = ElementTree.Element("manifest")
        contentXml.append(manifest)
        
        spine = ElementTree.Element("spine", {"toc":"ncx"})
        contentXml.append(spine)
        
        item = ElementTree.Element("item", {"id":"ncx", "href":"toc.ncx", "media-type":"text/xml"})
        manifest.append(item)
        css = ElementTree.Element("item", {"id":"style", "href":"epub.css", "media-type":"text/css"})
        manifest.append(css)
            
        hrefs=[]
        
        count = 1
        #item for toc, itemref and spine for content
        #Currently only one level
        newNameDict = {}
        for itemRef in orderedItem:
            print "-- processing: ", itemRef
            itemTitle, identifierref, node = fileNodeDict[itemRef] 
            path, name, ext = self.iceContext.fs.splitPathFileExt(itemRef)
            newName = self.iceContext.fs.join(path, "item-%s%s" % (identifierref, ext)).replace("/", "_").replace(" ", "_")
            newNameDict[itemRef] = newName            
            resourceNode = manifestXml.getNode("//x:resource[@identifier='%s']" % identifierref)
            src = resourceNode.getAttribute("href")
            path, name, srcExt = self.iceContext.fs.splitPathFileExt(src)
            srcMimeType = mimeTypePluginClass.get(srcExt)
            
            imageHtmlName = None
            if srcMimeType == "application/pdf":
                pass #pdf file do nothing
            elif srcMimeType.startswith("image"):
                #create the html file...
                htmlStr = """<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en'>
                <head><title>%s</title></head>
                <body><div><span>%s</span></div>
                <div><img src='%s' alt='%s'/></div>
                </body>
                </html>""" 
            #if srcMimeType != "application/pdf":
            if srcMimeType.find("htm")>-1 or srcMimeType.startswith("image"):
                #content
                excludedFile = True
                for fileNode in node.getChildren():
                    if fileNode and fileNode.getAttribute("href"):
                        href = fileNode.getAttribute("href") 
                        path, name, ext = self.iceContext.fs.splitPathFileExt(href)
                        name = hashlib.md5(name).hexdigest()
                        newHref = newName
                        if href != itemRef:
                            newHref = self.iceContext.fs.join(path, "item-%s%s" % (name, ext))
                        mimeType = "application/xhtml+xml"
                        
                        if (mimeTypePluginClass.get(ext)!="text/html"):
                            mimeType = mimeTypePluginClass.get(ext)
                        
                        if (mimeType.find("image")>-1 or href.find("htm")>-1):
                            if not newNameDict.has_key(href):
                                newNameDict[href] = newHref
                            
                            if srcMimeType.startswith("image") and mimeType.startswith("image"):
                                imageHtmlName = self.iceContext.fs.join(path, "item-%s.htm" % name)
                                htmlStr = htmlStr % (itemTitle, packageTitle, newHref, newHref)
                                self.io.write("%s/OEBPS/%s" % (toPath, imageHtmlName), str(htmlStr))  
                            
                            #if not href.endswith(".pdf"):
                            excludedFile = False
                            hrefs.append(href)
                            itemNode = ElementTree.Element("item", {"media-type":mimeType,
                                                                    "href": newHref})
                            manifest.append(itemNode)
                            if href == itemRef:
                                itemNode.set("id", "%s" % newName)
                            else:
                                itemNode.set("id", "%s" % newHref.replace("/", "_").replace(" ", "_"))
                            if srcMimeType.startswith("image") and mimeType.startswith("image"):
                                #put the generated html file...
                                imageItemNode = ElementTree.Element("item",
                                                                    {"id":"%s" % imageHtmlName,
                                                                     "media-type":"application/xhtml+xml",
                                                                     "href":"%s" % imageHtmlName})
                                manifest.append(imageItemNode)
                                
                if not excludedFile:
                    #toc
                    navPoint = ElementTree.Element("navPoint", {"class":"chapter", "id":"%s" % newName, 
                                                                "playOrder":"%s" % count})
                    navMap.append(navPoint)
                    parent = navPoint
                    
                    navLabel = ElementTree.Element("navLabel")
                    navPoint.append(navLabel)
                    textNode = ElementTree.Element("text")
                    textNode.text = itemTitle
                    navLabel.append(textNode)
                    content = ElementTree.Element("content")
                    navPoint.append(content)
                    if imageHtmlName:
                        content.set("src", imageHtmlName)
                    else:
                        content.set("src", newName)
                
                itemRefNode = ElementTree.Element("itemref")
                spine.append(itemRefNode)
                if imageHtmlName:
                    itemRefNode.set("idref", "%s" % imageHtmlName)
                else:
                    #itemRefNode.set("idref", "item-%s" % identifierref)
                    itemRefNode.set("idref", "%s" % newName)
                
                count +=1
         
        tocTree = ElementTree.ElementTree(tocXml)
        tocTree.write("%s/OEBPS/toc.ncx" % toPath, "UTF-8")
        
        contentTree = ElementTree.ElementTree(contentXml)
        contentTree.write("%s/OEBPS/content.opf" % toPath, "UTF-8")
        
        manifestXml.close()
        
        return hrefs, newNameDict

    def __export(self, fromPath, toPath, templateName=None):
        # Note: Assumes that the manifest has been updated first (if using the manifest)
        manifestXmlStr = None
        self.iceSite.updateManifest()
        imsManifest = self.iceSite.getImsManifest()
        if imsManifest is not None:
            manifestXmlStr = str(imsManifest)
        
        if not fromPath.endswith("/"):
            fromPath += "/"
        if not fromPath.startswith("/"):
            fromPath = "/" + fromPath
                
        mets = None
        fixupLinks = {}
        hrefs = []
        
        if manifestXmlStr!=None:
            ####################################################################
            print "Exporting a package"
            
            ## Create META-INF/container.xml
            self.__createMetaINF("%s/META-INF/container.xml" % (toPath))
            self.io.write("%s/mimetype" % (toPath), "application/epub+zip")
            
            css = """/* Style Sheet */
/* This defines styles and classes used in the book */
body { margin-left: 5%; margin-right: 5%; margin-top: 5%; margin-bottom: 5%; text-align: justify; }
pre { font-size: x-small; }
h1 { text-align: center; }
h2 { text-align: center; }
h3 { text-align: center; }
h4 { text-align: center; }
h5 { text-align: center; }
h6 { text-align: center; }

.CI {
    text-align:center;
    margin-top:0px;
    margin-bottom:0px;
    padding:0px;
    }
.center   {text-align: center;}
.smcap    {font-variant: small-caps;}
.u        {text-decoration: underline;}
.bold     {font-weight: bold;}
"""
            self.io.write("%s/OEBPS/epub.css" % (toPath), css)  
            
            hrefs, newNameDict = self.__epub(toPath, manifestXmlStr)
        
        # export all referenced content
        for relPath in hrefs:
            #check for resized images
            match = re.match("(.*)_files/(.*)\.(.*)", relPath)
            if match:
                dirName = match.group(1)
                fileName = match.group(2)
                htmlPath = self.io.join(fromPath, dirName + ".htm")
                htmlItem = self.rep.getItemForUri(htmlPath)
                data = self.iceSite.serve(htmlItem, ServerRequestData(htmlItem.uri))[0]
                
                xml = self.iceContext.Xml(data, parseAsHtml=True)
                imgSrc = '%s_files/%s' % (dirName, fileName)
                imgNode = xml.getNode("//img[starts-with(@src, '%s')]" % (imgSrc))
                #TODO might be multiple images resized differently??
                if imgNode is not None:
                    rPath = imgNode.getAttribute("src")
                else:
                    #For those files nested in directory
                    if dirName.find("/")>-1:
                        dirNameSplit = dirName.split("/")
                        newDirName = dirNameSplit[len(dirNameSplit)-1]
                        if newDirName != '':
                            newImgName = '%s_files/%s' % (newDirName, fileName)
                            imgNode = xml.getNode("//img[starts-with(@src, '%s')]" % (newImgName))
                            if imgNode is not None:
                                rPath = imgNode.getAttribute("src")
                                rPath = rPath.replace(newImgName, imgSrc)
                xml.close()
            else:
                rPath = relPath
            if rPath.startswith("_resources/"):
                if rPath.startswith("_resources/rep."):
                    url = rFixupLinks.get(rPath)
                    session = self.iceSite.session
                    username, password = session.username, session.password
                    headers = {"username":username, "password":password}
                    data = self.iceContext.wget(url, "", headers)
                    #data = self.iceContext.wget(url+"/_zipped", "", headers)
                    self.io.write(self.io.join(toPath, rPath), data)
                    continue
                else:
                    path = rPath[len("_resources"):]
            else:
                if rPath.startswith("/"):
                    rPath = rPath[1:]
                path = self.io.join(fromPath, rPath)
            # export the items
            item = self.rep.getItemForUri(path)
            def linksFixup(data):
                #fixupLinks, rFixupLinks
                depth = (len(rPath.split("/"))-1)
                #print "\n linksFixup of rPath='%s'  %s" % (rPath, depth)
                HtmlLinks = self.iceContext.getPluginClass("ice.HtmlLinks")
                htmlLinks = HtmlLinks(self.iceContext, data)
                relOutSideOfPackage = (depth+1)*"../"
                for att in htmlLinks.getUrlAttributes():
                    url = att.url
                    if url.startswith(relOutSideOfPackage):
                        #print "****** out side of package url='%s'" % url
                        # OK make this link absolute
                        fromPathParts = fromPath.strip("/").split("/")
                        u = (len(url.split("../"))-1)-depth
                        url = "/" + "/".join(fromPathParts[:-u]) + "/" + url.strip("../")
                    if fixupLinks.has_key(url):
                        att.url = (depth*"../") + fixupLinks.get(url)
                        #print "  url=%s, url=%s" % (url, att.url)
                data = str(htmlLinks) 
                
                htmlXml = self.iceContext.Xml(data) #, parseAsHtml=True)
                #Add xmlns in the html tag
                #xmlns="http://www.w3.org/1999/xhtml"
                htmlNode = htmlXml.getNode("//*[local-name()='html']")
#                if htmlNode.getAttribute("xmlns") is None:
#                    htmlNode.setAttribute("xmlns", "http://www.w3.org/1999/xhtml")

                headNode = htmlXml.getNode("//*[local-name()='head']")
                if headNode:
                    linkCss = htmlXml.createElement("link")
                    linkCss.setAttribute("rel", "stylesheet")
                    linkCss.setAttribute("href", "epub.css")
                    headNode.addChild(linkCss)
                
                #remove meta tag
#                metaNodes = htmlXml.getNodes("//*[local-name()='meta']")
#                for metaNode in metaNodes:
#                    metaNode.remove()
#                
#                #remove style tag
#                styleNodes = htmlXml.getNodes("//*[local-name()='style']")
#                for styleNode in styleNodes:
#                    styleNode.remove()
#                
#                #remove all class and style attribute
#                classOrStyleNodes = htmlXml.getNodes("//@style | //@class")
#                for classOrStyleNode in classOrStyleNodes:
#                    node = classOrStyleNode.getParent()
#                    if node:
#                        node.removeAttribute("style")
#                        node.removeAttribute("class")
#                        
#                #remove all ids generated from ICE?
#                idNodes = htmlXml.getNodes("//@id")
#                for idNode in idNodes:
#                    node = idNode.getParent()
#                    if node:
#                        node.removeAttribute("id")
                    
                #remove all name in a href as well as href with #
                #ahrefs = htmlXml.getNodes("//*[local-name()='a' and @name!='']")
                ahrefs = htmlXml.getNodes("//*[local-name()='a']")
                for a in ahrefs:
                    if a.getAttribute("name"):
                        a.removeAttribute("name")
                    href = a.getAttribute("href")
                    if href and newNameDict.has_key(href):
                        #a.removeAttribute("href")
                        a.setAttribute("href", newNameDict[href])
                    elif href and href.find("#")>-1:
                        text = a.getContent()
                        if a.getParent():
                            p = a.getParent()
                            c = p.getContent()
                            try:
                                a.remove()
                            except Exception, e:
                                print "***** ERROR removing <a> - '%s'" % str(e)
                            p.setContent("%s %s" % (c, text))
                
                ### fix up the image src (ignore object for now....
                imgs = htmlXml.getNodes("//*[local-name()='img']")
                for img in imgs:
                    src = img.getAttribute("src")
                    if src and newNameDict.has_key(src):
                        #img.removeAttribute("src")
                        img.setAttribute("src", newNameDict[src])
                
                
                ### Do not allow p inside span **normally only happen for foodnote or endnote
                ### with structure: <div><span><p>1 Vestibulum ante ipsum primis in faucibus 1</p></span></div>
                ps = htmlXml.getNodes("//*[local-name()='p']")
                for p in ps:
                    parent = p.getParent()
                    if parent and parent.getName()=="span":
                        parentParent = parent.getParent()
                        if parentParent and parentParent.getName()=="div":
                            parent.getParent().addChild(p.copy())
                            parent.remove()
                    
                data = str(htmlXml)
                
                htmlXml.close()
                
                return data
            
            if newNameDict.has_key(rPath):
                rPath = newNameDict[rPath]
            result = self.__serve(item, self.io.join(toPath + "/OEBPS", rPath), linksFixup)
            if result == False:
                break
        

    def __createMETS(self, mets, items, toPath, depth=0):
        div = mets.addDiv("issue", "")
        for item in items:
            if item.href.startswith("/") or item.href.startswith("http:") or \
                    item.href.startswith("https:"):
                print "__createMETS() skipping '%s'" % item.href
            else:
                try:
                    self.__processItem(mets, item, toPath, depth, div)
                except Exception, e:
                    print "Exception in __createMETS() - '%s'" % str(e)

    
    def __processItem(self, mets, item, toPath, depth, parentDiv=None):
        mods = self.iceContext.ElementTree.Element("{%s}mods" % Mets.Helper.MODS_NS)
        modsTitleInfo = self.iceContext.ElementTree.SubElement(mods, "{%s}titleInfo" % Mets.Helper.MODS_NS)
        modsTitle = self.iceContext.ElementTree.SubElement(modsTitleInfo, "{%s}title" % Mets.Helper.MODS_NS)
        modsTitle.text = item.title
        #dmdSec = mets.addDmdSecRef("dmdSec1", "URL", "MODS", "mods.xml")
        dmdId = "dmdSec-%s" % item.identifier
        dmdSec = mets.addDmdSecWrap(dmdId, "MODS", mods)
        fileGrp = mets.addFileGrp("Original")
        file = mets.addFile(fileGrp, toPath + "/" + item.href, item.href, dmdId, "")
        if depth > 0:
            type = "article"
        else:
            type = "section"
        div = mets.addDiv(type, dmdSec.id, parentDiv)
        mets.addFptr(div, file.id)
        for subItem in item.items:
            self.__processItem(mets, subItem, toPath, depth + 1, div)
    

    def __getListOfAllFilesToExport(self, fromPath):
        # get root skin files
        rootSkinFiles = []
        l = self.io.list(self.rep.getAbsPath("/skin"))
        for i in l:
            if not i.endswith("/"):
                rootSkinFiles.append(i)
            else:
                l2 = self.io.list(self.rep.getAbsPath("/skin/" + i))
                for i2 in l2:
                    rootSkinFiles.append(i + i2)
        for dirpath, dirnames, filenames in self.io.walk(self.rep.getAbsPath("/skin")):
            # root only
            while len(dirnames)>0:
                dirnames.pop()
            for name in filenames:
                rootSkinFiles.append(name)
        files = ["/skin/"+f for f in rootSkinFiles]
        
        templateFullPath = self.rep.getAbsPath(self.rep.documentTemplatesPath)
        exportFullPath = self.rep.exportPath
        
        absPath = self.rep.getAbsPath(fromPath)
        #Add index pages for all dirs BUT exclude hiddenDirectories (except the skin directories)
        for dirpath, dirnames, filenames in self.io.walk(absPath):
            dirpath = dirpath.replace("\\", "/")
            
            for dir in list(dirnames):
                rep = self.io.rep
                if dir.startswith("."):    # Exclude hidden directories
                    dirnames.remove(dir)
                    continue
                fullPath = self.io.join(dirpath, dir)
                # Exclude the templates path and the export's path (if it is located in the rep)
                if fullPath==templateFullPath or fullPath==exportFullPath:
                    dirnames.remove(dir)
                    continue
                # Exclude 'src' directories also
                if dir=="src":
                    dirnames.remove(dir)
            
            ## if dirpath is a package(root) path then add skin
            path = dirpath.replace(self.rep.getAbsPath("/"), "")
            if "manifest.xml" in filenames:
                # Add content from the root skin folder
                #print "'%s' is a package!" % path
                sfiles = [path + "skin/" + f for f in rootSkinFiles]
                files.extend(sfiles)
            #if path.endswith("/skin"):      # Add content from the root skin folder
            #    for fn in rootSkinFiles:
            #        if fn not in filenames:
            #            filenames.append(fn)
            
            filename = self.io.join(path, "default.htm")
            files.append(filename)
            # HACK - for now just add a toc.htm (may or may not exist)
            filename = self.io.join(path, "toc.htm")
            files.append(filename)
            
            # include all other content (files)
            for file in filenames:
                if file.startswith("myChanges_"):   # skip myChanges_files
                    continue
                file = self.io.join(path, file)  #####
                item = self.rep.getItem(file)
                if item is None:
                    if self.io.exists(file):
                        print "File '%s' exists but has no properties" % file
                        files.append(file)
                    continue
                images = item.getMeta("images")
#                isSlide = item.getMeta("isSlide")==True
#                isSlide = False
#                isPdf = item.hasPdf
                if images is None:
                    images = []
                #print "file='%s', images='%s', isSlide='%s', isPdf=%s" % (file, images, isSlide, isPdf)
                rawFile, ext = self.io.splitExt(file)
                #HACK This used to work but now fails with fatal exceptions when exporting RUBRIC content
                try:
                    for image in images:
                        files.append(self.io.join(rawFile + "_files", image))
                except Exception, e:
                    print "warning: %s" % str(e)
                if self.iceContext.oooConvertExtensions.count(ext) > 0:
                    ext = '.htm'
                    if self.includeSource:
                        files.append(file)    # include the source file
                    file = rawFile + ext
                files.append(file)
                
                #Look for PDF rendition
#                if isPdf:
#                    file = rawFile + ".pdf"
#                    files.append(file)
#                if isSlide:
#                    file = rawFile + ".slide.htm"
#                    files.append(file)
        return files

    
    def __serve(self, item, toFilename, linksFixup=None):
        if item.isDir:
            return True
        if item.isBinaryContent:
            data, mimeType = item.getBinaryContent()            
            if data is None:
                data = "404 '%s' not found!" % item.uri
            if mimeType is None:
                print " Unknown (or not supported) mimeType for '%s' (relPath='%s')" % (item.ext, item.relPath)
        else:
            data, mimeType = self.iceSite.serve(item, ServerRequestData(item.uri))[:2]
        if mimeType=="text/html":
            docType = self.__getDocType(data)
            if callable(linksFixup):
                data = linksFixup(data)
            data = self.objectFixup.htmlFixup(data, toFilename)
            data = self.__restoreDocType(data, docType)
        self.io.write(toFilename, data)
        if toFilename.endswith("/default.htm"):
            indexFilename = toFilename[:-len("default.htm")] + "index.html"
            self.io.write(indexFilename, data)
        return True


    def __preRenderMethod(self, iceSite):
        # HACK: Add <span/> to work around a firefox bug for empty elements
        iceSite["toolbar"] = "<span/>"        # remove the toolbar
        iceSite["statusbar"] = ""      # remove the statusbar
        iceSite["app-css"] = ""        # remove the application css

    def __getDocType(self, data):
        docType = None
        m = re.search(r"^(\s*\<\!.*?\>\s*)", data)
        if m:
            docType = m.groups()[0]
        return docType

    def __restoreDocType(self, data, docType):
        if docType is not None and docType!="" and not data.startswith(docType):
            data = docType + data
        return data

# HACK: make object elements data(url) references point to a local copy, so that
#    windows media files will work on CD export 
#       has to have an absolute path to the media file and NOT a relative path
class FixupObjectUrls(object):
    def __init__(self, iceIO):
        self.iceContext = iceIO.iceContext
        self.__io = iceIO
        self.__fixExtList = [".avi", ".wmv", ".wma", ".wav"]
        self.__toPath = None
        self.__manifestPath = None
        self.__fixupList = []
        self.__mediaFiles = {}
        #print "FixupObjectsUrls.__init__()"
    
    
    def setToPath(self, toPath):
        toPath = toPath.replace("\\", "/")
        if not toPath.endswith("/"):
            toPath += "/"
        self.__toPath = toPath
        self.__manifestPath = toPath + "manifest.xml"
        #print
        #print " to manifest path = '%s'" % self.__manifestPath
    
    
    def htmlFixup(self, htmlStrData, toPath):
        if self.__toPath is None:
            return htmlStrData
        
        #print
        #print "***************************************************"
        #print "ice_export.FixupObjectUrls.htmlFixup( toPath='%s')" % (toPath)
        
        toPath = self.__io.split(toPath)[0] + "/"
        toPath = toPath[len(self.__toPath):]
        xhtml = None
        if True:
            # Note: Also replace links within the object element that have been changed
            
            # match all between <object and </object>
            reObject = re.compile("<object\s.*?</object>", re.DOTALL)
            # match the attribute data='xxx' capturing the dataValue as 'data' (groupdict()) (and quoted with 'quot')
            #   groups()[0] + groups()[1] + groups()[2] + groups()[1]
            reObjData = re.compile("(?P<f><object\s[^>]*?data\s*=\s*)(?P<quot>'|\")(?P<data>.*?)(?P=quot)", re.DOTALL)
            #
            #   groups()[0] + groups()[3] + groups()[4] + groups()[3]
            pattern = "(?P<f><param\s[^>]*?name\s*=\s*(?P<q>'|\")(?P<name>src|movie|url)(?P=q)[^>]*?value\s*=\s*)(?P<quot>'|\")(?P<value>.*?)(?P=quot)"
            reParamValue = re.compile(pattern, re.DOTALL)
            #
            #   groups()[0] + groups()[1] + groups()[2] + groups()[1]
            reEmbedSrc = re.compile("(?P<f><embed\s[^>]*?src\s*=\s*)(?P<quot>'|\")(?P<src>.*?)(?P=quot)", re.DOTALL)
            #
            #   groups()[0] + groups()[3] + groups()[2]
            hrefOrSrc = re.compile("((href|src)\s*=\s*(?P<quot>'|\"))(?P<content>.*?)(?P=quot)", re.DOTALL)
            
            fixupList = {}
            def objectMethod(match):
                fixupList.clear()
                rdata = match.group()
                #print "objectMethod match.group()="
                #print rdata
                #print
                rdata = reObjData.sub(objDataMethod, rdata)
                rdata = reParamValue.sub(paramValueMethod, rdata)
                #rdata = reEmbedSrc.sub(embedSrcMethod, rdata)
                if fixupList!={}:
                    print
                    print "fixupList='%s'" % str(fixupList)
                    rdata = hrefOrSrc.sub(hrefOrSrcMethod, rdata)
                return rdata
            
            def hrefOrSrcMethod(match):
                groups = match.groups()
                content = groups[3]
                newUrl = fixupList.get(content, None)
                if newUrl is not None:
                    content = newUrl
                    #print "@@  ", groups[1], content, groups[3]
                else:
                    pass
                    #print "@@  ", groups[1], content, "Not Fixed"
                rdata = groups[0] + content + groups[2]
                return rdata
            
            def paramValueMethod(match):
                #print "paramValueMethod %s" % match.group()
                groups = match.groups()
                value = groups[4]
                r, data = testFixup(groups[4])
                if r:
                    #print "  fixup data='%s'" % data
                    #rdata = groups[0] + groups[3] + groups[4] + groups[3]
                    rdata = groups[0] + groups[3] + data + groups[3]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print "  ERROR"
                #    #print "    '%s'" % match.group()
                #    #print "    '%s'" % rdata
                #    #print "    groups='%s'" % str(groups)
                return rdata
            
            def objDataMethod(match):
                #print "objDataMethod %s" % match.group()
                groups = match.groups()
                r, data = testFixup(groups[2])
                if r:
                    #print " fixup data='%s'" % data
                    #rdata = groups[0] + groups[1] + groups[2] + groups[1]
                    rdata = groups[0] + groups[1] + data + groups[1]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print " ERROR"
                return rdata
            
            def embedSrcMethod(match):
                #print "embedSrcMethod %s" % match.group()
                groups = match.groups()
                r, data = testFixup(groups[2])
                if r:
                    #print " fixup data='%s'" % data
                    #rdata = groups[0] + groups[1] + groups[2] + groups[1]
                    rdata = groups[0] + groups[1] + data + groups[1]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print " ERROR"
                return rdata
            
            def testFixup(href):
                "Test if href needs to be fixed up"
                parts = href.split("?")
                url = parts[0]
                if self.__io.splitExt(url)[1] in self.__fixExtList:
                    content = href
                    parts = content.split("?")
                    url = parts[0]
                    if self.__io.splitExt(url)[1] in self.__fixExtList:
                        parts[0] = self.__io.split(url)[1]
                        toFile = toPath + self.__io.split(url)[1]
                        href = "?".join(parts)
                        x = self.__io.split(toFile)[0]
                        if x!="":
                            x += "/"
                        url = x + url
                        self.__fixupList.append( (url, toFile) )
                        if fixupList=={}:
                            fixupList[content] = href
                        #print "## %s - %s" % (content, href)
                        #print "##    %s - %s" % (url, toFile)
                    return True, href
                else:
                    return False, href
            
            htmlStrData = reObject.sub(objectMethod, htmlStrData)
        else:    
            # Note: Also replace links within the object element that have been changed
            try:
                xhtml = self.iceContext.Xml(htmlStrData)
                changed = False
                objNodes = xhtml.getNodes("//object")
                for objNode in objNodes:
                    nodes = objNode.getNodes("@data | param[@name='src' or @name='movie' or @name='url']/@value")
                    fixupList = {}
                    for n in nodes:
                        content = n.content
                        parts = content.split("?")
                        url = parts[0]
                        if self.__io.splitExt(url)[1] in self.__fixExtList:
                            if fixupList=={}:
                                print
                                print "==================="
                                print str(objNode)
                            parts[0] = self.__io.split(url)[1]
                            toFile = toPath + self.__io.split(url)[1]
                            n.content = "?".join(parts)
                            x = self.__io.split(toFile)[0]
                            if x!="":
                                x += "/"
                            url = x + url
                            self.__fixupList.append( (url, toFile) )
                            if fixupList=={}:
                                fixupList[content] = n.content
                            print "%s - %s" % (content, n.content)
                            print "    %s - %s" % (url, toFile)
                            changed = True
                    if fixupList!={}:
                        nodes = objNode.getNodes(".//@href | .//@src")
                        print len(nodes)
                        for n in nodes:
                            content = n.content
                            newUrl = fixupList.get(content, None)
                            if newUrl is not None:
                                n.content = newUrl
                                print n.getName(), content, n.content
                            else:
                                print n.getName(), content, "Not Fixed"
                        print "--------------"
                        print str(objNode)
                        print "==================="
                if changed:
                    htmlStrData = str(xhtml.getRootNode())            
            except Exception, e:
                print "XML error - '%s'" % str(e)
            if xhtml is not None:
                xhtml.close()
        
        #print " done ice_export.FixupObjectUrls.htmlFixup( toPath='%s')" % (toPath)
        return htmlStrData
    
    
    def finished(self):
        # now copy all referenced media files and fixup the manifest
        files = {}
        for f, t in self.__fixupList:
            self.__copy(self.__toPath + f, self.__toPath + t)
            files[self.__io.abspath(self.__toPath + f)] = None
        for f in files.keys():
            self.__io.remove(f)
        #print "FixupObjectsUrls.finished()"
    
    
    def __copy(self, fromFile, toFile):
        try:
            data = self.__io.read(fromFile)
            self.__io.write(toFile, data)
        except:
            print "Failed to copy from '%s' to '%s'" % (fromFile, toFile)









