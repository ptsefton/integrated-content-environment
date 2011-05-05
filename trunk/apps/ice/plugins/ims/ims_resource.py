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



imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]

 
class ImsResource(object):
    # ImsResource
    #  Constructor:
    #    ImsResource(parent, href=None, resNode=None, includeSource=False)
    #  Properties:
    #    startPath (ReadOnly)
    #    identifier (ReadOnly)
    #    href (ReadOnly)
    #    repPath (ReadOnly)
    #    isWordDoc (ReadOnly)
    #    files (ReadOnly) []
    #    
    #  Methods:
    #    serialize(xml)
    #    
    #  Notes:
    #    A resource can be created by passing it a href(path relative to the package) to the resource or
    #      by passing it a resourse xml node
    def __init__(self, parent, href=None, resNode=None, includeSource=False, update=False):
        rep = parent.rep
        self.__parent = parent
        self.__includeSource = includeSource
        self.__identifier = None
        self.__href = None                # the href
        self.__repPath = None             # the path to the file in the repository with the corrent extension (e.g. .odt)
        self.__type = "webcontent"
        self.__files = None
        self.__exists = None
        
        if resNode!=None:
            self.__href = resNode.getAttribute("href")
            self.__identifier = resNode.getAttribute("identifier")
            if update==False:
                self.__files = []
                nodes = resNode.getNodes("*[name()='file']")
                for node in nodes:
                    fileHref = node.getAttribute("href")
                    self.__files.append(fileHref)
        elif href!=None:
            self.__href = href
        elif href==None:
            raise Exception("Either 'href' or 'resNode' parameter must be set!")
        if update:
            # sets __repPath, __exists and return files[]
            self.__files = self.__setup(self.__href, self.__includeSource)
        else:
            i = rep.getItemForUri(self.startPath + self.__href)
            self.__repPath = i.relPath
            if i.uriNotFound:
                #print "'%s' does not exist!" % self.__href, i.isFile
                self.__exists = False
                if self.__href=="toc.htm" or self.__href=="default.htm":
                    self.__repPath = self.startPath + self.__href
                else:
                    if self.__href.startswith("skin/") and \
                                    rep.getItem(self.__href).exists:
                        self.__exists = True
        if self.__identifier==None:
            self.__identifier = self.__parent.getIdFor(self.__href)
    
    
    @property
    def iceContext(self):
        return self.__parent.iceContext
    
    
    def __setup(self, href, includeSource):
        rep = self.__parent.rep
        startPath = self.startPath
        repPath = None
        files = []
        exists = True
        fs = self.iceContext.fs
        
        item = rep.getItemForUri(fs.join(startPath, href))
        repPath = item.relPath      ###
        #if item.uriNotFound and href.startswith("skin/"):
        #    repPath = href
        hname = fs.splitExt(href)[0]
        rname = self.iceContext.iceSplitExt(repPath)[0]
        if (item.isMissing or item.isFile==False or not rname.endswith(hname)):
            if href=="toc.htm" or href=="default.htm":
                files.append(href)
                repPath = startPath + href
            else:
                if href.startswith("http:") or href.startswith("https:"):
                    pass
                    #print "*ims_resource __setup href='%s'" % href
                    files.append(href)
                else:
                    print "MISSING - ImsResource - ", startPath + href
                    print "  item.isMissing='%s', item.isFile='%s', item.relPath='%s'" \
                            % (item.isMissing, item.isFile, item.relPath)
                    exists = False
        else:
            name, ext = self.iceContext.fs.splitExt(href)
            name2, srcExt = self.iceContext.fs.splitExt(repPath)        
            ext = item.ext
            
            if item.hasHtml:
                ext = ".htm"
            elif item.hasPdf:
                ext = ".pdf"
            href = name + ext
            if href!=self.__href:
                print "Warning: resetting href in ims_resource.__setup()"
                print " was '%s', now '%s'" % (self.__href, href)
                print " item.hasHtml='%s', item.name='%s' %s" % \
                    (item.hasHtml, item.name, item.hasXRendition(".htm"))
                self.__href = href
            
            files.append(href)
            if (name+srcExt) not in files:
                if includeSource or srcExt not in [".odt", ".doc"]:
                    files.append(name+srcExt)
            try:
                if item.hasPdf and not(ext==".pdf"):
                    files.append(name + ".pdf")
                ## Speech MP3 Audio rendition
                if item.getMeta("_renderAudio") and item.convertFlag:
                    files.append(name + ".mp3")
                if bool(item.getMeta("isSlide")):
                    files.append(name + ".slide.htm")
                images = item.getMeta("images")
                if images is not None and images!=[]:
                    images = item.getMeta("images")
                    if images is not None:
                        for image in images:
                            files.append(self.iceContext.fs.splitExt(href)[0] + "_files/" + image)
                render = self.iceContext.iceRender
                for ext in render.getRenderableTypes(item.ext):
                    if files.count(name + ext)==0:
                        files.append(name + ext)
            except Exception, e:
                raise
        #--------------------
        
        self.__repPath = repPath
        self.__exists = exists
        return files
    
    
    @property
    def startPath(self):
        return self.__parent.startPath
    
    
    @property
    def identifier(self):
        return self.__identifier
    
    
    @property
    def href(self):
        return self.__href
    
    
    @property 
    def repPath(self):
        return self.__repPath
    
    
    @property
    def exists(self):
        if self.__exists is None:
            self.__files = self.__setup(self.__href, self.__includeSource)
        return self.__exists
    
    
    @property
    def files(self):
        if self.__files is None:
            self.__files = self.__setup(self.__href, self.__includeSource)
        return self.__files
    
    
    @property
    def isWordDoc(self):
        if self.__repPath==None:
            return False
        return self.iceContext.fs.splitExt(self.__repPath)[1]==self.iceContext.wordExt or self.iceContext.fs.splitExt(self.__repPath)[1]==self.iceContext.word2007Ext
    
    
    def update(self):
        self.__files = self.__setup(self.__href, self.__includeSource)
    

    def serialize(self, xml):
        node = xml.createElement("resource", identifier=self.__identifier, type=self.__type, href=self.__href)
        node.addContent("\n")
        for file in self.files:
            n = xml.createElement("file", href=file)
            node.addChild(n)
            node.addContent("\n")
        return node


    def __str__(self):
        xml = self.iceContext.Xml("<root/>")
        s = str(self.serialize(xml))
        xml.close()
        return s




 