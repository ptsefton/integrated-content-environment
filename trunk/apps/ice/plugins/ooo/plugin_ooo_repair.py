
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
import time

pluginName = "ice.ooo.repair"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    OoRepair.RepairTemplate = RepairTemplate
    pluginClass = OoRepair
    pluginInitialized = True
    return pluginFunc


class OoRepair(object):
    def __init__(self, iceContext, odtFile=None):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__odtFile = odtFile
        self.__rep = iceContext.rep
        self.__xml = iceContext.Xml
        self.oons = iceContext.OOoNSList 
        # for template repairing
        self.__replaceFiles = ["styles.xml", "Configurations2/menubar/menubar.xml"]
        self.__replaceDirs = ["Basic"]
        
    def repair(self, odtItem=None, tmpFile=None):
        if odtItem is None:
            odtFile = self.__odtFile
        else:
            odtFile = self.__rep.getAbsPath(odtItem.relPath)
        if tmpFile:
            odtFile = tmpFile
        self.repairLists(odtFile)
        if self.testForLinkedImages(odtFile)>0:
            self.breakLinks(odtFile)

    # zip_util.extractAllToTempDir
    # zip_util.zipTempDir(tmpDir, file)
    def repairTemplate(self, absOdtFiles=[], absTemplateFile=None):
        self.__templateFile = absTemplateFile
        
        #if self.__rep.getItem(absTemplateFile).isFile==False:
        if self.__rep.fs.isFile(absTemplateFile):
            raise Exception("templateFile not found!")

        results = []
        allOk = True
        try:
            templateTempDir = self.__fs.unzipToTempDirectory(absTemplateFile)
            try:
                for file in absOdtFiles:
                    try:
                        tempDir = None
                        try:
                            fileAbsPath = self.__rep.getAbsPath(file)
                            tempDir = self.__fs.unzipToTempDirectory(fileAbspath)
                            self.__repairTemplateFile(templateTempDir, tempDir)
                            tempDir.zip(file)
                        except Exception, e:
                            if tempDir is not None:
                                tempDir.delete()
                            raise e
                        results.append((True, "Updated template in file '%s' OK" % file))
                    except Exception, e:
                        allOk = False
                        results.append((False, 
                            "Failed to update template in file '%s'. Error: %s" % (file, str(e))))
            finally:
                if templateTempDir is not None:
                    templateTempDir.delete()
        except Exception, e:
            raise e
        return allOk, results

    def __repairTemplateFile(self, fromTempDir, tempDir):
        # Copy files
        fromTempDirName = str(fromTempDir)
        tempDirName = str(tempDir)
        for file in self.__replaceFiles:
            fromFile = self.iceContext.url_join(fromTempDirName, file)
            toFile = self.iceContext.url_join(tempDirName, file)
            #self.__fs.makeDirectory(dirname(toFile))
            self.__fs.copy(fromFile, toFile)
        # Copy directories
        for dir in self.__replaceDirs:
            fromDir = self.iceContext.url_join(fromTempDirName, dir)
            toDir = self.iceContext.url_join(tempDirName, dir)
            self.__fs.makeDirectory(toDir)
            self.__fs.copy(fromDir, toDir)


    def repairLists(self, odtFile=None):
        if odtFile is None:
            odtFile = self.__odtFile
        if odtFile is None:
            raise Exception("no odt file given to repair!")
        xml = None
        
        tmpDir = self.__fs.unzipToTempDirectory(odtFile)
        try:
            try:
                contentFile = self.__fs.join(str(tmpDir), "content.xml")
                xml = self.__xml(contentFile, self.iceContext.OOoNSList)
                try:
                    xml = self.__fixLists(xml)
                    xml.saveFile(contentFile)
                except Exception, e:
                    msg = "ERROR (in OoRepair.__fixLists()): %s" % str(e)
                    err = self.iceContext.formattedTraceback()
                    print err
                    raise Exception(msg)
            except Exception, e:
                msg = "ERROR (in OoRepair.repair()): %s" % str(e)
                raise Exception(msg)
            tmpDir.zip(odtFile)
        finally:
            if xml is not None:
                xml.close()
                xml = None
            tmpDir.delete()
        

    def testForLinkedImages(self, odtFile=None, contentXml=None):
        if odtFile is None and contentXml is None:
            odtFile = self.__odtFile
        if contentXml is None:
            if odtFile is None:
                raise Exception("Error: no odtFile or contentXml given!")
            content = self.__fs.readFromZipFile(odtFile, "content.xml")
            contentXml = self.iceContext.Xml(content, self.iceContext.OOoNSList)
            num = self.__testForLinkedImages(contentXml)
            contentXml.close()
            return num
        else:
            return self.__testForLinkedImages(contentXml)
    def __testForLinkedImages(self, contentXml):
        xpath = "//office:document-content/office:body/office:text//draw:image/@xlink:href"
        nodes = contentXml.getNodes(xpath)
        hrefs = [href.content for href in nodes]
        hrefs = [href for href in hrefs if href.startswith("../") or href.startswith("/")]
        return len(hrefs)


    def breakLinks(self, odtFile=None, toOdtFile=None):
        if odtFile is None:
            odtFile = self.__odtFile
            if odtFile is None:
                raise Exception("Error: no odtFile given!")
        file = odtFile
        toFile = toOdtFile
        if toFile is None:
            toFile = file
        print "**** Linked Images to be broken ****"
        print " file=", file
        tempDir = self.__fs.unzipToTempDirectory(file)
        tPath = str(tempDir)
        
        xml = self.iceContext.Xml(self.__fs.join(tPath, "content.xml"), self.iceContext.OOoNSList)
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
                    data = self.__fs.readFile(value)
                    name, ext = self.__fs.splitExt(value)
                    newName = "Pictures/" + self.iceContext.md5Hex(data) + ext
                    href.content = newName
                    self.__fs.makeDirectory(self.__fs.join(tPath, "Pictures"))
                    self.__fs.writeFile(self.__fs.join(tPath, newName), data)
                except Exception, e:
                    print "Error: (in .breakLinks()) " + str(e)
                    # OK then remove this image instead
                    href.getParent().delete()
        xml.saveFile()
        xml.close()
        tempDir.zip(toFile)
        tempDir.delete()


    def __getIndirectStyleNames(self, xml):
        autoStyleNames = dict()
        styleNodes = xml.getNodes("//office:automatic-styles/style:style")
        for styleNode in styleNodes:
            name = styleNode.getAttribute("name")
            value = styleNode.getAttribute("parent-style-name")
            autoStyleNames[name] = value
        return autoStyleNames
        

    def _fixLists(self, xml):        # for testing
        return self.__fixLists(xml)
    def __fixLists(self, xml):
        xml = self.__flattenLists(xml)
        
        # Get auto style names
        autoStyleNames = self.__getIndirectStyleNames(xml)
        
        # get style function
        def getStyle(node):
            if node is None:
                return None
            styleName = None
            
            if node.getName()=="text:list":
                node = node.getNode(".//*[name()='text:p']")
            #elif node.getName()!="p":
            #    return None
            
            if node!=None:
                styleName = node.getAttribute("style-name")
                if styleName is None:
                    styleName = node.getAttribute("text:style-name")
                # check for an indirect style name
                if styleName in autoStyleNames:
                    styleName = autoStyleNames[styleName]
            return styleName
        
        #
        oooStyle = self.iceContext.getPlugin("ice.ooo.utils").pluginClass.OOoStyle
        pNodes = xml.getNodes("//text:p")
        for pNode in pNodes:
            styleName = getStyle(pNode)
            style = oooStyle(name=styleName)
            if style.family=="li" and style.type!="p":
                listNode = xml.createElement("text:list")
                itemNode = xml.createElement("text:list-item")
                listNode.addChild(itemNode)
                pNode.replace(listNode)
                itemNode.addChild(pNode)
                prevStyle = None
                restart = False
                # get the style of the previous sibling
                prevSibling = listNode.getNode("preceding-sibling::*[1]")
                prevStyleName = getStyle(prevSibling)
                #print 
                #print "prevStyleName = ", str(prevStyleName)
                #print str(prevSibling)
                if prevStyleName is not None:
                    prevStyle = oooStyle(name=prevStyleName)
                
                if styleName!=None:
                    listNode.setAttribute("text:style-name", styleName)
                    #print "prevStyleName='%s', styleName='%s'" % (prevStyleName, styleName)
                    if self.__isPrevStyleDiff(style, prevStyle):
                        restart = True
                
                # set continue-numbering
                if restart==True:
                    # remove attribute text:continue-numbering="true"
                    #listNode.removeAttribute("continue-numbering")
                    listNode.setAttribute("text:continue-numbering", "false")
                else:
                    listNode.setAttribute("text:continue-numbering", "true")
        
        return xml
    
    
    def __isPrevStyleDiff(self, style, prevStyle):
        if style.family!="li":
            #print "Excepted sytle.family to be a 'li'!"
            return False
        if prevStyle is None:
            #print "Restart because prevStyle is None"
            return True
        if style.level>prevStyle.level:
            #print "style=", str(style)
            #print "prevStyle=", str(prevStyle)
            #print "Restart because style.level is greater than the prevStyle.level"
            return True
        if style.level<prevStyle.level and prevStyle.family=="li":
            #print "Continue because style.level is less than the prevStyle.level"
            return False
        if style.level==prevStyle.level:
            if style.family=="li":
                if prevStyle.family=="li":
                    if style.type==prevStyle.type:
                        #print "Continue because the prevStyle is the same"
                        return False
                    if prevStyle.type=="p":
                        #print "Continue because the prevStyle is a li#p of the same level"
                        return False
                #if prevStyle.family=="dt" or prevStyle.family=="dd":
                #    print "Continue because the prevStyle.family is 'dt|dd' with the same level"
                #    return False
        #print "Restart because a compatable prevStyle not found"
        return True
    

    def __flattenLists(self, xml):
        # Remove all text:list and text:list-item elements
        try:
            #print " flattenLists using python"
            startTime = time.time()
            
            # First remove all text:list and text:list-item elements (but not there children)
            nodes = xml.getNodes("//text:list | //text:list-item")
            for node in nodes:
                children = node.getChildren()
                node.replace(children)
            
            totalTime = str(round(time.time()-startTime,4))
            print "  Done %s\n" % totalTime
            xml2 = self.iceContext.Xml(str(xml), self.iceContext.OOoNSList)
            xml.close()
        except Exception, e:
            print "__flattenLists() exception - '%s'" % str(e)
            raise
        return xml2



class RepairTemplate(object):
    # replace styles.xml, Configurations2/menubar.xml and the Basic/Standard/*.xml files
    def __init__(self, iceContext, templateFile):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__rep = iceContext.rep
        self.__xml = iceContext.Xml
        self.oons = iceContext.OOoNSList
        self.__templateFile = templateFile
        self.__replaceFiles = ["styles.xml", "Configurations2/menubar/menubar.xml"]
        self.__replaceDirs = ["Basic"]
        
        self.styleList = {"h-audio":"audioCaption", "h-casestudy": "casestudyCaption", "h-cd":"cdCaption", "h-discussion":"discussionCaption", 
                 "h-example":"exampleCaption", "h-exercise":"exerciseCaption", "h-interactive":"interactiveCaption", 
                 "h-learning":"learningCaption","h-presentation":"presentationCaption", "h-reading":"readingCaption",
                 "h-reflection":"reflectionCaption", "h-selfassessment":"selfassessmentCaption", "h-stop":"stopCaption", "h-video":"videoCaption", 
                 "p-figure-caption":"figureCaption", "p-table-caption":"tableCaption",
                 "p-figure-caption-above":"figureCaption", "p-figure-caption-below":"figureCaption",
                 "p-table-caption-above":"tableCaption", "p-table-caption-below": "tableCaption"}
        
        self.__nextNumber = {}
        self.__activityStyles = {}
        self.__chapterNumber = 0
        
        #if self.__rep.getItem(self.__templateFile).isFile==False:
        if self.__fs.isFile(self.__templateFile)==False:
            raise Exception("templateFile not found!")
    
    def close(self):
        pass
    
    def repairFile(self, file):    
        pass
    
    def repairFiles(self, files=[]):        
        results = []
        allOk = True
        try:
            templateTempDir = self.__fs.unzipToTempDirectory(self.__templateFile)
            try:
                for file in files:
                    try:
                        tempDir = None
                        try:
                            fileAbsPath = self.__rep.getAbsPath(file)
                            tempDir = self.__fs.unzipToTempDirectory(fileAbsPath)
                            self.__repairFile(templateTempDir, tempDir)
                            tempDir.zip(fileAbsPath)
                            #self.__item.zipFromTempDir(tempDir)
                        except Exception, e:
                            if tempDir is not None:
                                tempDir.delete()
                            raise e
                        results.append((True, "Updated template in file '%s' OK" % file))
                    except Exception, e:
                        allOk = False
                        results.append((False, 
                            "Failed to update template in file '%s'. Error: %s" % (file, str(e))))
            finally:
                if templateTempDir is not None:
                    templateTempDir.delete()
                if tempDir is not None:
                    tempDir.delete()
        except Exception, e:
            raise e
        return allOk, results

    def __repairFile(self, fromTempDir, tempDir):        
        # Copy files
        fromTempDirName = str(fromTempDir)
        tempDirName = str(tempDir)
        for file in self.__replaceFiles:
            fromFile = self.iceContext.url_join(fromTempDirName, file)            
            if self.__fs.isFile(fromFile):
                #Before replace the style.xml, get all the <text:outline-style> 
                #incase the outline numbering is preset 
                toFile = self.iceContext.url_join(tempDirName, file)
                nodeLevel = {}
                if file=="styles.xml":
                    xml = self.__xml(toFile, self.iceContext.OOoNSList)
                    nodes = xml.getNodes("//text:outline-level-style ")  
                    if nodes != [] or nodes != None:  
                        for node in nodes:
                            level = node.getAttribute("level")
                            #print "NodeName='%s'" % name, "node='%s'" % node
                            nodeLevel[level] = node      
                    
                    
                #file_util.makeDir(os.path.dirname(toFile))
                #file_util.copyFile(fromFile, toFile)
                self.__fs.copy(fromFile, toFile)
                
                if nodeLevel != {} or nodeLevel != None:
                    #Replace text:outline-style
                    toXml = self.iceContext.Xml(toFile, self.iceContext.OOoNSList)
                    toNodes = toXml.getNodes("//text:outline-level-style ")
                    
                    for toNode in toNodes:
                        toLevel = toNode.getAttribute("level")
                        node = nodeLevel.get(str(toLevel))
                        toNode.replace(node)                    
                    
                    toXml.saveFile()
                    toXml.close()
                xml.close()
                
        self.__fixAutoText(tempDirName)
        # Copy directories
        for dir in self.__replaceDirs:
            fromDir = self.iceContext.url_join(fromTempDirName, dir)
            toDir = self.iceContext.url_join(tempDirName, dir)
            self.__fs.makeDirectory(toDir)
            self.__fs.copy(fromDir, toDir)


    def __fixAutoText(self, tempDirName):
        #Get Chapter/ModuleNumber
        metaFile = self.iceContext.url_join(tempDirName, "meta.xml")
        metaXml = self.__xml(metaFile, self.oons)
        dcTitle = metaXml.getNode("//dc:title")
        content = dcTitle.getContent()
        if content is not None and content.strip() != "":
            try:
                contentCount = content.split(" ")
                if len(contentCount) > 2:
                    chapterNumber = int(contentCount[1])
                    self.__chapterNumber = chapterNumber
            except:
                pass
        
        metaXml.close()
        #fix Caption
        contentFile = self.iceContext.url_join(tempDirName, "content.xml")
        contentXml = self.__xml(contentFile, self.oons)
        
        #populate styles
        allActivityStyles = contentXml.getNodes("""//style:style[starts-with(@style:parent-style-name, 'h-')] |
                                                   //style:style[starts-with(@style:parent-style-name, 'p-figure')] | 
                                                   //style:style[starts-with(@style:parent-style-name, 'p-table')]""")     
        if allActivityStyles is not None and allActivityStyles != []:
            for style in allActivityStyles:
                styleName = style.getAttribute("name")
                styleParentName = style.getAttribute("parent-style-name")
                if styleName is not None and styleName != "":
                    self.__activityStyles[styleName] = styleParentName
        
        #remove old captions
        variableDecNode = contentXml.getNode("//text:variable-decls")
        if variableDecNode != [] and variableDecNode is not None:
            children = variableDecNode.getChildren()
            if children != [] and children is not None:
                for child in children:
                    if child.getAttribute("name") == "FigureCaption" or \
                       child.getAttribute("name") == "figureCaption" or \
                       child.getAttribute("name") == "TableCaption"  or \
                       child.getAttribute("name") == "tableCaption":
                        child.remove()
         
        seqDeclarationNode = contentXml.getNode("//text:sequence-decls")
        if seqDeclarationNode is not None and seqDeclarationNode != []:
            for key in self.styleList:
                found = False        
                for child in seqDeclarationNode.getChildren():
                    attributeVal = child.getAttribute("name")
                    if attributeVal:
                        if self.styleList[key].lower() == attributeVal:
                            found = True
                    
                if found==False:
                    newSeqDec = contentXml.createElement("text:sequence-decl")
                    newSeqDec.setAttribute("text:display-outline-level", "1")
                    newSeqDec.setAttribute("text:separation-character", ".")
                    newSeqDec.setAttribute("text:name", self.styleList[key])
                    seqDeclarationNode.addChild(newSeqDec)
#        
        self.__processAllCaption(contentXml)
        contentXml.saveFile(contentFile)
        contentXml.close()
    
    def __processAllCaption(self, contentXml):
        allpTags = contentXml.getNodes("//text:p")
        for p in allpTags:
            replaceName = ""
            styleName = p.getAttribute("style-name")
            if self.styleList.has_key(styleName):
                replaceName = self.styleList[styleName]
            elif self.__activityStyles.has_key(styleName):
                hiddenName = self.__activityStyles[styleName]
                replaceName = self.styleList[hiddenName]
            if replaceName != "" and p.getChildren() != [] and p.getChildren() is not None:
                self.__processCaptions(p, contentXml, replaceName)
                    
    def __processCaptions(self, captions, contentXml, replaceName):
        autoNumber = 1
        if captions != []:
            if self.__nextNumber.has_key(replaceName):
                autoNumber = self.__nextNumber[replaceName] + 1
            self.__nextNumber[replaceName] = autoNumber
            spans = captions.getChildren()
            if spans is not None and spans != []:
                for span in spans:
                    spanChildren = span.getChildren()
                    if spanChildren != [] and spanChildren is not None:
                        for spanChild in spanChildren:
                            if spanChild.getContent() == ".":
                                span.remove()
                            if spanChild.getName() == "chapter":
                                if self.__chapterNumber == 0:
                                    if spanChild.getContent().strip() != "":
                                        self.__chapterNumber = int(spanChild.getContent())
                                span.remove()
                            if spanChild.getName() == "sequence":                                            
                                name = spanChild.getAttribute("name")
                                if replaceName != "":
                                    spanChild.removeAttribute("name")
                                    spanChild.setAttribute("text:name", replaceName)
                                    
                                    content = spanChild.getContent().strip()
                                    #update autonumber
                                    if content.find(".") > -1:
                                        self.__chapterNumber = content[:content.find(".")]
                                    spanChild.setContent("%s.%s" % (str(self.__chapterNumber), str(autoNumber)))
                                    refName = spanChild.getAttribute("ref-name")
                                    if refName:
                                        newRefName = "ref%s%s" % (replaceName, autoNumber)
                                        spanChild.removeAttribute("ref-name")
                                    spanChild.setAttribute("text:ref-name", newRefName)
                                    formula = spanChild.getAttribute("formula")
                                    if formula:
                                        newFormula = "ooow:%s+1" % replaceName
                                        spanChild.removeAttribute("formula")
                                    spanChild.setAttribute("text:formula", newFormula)
                                    spanChild.setContent("%s.%s" % (self.__chapterNumber, autoNumber))
                            if spanChild.getName() == "variable-set":
                                if replaceName != "":                                    
                                    newSeqNumber = contentXml.createElement("text:sequence")
                                    newSeqNumber.setAttribute("text:name", replaceName)
                                    newSeqNumber.setAttribute("text:ref-name", "ref%s%s" % (replaceName, autoNumber))
                                    newSeqNumber.setAttribute("text:formula", "ooow:%s+1" % (replaceName))
                                    newSeqNumber.setContent("%s.%s" % (self.__chapterNumber, autoNumber))
                                    spanChild.replace(newSeqNumber)







