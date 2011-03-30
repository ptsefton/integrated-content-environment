
#    Copyright (C) 2010  Distance and e-Learning Centre,
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

"""

Note: the following parameters need to be added to the config.xml's settings section:
    var name="mediaServerTestPattern" type="string"
            value="http://mediarep-dev-vip.usq.edu.au/media" />
    <var name="mediaServerExportPath" type="string" value="/media/video/" />
    <var name="mediaServerSsoParam" type="string" value="ssoId=USQSSO&amp;accept=true" />
    <var name="mediaServerPublicKey" type="string" value="iceExport" />
    <var name="mediaServerPrivateKey" type="string" value="-SecretKey-" />
    <var name="mediaServerFlashPlayer" type="string"
            value="http://mediarep-dev-vip.usq.edu.au/media/default/mediaplayer/player.swf"/>
    <var name="mediaServerSupportFiles" type="array"
      value="http://mediarep-dev-vip.usq.edu.au/media/default/js/modernizr-1.5.min.js, http://mediarep-dev-vip.usq.edu.au/media/default/mediaplayer/jwplayer.js, http://mediarep-dev-vip.usq.edu.au/media/default/mediaplayer/swfobject.js"/>

"""


import re
import os
from hashlib import md5
from datetime import datetime
from request_data import ServerRequestData
from urlparse import urlparse, urlunparse
import string

from directHelper import *

pluginName = "ice.function.exportCD"
pluginDesc = "CD Export"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

Mets = None

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = exportCD
    pluginClass = IceCDExport
    pluginInitialized = True
    
    path = iceContext.fs.split(__file__)[0]
    IceCDExport.myPath    = path
    IceCDExport.HtmlTemplate = iceContext.HtmlTemplate
    
    global Mets
    plugin = iceContext.getPlugin("ice.mets")
    Mets = plugin.pluginClass
    return pluginFunc

def isPackage(self):
    return self.isPackage

def displayIf(self):
    xhtmlTemplateFilename = self.session.get("xhtmlTemplateFilename", self.defaultXhtmlTemplateFilename)
    xhtmlTemplateFilename= xhtmlTemplateFilename.lower()
    templateName = self.iceContext.fs.split(xhtmlTemplateFilename)[1]
    cd = bool(re.search("(^|[^a-zA-Z])cd[^a-zA-Z]", templateName))
    ##
    #print
    #print "plugin_export_cd.py displayIf()"
    #print "  templateName='%s', cd %s" % (templateName, cd)
    #print
    ##
    return cd


# Export
def exportCD(self, exportBaseName=None, exportCallback=None, toZipFile=None):
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

    ex = IceCDExport(self, self.packagePath, templateName)
    body = ex.export(fromPath=path, to=fullFileName, toRepository=toRepository, \
                        exportCallback=exportCallback, templateName=templateName, get=self.get)
    if body is None:
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
    else:
        self["title"] = "Generating selected readings from DiReCt"
        self["body"] = body
exportCD.options = {"toolBarGroup":"publish", "position":48, "postRequired":True,
                "label":"CD-Export", "title":"CD Export this package",
                "displayIf":displayIf, "enableIf":True, #isPackage,
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



class IceCDExport:
    myPath    = ""
    exportTemplate = 'generate-selected-reading-template.tmpl'
    HtmlTemplate = None             # injected data
    """ iceCDExport class. """
    def __init__(self, iceSite, packagePath=None, templateName=None):
        # iceSite usage:
        #    iceSite.rep
        #    iceSite.clone()
        #    iceSite.preRenderCallback
        #    iceSite.serve(item)
        #    and maybe its dictionary e.g. iceSite["toolbar"] = "<span/>"
        self.iceContext = iceSite.iceContext
        self.fs = self.iceContext.fs
        self.io = IceIO(iceSite.iceContext)
        self.rep = iceSite.iceContext.rep
        self.iceSite = iceSite.clone()
        self.iceSite.exportVersion = True
        self.includeSource = iceSite.includeSource
        self.__makeObjectUrlLocal = False
        
        self.__xml = self.iceContext.xmlUtils.xml
        
        self.packagePath = packagePath
        self.templateName = templateName
        
        #Package Export for courseWare
        self.courseCode = iceSite.get("coursecode", "")
        self.courseNumber = iceSite.get("coursenumber", "")
        self.courseName = "%s%s" % (self.courseCode, self.courseNumber)
        self.year = iceSite.get("year", "")
        self.semester = iceSite.get("semester", "")
        
        if self.semester[:1].lower() == "s":
            self.semesterNumber = self.semester[1:]
        else:
            self.semesterNumber = self.semester
            self.semester = "S%s" % self.semester
        
        self.selectedReadingClass = None
        self.isStudyDesk = False
        self.d = {}
        self.requestType = ""
        
        self.directHelper = None
        username = self.iceContext.session.username
        
        if packagePath is not None:
            #Try to get request CDT
            self.requestType = "CDT"
            self.directHelper = DirectHelper(self.iceContext, self.packagePath, self.requestType, courseFullName=self.courseName, \
                                             courseYear=self.year, semesterNumber=self.semesterNumber)
            
            msg, srmsObject = self.directHelper.prod_refList()
            if srmsObject is None or srmsObject.hasProdRef == False:
                #Check if it has DVD
                self.requestType = "DVDT"
                self.directHelper = DirectHelper(self.iceContext, self.packagePath, self.requestType, courseFullName=self.courseName, \
                                             courseYear=self.year, semesterNumber=self.semesterNumber)

    def __assignIntoTemplate(self):
        file = self.iceContext.fs.join (self.myPath, self.exportTemplate)
        htmlTemplate = self.HtmlTemplate(templateFile=file)
        
        html = htmlTemplate.transform(self.d, allowMissing=True)
        
        return html
    
    def __getMakeObjectUrlLocal(self):
        return self.__makeObjectUrlLocal
    def __setMakeObjectUrlLocal(self, value):
        self.__makeObjectUrlLocal = value
    makeObjectUrlLocal = property(__getMakeObjectUrlLocal, __setMakeObjectUrlLocal)

    def __setTemplateFile(self, templateFile):
        selectedReadingTemplate = templateFile
        if not self.fs.isFile(selectedReadingTemplate):
            return None
        return selectedReadingTemplate
    def __getSelectedReadingItem(self, selectedReadingFile):
        if self.fs.isFile(self.rep.getAbsPath(selectedReadingFile)):
            return self.rep.getItem(selectedReadingFile)
        return None
    
    def export(self, fromPath, to, toRepository=False, exportCallback=None, deleteFirst=True, templateName=None, get=None):
        #print "*EXPORT export(fromPath='%s', to='%s', toRepository=%s, exportCallback='%s', deleteFirst=%s" \
        #        % (fromPath, to, toRepository, exportCallback, deleteFirst)
        self.iceSite.preRenderCallback = self.__preRenderMethod
        try:
###################################
            #Selected reading...
            error = ""
            originalFileExist = False
            exportTempDir = self.iceContext.fs.createTempDirectory()
            selectedReadingFile = self.iceContext.fs.join(fromPath, "selected_readings/list_of_readings.odt")
            listOfReadingAbsFile = self.rep.getAbsPath(selectedReadingFile)
            selectedReadingTemplate = self.__setTemplateFile(self.fs.absPath("plugins/usq/list_of_readings.odt"))
            readingItem = self.__getSelectedReadingItem(selectedReadingFile)
            
            originalReadingFileTemp = None
            msg, srmsObject = self.directHelper.prod_refList()
            
            if srmsObject is not None and srmsObject.hasProdRef:
                #check if user have access
                success = False
                for key in srmsObject.prodRefList:
                    xmlString = self.directHelper.prodXmlData(key)
                    exportUrls = None
                    xml = None
                    if xmlString is not None:
                        xml = self.__xml(xmlString)
                        exportUrls = xml.getNodes("//export_url")
                    if exportUrls is not None:
                        for exportUrl in exportUrls:
                            success = self.directHelper.testDownload(exportUrl.getContent().strip())
                            if success:
                                break
                    if xml:
                        xml.close()
                if success:                
                    # createTemporary directory to store the old list_of_readings.odt file and the pdfs
                    if self.fs.isFile(listOfReadingAbsFile):
                        originalFileExist = True
                        originalReadingFileTemp = self.fs.createTempDirectory()
                        tempOldSelectedReadingFilePath = "%s/list_of_readings.odt" % originalReadingFileTemp.absolutePath()
                        self.fs.copy(listOfReadingAbsFile, tempOldSelectedReadingFilePath)
                    
                    self.fs.copy(selectedReadingTemplate, listOfReadingAbsFile)
                    
                    error, stopProcessRequest = self.saveDirectToReadingFile(srmsObject, selectedReadingFile, exportTempDir)
                    
                    if error == "No Reading" and not stopProcessRequest:
                        if originalReadingFileTemp is not None:
                            self.fs.copy("%s/list_of_readings.odt" % originalReadingFileTemp.absolutePath(), listOfReadingAbsFile)
                            originalReadingFileTemp.delete()
                        else:
                            self.iceContext.fs.delete(listOfReadingAbsFile)
                            
                    #stopProcessRequest=False
                    if stopProcessRequest:
                        msg = "Fail"
                
                        if originalReadingFileTemp is not None:
                            self.fs.copy("%s/list_of_readings.odt" % originalReadingFileTemp.absolutePath(), listOfReadingAbsFile)
                            originalReadingFileTemp.delete()
                        exportTempDir.delete()
                        self.d["error"] = error
                        self.d["message"] = self.directHelper.message(msg)
                        self.d["showButton"] = False
                        self.d["completed"] = True
                        return self.__assignIntoTemplate()
            
            #To re render on selected reading
            selectedReadingFile = self.iceContext.fs.join(fromPath, "selected_readings/list_of_readings.odt")
            item = self.rep.getItem(selectedReadingFile)
            #render reading item
            item.render(force=True, fixPdfLink=True)
                            
###################################



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
                        #self.makeObjectUrlLocal = obj.makeObjectUrlLocal
                        pass
                except Exception, e:
                    print "##########################"
                    print "ERROR in exportCallback - " + str(e)
                    print "##########################"

            contentPath = toPath
            if True:        # is CD is True
                cdItem = self.iceContext.FileSystem("./plugins/usq/cd")
                for path, dirs, files in cdItem.walk():
                    if ".svn" in dirs:
                        dirs.remove(".svn")
                    contentFiles = ["autohtml.exe", "usq.ico", "showhtml.ini"]
                    for file in files:
                        tPath = path
                        if file.lower() in contentFiles:
                            tPath = "content"
                        #print "path='%s', file='%s' -> '%s'" % (path, file, self.io.join(toPath, tPath, file))
                        cdItem.copy(path+file, self.io.join(toPath, tPath, file))
                #cdItem = self.rep.getItem("./plugins/usq/")
                #for itemlist in cdItem.walk(filesOnly=True):
                #    for item in itemlist:
                #        toFilename = self.io.join(toPath, item.relPath[len(cdItem.relPath):])
                #        #result = self.__serve(item, toFilename)
                #        if item.isBinaryContent:
                #            data, mimeType = item.getBinaryContent()
                #            if data is None:
                #                data = "404 '%s' not found!" % item.uri
                #            if mimeType is None:
                #                print " Unknown (or not supported) mimeType for '%s' (relPath='%s')" % (item.ext, item.relPath)
                #        else:
                #            data, mimeType = self.iceSite.serve(item, ServerRequestData(item.uri))[:2]
                #        self.io.write(toFilename, data)
                
                contentPath = self.io.join(toPath, "content")
            #------------------------------
            #------------------------------
            #          Export
            self.__export(fromPath, contentPath, exportTempDir, templateName=templateName)
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
        
        ##check_links(self)
        check_links = self.iceContext.getPlugin("ice.function.check_links")
        checkLinkStr = ""
        if check_links is not None and check_links.pluginInitialized:
            checkLinkStr = check_links.pluginFunc(self, "courseware")
        else:
            print "Warning: check_links not found or initialized!"
        
        if error or checkLinkStr:
            self.d["error"] = error
            self.d["showButton"] = False
            self.d["completed"] = True
            self.d["checkLinkStr"] = checkLinkStr
            return self.__assignIntoTemplate()
        return None


    def __export(self, fromPath, toPath, tempPdfDir=None, templateName=None):
        # Note: Assumes that the manifest has been updated first (if using the manifest)
        manifestXmlStr = None
        #manifestJson = None
        self.iceSite.updateManifest()
        self.mediaLinkFixup = MediaLinkFixup(self.iceContext, fromPath,
                                                self.iceSite.session.username)
        imsManifest = self.iceSite.getImsManifest()
        if imsManifest is not None:
            manifestXmlStr = str(imsManifest)
            #
            manifest = self.iceSite.manifest
            #manifestJson = manifest.asJSON(self.iceContext.jsonWrite)
        dom = None

        if tempPdfDir is not None:
            self.iceContext.fs.copy(tempPdfDir.absolutePath(), toPath)
        
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
            #self.io.write(self.io.join(toPath, "manifest.json"), manifestJson)
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

        # export all referenced content
        for relPath in hrefs:
            self.__exportAFile(relPath, fromPath, toPath, fixupLinks, rFixupLinks)

        def _write(rfile, data):
            self.io.write(self.io.join(toPath, rfile), data)
        self.mediaLinkFixup.addWriteChanges(self.rep, _write, manifestXmlStr)
        if dom is not None:
            dom.close()

        if mets is not None:
            #print "fromPath='%s'" % fromPath
            items = imsManifest.organizations.defaultOrganization.items
            self.__createMETS(mets, items, toPath)
            xml = mets.getXml()
            self.io.write(self.io.join(toPath, "mets.xml"), xml)


    def __exportAFile(self, relPath, fromPath, toPath, fixupLinks, rFixupLinks):
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
                xml = self.iceContext.Xml(data)     #, parseAsHtml=True)
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
                return True
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
        def _serveWrite(data):
            toFilename = self.io.join(toPath, rPath)
            self.io.write(toFilename, data)
            if rPath=="default.htm":
                indexFilename = self.io.join(toPath, "index.html")
                self.io.write(indexFilename, data)
        def _htmlDataFixup(htmlData):
            docType = self.__getDocType(htmlData)
            if callable(linksFixup):
                try:
                    htmlData = linksFixup(htmlData)
                except Exception, e:
                    print "Invalid htm file: ", str(e)
            htmlData = self.mediaLinkFixup.fixupMediaLinks(htmlData, rPath)
            htmlData = self.__restoreDocType(htmlData, docType)
            return htmlData
        result = self.__serve(item, _serveWrite, _htmlDataFixup)
        if result==False:
            return False
        return True


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


    def __serve(self, item, write, htmlDataFixup):
        if item.isBinaryContent:
            data, mimeType = item.getBinaryContent()
            if data is None:
                data = "404 '%s' not found!" % item.uri
            if mimeType is None:
                print " Unknown (or not supported) mimeType for '%s' (relPath='%s')" % (item.ext, item.relPath)
        else:
            data, mimeType = self.iceSite.serve(item, ServerRequestData(item.uri))[:2]
        if mimeType=="text/html":
            data = htmlDataFixup(data)
        write(data)
        return True


    def __preRenderMethod(self, iceSite):
        # HACK: Add <span/> to work around a firefox bug for empty elements
        iceSite["toolbar"] = "<span/>"        # remove the toolbar
        iceSite["statusbar"] = ""      # remove the statusbar
        iceSite["app-css"] = ""        # remove the application css

    def __getDocType(self, data):
        docType = None
        m = re.search(r"^(\s*\<\!.*?\>\s*)", data,re.DOTALL)
        if m:
            docType = m.groups()[0]
        return docType

    def __restoreDocType(self, data, docType):
        if docType is not None and docType!="" and not data.startswith(docType):
            data = docType + data
        return data

    def saveDirectToReadingFile(self, srmsObject, selectedReadingFile, exportTempDir=None):
        import tempfile
        tempDirectory = tempfile.gettempdir()
        pdfTempDir = "%s/%s" % (tempDirectory.rstrip("/"), "cache")

        if self.iceContext.fs.isDirectory(pdfTempDir) or self.iceContext.fs.exists(pdfTempDir):
            self.iceContext.fs.delete(pdfTempDir)
        
        self.iceContext.fs.makeDirectory(pdfTempDir)
    
        copyRightErrorDict = {}
        copyRightErrorList = []
        statusErrorDict = {}
        statusErrorList = []
        duplicateReading = []
        isNotTickedInSrmsDict = {}
        isNotTickedInSrmsList = []
        isDownloaded = {}
        isLowResDict = {}
        isEncrypted = {}
        addingCopyrightPageError = {}

        srmsObject = self.directHelper.processAllReadingForSrms(srmsObject, printVersion=False)
        if srmsObject.requestObjectList == []:
            return "No Reading", False
        for requestObject in srmsObject.requestObjectList:
            #open up selected reading odt file and save to it
            
            selectedReadingFileAbsPath = self.iceContext.rep.getAbsPath(selectedReadingFile)
            selectedReadingTempDir = self.iceContext.fs.unzipToTempDirectory(selectedReadingFileAbsPath)
            content = self.iceContext.fs.readFile(selectedReadingTempDir.absolutePath("content.xml"))
            contentXml = self.__xml(content, self.directHelper.oons)
            contentXml = self.directHelper.createStyle(contentXml)
            
            listOfReadingNode = contentXml.getNode("//text:p[string()='List of readings']")
            lastNode = listOfReadingNode

            disNode = contentXml.createElement("text:p")
            disSpan = contentXml.createElement("text:span")
            disSpan.setContent("Please be aware that the referencing style used in the following citations may differ from that specified for your assessment. For further information, please refer to the referencing guides on the ")
            disNode.addChild(disSpan)
                
            disSpan = contentXml.createElement("text:a")
            disSpan.setAttribute("xlink:href","http://libcat.usq.edu.au")
            disSpan.setContent("USQ Library website")
            disNode.addChild(disSpan)
                
            disSpan = contentXml.createElement("text:span")
            disSpan.setContent(" or to guides as specified by your examiner. ")
            disNode.addChild(disSpan)
                              
            lastNode.addNextSibling(disNode)
            lastNode = disNode

            
            usedModuleNumber = []
            
            readingListDict = requestObject.readingListDict
            moduleTitleList = requestObject.moduleTitleList
            for readingNumber in requestObject.sortedReadingNumber:
                addingCopyrightPageErrorList = []
                isEncryptedList = []
                isDownloadedList = []
                isLowResList = []
                readingObject = readingListDict[readingNumber]
                
                #generating Module Title
                moduleNumber = readingObject.moduleNumber
                if moduleNumber != 0 and moduleNumber not in usedModuleNumber:
                    moduleTitleString= moduleTitleList[moduleNumber]
                    if moduleTitleString.find("not exist in study_modules")==-1:
                        moduleTitleNode = self.directHelper.createModuleHeader(moduleTitleString, contentXml)
                        lastNode.addNextSibling(moduleTitleNode)
                        lastNode = moduleTitleNode
                    usedModuleNumber.append(readingObject.moduleNumber)
                    
                #generating readingNumberNode
                readingNumberNode = None
                if self.isStudyDesk:
                    readingNumberNode = readingObject.generateReadingNumberNode(contentXml, withPermalink=True) #online with permalink
                else:
                    if readingObject.url and readingObject.fileList ==[]:
                        readingNumberNode = readingObject.generateReadingNumberNode(contentXml, withPermalink=True)
                    else:
                        readingNumberNode = readingObject.generateReadingNumberNode(contentXml, withPermalink=False)
                if readingNumberNode is not None:
                    lastNode.addNextSibling(readingNumberNode)
                    lastNode = readingNumberNode
                #citation
                citationNode = readingObject.citation.getCitationNode(contentXml, self.iceContext)
                if citationNode is not None:
                    lastNode.addNextSibling(citationNode)
                    lastNode = citationNode
                    
                if readingObject.url and readingObject.citation.citationType=="print":
                    urlNode = readingObject.getUrlNode(contentXml)
                    if urlNode is not None:
                        lastNode.addNextSibling(urlNode)
                        lastNode = urlNode
                    
                #copyright notice
                copyrightNoticeNode = readingObject.copyright.getCopyrightNoticeNode(contentXml)
                if copyrightNoticeNode is not None:
                    lastNode.addNextSibling(copyrightNoticeNode)
                    lastNode = copyrightNoticeNode
                #alternative
                if readingObject.alternative:
                    altNode = readingObject.alternative.getAltNode(contentXml)
                    if altNode is not None:
                        lastNode.addNextSibling(altNode)
                        lastNode = altNode
                
                #Adding copyright page
                for file in readingObject.fileList:
                    if file.isHighRes:
                        #Add copyright page
                        fileName = "%s/%s" % (pdfTempDir, file.fileName)
                        file.downloadedFilePath = fileName
                        
                        if not self.iceContext.fs.exists(fileName):
                            file.downloadFile()
                        if file.isDownloadSuccess:
                            copyrightPdf = self.fs.absPath("plugins/usq/copyrightbox.pdf")
                            success = self.directHelper.addCopyrightPage(file.fileName, file.downloadedFilePath, copyrightPdf)
                            if not success:
                                addingCopyrightPageErrorList.append(file.fileName)
                        elif file.isEncrypted:
                            isEncryptedList.append(file.fileName)
                        else:
                            isDownloadedList.append(file.fileName)
                    else:
                        isLowResList.append(file.fileName)
                            
                #Report low res pdf files
                if isLowResList:
                    isLowResDict[readingNumber] = isLowResList
                if isEncryptedList != []:
                    isEncrypted[readingObject.readingNumber] = isEncryptedList
                if isDownloadedList != []:
                    isDownloaded[readingObject.readingNumber] = isDownloadedList
                if addingCopyrightPageErrorList != []:
                    addingCopyrightPageError[readingObject.readingNumber] = addingCopyrightPageErrorList
                
                #error processing
                duplicateReading = requestObject.duplicateReading
                if readingObject.status != "live":
                    statusErrorList.append(readingNumber)
                    statusErrorDict[readingNumber] = readingObject.status
                if readingObject.copyright.errorStr != "":
                    copyRightErrorList.append(readingNumber)
                    copyRightErrorDict[readingNumber] = readingObject.copyright.errorStr
                if readingObject.alternative:
                    if readingObject.alternative.typeIsNone:
                        isNotTickedInSrmsList.append(readingNumber)
                        isNotTickedInSrmsDict[readingNumber] = "None of the product reference is ticked"
                
            contentXml.saveFile(selectedReadingTempDir.absolutePath("content.xml"))
            self.iceContext.fs.copy(self.fs.absPath("fake.skin/pdf.gif"), selectedReadingTempDir.absolutePath("Pictures/pdf.gif"))
                
            self.iceContext.fs.zip(selectedReadingFileAbsPath, selectedReadingTempDir.absolutePath())
            selectedReadingTempDir.delete()
            
            #processing the error msg:
            error = ""
            warningList = []
            
            copyRightErrorList = self.directHelper.sort(copyRightErrorList)
            statusErrorList = self.directHelper.sort(statusErrorList)
            isNotTickedInSrmsList = self.directHelper.sort(isNotTickedInSrmsList)
            
            self.iceContext.fs.copy(self.iceContext.fs.absPath(pdfTempDir), exportTempDir.absolutePath("media/readings/"))
            
            if requestObject.warning != '':
                warningList.append(requestObject.warning)
            if duplicateReading:
                error += self.directHelper.generateListError(duplicateReading, "Duplicate Reading")
            if copyRightErrorDict:
                error += self.directHelper.generateCopyRightErrorStatus(copyRightErrorDict, "Copyright code Error", copyRightErrorList)
            if statusErrorDict:
                error += self.directHelper.generateCopyRightErrorStatus(statusErrorDict, "DiReCt Item Status Error", statusErrorList)
            if warningList:
                error += self.directHelper.generateListError(warningList, ("Warning for: %s") % requestObject.prodRef, warning=True)
            if isNotTickedInSrmsDict:
                error += self.directHelper.generateCopyRightErrorStatus(isNotTickedInSrmsDict, "Not ticked", isNotTickedInSrmsList)
            if isEncrypted != {}:
                error += self.directHelper.generateFileError(isEncrypted, "Encrypted Pdf(s)")
            if isDownloaded != {}:
                error += self.directHelper.generateFileError(isDownloaded, "Download Pdf(s) Error")
            if isLowResDict != {}:
                error += self.directHelper.generateFileError(isLowResDict, "Low resolution Pdf(s)")
            if addingCopyrightPageError != {}:
                error += self.directHelper.generateFileError(addingCopyrightPageError, "Adding copyright page Error")

            return error, False
        return None, None


class MediaLinkFixup(object):
    def __init__(self, iceContext, fromBasePath, username):
        self.mediaTitle = ""
        self.iceContext = iceContext
        self.username = username
        self.mediaServer = self.iceContext.config.settings.get("mediaServerTestPattern")
        self.newBaseUrl = self.iceContext.config.settings.get("mediaServerExportPath")
        self.mediaSso = self.iceContext.config.settings.get("mediaServerSsoParam")
        self.publicKey = self.iceContext.config.settings.get("mediaServerPublicKey")
        self.privateKey = self.iceContext.config.settings.get("mediaServerPrivateKey")
        self.flashPlayer = self.iceContext.config.settings.get("mediaServerFlashPlayer")
        self.supportFiles = self.iceContext.config.settings.get("mediaServerSupportFiles")
        self.supportFiles.append(self.flashPlayer)
        self.newBaseUrl = self.newBaseUrl.lstrip("/")
        if not self.mediaServer.endswith("/"):
            self.mediaServer += "/"
        #
        self.changedUrls = {}                       # mediaUrl:newRelUrl
        self.mediaFileName = {}
        self.contentSizes = {}
        self.standalonePlayers = {}                 # name:htmlContent  (name=newRelUrl)
        urlRoot = self.iceContext.urlRoot
        if fromBasePath.startswith(urlRoot):
            fromBasePath = fromBasePath[len(urlRoot)-1:]
        self.fromBasePath = fromBasePath


    def fixupMediaLinks(self, htmlStr, relPath):
        def getQueryParams(href):
            if href.find("?")>0:
                params = [i.split("=", 1) for i in href.split("?", 1)[1].split("&")]
                params = [(i[0],i[-1]) for i in params]
                queryParams = dict(params)
            else:
                queryParams = {}
            return queryParams
        def makeUrlRelative(url):
            return rPath + url
        def makeMediaRelaive(url):
            return makeUrlRelative(os.path.join(self.newBaseUrl,
                                            url[len(self.mediaServer):]))
        def getSupportScripts():
            scripts = ""
            jsFiles = [makeMediaRelaive(url) for url in self.supportFiles if url.endswith(".js")]
            for jsFile in jsFiles:
                scripts += "<script type='text/javascript' src='%s'> </script>\n" % jsFile
            return scripts
        def getSizeInfo(url, jsonOutputs):
            name = url.rsplit("/", 1)[-1]
            size = None
            try:
                size = string.atoi(jsonOutputs.get(name, {}).get("size"))
            except:
                size = None
            self.contentSizes[url] = size
            return size
        def getSizeData(mUrl):
            baseUrl = mUrl.rsplit("/", 1)[0]
            baseUrl = "%s/" % baseUrl.replace("detail", "metadata").rstrip("/")
            try:
                #json = self.__getJson(baseUrl + "/ffmpeg.info")
                json = self.__getJson(baseUrl)
            except Exception, e:
                print "?Failed to get json???? ", str(e)
                return
            jsonOutputs = json.get("outputs", {})
            self.mediaTitle = json.get("title", "")
            getSizeInfo(mUrl, jsonOutputs)
            getSizeInfo(baseUrl + "/ffmpegSplash.jpg", jsonOutputs)

        rPath = relPath.count("/") * "../"      # used by makeUrlRelative()
        try:
            fixups = 0
            flashPlayer = makeMediaRelaive(self.flashPlayer)
            mediaPlayerWrapper = MediaPlayerWrapper(flashPlayer)
            xml = self.iceContext.Xml(htmlStr)
            try:
                aNodes = xml.getNodes("//*[local-name()='a'][@href]")
                for aNode in aNodes:
                    href = aNode.getAttribute("href")
                    isMediaLink = href.startswith(self.mediaServer)
                    if isMediaLink:
                        text = ""
                        if self.mediaTitle:
                            #remove special character
                            text = self.mediaTitle.replace(" ", "_")
                        else:
                            text = aNode.getContent()
                            if text:
                                text = text.replace(" ", "_")
                                #make sure there is no special character
                        text = re.sub("[^a-zA-Z0-9_]", "", text)
                        fixups += 1
                        queryParams=getQueryParams(href)
                        mUrl = href.split("?")[0]
                        
                        filename = href.split("/")[-1]
                        newBaseUrl = self.newBaseUrl
                        counter = mediaPlayerWrapper.IdCounter
                        #check if it's a audio or video
                        if filename.endswith(".mp3"):
                            newBaseUrl = self.newBaseUrl.replace("/video", "/audio")
                        exPath = os.path.join(newBaseUrl, mUrl[len(self.mediaServer):])
                        
                        fPath, fName, fExt = self.iceContext.fs.splitPathFileExt(exPath)
                        newPath = "%s/%s_%s%s" % (fPath, text, counter, fExt)
                        
                        if not queryParams.has_key("embedmedia") and not mUrl.endswith("index.htm"):
                            #do checking here
                            if self.mediaFileName.has_key(exPath):
                                newPath, playerName = self.mediaFileName.get(exPath)
                            else:
                                playerName = "%s_%s.htm" % (text, counter)
                                self.mediaFileName[exPath] = (newPath, playerName)
                        else:
                            newPath = None
                        self.changedUrls[mUrl] = (exPath, newPath)
                        rUrl = makeUrlRelative(exPath)
                        if newPath:
                            newPath = makeUrlRelative(newPath)
                        
                        print "newPath: '%s', mUrl: '%s'" % (newPath, mUrl)
                        aNode.setAttribute("href", rUrl)
                        pHtml, setupScript = mediaPlayerWrapper.createPlayer(rUrl, queryParams, newPath=newPath, title=self.mediaTitle)
                        pHtml = "<span>\n%s\n</span>" % pHtml
                        if queryParams.has_key("embedmedia"):
                            aNode.replace(xml.xmlStringToElement(pHtml))
                            thumbnail = mUrl.rsplit("/", 1)[0] + "/ffmpegSplash.jpg"
                            exPath = os.path.join(self.newBaseUrl, thumbnail[len(self.mediaServer):])
                            self.changedUrls[thumbnail] = (exPath, None)
                            getSizeData(mUrl)
#                            def getSize(name):
#                                size = None
#                                try:
#                                    size = string.atoi(jsonOutputs.get(name, {}).get("size"))
#                                except:
#                                    size = None
#                                return size
#                            name = mUrl.rsplit("/", 1)[-1]
#                            size = getSize(name)
#                            self.contentSizes[mUrl] = size
#                            size = getSize("ffmpegSplash.jpg")
#                            self.contentSizes[thumbnail] = size
                        elif mUrl.endswith("index.htm"):        # presenter?
                            aNode.setAttribute("href", rUrl)
                            aNode.setAttribute("target", "_blank")
                            aNode.removeAttribute("onclick")
                            #print "---------- PRESENTER -------------"
                            #print "mUrl='%s', rUrl='%s'" % (mUrl, rUrl)
                            try:
                                mUrl = mUrl[:-len("index.htm")]
                                exPath = exPath[:-len("index.htm")]
                                #print "  mUrl='%s', exPath='%s'" % (mUrl, exPath)
                                # get imsmanifest.xml
                                files = self.__getImsManifestFiles(mUrl+"imsmanifest.xml")
                                #print "  files='%s'" % files
                                for file in files:
                                    self.changedUrls[mUrl+file] = (exPath+file, None)
                                    #print "'%s'" % (mUrl+file)
                                    #print "  '%s'" % (exPath+file)
                            except Exception, e:
                                print "ERROR: '%s'" % str(e)
                            #print "----------------------------------"
                        else:
                            basePath = ""
                            if relPath.find("/")!=-1:
                                basePath = relPath.rsplit("/", 1)[0] + "/"
                            scripts = getSupportScripts()
                            scripts += "<script type='text/javascript'>\n%s\n</script>\n" % setupScript
                            #playerName = "_mplayer%s.htm" % mediaPlayerWrapper.IdCounter
                            playerName = "%s_%s.htm" % (text, counter)
                            #print playerName
                            aNode.setAttribute("href", playerName)
                            aNode.setAttribute("target", "_blank")
                            aNode.removeAttribute("onclick")
                            playerHtml = "<!DOCTYPE html><html><head><title>MediaPlayer</title></head><body>%s %s</body></html>"
                            playerHtml = playerHtml % (pHtml, scripts)
                            self.standalonePlayers[os.path.join(basePath, playerName)] = playerHtml
                            #
                            thumbnail = mUrl.rsplit("/", 1)[0] + "/ffmpegSplash.jpg"
                            exPath = os.path.join(self.newBaseUrl, thumbnail[len(self.mediaServer):])
                            self.changedUrls[thumbnail] = (exPath, None)
                            getSizeData(mUrl)
            except Exception, e:
                print "Failed processing XML! - '%s'" % str(e)
            if fixups:
                scripts = getSupportScripts()
                scripts += mediaPlayerWrapper.getSetupScripts()
                scripts = xml.xmlStringToNodeList(scripts)
                body = xml.getNode("//*[local-name()='body']")
                if body:
                    body.addChildren(scripts)
                htmlStr = str(xml.getRootNode())
            xml.close()
        except Exception, e:
            print "Failed to read as XML. - '%s'" % str(e)
        return htmlStr


    def addWriteChanges(self, rep, write, manifestXmlStr):
        reports = []
        if self.changedUrls=={}:
            return
        for key, value in self.standalonePlayers.iteritems():
            #print " write %s=%s" % (key, len(value))
            write(key, value)
        http = self.iceContext.Http()
        for sf in self.supportFiles:
            self.changedUrls[sf] = (os.path.join(self.newBaseUrl, sf[len(self.mediaServer):]), None)
        total = len(self.changedUrls)
        count = 0
        for key, value in self.changedUrls.iteritems():
            count += 1
            if value[1] is not None:
                value = value[1]
            else:
                value = value[0]
            if key.startswith("/"):
                item = rep.getItemForUri(key)
                if item.isBinaryContent:
                    data, mimeType = item.getBinaryContent()
                    write(value, data)
                else:
                    print " **************** ERROR '%s' is not binaryContent!" % key
            else:
                # Add possible media security token before getting
                resolvedUrl = self.__resolveMediaSecurity(self.username, key)
                print "Retrieving %s of %s files from the media server" % (count, total)
                #print "Retrieving remote data : '%s'" % (resolvedUrl)
                data = http.get(resolvedUrl)
                #print "Storing locally for export : '%s'" % (value)
                # Time to store
                if data:
                    size=self.contentSizes.get(key, None)
                    #print "  len(data)=%s, size=%s  %s" % (len(data), size, key)
                    if size is not None:
                        if size!=len(data):
                            msg = "***ERROR: incorrect data size %s expected %s for %s" % (len(data), size, key)
                            print msg
                            # OK try again
                            resolvedUrl = self.__resolveMediaSecurity(self.username, key)
                            data = http.get(resolvedUrl)
                            if data and len(data)==size:
                                print " Retry - size checked OK"
                            else:
                                reports.append(msg)
                        else:
                            print " Size checked OK"
                    #else:
                    #    if len(data)<2048:
                    #        print "---- size %s  %s" % (len(data), key)
                            #print data
                    write(value, data)
                else:
                    print "*************** ERROR failed to get data for '%s'" % key
        if reports!=[]:
            print "---- Report ----"
            for report in reports:
                print report
        if manifestXmlStr!=None:
            try:
                xml = self.iceContext.Xml(manifestXmlStr, [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
                ress = xml.getNode("//x:resources")
                for value, value2 in self.changedUrls.itervalues():
                    if value2:
                        value = value2
                    r = xml.createElement("resource", href=value)
                    r.setAttribute("type", "webcontent")
                    r.setAttribute("identifier", md5(value).hexdigest())
                    r.addChild(xml.createElement("file", href=value))
                    ress.addChild(r)
                    ress.addChild(xml.createText("\n"))
                manifestXmlStr = str(xml.getRootNode())
                xml.close()
            except Exception, e:
                print "**** ERROR: %s" % str(e)
            for value, value2 in self.changedUrls.itervalues():
                if value2:
                    value = value2
                d = {"visible":False, "relPath":value, "children":[], "title":"[Untitled '%s']" % value}
            write("imsmanifest.xml", manifestXmlStr)

    def __getImsManifestFiles(self, imsmanifestFilename):
        # xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
        files = ["imsmanifest.xml"]
        http = self.iceContext.Http()
        resolvedUrl = self.__resolveMediaSecurity(self.username, imsmanifestFilename)
        print "  Retrieving remote data : '%s'" % (resolvedUrl)
        xmlStr = http.get(resolvedUrl)
        xml = None
        try:
            xml = self.iceContext.Xml(xmlStr)
            fileNodes = xml.getNodes("//*[local-name()='resources']/*[local-name()='resource']/*[local-name()='file']")
            for fileNode in fileNodes:
                href = fileNode.getAttribute("href")
                files.append(href)
            xml.close()
        except Exception, e:
            print "Error processing the imsmanifest.xml data! '%s'" % str(e)
            try:
                xml.close()
            except:
                pass
        return files

    def __getJson(self, jsonUrl):
        json = {}
        http = self.iceContext.Http()
        try:
            resolvedUrl = self.__resolveMediaSecurity(self.username, jsonUrl)
            print "  Retrieving remote data : '%s'" % (resolvedUrl)
            jsonStr = """%s""" % http.get(resolvedUrl)
            json = self.iceContext.jsonRead(jsonStr)
        except Exception, e:
            print "Error getting json - '%s'" % str(e)
        return json

    ########################
    # __resolveMediaSecurity()
    #
    # Test links to see if they are for the media server
    #  and add appropriate security tokens for access.
    def __resolveMediaSecurity(self, username, url):
        # Check whether we even need to talk to the media server
        if url.find(self.mediaServer) != -1:
            # Strip out SSO parameters for the HTML export
            if url.find("?" + self.mediaSso) != -1:
                url = url.replace("?" + self.mediaSso, "")
            # Find the logged in user (or the windows user)
            if username is None:
                print "Warning, no username in session, trying guest access to media server!"
            else:
                # Get the key pair required to build the token
                if self.publicKey is None or self.privateKey is None:
                    print "ERROR! One or both keys for security token are missing!"
                else:
                    # Build the token hash
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    tokenSeed = username + ":" + timestamp + ":" + self.privateKey
                    tokenHash = md5(tokenSeed).hexdigest()
                    # Now add the token parts to the URL
                    token = username + "%3A" + timestamp + "%3A" + self.publicKey + "%3A" + tokenHash
                    url = url + "?token=" + token + "&accept=true"
        return url


class MediaPlayerWrapper(object):
    IdCounter = 0
    def __init__(self, flashPlayerUrl):
        self.flashPlayerUrl = flashPlayerUrl
        self.setups = {}

    def createPlayer(self, href, queryParams, newPath=None, title=""):
        if title == "":
            title = "Download link: "
        filename = href.split("/")[-1]
        width, height = self.__getWidthHeight(filename, queryParams)
        if newPath:
            filename = newPath.split("/")[-1]
            href = newPath
        isAudio, isVideo, isHtml = self.__getIsAudioIsVideoIsHtml(filename)
        thumbnail = ""
        MediaPlayerWrapper.IdCounter += 1
        playerId = "player%s" % self.IdCounter
        pHtml = ""
        setupOptions = {}
        style = "width:%spx; height:%spx;" % (width, height)
        downloadFileName = href
        if isAudio:
            pHtml = "<b>Audio: </b><span id='%s' style='%s'> </span>" % (playerId, style)
            audioDownload = "<p>%s &#160; <a class='audio' href='%s'><img src='skin/download.png' style='text-decoration: none; border: 0 none'/></a></p>"
            audioDownload = audioDownload % (title, href)
            pHtml += audioDownload
            setupOptions = self.__getAudioJwPlayerOptions(href, height, width)
        elif isVideo:
            pHtml = "<span id='%s' style='%s'></span>" % (playerId, style)
            videoDownload = "<p>%s&#160; <a class='video' href='%s'><img src='skin/download.png' style='text-decoration: none; border: 0 none'/></a></p>"
            videoDownload = videoDownload % (title, href)
            pHtml += videoDownload
            thumbnail = href[:-len(filename)] + "ffmpegSplash.jpg"
            setupOptions = self.__getVideoJwPlayerOptions(href, height, width, thumbnail)
        self.setups[self.IdCounter] = setupOptions
        return pHtml, self.__getSetupScript(self.IdCounter, setupOptions)

    def getSetupScripts(self):
        if self.setups=={}:
            return ""
        parts = []       # dummy object (with dummy setup()) for if jwplayer() return null
        ids = self.setups.keys()
        ids.sort()
        for id in ids:
            parts.append(self.__getSetupScript(id, self.setups[id]))
        return "<script type='text/javascript'>\n" + "\n".join(parts) + "\n</script>\n"

    def __getSetupScript(self, id, setupOptions):
        s = """try{
        var o=%s;
        while(/\/\.\.\//.test(o.file)){o.file=o.file.replace(/\/[^\/]+\/\.\.\//, "/");}
        jwplayer('player%s').setup(o);}catch(e){}"""
        s = s % (setupOptions, id)
        return s

    def __getVideoJwPlayerOptions(self, filepath, height, width, thumbnail):
        options = """{flashplayer: "%s",
            "controlbar.idlehide": true,
            "viral.onpause": false, "viral.oncomplete": false, "viral.allowmenu": false,
            file: location.href.replace(/\/[^\/]*$/,"")+"/%s",
            height: %s, width: %s,
            image: "%s" }"""
        options = options % (self.flashPlayerUrl, filepath, height, width, thumbnail)
        return options

    def __getAudioJwPlayerOptions(self, filepath, height, width):
        options = """{flashplayer: "%s",
            controlbar: "bottom",
            file: location.href.replace(/\/[^\/]*$/,"")+"/%s",
            height: %s, width: %s}"""
        options = options % (self.flashPlayerUrl, filepath, height, width)
        return options

    def __getWidthHeight(self, filename, queryParams):
        width = 400
        height = 40
        if filename=="preview.flv":
            width = 410
            height = 234
        elif filename=="preview.mp4":
            width = 480
            height = 320
        elif filename=="hiRes.mp4":
            width = 1024
            height = 768
        elif filename=="hiRes.flv":
            width = 810
            height = 610
        elif filename=="audio.mp3":
            height = 24
        width = queryParams.get("width", width)
        height = queryParams.get("height", height)
        return width, height

    def __getIsAudioIsVideoIsHtml(self, filename):
        isAudio = False
        isVideo = False
        isHtml = False
        if filename.endswith(".flv") or filename.endswith(".mp4"):
            isVideo = True
        elif filename.endswith(".mp3"):
            isAudio = True
        elif filename.endswith(".htm") or filename.endswith(".html"):
            isHtml = True
        return isAudio, isVideo, isHtml

