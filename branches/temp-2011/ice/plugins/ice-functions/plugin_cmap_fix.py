
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

""" 
CMAP plugin to fix the CMAP HTML
"""

pluginName = "ice.function.cmap"
pluginDesc = "Fix CMAP HTML"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized,HtmlTemplate
    pluginFunc = fixCmap
    pluginClass = None  
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    HtmlTemplate = iceContext.fs.join(path, "cmap.tmpl")
    iceContext.ajaxHandlers["cmap"] = ajaxCallback
    return pluginFunc

def displayIf(self):
    """
    return whether to display in the toolbar or not
    @return:boolean
    @rtype:boolean
    """
    return self.iceContext.settings.get("enablecmap", False)
def ajaxCallback(iceContext):
 
#    print "Cmap ajaxCallBack"
    resultData = "<div>done</div>"
    requestData = iceContext.requestData
    fileStr= requestData.value("files", "")
    findStr = requestData.value("findStrs", "")
    replaceStr = requestData.value("replaceStrs", "")
    findStrs = []
    replaceStrs = []
    files = []
    
    #fixing the string.
    fileStr = fileStr[1:-1]
    files = fileStr.split(",")
    
    findStr=findStr[1:-1]
    findStrs = findStr.split(",")

    replaceStr = replaceStr[1:-1]
    replaceStrs = replaceStr.split(",")
    
#    print "files:",files
#    print "findStrs:",findStrs
#    print "replaceStrs:", replaceStrs
    if files==[] or findStrs==[] or replaceStrs==[]:
        return resultData,False
    success = True
    processedFiles = []
    for file in files:
        #convert url to the file path. 
        file = file.strip()
        file = file.replace(iceContext.siteBaseUrl,"").replace(iceContext.urlRoot.lstrip("//"),"")
        file = file.replace("\\","/").replace("'","")
        #for return data
        if file.find(iceContext.path.lstrip("//"))==-1:
            file = iceContext.path+file
        file = iceContext.siteBaseUrl.lstrip("//")+iceContext.urlRoot.lstrip("//")+file.lstrip("//")
        processedFiles.append(file)
        
        file = file.replace(iceContext.siteBaseUrl,"").replace(iceContext.urlRoot.lstrip("//"),"")
        file = file.replace("\\","/").replace("'","")        
        file = iceContext.rep.getAbsPath(file)
        if not iceContext.fs.exists(file):
            print "file does not exists. Aborting..."
            return "",False
        success = success and replaceImageLink(iceContext,file,findStrs,replaceStrs) 
    if success:
        #return which files and urls for jquery proceessing 
        data = "(%s,%s)" % (processedFiles,findStrs)
        return data,success
    else:
        return "",False
    

def replaceImageLink(iceContext,file,findStrs,replaceStrs):
    """
    Find and replace the href and image src in the html.
    @param file,findStrs,replaceStrs
    @type string
    @return success
    @rtype: boolean
    """
    #assume data is clean now. and local href is correct as well
    
    #print "replace Image links"
    data = iceContext.fs.readFile(file)
    data = iceContext.HtmlCleanup.cleanup(data)
    xml = iceContext.Xml(data)
    for i in range(len(findStrs)):
        findStr = findStrs[i]
        replaceStr = replaceStrs[i].strip()
        
#        print findStr
#        print replaceStr
        if findStr =="undefined" or replaceStr=="undefined":
            continue
        aNodes = xml.getNodes("//a[@href='%s']"%findStr)
        
        if aNodes != []:
            for a in aNodes:
                a.setAttribute("href",replaceStr)
                
        imgNodes = xml.getNodes("//img[@src='%s']"%findStr)
        if imgNodes != []:
            for img in imgNodes:
                #assume that the import is correct
                img.setAttribute("src",replaceStr)
    xml.saveFile()
    data = str(xml)
    iceContext.fs.writeFile(file,data)
    xml.close()
    return True
    
    
    
        
        
def fixCmap(self):
    """
    Function called from the toolbar to fix CMAP HTML.
    This looks for CMAP html files and fix the html for ICE rendition.
    """
    self.__rep = self.iceContext.rep
    self.__fs = self.iceContext.fs
    
    #### get the url from ice context 
    cmapDirPath = self.__rep.getAbsPath(self.iceContext.path)
    cmapDirUrl = self.iceContext.siteBaseUrl +self.iceContext.urlRoot.lstrip("//") +self.iceContext.path.lstrip("//") 
    ##### assume all html files are cmap files
    def callback(path, dirs, files):
        for file in files:
            if file.endswith("html") or file.endswith("htm"):
                listOfFiles.append(path + file)
    listOfFiles = []
    self.iceContext.fs.walker(cmapDirPath, callback)
    hasInvalidLinks = False
    filesWithInvalidLinks = {}
    d = {}
    cmapFileCount = 0
    if listOfFiles != []:
        cmapObj = Cmap(self.iceContext)
        for file in listOfFiles:
            data = self.__fs.readFile(file)
            if data.find("IHMC CmapTools") != -1:
                cmapFileCount = cmapFileCount + 1
                filepath, fileName = self.__fs.split(file)
                fileLocs = filepath.split(self.iceContext.path.lstrip("//"))
                url = cmapDirUrl
                if len(fileLocs)>1:
                    url = url + fileLocs[1]
                data,invalidHrefs = cmapObj.cleanupCmap(data,url)
                if invalidHrefs != []:
                    if not url.endswith("/"):
                        url = url + "/"
                    fileUrl = url + fileName
                    filesWithInvalidLinks[fileUrl] = [fileName,invalidHrefs]
                self.__fs.writeFile(file,data)
    
    hrefs={}
    for key in filesWithInvalidLinks:
        #create the dict with href as key
        for href in filesWithInvalidLinks[key][1]:
            if not href in hrefs:
                hrefs[href]=[[filesWithInvalidLinks[key][0],key]]
            else:
                if not filesWithInvalidLinks[key][0] in hrefs[href]:
                    hrefs[href].append([filesWithInvalidLinks[key][0],key])

    if cmapFileCount == 0:
        d["result"] = "No CMAP HTML file found."
        d["success"] = True
    else:
        if filesWithInvalidLinks !={}:
            hasInvalidLinks = True
            d["hrefs"]=hrefs # for links sorting
            d["filesWithInvalidLinks"]=filesWithInvalidLinks #for each file
            d["result"] = "Found %s file(s) and CMAP File(s) have following Invalid Link(s)." % cmapFileCount
            d["success"] = False
        else:
            d["result"] = "Found %s file(s) and CMAP HTML has been fixed." % cmapFileCount
            d["success"] = True
    
    
    htmlTemplate = self.iceContext.HtmlTemplate(HtmlTemplate)
    self.body = htmlTemplate.transform(d,allowMissing=True)
    
fixCmap.options = {"toolBarGroup":"advanced", "position":1000, "postRequired":True,
                "label":"Fix CMAP HTML", "title":"Fix CMAP HTML in this folder", "displayIf":displayIf}


class Cmap(object):
    """ Base CMAP class"""
    def __init__(self,iceContext):
        """CMAP Constructor method"""
        self.iceContext = iceContext
            
    def cleanupCmap(self,html,cmapDirPath):
        """
        main method to cleanup CMAP HTML
        @param html: html from the file that needs cleans up
        @type html:String
        @param cmapDirPath:File location path.
        @type cmapDirPath : String
        @return htmlresult, invalidHrefs
        @rtype (String,list)
        """
        # assume this meta data will always generated. If not, ....
        #  <meta NAME = "GENERATOR" CONTENT = "IHMC CmapTools vr. 4.12 ">
        if html.find("IHMC CmapTools") != -1:
            #put back the divs inside HTML.
            htmlresult = self.__putInvalidDivToBody(html)
             
            #cleaning up the html
            htmlresult = self.iceContext.HtmlCleanup.cleanup(htmlresult)
            htmlresult = self.__cleanupHTML(htmlresult)
       
            xml = self.iceContext.Xml(htmlresult)
            
            xml = self.__cleanupCapitalName(xml) #cmap html has mixed lower and upper characterfs for elements
            
            #fix up html links
            xml, invalidHrefs = self.__cleanupImageLink(xml,cmapDirPath)
            htmlresult = str(xml)
            htmlresult = self.__cleanupHTML(htmlresult)
            xml.close()
        return htmlresult, invalidHrefs
    
    def __cleanupHTML(self,html):
        """
        Method to cleanup HTML tags that cause the parser errror
        @param html:html from the file
        @type html : String
        @rtype String
        @return html
        """
        html = html.replace("""<meta content="text/html; charset=utf-8 http-equiv=" content-type="">""", "")
        html = html.replace("""<meta content="text/html; charset=utf-8 http-equiv="Content-Type"/>""","")
        html = html.replace("""<?xml version="1.0"?>""", "")
        return html
    
    def __notEmpty(self, node):
        """
        return if the node is empty or not
        @rtype : boolean
        """
        return node is not None or node != [] or node != {} 
    
    def __cleanUpAttribute(self, node):
        """
        @param node:Element Node
        @type node:Element
        @rtype Element
        @return node
        """
        attrs = node.getAttributes()
        if self.__notEmpty(attrs):
            for key in attrs:
                attrVal = attrs[key]
                node.removeAttribute(key)
                node.setAttribute(key.lower(), attrVal)
        return node
    
    def __cleanupCapitalName(self, xml):
        """
        @param xml: xml 
        @type xml:xml dom
        @rtype: xml dom
        """
        xml = self.__cleanUpAttribute(xml)
        children = xml.getChildren()
        if self.__notEmpty(children):
            for child in children:
                if child.getName() != None: # to skip the javascript. which is commented for html parser
                    child = self.__cleanUpAttribute(child)
                    child.setName(child.getName().lower())
                    if self.__notEmpty(child.getChildren()):
                        self.__cleanupCapitalName(child)
        else:
            xml.setName(xml.getName().lower())
        return xml

        
    def __putInvalidDivToBody(self,html):
        """
        put back cmap divs inside body node
        @type html: String
        @rtype String
        """
        htmlTag = html
        #in case cmap is using capital letter
        htmlString  = html.replace("</HTML>","</html>").replace("</BODY>","</body>")
        htmlArray = htmlString.split("</html>")
        if (len(htmlArray)==2):
            divTag = htmlArray[1].strip()
            if divTag != "":
                htmlTag = htmlArray[0].replace("</body>", "")
                htmlTag = "%s%s</body></html>" % (htmlTag, divTag)
                
                #### fix up java script so cmap will be displayed in firefox
                htmlTag = self.__fixCmapJs(htmlTag)
        return htmlTag
    
    def __cleanupImageLink(self,xml,cmapDirPath):
        """
        Fix image and href links in the html to absolute path
        !@param: xml,cmapDirPath 
        @type xml: xml dom
        @type cmapDirPath:String
        @rtype:(xml dom,list)
        @return xml,inValidHrefs
        """
        inValidHrefs = []
        if not cmapDirPath.endswith("/"):
            cmapDirPath =cmapDirPath+"/"
        aHrefs = xml.getNodes("//a[@href != '']")
        for a in aHrefs:
            href =a.getAttribute("href").strip()
            if (href == "" or href.find("../") != -1 or href.find("./")!= -1) and not href in inValidHrefs:
                inValidHrefs.append(href)
            elif href.find("http://") == -1 and href.find("https://") == -1 and href.find("./")==-1:
                a.setAttribute("href",cmapDirPath+href.strip())
        imgNodes = xml.getNodes("//img[@src != '']")
        for img in imgNodes:
            imgSrc =img.getAttribute("src").strip()
            if (imgSrc =="" or imgSrc.find("../") != -1 or imgSrc.find("./")!= -1) and not imgSrc in inValidHrefs:
                inValidHrefs.append(imgSrc)
            elif imgSrc.find("http://") == -1 and imgSrc.find("https://") == -1 and imgSrc.find("./")==-1:
                img.setAttribute("src",cmapDirPath+imgSrc.strip())
        return xml,inValidHrefs
    
    def checkInvalidHrefs(self,xml):
        inValidHrefs = []
        aHrefs = xml.getNodes("//a[@href != '']")
        for a in aHrefs:
            href =a.getAttribute("href").strip()
            if (href == "" or href.find("../") != -1 or href.find("./")!= -1) and not href in inValidHrefs:
                inValidHrefs.append(href)
        imgNodes = xml.getNodes("//img[@src != '']")
        for img in imgNodes:
            imgSrc =img.getAttribute("src").strip()
            if (imgSrc =="" or imgSrc.find("../") != -1 or imgSrc.find("./")!= -1) and not imgSrc in inValidHrefs:
                inValidHrefs.append(imgSrc)
        return inValidHrefs
    
    def __fixCmapJs(self, html):
        """
        fix cmap javascript for firefox
        @param html: html
        @type html: String
        @rtype: String
        """
        # tobe fixed as such
#        document.getElementById(popupName).style.left = event.layerX+"px";
#        document.getElementById(popupName).style.top = event.layerY+"px";
        html = html.replace("document.getElementById(popupName).style.left = event.layerX;", "document.getElementById(popupName).style.left = event.layerX + 'px';")
        html = html.replace("document.getElementById(popupName).style.top = event.layerY;", "document.getElementById(popupName).style.top = event.layerY + 'px';")
        return html
    
