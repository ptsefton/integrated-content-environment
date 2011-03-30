
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

from baseConverter import BaseConverter
from urllib import quote
import ipycomm

pluginName = "ice.test.render.docxConverter"
pluginDesc = "converts Word docx documents to HTML and PDF"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = DocxConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginClass


# First convert docx to odt
# then HACK: modify the content.xml file
#       removing draw:rect elements (and children)  - this will remove the small boxes from the top of the page
#       find all style:style[@style:family='graphic'] elements and add a
#                           style:parent-style-name="Graphics" attribute.
#                           This is so that OOo3 will add the alt attribute to the html version.

class DocxConverter(BaseConverter):
    fromToExts = {".docx":[".htm", ".pdf"]}
    docNS = {"ve": "http://schemas.openxmlformats.org/markup-compatibility/2006", 
         "o" : "urn:schemas-microsoft-com:office:office",
         "r" : "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
         "m" : "http://schemas.openxmlformats.org/officeDocument/2006/math",
         "v" : "urn:schemas-microsoft-com:vml",
         "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing", 
         "w10" : "urn:schemas-microsoft-com:office:word",
         "w" : "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
         "wne" : "http://schemas.microsoft.com/office/word/2006/wordml"
         } 

    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs
        BaseConverter.__init__(self, iceContext)
        self.convertToOdt = True
        self.__wc = None
        c = ipycomm.IPYComm()
        #print "\n--- DOCX --- c='%s'" % c
        if c.isRunning and c.error=="":
            self.__wc = c
            self._processImages = self.__wordProcessImages
            self.renderMethod = self.__wordDocRender
            self._setup1 = self.__setup1
            def doNothing(*args):
                pass
            self._fixupImageReferences = doNothing
            self._turnOleImagesIntoBW = False
        else:
            pass
            #print "  ERROR: %s" % c.error
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        #before render, convert the word4chem object to ontologize me link
        self.__processWord4Chem(file)
        print "DOCX render()"
        return self.renderMethod(file, convertedData)

    def __setup1(self, copyToMethod, sourceFileName, convertToOdt=False):
        if convertToOdt:
            # Convert to odt first
            print "DOCX converting to ODT"
            copyToMethod(sourceFileName, self._tmpDocFileName)
            self.__convertToOdt(self._tmpDocFileName, self._tmpOooFileName)
        else:
            copyToMethod(sourceFileName, self._tmpOooFileName)

    def __wordDocRender(self, file, convertedData):     # renderMethod()
        print "\n---- DOCX __wordDocRender(file='%s', convertedData) ----" % file
        self.convertedData = convertedData
        rep = self.iceContext.rep
        if rep is not None:
            absFile = rep.getAbsPath(file)
        else:
            absFile = file
        self._relDocPath, _, _ = self._fs.splitPathFileExt(file)
        # setup
        def copy(src, dest):
            src = absFile
            self.__fs.copy(src, dest)
        copyToMethod = copy
        sourceFileName = file
        self._sourceFileName = sourceFileName
        self._tmpOooFileName = self.convertedData.abspath("temp.odt")
        sourceExt = self.__fs.splitExt(sourceFileName)[1]
        self._tmpDocFileName = self.convertedData.abspath("temp" + sourceExt)
        self._tmpHtmlFileName = self.convertedData.abspath("temp.html")
        self._tmpPdfFileName = self.convertedData.abspath("temp.pdf")
        copyToMethod(sourceFileName, self._tmpDocFileName)
 
        self.__renderPdf(self._tmpDocFileName, self._tmpPdfFileName)
        self.convertedData.addRenditionFile(".pdf", self._tmpPdfFileName)
        self.__convertToOdt(self._tmpDocFileName, self._tmpOooFileName)
        self.__saveAsHtml(self._tmpDocFileName, self._tmpHtmlFileName)

        kwargs = {"includePdf":False}
        self._renderMethod(file, absFile, includeHtml=True, reindex=False, **kwargs)
        title = self._getTitle()
        if title=="":
            title = "Untitled"
        self.convertedData.addMeta("title", title)
        self._close()
        cData = self.convertedData
        self.convertedData = None
        return cData
    
    
    def __wordProcessImages(self, xhtml, htmlOooFile):
        # returns a list of image names
        images = {}
        imageList = []
        imageSrcs = {}
        print "---- wordProcessImages(xhtml, htmlOooFile='%s') ----" % htmlOooFile
        fileName = self.__fs.split(self._sourceFileName)[1]
        baseName = self.__fs.splitExt(fileName)[0]
        if fileName.endswith(".book.odt"):
            baseName = self.__fs.splitExt(baseName)[0]
        baseName += "_files/"            
        if False:
            imgNodes = xhtml.getNodes("//img")
            for img in imgNodes:
                src = img.getAttribute("src")
                name = self.__fs.split(src)[-1]
                imageSrcs[src] = name
                img.setAttribute("src", baseName + name)
            for src, name in imageSrcs.iteritems():
                try:
                    idata = self.__fs.readFromZipFile(self._tmpDocFileName, "word/" + src)
                    self.convertedData.addImageData(name, idata)
                except Exception, e:
                    print " -- %s" % str(e)
            # get list of images from the xhtml
            #self.convertedData.addImageFile(simpleName, filename=src)
        else:
            self._tmpHtmlFilesDir = self.__fs.splitExt(self._tmpHtmlFileName)[0]+"_files/"
            htmlStr = self.__fs.readFile(self._tmpHtmlFileName)
            htmlStr = htmlStr.decode("windows-1252").encode("utf-8")
            html = self.iceContext.Xml(htmlStr, parseAsHtml=True)
            imgNodes = html.getNodes("//img")
            for img in imgNodes:
                src = img.getAttribute("src")
                name = self.__fs.split(src)[-1]
                images[name] = (img.getAttribute("width"), img.getAttribute("height"))
                imageList.append(name)
            html.close()
            for name in images.keys():
                idata = self.__fs.readFile(self._tmpHtmlFilesDir + name)
                self.convertedData.addImageData(name, idata)
            imgNodes = xhtml.getNodes("//img")
            count = 0
            for img in imgNodes:
                name = imageList[count]
                img.setAttribute("src", baseName + name)
                count += 1
        return images.keys()
    
    
    def __saveAsHtml(self, fromAbsFile, toAbsFile):
        self.__wc.openDoc(fromAbsFile)
        self.__wc.saveDocAs(toAbsFile)
        self.__wc.closeDoc()
    
    def __renderPdf(self, fromAbsFile, toAbsFile):
        self.__wc.openDoc(fromAbsFile)
        self.__wc.saveDocAs(toAbsFile)
        self.__wc.closeDoc()

    def __convertToOdt(self, fromAbsFile, toAbsFile):
        self.__wc.openDoc(fromAbsFile)
        self.__wc.saveDocAs(toAbsFile)
        self.__wc.closeDoc()


    #====================================================
    
    def __processWord4Chem(self, fileRelPath):
        docAbsPath = self.iceContext.rep.getAbsPath(fileRelPath)
        
        #create template file as word 2007 locked the document for unzipping
        TempFileName = self.iceContext.rep.getAbsPath("temp.docx")
        self.iceContext.fs.copy(docAbsPath,TempFileName)
        TempFile = self.iceContext.rep.getAbsPath(TempFileName)
        documentTempDir = self.iceContext.fs.unzipToTempDirectory(TempFileName)
        document = self.iceContext.fs.join (documentTempDir.absPath(), "word/document.xml")
        relationships = self.iceContext.fs.join (documentTempDir.absPath(), "word/_rels/document.xml.rels")

        customXmlList = {}
#        try:
        lastRelationshipId, relationshipList = self.__getLastRelationshipId(relationships)
        
        #Getting customXml information
        documentXml = self.iceContext.Xml(document, self.docNS.items())
        customXmls = documentXml.getNodes("//w:customXml")
        for customXml in customXmls:
            lastRelationshipIdStr = "rId%s" % lastRelationshipId
            attrList = {}
            
            customXmlPrAttributes = customXml.getNodes("./*[local-name()='customXmlPr']/*[local-name()='attr']")
            for attr in customXmlPrAttributes:
                name = attr.getAttribute("name").strip()
                val = attr.getAttribute("val").strip()
                attrList[name] = val
            url = ""
            anchor = ""
            if attrList.has_key("url"):
                url = attrList["url"]
                anchor = self.__getAnchor(url)
            
            text = self.__getTextContent(customXml)
            
            #replacing smart tag with new hyperlink tag
            smartTag = customXml.getNode("./*[local-name()='smartTag']")
            rsidRPr = ""
            if smartTag:
                #get old rsidRPRr id from the w:r in smarttag
                wr = smartTag.getNode("./*[local-name()='r']")
                if wr:
                    rsidRPr = wr.getAttribute("rsidRPr")
            else:
                smartTag = customXml.getNode("./*[local-name()='r']")
                if smartTag:
                    rsidRPr = smartTag.getAttribute("rsidRPr")
            
            #new hyperlink Tag
            hyperlinkNode = documentXml.createElement("w:hyperlink")
            hyperlinkNode.setAttribute("r:id", lastRelationshipIdStr)
            hyperlinkNode.setAttribute("w:anchor", anchor)
            hyperlinkNode.setAttribute("w:history", "1")
            
            #new w:r node
            newWrNode = documentXml.createElement("w:r")
            newWrNode.setAttribute("w:rsidRPr", rsidRPr)
            hyperlinkNode.addChild(newWrNode)
            
            #new w:rPr hyperlink Node
            newWPrNode = documentXml.createElement("w:rPr")
            newWrNode.addChild(newWPrNode)
            
            #new w:rStyle node
            newRStyleNode = documentXml.createElement("w:rStyle")
            newRStyleNode.setAttribute("w:val", "Hyperlink")
            newWPrNode.addChild(newRStyleNode)
            
            #new w:t node (can we just copy the old node??)
            newWTNode = documentXml.createElement("w:t")
            newWTNode.setContent(text)
            newWrNode.addChild(newWTNode)
            
            if smartTag: 
                smartTag.replace(hyperlinkNode)    
            customXmlList[lastRelationshipIdStr] = (text, attrList)
            
            lastRelationshipId+=1
        documentXml.saveFile()
        
        #relationship
        relationshipXml = self.iceContext.Xml(relationships)
        relationshipsNode = relationshipXml.getRootNode()
        for key in customXmlList:
            textValue, attr = customXmlList[key]
            if textValue != '':
                url = ""
                if attr.has_key("url"):
                    url = attr["url"]
                    findAnchor = url.find("#")
                    if findAnchor != -1:
                        url = url[:findAnchor]
                textValue = quote(textValue)
                targetStr = "http://ontologize.me/meta/?r=%s&o=%s" % (textValue, url)
                if targetStr not in relationshipList:
                    newRelationshipNode = relationshipXml.createElement("Relationship")
                    newRelationshipNode.setAttribute("Id", key)
                    newRelationshipNode.setAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink")
                    newRelationshipNode.setAttribute("Target", targetStr)
                    newRelationshipNode.setAttribute("TargetMode", "External")
                
                    relationshipsNode.addChild(newRelationshipNode)
        relationshipXml.saveFile()
        relationshipXml.close()
        
        documentXml.close()
    
        # delete all Temp files 
        documentTempDir.zip(TempFileName)
        documentTempDir.delete()
        self.iceContext.fs.delete(path=TempFileName)    
#        except Exception, e:
#            print 'error'
#            raise e


    def __getLastRelationshipId(self, relationshipDocument):
        relationshipXml = self.iceContext.Xml(relationshipDocument)
        relationships = relationshipXml.getRootNode()
        lastRelationshipId = 1
        relationshipList = []
        for relationshipNode in relationships.getChildren():
            Id = relationshipNode.getAttribute("Id")
            Target = relationshipNode.getAttribute("Target")
            relationshipList.append(Target)
            idNumber = int(Id[3:])
            if lastRelationshipId < idNumber:
                lastRelationshipId = idNumber
                
        relationshipXml.close()
        return lastRelationshipId + 1, relationshipList


    def __getAnchor(self, url):
        anchor = ""
        anchorLocation = url.find("#")
        if anchorLocation!=-1:
            anchor = url[anchorLocation+1:]
        return anchor

    
    def __getTextContent(self, customXml):
        textValue = ""
        text = customXml.getNode("./*[local-name()='r']/*[local-name()='t']")
        if text:
            textValue = text.getContent()
        else:
            text = customXml.getNode("./*[local-name()='smartTag']/*[local-name()='r']/*[local-name()='t']")
            if text:
                textValue = text.getContent()
                
        return textValue.strip()







