import sys, os
from urllib import quote_plus, urlopen, urlretrieve
import urllib2
from base64 import b64encode
import time

import tempfile

OONS = [
             ["office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"],
             ["xlink", "http://www.w3.org/1999/xlink"],
             ["dc", "http://purl.org/dc/elements/1.1/"],
             ["meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"],
             ["ooo","http://openoffice.org/2004/office"],
             ["office","urn:oasis:names:tc:opendocument:xmlns:office:1.0"],
             ["style","urn:oasis:names:tc:opendocument:xmlns:style:1.0"],
             ["text","urn:oasis:names:tc:opendocument:xmlns:text:1.0"],
             ["table","urn:oasis:names:tc:opendocument:xmlns:table:1.0"],
             ["draw","urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"],
             ["fo","urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"],
             ["xlink","http://www.w3.org/1999/xlink"],
             ["dc","http://purl.org/dc/elements/1.1/"],
             ["meta","urn:oasis:names:tc:opendocument:xmlns:meta:1.0"],
             ["number","urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"],
             ["svg","urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"],
             ["chart","urn:oasis:names:tc:opendocument:xmlns:chart:1.0"],
             ["dr3d","urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"],
             ["math","http://www.w3.org/1998/Math/MathML"],
             ["form","urn:oasis:names:tc:opendocument:xmlns:form:1.0"],
             ["script","urn:oasis:names:tc:opendocument:xmlns:script:1.0"],
             ["ooo","http://openoffice.org/2004/office"],
             ["ooow","http://openoffice.org/2004/writer"],
             ["oooc","http://openoffice.org/2004/calc"],
             ["dom","http://www.w3.org/2001/xml-events"],
             ["xforms","http://www.w3.org/2002/xforms"],
             ["xsd","http://www.w3.org/2001/XMLSchema"],
             ["xsi","http://www.w3.org/2001/XMLSchema-instance"]
        ]
#CONTENT_STRING = """<?xml version="1.0" encoding="UTF-8"?><root xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
#xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
#xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"></root>"""
CONTENT_STRING = """<?xml version="1.0" encoding="UTF-8"?><root/>"""

def getContent(rootNode, xpath):
    element = rootNode.getNode(xpath)
    if element:
        return element.getContent()
    return ""

def isNotEmpty(nodes):
    return nodes!= [] and nodes is not None

class RequestObject(object):
    def __init__(self, requestNode, sitePath):
        self.requestNode = requestNode
        self.sitePath = sitePath
        self.departmentName = "" #not implemented
        
        self.courseCode = getContent(self.requestNode, "./course_code")
        self.courseName = getContent(self.requestNode, "./course_name")
        self.courseFaculty = getContent(self.requestNode, "./course_faculty")
        self.facultyName = ""
        if self.courseFaculty:
            facultyObject = Faculty(self.sitePath, self.courseFaculty)
            self.facultyName = facultyObject.facultyName
        self.courseYear = getContent(self.requestNode, "./course_year")
        self.courseSemester = getContent(self.requestNode, "./course_semester")
        self.prodRef = getContent(self.requestNode, "./srms_prod_ref")
        self.warning = getContent(self.requestNode, "warning")
        
        self.sortedReadingNumber = []
        self.availableReading = []
        self.readingListDict = {}
        self.moduleTitleList = {}
        self.duplicateReading = []
    
class Faculty(object):
    def __init__(self, siteFilePath, facultyCode=None):
        self.__facCode=""
        if facultyCode is not None:
            self.__facCode = facultyCode

        self.__facDict = {"":""}

        #siteFilePath = "%s/" % siteFilePath.rstrip("/")
        #fileName = "%sfacultyList.txt" % siteFilePath
        try:
            f = open("plugins\usq\\facultyList.txt", "r")
            lines = f.readlines()
            f.close()
            for line in lines:
                line = line.strip()
                if line=="" or line.startswith("#"):
                    pass
                else:
                    parts = line.split()
                    if len(parts)<3:
                        self.__facDict[parts[0]] = parts[1]
                    else:
                        strPart = ""
                        for part in range(1, len(parts)):
                            strPart += parts[part] + " "
                        self.__facDict[parts[0]] = strPart
        except Exception, e:
            print "ERROR: Loading Faculty.txt file failed"

    @property
    def facultyName(self):
        if self.__facDict.has_key(self.__facCode):
            return self.__facDict[self.__facCode].strip()
        return None

class CopyRightClass(object):
#Type of copyright
#If the Copyright isn't reproduced with permission and if we have the file for any SRMS, 
    #ICE outputs copyright code and checks the copyright code if it's valid
#If the Copyright IS reproduced without permission:
    #If the copyright code is "RWP" and there is no copyright notice then an error is generated - "Reproduce with Permission copyright code found but do not copyright notice"
    #If there is copyright notice, ICE outputs the copyright notice.
#Check the copyright code if it's valid
#If there is something in the code field:
    #Copyright code is valid if we find "Commonwealth of Australia" or "WARNING"
    #If the code is "no copyright code" AND copyright notice doesn't have "Commonwealth of Australia" or "WARNING" treat it as Special
    #If the copyright code isn't "RWP" and there is no copyright notice, then an error is generated - "No copyright code but has a standard copyright notice"
#If there's no code and no notice, an error is generated - "No copyright code and copyright notice"

    def __init__(self, copyrightCode, copyrightNotice, haveFile=True):
        self.copyrightCode = copyrightCode
        self.copyrightNotice = copyrightNotice
        
        self.errorStr = ""
        self.isSpecial = False
        self.isValid = self.__isValid()
        if not haveFile:
            self.errorStr = ""

    def __findStringInNotice(self, str):
        return self.copyrightNotice.find(str)!=-1
    
    def __isValid(self):
        foundStandardNotice = self.__findStringInNotice("Commonwealth of Australia") or self.__findStringInNotice("WARNING")
        if self.copyrightCode=="RWP":
            self.isSpecial = True
            if not self.copyrightNotice:
                self.errorStr = "Reproduce with Permission copyright code found but the copyright notice is empty"
                return False
            return True
        elif self.copyrightCode:
            if self.copyrightNotice:
                if self.copyrightCode == "no copyright code" and not foundStandardNotice:
                     self.isSpecial = True
                     return True 
            return True
        elif self.copyrightNotice:
            if foundStandardNotice:
                self.errorStr = "No copyright code but has a standard copyright notice"
            else:
                self.errorStr = "No copyright code but has copyright notice"
            return False
        else:
            self.errorStr = "No copyright code and copyright notice"
            return False

    def getCopyrightCodeNode(self, xml):
        if not self.isSpecial and self.copyrightCode:
            spanNode = xml.createElement("text:span")
            spanNode.setAttribute("text:style-name", "copyright")
            spanNode.addContent(" [%s]" % self.copyrightCode)
            return spanNode
        return None
        
    def getCopyrightNoticeNode(self, xml):       
        if self.isSpecial and self.copyrightNotice:
            copyrightNode = xml.createElement("text:p")
            copyrightNode.setAttribute("text:style-name", "p")
            copyrightSpan = xml.createElement("text:span")
            copyrightSpan.setAttribute("text:style-name", "alternatives")
            copyrightSpan.setContent(self.copyrightNotice)
            copyrightNode.addChild(copyrightSpan)
            return copyrightNode
        return None

class AlternativeObject(object):
#If alternative type is NONE:
    #ICE product warning mentioning none of the srms are ticked
    #the alternative string will be produced:
        #online:    This reading is not available online for this course
        #CD:        This reading is not available on the CD for this course
        #Print:     This reading is not available on the printed material for this course
#If request is WWW:
    ###################################################
    # alternative Type   #  alternative string        #
    #   Online:          #    ""                      #
    #   CD:              #    on the CD               # 
    #   Print:           #    on the printed material #
    ###################################################
#If request is CDT:
    ###################################################
    # alternative Type   #  alternative string        #
    #   Online:          #    online                  #
    #   CD:              #    ""                      # 
    #   Print:           #    on the printed material #
    ###################################################
#If request is SR:
    #######################################################
    # alternative Type   #  alternative string            #
    #   Online:          #    online                      #
    #   CD:              #    on the CD                   # 
    #   Print:           #    on another printed material #
    #######################################################
    def __init__(self, requestType, alternativeNode= None, hasUrl=False):
        self.alternativeNode = alternativeNode
        self.requestType = requestType
        self.hasUrl = hasUrl
        
        self.isDrProduct = False
        self.isInAnotherPrinting = False
        self.typeIsNone = False     #this is to report those reading that has none of the smrs ticked
        self.typeLists = self.__getAllAlts()
            
    def __getAllAlts(self):
        typeLists = []
        if isNotEmpty(self.alternativeNode):
            children = self.alternativeNode.getNodes("./alt")
            if isNotEmpty(children):
                for child in children:
                    type = getContent(child, "./type")
                    prodRef = getContent(child, "./prod_ref")
                    if prodRef.find("DR1")!=-1:
                        self.isDrProduct = True
                    if type=="Print" and self.requestType == "SR":
                        self.isInAnotherPrinting = True
                    if type:
                        typeLists.append(type)            
        return typeLists
    
    @property
    def altStr(self):
        altStr = ""
        if self.hasUrl:
            return self.__getAltStr('url')
        if self.typeLists:
            self.typeLists.sort()
            if len(self.typeLists) == 1 and self.typeLists[0] == 'none':
                self.typeIsNone = True
                str = self.__getAltStr('none')
                altStr = "This reading is not available %s for this course" % str 
            else:
                for type in self.typeLists:
                    str = self.__getAltStr(type)
                    if str:
                        altStr += " %s and" % str
                if altStr:
                    altStr = "This reading is available%s for this course" % altStr.rstrip(" and ")
        return altStr
    
    def __getAltStr(self, type):
        if type=="url":
            if self.requestType=="WWW":
                return ""
            if self.requestType=="CDT" or self.requestType=="DVDT":
                return "To access this reading you must be connected to the internet."
            if self.requestType=="SR":
                return "Please access this reading via the DiReCt link on your USQStudyDesk."
        if type=="CD" or type=="DVD":
            return "on the CD"
        if type=="Online":
            return "online"
        if type=="Print":
            if self.isInAnotherPrinting:
                return "on another printed material"
            else:
                return "on the printed material"
        if type=="none":
            if self.requestType=="WWW":
                return "online"
            if self.requestType=="CDT" or self.requestType=="DVDT":
                return "on the CD"
            if self.requestType=="SR":
                return "on the printed material"
        return None
    
    def getAltNode(self, xml):        
        if self.altStr:
            altNode = xml.createElement("text:p")
            altNode.setAttribute("text:style-name", "p")
            altSpan = xml.createElement("text:span")
            altSpan.setAttribute("text:style-name", "alternatives")
            altSpan.setContent(self.altStr)
            altNode.addChild(altSpan)
            return altNode
        return None
      
class FileObject(object):
    def __init__(self, fileNode=None, iceContext=None):
        self.fileNode = fileNode
        self.isHighRes = False
        
        self.fileName = ""
        if self.fileNode is not None:
            self.fileName = getContent(self.fileNode, "./name")
            if self.fileName.find("hires.pdf")!=-1:
                self.isHighRes=True
                
        self.exportUrl = ""
        if self.fileNode is not None:
            self.exportUrl = getContent(self.fileNode, "./export_url").strip()
        
        self.username = iceContext.session.username
        self.isValidPdf = False
        self.isDownloadSuccess = None
        self.isEncrypted = False
        self.iceContext = iceContext
        self.downloadedFilePath = ""
        if self.iceContext is not None:
            self.pdfUtilClass = self.iceContext.getPlugin("ice.pdfUtils").pluginClass(self.iceContext.fs)
        
    def downloadFile(self, test=False):
        if test:
            tempDirectory = tempfile.gettempdir()
            downloadPath = "%s/%s" % (tempDirectory.rstrip("/"), self.fileName)
            
            self.username = "octalina"
            exportUrl = "%s%s" % (self.exportUrl, self.username)
            
            tempDirectory = tempfile.gettempdir()
            self.downloadedFilePath = "%s/%s" % (tempDirectory.rstrip("/"), self.fileName)
        
        try:
            exportUrl = "%s%s" % (self.exportUrl, self.username)
            print "Downloading: %s" % self.fileName 
            #urlretrieve(exportUrl, filename=self.downloadedFilePath)
            
            file = open(self.downloadedFilePath, "wb")
            retrieve = urllib2.urlopen(exportUrl)
            file.write(retrieve.read())
            file.close()
            
            if self.iceContext.fs.exists(self.downloadedFilePath):
                self.isValidPdf = not self.isValidPdfFile()
                self.isDownloadSuccess = self.isValidPdf
            else:
                self.isDownloadSuccess = False
                self.downloadErrorMsg="Unable to download the %s from %s" % (self.name, exportUrl)
        except Exception, e:
            self.isDownloadSuccess = False
            pass
    

    def isValidPdfFile(self, pdfFileNeedToBeTested=None):
        if pdfFileNeedToBeTested:
            self.downloadedFilePath = pdfFileNeedToBeTested
        if self.downloadedFilePath:
            #check for EOF
            pdfReaderUtil = self.pdfUtilClass.pdfReader()
            pdfReader = pdfReaderUtil.createPdfReader(self.downloadedFilePath)
            isInValid = True
            if pdfReader is not None:
                isInValid = False
                if pdfReaderUtil.isEncrypted:
                    self.isEncrypted = True
                pdfReaderUtil.close()
            else:
                #this is invalid with no %EOF, try to fix it
                pdfReaderUtil.close()
                fixed = self.pdfUtilClass.fixPdf(self.downloadedFilePath)
                if fixed=="Fixed":
                    #try to reopen the pdf
                    pdfReader = pdfReaderUtil.createPdfReader(self.downloadedFilePath)
                    if pdfReader is not None:
                        isInValid = False
                    if pdfReaderUtil.isEncrypted:
                        self.isEncrypted = True
                    pdfReaderUtil.close()
            return isInValid
        else:
            return False


class Citation(object):
    #make sure to preserve the <i> or <b> tags from direct
    def __init__(self, citationNode):
        self.citationNode = citationNode
        self.lecturerPref = getContent(self.citationNode, "./lecturer_preference")
        self.citationType = getContent(self.citationNode, "./citation_type").lower()
        self.lecPrefCite = self.__getNodeContent(self.citationNode.getNode("./%s" % self.lecturerPref), preserve=True)
        self.harvard = self.__getNodeContent(self.citationNode.getNode("./harvard"), preserve=True) 
    @property
    def citation(self):
        if self.lecturerPref:
            return self.lecPrefCite
        else:
            return self.harvard
    
    def __getNodeContent(self, node, preserve=False):
        if node is not None:
            if preserve:
                return str(node).replace("<%s>" % node.getName(), "").replace("</%s>" % node.getName(), "")
            elif isNotEmpty(node):
                return node.getContent()
        return ""
    
    def getCitationNode(self, xml, iceContext):
        if self.citation:
            citationItemNode = xml.createElement("text:p")
            citationItemNode.setAttribute("text:style-name", "p")
            bibioNode = []
            if self.citation.find("&lt;i&gt;")>-1 or self.citation.find("&lt;b&gt;")>-1:
                bibioNode = self.__processContent(self.citation, iceContext)
            if bibioNode != []:
                for node in bibioNode:
                    citationItemNode.addChild(node)
            else:
                citationItemNode.setContent(self.citation)
            return citationItemNode
        return None
    
    #if this is used in other class, make public
    def __processContent(self, content, iceContext):
        contentNode = []
        content = content.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>").replace("&amp;lt;", "&lt;")
        content = content.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>").replace("&amp;gt;", "&gt;")
        contentString = '<?xml version="1.0" encoding="UTF-8"?><root>%s</root>' % content
        contentXml = iceContext.Xml(contentString)
        nodes = contentXml.getNodes("//i | //b")
        if isNotEmpty(nodes):
            for node in nodes:
                name = node.getName()
                if name=="i":
                    style = "i-i"
                elif name=="b":
                    style = "i-b"
                node.setName("text:span")
                node.setAttribute("text:style-name", style)

        for child in contentXml.getNode("//root").getChildren():
            childCopy = child.copy()
            contentNode.append(childCopy)

        contentXml.close()
        return contentNode

class ReadingItem(object):
    def __init__(self, readingNode, requestType, iceContext, printVersion=False):
        self.readingNode = readingNode
        self.requestType = requestType
        self.__xml = iceContext.Xml
        self.__iceContext = iceContext
        self.__printVersion = printVersion            #####NOTE: this is for CDT BOOK and other BOOK
        self.pageNumberInBook = 0
        self.alternative = None
        self.initialize()
            
    def initialize(self):
        self.readingNumber = getContent(self.readingNode, "./reading_number")
        if self.readingNumber.find("Reading")!=-1:
            self.readingNumber = self.readingNumber.replace("Reading", "").strip()
        self.permalink = getContent(self.readingNode, "./permalink")
        self.citation = Citation(self.readingNode.getNode("./citations"))
        
        self.copyrightCode = getContent(self.readingNode, "./copyright_code") 
        self.copyrightNotice = getContent(self.readingNode, "./copyright_notice")
        
        self.url = getContent(self.readingNode, "./url")
        self.available = self.readingNode.getAttribute("available")
        self.status = self.readingNode.getAttribute("status")
        self.alternativeNode = self.readingNode.getNode("./alternatives")
        self.fileListNode = self.readingNode.getNode("./file_list")
        self.fileList = self.__getFileList()
        hasUrl = self.url!=''
        if self.fileList == []:
            if isNotEmpty(self.alternativeNode):
                self.alternative = AlternativeObject(self.requestType, self.alternativeNode)
            elif hasUrl:
                self.alternative = AlternativeObject(self.requestType, self.alternativeNode, hasUrl=hasUrl)
            
    @property
    def copyright(self):
        cpClass = CopyRightClass(self.copyrightCode, self.copyrightNotice, haveFile=self.fileList!=[])
        return cpClass
        
    def __getFileList(self):
        fileList = []   #is there any more case high rest with split file?
        if isNotEmpty(self.fileListNode):
            children = self.fileListNode.getChildren()
            if isNotEmpty(children):
                for file in children:
                    fileObject = FileObject(file, self.__iceContext)
                    if fileObject.fileName:
                        fileList.append(fileObject)
        return fileList
    
    def generateReadingNumberNode(self, xml, withPermalink=True):
        foundLowResFile = False
        readingNumberTitle = "Reading %s" % self.readingNumber
        readingNumberNode = xml.createElement("text:p")
        readingNumberNode.setAttribute("text:style-name", "h2")
        
       
        if withPermalink: #All online, some case for CD and Print
            if self.permalink:
                readingPermalink = xml.createElement("text:a")
                readingPermalink.setAttribute("xlink:href", self.permalink)
                readingPermalink.setAttribute("office:target-frame-name", "_blank")
                readingPermalink.setAttribute("xlink:show", "new")
                readingPermalink.setContent(readingNumberTitle)
                readingNumberNode.addChild(readingPermalink)
            else:
                readingNumberNode.setContent(readingNumberTitle)
                
            #copyright code *** duplicate....***
            if self.fileList != [] and not foundLowResFile:
                copyrightCodeNode = self.copyright.getCopyrightCodeNode(xml)
                if copyrightCodeNode is not None:
                    space = xml.createElement("text:s")
                    space.setAttribute("text:c", "4")
                    readingNumberNode.addChild(space)
                    readingNumberNode.addChild(copyrightCodeNode)
                
        if not withPermalink:
            readingNumberNode.setContent(readingNumberTitle)
            
            #copyright code *** duplicate....***
            if self.fileList != [] and not foundLowResFile:
                copyrightCodeNode = self.copyright.getCopyrightCodeNode(xml)
                if copyrightCodeNode is not None:
                    space = xml.createElement("text:s")
                    space.setAttribute("text:c", "4")
                    readingNumberNode.addChild(space)
                    readingNumberNode.addChild(copyrightCodeNode)
            
            if (self.requestType == "CDT" or self.requestType == "DVDT") and not self.__printVersion:   #put pdf icon
                if self.fileList != []:
                    #if file is not low res..... and download success the put icon
                    #SHOULD the adding copy right page done here?????????????????
                    fileList = self.fileList
                    for fileObject in fileList:
                        if fileObject.isHighRes: #and fileObject.isDownloadSuccess 
                            fileName = fileObject.fileName
                            space = xml.createElement("text:s")
                            space.setAttribute("text:c", "1")
                            readingNumberNode.addChild(space)
                            fileLink = self.__addPdfImage(fileName, xml)
                            readingNumberNode.addChild(fileLink)
                        else:
                            foundLowResFile = True
            else: #for print version
                pass        
            
        return readingNumberNode
    
    @property
    def moduleNumber(self):
        if self.readingNumber.find(".")>-1:
            return self.readingNumber.split(".")[0]
        return 0
    
    def getUrlNode(self, xml):
        url = self.url
        if url.find("ezproxy")>-1:
            url = ""
                
        if url:
            urlNode = xml.createElement("text:p")
            urlNode.setAttribute("text:style-name", "p")
            urlNode.setContent(self.url)
            return urlNode
        return None
    
    def __addPdfImage(self, fileName, contentXml):
        filePath = "../media/readings/%s" % fileName
        fileLink = contentXml.createElement("draw:a")
        fileLink.setAttribute("xlink:type", "simple")
        fileLink.setAttribute("xlink:href", filePath)
        fileIcon = contentXml.createElement("draw:frame")
        fileIcon.setAttribute("draw:style-name", "fr1")
        fileIcon.setAttribute("draw:name", filePath)
        fileIcon.setAttribute("text:anchor-type", "as-char")
        fileIcon.setAttribute("svg:width","0.741cm")
        fileIcon.setAttribute("svg:height","0.82cm")
        fileIcon.setAttribute("draw:z-index","0")
        fileLink.addChild(fileIcon)
        fileImage = contentXml.createElement("draw:image")
        fileImage.setAttribute("xlink:href", "Pictures/pdf.gif")
        fileImage.setAttribute("xlink:type", "simple")
        fileImage.setAttribute("xlink:show", "embed")
        fileImage.setAttribute("xlink:actuate", "onLoad")
        fileIcon.addChild(fileImage)

        return fileLink
    
    
class SRMSObject(object):
    def __init__(self, srmsNode, requestType, direct_types=[]):
        self.srmsNode = srmsNode
        self.requestType = requestType
        self.direct_types = direct_types
        self.prodRefList = self.__getProdRef()
        self.hasProdRef = self.prodRefList != {}
        self.srmsNode.close()
        
        #child objects
        self.requestObjectList = []
        

    def __getProdRef(self):
        prodRefList = {}
        try:
            if self.direct_types != []:
                str = ""
                for direct_type in self.direct_types:
                    str += "direct_type='%s' or " % direct_type
                requestStr = str.rstrip(" or ")
            else:
                requestStr = "srms_type='%s'" % self.requestType
            matchNodes = self.srmsNode.getNodes("//match[%s]" % requestStr)    
            if matchNodes:
                for match in matchNodes:
                    srmsProdRef = getContent(match, "./srms_prod_ref")
                    directTotal = getContent(match,"./direct_total")
                    if directTotal:
                        directTotal = int(directTotal)
                    prodRefList[srmsProdRef] = directTotal
            return prodRefList
        except Exception, e:
            return {}

class DirectHelper(object):
    def __init__(self, iceContext, packagePath, requestType, pdfFileContainer=None,
                 courseFullName="", courseYear="", semesterNumber="", packageTitle=""):
        self.__courseFullName = courseFullName
        self.__courseYear = courseYear

        if semesterNumber[:1].lower() == "s":
            semesterNumber = semesterNumber[1:]
        else:
            semester = "S%s" % semesterNumber
        self.__semester = semester
        self.__semesterNumber = semesterNumber
        if len(courseYear) == 4:
            courseYear = courseYear[2:]
        self.__cycleId = "%s%sSM" % (courseYear, self.__semester)

        self.iceContext = iceContext

        self.pdfUtilClass = self.iceContext.getPlugin("ice.pdfUtils").pluginClass(self.iceContext.fs)

        self.pdfFileContainer = pdfFileContainer
        self.requestType = requestType
        self.__xml = self.iceContext.xmlUtils.xml
        self.__packagePath = packagePath
        self.__rep = iceContext.rep
        self.__fs = iceContext.fs
    
    @property
    def oons(self):
        return OONS
    
    def prod_refList(self, direct_types=[]):
        #prod_ref = {}
        srmsObject = None
        #course=CMS1000&year=2008&sem=2
        srmsUrl = "http://ereserveweb-prod2.usq.edu.au:8089/services/export/srms.php?course=%s&year=%s&sem=%s"
        srmsUrl = srmsUrl % (self.__courseFullName, self.__courseYear, self.__semesterNumber)

        try:
            reader = urlopen(srmsUrl, proxies={}).read()
            if reader is not None and reader.strip() != "":
                if str(reader).find("not found on this server")>-1:
                     return "Product Ref or Access Error", prod_ref
                prodXml = self.__xml(reader)
                srmsObject = SRMSObject(prodXml, self.requestType, direct_types)
                
                if self.requestType is not None and srmsObject is not None:
                    return "ok", srmsObject
            else:
                return "Product Ref Error", srmsObject
            return "ok", srmsObject
        except Exception, e:
            return "connection Fail when retrieving srms product reference", srmsObject
    
    def processAllReadingForSrms(self, srmsObject, printVersion=False):
        for key in srmsObject.prodRefList:
            moduleTitleList = {}
            readingListNumberToBeSorted = []
            readingListDict = {}
            duplicateReading = []
            availableReading = []
            xmlString = self.prodXmlData(key)
            requestObject = None
            if xmlString is not None:
                xml = self.iceContext.Xml(xmlString)
                requestNode = xml.getNode("//request")
                requestObject = RequestObject(requestNode, self.__rep.getAbsPath(".site"))
                readingNodes = xml.getNodes("//reading")
                for readingNode in readingNodes:
                    if readingNode.getAttribute("available") == "1":
                        readingObject = ReadingItem(readingNode, self.requestType, self.iceContext, printVersion=printVersion)
                        #get all the module number for this requestObject
                        readingNumber = readingObject.readingNumber
                        if readingNumber != "" and readingNumber is not None:
                            moduleNumber = readingObject.moduleNumber
                            if readingObject.alternative is None:
                                availableReading.append(readingNumber)
                            else:
                                if not readingObject.alternative.isInAnotherPrinting:
                                    availableReading.append(readingNumber)
                            if moduleNumber!=0 and not moduleTitleList.has_key(moduleNumber):
                                moduleTitleList[moduleNumber] = self.__getModuleTitle(moduleNumber)
                            if readingNumber not in readingListNumberToBeSorted:
                                readingListNumberToBeSorted.append(readingNumber)
                                readingListDict[readingNumber] = readingObject
                            else:
                                #check for duplicate reading
                                duplicateReading.append(readingNumber)
                
                
                xml.close()
            if requestObject:
                requestObject.availableReading = self.sort(availableReading)
                requestObject.readingListDict = readingListDict
                requestObject.moduleTitleList = moduleTitleList
                requestObject.sortedReadingNumber = self.sort(readingListNumberToBeSorted)
                requestObject.duplicateReading = self.sort(duplicateReading)
                srmsObject.requestObjectList.append(requestObject)
#            srmsList[requestObject.requestObject.prodRef] = requestObject
                
        return srmsObject
        
    def prodXmlData(self, prodRef):
        directUrl = "http://ereserveweb-prod2.usq.edu.au:8089/services/export/ice.php?prod_ref=%s&cycle_id=%s" % (prodRef, self.__cycleId)
        #directUrl = "http://usqdirect.usq.edu.au:8089/services/export/ice_2.php?prod_ref=%s&cycle_id=%s" % (prodRef, self.__cycleId)
        #print 'directUrl: ', directUrl
        try:
            reader = urlopen(directUrl, proxies={}).read()
            if reader is not None and reader.strip() != "" and reader.strip().find("No results returned!")==-1:
                return reader
            return None
        except Exception, e:
            return "connection Fail when retrieving reading list for prod_ref: " % prodRef
        
    def __getModuleTitle(self, moduleNumber):

        moduleTitle = ""
        moduleFileName = self.__checkifModuleFileExist(moduleNumber)

        if moduleFileName:
            tempDir = self.__fs.unzipToTempDirectory(self.__fs.absolutePath(moduleFileName))
            meta = self.__fs.readFile(tempDir.absolutePath("meta.xml"))
            metaXml = self.__xml(meta, OONS)
            dcTitle = metaXml.getNode("//dc:title")
            if isNotEmpty(dcTitle):
                moduleTitle = dcTitle.getContent()
            else:
                moduleTitle = "[Untitled]"
            metaXml.close()
            tempDir.delete()
            return moduleTitle
        return "Module %s not exist in study_modules folder" % moduleNumber

    def __checkifModuleFileExist(self, moduleNumber):
        moduleFilePath = "%s/study_modules" % (self.__rep.getAbsPath(self.__packagePath).rstrip("/"))
        moduleFileName = "%s/module0%s.odt" % (moduleFilePath, moduleNumber)

        if self.__fs.isFile(moduleFileName):
            return moduleFileName

        moduleFileName = "%s/module%s.odt" % (moduleFilePath, moduleNumber)
        if self.__fs.isFile(moduleFileName):
            return moduleFileName

        moduleFileName = "%s/module_0%s.odt" % (moduleFilePath, moduleNumber)
        if self.__fs.isFile(moduleFileName):
            return moduleFileName

        moduleFileName = "%s/module_%s.odt" % (moduleFilePath, moduleNumber)
        if self.__fs.isFile(moduleFileName):
            return moduleFileName

        return None
    
    def sort(self, lists=[]):
        if lists != []:
            for i in range(0, len(lists)):
                l = lists[i]
                for j in range(i+1, len(lists)):
                    if i<len(lists)-1:
                        l2 = lists[j]
                        l, l2 = self.__swap(l, l2)
                        lists[i] = l
                        lists[j] = l2
        return lists

    def __breakNumberChar(self, l):
        char=""
        digit=""
        for i in range(len(l)):
            if l[i].isdigit():
                digit = "%s%s" % (digit, l[i])
            else:
                char = "%s%s" % (char, l[i])
        return digit, char

    def __breakNumber (self, l):
        la = 0
        lb = 0
        lc = ""
        if l.find(".")>0:
            #Need to process 1.1a, 1.1b
            la, lb = l.split(".")
            lb, lc = self.__breakNumberChar(lb)
        else:
            #Need to process 1a, 1b
            lb, lc = self.__breakNumberChar(l)

        return (la, lb, lc)

    def __swap(self, l, l2):
        
        la, lb, lc = self.__breakNumber(l)
        l2a, l2b, l2c = self.__breakNumber(l2)
        if int(la)>int(l2a):
            temp = str(l)
            l = str(l2)
            l2 = str(temp)
        elif int(la)==int(l2a):
            if int(lb)>int(l2b):
                temp = str(l)
                l = str(l2)
                l2 = str(temp)
            elif int(lb)==int(l2b) and lc != '' and l2c != '':
                if lc>l2c:
                    temp = str(l)
                    l = str(l2)
                    l2 = str(temp)
            elif int(lb)==int(l2b) and lc != '' and l2c == '':
                temp = str(l)
                l = str(l2)
                l2 = str(temp)

        return l, l2
    
    def createStyle(self, contentXml):
        #Create new page style to support page break before
        officeAutomaticSytle = contentXml.getNode("//office:automatic-styles")
        lastChild = None
        if officeAutomaticSytle:
            children = officeAutomaticSytle.getChildren()
            if children:
                lastChild = officeAutomaticSytle.getLastChild()

        newPageBreakStyle = contentXml.createElement("style:style")
        newPageBreakStyle.setAttribute("style:name", "newPage")
        newPageBreakStyle.setAttribute("style:family", "paragraph")
        newPageBreakStyle.setAttribute("style:parent-style-name", "Standard")

        newStyleParaProp = contentXml.createElement("style:paragraph-properties")
        newStyleParaProp.setAttribute("fo:break-before", "page")
        newPageBreakStyle.addChild(newStyleParaProp)

        if lastChild:
            lastChild.addNextSibling(newPageBreakStyle)
        else:
            officeAutomaticSytle.addChild(newPageBreakStyle)
            lastChild = newPageBreakStyle

        newTextStyle = contentXml.createElement("style:style")
        newTextStyle.setAttribute("style:name", "copyright")
        newTextStyle.setAttribute("style:family", "text")

        newTextStyleProp = contentXml.createElement("style:text-properties")
        newTextStyleProp.setAttribute("fo:font-size", "9pt")
        newTextStyleProp.setAttribute("fo:font-size-asian", "9pt")
        newTextStyleProp.setAttribute("fo:font-size-complex", "9pt")
        newTextStyle.addChild(newTextStyleProp)
        lastChild.addNextSibling(newTextStyle)
        lastChild = newTextStyle

        newAltStyle = contentXml.createElement("style:style")
        newAltStyle.setAttribute("style:name", "alternatives")
        newAltStyle.setAttribute("style:family", "text")

        newAltStyleProp = contentXml.createElement("style:text-properties")
        newAltStyleProp.setAttribute("fo:font-size", "10pt")
        newAltStyleProp.setAttribute("fo:font-size-asian", "10pt")
        newAltStyleProp.setAttribute("fo:font-size-complex", "10pt")
        newAltStyle.addChild(newAltStyleProp)
        lastChild.addNextSibling(newAltStyle)
        lastChild = newAltStyle

        return contentXml

    def createModuleHeader(self, moduleTitleStr, contentXml):
        moduleTitleNode = contentXml.createElement("text:p")
        moduleTitleNode.setAttribute("text:style-name", "h1")
        moduleTitleNode.setContent(moduleTitleStr)
        return moduleTitleNode


    def generateListError(self, copyRightErrorList, title, warning=False):
        html = "<div><div style='font-weight:bold;text-align:left;padding: 2px;'><b>%s:</b></div><ul>" % title
        for list in copyRightErrorList:
            if warning:
                html += "<li>%s</li>" % list
            else:
                html += "<li>Reading number: %s</li>" % list
        html += "</ul></div>"
        return html
    
    def generateCopyRightErrorStatus (self, errorDict, title, list):
        html = "<div><div style='font-weight:bold;text-align:left;padding: 2px;'><b>%s:</b></div><ul>" % title
        if list != []:
            for number in list:
                reason = errorDict[number]
                html += "<li>Reading number: %s, reason: %s</li>" % (number, reason)
            html += "</ul></div>"
            return html
        return ""
    
    def generateFileError(self, errorDict, title):
        html = "<div><div style='font-weight:bold;text-align:left;padding: 2px;'><b>%s:</b></div><ul>" % title
        for readingNumber in errorDict:
            files = errorDict[readingNumber]
            if len(files)==1:
                html += "<li>Reading number: %s: %s </li>" % (readingNumber, files[0])
            else:
               html += "<li>Reading number: %s: <ul>" % (readingNumber)
               files = errorDict[readingNumber]
               for file in files:
                   html += "<li>%s</li>" % file
               html += "</ul></li>"
        html += "</ul></div>"
        return html
    
    def message(self, err):
        if err == "" or err=="ok":
            errStr = "Successfully generated <a href='%s/selected_readings'>selected readings</a>" % self.__packagePath
        elif err == "Fail":
            errStr = "Failed to generate selected readings list"
        elif err.find("No Reading")>-1:
            errStr = "There is no list of readings for this course"
        elif err.find("Product Ref Error")>-1:
            errStr = "(Product Reference error)<br/>There are no readings in USQDiReCt with the information you have provided.<br/>Please check course code, semester and course delivery method."
        elif err.find("Product Ref or Access Error")>-1:
            errStr = "(Product Reference error)<br/>There is no result returned from USQDiReCt.<br/>Please check course code, semester and course delivery method OR you may not have access to USQDiReCt."
        elif err.find("Template not found")>-1:
            errStr = "There is no list_of_readings.odt template file found in skin/templates folder"
        elif err.find("Book template not found")>-1:
            errStr = "There is no list_of_readingsBook.odt template file found in skin/templates folder"
        elif err.find("File exist")>-1:
            errStr = "list_of_readings.odt file already exists, Prompt for replacement"
        elif err.find("Cannot add SRMS")>-1:
            errStr = "Cannot add new SRMS to Print SR Book, only single file is allowed"
        else:
            errStr = err
        return "<div>CourseName: %s, year: %s, semester: %s, semesterNumber: %s, " \
               "Request Type: %s<br/><b>%s</b></div>" % \
               (self.__courseFullName, self.__courseYear, self.__semester, self.__semesterNumber, self.requestType, errStr)
    
    def addCopyrightPage(self, file, pdfFilePath, copyrightPagePdf):
        if not self.__fs.isFile(copyrightPagePdf):
            return False
        
        #tempName = pdfFilePath.replace(file, "temp.pdf")
        tempName = self.__fs.join(self.__fs.splitPathFileExt(pdfFilePath)[0], "temp.pdf")
        
        pdfUtilClass = self.iceContext.getPlugin("ice.pdfUtils").pluginClass(self.__fs)
        pdfWriter = pdfUtilClass.pdfWriter(tempName)

        pdfReader = pdfUtilClass.pdfReader()
        copyRightReader = pdfReader.createPdfReader(copyrightPagePdf)
        pdfWriter.addPage(copyRightReader.getPage(0))

        pdfReader2 = pdfUtilClass.pdfReader()
        pdfFileReader = pdfReader2.createPdfReader(pdfFilePath)
        for pageNum in range(pdfReader2.numOfPages):
            pdfWriter.addPage(pdfFileReader.getPage(pageNum))
            
        pdfWriter.savePdf()
        pdfReader.close()
        pdfReader2.close()
        try:
            self.__fs.delete(pdfFilePath)
            self.__fs.move(tempName, pdfFilePath)
        except:
            pass
        
        return True
      
    def testDownload(self, exportPath):
        username = self.iceContext.session.username
        exportUrl = "%s%s" % (exportPath, username)
        try:
            import tempfile
            print 'test download...%s' % exportUrl
            tempDirectory = tempfile.gettempdir()
            downloadPath = "%s/download.pdf" % tempDirectory.rstrip("/") 
            
            #urlretrieve(exportUrl, filename=downloadPath)
            
            file = open(downloadPath, "wb")
            retrieve = urllib2.urlopen(exportUrl)
            file.write(retrieve.read())
            file.close()
            
            if self.iceContext.fs.exists(downloadPath):
                return not self.__isValidPdfFile(downloadPath)
            else:
                return False
        except Exception, e:
            return False
        
    def __isValidPdfFile(self, pdfFileNeedToBeTested=None):
        downloadedFilePath = pdfFileNeedToBeTested
        if downloadedFilePath:
            #check for EOF
            pdfReaderUtil = self.pdfUtilClass.pdfReader()
            pdfReader = pdfReaderUtil.createPdfReader(downloadedFilePath)
            isInValid = True
            if pdfReader is not None:
                isInValid = False
                pdfReaderUtil.close()
            else:
                #this is invalid with no %EOF, try to fix it
                pdfReaderUtil.close()
                fixed = self.pdfUtilClass.fixPdf(self.downloadedFilePath)
                if fixed=="Fixed":
                    #try to reopen the pdf
                    pdfReader = pdfReaderUtil.createPdfReader(self.downloadedFilePath)
                    if pdfReader is not None:
                        isInValid = False
                    pdfReaderUtil.close()
            return isInValid
        else:
            return False
