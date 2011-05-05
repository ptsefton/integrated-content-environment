#    Copyright (C) 2006  Distance and e-Learning Centre, 
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
import urlparse
from hashlib import md5
import time
import urllib
import json
from http_util import Http

class odpBaseConverter:
    # Constructor
    #    __init__(iceContext, getRelativeLinkMethod, oooConverterMethod)
    # Properties:
    #    
    # Methods:
    #    renderMethod(file, absFile, oooConverterMethod=None) -> convertedData object
    #    renderPdfOnlyMethod(file, absFile, oooConverterMethod=None) -> convertedData object
    #    
    # Private Methods:
    #    _setup(copyToMethod, sourceFileName, absSourceFile=None, convertToOdp=False)
    #    _close()
    #    _convertToHtml()
    #        _convertFile(self._tmpOooFileName, self._tmpHtmlFileName)
    #        __processHtmlContentXml(self._contentXml, self.__stylesXml)
    #            Transforming contentXml using python or xslt  NOTE: newXml = xhtml
    #            __processImages(xml)
    #                imageNames = __findAllImageNames(self._tmpHtmlFileName)
    #                __convertImageNames(xml, self._sourceFileName, imageNames)        
    #            __processContent(xml, self._sourceFileName)
    #                __fixupImageReferences(xml)
    #                    __processImageNode
    #                       __convertImageToJpg()
    #   
    
    def __init__(self, iceContext, \
                        getRelativeLinkMethod=None, oooConverterMethod=None):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs
        self._fs = self.__fs
        plugin = self.iceContext.getPlugin("ice.ooo.ooo2xhtml")
        if plugin is None:
            raise Exception("ice.ooo.ooo2xhtml plugin not found!")
        self.__ooo2xhtml = plugin.pluginClass
        if getRelativeLinkMethod is None:
            getRelativeLinkMethod = iceContext.getRelativeLink
        self.__getRelativeLinkMethod = getRelativeLinkMethod
        if oooConverterMethod is None:
            oooConverterMethod = iceContext.getOooConverter().convertDocumentTo
        self._oooConverterMethod = oooConverterMethod
        
        self.OOoNS = self.iceContext.OOoNS.items()
       
        self.__lastTime = None
        self._sourceFileName = None
        self._tmppptFileName = None
        self._tmpOooFileName = None
        self._tmpHtmlFileName = None
        self._tmpPdfFileName = None
        self._contentXml = None
        self.__baseUrl = None        # doc
        self.__packageUrl = None     # doc
        self.convertToOdp = False
        self.__output = iceContext.output
        self._imageMagickPath = None
        self._exiftoolPath = None
        
        self.__embeddedPlugins = {
                        ".mov": "http://www.apple.com/quicktime/download/" 
                        }
        self.__objectsClassIdCodeBase = {
                        ".swf": ("clsid:d27cdb6e-ae6d-11cf-96b8-444553540000", 
                                  "http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0",
                                  "application/x-shockwave-flash"),
                        ".wmv": ("clsid:6BF52A52-394A-11d3-B153-00C04F79FAA6", 
                                  "http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=6,4,7,1112",
                                  "video/x-ms-wmv"),
                        ".dcr": ("clsid:166B1BCA-3F9C-11CF-8075-444553540000", "", "application/x-director"),
                        ".rm": ("clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA", "", "audio/x-pn-realaudio-plugin"),
                        ".mov": ("clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B", "http://www.apple.com/qtactivex/qtplugin.cab", "video/quicktime"),
                        }
        self.__transformMethod = None
        self.__stylesXml = None
        self.__convertLinksToEndNotes = False
        self.convertedData = None
        
        self.__relDocPath = None
        self.__startOpenOffice = True
        self.__openOfficeProcess = None
    
    
    @property
    def transformUsingPython(self):
        if self.__transformMethod is not None:
            return self.__transformMethod
        return self.iceContext.config.settings.get("transformUsingPython", True)

    def setTransformUsingPython(self, value=True):
        self.__transformMethod = value

    def __startOpenOfficePipe(self):
        if self.__startOpenOffice and self.iceContext.isServer==False:
            soffice ="soffice"
            try:
                soffice = self.iceContext.urlJoin(self.iceContext.settings.get("oooPath"), "program/soffice")
            except: pass
            print "*** Failed to connect to OpenOffice - try starting OpenOffice"
            print "*** Starting soffice='%s'" % soffice
            p3 = self.iceContext.system.execute3(soffice, 
                "-accept=pipe,name=oooPyPipe;urp;StarOffice.ServiceManager",
                "-quickstart", "-norestore", "-nodefault") #, "-invisible") # "-nologo" "-minimized" "-headless"
            self.__openOfficeProcess = p3
            print "Waiting for OpenOffice to startup"
            self.iceContext.sleep(8)
    
    # Main Method
    # Note: the rep is only used to access the export method
    def renderMethod(self, file, convertedData, statusCallback=None, **kwargs):
        # Store thumbnail options for later
        self.options = {}
        if kwargs.has_key("multipleImageOptions"):
            self.options["multipleImageOptions"] = kwargs["multipleImageOptions"]

        self.convertedData = convertedData
        convertedData = self._render(file, True)
        if convertedData.errorMessage.startswith("Failed to connect to OpenOffice"):
            self.__startOpenOfficePipe()
            print "OK trying again"
            convertedData.clearError()
            self.convertedData = convertedData
            convertedData = self._render(file, True)
            if convertedData.errorMessage.startswith("Failed to connect to OpenOffice"):
                self.__startOpenOffice = False
        return convertedData
    
    
    def renderPdfOnlyMethod(self, file, convertedData, reindex=False, **kwargs):
        self.convertedData = convertedData
        return self._render(file, False, reindex=reindex)
    
    
    def _render(self, file, includeHtml=True, reindex=False):
        rep = self.iceContext.rep
        if rep is not None:
            absFile = rep.getAbsPath(file)
        else:
            absFile = file
        self.__relDocPath, _, _ = self._fs.splitPathFileExt(file)

        try:
            if rep is None or not hasattr(rep, "getProperty"):
                def copy(src, dest):
                    src = absFile
                    self.__fs.copy(src, dest)
                    pass
                if rep is not None: #when there is no attribute getProperty but has rep
                    item = rep.getItem(file)
                    self.__convertLinksToEndNotes = False
                    if bool(item.getMeta("_convertLinksToEndNote")):
                        self.__convertLinksToEndNotes = True

                setup=self._setup(copy, file, absFile, convertToOdp=self.convertToOdp)
            else:
                item = rep.getItem(file)
                self.__convertLinksToEndNotes = False
                if bool(item.getMeta("_convertLinksToEndNote")):
                    self.__convertLinksToEndNotes = True
                setup=self._setup(rep.copyx, file, absFile, convertToOdp=self.convertToOdp)
                if setup == True:
                    # Hack for Word files
                    basePackageUrl = item.getMeta("_basePackageUrl")
                    if basePackageUrl is not None:
                            self.__baseUrl, self.__packageUrl = basePackageUrl
                            self.__packageUrl = self.__packageUrl.rstrip("/")

        except Exception, e:
            print "error :", str(e)
            self._close()
            self.convertedData.addErrorMessage(str(e))
            self.convertedData.terminalError = True
            self.convertedData.Exception = e
            cData = self.convertedData
            self.convertedData = None
            
            return cData
        
        if setup==True:
            self._renderMethod(file, absFile, includeHtml, reindex=reindex)
            if self.convertedData.getMeta("title")=="":
                self.convertedData.addMeta("title", self.convertedData.meta.get("title", "Untitled"))
            elif self.convertedData.meta.get("title", "")=="":
                self.convertedData.meta["title"] = self.convertedData.getMeta("title")
        else:
            msg = "Open Office document is Invalid"
            self.convertedData.addErrorMessage(msg)
            self.convertedData.terminalError = True
            self.convertedData.Exception = msg
            cData = self.convertedData
            self.convertedData = None
            return cData
        self._close()
        
        cData = self.convertedData
        self.convertedData = None
        return cData
    
    
    # virtual method
    def _renderMethod(self, file, absFile, includeHtml=True, reindex=False):
        #raise Exception("This method must be overriden!")
        #converter = self._oooConverterMethod
        
        #check if has local imagemagic and exiftool
        useLocalOpenOffice = self.iceContext.settings.get("useLocalOpenOffice")
        if not self.__hasLocalImageMagick() or useLocalOpenOffice == False:
            self.__convertUrl = self.iceContext.settings.get("convertUrl")
            if self.__convertUrl=="":
                self.__convertUrl = None
            if self.__convertUrl is not None:
                self.__convertUrl += "/odp"
            if self.__convertUrl is not None:
                print "Using PPT/ODP service at", self.__convertUrl
                tempDir = self.__fs.createTempDirectory()
                tempZipFileName = tempDir.absolutePath("temp.zip")
                fd = open(absFile, "rb")
                #postData = [("file", fd)]
                
                options = {}
                options.update({"sessionid": ""})
                postData = [(k, v) for k, v in options.iteritems()]
                pptData = fd.read()
                postData.append(("file", ("%s" % absFile, pptData)))
                postData.append(("zip", "True"))
                
                zipData, headers, _, _ = self.iceContext.Http().post(self.__convertUrl, postData,
                                                                includeExtraResults=True)
                
#                if data.find("ice-error") > -1:
#                    self.convertedData.addErrorMessage("Error in _convertToPdf() - from server")
#                else:
                #returning zip file
                self.__fs.writeFile(tempZipFileName, zipData)
                unzipFile = self.__fs.unzipToTempDirectory(tempZipFileName)
                dirs, files = unzipFile.listDirsFiles()
                
                _, name, _ = self.__fs.splitPathFileExt(absFile)
                #xhtml.body
                renditionName = "%s.htm" % name
                if renditionName in files:
                    filePath = unzipFile.absPath(renditionName)
                    rendition = self.__fs.readFile(filePath)
                    
                    xmlRendition = self.iceContext.Xml(rendition)
                    body = xmlRendition.getNode("//body")
                    div = xmlRendition.createElement("div")
                    if body:
                        renditionLinks = body.getNode("./div[@class='rendition-links']")
                        renditionLinks.remove()
                        for child in body.getChildren():
                            div.addChild(child)
                    rendition = str(div)
                    xmlRendition.close()
                    self.convertedData.addRenditionData(".xhtml.body", rendition)
                pdfRendition = "%s.pdf" % name
                if pdfRendition in files:
                    filePath = unzipFile.absPath(pdfRendition)
                    self.convertedData.addRenditionFile(".pdf", filePath)
                    self.convertedData.getRendition(".pdf")        

                supportDir = "%s_files" % name
                if supportDir in dirs:
                    supportPath = unzipFile.absPath(supportDir)
                    for file in self.__fs.listFiles(supportPath):
                        if file.endswith(".jpg"):
                            imagePath = unzipFile.absPath("%s/%s" % (supportDir, file))
                            self.convertedData.addImageData(file, self.__fs.readFile(imagePath))

                tempDir.delete()
                unzipFile.delete()
                fd.close()                    
        else:
            oooConverterMethod = None 
            if True:
                # PDF
                try:
                    result = self._convertToPdf(reindex=reindex)
                    #convert to html using the images generated by the pdfs...
                    
                    result = self._convertToHtml()
                    
                    if result!="ok":
                        self.convertedData.addErrorMessage(result)
                except Exception, e:
                    self.convertedData.addErrorMessage("Error in _convertToPdf() - " + str(e))
            
    def __hasLocalImageMagick(self):
        try:
            cmd = self.iceContext.settings.get("imageMagickPath","convert")
            if self.iceContext.isWindows:
                cmd =r"%s " %  cmd
            _, stderr = self.__execute3(cmd)

            self._imageMagickPath = cmd
            if self.iceContext.isWindows:
                keyword = "recognized"
            else:
                keyword = "found"
            hasLocal = stderr.find("not " + keyword) == -1
            #now check exif
            if hasLocal:
                cmd =self.iceContext.settings.get("exiftoolPath","exiftool")
            if self.iceContext.isWindows:
                cmd =r"%s " %  cmd
                _, stderr = self.__execute3(cmd)
                self._exiftoolPath = cmd
                if self.iceContext.isWindows:
                    keyword = "recognized"
                else:
                    keyword = "found"
                hasLocal = stderr.find("not " + keyword) == -1
            return hasLocal
        except Exception,e:
            print "Error in Finding ImageMagick - '%s'" % str(e)
            #ice-server doesnot have imageMagick yet. So have to direct to ice-service for now. 
            #raise
    
    def __execute3(self, cmd, *args):
        stdout, stderr = self.iceContext.system.executeNew(cmd, *args)
        return stdout, stderr
        #out = stdout.read()
        #err = stderr.read()
        #stdin.close()
        #stdout.close()
        #stderr.close()
        #return out, err
    
    def _setup(self, copyToMethod, sourceFileName, absSourceFile=None, convertToOdp=False):
        self._sourceFileName = sourceFileName
        self._tmpOooFileName = self.convertedData.abspath("temp.odp")
        sourceExt = self.__fs.splitExt(sourceFileName)[1]
        self._tmppptFileName = self.convertedData.abspath("temp" + sourceExt)
        self._tmpHtmlFileName = self.convertedData.abspath("temp.html")
        self._tmpPdfFileName = self.convertedData.abspath("temp.pdf")
        #self._tmpDir = self.convertedData.abspath("tmpDir")
        if convertToOdp:
            # Convert to odp first
            copyToMethod(sourceFileName, self._tmppptFileName)
            result = self._convertToOdp(self._tmppptFileName, self._tmpOooFileName)
            if result == "Power point document is Invalid":
                self.__startOpenOfficePipe()
                result = self._convertToOdp(self._tmppptFileName, self._tmpOooFileName)
                if result == "Power point document is Invalid":
                    self.__startOpenOffice = False
                    raise Exception(result)
            # Repair
        else:
            copyToMethod(sourceFileName, self._tmpOooFileName)
        
        try:
            content = self.__fs.readFromZipFile(self._tmpOooFileName, "content.xml")
            if content is None:
                return False
            try:
                self._contentXml = self.iceContext.Xml(content, self.OOoNS)
                if self.__testForLinkedImages()>0:
                    self.__breakLinks(absSourceFile)
                    copyToMethod(sourceFileName, self._tmpOooFileName)
                    content = self.__fs.readFromZipFile(self._tmpOooFileName, "content.xml")
                    self._contentXml = self.iceContext.Xml(content, self.OOoNS)
            except Exception, e:
                msg = "ERROR: Failed to transformToDom! - " + str(e)
                msg += " Skipping sourceFile " + sourceFileName
                print msg
                return False
            self.__stylesXml = self.__fs.readFromZipFile(self._tmpOooFileName, "styles.xml")
            
            if True:
                # HACK: add text:outline-style element (from styles.xml) to the content.xml
                styles = self.__fs.readFromZipFile(self._tmpOooFileName, "styles.xml")
                stylesXml = self.iceContext.Xml(styles, self.OOoNS)
                node = stylesXml.getNode("//text:outline-style")
                outlineStyleStr = str(node)
                stylesXml.close()
                if outlineStyleStr == "None":
                    pass
                    #raise Exception ("Open Office document is Invalid")
                    #return False
                else:
                    try:
                        outlineStyleStr = outlineStyleStr.replace("<text:outline-style>", 
                            "<text:outline-style xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0'>")
                        newElem = self._contentXml.xmlStringToElement(outlineStyleStr)
                        asNode = self._contentXml.getNode("/office:document-content/office:automatic-styles")
                        tosNode = asNode.getNode("*[name()='text:outline-style']")
                        if tosNode is None:
                            asNode.addChild(newElem)
                        else:
                            # Note: this should not be needed
                            self._contentXml.getRootNode().addChild(newElem)
                    except Exception, e:
                        self.__write("Styles.xml Error - %s\n" % str(e))
            title = self._getTitle()
            self.convertedData.addMeta("title", title)
            return True
        except Exception, e:
            return False    
    
    
    def _close(self):
        if self._contentXml != None:
            self._contentXml.close()
            self._contentXml = None
    
    
    def convertPptToOdp(self, pptFile, odpFile):
        return self._convertToOdp(pptFile, odpFile)
    def _convertToOdp(self, pptFile, odpFile):
        # Note: used for WORD (.doc) files only
        result = ""
        result, msg = self._convertFile(pptFile, odpFile)
        if result==False:
            result = "Power Point document is Invalid" 
            return result
        
        if True:        # Do Word HACKS
            tmpDir = self.__fs.unzipToTempDirectory(odpFile)
            contentPath = self.__fs.join(str(tmpDir), "content.xml")
            content = self.iceContext.Xml(contentPath, self.OOoNS)
            
            #Check if there're any content 
            xpath = "//office:document-content/office:body/office:spreadsheet/*[not(name()='office:forms')]" + \
                        "[not(name()='text:sequence-decls')]"
            nodes = content.getNodes(xpath)
            
            #Check if there are content in the document
            hasContent = False
            for node in nodes:
                if node.getContent() != "" or len(node.getChildren()) > 0:
                    hasContent = True
            if hasContent == False:
                result = "Excel document is Invalid"                      
            else:
                # HACK: Fixup tables so that rows expand across pages
                nodes = content.getNodes("//style:table-row-properties/@style:keep-together[.='false']")
                l = len(nodes)
                for node in nodes:
                    node.setContent("true")
                # HACK: To work around an oOffice bug # where the title is cut to no more than ~63 characters
                try:
                    metaTitle = self._getTitle()
                except:
                    metaTitle = ""
                if len(metaTitle)>62:
                    #metaPath = os.path.join(str(tmpDir), "meta.xml")
                    metaPath = self.__fs.join(str(tmpDir), "meta.xml")
                    meta = self.iceContext.Xml(metaPath, self.OOoNS)
                    test = "@text:style-name=//style:style[starts-with(@style:parent-style-name, 'Title')]/@style:name"            
                    title = content.getContent("//office:body/office:spreadsheet/table:table[%s]" % test)
                    if title is None:
                        title = content.getContent("//office:body/office:spreadsheet/table:table[@table:name][%s]" % test)
                    dcTitle = meta.getNode("//office:meta/dc:title")
                    #print str(text)
                    if dcTitle!=None:
                        dcTitleContent = dcTitle.getContent()
                        if title is None:
                            dcTitle.setContent(metaTitle[:62])
                        elif title.startswith(dcTitle.getContent()):
                            dcTitle.setContent(title)
                        elif dcTitleContent.find(title[:32])>0:
                            pos = dcTitleContent.find(title[:32])
                            pre = dcTitleContent[:pos]
                            rest = dcTitleContent[pos:]
                            if title.startswith(rest):
                                dcTitle.setContent(pre + title)
                    meta.saveFile()
                    meta.close()
                
                content.saveFile()                
            content.close()
            tmpDir.zip(odpFile)
            tmpDir.delete()
        return result


    def _convertToHtml(self):
        #directly apply to the self._tmpHtmlFileName
        
        fileName = self.__fs.splitPathFileExt(self._sourceFileName)[1] 
        
        slideDetail = self.convertedData.getMeta("slideDetail")
        rendition = "<div>"
        images = self.convertedData.getMeta("images")
        count = 1
        for image in images:
            if image.find("_thumbnail")<0:
                detailPage = "page%s" % count
                title = "Page %s" % count
                name = "%s_files/%s" % (fileName, image)
                rendition += """<div class='slide'><h1>%s</h1><p>
                             <img name='%s' src='%s' width='552' height='413'/></p></div>""" % (title, name, name)
                count += 1
        rendition += "</div>"
        
        self.convertedData.addRenditionData(".xhtml.body", rendition)
        
        #<div class="slide"><h1>Hslide<br/>Slide content</h1><p class="P4"/>
        #<p class="P4">azsdasd</p></div><p/><p/><div class="slide"><h1>Hslide 2</h1><p class="P4">Slide 2 content</p></div>
        
        return "ok"
    
    def _convertToPdf(self, reindex=False):
        officeValue = ""
        separator = ""
        
        tempFs = self.__fs.unzipToTempDirectory(self._tmpOooFileName)
        xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), 
                       self.iceContext.OOoNS.items())

        #Need to read each slide and get the information
        slideDetail = {}
        slidePages = xml.getNodes("//draw:page")
        count = 1
        for slide in slidePages:
            pageName = slide.getAttribute("name")
            title = ""
            if not pageName.startswith("page"):
                title = pageName
            slideChildren = slide.getChildren()
            content = ""
            if slideChildren:
                for child in slideChildren:
                    #need to loop through the child to get a clean content
                    content += child.getContent()
                content += ", "
            if title == "" or title is None:
                title = "[ Untitled ]"
            count +=1
            slideDetail[count] = "%s, %s" % (title, content.rstrip(", "))
            
        self.convertedData.addMeta("slideDetail", slideDetail)
        
        xml.close()
        tempFs.zip(self.__fs.absolutePath(self._tmpOooFileName))
        tempFs.delete()
                
        result, msg = self._convertFile(self._tmpOooFileName, \
                    self._tmpPdfFileName, reindex=reindex)
        if result==False:
            return msg
        self.convertedData.addRenditionFile(".pdf", self._tmpPdfFileName)
        self.convertedData.getRendition(".pdf")
        self.__convertToJpg(self._tmpPdfFileName)

        return "ok"
        
    def __convertToJpg(self, pdfFileName):
        #convert -density 100 file.pdf file%02d.jpg
        try:
            fileName = self.__fs.splitPathFileExt(self._sourceFileName)[1]
            tempImageDir = self.__fs.createTempDirectory()
            outputFileName = tempImageDir.absPath(fileName + "%02d.jpg")
            outputFileName = outputFileName.replace(" ", "_")
            cmd = self._imageMagickPath
            if cmd is None:
                cmd = "convert"
            if self.iceContext.isWindows:
                cmd = r"%s" % cmd
            stdout, stderr = self.__execute3(cmd,"-density", "100", "%s" % pdfFileName, "-scale", "2000x1000", "%s" % outputFileName)
            slideDetail = self.convertedData.getMeta("slideDetail")
            images = []
            count = 1
            convertedImagesFiles = tempImageDir.listFiles()
            if convertedImagesFiles:
                convertedImagesFiles.sort() 
                for file in convertedImagesFiles:
                    path, name, ext = self.__fs.splitPathFileExt(file)
                    imageName = "%s%s" % (name, ext)
                    imageTempFilePath = tempImageDir.absPath(file)
                    imageDetailPage = "page%s" % count
                    if slideDetail.has_key(count):
                        self.__addImageMeta(imageTempFilePath, slideDetail[count])
                        
                    self.convertedData.addImageData(imageName, self.__fs.readFile(imageTempFilePath))
                    
                    # First page needs a thumbnail
                    if count == 1:
                        imageOptions = {}
                        imageOptions["thumbnail"] = {}
                        # But does it haves the config to generate one?
                        if self.options.has_key("multipleImageOptions"):
                            # Get and trim our config to exclude extra renditions
                            multipleImageOptions = json.loads(self.options["multipleImageOptions"])
                            if multipleImageOptions and multipleImageOptions.has_key("thumbnail"):
                                imageOptions["thumbnail"] = multipleImageOptions["thumbnail"]
                                self.options["multipleImageOptions"] = json.dumps(imageOptions)
                        # No config found, create some defaults
                        if not imageOptions["thumbnail"].has_key("option"):
                            imageOptions["thumbnail"]["option"] = "fixedWidth"
                            imageOptions["thumbnail"]["ratio"] = "-90"
                            imageOptions["thumbnail"]["fixedWidth"] = "160"
                            imageOptions["thumbnail"]["enlarge"] = "false"
                            self.options["multipleImageOptions"] = json.dumps(imageOptions)
                        # Run the converter
                        thumbConvert = self.iceContext.getPlugin("ice.converter.imageResize").pluginClass
                        thumbConvert = thumbConvert(self.iceContext)
                        thumbConvert.convert(imageTempFilePath, self.options, tempImageDir)
                        imageThumbnailName = "%s_thumbnail%s" % (name, ext)
                        imageTempFullPath = "%s/%s" % (tempImageDir, imageThumbnailName)
                        self.convertedData.addImageData(imageThumbnailName, self.__fs.readFile(imageTempFullPath))
                        images.append(imageThumbnailName)

                    #need to add metadata for each of the images
                    images.append(imageName)
                    count+=1
            self.convertedData.addMeta("images", images)            
            tempImageDir.delete()
        except Exception, e:
            print 'error in converting pdf to jpg: ', str(e)
    
    def __addImageMeta(self, imagePath, imageMeta):
        try:
            cmd = self._exiftoolPath
            if cmd is None:
                cmd = "exiftool"
            if self.iceContext.isWindows:
                cmd = r"%s" % cmd
            if self.iceContext.isWindows:
                self.__execute3(cmd, "-UserComment='%s'" % imageMeta, '"%s"' % imagePath)
            else:
                self.iceContext.system.execute2(cmd,
                            "-UserComment='%s'" % imageMeta, '"%s"' % imagePath)
        except Exception, e:
            print 'error in inserting metadata to the image: ', str(e)

    
    def __breakLinks(self, file, toFile=None):
        if toFile is None:
            toFile = file
        self.__write("**** Linked Images to be broken ****\n")
        self.__write(" file='%s'\n" % file)
        tempDir = self.__fs.unzipToTempDirectory(file)
        tPath = str(tempDir)
        
        #xml = self.iceContext.Xml(os.path.join(tPath, "content.xml"), self.OOoNS)
        xml = self.iceContext.Xml(self.__fs.join(tPath, "content.xml"), self.OOoNS)
        xpath = "//office:document-content/office:body/office:text//draw:image/@xlink:href"
        nodes = xml.getNodes(xpath)
        for href in nodes:
            value = href.content
            if value.startswith("../") or value.startswith("/"):
                if value.startswith("../"):
                    #value = value[3:]
                    count = 0
                    f = file
                    while value.startswith("../"):
                        value = value[3:]
                        #f = os.path.split(f)[0]
                        f = self.__fs.split(f)[0]
                    #value = os.path.join(f, value)
                    value = self.__fs.join(f, value)
                try:
                    f = open(value, "rb")
                    data = f.read()
                    f.close()
                    #name, ext = os.path.splitext(value)
                    name, ext = self.__fs.splitExt(value)
                    newName = "Pictures/" + md5(data).hexdigest() + ext
                    href.content = newName
                    self.__fs.makeDirectory(self.__fs.join(tPath, "Pictures"))
                    self.__fs.writeFile(self.__fs.join(tPath, newName), data)
                except Exception, e:
                    self.__write("Error: (in .__breakLinks()) %s\n" % str(e))
                    # OK then remove this image instead
                    href.getParent().delete()
        xml.saveFile()
        xml.close()
        tempDir.zip(toFile)
        tempDir.delete()


    def __testForLinkedImages(self, contentXml=None):
        if contentXml is None:
            contentXml = self._contentXml
        xpath = "//office:document-content/office:body/office:text//draw:image/@xlink:href"
        nodes = contentXml.getNodes(xpath)
        hrefs = [href.content for href in nodes]
        hrefs = [href for href in hrefs if href.startswith("../") or href.startswith("/")]
        return len(hrefs)
    
    
    def _convertFile(self, sourceFileName, destFileName, reindex=False):
        """ Using Ooo, convert from sourceFileName to destFileName"""
        result = False
        try:
            result, msg = self._oooConverterMethod(sourceFileName, \
                                    destFileName, reindex=reindex)
        except Exception, e:
            self.__write("#### Error in oooConverterMethod: %s\n" % str(e))
            raise e
        return result, msg

    
    def _getTitle(self):
        meta = self.__fs.readFromZipFile(self._tmpOooFileName, "meta.xml")
        xml = self.iceContext.Xml(meta, self.OOoNS)
        title = ""
        node = xml.getNode("//office:meta/dc:title")
        if node!=None:
            title = node.getContent()
        if title==None or title=="":
            title = ""
        xml.close()
        return title

    
    def __processHtmlContentXml(self, html, stylesXml=None):
        if html is None:
            return
        htmlCleanup = self.iceContext.HtmlCleanup
        html = htmlCleanup.convertHtmlToXml(html)
        def entitySub(m):
            e = m.group()
            if self.iceContext.xml_entites.has_key(e):
                # leave as is
                pass
            else:
                unknownEntity = u"\u00bf"       # inverted '?'
                u = self.iceContext.xhtml_entities.get(e, unknownEntity)
                e = "&#%s;" % hex(ord(u))[1:]
            return e
        html = re.sub("\&[a-z0-9]+;", entitySub, html)
        try:
            xml = self.iceContext.Xml(html)
            try:
                xml = self.__cleanupCapitalName(xml)
            except Exception, e:
                self.__write("Error in cleanup : %s " % e)
            if stylesXml is None:
                stylesXml = self.__stylesXml
            st = time.time()

            # check for any special charecters
            self.__processSpecialCharacters(xml)
            self.__processContent(xml, self._sourceFileName)
            
            et = time.time() - st
            self.__write(" done transforming content using python in %s mS\n" % int(et * 1000))
            
            return xml
        except Exception, e:
            raise "Error in parsing to XML "
 

    def __notEmpty(self, node):
        return node is not None or node != [] or node != {} 
    
    def __cleanUpAttribute(self, node):
        attrs = node.getAttributes()
        if self.__notEmpty(attrs):
            for key in attrs:
                attrVal = attrs[key]
                node.removeAttribute(key)
                node.setAttribute(key.lower(), attrVal.lower())
        return node
    
    def __cleanupCapitalName(self, xml):
        xml = self.__cleanUpAttribute(xml)
        children = xml.getChildren()
        if self.__notEmpty(children):
            for child in children:
                child = self.__cleanUpAttribute(child)
                child.setName(child.getName().lower())
                if self.__notEmpty(child.getChildren()):
                    self.__cleanupCapitalName(child)
        else:
            xml.setName(xml.getName().lower())
        return xml

    def __processContent(self, xml, sourceFilename):
        try:
            images = self.__processImages(xml)

            # fixup links to be relative links
            links = self.__fixupRelativeLinks(xml, sourceFilename)
            self.__fixupImageReferences(xml)
            self.convertedData.addRenditionData(".ALL.txt", str(xml))
    
            #Style:
            elems = xml.getNodes("//STYLE | //style")
            style = ""
            if len(elems)<>0:
                styleElem = elems[0]
                style = str(styleElem)
                self.convertedData.addMeta("style.css", style)
            else:
                self.__write("*****\n Did not find the style element! \n*****\n")
            
            #elems = xml.getNodes("//body/*")
            # HACK: Replaced previous line with the next 2 lines
            # to fix problem using Mac compiled version (crashes when rendering)       
            body = xml.getNode("//BODY | //body")
            elems = body.getNodes("*")
            
            rendition = "<div>"
            for elem in elems:
                rendition += str(elem)
            rendition += "</div>"
            
            self.convertedData.addRenditionData(".xhtml.body", rendition)
            
            # setMeta data
            self.convertedData.addMeta("images", images)
            self.convertedData.addMeta("links", links)
            xml.close()
        except:
            raise "Error in processing XML content"
            
            
    def __processSpecialCharacters(self, xhtml):
        textNodes = xhtml.getNodes("//text()")
        try:
            for textNode in textNodes:
                text = textNode.content
                utext = unicode(text, "utf-8")
                utext = utext.replace("&", "&amp;").replace("<", "&lt;")
                specialChars = {}
                for uc in utext:
                    ucv = ord(uc)
                    if ucv>127 and ucv<>160:
                        specialChars[uc] = True
                if len(specialChars)>0:
                    for uc in specialChars.keys():
                        hValue = hex(ord(uc))
                        entity = "&#%s;" % hValue[1:]
                        utext = utext.replace(uc, "<span class='spCh spCh%s'>%s</span>" % (hValue[1:], entity))
                    newNodeList = xhtml.xmlStringToNodeList(utext.encode("utf-8"))
                    textNode.replace(newNodeList)
                    textNode.delete()
        except Exception, e:
            self.__write("Error: %s\n" % str(e))
                    
    def __processImages(self, xhtml):
        # dictionary of images, name:filename eg Graphic1:graphic.png
        imageNames = {}
        try:
            imageNames = self.__findAllImageNames(xhtml)
        except Exception, e:
            msg = "ERROR in findAllImageNames(): - " + str(e)
            raise Exception(msg)
        
        try:
            images = self.__convertImageNames(xhtml, self._sourceFileName, imageNames)
            return images
        except Exception, e:
            msg = "ERROR in convertImageNames(): - " + str(e)
            raise Exception(msg)
    
#    
    def __findAllImageNames(self, xml):
        """Given a html file, search for img tags and load name, src into a dictionary"""
        imageNames = {}
        try:
            imgNodes = xml.getNodes("//IMG  | //img")
            count = 0
            for img in imgNodes:
                src = img.getAttribute("src")
                name = img.getAttribute("name")
                if name== "" or name is None:
                    name = str(count)
                    count = count + 1
                imageNames[name] = src
            return imageNames
        except Exception, e:
            self.__write("Couldn't file the image name. \n Error %s" % str(e))


    def __convertImageNames(self, xml, sourceFilename, imageNames):
        """Convert image names from OOo format (eg src="#Pictures/100000000000002D0000002D7AE625C4")
        to HTML format (eg src="Module1_html_7ae625c4.png")
        Also copy the image file into the repository"""
        # TODO keep a list of images which have already been copied and don't copy them again
        
        copiedImages = dict()
        linkedImages = dict()
        count = 0
        imageNodes = xml.getNodes("//IMG  | //img")
        for img in imageNodes:
            # find image by name in dictionary and substitute the src filename
            href = img.getAttribute("src")
            name = img.getAttribute("alt") 
            height = None
            width = None
            if name== "" or name is None:
                name = str(count)
                count = count + 1
            
            if img.getAttribute("width")!=None and img.getAttribute("height")!=None:
                width = img.getAttribute("width")
                height = img.getAttribute("height")
            if imageNames is not None and imageNames.has_key(name): 
                src = imageNames[name]
                simpleName = self.__getSimpleImageFileName(src)   
                if not copiedImages.has_key(src):
                    copiedImages[src] = simpleName
                    data = None
                    self.convertedData.addImageFile(simpleName, filename=src)
                if height!=None:
                    nameOnly, ext = self.__fs.splitExt(simpleName)
                    simpleName = nameOnly + "_" + width + "x" + height + ext
                linkedImages[simpleName] = simpleName
                simpleName = self.__getRelativeImageLink(simpleName, sourceFilename)
                img.setAttribute("src", simpleName)
            else:
                pass
        return linkedImages.values()

    
    def __fixupRelativeLinks(self, xml, sourceFilename):
        try:
            links = []
            refNodes = xml.getNodes("//*[@href]")
            
            for ref in refNodes:
                # this call will return url with entities resolved eg &amp;
                url = ref.getAttribute("href")
                replaceStr = url
                url = self.__getRelativeLink(sourceFilename, url)
                ref.setAttribute("href", url)
                
                if ref.getAttribute("onclick") is not None:
                    replaced = ref.getAttribute("onclick").replace(replaceStr, url)
                    ref.setAttribute("onclick", replaced)
                
                linkText = ""
                nodes = ref.getNodes("*|text()")
                for node in nodes:
                    #Ignore link especially from foot notes or endnodes
                    if node.getName() != "a":
                        linkText += str(node)
                links.append([url, linkText])    
             
            # Fixup src links
            srcNodes = xml.getNodes("//*[@src]")
            for src in srcNodes:
                url = src.getAttribute("src")
                url = self.__getRelativeLink(sourceFilename, url)
                src.setAttribute("src", url)
                
            # Fixup object data links
            dataNodes = xml.getNodes("//object[@data]")
            for data in dataNodes:
                url = data.getAttribute("data")
                url = self.__getRelativeLink(sourceFilename, url)
                data.setAttribute("data", url)
            # Fixup object value links
            dataNodes = xml.getNodes("//object/param[@name='url' or @name='movie']")
            for data in dataNodes:
                url = data.getAttribute("value")
                url = self.__getRelativeLink(sourceFilename, url)
                data.setAttribute("value", url)
            
        except Exception, e:
            self.__write("Error in __fixupRelativeLinks() - Error: %s\n" % str(e))
            raise e
        return links

   
    def __getRelativeLink(self, sourceFilename, url):
        if self.__baseUrl is not None:
            if url.startswith(self.__baseUrl):
                # fixup the url
                urlParts = url.split("/")
                packageParts = self.__packageUrl.split("/")
                for x in range(len(packageParts)):
                    urlParts[x] = packageParts[x]
                url = "/".join(urlParts)
        if callable(self.__getRelativeLinkMethod):
            url = self.__getRelativeLinkMethod(sourceFilename, url)
        return url
    
    
    def __getRelativeImageLink(self, imgSrc, sourceFilename):
        """get a reference to the img src, relative to the source filename"""
        fileName = self.__fs.split(sourceFilename)[1]
        baseName = self.__fs.splitExt(fileName)[0]
        if fileName.endswith(".book.odt") or fileName.endswith(".book.odp"):
            baseName = self.__fs.splitExt(baseName)[0]
        src = "%s_files/%s" % (baseName, imgSrc)
        return src
    
    
    def __getSimpleImageFileName(self, src):
        """given a src like Module_1_Instructional_Design_and_Fl_htm_m268e6629.png,
        return the simple bit ie m268e6629.png
        """
        index = src.rfind("_") + 1
        src = src[index:]
        return src
#    
#    
    def __time(self):
        now = time.time()
        t = 0
        if self.__lastTime!=None:
            t = now - self.__lastTime
        self.__lastTime = now
        return round(t, 3)

    
    def __fixupImageReferences(self, xml):
        try:
            imgNodes = xml.getNodes("//img")

            images = {}
            for node in imgNodes:
                newImgName = self.__processImageNode(node)
                newImgName = self.__fs.split(newImgName)[1]
                images[newImgName] = None
            for img in self.convertedData.imageNames: 
                if not images.has_key(img):
                    self.convertedData.removeImage(img)
            images = images.keys()
            images.sort()
            self.convertedData.addMeta("images", images)
        except Expection, e:
            self.__write("Error in fixing up Image References: % s"%str(e))


    def __processImageNode(self, node):  
        src = ""
        newImgName = ""
        try:
            # get image name from src
            src = node.getAttribute("src")
            if src is None:
                src = node.getAttribute("SRC")
            orgImgName = src
            newImgName = src
            m = re.search("(.*?)/(.*?)_(\d+)x(\d+)(bw)*(\..*$)", src)
            if m is not None:
                pieces = m.groups()
                width = node.getAttribute("width")
                height = node.getAttribute("height")
                if pieces[2] != width and pieces[3] != height:
                    self.__write(
                            "Warning: Dimensions do not match in node %s and filename %s\n" % \
                            ((width, height), (pieces[2], pieces[3])))
                # get image data
                orgImgName = pieces[1]+pieces[5]
                imgData = self.convertedData.getImage(orgImgName)
                img = self.iceContext.IceImage(imgData)
                # get newSize from src
                newSize = (int(width), int(height))
                if pieces[4]=="bw":
                    #fix all mathtype
                    #('math_files', 'm5e0afe47', '137', '45', 'bw', '.gif')
                    newSrc = pieces[0] + "/" + pieces[1] + "_" + pieces[2] + "x" + pieces[3] + "bw" + pieces[5]
                    node.setAttribute("src", newSrc)
                    newImgName = pieces[0] + "/" + pieces[1] + pieces[5]
                elif img.needsResizing(newSize) and not img.isAnim():
                    # ok it will need resizing any way
                    # change to jpeg
                    try:
                        newImgName = self.__convertImageToJpg(img, pieces, newSize)
                        node.setAttribute("src", newImgName)
                    except Exception, e:
                        #print "Error reading orginal image file!"
                        newImgName = pieces[0] + "/" + pieces[1] + pieces[5]
                        self.__write("Error in BaseConverter.__processImageNode() convertImage src='%s' ErrorMessage='%s'\n" % (src, str(e)))
                        #raise e
                else:
                    # ok change the size back to the original size (if not already)
                    imgSize = img.getSize()
                    if not img.isAnim(): #only change for non-animated pics
                        node.setAttribute("width", str(imgSize[0]))
                        node.setAttribute("height", str(imgSize[1]))
                    #new src value with no _###x###
                    newImgName = pieces[0] + "/" + pieces[1] + pieces[5]
                    node.setAttribute("src", newImgName)
            else:
                self.__write("Warning: image was skipped because src='%s' has an unexpected pattern\n" % src)
        except Exception, e:
            self.__write("Error in BaseConverter.__processImageNode() src='%s' ErrorMessage='%s'\n" % (src, str(e)))
        return newImgName


    def __convertImageToJpg(self, img, pieces, newSize):
        if img.hasTransparency():
            img.removeTransparency()
        newImgName = "%ss%sx%s.jpg" % (pieces[1], newSize[0], newSize[1])
        img.resizeImage2(newSize)
        filename = self.convertedData.abspath(newImgName)
        img.save(filename)
        self.convertedData.addImageFile(newImgName, filename)
        return pieces[0] + "/" + newImgName
    
    
    def __write(self, str):
        if self.__output is not None:
            self.__output.write(str)





