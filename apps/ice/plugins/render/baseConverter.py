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


from http_util import Http



class BaseConverter:
    # Constructor
    #    __init__(iceContext, getRelativeLinkMethod, oooConverterMethod)
    # Properties:
    #    
    # Methods:
    #    renderMethod(file, absFile, oooConverterMethod=None) -> convertedData object
    #    renderPdfOnlyMethod(file, absFile, oooConverterMethod=None) -> convertedData object
    #    
    # Private Methods:
    #    _setup(copyToMethod, sourceFileName, absSourceFile=None, convertToOdt=False)
    #    _close()
    #    _convertToHtml()
    #        _convertFile(self._tmpOooFileName, self._tmpHtmlFileName)
    #        __processHtmlContentXml(self._contentXml, self.__stylesXml)
    #            Transforming contentXml using python or xslt  NOTE: newXml = xhtml
    #            __processEmbeddedLinks(xml)
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
        #self._tmpDir = None
        self._tmpDocFileName = None
        self._tmpOooFileName = None
        self._tmpHtmlFileName = None
        self._tmpPdfFileName = None
        self._contentXml = None
        self.__baseUrl = None        # doc
        self.__packageUrl = None     # doc
        self.convertToOdt = False
        self.__output = iceContext.output
        
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
        self.convertedData = convertedData
        convertedData = self._render(file, True, **kwargs)
        if convertedData.errorMessage.startswith("Failed to connect to OpenOffice"):
            self.__startOpenOfficePipe()
            print "OK trying again"
            convertedData.clearError()
            self.convertedData = convertedData
            convertedData = self._render(file, True, **kwargs)
            if convertedData.errorMessage.startswith("Failed to connect to OpenOffice"):
                self.__startOpenOffice = False
        return convertedData
    
    
    def renderPdfOnlyMethod(self, file, convertedData, reindex=False, **kwargs):
        self.convertedData = convertedData
        return self._render(file, False, reindex=reindex, **kwargs)
    
    
    def _render(self, file, includeHtml=True, reindex=False, **kwargs):
        rep = self.iceContext.rep
        if rep is not None:
            absFile = rep.getAbsPath(file)
        else:
            absFile = file
        self.__relDocPath, _, _ = self._fs.splitPathFileExt(file)
        try:
            if rep is None or not hasattr(rep, "getProperty"):
                #self.iceContext.printCallers(6)
                def copy(src, dest):
                    src = absFile
                    self.__fs.copy(src, dest)
                    pass
                if rep is not None: #when there is no attribute getProperty but has rep
                    item = rep.getItem(file)
                    self.__convertLinksToEndNotes = False
                    if bool(item.getMeta("_convertLinksToEndNote")):
                        self.__convertLinksToEndNotes = True
                setup=self._setup(copy, file, absFile, convertToOdt=self.convertToOdt)
            else:
                item = rep.getItem(file)
                self.__convertLinksToEndNotes = False
                if bool(item.getMeta("_convertLinksToEndNote")):
                    self.__convertLinksToEndNotes = True
                setup=self._setup(rep.copyx, file, absFile, convertToOdt=self.convertToOdt)
                if setup == True:
                    # Hack for Word files
                    basePackageUrl = item.getMeta("_basePackageUrl")
                    if basePackageUrl is not None:
                        self.__baseUrl, self.__packageUrl = basePackageUrl
                        self.__packageUrl = self.__packageUrl.rstrip("/")
        except Exception, e:
            self._close()
            self.convertedData.addErrorMessage(str(e))
            self.convertedData.terminalError = True
            self.convertedData.Exception = e
            cData = self.convertedData
            self.convertedData = None
            return cData

        if setup==True:
            self._renderMethod(file, absFile, includeHtml, reindex=reindex, **kwargs)
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
    def _renderMethod(self, file, absFile, includeHtml=True, reindex=False, **kwargs):
        #raise Exception("This method must be overriden!")
        #converter = self._oooConverterMethod
    
        useLocalOpenOffice = self.iceContext.settings.get("useLocalOpenOffice")
        if useLocalOpenOffice == False:
            self.__convertUrl = self.iceContext.settings.get("convertUrl")
            print "Using ICE-service at: ", self.__convertUrl
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
            #if using local OpenOffice:
            oooConverterMethod = None 
            if includeHtml:
                # HTML
                try:
                    result = self._convertToHtml()
                except Exception, e:
                    msg = str(e)
                    if msg.find("cannot find OpenOffice.org")!=1:
                        self.convertedData.addErrorMessage(msg)
                    else:
                        self.convertedData.addErrorMessage("Error in _convertToHtml() - %s" % msg)
                    return
            if True:
                # PDF
                try:
                    result = self._convertToPdf(reindex=reindex, **kwargs)
                    if result!="ok":
                        self.convertedData.addErrorMessage(result)
                except Exception, e:
                    msg = str(e)
                    if msg.find("cannot find OpenOffice.org")!=1:
                        self.convertedData.addErrorMessage(msg)
                    else:
                        self.convertedData.addErrorMessage("Error in _convertToPdf() - %s" % msg)
    
    
    def _setup(self, copyToMethod, sourceFileName, absSourceFile=None, convertToOdt=False):
        self._sourceFileName = sourceFileName
        self._tmpOooFileName = self.convertedData.abspath("temp.odt")
        sourceExt = self.__fs.splitExt(sourceFileName)[1]
        self._tmpDocFileName = self.convertedData.abspath("temp" + sourceExt)
        self._tmpHtmlFileName = self.convertedData.abspath("temp.html")
        self._tmpPdfFileName = self.convertedData.abspath("temp.pdf")
        #self._tmpDir = self.convertedData.abspath("tmpDir")

        if convertToOdt:
            # Convert to odt first
            copyToMethod(sourceFileName, self._tmpDocFileName)
            result = self._convertToOdt(self._tmpDocFileName, self._tmpOooFileName)
            if result == "Word document is Invalid":
                self.__startOpenOfficePipe()
                print "OK trying again"
                result = self._convertToOdt(self._tmpDocFileName, self._tmpOooFileName)
                if result == "Word document is Invalid":
                    #changed the error message as it is too confusing.
                    result = "Cannot find Open Office. Aborting the rendition..."
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
                return False
            self.__stylesXml = self.__fs.readFromZipFile(self._tmpOooFileName, "styles.xml")

            if True:
                # HACK: add text:outline-style element (from styles.xml) to the content.xml
                stylesXml = self.iceContext.Xml(self.__stylesXml, self.OOoNS)
                node = stylesXml.getNode("//text:outline-style")
                outlineStyleStr = str(node)
                if outlineStyleStr == "None":
                    pass
                    #raise Exception ("Open Office document is Invalid")
                    #return False
                else:
                    listStylesStr = ""
                    if False:
                        try:
                            nodes = self._contentXml.getNodes("/office:document-content/office:body//*/@text:style-name")
                            #for n in nodes:
                            #    print n.content
                            styleNames = set([n.content for n in nodes])
                            predicate = " or ".join([("@style:name='%s'" % sn) for sn in styleNames])
                            xpath = "/office:document-styles/office:styles/text:list-style[%s]" % predicate
                            nodes = stylesXml.getNodes(xpath)
                            listStylesStr = "\n".join([str(n) for n in nodes])
                            #print listStylesStr
                            #print "#### ===="
                        except Exception, e:
                            print "##### e=%s" % str(e)
                    try:
                        outlineStyleStr = outlineStyleStr.replace("<text:outline-style>", 
                            "<text:outline-style " + \
                            "xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' " + \
                            "xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0'>")
                        # ---- Hack needed for windows only ---- namespace must be declared before use
                        #newElem = self._contentXml.xmlStringToElement(outlineStyleStr)
                        rootElem = "<root " + \
                            "xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' " + \
                            "xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0'>"
                        outlineStyleStr = rootElem + outlineStyleStr + "</root>"
                        newElem = self._contentXml.xmlStringToElement(outlineStyleStr)
                        newElem = newElem.getNode("*")
                        # ---- 
                        asNode = self._contentXml.getNode("/office:document-content/office:automatic-styles")
                        tosNode = asNode.getNode("*[name()='text:outline-style']")
                        if tosNode is None:
                            asNode.addChild(newElem)
                        else:
                            # Note: this should not be needed
                            self._contentXml.getRootNode().addChild(newElem)
                        if listStylesStr!="":
                            xs = rootElem + listStylesStr + "</root>"
                            newElem = self._contentXml.xmlStringToElement(xs)
                            for n in newElem.getNodes("*"):
                                asNode.addChild(n)
                            #print asNode
                        #print str(self._contentXml.getRootNode())
                    except Exception, e:
                        self.__write("Styles.xml Error - %s\n" % str(e))
                stylesXml.close()
            title = self._getTitle()
            self.convertedData.addMeta("title", title)
            return True
        except Exception, e:
            return False	
    
    
    def _close(self):
        if self._contentXml!=None:
            self._contentXml.close()
            self._contentXml = None
    
    def _fixTablesInDocxFiles(self,docxContentXml,odtContentXml):
        ### ooo does not support the table border and the merge cell. 
        ### this function hack the document to support merge cell and table border. 
        if docxContentXml is None or odtContentXml is None:
            return
        try:
            #get data from docx file
            body = docxContentXml.getNode("//w:body")
            docTableBorders = []
            MergedCells = {}
            tables = docxContentXml.getNodes("//w:tbl")
            tableCount = 0
            for table in tables:
                tableCount = tableCount + 1
                #tableXml = self.iceContext.Xml(str(table), self.docNS.items())
                tblBorders = table.getNodes("//*[local-name()='tblBorders']/*")
                docTableBorder = {}
                if tblBorders != []:
                    for tblBorder in tblBorders:
                        try:
                            name = tblBorder.getName()
                            if name != "insideH" and name !="insideV":
                                name = "border-%s" % name
                                if tblBorder.getAttribute("sz")!= "":
                                    size =  (float(tblBorder.getAttribute("sz"))/8)/ 28.35
                                    color = tblBorder.getAttribute("color")
                                    if color == "auto":
                                        color = "000000"
                                    if size != 0.0:
                                        docTableBorder[name]= "%.3fcm solid #%s" % (size,color)
                        except Exception,e:
                            print "Error in getting tblborder - %s " % str(e)
                else:
                    tblBorders = table.getNodes("//*/*[tc/tcPr/tcBorders]")
                    if tblBorders != []:
                        for tblBorder in tblBorders:
                            tcBorders = tblBorder.getChildren()
                            for tcBorder in tcBorders:
                                try:
                                    name = tcBorder.getName()
                                    if name != "insideH" and name !="insideV":
                                        name = "border-%s" % name
                                        if tcBorder.getAttribute("sz")!= "":
                                            size =  (float(tcBorder.getAttribute("sz"))/8)/ 28.35
                                            color = tblBorder.getAttribute("color")
                                            if color == "auto":
                                                color = "000000"
                                            if size != 0.0:
                                                docTableBorder[name]= "%.3fcm solid #%s" % (size,color)
                                except Exception,e:
                                    print "Error in getting tcBorder - %s " % str(e)
                docTableBorders.append(docTableBorder)
            #add the table border
            nodes = odtContentXml.getNodes("//style:table-cell-properties")
            for node in nodes:
                parentNode = node.getParent()
                parentName = parentNode.getAttribute("name")
                i = int(parentName.split(".")[0][-1])
                border = {}
                if (i-1) < len(docTableBorders):
                    border = docTableBorders[i-1]
                if border != {}:
                    value = ""
                    keys = ["border-top", "border-bottom","border-left", "border-right"]
                    for key in keys:
                        if border.has_key(key):
                            value = border[key]
                        else:
                            value = "0.035cm solid #000000"
                        node.setAttribute(key, value)
                    if node.getAttribute("border") == "none":
                        #in case there is border attribute
                        node.setAttribute("border", value)
                odtContentXml.saveFile()
            self.__fixMergeCellInDocxFile(odtContentXml)
        except Exception, e:
            print "Error in _fixTablesInDocxFiles - '%s'" % str(e)
    
    def __fixMergeCellInDocxFile(self,odtContentXml):
        nodes = odtContentXml.getNodes("//table:table-cell[@table:number-columns-spanned='65535']")
        if nodes != []:
            styleNames = []
            for node in nodes:
                parentNode = node.getParent()
                children = parentNode.getChildren()
                for child in children:
                    child.setAttribute("number-columns-spanned","1")
                grandParentNode = parentNode.getParent()
                while True:                
                    if grandParentNode.getName() == "table":
                        break;
                    grandParentNode = grandParentNode.getParent()
                styleName = grandParentNode.getAttribute("name")
                if not(styleName in styleNames):
                    styleNames.append(styleName)
            print styleNames
            for styleName in styleNames:
                maxColumns = len(odtContentXml.getNodes("//table:table[@table:name = '%s']/table:table-column"% styleName))
                #remove the column width
                for i in range(1, maxColumns+1):
                    colStyleName = "%s.%s" % (styleName,chr(64+i))
                    styleNode = odtContentXml.getNode("//style:style[@style:name='%s']/style:table-column-properties" % colStyleName)
                    print styleNode
                    styleNode.removeAttribute("column-width")
                
                def fixCells(query):
                    nodes = odtContentXml.getNodes(query)
                    for node in nodes:
                        if len(node.getChildren())<maxColumns:
                            colspan = maxColumns - len(node.getChildren()) + 1
                            children = node.getChildren()
                            try:
                                child = children.getLastChild()
                            except:
                                child = children[-1]
                            child.setAttribute("table:number-columns-spanned",str(colspan))
                #for those rows under table-header elements
                fixCells("//table:table[@table:name='%s']/*/table:table-row" % styleName)
                #for normal row
                fixCells("//table:table[@table:name='%s']/table:table-row" % styleName)
        odtContentXml.saveFile()
        
    def __fixExtraImagesInDocxFile(self,docxContentXml ,odtContentXml):
        #find the first element in docx
        body = docxContentXml.getNode("//w:body")
        firstChild = body.getFirstChild()
        firstChildName = firstChild.getName()
        if firstChildName == "tbl":
            firstChildName = "table"
        if firstChild.getLastChild() and firstChild.getLastChild().getName() != "r":
            secondChildName = firstChild.getNextSibling().getName()
            firstChildHasContent = False
        #fixing the extra images.   
        body = odtContentXml.getNode("//office:text")
        firstChild = body.getFirstChild().getNextSibling() # to skip the first child is text:sequence-decls
        def checkFirstChild(firstChild):
            if firstChild.getName() !=  firstChildName:
                firstChild.remove()
                firstChild = body.getFirstChild().getNextSibling()
                checkFirstChild(firstChild)
        if firstChild is not None:
            checkFirstChild(firstChild)
        odtContentXml.saveFile()
        
    def _fixMathTypeInDocxFiles(self,docxContentXml ,odtContentXml):
        #to fix mathtype being squshed when open in open office
        shapes = docxContentXml.getNodes("//v:shape")
        if shapes != []:
             dimensions=[]
             for shape in shapes:
                 style = shape.getAttribute("style")
                 styleProps=style.split(";")
                 propDict = {}
                 for prop in styleProps:
                     if prop.find("width")!=-1 or prop.find("height")!=-1:
                         
                         propSplits = prop.split(":")
                         if propSplits[1].find("pt")!=-1:
                             #convert to cm
                             value = float(propSplits[1].replace("pt","")) * 0.0352777778
                             propDict[propSplits[0]]= "%3.3fcm" %value
                 dimensions.append(propDict)             
        drawFrames = odtContentXml.getNodes("//draw:frame[draw:object-ole]")
        count = 1
        for drawFrame in drawFrames:
            drawFrame.setAttribute("draw:name",str(count))
            drawFrame.setAttribute("width",dimensions[count-1]["width"])
            drawFrame.setAttribute("height",dimensions[count-1]["height"])
            count = count + 1
        odtContentXml.saveFile()
    
    def __fixupDocx(self):
        #read docx file
        docxContentStr = self.__fs.readFromZipFile(self._tmpDocFileName,"word/document.xml")
        docxContentXml = self.iceContext.Xml(docxContentStr, self.docNS.items())
        
        # read odt file
        tmpDir = self.__fs.unzipToTempDirectory(self._tmpOooFileName)
        contentPath = self.__fs.join(str(tmpDir), "content.xml")
        odtContentXml = self.iceContext.Xml(contentPath, self.OOoNS)
        
        if docxContentXml is not None and odtContentXml is not None:
            self. __fixExtraImagesInDocxFile(docxContentXml ,odtContentXml)
            self._fixTablesInDocxFiles(docxContentXml,odtContentXml)
            self._fixMathTypeInDocxFiles(docxContentXml,odtContentXml)
            odtContentXml.saveFile()
        docxContentXml.close()
        odtContentXml.close()
        tmpDir.zip(self._tmpOooFileName)
        tmpDir.delete()

    def convertDocToOdt(self, docFile, otdFile):
        return self._convertToOdt(docFile, otdFile)
    def _convertToOdt(self, docFile, odtFile):
        # Note: used for WORD (.doc) files only
        result, msg = self._convertFile(docFile, odtFile)
        if result==False:
            result = "Word document is Invalid" 
            return result
        _,docExt = self.__fs.splitExt(docFile)
        if docExt == ".docx":
            self.__fixupDocx()
            #return result
        
        if True:        # Do Word HACKS
            tmpDir = self.__fs.unzipToTempDirectory(odtFile)
            contentPath = self.__fs.join(str(tmpDir), "content.xml")
            content = self.iceContext.Xml(contentPath, self.OOoNS)
            
            #Check if there're any content 
            xpath = "//office:document-content/office:body/office:text/*[not(name()='office:forms')]" + \
                        "[not(name()='text:sequence-decls')]"
            nodes = content.getNodes(xpath)
            
            #Check if there are content in the document
            hasContent = False
            for node in nodes:
            	if node.getContent() != "" or len(node.getChildren()) > 0:
            		hasContent = True
            if hasContent == False:
                pass
                #commented to fix the ICE fail to render Empty word Document
                #if you find the bug please uncomment the following.
                #result = "Word document is Invalid"                      
            else:
                # HACK: Fixup tables so that rows expand across pages
                nodes = content.getNodes("//style:table-row-properties/@style:keep-together[.='false']")
                l = len(nodes)
                if nodes != []:
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
                    title = content.getContent("//office:body/office:text/text:p[%s]" % test)
                    if title is None:
                        title = content.getContent("//office:body/office:text/text:h[%s]" % test)
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
            tmpDir.zip(odtFile)
            tmpDir.delete()
        return result


    def _convertToHtml(self):
        #Before convert to Html, extract "//draw:frame[./draw:text-box]"
        #Replace text:anchor-type of as-char to paragraph
        startTime = time.time()
        htmlOooFile= self.convertedData.abspath("tempForHtml.odt")
        self.__fs.copy(self._tmpOooFileName, htmlOooFile)
        
        hasFrame=False
        
        
        
        try:
            tempFs = self.__fs.unzipToTempDirectory(htmlOooFile)
            
            #content.xml 
            xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), self.OOoNS)
            
            forceIceStyles = self.iceContext.settings.get("forceIceStyles", False)
            if forceIceStyles:
                plugin = self.iceContext.getPlugin("ice.ooo.cleanUpStyles")
                if plugin is None:
                    raise Exception("ice.ooo.cleanUpStyles plugin not found!")
                cleanUpStyles = plugin.pluginClass
                cleanUpStyles = cleanUpStyles(self.iceContext)
                #todo check which doc we want to fix the styles 
                isIceDoc = False
                nodes= xml.getNodes("//*[@text:style-name!= '']")
                if nodes!= []:
                    for node in nodes:
                        styleName = node.getAttribute("style-name")
                        if cleanUpStyles.isIceStyle(styleName):
                            isIceDoc = True
                            break
                #print "isIceDoc:", isIceDoc
                if not isIceDoc:
                    #check the base style just in case they are:
                    nodes = xml.getNodes("//style:style[@style:parent-style-name!='']")
                    if nodes != []:
                        for node in nodes:
                            styleName = node.getAttribute("parent-style-name")
                            if cleanUpStyles.isIceStyle(styleName):
                                isIceDoc = True
                                break
                #print "isIceDoc:", isIceDoc
                if not isIceDoc:
                    styleXml = self.iceContext.Xml(tempFs.absolutePath("styles.xml"), self.OOoNS)
                    xml,styleXml = cleanUpStyles.forceIceStyles(xml,styleXml)
                    xml.saveFile()
                    styleXml.saveFile()
                    self._contentXml = xml
                    styleXml.close()

            nodes = xml.getNodes("//draw:frame/draw:text-box")
            
            if nodes != []:
                hasFrame=True
                for node in nodes:
                    parentNode = node.getNode("./..")
                    if parentNode.getAttribute("anchor-type") != "paragraph":
                        parentNode.setAttribute("anchor-type", "paragraph")
                        
            xml.saveFile()
            
            tempFs.zip(self.__fs.absolutePath(htmlOooFile))
            
            #print "Time used to hack the draw:frame  %s" % (time.time() - startTime)        
            self.__time()
            
            if hasFrame:
                result, msg = self._convertFile(htmlOooFile, self._tmpHtmlFileName)
            else:
                result, msg = self._convertFile(self._tmpOooFileName, self._tmpHtmlFileName)
            
            if result==False:
                return msg
            
            try:
                if hasattr(self, "pluginProcessContentXml"):
                    if hasFrame:
                        dom = self.pluginProcessContentXml(xml, self._sourceFileName)
                    else:
                        dom = self.pluginProcessContentXml(self._contentXml, self._sourceFileName)
                else:
                    if hasFrame:
                        dom = self.__processHtmlContentXml(xml)
                    else:
                        ##
                        
                        dom = self.__processHtmlContentXml(self._contentXml)
            except Exception, e:
                print "---- Exception in baseConverter._convertToHtml() ----"
                print " Message='%s'" % str(e)
                print self.iceContext.formattedTraceback()
                print "-----------------------------"
                raise
        finally:
            tempFs.delete()
            
            xml.close()
            if self.__fs.isFile(htmlOooFile):
                self.__fs.delete(self.__fs.absolutePath(htmlOooFile))
        return "ok"
    
    
    def _convertToPdf(self, reindex=False, **kwargs):
        officeValue = ""
        separator = ""
        
        #hack to fix the relative path to local file in file system
        if kwargs.has_key('fixPdfLink'):
            if kwargs['fixPdfLink']:
                self.__fixRelativeLinkForPdf(self._tmpOooFileName)
        
        if self.__convertLinksToEndNotes:
            plugin = self.iceContext.getPlugin("ice.ooo.odtAddLinkEndnotes")
            if plugin is None:
                raise Exception("cannot find plugin 'ice.ooo.odtAddLinkEndnotes'!")
            addLinkEndnotes = plugin.pluginClass(self.iceContext)
            try:
                result = addLinkEndnotes.addEndnotes(self._tmpOooFileName)
            except Exception, e:
                tb = self.iceContext.formattedTraceback()
                print tb
                result = "Exception: %s" % str(e)
            if result!="ok":   # result = "Error Message"
                print "Failed in addEndnotes - error message='%s'" % result
        
        self.__removeLocalhostLinks(self._tmpOooFileName)
        
        
        #testing
        tempFs = self.__fs.unzipToTempDirectory(self._tmpOooFileName)
        
        #style.xml- fix up the internet link styles.
        styleXml = self.iceContext.Xml(tempFs.absolutePath("styles.xml"),
                        self.iceContext.OOoNS.items())
        nodes = styleXml.getNodes("//style:style[@style:name='Internet_20_link']/style:text-properties")
            
        if nodes != []:
            for node in nodes:
                if node.getAttribute("text-underline-style") != "none":
                    node.setAttribute("text-underline-style", "none")
        styleXml.saveFile()
        
        nodes = styleXml.getNodes("//style:style[@style:name='Visited_20_Internet_20_Link']/style:text-properties")
            
        if nodes != []:
            for node in nodes:
                if node.getAttribute("text-underline-style") != "none":
                    node.setAttribute("text-underline-style", "none")

        styleXml.saveFile()
        styleXml.close()
        
        
        #context.xml
        xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), 
                       self.iceContext.OOoNS.items())

        #Hack to fix localhost links are shown as link when they are not in .doc file
        anchorNodes = xml.getNodes("//*/*[@text:style-name='Internet_20_link']")
        for a in anchorNodes:
            parentNode = a.getNode("./..")
            if parentNode.getName() <> "a":
                a.setAttribute("style-name",parentNode.getAttribute("style-name"))
            
        #Hack to fix cross references when using TableCaption and FigureCaption autonumbering
        tableCaptions = xml.getNodes("//text:p[@text:style-name='p-table-caption']")
        if tableCaptions is not None and tableCaptions != []:
            fixed = False
            officeValue = ""
            for tableCaption in tableCaptions:
                hasBookMark = False
                bookMarkNo = ""
                count = 1
                needToFixNode = tableCaption.getNodes("./*/*[name()='text:chapter']")
                if needToFixNode != [] and needToFixNode is not None:
                    tableCaptionChild = tableCaption.getChildren()
                    if tableCaptionChild != [] and tableCaptionChild is not None:
                        for child in tableCaptionChild:
                            if child.getName() == "bookmark-start":
                                if hasBookMark:
                                    child.remove()
                                else:
                                    bookMarkNo = child.getAttribute("name")
                                    hasBookMark = True
                            
                            if child.getName() == "bookmark-end":
                                if child.getAttribute("name") != bookMarkNo:
                                    child.remove()
                                    
                            content = child.getContent().lower()    
                            if content.strip() == ".":
                                separator = content.strip()
                                child.remove()
                                continue
                            
                            children = child.getChildren()
                            if children is not None and children != []:
                                for varChild in children:
                                    if varChild.getName() == "chapter":
                                        officeValue = varChild.getAttribute("outline-level")
                                        chapterNumber = varChild.getContent()
                                        varChild.getParent().remove()
                                        
                                    if varChild.getName() == "variable-set":
                                        newNode = xml.createElement("text:sequence")
                                        tableNumber = varChild.getContent()
                                        newNode.setAttribute("text:ref-name", "refTable%s" % count)
                                        newNode.setAttribute("text:name", "Table")
                                        newNode.setAttribute("text:formula", "ooow:Table+1")
                                        content = "%s.%s" % (chapterNumber, tableNumber)
                                        if officeValue != "":
                                            newNode.setAttribute("style:num-format", officeValue)
                                        newNode.setContent(content)
                                        varChild.replace(newNode)
                fixed = True        
            if fixed:
                #Fix Table Properties
                seqNode = xml.getNode("//text:sequence-decl[@text:name='Table']")
                if seqNode is not None:
                    if seqNode.getAttribute("display-outline-level") is not None:
                        seqNode.removeAttribute("display-outline-level")
                    if seqNode.removeAttribute("separation-character") is not None:
                        seqNode.removeAttribute("separation-character")
                    seqNode.setAttribute("text:display-outline-level", officeValue)
                    seqNode.setAttribute("text:separation-character", separator)
                else:
                    seqdec = xml.getNode("//text:sequence-decls")
                    newNode = xml.createElement("text:sequence-decl")
                    newNode.setAttribute("text:display-outline-level", officeValue)
                    newNode.setAttribute("text:separation-character", separator)
                    newNode.setAttribute("text:name", "Tanbe")
                    seqdec.addChild(newNode)
        #hack to fix figure
        figureCaptions = xml.getNodes("//text:p[@text:style-name='p-figure-caption']")
        if figureCaptions is not None and figureCaptions != []:
            fixed = False
            for figureCaption in figureCaptions:
                hasBookMark = False
                bookMarkNo = ""
                count = 1
                needToFixNode = figureCaption.getNodes("./*/*[name()='text:chapter']")
                if needToFixNode != [] and needToFixNode is not None:
                    figureCaptionChild = figureCaption.getChildren()
                    if figureCaptionChild != [] and figureCaptionChild is not None:
                        for child in figureCaptionChild:
                            if child.getName() == "bookmark-start":
                                if hasBookMark:
                                    child.remove()
                                else:
                                    bookMarkNo = child.getAttribute("name")
                                    hasBookMark = True
                            
                            if child.getName() == "bookmark-end":
                                if child.getAttribute("name") != bookMarkNo:
                                    child.remove()
                                    
                            content = child.getContent().lower()    
                            if content.strip() == ".":
                                separator = content.strip()
                                child.remove()
                                continue
                            
                            children = child.getChildren()
                            if children is not None and children != []:
                                for varChild in children:
                                    if varChild.getName() == "chapter":
                                        officeValue = varChild.getAttribute("outline-level")
                                        chapterNumber = varChild.getContent()
                                        varChild.getParent().remove()
                                        
                                    if varChild.getName() == "variable-set":
                                        newNode = xml.createElement("text:sequence")
                                        figureNumber = varChild.getContent()
                                        newNode.setAttribute("text:ref-name", "refFigure%s" % count)
                                        newNode.setAttribute("text:name", "Figure")
                                        newNode.setAttribute("text:formula", "ooow:Figure+1")
                                        content = "%s.%s" % (chapterNumber, figureNumber)
                                        if officeValue != "":
                                            newNode.setAttribute("style:num-format", officeValue)
                                        newNode.setContent(content)
                                        varChild.replace(newNode)
                fixed = True        
            if fixed:
                #Fix Table Properties
                seqNode = xml.getNode("//text:sequence-decl[@text:name='Figure']")
                if seqNode is not None:
                    if seqNode.getAttribute("display-outline-level") is not None:
                        seqNode.removeAttribute("display-outline-level")
                    if seqNode.removeAttribute("separation-character") is not None:
                        seqNode.removeAttribute("separation-character")
                    seqNode.setAttribute("text:display-outline-level", officeValue)
                    seqNode.setAttribute("text:separation-character", separator)
                else:
                    seqdec = xml.getNode("//text:sequence-decls")
                    newNode = xml.createElement("text:sequence-decl")
                    newNode.setAttribute("text:display-outline-level", officeValue)
                    newNode.setAttribute("text:separation-character", separator)
                    newNode.setAttribute("text:name", "Figure")
                    seqdec.addChild(newNode)
        xml.saveFile()
        
        xml.close()
        tempFs.zip(self.__fs.absolutePath(self._tmpOooFileName))
        tempFs.delete()
        
        result, msg = self._convertFile(self._tmpOooFileName, \
                    self._tmpPdfFileName, reindex=reindex)
        if result==False:
            return msg
            
        self.convertedData.addRenditionFile(".pdf", self._tmpPdfFileName)
        
        return "ok"
    
    
    def __fixRelativeLinkForPdf(self, tmpOooFileName):
        tmpDir = self.__fs.split(tmpOooFileName)[0] + "/tmpDir"
        tmpContent = self.__fs.join(tmpDir, "content.xml")
        self.__fs.unzipToDirectory(tmpOooFileName, tmpDir)
        
        xml = self.iceContext.Xml(tmpContent, self.OOoNS)
        hrefNodes = xml.getNodes("//draw:a[starts-with(@xlink:href, './') or starts-with(@xlink:href, '../')]")
        for href in hrefNodes:
            drawLink = href.getAttribute("href")
            if drawLink and drawLink.startswith("../"):
                drawLink = "../%s" % drawLink
                href.removeAttribute("href")
            href.setAttribute("xlink:href", drawLink)
            for child in href.getChildren():
                if child.getName() == "frame" and child.getAttribute("name") != "" and child.getAttribute is not None:
                    child.removeAttribute("name")
                    child.setAttribute("draw:name", drawLink)
        xml.saveFile(tmpContent)
        xml.close()
        
        self.__fs.zip(tmpOooFileName, tmpDir)
    
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
    
    
    #def testForLinkedImages(self, file=None):
    #    contentXml = None
    #    if file is not None:
    #        content = zip_util.extractFile(file, "content.xml")
    #        contentXml = self.iceContext.Xml(content, self.OOoNS)
    #        num = self.__testForLinkedImages(contentXml)
    #        contentXml.close()
    #        return num
    #    else:
    #        return self.__testForLinkedImages(contentXml)
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
            msg = str(e)
            if msg.find("cannot find OpenOffice.org"):
                pass
            else:
                self.__write("#### Error in oooConverterMethod: %s\n" % msg)
            raise e
        return result, msg


    def __removeLocalhostLinks(self, tmpOooFileName):
        tmpDir = self.__fs.split(tmpOooFileName)[0] + "/tmpDir"
        tmpContent = self.__fs.join(tmpDir, "content.xml")
        self.__fs.unzipToDirectory(tmpOooFileName, tmpDir)
        
        xml = self.iceContext.Xml(tmpContent, self.OOoNS)
        nodes = xml.getNodes("//text:a[starts-with(@xlink:href, 'http://localhost')]")
        for node in nodes:
            children = node.getChildren()
            node.replace(children)
            node.delete()
        xml.saveFile(tmpContent)
        xml.close()
        
        self.__fs.zip(tmpOooFileName, tmpDir)
        
    
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

    
    def __processHtmlContentXml(self, contentXml, stylesXml=None):
        if contentXml is None:
            return
        
        if stylesXml is None:
            stylesXml = self.__stylesXml

        st = time.time()
        o = self.__ooo2xhtml(self.iceContext)
        o.process(str(contentXml), str(stylesXml))
        meta = o.meta
        self.convertedData.meta = meta
        xmlStr = o.serialize()
        et = time.time() - st
        self.__write(" done transforming content using python in %s mS\n" % int(et * 1000))

        xmlStr = re.sub('<html xmlns\=\"[^\"]*\"', "<html", xmlStr)
        xhtml = self.iceContext.Xml(xmlStr[xmlStr.find("<html"):])
        
        # check for any special charecters
        self.__processSpecialCharacters(xhtml)
        self.__processEmbeddedLinks(xhtml)
        images = self.__processImages(xhtml)
        
        if True:   # Turn OLE images into Black&White(GrayScale) images
            names = self.__getOLEImageNames(contentXml)
            #print "OLE Image names=", names
            bwResizedImages = self.__bwResizeTheseImages(xhtml, names)
            for img in bwResizedImages.keys():
                if img in images:
                    images.remove(img)
            images.extend(bwResizedImages.values())
        
        # setMeta "images" and addImages
        self.convertedData.addMeta("images", images)
        
        self.__processContent(xhtml, self._sourceFileName)
        xhtml.close()
    
    
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
            #print "-----"
            #print xhtml.getRootNode().serialize(format=False)
            #print "-----"
        except Exception, e:
            self.__write("Error: %s\n" % str(e))
                    
            
    
    # MathType images
    def __getOLEImageNames(self, contentXml):
        names = []
        xpath = "//office:document-content/office:body/office:text//draw:frame[draw:object-ole]"
        nodes= contentXml.getNodes(xpath)
        for node in nodes:
            name = node.getAttribute("name")
            names.append(name)
        return names
    def __bwResizeTheseImages(self, htmlXml, names):
        # Use the Black&White resizing logic on these images
        bwResizedImages = dict()
        nodes = htmlXml.getNodes("//img")
        for node in nodes:
            alt = node.getAttribute("alt")
            if alt in names:
                src = node.getAttribute("src")
                #print "src before = ", src
                #src = re.sub("(_\d+x\d+)\.", ".", src)
                #src = re.sub("\.", "bw.", src)
                #print "src after = ", src
                #name, ext = os.path.splitext(src)
                name, ext = self._fs.splitExt(src)
                #name2 = os.path.split(name)[1]
                name2 = self._fs.split(name)[1]
                bwResizedImages[name2 + ext] = name2 + "bw" + ext
                src2 = name + "bw" + ext
                node.setAttribute("src", src2)
        return bwResizedImages
    
    
    def __processImages(self, xhtml):
        # dictionary of images, name:filename eg Graphic1:graphic.png
        imageNames = {}
        try:
            imageNames = self.__findAllImageNames(self._tmpHtmlFileName)
            # convert image names to proper html ones
        except Exception, e:
            msg = "ERROR in findAllImageNames(): - " + str(e)
            raise Exception(msg)
        
        try:
            images = self.__convertImageNames(xhtml, self._sourceFileName, imageNames)
            return images
        except Exception, e:
            msg = "ERROR in convertImageNames(): - " + str(e)
            raise Exception(msg)
    
    
    def __findAllImageNames(self, htmlFilename):
        """Given a html file, search for img tags and load name, src into a dictionary"""
        # first reset the image names for processing a new document?
        imageNames = {}
        xml = None
        try:
            # remove SDFIELD tags
            f = open(htmlFilename, "rb")
            html = f.read()
            f.close()
            html = re.sub("</?SDFIELD.*?>", "", html)            
            xml = self.iceContext.Xml(html, parseAsHtml=True)
        except Exception, e:
            self.__write("could not parse html file %s\n" % htmlFilename)
            self.__write(" ... %s\n" % str(e))
            return
        
        count = 0
        imgNodes = xml.getNodes("//img")
        for img in imgNodes:
            #print "########   %s" % str(img)
            src = img.getAttribute("src")
            name = img.getAttribute("name")
            if name is None:
                count += 1
                name = "noname%s" % count
            imageNames[name] = src
        xml.close()
        return imageNames


    def __convertImageNames(self, xml, sourceFilename, imageNames):
        """Convert image names from OOo format (eg src="#Pictures/100000000000002D0000002D7AE625C4")
        to HTML format (eg src="Module1_html_7ae625c4.png")
        Also copy the image file into the repository"""
        # TODO keep a list of images which have already been copied and don't copy them again
        if imageNames is None:
            imageNames = {}
        copiedImages = dict()
        linkedImages = dict()
        #print "Processing images names"
        #imageNodes = xml.getNodes("//*[local-name()='img']")
        imageNodes = xml.getNodes("//img")
        # Hack - part 1of2 - For when OOo does not assign an alt attribute to an image
        imageNodes.reverse()
        noNameCount = -1
        for kn in [int(k[len("noname"):]) for k in imageNames.keys() if k.startswith("noname")]:
            if kn>noNameCount:
                noNameCount = kn
        # end hack
        for img in imageNodes:
            # find image by name in dictionary and substitute the src filename
            href = img.getAttribute("src")
            name = img.getAttribute("alt")
            height = None
            width = None
            if img.getAttribute("width")!=None and img.getAttribute("height")!=None:
                width = img.getAttribute("width")
                height = img.getAttribute("height")
            # Hack - part 2of2 - 
            #if not imageNames.has_key(name) and imageNames.has_key(None):
            #    imageNames[name] = imageNames[None]
            if not imageNames.has_key(name):
                if imageNames.has_key("noname%s" % noNameCount):
                    name = "noname%s" % noNameCount
                    noNameCount -= 1
                elif not imageNames.has_key(name) and imageNames.has_key(None):
                    imageNames[name] = imageNames[None]
            # end hack
            if imageNames.has_key(name): 
                src = imageNames[name]
                simpleName = self.__getSimpleImageFileName(src)
                if not copiedImages.has_key(src):
                    copiedImages[src] = simpleName
                    data = None
                    self.convertedData.addImageFile(simpleName, filename=src)
                if height!=None:
                    #nameOnly, ext = os.path.splitxt(simpleName)
                    nameOnly, ext = self.__fs.splitExt(simpleName)
                    simpleName = nameOnly + "_" + width + "x" + height + ext
                linkedImages[simpleName] = simpleName
                simpleName = self.__getRelativeImageLink(simpleName, sourceFilename)
                img.setAttribute("src", simpleName)
                if img.getAttribute("longdesc") is not None:
                    newAlt = img.getAttribute("longdesc")
                    img.setAttribute("alt", newAlt)
                    img.removeAttribute("longdesc")
                elif (name.find("localhost")>-1 or name.find("LOCALHOST")>-1):
                    name = self.__fs.splitPathFileExt(name)[1] + self.__fs.splitPathFileExt(name)[2]
                    img.setAttribute("alt", name)
            else:
                #print " ??? %s" % imageNames
                pass
        #print "linkedImages = ", linkedImages.values()
        #self.convertedData.addMeta("images", linkedImages.values())
        return linkedImages.values()


    def __processContent(self, xml, sourceFilename):
        # fixup links to be relative links
        links = self.__fixupRelativeLinks(xml, sourceFilename)
        
        self.__fixupImageReferences(xml)
        self.__convertATagToRdfa(xml)
        
        self.convertedData.addRenditionData(".ALL.txt", str(xml))

        #elems = xml.getNodes("//*[local-name()='style']")
        elems = xml.getNodes("//style")
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
        body = xml.getNode("//body")
        elems = body.getNodes("*")
        
        rendition = "<div>"
        for elem in elems:
            rendition += str(elem)
        rendition += "</div>"
        self.convertedData.addRenditionData(".xhtml.body", rendition)
        
        self.convertedData.addMeta("links", links)
        
    
    def __fixupRelativeLinks(self, xml, sourceFilename):
        try:
            #links = dict()
            links = []
            refNodes = xml.getNodes("//*[@href]")
            for ref in refNodes:
                # this call will return url with entities resolved eg &amp;
                replaceStr = ref.getAttribute("href")
                url = self.__getRelativeLink(sourceFilename, replaceStr)
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
                #links[url] = linkText
             
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
            local = self.iceContext.isLocalUrl(url)
            if local:
                url = self.__getRelativeLinkMethod(sourceFilename, url)
        return url
    
    
    def __getRelativeImageLink(self, imgSrc, sourceFilename):
        """get a reference to the img src, relative to the source filename"""
        fileName = self.__fs.split(sourceFilename)[1]
        baseName = self.__fs.splitExt(fileName)[0]
        if fileName.endswith(".book.odt"):
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
    
    
    def __time(self):
        now = time.time()
        t = 0
        if self.__lastTime!=None:
            t = now - self.__lastTime
        self.__lastTime = now
        return round(t, 3)
    
    
    # for testing only
    def _processEmbeddedLinks(self, xml):
        return self.__processEmbeddedLinks(xml)
    
    
    def __processEmbeddedLinks(self, xml):
        # look for <a href='/xxxx/x.xxx?embed&xxx' >
        #links = xml.getNodes("//*[local-name()='a'][@href]")
        firstLightbox = True
        links = xml.getNodes("//a[@href]")
        for link in links:
            s = link.getAttribute("href")
            protocol, loc, path, param, query, fid = urlparse.urlparse(s)
            href = protocol + "://" + loc + path
            querylist = query.split("&")
            querysplit = [i.split("=")[0].lower() for i in querylist]
            if "embed" in querysplit:
                try:
                    newNode = self.__getObjectNode(querylist, link.getContent(), \
                                href, xml)
                    link.replace(newNode)
                    link.delete()
                except Exception, e:
                    self.__write("ERROR: %s\n" % str(e))
            elif "lightbox" in querysplit:
                content = self.__getObjectNode(querylist, link.getContent(), href, xml)
                try:
                    Lightbox = self.iceContext.getPluginClass("ice.extra.lightbox")
                    lightbox = Lightbox(self.iceContext)
                    if firstLightbox:
                        firstLightbox = False
                        lightbox.addScript(xml)
                    linkNode, externalFiles = lightbox.processLink(xml, link, content)
                    self.convertedData.addMeta("externalFiles", externalFiles)
                except Exception, e:
                    print self.iceContext.formattedTraceback()
                    self.__write("ERROR: %s\n" % str(e))
         
    def __getObjectNode(self, querylist, linkContent, href, xml):
        createElement = xml.createElement
        createComment = xml.createComment
        # self.iceContext.MimeTypes (dictionary)
        
        #default values
        ext = self.__fs.splitExt(href)[1].lower()
        type = self.iceContext.MimeTypes.get(ext, "")
        if type=="text/html":
            return self.__getHtmlDivNode(querylist, linkContent, href, xml)
        
        classId = ""
        codeBase = ""
        data = href
        if type.startswith("audio"):
            width = "240"
            height = "48"
        else:
            width = "320"
            height = "240"
        base = "."
        
        # Do we have a (classId, codeBase, type) information for this media type
        if self.__objectsClassIdCodeBase.has_key(ext):
            classId, codeBase, type = self.__objectsClassIdCodeBase[ext]
        
        fixParamForSwf = ['embed', 'width', 'height', 'wmode', 'autoStart', 'autostart', 'movie', 'url', 'base']
        userDefinedParam = dict()

        queryDict = dict()
        for item in querylist:
            parts = item.split("=")
            parts.append(None)
            queryDict[parts[0]] = parts[1]
            if parts[0] not in fixParamForSwf:
                userDefinedParam[parts[0]] = parts[1]
            
        width = queryDict.get("width", width)
        height = queryDict.get("height", height)
        wmode = queryDict.get("wmode", "")
        
        autoStart = queryDict.get("autoStart", "")
        if autoStart == "": 
            autoStart = queryDict.get("autostart", "")
        if autoStart == "":
            autoStart = "0"
        data2 = data
        media = queryDict.get("media", "")
        if media!="":
            data2 += "?media=" + media
        for k in ["width", "height", "media"]:
            if queryDict.has_key(k):
                queryDict.pop(k)
        
        if ext in [".gif", ".png", ".jpg"]:     # embedded image
            alt = self.iceContext.fs.split(data)[1]
            newNode = createElement("img", width=width, height=height, src=data, alt=alt)
        elif classId=="" and codeBase=="":    # standard
            newNode = createElement("object", width=width, height=height, data=data, type=type)
            paramNode = createElement("param", name="src", value=data)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="type", value=type)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="autoStart", value=autoStart)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="controller", value="true")
            newNode.addChild(paramNode)
            pNode = createElement("p", title="Object failed to load, alternative text provided")
            newNode.addChild(pNode)
            aNode = createElement("a", elementContent=linkContent, href=data)
            pNode.addChild(aNode)
            # if .swf   then    wmode="transparent"
            if ext==".swf": 
                if wmode != "":
                    paramNode = createElement("param", name="wmode", value="transparent")
                    newNode.addChild(paramNode)
                if userDefinedParam != {}:
                    for key in userDefinedParam.keys():
                        paramNode = createElement("param", name=key, value=userDefinedParam[key])
                        newNode.addChild(paramNode)
        else:
            newNode = createElement("object", width=width, height=height, type=type, classid=classId, codebase=codeBase)
            paramNode = createElement("param", name="movie", value=data2)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="url", value=data2)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="autoStart", value=autoStart)
            newNode.addChild(paramNode)
            paramNode = createElement("param", name="base", value=base)
            newNode.addChild(paramNode)
            # if .swf   then    wmode="transparent"
            if ext==".swf":
                if wmode != "":
                    paramNode = createElement("param", name="wmode", value="transparent")
                    newNode.addChild(paramNode)
                if userDefinedParam != {}:
                    for key in userDefinedParam.keys():
                        paramNode = createElement("param", name=key, value=userDefinedParam[key])
                        newNode.addChild(paramNode)
            #<!--[if gte IE 7]> <!-->
            comment = createComment("[if gte IE 7]> <!")
            newNode.addChild(comment)
            newNode2 = createElement("object", width=width, height=height, type=type, data=data2)
            paramNode = createElement("param", name="base", value=base)
            newNode2.addChild(paramNode)
            paramNode = createElement("param", name="autoStart", value=autoStart)
            newNode2.addChild(paramNode)
            pNode = createElement("p", title="Object failed to load, alternative text provided")
            newNode2.addChild(pNode)
            aNode = createElement("a", elementContent=linkContent, href=data)
            pNode.addChild(aNode)
            newNode.addChild(newNode2)
            # if .swf   then    wmode="transparent"
            if ext==".swf":
                if wmode != "":
                    paramNode = createElement("param", name="wmode", value="transparent")
                    newNode2.addChild(paramNode)
                if userDefinedParam != {}:
                    for key in userDefinedParam.keys():
                        paramNode = createElement("param", name=key, value=userDefinedParam[key])
                        newNode2.addChild(paramNode)
            #<!--<![endif]-->
            #    <!--[if lt IE 7]>
            #     <![endif]-->
            comment = createComment("<![endif]")
            newNode.addChild(comment)
        return newNode
    
    
    def __getHtmlDivNode(self, queryList, linkContent, href, xml):
        protocol, loc, path, param, query, fid = urlparse.urlparse(href)
        foundFile = False
        data = None
        msg = ""
        errCode = ""
        newPath = ""
        if protocol=="http" or protocol=="https":
            local = self.iceContext.isNetlocLocal(loc)
            if href.find("/rep.")>0:
                if href.find("?")>0:
                    href += "&exportVersion=1"
                else:
                    href += "?exportVersion=1"

            if path.find("/rep.")>-1:
                filePath = path.lstrip("/rep.")
                pathStrip = filePath.split("/")
                repName = pathStrip[0]
                for i in range(1, len(pathStrip)):
                    newPath = self.__fs.join(newPath, pathStrip[i])
                
                if self.iceContext.reps is not None:
                    rep = self.iceContext.reps.getRepository(repName)
                    if rep is not None:
                        item = rep.getItemForUri(newPath)
                        item.convertFlag = True
                        if not item.isFile:
                            msg = "Missing"
                        else:
                            msg = "OK"
                            data = item.getHtmlRendition(embed=True)[0]
                            foundFile = True
            
            if data is None and msg!="Missing":
                foundFile = True
                data, _, errCode, msg = Http().get(href, includeExtraResults=True)
            
            if foundFile and data is not None:
                data = re.sub(r"\<\!(?!\[CDATA\[)(?!\-\-).*?\>", "", data)
                data = self.iceContext.HtmlCleanup.cleanup(data)
                try:
                    RelativeLinker = self.iceContext.getPlugin("ice.relativeLinker").pluginClass
                    relLinker = RelativeLinker(self.iceContext, self.__relDocPath)
                    data = relLinker.makeRelative(data, path=self._sourceFileName)
                except Exception, e:
                    print "Couldn't make links relative: %s" % str(e)
            if data==None:
                errCode = 500
                msg = "Couldn't read local content %s" % path
            else:
                errCode = 200
                msg = "OK"
        else:
            errCode = -1
            msg = "Unsupported protocol: %s" % protocol
        #print "---- %s ----" % href
        #print len(data), errCode, msg 
        if msg=="OK":
            data = re.sub("\<html\s.*?\>", "<html>", data)
            data = re.sub("\<HTML\s.*?\>", "<HTML>", data)
            data = "<div>%s</div>" % data
            try:
                newXmlNode = xml.xmlStringToElement(data)
            except Exception, e:
                newXmlNode = xml.xmlStringToElement(data, True)
            # get the body
            bodyNode = newXmlNode.getNode(".//body")
            if bodyNode is None:
                bodyNode = newXmlNode.getNode(".//BODY")
            if bodyNode!=None:
                bodyNode.setName("div")
                # get script elements in the head and insert them into body
                scriptNodes = newXmlNode.getNodes(".//head/script")
                firstChild = bodyNode.getFirstChild()
                if firstChild is None:
                    bodyNode.addChildren(scriptNodes)
                else:
                    for scriptNode in scriptNodes:
                        firstChild.addPrevSibling(scriptNode)
                newNode = bodyNode
            else:
                newNode = newXmlNode
        else:
            newNode = xml.createElement("div", style="border:1px solid red;color:red;")
            comment = xml.createComment("embedded html")
            newNode.addChild(comment)
            div = xml.createElement("div", style="padding:0.5em;")
            div.addContent("HTML embed error: ")
            div.addChild(xml.createElement("br"))
            div.addContent("url='%s'" % href)
            div.addChild(xml.createElement("br"))
            div.addContent("message='%s', errCode='%s'" % (msg, errCode))
            newNode.addChild(div)
            print "* HTML embed error: url='%s', msg='%s', code='%s'" % (href, msg, errCode)
        newNode.setAttribute("class", "embedded-html")
        return newNode
    
    def __convertATagToRdfa(self, xml):
        tripLinkPlugin = self.iceContext.getPlugin("ice.extra.TripLink")
        if tripLinkPlugin:
            defaultTemplatePath = self.iceContext.fs.absPath("plugins/extras/triplinkTemplate.json")
            tripLinkPlugin = tripLinkPlugin.pluginClass(defaultTemplatePath=defaultTemplatePath)     
            aNodes = xml.getNodes("//a")
            for aNode in aNodes:
                href = aNode.getAttribute("href")
                if href:
                    outerHtml = str(aNode)

                    processedMetadata = tripLinkPlugin.process(href, outerHtml)
                    rdfaContent = processedMetadata.get("RDFaTemplate")
                    if rdfaContent:
                        
                        xml = self.iceContext.Xml(rdfaContent)
                        dcTag, dcContent = processedMetadata.get("dc_metadata")
                        
                        metaTag = dcTag
                        metadata = dcContent
                        if dcTag == "creator":
                            metaTag = "authors"
                            metadata = []
                        
                        if self.convertedData.meta.has_key(metaTag):
                            metadata = self.convertedData.meta.get(metaTag)
                            
                        if metaTag == "authors":
                            metadata.append({"name": dcContent})
                        elif type(metadata).__name__ == "list":
                            metadata.append(dcContent)
                        
                        self.convertedData.meta[metaTag] = metadata
                        span = xml.getNodes("/*")
                        if span:
                            aNode.replace(span)
                        xml.close()
        
    def __fixupImageReferences(self, xml):
        imgNodes = xml.getNodes("//img")
        #print "__fixupImageReferences"
        #print " imageNames='%s'" % self.convertedData.imageNames
        #print " images='%s'" % self.convertedData.getMeta("images")
        
        images = {}
        for node in imgNodes:
            #print 'node before processImageNode: ', node
            newImgName = self.__processImageNode(node)
            #print 'newImgName after processImageNode: ', newImgName
            #newImgName = os.path.split(newImgName)[1]
            newImgName = self.__fs.split(newImgName)[1]
            images[newImgName] = None
        for img in self.convertedData.imageNames: 
            if not images.has_key(img):
                self.convertedData.removeImage(img)
        images = images.keys()
        images.sort()
        
        metaImages = self.convertedData.getMeta("images")
        metaImages.sort()
        
        #add back the new images meta and avoid redundancy
        for image in images:
            name, ext = self.__fs.splitExt(image)
            for metaImage in metaImages:
                metaName, metaext = self.__fs.splitExt(metaImage)
                if metaName == name and ext != metaext:
                    metaImages.remove(metaImage)
                    metaImages.append(image)
                elif (metaName.find(name)>-1 or (name.find(metaName)>-1) and ext == metaext):
                    metaImages.remove(metaImage)
                    metaImages.append(image)
                
        if metaImages ==[] or metaImages is None:
            metaImages = images
        
        self.convertedData.addMeta("images", metaImages)
#        self.convertedData.addMeta("images", images)
        #print "__fixupImageReferences() done."


    def __processImageNode(self, node):  
        #print "__fixupImageReferences()"
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
                    #fix all mathtype convert to png
                    #('math_files', 'm5e0afe47', '137', '45', 'bw', '.gif')
                    try: 
                        newImgName = self.__convertImageToPng(img, pieces, newSize)
                        node.setAttribute("src", newImgName)
                    except Exception, e:
                        self.__write("Error in BaseConverter.__processImageNode() convertMathType src='%s' ErrorMessage='%s'\n" % (src, str(e)))
#                    newSrc = pieces[0] + "/" + pieces[1] + "_" + pieces[2] + "x" + pieces[3] + "bw" + pieces[5]
#                    node.setAttribute("src", newSrc)
#                    newImgName = pieces[0] + "/" + pieces[1] + pieces[5]
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
                    #node.setAttribute("src", newImgName)
                else:
                    # ok change the size back to the original size (if not already)
                    imgSize = img.getSize() 
                    if not img.isAnim(): #only change for non-animated pics
                        node.setAttribute("width", str(imgSize[0]))
                        node.setAttribute("height", str(imgSize[1]))
                    #new src value with no _###x###
                    newImgName = pieces[0] + "/" + pieces[1] + pieces[5]
                    node.setAttribute("src", newImgName)
            elif src.startswith("media/"):
                newImgName = src
            elif src.find("skin/")==0:
                pass
            #elif src.find("skin/")!=-1:
            #    pass
            #else:
            #    self.__write("Warning: image was skipped because src='%s' has an unexpected pattern\n" % src)
        except Exception, e:
            self.__write("Error in BaseConverter.__processImageNode() src='%s' ErrorMessage='%s'\n" % (src, str(e)))
            #raise e
        #print "done __fixupImageReferences() %s => %s" % (orgImgName, newImgName)
        return newImgName

    def __convertImageToJpg(self, img, pieces, newSize):
        if img.hasTransparency():
            img.removeTransparency()
        newImgName = "%s_%sx%s.jpg" % (pieces[1], newSize[0], newSize[1])
        img.resizeImage2(newSize)
        filename = self.convertedData.abspath(newImgName)
        img.save(filename)
        self.convertedData.addImageFile(newImgName, filename)
        return pieces[0] + "/" + newImgName
    
    def __convertImageToPng(self, img, pieces, newSize, bw=True):
        newImgName = "%s_%sx%sbw.png" % (pieces[1], newSize[0], newSize[1])
        if not bw:
            newImgName = "%s_%sx%s.png" % (pieces[1], newSize[0], newSize[1])
        img.convertbwGifToPng(newSize)
        
        filename = self.convertedData.abspath(newImgName)
        img.save(filename)
        self.convertedData.addImageFile(newImgName, filename)
        
        return pieces[0] + "/" + newImgName
    
    
    def __write(self, str):
        if self.__output is not None:
            self.__output.write(str)





