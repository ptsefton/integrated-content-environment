
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


pluginName = "ice.ooo.WordDownConverter"
pluginDesc = "WordDownConverter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OOoConverter
    pluginInitialized = True
    return pluginFunc



class OOoConverter(object):
    defaultHtmlTemplate = """<html>
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

    #htmlTemplate = OOoConverter.defaultHtmlTemplate

    
    def __init__(self, iceContext, fs=None, htmlTemplate=None):
        self.iceContext = iceContext
        self.__output = iceContext.output
        self.__oooConverter = self.iceContext.getOooConverter()
        
        # .odt
        OdtConvert = iceContext.getPlugin("ice.render.odtConverter").pluginClass
        odtConvert = OdtConvert(self.iceContext)
        self.__odtRenderMethod = odtConvert.renderMethod
        
        # .doc
        DocConvert = iceContext.getPlugin("ice.render.docConverter").pluginClass
        docConvert = DocConvert(self.iceContext)
        self.__docRenderMethod = docConvert.renderMethod

        #.docx
        DocxConvert = iceContext.getPlugin("ice.render.docxConverter").pluginClass
        docxConvert = DocxConvert(self.iceContext)
        self.__docxRenderMethod = docxConvert.renderMethod
        
        if htmlTemplate is None:
            htmlTemplate = self.defaultHtmlTemplate
        self.__htmlTemplate = htmlTemplate
        if fs is None:
            fs = iceContext.fs.createTempDirectory(persist=False)
        self.__fs = fs
        self.__skinFs = iceContext.FileSystem("fake.skin")
        self.rep = None

    
    def convert(self, file, toDir, options={}):
        path, name, ext = self.__fs.splitPathFileExt(file)
        ext = ext.lower()
        # if __rep is set in options, it is an internal call
        self.rep = options.get("__rep", None)
        
        item = None
        sourcelink = self.__getOptionValue(options, "sourcelink")
        if self.rep is not None:
            argPath = options.get("argPath")
            item = self.rep.getItemForUri(argPath)
            file = item.relPath
        
        
        
        if ext==".odt":
            convertedData = self.__render(file, self.__odtRenderMethod, self.__output, self.rep)
        elif ext==".doc" or ext==".rtf":
            convertedData = self.__render(file, self.__docRenderMethod, self.__output, self.rep)
            tempOdtFile = convertedData.abspath("temp.odt")
            self.__fs.copy(tempOdtFile, self.__fs.join(path, name + ".odt"))
        elif ext == ".docx":
            convertedData = self.__render(file, self.__docxRenderMethod, self.__output, self.rep)
            tempOdtFile = convertedData.abspath("temp.odt")
            self.__fs.copy(tempOdtFile, self.__fs.join(path, name + ".odt"))
        else:
            return ("Unsupported file extension '%s'." % ext, None, None)
        
        toDir = self.__fs.absolutePath(toDir)
        supportDirName = "%s_files" % name
        supportDir = self.__fs.join(toDir, supportDirName)
        self.__fs.makeDirectory(toDir)
        self.__fs.makeDirectory(supportDir)
        pdfFile = self.__fs.join(toDir, name + ".pdf")
        
        htmlFile = self.__fs.join(toDir, name + ".htm")
        for imageName in convertedData.imageNames:
            convertedData.saveImageTo(imageName, supportDir)
        
        
        includeSkin= self.__getOptionValue(options, "includeSkin")
        includetitle = self.__getOptionValue(options,"includetitle")

        if includetitle:   
            title = convertedData.getMeta("title")
        else:
            title = " "
        if title.strip() == "":
            if item is not None:
                title = item.getMeta("title")
            else:
                title = options.get("title"," ")
        self.title = title
        
        self.meta = convertedData.meta
        style = convertedData.getMeta("style.css")
        body = convertedData.getRendition(".xhtml.body")
        
        toc = self.__getOptionValue(options, "toc")
        if toc:  
            pageToc = convertedData.getMeta("toc")
	    if pageToc == "<ul/>":
		toc = pageToc=""
        else:
            pageToc = ""
            
        slideFileName = "%s.slide.htm" % name
        slideFile = self.__fs.join(toDir, slideFileName)
        slideLink = self.__getOptionValue(options, "slidelink")
        
        pdfLink = self.__getOptionValue(options, "pdflink")
        
        if sourcelink:
            sourceLink = "<a href='%s' title='View the original document'>Source</a>" % (name + ext)
            if ext == ".doc":
                # include the generated odt for word docs
                sourceLink += " | <a href='%s' title='View the derived ODT'>Derived ODT</a>" % (name + ".odt")
            if slideLink or pdfLink:
                sourceLink += " | "
        else:
            sourceLink = ""
            self.__fs.delete(self.__fs.join(path, name + ".odt"))
            if ext == ".doc" or ext==".docx":
                self.__fs.delete(file)
        slideRendition = ""
        if slideLink:
            slideRendition = "<a href='%s' title='View presentation'>Slides</a>" % slideFileName
            if pdfLink:
                slideRendition += " | "
        pdfRendition = ""
        if pdfLink:
            convertedData.saveRenditionTo(".pdf", pdfFile)
            # target='_blank' alt='PDF version'
            pdfRendition = "<a href='%s' title='View the printable version of this page'>PDF version</a>" % (name + ".pdf")
        dataDict = {"title":title, "style-css":style, "page-toc":pageToc, "body":body,
                    "pdf-rendition-link":pdfRendition, "source-link":sourceLink,
                    "slide-link":slideRendition, "annotations":"<!--No annotations-->",
                    "toolbar": "<!--No toolbar-->"}
        
        
        html = self.__applyHtmlTemplate(self.__htmlTemplate, dataDict)
        if self.rep is not None:
            # process media objects
            basePath = self.__fs.split(file)[0]
            links = convertedData.getMeta('links')
            for link in links:
                linkPath = link[0].strip()
                if not linkPath.startswith("#"):
                    absLinkPath = self.rep.getAbsPath(self.__fs.join(basePath, linkPath))
                    path, linkName, linkExt = self.__fs.splitPathFileExt(linkPath)
                    linkFileName = linkName + linkExt
                    if linkPath.find(".swf")!=-1:
                        #for video files
                        def copySWFs(path, dirs, files):
                            for file in files:
                                if file.endswith("swf"):
                                    filePath = self.__fs.join(path,file)
                                    self.__copyFile(filePath,supportDir)
                                    
                                    
                        self.__fs.walker(self.rep.getAbsPath(self.__fs.join(basePath, path)),copySWFs)
                        html = html.replace(linkPath, self.__fs.join(supportDirName, linkFileName))

                    elif linkPath.find("localhost")!=-1:
                        self.__copyFile(absLinkPath,supportDir)
                        html = html.replace(linkPath, self.__fs.join(supportDirName, linkFileName))
                    elif linkPath.find("../")!=-1:
                        #for cmap image links
                        if self.__fs.exists(absLinkPath):
                            self.__copyFile(absLinkPath,supportDir)
                            html = html.replace(linkPath, self.__fs.join(supportDirName, linkFileName))
                if link[1] is not None or link[1] != "":
                    if link[1].find("embed&amp;media=")!=-1:
                        #if there is audio or video files
                        startPoint =link[1].find("embed&amp;media=") + 16
                        endPoint = link[1].find("&amp;",startPoint)
                        linkFileName = link[1][startPoint:endPoint]
                        linkPath = self.__fs.join(path,linkFileName)
                        absLinkPath = self.rep.getAbsPath(self.__fs.join(basePath, linkPath))
                        if self.__fs.exists(absLinkPath):
                            self.__copyFile(absLinkPath,supportDir)
                            
            
                        
            #embeded Links (CMAP)
            if html is not None:
                xml = self.iceContext.Xml(html)
                imgNodes = xml.getNodes("//*[local-name()='img']")
                if imgNodes != []:
                    for img in imgNodes:
                        imgSrc = img.getAttribute("src")
                        imgFileName =self.__fs.split(imgSrc)[1]
                       
                        if imgSrc.find(supportDirName)==-1:
                            imgPath = self.rep.getAbsPath(self.__fs.join(basePath, imgSrc))
                            
                            if self.__fs.exists(imgPath) and imgSrc.find("skin") ==-1:
                                #self.__fs.copy(imgPath, self.__fs.join(supportDir, imgFileName))
                                self.__copyFile(imgPath,supportDir)
                                img.setAttribute("src",self.__fs.join(supportDirName, imgFileName))
                            elif html.find("JmolApplet.jar"):
                                #if CML
                                editThis = False
                                if imgSrc.find("http://")!= -1:
                                    isLocal =  self.iceContext.isLocalUrl(imgSrc)
                                    #do to find out how to check the local url
                                    if isLocal:
                                        editThis = True
                                        imgSrc = imgSrc.replace(self.iceContext.siteBaseUrl,"").replace(self.iceContext.urlRoot.lstrip("//"),"")
                                else:
                                    editThis = True
                                if editThis:
                                    path, name,ext = self.__fs.splitPathFileExt(imgSrc)
                                    imageExist = False
                                    fileName = name
                                    
                                    imgPath = self.rep.getAbsPath(self.__fs.join(basePath,"%s/.ice/%s/rendition%s"%(path,fileName,ext)))
                                    if self.__fs.exists(imgPath):
                                        imageExist = True
                                    
                                    if not imageExist:
                                        fileName = name +".cml"
                                        #C:\cynthia\workspace\ice\downloads\latest\documentation\www\instructions\technical\cml\.ice\mol10.cml\rendition.png
                                        #C:\cynthia\workspace\ice\demonstration\abc\1234\s1\media\compound\.ice\mol9.cml\rendition.png
                                        imgPath = self.rep.getAbsPath(self.__fs.join(basePath,"%s/.ice/%s/rendition%s"%(path,fileName,ext)))
                                        if self.__fs.exists(imgPath):
                                            
                                            imageExist = True
                                    
                                    if imageExist:
                                        #destination = self.__fs.join(supportDir,"%s%s"%(name,ext))
                                        destination = supportDir
                                        self.__copyFile(imgPath,destination)
                                         
                                        img.setAttribute("src","%s/%s%s"%(supportDirName,name,ext))
                                        self.__fs.move(self.__fs.join(supportDir,"rendition%s"%(ext)),self.__fs.join(supportDir,"%s%s"%(name,ext)))
                                
                html = str(xml)
                xml.close()
                
            try:
                externalFiles = item.getMeta("externalFiles")
            except:
                externalFiles = []
            if externalFiles is not None and externalFiles != []:
                packagePath = self.iceContext.iceSite.packagePath
                for file in externalFiles:
                    oriFilePath = ""
                    if self.rep is not None:
                        oriFilePath = self.rep.getAbsPath(file)
                        if not self.__fs.exists(oriFilePath):
                            oriFilePath = self.__skinFs.absPath(file.replace("skin/", ""))
                    if oriFilePath.find(".ice")!=-1 and oriFilePath.find(packagePath)!=-1:
                        file = file.split(packagePath)[1]
                        #"/home/octalina/ICE/eresearch/packages/demonstration/media/compound/.ice/mol9.cml/rendition.png"
                        #"media/compound/mol9.png"
                        if file.find(".png")!=-1 and file.find(".cml"):
                            
                            file = file.replace(".cml", "").replace("/.ice", "").replace("/rendition", "")
                            #try to copy the applet file... JmolApplet.jar
                            jmolappletJarFile = self.iceContext.fs.splitPathFileExt(file)[0] + "/JmolApplet.jar"
                            jmolappletJar = self.iceContext.fs.join(packagePath.lstrip("/"), jmolappletJarFile)
                            jmolDest = self.__fs.join(toDir, jmolappletJarFile)
                            if self.rep is not None:
                                jmolAbsPath = self.rep.getAbsPath(jmolappletJar)
                                if self.iceContext.fs.isFile(jmolAbsPath):
                                    #self.__fs.copy(jmolAbsPath, jmolDest)
                                    self.__copyFile(jmolAbsPath, supportDir)
                                else:
                                    print 'JmolApplet.jar file not found'
                    if oriFilePath:
                        #to do test what is this for
                        destFileName = file.replace(packagePath, "").split("/")[-1]
                        destFileName = self.__fs.join(toDir, destFileName)
                        self.__fs.copy(oriFilePath, destFileName,[".svn"])
        
        if html.find("applet") and self.rep is not None:
            xml = self.iceContext.Xml(html)
            appletNodes = xml.getNodes("//*[local-name()='applet']")
            if appletNodes != []:
                for appletNode in appletNodes:
                    src = appletNode.getAttribute("archive")
                    if src.find("http://")==-1:
                        path ,fileName ,ext = self.__fs.splitPathFileExt(src)
                        path = self.rep.getAbsPath(self.__fs.join(basePath, path))
                        self.__copyFile(path,supportDir)
                        src = "%s/%s%s" %(supportDirName,fileName,ext)
                        appletNode.setAttribute("archive",src)
                        #jmol
                        paramNode = appletNode.getNode("*[local-name()='param' and @name='load']")
                        if paramNode is not None:
                            src = "%s/%s" %(supportDirName,paramNode.getAttribute("value").split("/")[-1])
                            paramNode.setAttribute("value",src)
                            
                        #if ggb
                        paramNode = appletNode.getNode("*[local-name()='param' and @name='filename']")
                        if paramNode is not None:
                            src = "%s/%s" %(supportDirName,paramNode.getAttribute("value").split("/")[-1])
                            paramNode.setAttribute("value",src)
                
            html = str(xml.getRootNode())
            xml.close()
        
        if not includeSkin:
            #lightbox and cml
            hasLightBox = False
            if html.find("package-root/skin/jquery.js")>-1:
                html = html.replace("package-root/skin/jquery.js", "%s/jquery.js" % supportDirName)
                #jquery = self.__skinFs.absPath("jquery.js")
                self.__copyFile("jquery.js",supportDir)
                #self.__fs.copy(jquery, "%s/jquery.js" % supportDir)
                
            if html.find("package-root/skin/fancyzoom/fancyzoom.js")>-1:
                html = html.replace("package-root/skin/fancyzoom", supportDirName)
                
                fancyzoomSupportDir = "%s/fancyzoom" % supportDir
                cssFile = "%s/fancyzoom.css" % fancyzoomSupportDir
                xml = self.iceContext.Xml(html)
                headNode = xml.getNode("/*[local-name()='html']/*[local-name()='head']")
                cssHrefNode = headNode.getNode("/*[local-name()='link' and @href='%s']" % cssFile)
                if headNode is not None and cssHrefNode is None:
                    cssNode = xml.createElement("link")
                    cssNode.setAttribute("class", "sub css")
                    cssNode.setAttribute("rel", "stylesheet")
                    cssNode.setAttribute("href", cssFile)
                    headNode.addChild(cssNode)
                
                #copy the css and the js
                fancyzoomDir = self.__skinFs.absPath("fancyzoom")
                self.__fs.copy(fancyzoomDir, supportDir,[".ice",".svn"])
                #self.__copyFile("fancyzoom", supportDir)            
                
                #get the original image file and copy to _files folder + fix the link
                ahrefLightBoxesNodes = xml.getNodes("//*[local-name()='a' and @class='lightbox']")
                for ahref in ahrefLightBoxesNodes:
                    href = ahref.getAttribute("href")
                    if href.startswith("#"):
                        href = href[1:]
                    #original Image path is in div based on the href
                    div = xml.getNode("//*[local-name()='div' and @id='%s']" % href)
                    if div is not None:
                        oriImage = div.getNode("./*[local-name()='img']")
                        if oriImage and self.rep is not None:
                            imageSrc = oriImage.getAttribute("src")
                            if imageSrc.rfind("/"):
                                imageName = imageSrc[imageSrc.rfind("/")+1:]
                            imageAbsPath = self.rep.getAbsPath(self.__fs.join("%s" % self.iceContext.iceSite.packagePath, "%s" % imageSrc))
                            self.__copyFile(imageAbsPath, supportDir)
                            #self.__fs.copy(imageAbsPath, "%s/%s" % (supportDir, imageName))
                            
                            #change the path of th esrc
                            oriImage.setAttribute("src", "%s/%s" % (supportDirName, imageName))
                
                html = str(xml.getRootNode())
                xml.close()
            
            
            
            #tooltip footnote
            if html.find('class="footnote"')>-1:
                defaultcssFile = "skin/default.css"
                xml = self.iceContext.Xml(html)
                headNode = xml.getNode("/*[local-name()='html']/*[local-name()='head']")
                cssHrefNode = headNode.getNode("/*[local-name()='link' and @href='%s']" % defaultcssFile)
                if cssHrefNode is None:
                    # if export single document
                    defaultcssFile = "skin/default.css"
                    cssHrefNode = headNode.getNode("/*[local-name()='link' and @href='%s']" % defaultcssFile)
                    
                if headNode is not None and cssHrefNode is None:
                    defaultcssFile = supportDirName + "/default.css"
                    cssNode = xml.createElement("link")
                    cssNode.setAttribute("class", "sub css")
                    cssNode.setAttribute("rel", "stylesheet")
                    cssNode.setAttribute("href", defaultcssFile)
                    headNode.addChild(cssNode)
                
                html = str(xml.getRootNode())
                xml.close()
                self.__copyFile(defaultcssFile,supportDir)
            
            
        else:
            skinDirName= "skin"
            skinDir = self.__fs.join(toDir, skinDirName)
            supportDirName = skinDirName
            supportDir = skinDir
            if not self.__fs.exists(skinDir):
                self.__fs.makeDirectory(skinDir) 
            if html.find("package-root/skin")>-1:
                html = html.replace("package-root/skin", skinDirName)
            
            
            def processCSSFile(destination):
                cssData = self.__fs.read(destination)
                if cssData is None:
                    found = -1
                    notFound = destination[destination.find("skin/"):]
                    print "**** Warning %s file not found" % notFound
                else:
                    found = cssData.find("url(")
                while found > -1:
                    #get the file name from the following
                    #url(blankLink_img.gif)
                    #@import url("faculty.css");
                    endFound = cssData.find(")",found+4)
                    fileName =cssData[found+4:endFound]
                    fileName = fileName.replace("\"","",2) # replace " if there is any in the name
                    
                    file ="skin/" + fileName
                    self.__copyFile(file,skinDir)
                    
                    if fileName.find(".css")!=-1:
                        destinationFile= self.__fs.join(skinDir,fileName)
                        processCSSFile(destinationFile)
                    found =cssData.find("url(",found+5)
                    
            #if it is to include skin copy the required items from skin folder.
            xml = self.iceContext.Xml(html)
            cssHrefNodes = xml.getNodes("//*[local-name()='head']/*[local-name()='link' and @rel='stylesheet']" )
            foundDefault = False
            if cssHrefNodes != []:
                for cssHrefNode in cssHrefNodes:
                    href = cssHrefNode.getAttribute("href")
                    if href.find("default.css")!=-1:
                        foundDefault = True
                    self.__copyFile(href,skinDir)
                    destination = self.__fs.join(skinDir,href.split("/")[-1])
                    #get the images from the css.
                    processCSSFile(destination)
            #copy default.css
            if not foundDefault:
                headNode = xml.getNode("//*[local-name()='head']")
                if headNode is not None:
                    defaultcssFile = "skin/default.css"
                    cssNode = xml.createElement("link")
                    cssNode.setAttribute("class", "sub css")
                    cssNode.setAttribute("rel", "stylesheet")
                    cssNode.setAttribute("href", defaultcssFile)
                    headNode.addChild(cssNode)
                    self.__copyFile(defaultcssFile,skinDir)
                    
                    destination = self.__fs.join(skinDir,"default.css")
                    processCSSFile(destination)
                    
            scriptNodes = xml.getNodes("//*[local-name()='script' and @src != '']")
            
            if scriptNodes != []:
                for scriptNode in scriptNodes:
                    src = scriptNode.getAttribute("src")
                    scriptNode.setAttribute("src","%s/%s"%(skinDirName,src.split("/")[-1]))
                    self.__copyFile(src,skinDir)
            
            bodyNode = xml.getNode("//*[local-name()='body']")
            if bodyNode != []:
                #check if there are input[@type='image']
                inputNodes = bodyNode.getNodes("//*[local-name()='input' and @type='image']")
                if inputNodes != []:
                    for inputNode in inputNodes:
                        self.__copyFile(inputNode.getAttribute('src'),skinDir)
#    
                imgNodes = bodyNode.getNodes("//*[local-name()='img' and contains(@src,'skin/')]")
                if imgNodes !=[]:
                    for imgNode in imgNodes:
                        self.__copyFile(imgNode.getAttribute('src'),skinDir)
            #hack to remove the breadCrumbs if the package title is not exist
            spanBreadcrumbs= xml.getNode("//*[local-name()='span' and @class='breadcrumbs']")
            if spanBreadcrumbs is not None:
                spanPackageTitle = spanBreadcrumbs.getNode("//*[local-name()='span' and @class='packagetitle']")
                if spanPackageTitle.getContent() =="" :
                    spanBreadcrumbs.getLastChild().remove()
                
            html = str(xml.getRootNode())
            bodyNode =xml.getNode("//*[local-name()='div' and @class='body']")
            if bodyNode is not None:
                body = str(bodyNode)
            xml.close()
        
        self.__fs.writeFile(htmlFile, html)    
        
        if slideLink:
            # process slides
            xml = self.iceContext.Xml(body)
            div = xml.createElement("div")
            slideNodes = xml.getNodes("//div[@class='slide']")
            slideCount = len(slideNodes)
            div.addChildren(slideNodes)
            slideTitle = convertedData.getMeta("title")
            slideBody = str(div)
            xml.close()
            dataDict.update({"body":slideBody, "title":slideTitle})
            slideSkinPath = self.__skinFs.absPath("slide")
            if self.rep is not None:
                slideTemplate = self.rep.getItem("/skin/slide/slide.xhtml").read()
                repSlideSkinPath = self.rep.getAbsPath("/skin/slide")
                if self.__fs.exists(repSlideSkinPath):
                    slideSkinPath = repSlideSkinPath
            else:
                slideTemplate = self.__skinFs.readFile("slide/slide.xhtml")
            slideHtml = self.__applyHtmlTemplate(slideTemplate, dataDict)
            # fix up skin links
            slideHtml = slideHtml.replace("package-root/.skin/slide/", "%s/" % supportDirName)
            slideHtml = slideHtml.replace("package-root/.skin/", "%s/" % supportDirName)
            slideHtml = slideHtml.replace("package-root/skin/slide/", "%s/" % supportDirName)
            slideHtml = slideHtml.replace("package-root/skin/", "%s/" % supportDirName)
            
            self.__fs.writeFile(slideFile, slideHtml)
            # copy supporting files
            self.__fs.copy(slideSkinPath, supportDir,[".svn"])
        
        convertedData.close()
        return "ok", htmlFile, pdfFile

    def __copyFile(self,src,supportDir):
        #copy the require files
        copyDir = False
        if self.__fs.exists(src) or self.__fs.isDirectory(src):
            source = src
            if self.__fs.isDirectory(source):
                copyDir = True
        else:
            if self.rep is None:
                if src.find("/")!= -1:
                    source = self.__skinFs.absPath(src.split("/")[-1])
                else:
                    source = self.__skinFs.absPath(src)
            else:
                source= self.rep.getAbsPath(src)
                if not self.__fs.exists(source):
                    #if there is no skin folder in the rep.i.e. using fake.skin
                    if src.find("/")!= -1:
                        if src.find("fancyzoom")==-1:
                            source = self.__skinFs.absPath(src.split("/")[-1])
                        if not self.__fs.exists(source):
                            #just in case of fancyzoom and other
                            copyDir = True
                            source = self.__skinFs.absPath(src.split("/")[-2])
                    else:
                        source = self.__skinFs.absPath(src)
                        if self.__fs.isDirectory(source):
                            copyDir = True
        if  copyDir:
#            destination = self.__fs.join(supportDir,src.split("/")[-2])
            destination = supportDir
        else:
            destination = self.__fs.join(supportDir,src.split("/")[-1])
        #print "source : %s, destination : %s" % (source,destination)
        excludingDirectories=[".svn"]
        if not self.__fs.exists(destination) or copyDir:
            self.__fs.copy(source, destination,excludingDirectories)
            
        
    def __applyHtmlTemplate(self, template, dataDict):
        template, subs, inserts = self.__templateConvert(template)
        for key in subs:
            if not dataDict.has_key(key):
                dataDict.update({key:''})
        for key in inserts:
            if not dataDict.has_key(key):
                dataDict.update({key:'<!-- No content -->'})
        
        return template%dataDict


    def __templateConvert(self, htmlTemplate):
        subs = {}
        inserts = {}
        xml = self.iceContext.Xml(htmlTemplate)
        nodes = xml.getNodes("//*[starts-with(@class,'sub ')]")
        for node in nodes:
            # remove the 'sub '
            classname = node.getAttribute("class")[4:] # string after 'sub '
            node.setAttribute("class", classname)
            subs[classname] = True
            textNode = xml.createText('%%(%s)s' % classname)
            node.replace(textNode)
            node.delete()
        nodes = xml.getNodes("//*[starts-with(@class,'ins ')]")
        for node in nodes:
            # remove the 'ins '
            classname = node.getAttribute("class")[4:] # string after 'ins '
            node.setAttribute("class", classname)
            inserts[classname] = True
            node.setContent('%%(%s)s' % classname)

        xmlStr = str(xml.getRootNode())
        xml.close()
        return xmlStr, subs, inserts


    def __getOptionValue(self, options, optionName):
        value = options.get(optionName, "False")
        if type(value) == bool:
            value = str(value).lower()
        elif value.strip() == "on":
            value = "true"
        return value.lower() == "true"


    def __render(self, file, method, output, rep=None):
        if rep is None:
            class MockRep(object):
                def getAbsPath(self, file):
                    return file
            rep = MockRep()         # OK
        try:
            convertedData = method(file, self.iceContext.ConvertedData())
        except Exception, e:
            if output is not None:
                traceback = self.iceContext.formattedTraceback()
                output.write("#############\n%s#############\n" % traceback)
            raise e
        errorMessage = convertedData.errorMessage
        
        if convertedData.terminalError==True:
            e = convertedData.Exception
        if errorMessage!="":
            if output is not None:
                output.write("errorMessage=%s\n" % errorMessage)
            if errorMessage.find("Failed to connect to OpenOffice")>-1:
                msg = "Failed to connect to OpenOffice!\n  Please start OpenOffice and try again!"
                if output is not None: output.write(msg + "\n")
                return msg
            elif errorMessage.find("Failed to save changes")>-1:
                msg = "Failed to save changes to Book!\n  Please close the document in OpenOffice and try again!"
                if output is not None: output.write(msg + "\n")
                return msg
            elif errorMessage.find("Word document is Invalid")>-1: 
                msg = "Failed to render document. Word document is empty"
                if output is not None: output.write(msg + "\n")
                return msg
            elif errorMessage.find("Open Office document is Invalid")>-1:
                msg = "Failed to render document. Open office document is empty"
                if output is not None: output.write(msg + "\n")
                return msg
            else:
                msg =  "**** Failed to Convert file using open office! ****\n"
                msg += errorMessage
                if output is not None: output.write(msg + "\n")
                raise Exception(msg)
                return msg
        
        # add table-of-contents
        if ".xhtml.body" in convertedData.renditionNames:
            body = convertedData.getRendition(".xhtml.body")
            toc = self.__generateToc(body, output)
            convertedData.addMeta("toc", toc)
            
        return convertedData
    
    def __generateToc(self, body, output):
        if body==None:
            return ""
        bodyXml = self.iceContext.Xml(body)
        nodes = bodyXml.getNodes("//h1")
        xml = self.iceContext.Xml("<root/>")
        ul = None
        try:
            if len(nodes)>1:
                ul = xml.createElement("ul")
                for node in nodes:
                    destNode = node.getNodes("a/@name")
                    if len(destNode)!=0 and node.getContent()!="":
                        liNode = xml.createElement("li")
                        ul.addChild(liNode)
                        dest = destNode[0].getContent()
                        content = node.getContent()
                        #content = "<a href='#%s'>%s</a>" % (dest, content)
                        aNode = xml.createElement("a", elementContent=content, href="#"+dest)
                        liNode.addChild(aNode)
                        
                        if True:    # Level 2 Heading
                            hnodes = node.getNodes("following-sibling::h1 | following-sibling::h2")
                            h2nodes = []
                            for h in hnodes:
                                if h.getName()=="h1":
                                    break
                                h2nodes.append(h)
                            if len(h2nodes)>0:
                                ul2 = xml.createElement("ul")
                                for h2 in h2nodes:
                                    dest = h2.getContent("a/@name")
                                    if dest!=None and h2.getContent()!="":
                                        content = h2.getContent()
                                        #print "\t content='%s'" % content
                                        #content = "\t<li><a href='#%s'>%s</a></li>" % (dest, content2)
                                        li2Node = xml.createElement("li")
                                        ul2.addChild(li2Node)
                                        aNode = xml.createElement("a", elementContent=content, href="#"+dest)
                                        li2Node.addChild(aNode)
                                liNode.addChild(ul2)
        except Exception, e:
            self.__output.write("Error in __generateToc: %s\n" % str(e))
        bodyXml.close()
        toc = ""
        if ul!=None:
            toc = str(ul)
        xml.close()
        return toc
