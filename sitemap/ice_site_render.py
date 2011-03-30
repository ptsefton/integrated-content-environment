#!/usr/bin/python
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


import socket
import time
import types


class IceSiteRender(object):
    """ Ice Site Render class """
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    
    #    includeSource = self.includeSource
    #    addNbspToEmptyTableCells = self.addNbspToEmptyTableCells
    def render(self, content, iceTemplateInfo, item, \
                contextList=[], manifest=None, includeSource=False, \
                addNbspToEmptyTableCells=False, exportVersion=False, \
                noContextLink=False):
        # returns the (xml) html result

        # spath
        spath = content.url
        if content.defaultPageEquals!=None and content.defaultPageEquals!="toc.htm":
            spath = content.defaultPageEquals
        
        # Get Context-Link
        contextLink = self.__getContextLink(contextList)
        if type(contextLink) is types.UnicodeType:
            contextLink = contextLink.encode("utf-8")
        content["context-link"] = contextLink
        if noContextLink:
            content["context-link"] = ""
        
        # Slide (link for this document (if needed))
        slideLink, closeSlideLink = self.__getSlideLinks(spath, item)
        content["slide-link"] = slideLink
        content["close-slide"] = closeSlideLink
        
        # Source Link
        if item.displaySourceType:
            includeSource = item.displaySourceType
            
        sourceLink = self.__getSourceLink(spath, includeSource, item)
        content["source-link"] = sourceLink
        
        # Get PDF link for this document (if needed)  - Master PDFs
        pdfRenditionLink = self.__getPdfRenditionLink(content.url, \
                        content.defaultPageEquals, content.packagePath, 
                        manifest, item)
        content["pdf-rendition-link"] = pdfRenditionLink.encode("utf-8")
        
        # Cleanup/fixup 'body'
        content["body"] = self.__cleanupFixupBody(content["body"], content["title"],
                                addNbspToEmptyTableCells)
        
        # Get CSS link
        appStyleCss = content.get("appStyleCss", "")
        content["css"] = self.__getCssLink(content.packagePath, content.get("app-css", ""), appStyleCss)
        
        if item.hasRendition(".rdf") and not exportVersion:
            urlRoot = self.iceContext.urlRoot
            resMapUrl = item.relPath[1:-len(item.ext)] + ".rdf"
            resMapUrl = self.iceContext.urlJoin(urlRoot,  resMapUrl)
            content["style-css"] += "\n<link rel='resourcemap' type='application/rdf+xml' href='%s'/>" % resMapUrl
        
        # Work a round for a FireFox bug (empty element bug)
        if content["statusbar"]==None or content["statusbar"]=="":
            content["statusbar"]=" "
        
        # Annotations
        if not exportVersion:
            annotationHtml = ""
            # InlineAnnotations
            plugin = self.iceContext.getPlugin("ice.extra.inlineAnnotate")
            if plugin:
                #print 
                #print "Got ice.inlineAnnotations ok."
                inlineAnnotations = plugin.pluginClass.getInlineAnnotations(item)
                if inlineAnnotations is not None and inlineAnnotations.hasAnnontations:
                    inlineHtml = inlineAnnotations.getHtmlDiv()
                    #print "inlineHtml='%s'" % inlineHtml
                    #print 
                    annotationHtml += inlineHtml
            content["annotations"] = annotationHtml
        else:
            content["annotations"] = "<!-- -->"
        
        ## Add Description
        #if not exportVersion:
        #    description = item.description
        #    description = "<div class='content-description-area' style='margin:1ex; border:1px solid gray;padding:0.5ex;background:#ccffff;'><div style='color:green;'>Description</div><div class='content-description'>%s</div></div>" % description
        #    content["page-toc"] = description + content.get("page-toc", "")
        
        if type(content["title"]) is types.UnicodeType:
            content["title"] = content["title"].encode("utf-8")
        for key in content.keys():
            if type(content[key]) is types.UnicodeType:
#                print "'%s' is unicode" % key
                content[key] = content[key].encode("utf-8")
        result = iceTemplateInfo.applyToTemplate(content)
        
        xml = self.iceContext.Xml(result)
        
        # package-root/ fixup - remap any href's or src's starting with package-root with the current package-path
        packageRootAtts = xml.getNodes("(//@href | //@src)[starts-with(., 'package-root/')]")
        for att in packageRootAtts:
            value = att.getContent()
            value2 = self.__makePackageRootLinkRelativeToCurrentPath(value, \
                                            content.url, content.packagePath)
            att.setContent(value2)

        ## HACK
        # change all links with .skin to skin
        linkAtts = xml.getNodes("(//@href | //@src)")
        for att in linkAtts:
            value = att.getContent()
            if value.startswith(".skin/"):
                value = value[1:]
            att.setContent(value.replace("/.skin/", "/skin/"))
        ##
        
        # Relative stuff 
        #   (replace link to self and change the link to bold text)
        #   make all link relative
        xml = self.__makeAllLinksRelativeAndNullOutSelfLinks(xml, content.url, \
                                content.altUrls)  ######### content.defaultPageEquals, content.isDefaultPage
        # Fix for Firefox bug(s)
        xml = self.__applyFirefoxBugFixup(xml)
        
        #Remove empty h-slide
        divs = xml.getNodes("//*[local-name()='div'][@class='slide']")
        for div in divs:
            if div.getContent().strip() == "":
                div.remove()
            else:
                children = div.getChildren()
                if children is not None and children != []:
                    for child in children:
                        if child.getName() == "h1" and child.getContent().strip() == "":
                            child.remove()
        
        
        if not exportVersion:
            # Add jQuery.js and ice.js to the head and other javascript source (e.g. jquery-ui.js)
            headNode = xml.getNode("/*[local-name()='html']/*[local-name()='head']")
            if headNode!=None:
                scriptNode = xml.createElement("script", type="text/javascript", src="/jquery.js")
                scriptNode.addChild(xml.createComment(" "))
                headNode.addChild(scriptNode)
                scriptNode = xml.createElement("script", type="text/javascript", src="/ice.js")
                scriptNode.addChild(xml.createComment(" "))
                headNode.addChild(scriptNode)
                
                #For jQAlert function - drag/move
                scriptNode = xml.createElement("script", type="text/javascript", src="/skin/jquery-event-drag.js")
                scriptNode.addChild(xml.createComment(" "))
                headNode.addChild(scriptNode)
                # other javascript source files
                for src in content.get("javascript-files", []):     # e.g. ["/jquery-ui.js"]
                    scriptNode = xml.createElement("script", type="text/javascript", src="%s" % src)
                    scriptNode.addChild(xml.createComment(" "))
                    headNode.addChild(scriptNode)
                for js in content.get("javascripts", []):
                    scriptNode = xml.createElement("script", type="text/javascript")
                    scriptNode.addContent("//")
                    scriptNode.addChild(xml.createComment("\n%s\n//" % js))
                    headNode.addChild(scriptNode)
#                scriptNode = xml.createElement("script", type="text/javascript", src="http://ie7-js.googlecode.com/svn/version/2.0(beta3)/IE7.js")
#                scriptNode.addChild(xml.createComment(" "))
#                headNode.addChild(scriptNode)
#                scriptNode = xml.createElement("script", type="text/javascript", src="http://ie7-js.googlecode.com/svn/version/2.0(beta3)/IE8.js")
#                scriptNode.addChild(xml.createComment(" "))
#                headNode.addChild(scriptNode)
                textNode = xml.createText("\n")
                headNode.addChild(textNode)
        
        if False:    # jQuery testing for IE
            body = xml.getNode("//*[local-name()='div'][@class='body']")
            if body!=None:
                newNode = xml.xmlStringToElement(self.__addJSTestSection())
                body.addChild(newNode)
            else:
                print "* div class='body' is None (not found!)"
        
        if not exportVersion:
            # HACK: check for jquery added by lightbox and remove it
            bodyNode = xml.getNode("/*[local-name()='html']/*[local-name()='body']")
            if bodyNode!=None:
                jqueryNode = bodyNode.getNode("//*[local-name()='script' and @src='skin/jquery.js']")
                if jqueryNode!=None:
                    jqueryNode.remove()
        
        result = str(xml.getRootNode())
        xml.close()
        
        return iceTemplateInfo.templateHeader + result
    
    
    def __getContextLink(self, contextList):
        # Context-Link
        contextLinkSep = " > "
        links = []
        for n, p in contextList:
            try:
                n = n.encode("utf-8")
            except: pass
            try:
                p = p.encode("utf-8")
            except: pass
            p = self.iceContext.escapeXmlAttribute(p)
            n = self.iceContext.escapeXmlAttribute(n)
            links.append("<a href='%s'>%s</a>" % (p, n))
        return contextLinkSep.join(links)
    
    
    def __getSlideLinks(self, spath, item):
        # HACK: for slides
        name = self.iceContext.fs.split(spath)[1]
        closeSlideLink = ""
        if name.endswith(".slide.htm"):
            name = name[:-len(".slide.htm")]
            closeSlideLink = "<a class='close-slide' href='%s'>Close&#160;</a>" % (name + ".htm")
        
        # Slide link for this document (if needed)
        slide = item.getMeta("isSlide")
        slideLink = ""
        if bool(slide):
            #s = self.iceContext.fs.split(spath)[1]
            #s = self.iceContext.fs.splitExt(s)[0] + ".slide.htm"
            s = item.relPath[:-len(item.ext)] + ".slide.htm"
            imgSrc = "package-root/skin/slideicon.gif"
            link = "<a href='%s'><span><img src='%s' border='0' alt='View slide'/></span></a>"
            slideLink = link % (s, imgSrc)
        return slideLink, closeSlideLink
    
    
    def __getSourceLink(self, spath, includeSource, item):
        # Source Link
        sourceLink = ""
        if includeSource and item.isFile:
            itemName = item.name
            if itemName!=None and not itemName.endswith(".htm"):
                imgSrc = "package-root/skin/source.gif"
                link = "<a href='%s'><span><img src='%s' border='0' alt='Source document'/></span></a>"
                sourceLink = link % (item.relPath, imgSrc)
        return sourceLink
    
    
    def __getPdfRenditionLink(self, spath, defaultPageEquals, packagePath, 
                                                        manifest, item):
        fs = self.iceContext.fs
        rep = self.iceContext.rep
        pdfRenditionLink = "&#160;"
        # Get PDF link for this document (if needed)  - Master PDFs
        if defaultPageEquals!=None and defaultPageEquals!="toc.htm":
            spath = defaultPageEquals
        if spath.endswith("/toc.htm") and spath[:len(spath)-len("toc.htm")]==packagePath \
                                        and packagePath!="":
            spath = packagePath
            #OK get a list of all master documents in this directory!
            item = rep.getItem(spath)
            listItems = item.listItems()
            files = [i.relPath for i in listItems if i.ext==self.iceContext.oooMasterDocExt]
            # Also any 'Book' documents in this direcory
            books = [i.relPath for i in listItems if i.ext in self.iceContext.bookExts]
            files.extend(books)
            # Get only the ones with a PDF rendition
            files = [file for file in files 
                        if self.iceContext.iceSplitExt(file)[1] in self.iceContext.pdfItemExtensions]
            if len(files)>0:
                files.sort()
                fileItems = [self.iceContext.rep.getItem(file) for file in files]
                if manifest is not None:
                    children = manifest.children
                    for fileItem in fileItems:
                        mItem = manifest.getManifestItem(fileItem.guid)
                        fileItem.mItem = mItem
                        try:
                            i = 9999
                            i = children.index(mItem)
                        except: pass
                        fileItem.mItemIndex = i
                    def sort(fItem1, fItem2):
                        return cmp(fItem1.mItemIndex, fItem2.mItemIndex)
                    # Sort by manifest order
                    fileItems.sort(sort)
                    
                row1=""; row2=""
                for fileItem in fileItems:
                    pdfName = fileItem.name[:-len(fileItem.ext)] + ".pdf"
                    #pdfLink = "<a href='%s' target='_blank'>" % pdfName
                    pdfLink = "<a href='%s' onclick='javascript:window.open(this.href);return false;'>" % (pdfName)
                    src = "package-root/skin/pdf.gif"
                    pdfLinkTitle = "View the printable version in a new window"
                    pdfLink += "<img border='0' src='%s' alt='PDF version' title='%s'/></a>" % (src, pdfLinkTitle)
                    title = fileItem.getMeta("title")
                    if title is None:
                        title = "[Untitled] '%s'" % fileItem.name
                    if hasattr(fileItem, "mItem") and fileItem.mItem:
                        mTitle = fileItem.mItem.manifestTitle
                        if mTitle is not None:
                            title = mTitle
                    pdfLink = "<span class='pdf-rendition-link'>%s</span>" % pdfLink
                    row1 += "<td style='padding-left:2em;text-align:center;'>%s</td>" % pdfLink
                    row2 += "<td style='padding-left:2em;text-align:center;'>%s</td>" % title
                row2 = row2.decode('utf-8')
                pdfRenditionLink = "<table><tbody><tr>%s</tr><tr>%s</tr></tbody></table>" % (row1, row2)
        else:
            baseName = item.relPath[:-len(item.ext)]
            if item.hasPdf:
                # special case for pdfs to open in new window
                pdfName = baseName + ".pdf"
                pdfLinkTitle = "View the printable version of this page in a new window"
                pdfLink = "<a href='%s' onclick='javascript:window.open(this.href);return false;'>" % (pdfName)
                src = "package-root/skin/pdf.gif"
                pdfLink += "<img border='0' src='%s' alt='PDF version' title='%s'/></a>" % (src, pdfLinkTitle)
                pdfLink = "<span class='pdf-rendition-link'>%s</span>" % pdfLink
            else:
                pdfLink = ""
            if item.exists:
                ext = item.ext
                exts = list(rep.render.getRenderableTypes(ext))
                if item.hasAudio:
                    # mp3  renditions are rendered on the fly unlike other types
                    # so we add it here if available
                    exts.append(".mp3")
                if len(exts) > 0:
                    ignoreExts = [".htm", ".pdf"]
                    for toExt in exts:
                        if not toExt in ignoreExts and (rep.render.hasViewableIcon(ext, toExt) or toExt==".mp3"):
                            href = baseName + toExt
                            extName = toExt[1:]
                            src = "package-root/skin/%s.png" % extName
                            mimeType = self.iceContext.MimeTypes[toExt.lower()]
                            if mimeType.startswith("audio"):
                                title = "Listen to this audio version (%s)" % extName
                            elif mimeType.startswith("image"):
                                title = "View this as an image (%s)" % extName
                            else:
                                title = "Open the %s rendition" % extName
                            alt = "%s rendition" % extName
                            link = "<a href='%s'><img border='0' src='%s' alt='%s' title='%s'/></a>" \
                                 % (href, src, alt, title)
                            pdfRenditionLink += "&#160;" + link
            pdfRenditionLink += "&#160;" + pdfLink
        return pdfRenditionLink
    
    
    def __cleanupFixupBody(self, body, title, addNbspToEmptyTableCells=False):
        # Cleanup/fixup 'body'
        if body is not None and body!="":
            if addNbspToEmptyTableCells:
                body = self.__doAddNbspToEmptyTableCells(body)
            body = self.__addPIds(body, title)
        body = self.iceContext.HtmlCleanup.cleanup(body)
        if body is not None and body!="" and body.startswith("<?"):
            body = body[body.find("?>")+2:]
        if body is None:
            body = "<!-- no body data set -->"
        if body == "":
            body = "<!-- body is empty -->"
        return body
    
    
    def __getCssLink(self, packagePath, appCssLink, appStyleCss):
        cssLink = "<link rel='stylesheet' href='%sskin/default.css'/>" % packagePath
        #if appCssLink != "":
        #    cssLink = "<link rel='stylesheet' href='%s'/>\n%s" % (appCssLink, cssLink)
        if appStyleCss is not None and appStyleCss!="":
            tmp = "\n<style type='text/css'>\n%s</style>" % appStyleCss
            cssLink += tmp
        return cssLink
    
    
    def __makeAllLinksRelativeAndNullOutSelfLinks(self, xml, path, altUrls): #  defaultPageEquals, isDefaultPage
        # null out links to self (and make bold)
        #selfHrefNodes = xml.getNodes("//*[local-name()='a'][@href='%s'][not(ancestor::*/@class='searchResults')]" % \
        #                             self.iceContext.escapeXmlAttribute(path))
        #xml = self.iceContext.relativeLinker.nullLinks(xml, path, selfHrefNodes)
        ##
        #print "path='%s'" % path
        selfHrefNodes = xml.getNodes("//*[local-name()='a'][@href][not(ancestor::*/@class='searchResults')]")
        nodes = []
        for node in selfHrefNodes:
            href = node.getAttribute("href")
            if href in altUrls:
                nodes.append(node)
        xml = self.iceContext.relativeLinker.nullLinks(xml, path, nodes)
        
        # make all links relative
        xml = self.iceContext.relativeLinker.makeRelative(xml, path)
        
##        # null out other links that also (in effect) link to this page
##        if defaultPageEquals!=None:
##            rel = self.iceContext.relativeLinker.makeUrlRelativeTo(defaultPageEquals, path)
##            xml = self.iceContext.relativeLinker.nullLinks(xml, rel)
##        if isDefaultPage:               # to null out default.htm links
##            xml = self.iceContext.relativeLinker.nullLinks(xml, "default.htm")
##        xml = self.iceContext.relativeLinker.nullLinks(xml, "")
        return xml
    
    
    def __applyFirefoxBugFixup(self, xml):
        # Work around for a Firefox bug where the item following an empty anchor tag is display as a link
        nodes = xml.getNodes("//*[local-name()='a']")
        for node in nodes:
            if node.getFirstChild()==None:
                newComment = xml.createComment("")
                node.addChild(newComment)
        return xml
    
    
    def __makePackageRootLinkRelativeToCurrentPath(self, value, path, packagePath):
        if value.startswith("package-root/"):
            value = packagePath + value[len("package-root/"):]
        return value
        # make this link relative to our current path
        p = len(path.split("/"))
        v = len(packagePath.split("/")) + 1
        diff = p - v
        if diff > 0:
            value = diff * "../" + value
        elif diff < 0:
            value = self.iceContext.fs.split(packagePath)[1] + "/" + value        
        return value
    
    
    def __doAddNbspToEmptyTableCells(self, body):
        bodyXml = None
        try:
            bodyXml = self.iceContext.Xml(body)
            addedNbsp = False
            nodes = bodyXml.getNodes("//*[local-name()='td' or local-name()='th']")
            #nodes = bodyXml.getNodes("//*[local-name='td' or local-name='th']")
            for node in nodes:
                numChildren = len(node.getChildren())
                if numChildren>1:
                    continue
                if numChildren==1:
                    node = node.getFirstChild()
                    if node.getName()!="p":
                        continue
                content = node.content.replace(" ", "")
                if content=="":
                    node.addRawContent("&#160;")
                    addedNbsp = True
            if addedNbsp:
                body = str(bodyXml)
                #print "===="
                #print body
                #print "===="
        except:
            print "Failed to parse the body as XML while rendering page!"
        if bodyXml is not None:
            bodyXml.close()
            bodyXml = None
        return body

    def __addPIds(self, body, title):
        #print "\n__addPids()"
        #startTime = time.time()
        hash = {}
        bodyXml = None
        try:
            bodyXml = self.iceContext.Xml(body)
            titleId = "h%st" % self.iceContext.crc32Hex(title)
            node = bodyXml.xmlStringToElement("<div class='title' id='%s' style='display:none;'>%s</div>" % ( titleId, title))
            bodyXml.getRootNode().getFirstChild().addPrevSibling(node)
            nodes = bodyXml.getNodes("//*[local-name()='p' or (starts-with(local-name(),'h') \
                                                             and string-length(local-name())=2)]")
            for node in nodes:
                try:
                    id = self.iceContext.crc32Hex(str(node))
                    p = hash.get(id, 0) + 1
                    hash[id] = p
                    node.setAttribute("id", "h%sp%s" % (id, p))
                except Exception, e:
                    print " error - '%s'" % str(e)
            body = str(bodyXml)
        except:
            print "Failed to parse the body as XML while rendering page!"
        if bodyXml is not None:
            bodyXml.close()
            bodyXml = None
        #print "  addedParaIds in '%s'" % (time.time()-startTime)
        return body
    
    
    def __addJSTestSection(self):
        html = """<div id='jsTestSection' style='border:1px solid red; padding:1em;'>
        <script>
            var print = function(arg)
            {
                jQ("#jsOutput").html(arg);
            }
            var wprint = print;
            var jsExec = function() {
                var jsTest = jQ("#jsTest");
                var jsOutput = jQ("#jsOutput");
                var o = "";
                var print=function(arg) { o+=arg; }; 
                var r;
                try
                {
                    r = eval(jQ("#jsText").val());
                } catch (err) {
                    r = err.message;
                }
                if(typeof(r)=="undefined") r="";
                o = o + "\\n" + r
                //o=o.replace(/\\n/g, "&lt;br/&gt;");
                jsOutput.html(o);
            }
        </script>
        <div onclick='jsExec();'>Javascipt  (print("Testing");)</div>
        <textarea rows='16' cols='120' name='jsText' id='jsText'>jQ</textarea>
        <div style='padding:1em;'>
            <button name='jsExec' id='jsExec' onclick='jsExec();'>Execute</button>
        </div>
        <pre id='jsOutput' name='jsOutput' style='border:1px solid blue;color:blue;'> </pre>
        <div id='jsTest'>jsTest</div>
</div>
"""
        return html






