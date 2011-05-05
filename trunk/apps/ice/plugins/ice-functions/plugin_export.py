
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
import sys
from datetime import datetime
from request_data import ServerRequestData
from urlparse import urlparse, urlunparse



pluginName = "ice.function.export"
pluginDesc = "Export"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

Mets = None

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = export
    pluginClass = IceExport
    pluginInitialized = True
    plugin = iceContext.getPlugin("ice.mets")
    global Mets
    Mets = plugin.pluginClass
    return pluginFunc

def isPackage(self):    
    return self.isPackage   

# Export
def export(self, exportBaseName=None, exportCallback=None, toZipFile=None):
    downloadFilename = None
    fileName = None
    toRepository = False
    fullFileName = None
    
    path = self.packagePath
    if path=="":
        path = self.path
    
    xhtmlTemplateFilename = self.session.get("xhtmlTemplateFilename", self.defaultXhtmlTemplateFilename)
    templateName = self.iceContext.fs.split(xhtmlTemplateFilename)[1]
    templateName = self.iceContext.fs.splitExt(templateName)[0]
    if templateName=="template":
        templateName = "Default"
    
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
    
    print " fileName=", fileName
    print " (from:) path=", path
    print " (to:) toRepository=%s, fullFileName='%s'" % (toRepository, fullFileName)
    #print "Just testing..."
    #return
    
#    courseCode = self.get("coursecode", "")
#    courseNumber = self.get("coursenumber", "")
#    year = self.get("year", "")
#    semester = self.get("semester", "")
    
    ex = IceExport(self)
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
    print "Exported to '%s'" % fullFileName
    if downloadFilename is not None:
        print " downloadFilename='%s'" % downloadFilename
        r = (None, None, downloadFilename)
    else:
        r = fullFileName
    print
    return r
export.options = {"toolBarGroup":"publish", "position":46, "postRequired":True,
                "label":"Export", "title":"Export this package", "enableIf":True, #isPackage,
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
    
    def isDirectory(self, path):
        return self.__fs.isDirectory(path)
    
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
        return self.__fs.zip(to, fromPath)

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
            if not(self.isDirectory(fileName)):
                f = open(fileName, "wb")
                f.write(data)
                f.close()
        except Exception, e:
            print "********** ERROR failed to write file '%s' %s *********" % (fileName, str(e))
            print " dir='%s'" % dir
            print " dir=", self.split(fileName)
            print "  %s, %s" % (self.exists(dir), self.isFile(dir))
    
    def read(self, fileName):
        f = open(fileName, "rb")
        data = f.read()
        f.close()
        return data
    


class IceExport:
    """ iceExport class. """
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
            print "\n--- Export(fromPath='%s', toPath='%s') ---" % (fromPath, to)
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
                print "zipping exported data:", to
#                if toRepository:
#                    self.rep.getItem(to).zipFromTempDir(tempDir)
#                else:
                    #print " zipping from toPath='%s', to='%s'" % (toPath, to)
                self.io.write(to, "")
                self.io.zipAll(to, fromPath=toPath)
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


    def __export(self, fromPath, toPath, templateName=None):
        # Note: Assumes that the manifest has been updated first (if using the manifest)
        manifestXmlStr = None
        manifestJson = None
        self.iceSite.updateManifest()
        imsManifest = self.iceSite.getImsManifest()
        if imsManifest is not None:
            manifestXmlStr = str(imsManifest)
            #
            manifest = self.iceSite.manifest
            manifestJson = manifest.asJSON(self.iceContext.jsonWrite)
        dom = None
        
        if not fromPath.endswith("/"):
            fromPath += "/"
        if not fromPath.startswith("/"):
            fromPath = "/" + fromPath
                
        mets = None
        fixupLinks = {}
        if manifestXmlStr!=None:
            ####################################################################
            print "Exporting a package"
            # Export a package

            ## process the manifest resource links first
            xml = self.iceContext.Xml(manifestXmlStr, [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
            for a in xml.getNodes("//x:resource/@href | //x:resource/x:file/@href"):
                href = a.getContent()
                if href is None:
                    continue
                protocol, netloc, path, param, query, fid  = urlparse(href)
                if href.startswith("/"):
                    newHRef = "_resources" + href
                    fixupLinks[href] = newHRef
                    a.setContent(newHRef)
                elif protocol=="http" or protocol=="https":
                    #if path.find("/media/")!=-1:
                    #    print "  external media content"
                    newHRef = "_resources" + urlunparse(("", "", path, param, query, fid))
                    fixupLinks[href] = newHRef
                    a.setContent(newHRef)
            rFixupLinks = {}
            for k,v in fixupLinks.iteritems():
                rFixupLinks[v] = k
                
            ## remove dc and rdf file href
            for file in xml.getNodes("//x:file[not(contains(@href,'skin'))]"):
                attr = file.getAttribute("href")
                if attr.endswith(".dc") or attr.endswith(".rdf"):
                    file.delete()

            manifestXmlStr = str(xml.getRootNode())
            xml.close()
            ##

            # copy the IMS manifest.xml
            #self.io.copy("manifest.xml", fromPath, toPath)
            self.io.write(self.io.join(toPath, "imsmanifest.xml"), manifestXmlStr)
            self.io.write(self.io.join(toPath, "manifest.json"), manifestJson)
            # and the DTD
            #check if the DTD is existed in the package
            dtdName = "imscp_rootv1p1.dtd"
            dtdPath = self.io.join("/", dtdName) 
            found = False
            if self.io.isFile(self.rep.getAbsPath(dtdPath)):
                fromDir = "/"
                found = True
            else:
                dtdPath = self.io.join("/skin", dtdName)
                if self.io.isFile(self.rep.getAbsPath(dtdPath)):
                    fromDir = self.rep.getAbsPath("/skin")
                    found = True
            if found:
                self.io.copy("imscp_rootv1p1.dtd", fromDir, toPath)
            else:
                print "--- %s file is not found in either root or skin folder---" % (dtdName)
            
            dom = self.iceContext.Xml(manifestXmlStr, [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
            hrefs = dom.getContents("//x:resource/x:file/@href")

            if self.makeObjectUrlLocal:
                self.objectFixup.setToPath(toPath)
            
            #create the METS xml
            now = datetime.now().isoformat() + 'Z'
            mets = Mets(self.iceContext, "METS_ICE", Mets.Helper.METS_NLA_PROFILE)
            mets.setCreateDate(now)
            mets.setLastModDate(now)
            mets.addDisseminator(Mets.Helper.MetsAgent.TYPE_INDIVIDUAL, "ICE User")
            mets.addCreator("ICE 2.0")
        else: # else EXPORT ALL
            print "Not in a package!"
            print "Will just export the lot! from='%s'" % fromPath
            hrefs = self.__getListOfAllFilesToExport(fromPath)
            hrefs = [ p[len(fromPath):] for p in hrefs]
        
        #for CD selected reading
        if templateName == "CD":
            pass

        # export all referenced content
        for relPath in hrefs:
            rPath = relPath
            #check for resized images
            match = re.match("(.*)_files/(.*)\.(.*)", relPath)
            if match:
                dirName = match.group(1)
                fileName = match.group(2)
                ext = match.group(3)
                if ext in [".jpg", ".png", ".gif", "jpeg", "ico"]:
                    htmlPath = self.io.join(fromPath, dirName + ".htm")
                    htmlItem = self.rep.getItemForUri(htmlPath)
                    data = self.iceSite.serve(htmlItem, ServerRequestData(htmlItem.uri))[0]
                    xml = self.iceContext.Xml(data)#, parseAsHtml=True)
                    imgSrc = '%s_files/%s' % (dirName, fileName)
                    imgNode = xml.getNode("//*[local-name()='img'][starts-with(@src, '%s')]" % (imgSrc))
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
                                imgNode = xml.getNode("//*[local-name()='img'][starts-with(@src, '%s')]" % (newImgName))
                                if imgNode is not None:
                                    rPath = imgNode.getAttribute("src")
                                    rPath = rPath.replace(newImgName, imgSrc)
                        #print data
                    xml.close()
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
                return data
#            if path.endswith("default.htm"):
#                print "*********** default.htm *********"
            result = self.__serve(item, self.io.join(toPath, rPath), linksFixup)
            if result == False:
                break
        if dom is not None:
            self.objectFixup.finished()
            dom.close()
        
        if mets is not None:
            #print "fromPath='%s'" % fromPath
            items = imsManifest.organizations.defaultOrganization.items
            self.__createMETS(mets, items, toPath)
            xml = mets.getXml()
            self.io.write(self.io.join(toPath, "mets.xml"), xml)
    

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
            if i.startswith("."):   # remove .svn and .ice folders from skin
                continue
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
                isSlide = item.getMeta("isSlide")==True
                isSlide = False
                isPdf = item.hasPdf
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
                if isPdf:
                    file = rawFile + ".pdf"
                    files.append(file)
                if isSlide:
                    file = rawFile + ".slide.htm"
                    files.append(file)
        return files

    
    def __serve(self, item, toFilename, linksFixup=None):
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
                try:
                    data = linksFixup(data)
                except Exception, e:
                    print "Invalid htm file: ", str(e)
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









