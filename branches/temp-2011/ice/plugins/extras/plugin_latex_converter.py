#!/usr/bin/env python
#
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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


pluginName = "ice.extra.LaTeXConverter"
pluginDesc = "LaTeX converter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = LaTeXConverter(iceContext)
    pluginClass = LaTeXConverter
    pluginInitialized = True
    return pluginFunc


defaultTemplate = """<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        <title>Default Template</title>
        <style type="text/css">
            .rendition-links { text-align: right;}
            .body table td {vertical-align: top;}
        </style>
        <style class="sub style-css" type="text/css"></style>
    </head>
    <body>
        <div class="rendition-links">
          <span class="ins pdf-rendition-link" />
        </div>
        <h1 class="ins title"></h1>
        <div class="ins page-toc"/>
        <div class="ins body"/>
    </body>
</html>"""


def templateConvert(iceContext, htmlTemplate):
    subs = {}
    inserts = {}
    xml = iceContext.Xml(htmlTemplate)
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


class LaTeXConverter(object):
    XHTML_NS = "http://www.w3.org/1999/xhtml"
    
    def __init__(self, iceContext, fileSystem = None, htmlTemplate = None):
        self.iceContext = iceContext
        if fileSystem is None:
            fileSystem = iceContext.fs
        if htmlTemplate is None:
            htmlTemplate = defaultTemplate
        self.__fs = fileSystem
        self.__htmlTemplate = htmlTemplate
        self.__unicodeDict = iceContext.getPluginClass("ice.unicode.dict").dictionary
    
    def tex4html(self, latexPath, toDir = "", options = {}):
        if self.__hasLocalLaTeX():
            print "Using local LaTeX installation"
            return self.__tex4html(latexPath, toDir, options)
        else:
            convertUrl = self.iceContext.settings.get("convertUrl")
            if convertUrl == None:
                return "LaTeX conversion service not available", None, None
            else:
                print "Using LaTeX service at", convertUrl
                options.update({"sessionid": ""})
                
                latexFile = open(latexPath)
                postData = [(k, v) for k, v in options.iteritems()]
                latexData = latexFile.read()
                postData.append(("file", ("%s" % latexPath, latexData)))
                postData.append(("zip", "True"))
                
                #postData.append(("file", latexFile))
                
                _, name, _ = self.__fs.splitPathFileExt(latexPath)
                try:
                    zipData, headers, _, _ = self.iceContext.Http().post(convertUrl, postData,
                                                         includeExtraResults=True)
                    contentType = headers.gettype()
                    if contentType == self.iceContext.MimeTypes[".zip"]:
                        zipFile = name + ".zip"
                        zipFile = zipFile.replace(" ", "_")
                        latexFile.close()
                        
                        outFs = self.iceContext.FileSystem(toDir)
                        outFs.writeFile(zipFile, zipData)
                        outFs.unzipToDirectory(zipFile, toDir)
                        
                        htmlFile = outFs.absPath(name + ".html")
                        pdfFile = outFs.absPath(name + ".pdf")
                        
                        return "ok", htmlFile, pdfFile
                    else:
                        return "Unexpected response from server.", zipData, None
                except Exception, e:
                    return "Remote server response: %s" % str(e), None, None
    
    def __hasLocalLaTeX(self):
        _, stderr = self.__execute3("latex")
        
        if self.iceContext.isWindows:
            keyword = "recognized"
        else:
            keyword = "found"
        hasLocal = stderr.find("not " + keyword) == -1
        
        return hasLocal
    
    def __execute3(self, cmd, *args):
        stdin, stdout, stderr = self.iceContext.system.execute3(cmd, *args)
        out = stdout.read()
        err = stderr.read()
        stdin.close()
        stdout.close()
        stderr.close()
        return out, err
    
    def __tex4html(self, latexPath, toDir, options):
        latexPath = self.__fs.absPath(latexPath)
        path, name, ext = self.__fs.splitPathFileExt(latexPath)
        
        if toDir is None or toDir == "":
            toDir = self.__fs.join(path, name + "_files")
        else:
            toDir = self.__fs.absPath(toDir)
        
        outFs = self.iceContext.FileSystem(toDir)
        inputFile = outFs.absPath(name + ext)
        htmlFile = outFs.absPath(name + ".html")
        pdfFile = outFs.absPath(name + ".pdf")
        logFile = outFs.absPath(name + ".log")
        
        if bool(options.get("directory", False)):
            # clean/create the output directory if necessary
            if self.__fs.exists(toDir):
                self.__fs.delete(toDir)
            self.__fs.makeDirectory(toDir)
        
        # keep current directory, restore on completion or errors
        cwd = self.iceContext.getcwd()
        
        try:
            try:
                # change temporarily to the working directory
                print "Changing directory to", toDir
                self.iceContext.chdir(toDir)
                outFs.copy(latexPath, inputFile)
                
                # run latex to create the pdf
                stdout, _ = self.__execute3("latex", "-halt-on-error",
                                                     "-output-format=pdf",
                                                     inputFile)
                if stdout.find(" Fatal error occurred") > -1:
                    raise Exception("Failed creating PDF")
                
                # run htlatex to convert to html
                _, stderr = self.__execute3("htlatex", inputFile)
                if stderr.find("--- warning --- Problem with command line") > -1:
                    raise Exception("Failed creating HTML")
                
                # cleanup html to xhtml strict
                tidyHtml = self.__tidy(htmlFile)
                
                # render using the html template
                title, body = self.__parseHtml(tidyHtml)
                title = " "    # FIXME set blank title or else it appears twice
                styleCss = '<link rel="stylesheet" type="text/css" href="%s.css"/>' % name
                dataDict = {"title": title, "style-css": styleCss, "body": body,
                            "page-toc": "", "pdf-rendition-link": "", "slide-link": "", "source-link": ""}
                if bool(options.get("pdflink", False)):
                    pdfLink = '<a href="%s" title="View the printable version of this page">PDF version</a>' % (name + ".pdf")
                    dataDict.update({"pdf-rendition-link": pdfLink})
                template, subs, inserts = templateConvert(self.iceContext, self.__htmlTemplate)
                html = template % dataDict
                
                # process footnotes
                tree = self.iceContext.ElementTree.XML(html)
                
                footNoteFiles = []
                for footnote in tree.getiterator():
                    if footnote.get("class", "") == "footnote-mark":
                        for child in footnote.getchildren():
                            if child.get("href", "").find("html#") > -1:
                                fileName, anchor = child.get("href", "").split("#")
                                footNoteFiles.append([fileName, anchor])
                                newAnchor = "#%s" % anchor
                                child.set("href", newAnchor)
                
                bodyElem = tree.find(".//body")
                for footNoteFile, anchor in footNoteFiles:
                    fileName = outFs.absPath(footNoteFile)
                    footNoteHtml = self.__tidy(fileName)
                    footNoteTree = self.iceContext.ElementTree.XML(footNoteHtml)
                    self.__removeNamespace(footNoteTree, self.XHTML_NS)
                    footNoteBodyElem = footNoteTree.find(".//body")
                    for child in footNoteBodyElem.getchildren():
                        bodyElem.append(child)
                
                html = self.iceContext.ElementTree.tostring(tree).strip()
                
                # write out the final xhtml
                outFs.writeFile(htmlFile, html)
            except Exception, e:
                if not outFs.exists(logFile):
                    logFile = outFs.absPath("texput.log")
                return "Error: %s" % str(e), logFile, None
        finally:
            self.__cleanupDir(toDir, name)
            print "Changing directory back to", cwd
            self.iceContext.chdir(cwd)
        
        return "ok", htmlFile, pdfFile
    
    def __tidy(self, htmlFile):
        import tidy
        tidyOpts = dict(output_xhtml = 1, add_xml_decl = 1, indent = 1)
        tidyHtml = str(tidy.parse(htmlFile, **tidyOpts))
        for key, value in self.__unicodeDict.iteritems():
            if tidyHtml.find(key):
                tidyHtml = tidyHtml.replace(key, value)
        return tidyHtml
    
    def __removeNamespace(self, tree, ns):
        for elem in tree.getiterator():
            elem.tag = elem.tag.replace("{%s}" % ns, "")
    
    def __parseHtml(self, html):
        tree = self.iceContext.ElementTree.XML(html)
        self.__removeNamespace(tree, self.XHTML_NS)
        
        # get the title
        title = ""
        titleElem = tree.find(".//title")
        if titleElem is not None:
            if titleElem.text is not None:
                title = titleElem.text.strip()
        
        # get the body without the body element
        bodyElem = tree.find(".//body")
        body = self.iceContext.ElementTree.tostring(bodyElem).strip()
        body = body[6:-7].strip()
        
        return title, body
    
    def __cleanupDir(self, outputDir, docName):
        exts = [".html", ".css", ".tex", ".pdf", ".png", ".log"]
        fs = self.iceContext.FileSystem(outputDir)
        for file in fs.listFiles():
            name, ext = fs.splitExt(file)
            if name == docName and not (ext in exts):
                fs.delete(file)
    
    def __call__(self, latexPath, toDir = "", options = {}):
        return self.tex4html(latexPath, toDir, options)
    