#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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

""" Module to export a package/site to a zip file. """

import os
import re

from request_data import serverRequestData
import ice_site



class iceIO(object):
    def __init__(self, rep, fileSystem=None):
        if fileSystem is None:
            self.__fs = fs
        else:
            self.__fs = fileSystem
        self.__rep = rep
    
    @property
    def rep(self):
        return self.__rep
    
    def abspath(self, path):
        return self.__fs.absPath(path)
    
    def join(self, *args):
        return self.__fs.join(*args).replace("\\", "/")
    
    def split(self, path):
        return self.__fs.split(path)
    
    def splitExt(self, path):
        return self.__fs.splitExt(path)
    
    def exists(self, path):
        return self.__fs.exists(path)
        
    def makeDirs(self, path):
        return self.__fs.makeDirectory(path)    
    
    def walk(self, path):
        return self.__fs.walk(path)
    
    def removeDir(self, path):
        return self.__fs.delete(path)
    
    def remove(self, file):
        try:
            self.__fs.delete(path)
            #print " deleted - '%s'" % file
        except:
            print " failed to delete - '%s'" % file
    
    def createTempDir(self):
        return self.__fs.createTempDirectory()
    
    def zipAll(self, toPath, to):
        return self.__fs.zip(toPath, to)

    def copy(self, fileName, srcPath, destPath):
        data = self.__rep.getItem(self.join(srcPath, fileName)).read()
        if data!=None:
            self.write(self.join(destPath, fileName), data)

    def write(self, fileName, data):
        try:
            dir = self.split(fileName)[0]
            if not(self.exists(dir)):
                self.makeDirs(dir)
            #print "Writing file " + fileName
            f = open(fileName, "wb")
            f.write(data)
            f.close()
        except Exception, e:
            print "********** ERROR failed to write file '%s' *********" % fileName
    
    def read(self, fileName):
        f = open(fileName, "rb")
        data = f.read()
        f.close()
        return data
    
    def zipString(self):
        return self.iceContext.ZipString()
    


class iceExport:
    """ iceExport class. """
    def __init__(self, iceSite):
        # iceSite usage:
        #    iceSite.rep
        #    iceSite.clone()
        #    iceSite.preRenderCallback
        #    iceSite.serve(item)
        #    and maybe its dictionary e.g. iceSite["toolbar"] = "<span/>"
        self.io = iceIO(iceSite.rep)
        self.iceSite = iceSite.clone()
        self.includeSource = iceSite.includeSource
        self.objectFixup = FixupObjectUrls(self.io)
        self.__makeObjectUrlLocal = False
    
    def __getMakeObjectUrlLocal(self):
        return self.__makeObjectUrlLocal
    def __setMakeObjectUrlLocal(self, value):
        self.__makeObjectUrlLocal = value
    makeObjectUrlLocal = property(__getMakeObjectUrlLocal, __setMakeObjectUrlLocal)
    
    def export(self, fromPath, to=None, toRepository=False, exportCallback=None, \
                    deleteFirst=True, ignoreManifest=False):
        ignoreManifest = True
        self.iceSite.preRenderCallback = self.__preRenderMethod
        try:
            print "\n--- Export(fromPath='%s') ---" % (fromPath)
            toPath = None
##            tempDir = None
##            if toRepository and not to.lower().endswith(".zip"):
##                to += ".zip"
##            if self.io.splitExt(to)[1]==".zip":
##                tempDir = self.io.createTempDir()
##                toPath = str(tempDir)
##            else:
##                toPath = to
##            if not fromPath.endswith("/"):
##                fromPath += "/"
##            
##            if deleteFirst:
##                self.io.removeDir(toPath)
##            if not(self.io.exists(toPath)):
##                self.io.makeDirs(toPath)
            
            if callable(exportCallback):
                try:
                    obj = exportCallback(self.iceSite, toPath)
                    if obj is not None and hasattr(obj, "makeObjectUrlLocal"):
                        self.makeObjectUrlLocal = obj.makeObjectUrlLocal
                except Exception, e:
                    print "##########################"
                    print "ERROR in exportCallback - " + str(e)
                    print "##########################"
            
            #------------------------------
            #          Export
            self.__export(fromPath, toPath, ignoreManifest=ignoreManifest)
            #------------------------------
            
            print "--- Finished exporting ---\n"
        except Exception, e:
            self.iceSite.preRenderCallback = None
            raise
        self.iceSite.preRenderCallback = None


    def __export(self, fromPath, toPath=None, ignoreManifest=False):
        manifestPath = self.io.join(fromPath, "manifest.xml")
        manifestXmlStr = self.io.rep.getItem(manifestPath).read()
        dom = None
        
        if not fromPath.endswith("/"):
            fromPath += "/"
        if not fromPath.startswith("/"):
            fromPath = "/" + fromPath
        
        if not ignoreManifest and manifestXmlStr!=None:
            # Export a package
            # Update the manifest first!!!
            
            # copy the IMS manifest.xml
            ##self.io.write(self.io.join(toPath, "imsmanifest.xml"), manifestXmlStr)
            # and the DTD
            ##self.io.copy("imscp_rootv1p1.dtd", "/", toPath)
            
            dom = self.iceContext.Xml(manifestXmlStr, [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
            hrefs = dom.getContents("//x:resource/x:file/@href")
            
            ##if self.makeObjectUrlLocal:
            ##    self.objectFixup.setToPath(toPath)
        else: # else EXPORT ALL
            ##if ignoreManifest:
            ##    print "Ignoring manifest"
            ##else:
            ##    print "No '%s' file found in repository" % manifestPath
            ##print "Will just export the lot! from='%s'" % fromPath
            hrefs = self.__getListOfAllFilesToExport(fromPath)
            hrefs = [ p[len(fromPath):] for p in hrefs]
            ##toPath = self.io.join(toPath, fromPath[1:])
        
##        # export all referenced content
##        for relPath in hrefs:
##            path = self.io.join(fromPath, relPath)
##            #print "    path='%s'" % path
##            # export the items
##            result = self.__serve(path, None) ##self.io.join(toPath, relPath))
##            if result == False:
##                break
        if dom!=None:
            self.objectFixup.finished()
            dom.close()


    def __getListOfAllFilesToExport(self, fromPath):
        from http_util import Http
        # get root skin files
        rootSkinFiles = []
        for dirpath, dirnames, filenames in self.io.walk(self.io.rep.getAbsPath("/skin")):
            # root only
            while len(dirnames)>0:
                dirnames.pop()
            for name in filenames:
                rootSkinFiles.append(name)
        files = []
        
        templateFullPath = self.io.rep.getAbsPath(self.io.rep.documentTemplatesPath)
        exportFullPath = self.io.rep.exportPath
        
        absPath = self.io.rep.getAbsPath(fromPath)
        #Add index pages for all dirs BUT exclude hiddenDirectories (except the skin directories)
        for dirpath, dirnames, filenames in self.io.walk(absPath):
            dirpath = dirpath.replace("\\", "/")
            
            for dir in list(dirnames):
                rep = self.io.rep
                if dir.startswith(".") and dir!="skin":    # Exclude hidden directories
                    dirnames.remove(dir)
                    continue
                fullPath = self.io.join(dirpath, dir)
                # Exclude the templates path and the export's path (if it is located in the rep)
                if fullPath==templateFullPath or fullPath==exportFullPath:
                    dirnames.remove(dir)
                    continue
                # Exclude 'src' directories also
                if dir=="src":
                    dirnames.remove(dir)
            
            path = dirpath.replace(self.io.rep.getAbsPath("/"), "/")
            if path.endswith("/skin"):
                for fn in rootSkinFiles:
                    if fn not in filenames:
                        filenames.append(fn)                
            filename = self.io.join(path, "default.htm")
            files.append(filename)
            # HACK - for now just add a toc.htm (may or may not exist)
            filename = self.io.join(path, "toc.htm")
            files.append(filename)
            
            # include all other content (files)
            for file in filenames:
                if file.startswith("myChanges_"):   # skip myChanges_files
                    continue
                file = self.io.join(path, file)  #####
                item = self.io.rep.getItem(file)
                images = item.getMeta("images")
                isSlide = item.getMeta("isSlide")==True
                isSlide = False
                isPdf = item.hasPdf
                isHtml = item.hasHtml
                if images is None:
                    images = []
                #print "file='%s', images='%s', isSlide='%s', isPdf=%s" % (file, images, isSlide, isPdf)
                rawFile, ext = self.io.splitExt(file)
                
                if isHtml:
                    #currentMd5 = item.getCurrentMd5()
                    #lastMd5 = item.getMeta("lastMD5")                    
                    title = item.getMeta("title")
                    style = item.getMeta("style.css")
                    toc = item.getMeta("toc")
                    body = item.getRendition(".xhtml.body")
                    full = item.getRendition(".ALL.txt")
                    fedoraPrefix = "changeme"
                    currentPid = fedoraPrefix + ":" + item.guid
                    #if currentMd5 != lastMd5:
                    #    print "MD5 has changed"
                    try:
                        tempDir = self.io.createTempDir()
                        tempZipFile = self.iceContext.fs.join(str(tempDir), "fedora_export.zip")
                        relsExt = """
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rel="info:fedora/fedora-system:def/relations-external#" xmlns:ice="info:fedora/ice:def/meta#">
    <rdf:Description rdf:about="info:fedora/dummy">
        <rel:HasDescription>%s</rel:HasDescription>
        <ice:basePath>%s</ice:basePath>
        <ice:docPath>%s</ice:docPath>
    </rdf:Description>
</rdf:RDF>"""
                        docPath = rawFile[:rawFile.rfind("/") + 1]
                        print "docPath=%s" % docPath
                        zip = self.io.zipString()
                        zip.add("title.html", title)
                        zip.add("style.css", style)
                        zip.add("toc.html", toc)
                        zip.add("body.html", body)
                        zip.add("full.html", full)
                        zip.add("RELS-EXT", relsExt % (rawFile + ".htm", fromPath, docPath))
                        
                        for image in images:
                            data = item.getImage(image)
                            zip.add("img_" + image, data)
                        
                        data = zip.getZipData()
                        f = open(tempZipFile, 'w')
                        f.write(data)
                        f.close()
                        zip.close()
                        
                        username = "fedoraAdmin"
                        password = "fedoraAdmin"
                        http = Http()
                        f2 = open(tempZipFile, "rb")
                        wsurl = "http://localhost:8080/ice-fedora-module/ingest"
                        url = "http://localhost:8080/fedora"
                        print "calling ingest web service: currentPid=%s" % currentPid
                        result = http.post(wsurl, [("url", url), ("username", username), ("password", password), ("pid", currentPid), ("file", f2)])
                        print "called ingest web service"
                        print "result=[%s]" % result
                        start = result.find(" failed:")
                        if start > 0:
                            end = result.find("</p>", start)
                            print "fedora export failed: %s" % result[start+9:end]
                        else:
                            start = result.find("PID = ") + 6
                            end = result.find("</p>", start)
                            pid = result[start:end]
                    except Exception, e:
                        print "fedora export failed: %s" % e
                # End If isHtml:
                #HACK This used to work but now fails with fatal exceptions when exporting RUBRIC content
                try:
                    for image in images:
                        files.append(self.io.join(rawFile + "_files", image))
                except Exception, e:
                    print "warning: %s" % str(e)
                if self.iceContext.oooConvertExtensions.count(ext) > 0:
                     ext = '.htm'
                     if self.includeSource:
                         files.append(file)    # include the source file
                     file = rawFile + ext
                files.append(file)
                
                #Look for PDF rendition
                if isPdf:
                    file = rawFile + ".pdf"
                    files.append(file)
                if isSlide:
                    file = rawFile + ".slide.htm"
                    files.append(file)
        try:
            http = Http();
            wsurl = "http://localhost:8080/ice-fedora-module/processLinks"
            url = "http://localhost:8080/fedora"
            basePath = absPath
            result = http.post(wsurl, [("url", url), ("username", "fedoraAdmin"), ("password", "fedoraAdmin"), ("basePath", basePath)])
        except Exception, e:
            print "process links failed: %s" % e
        
        return files

    
    def __serve(self, path, toFileName):
        item = self.iceSite.rep.getItemForUri(path)
        data, mimeType = self.iceSite.serve(item, serverRequestData(path))
        if mimeType=="text/html":
            data = self.objectFixup.htmlFixup(data, toFileName)
        self.io.write(toFileName, data)
        return True


    def __preRenderMethod(self, iceSite):
        # HACK: Add <span/> to work around a firefox bug for empty elements
        iceSite["toolbar"] = "<span/>"        # remove the toolbar
        iceSite["statusbar"] = ""      # remove the statusbar
        iceSite["app-css"] = ""        # remove the application css


# HACK: make object elements data(url) references point to a local copy, so that
#    windows media files will work on CD export 
#       has to an absolute path to the media file and NOT a relative path
class FixupObjectUrls(object):
    def __init__(self, iceIO):
        self.__io = iceIO
        self.__fixExtList = [".avi", ".wmv", ".wma", ".wav"]
        self.__toPath = None
        self.__manifestPath = None
        self.__fixupList = []
        self.__mediaFiles = {}
        #print "FixupObjectsUrls.__init__()"
    
    def setToPath(self, toPath):
        toPath = toPath.replace("\\", "/")
        if not toPath.endswith("/"):
            toPath += "/"
        self.__toPath = toPath
        self.__manifestPath = toPath + "manifest.xml"
        #print
        #print " to manifest path = '%s'" % self.__manifestPath
        
    
    def htmlFixup(self, htmlStrData, toPath):
        if self.__toPath is None:
            return htmlStrData
        
        #print
        #print "***************************************************"
        #print "ice_export.FixupObjectUrls.htmlFixup( toPath='%s')" % (toPath)
        
        toPath = self.__io.split(toPath)[0] + "/"
        toPath = toPath[len(self.__toPath):]
        xhtml = None
        if True:
            # Note: Also replace links within the object element that have been changed
            
            # match all between <object and </object>
            reObject = re.compile("<object\s.*?</object>", re.DOTALL)
            # match the attribute data='xxx' capturing the dataValue as 'data' (groupdict()) (and quoted with 'quot')
            #   groups()[0] + groups()[1] + groups()[2] + groups()[1]
            reObjData = re.compile("(?P<f><object\s[^>]*?data\s*=\s*)(?P<quot>'|\")(?P<data>.*?)(?P=quot)", re.DOTALL)
            #
            #   groups()[0] + groups()[3] + groups()[4] + groups()[3]
            pattern = "(?P<f><param\s[^>]*?name\s*=\s*(?P<q>'|\")(?P<name>src|movie|url)(?P=q)[^>]*?value\s*=\s*)(?P<quot>'|\")(?P<value>.*?)(?P=quot)"
            reParamValue = re.compile(pattern, re.DOTALL)
            #
            #   groups()[0] + groups()[1] + groups()[2] + groups()[1]
            reEmbedSrc = re.compile("(?P<f><embed\s[^>]*?src\s*=\s*)(?P<quot>'|\")(?P<src>.*?)(?P=quot)", re.DOTALL)
            #
            #   groups()[0] + groups()[3] + groups()[2]
            hrefOrSrc = re.compile("((href|src)\s*=\s*(?P<quot>'|\"))(?P<content>.*?)(?P=quot)", re.DOTALL)
            
            fixupList = {}
            def objectMethod(match):
                fixupList.clear()
                rdata = match.group()
                #print "objectMethod match.group()="
                #print rdata
                #print
                rdata = reObjData.sub(objDataMethod, rdata)
                rdata = reParamValue.sub(paramValueMethod, rdata)
                #rdata = reEmbedSrc.sub(embedSrcMethod, rdata)
                if fixupList!={}:
                    print
                    print "fixupList='%s'" % str(fixupList)
                    rdata = hrefOrSrc.sub(hrefOrSrcMethod, rdata)
                return rdata
            
            def hrefOrSrcMethod(match):
                groups = match.groups()
                content = groups[3]
                newUrl = fixupList.get(content, None)
                if newUrl is not None:
                    content = newUrl
                    #print "@@  ", groups[1], content, groups[3]
                else:
                    pass
                    #print "@@  ", groups[1], content, "Not Fixed"
                rdata = groups[0] + content + groups[2]
                return rdata
            
            def paramValueMethod(match):
                #print "paramValueMethod %s" % match.group()
                groups = match.groups()
                value = groups[4]
                r, data = testFixup(groups[4])
                if r:
                    #print "  fixup data='%s'" % data
                    #rdata = groups[0] + groups[3] + groups[4] + groups[3]
                    rdata = groups[0] + groups[3] + data + groups[3]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print "  ERROR"
                #    #print "    '%s'" % match.group()
                #    #print "    '%s'" % rdata
                #    #print "    groups='%s'" % str(groups)
                return rdata
            
            def objDataMethod(match):
                #print "objDataMethod %s" % match.group()
                groups = match.groups()
                r, data = testFixup(groups[2])
                if r:
                    #print " fixup data='%s'" % data
                    #rdata = groups[0] + groups[1] + groups[2] + groups[1]
                    rdata = groups[0] + groups[1] + data + groups[1]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print " ERROR"
                return rdata
            
            def embedSrcMethod(match):
                #print "embedSrcMethod %s" % match.group()
                groups = match.groups()
                r, data = testFixup(groups[2])
                if r:
                    #print " fixup data='%s'" % data
                    #rdata = groups[0] + groups[1] + groups[2] + groups[1]
                    rdata = groups[0] + groups[1] + data + groups[1]
                else:
                    rdata = match.group()
                #if rdata!=match.group():
                #    print " ERROR"
                return rdata
            
            def testFixup(href):
                "Test if href needs to be fixed up"
                parts = href.split("?")
                url = parts[0]
                if self.__io.splitExt(url)[1] in self.__fixExtList:
                    content = href
                    parts = content.split("?")
                    url = parts[0]
                    if self.__io.splitExt(url)[1] in self.__fixExtList:
                        parts[0] = self.__io.split(url)[1]
                        toFile = toPath + self.__io.split(url)[1]
                        href = "?".join(parts)
                        x = self.__io.split(toFile)[0]
                        if x!="":
                            x += "/"
                        url = x + url
                        self.__fixupList.append( (url, toFile) )
                        if fixupList=={}:
                            fixupList[content] = href
                        #print "## %s - %s" % (content, href)
                        #print "##    %s - %s" % (url, toFile)
                    return True, href
                else:
                    return False, href
            
            htmlStrData = reObject.sub(objectMethod, htmlStrData)
        else:    
            # Note: Also replace links within the object element that have been changed
            try:
                xhtml = self.iceContext.Xml(htmlStrData)
                changed = False
                objNodes = xhtml.getNodes("//object")
                for objNode in objNodes:
                    nodes = objNode.getNodes("@data | param[@name='src' or @name='movie' or @name='url']/@value")
                    fixupList = {}
                    for n in nodes:
                        content = n.content
                        parts = content.split("?")
                        url = parts[0]
                        if self.__io.splitExt(url)[1] in self.__fixExtList:
                            if fixupList=={}:
                                print
                                print "==================="
                                print str(objNode)
                            parts[0] = self.__io.split(url)[1]
                            toFile = toPath + self.__io.split(url)[1]
                            n.content = "?".join(parts)
                            x = self.__io.split(toFile)[0]
                            if x!="":
                                x += "/"
                            url = x + url
                            self.__fixupList.append( (url, toFile) )
                            if fixupList=={}:
                                fixupList[content] = n.content
                            print "%s - %s" % (content, n.content)
                            print "    %s - %s" % (url, toFile)
                            changed = True
                    if fixupList!={}:
                        nodes = objNode.getNodes(".//@href | .//@src")
                        print len(nodes)
                        for n in nodes:
                            content = n.content
                            newUrl = fixupList.get(content, None)
                            if newUrl is not None:
                                n.content = newUrl
                                print n.getName(), content, n.content
                            else:
                                print n.getName(), content, "Not Fixed"
                        print "--------------"
                        print str(objNode)
                        print "==================="
                if changed:
                    htmlStrData = str(xhtml.getRootNode())            
            except Exception, e:
                print "XML error - '%s'" % str(e)
            if xhtml is not None:
                xhtml.close()
        
        #print " done ice_export.FixupObjectUrls.htmlFixup( toPath='%s')" % (toPath)
        return htmlStrData

    def finished(self):
        # now copy all referenced media files and fixup the manifest
        files = {}
        for f, t in self.__fixupList:
            self.__copy(self.__toPath + f, self.__toPath + t)
            files[self.__io.abspath(self.__toPath + f)] = None
        for f in files.keys():
            self.__io.remove(f)
        #print "FixupObjectsUrls.finished()"

    def __copy(self, fromFile, toFile):
        try:
            data = self.__io.read(fromFile)
            self.__io.write(toFile, data)
        except:
            print "Failed to copy from '%s' to '%s'" % (fromFile, toFile)









