
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

import sys
import tempfile


pluginName = "ice.ooo.OdpPptConverter"
pluginDesc = "OdpPptConverter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OdpConverter
    pluginInitialized = True
    return pluginFunc



class OdpConverter(object):
    htmlTemplate = """<html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>Default Template</title>
        <style type="text/css">
          .rendition-links { text-align: right; }
          .body table td { vertical-align: top; }
        </style>
        <script src="package-root/.skin/slide/slideous.js" type="text/javascript"><!-- --></script>
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
    
    def templateConvert(self, htmlTemplate):
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
    
    
    def __init__(self, iceContext, fs, htmlTemplate):
        self.iceContext = iceContext
        self.__output = iceContext.output
        self.__oooConverter = self.iceContext.getOooConverter()
        
        # .odp
        OdpConvert = self.iceContext.getPlugin("ice.render.odpConverter").pluginClass
        OdpConvert = OdpConvert(self.iceContext)
        self.__odpRenderMethod = OdpConvert.renderMethod
        
        # .ppt
        PptConvert = self.iceContext.getPlugin("ice.render.pptConverter").pluginClass
        PptConvert = PptConvert(self.iceContext)
        self.__pptRenderMethod = PptConvert.renderMethod
        
        # .pptx
        PptxConvert = self.iceContext.getPlugin("ice.render.pptxConverter").pluginClass
        PptxConvert = PptxConvert(self.iceContext)
        self.__pptxRenderMethod = PptxConvert.renderMethod
        
        self.__htmlTemplate = htmlTemplate
        self.__fs = fs
        self.__skinFs = self.iceContext.FileSystem("fake.skin")
    
    def __getOptionValue(self, options, optionName):
        value = options.get(optionName, "False")
        if type(value) == bool:
            value = str(value).lower()
        elif value.strip() == "on":
            value = "true"
        return value.lower() == "true"
    
    def convert(self, file, toDir, options={}):
        path, name, ext = self.__fs.splitPathFileExt(file)
        ext = ext.lower()
        # Store options, we need to pass them on later to generate the thumbnail
        self.__options = options
        # if __rep is set in options, it is an internal call
        rep = options.get("__rep", None)
        sourcelink = self.__getOptionValue(options, "sourcelink")
        item = None
        if rep is not None:
            argPath = options.get("argPath")
            item = rep.getItemForUri(argPath)
            file = item.relPath
        if ext==".odp":
            convertedData = self.__render(file, self.__odpRenderMethod, self.__output, rep)
        elif ext==".ppt":
            convertedData = self.__render(file, self.__pptRenderMethod, self.__output, rep)
            tempOdpFile = convertedData.abspath("temp.odp")
            if sourcelink:
                self.__fs.copy(tempOdpFile, self.__fs.join(path, name + ".odp"))
        elif ext==".pptx":
            convertedData = self.__render(file, self.__pptxRenderMethod, self.__output, rep)
            tempOdpFile = convertedData.abspath("temp.odp")
            if sourcelink:
                self.__fs.copy(tempOdpFile, self.__fs.join(path, name + ".odp"))
        else:
            return ("Unsupported file extension '%s'." % ext, None, None)
        
        toDir = self.__fs.absolutePath(toDir)
        supportDirName = "%s_files" % name
        supportDir = self.__fs.join(toDir, supportDirName)
        self.__fs.makeDirectory(toDir)
        self.__fs.makeDirectory(supportDir)
        pdfFile = self.__fs.join(toDir, name + ".pdf")
        self.meta = convertedData.meta
        htmlFile = self.__fs.join(toDir, name + ".htm")
        
        #print "convertedData: ", convertedData
        images = convertedData.getMeta("images")
        for imageName in images:
            imageData = convertedData.getImage(imageName)
            self.__fs.writeFile(self.__fs.join(supportDir, imageName), imageData)
            
        includetitle = self.__getOptionValue(options, "includetitle")
        if includetitle:   
            title = convertedData.getMeta("title")
        else:
            title = " "
        self.title = title
        body = convertedData.getRendition(".xhtml.body")
        slideFileName = "%s.slide.htm" % name
        slideFile = self.__fs.join(toDir, slideFileName)
        #slideLink = True    #will always have slide when rendering odp or ppt
        slideLink = self.__getOptionValue(options, "slidelink")        
        
        pdfLink = self.__getOptionValue(options, "pdflink")
        if sourcelink:
            sourceLink = "<a href='%s' title='View the original document'>Source</a>" % (name + ext)
            if ext == ".ppt":
                # include the generated odp for ppt
                sourceLink += " | <a href='%s' title='View the derived ODP'>Derived ODP</a>" % (name + ".odp")
            if slideLink or pdfLink:
                sourceLink += " | "
        else:
            sourceLink = ""
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
        else:
            self.__fs.delete(pdfFile)
        
        dataDict = {"title":title, "body":body,
                    "pdf-rendition-link":pdfRendition, "source-link":sourceLink,
                    "slide-link":slideRendition}
        
        html = self.__applyHtmlTemplate(self.__htmlTemplate, dataDict)
        
        if rep is not None:
            # process media objects
            basePath = self.__fs.split(file)[0]
            links = convertedData.getMeta('links')
            for link in links:
                linkPath = link[0]
                if not linkPath.startswith("#"):
                    absLinkPath = rep.getAbsPath(self.__fs.join(basePath, linkPath))
                    _, linkName, linkExt = self.__fs.splitPathFileExt(linkPath)
                    linkFileName = linkName + linkExt
                    self.__fs.copy(absLinkPath, self.__fs.join(supportDir, linkFileName))
                    html = html.replace(linkPath, self.__fs.join(supportDirName, linkFileName))
        
        self.__fs.writeFile(htmlFile, html)
        
        if slideLink:
            # process slides
            xml = self.iceContext.Xml(body)
            div = xml.createElement("div")
            div.addChildren(xml.getNodes("//div[@class='slide']"))
            slideTitle = convertedData.getMeta("title")
            slideBody = str(div)
            xml.close()
            
            dataDict.update({"body":slideBody, "title":slideTitle})
            slideSkinPath = self.__skinFs.absPath("slide")
            if rep is not None:
                slideTemplate = rep.getItem("/skin/slide/slide.xhtml").read()
                repSlideSkinPath = rep.getAbsPath("/skin/slide")
                if self.__fs.exists(repSlideSkinPath):
                    slideSkinPath = repSlideSkinPath
            else:
                slideTemplate = self.__skinFs.readFile("slide/slide.xhtml")
            slideHtml = self.__applyHtmlTemplate(slideTemplate, dataDict)
            # fix up skin links
            slideHtml = slideHtml.replace("package-root/.skin/slide", supportDirName)
            slideHtml = slideHtml.replace("package-root/.skin", supportDirName)
            slideHtml = slideHtml.replace("package-root/skin/slide", supportDirName)
            slideHtml = slideHtml.replace("package-root/skin", supportDirName)
            
            self.__fs.writeFile(slideFile, slideHtml)
            # copy supporting files
            self.__fs.copy(slideSkinPath, supportDir)
        
        convertedData.close()
        return "ok", htmlFile, pdfFile
    
    def __applyHtmlTemplate(self, template, dataDict):
        template, subs, inserts = self.templateConvert(template)
        for key in subs:
            if not dataDict.has_key(key):
                dataDict.update({key:''})
        for key in inserts:
            if not dataDict.has_key(key):
                dataDict.update({key:''})
        return template % dataDict
    
    def __render(self, file, method, output, rep=None):
        if rep is None:
            class MockRep(object):
                def getAbsPath(self, file):
                    return file
            rep = MockRep()         # OK
        try:
            convertedData = method(file, self.iceContext.ConvertedData(), **self.__options)
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
            elif errorMessage.find("Excel document is Invalid")>-1: 
                msg = "Failed to render document. Excel document is empty"
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
