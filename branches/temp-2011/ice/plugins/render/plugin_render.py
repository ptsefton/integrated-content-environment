
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

pluginName = "ice.render"
pluginDesc = "Render - converts documents/files to other renditions"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceRender
    pluginInitialized = True
    return pluginFunc




class IceRender(object):
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   renderMethods               # e.g. {".odt":renderMethod, ".doc":renderMethod}
    #   postRenderPlugin
    # Methods:
    #   setPostRenderPlugin(postRenderMethod)
    #   getRenderableFrom(ext)      # -> []     e.g. (".htm") -> [".odt", ".doc"]
    #   getRenderableTypes(ext)     # -> []     e.g. (".odt") -> [".htm", ".pdf"]
    #   getRenderableExtensions()   # -> []
    #   isExtensionRenderable(ext)
    #   addRenderMethod(ext, (*)renderMethod, renditionExts)   # renderMethod*
    #   render(item, output=None)
    #
    #       (*)renderMethod()  [Wrong needs updating]
    #               message, renderedFiles = renderMethod(rep, filesToBeRendered, output=output)
    #                  message = "ok"
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__renderMethods = {}               # e.g. {".odt": [method1], ".doc": [method1, method2, methodN] }  
        self.__renderableTypes = {}             # e.g. {".odt":[".htm", ".pdf"], ".doc":[".htm", ".pdf"], ".odm":[".pdf"]}
        self.__renderableFromCollection = {}    # e.g. {".htm":[".odt", ".doc"] , ".pdf":[".odt", ".doc", ".odm"]}
        self.__viewableIcons = {}               # e.g. {".odt":{".rdf":False},".cml":{".png":True}}
        self.__renderedExtensions = []          # e.g. [".htm", ".pdf"]
        self.__postRenderPlugin = None
        self.__output = iceContext.output
        try:
            self.__loadRenderPlugins()
        except Exception, e:
            print "Failed to load RenderPlugins - '%s'" % str(e)
    
    
    def __loadRenderPlugins(self):
        # add plugin renders
        def addPluginRender(renderPlugin):
            renderPlugin.pluginInit(self.iceContext)
            try:
                Render = renderPlugin.pluginClass(self.iceContext)
            except Exception, e:
                print "Failed to initialize render plugin '%s' - '%s'" % (renderPlugin.pluginName, str(e))
                return
            for ext, toExts in Render.fromToExts.iteritems():
                try:
                    viewableIcon = False
                    if hasattr(Render, 'viewableIcon'):
                        viewableIcon = Render.viewableIcon
                    priority = False
                    if hasattr(Render, 'priority'):
                        priority = True
                    self.addRenderMethod(ext, Render.render, toExts, viewableIcon, priority)
                except Exception, e:
                    print "Error: failed to load '%s' render. - '%s'" % (renderPlugin.pluginName, str(e))
        for renderPlugin in self.iceContext.getPluginsOfType("ice.render."):
            addPluginRender(renderPlugin)
        settings = self.iceContext.settings
        testRenders = [name for name in settings.keys() if name.startswith("ice.test.render.")]
        for testRender in testRenders:
            if settings.get(testRender, False)==True:
                try:
                    renderPlugin = self.iceContext.getPlugin(testRender)
                    addPluginRender(renderPlugin)
                    print "* Using test render '%s'" % testRender
                except Exception, e:
                    print "Failed to load testRender '%s'" % testRender

    
    
    @property
    def renderMethods(self):            # e.g. {".odt":renderMethod, ".doc":renderMethod}
        return self.__renderMethods
    
    @property
    def postRenderPlugin(self):
        return self.__postRenderPlugin
    
    @property
    def renderedExtensions(self):
        return self.__renderedExtensions
    
    def setPostRenderPlugin(self, postRenderMethod):
        """ The postRenderMethods takes (repository, convertedData, documentType) as arguments and
              returns a ConvertedData object as the result. 
                (which may be the same as the convertedData argument or changed)
        """
        self.__postRenderPlugin = postRenderMethod
    
    
    def getRenderableFrom(self, ext):
        return self.__renderableFromCollection.get(ext, [])
    
    
    def getRenderableTypes(self, ext):
        return self.__renderableTypes.get(ext, [])
    
    
    def getRenderableExtensions(self):
        return self.__renderMethods.keys()
    
    
    def isExtensionRenderable(self, ext):
        return self.__renderMethods.has_key(ext)
    
    
    def hasViewableIcon(self, ext, toExt):
        return self.__viewableIcons.get(ext, {}).get(toExt, False)
    
    
    def addRenderMethod(self, ext, renderMethod, renditionExts, viewableIcon=False, priority=False):
        """ e.g. addRenderMethod(".odt", renderMethod, [".htm", ".pdf", ".txt"])
        """
        if ext in self.__renderMethods:
            if renderMethod not in self.__renderMethods[ext]:
                if priority:
                    self.__renderMethods[ext].insert(0, renderMethod)
                else:
                    self.__renderMethods[ext].append(renderMethod)
        else:
            self.__renderMethods[ext] = [renderMethod]

        if ext in self.__renderableTypes:
            self.__renderableTypes[ext].extend(renditionExts)
        else:
            self.__renderableTypes[ext] = renditionExts
        self.__renderableTypes[ext] = list(set(self.__renderableTypes[ext]))
        
        #self.__renderableFromCollection     # e.g. {".htm":[".odt", ".doc"] , ".pdf":[".odt", ".doc", ".odm"]}
        if ext not in self.__viewableIcons:
            self.__viewableIcons[ext] = {}
        for rType in renditionExts:
            self.__viewableIcons[ext][rType] = viewableIcon
            if self.__renderableFromCollection.has_key(rType):
                if ext not in self.__renderableFromCollection[rType]:
                    self.__renderableFromCollection[rType].append(ext)
            else:
                self.__renderableFromCollection[rType] = [ext]
        for rExt in renditionExts:
            if rExt not in self.__renderedExtensions:
                self.__renderedExtensions.append(rExt)
    
    
    # New reRender method
    def render(self, item, output=None, **kwargs):
        """ renders the given item and returns a ConvertedData object """
        if output is None:
            output = self.__output
        elif output==False:
            output = None
        if output is not None:
            output.write("\nProcessing file: - '%s'\n" % item.relPath)
        ext = item.ext           
        renderMethodsForExt = self.__renderMethods.get(ext, [])   # get the render methods
        if renderMethodsForExt==[]:
            if output is not None:
                output.write("*** Warning: no render method given for '%s' type files!\n" % ext)
                output.write("***   No registered render/converter to call!\n")
                output.write("***   Failed to render '%s'  ***\n" % item.relPath)
        convertedData = self.iceContext.ConvertedData()
        for renderMethod in renderMethodsForExt:
            result = ""
            failMessage = "Failed rendering '%s' " % item.relPath
            try:
                result = self.__render(item, renderMethod, output, convertedData, **kwargs)
            except Exception, e:
                #print self.iceContext.formattedTraceback()
                ex = str(e)
                msg = "Exception! Failed to render document '%s' - %s" % (item.relPath, ex)
                if output is not None:
                    output.write("#### %s\n%s####\n" % (msg, self.iceContext.formattedTraceback()))
                # Change to a more friendly error message for the user.
                if ext in [".odt", ".doc",".ods",".xls"]:
                    failMessage += "please restart OpenOffice and try again!"
                else:
                    failMessage += ex
                raise

        if result=="ok":
            self.__postRender(item, output, convertedData)
        return convertedData
    
    
    def __render(self, item, method, output, convertedData, **kwargs):
        """ Render a single item using the given render method. """
        try:
            try:
                method(item, convertedData, **kwargs)
            except:
                method(item, convertedData)
        except Exception, e:
            if output is not None:
                output.write("#############\n%s\n%s#############\n" % \
                        (str(e), self.iceContext.formattedTraceback()))
            raise
        errorMessage = convertedData.errorMessage
        
        if convertedData.terminalError==True:
            e = convertedData.Exception
        if errorMessage!="":
            if output is not None:
                output.write('errorMessage="%s"\n' % errorMessage)
            if errorMessage.find("Failed to connect to OpenOffice")>-1:
                msg = "Failed to connect to OpenOffice!\n  Please start OpenOffice and try again!"
                if output is not None: 
                    output.write(msg + "\n")
            elif errorMessage.find("Failed to save changes")>-1:
                msg = "Failed to save changes to Book!\n  Please close the document in OpenOffice and try again!"
                if output is not None: 
                    output.write(msg + "\n")
            elif errorMessage.find("Word document is Invalid")>-1: 
                msg = "Failed to render document. Word document is empty"
                if output is not None: 
                    output.write(msg + "\n")
            elif errorMessage.find("Open Office document is Invalid")>-1:
                msg = "Failed to render document. Open office document is empty"
                if output is not None: 
                    output.write(msg + "\n")
            else:
                msg =  "**** Failed to render the file! ****\n"
                msg += errorMessage
                if output is not None: output.write(msg + "\n")
                raise Exception(errorMessage)
            convertedData.close()
            return msg
        return "ok"
    
    
    def __postRender(self, item, output, convertedData):
        rep = self.iceContext.rep
        
        if callable(self.__postRenderPlugin):
            try:
                documentType = item.getMeta("documentType")
                convertedData = self.__postRenderPlugin(rep, convertedData, documentType)
            except Exception, e:
                if output is not None:
                    msg = "#############\n Error in postRenderPlugin callback: %s\n#############\n"
                    output.write(msg % str(e))
        
        # add table-of-contents
        #body = item.getRendition(".xhtml.body")
        if ".xhtml.body" in convertedData.renditionNames:
            body = convertedData.getRendition(".xhtml.body")
            levels = item.getMeta("_tocLevels", 2)
            toc = self.__generateToc(body, levels=levels,
                                isBook=(item.ext==".book.odt"), output=output)
            convertedData.addMeta("toc", toc)
        
        # HACK: for Slides (for now)
        if ".xhtml.body" in convertedData.renditionNames:
            data = convertedData.getRendition(".xhtml.body")
            xml = self.iceContext.Xml(data)
            node = xml.getNode("//div[@class='slide']")
            convertedData.addMeta("isSlide", node!=None)
            xml.close()
    
    
    def __generateToc(self, body, levels, isBook, output):
        #levels = 2          # 0, 1, 2, 3 or 4
        if body==None:
            return ""
        bodyXml = self.iceContext.Xml(body)
        xml = self.iceContext.Xml("<root/>")
        ul = None

        headings = []
        if isBook:
            nodes = bodyXml.getNodes("//p[@class='Title'] | //p[@class='Title-chapter'] |" + \
                                     "//h1[a/@name] | //h2[a/@name] | //h3[a/@name] | //h4[a/@name]")
            for n in nodes:
                name = n.getName()
                content = n.getContent()
                if name.startswith("h"):
                    lev = int(name[-1]) + 1
                    anchor = n.getNodes("a/@name")[0].getContent()
                else:
                    lev = 1
                    try:
                        anchor = n.getNodes("a/@name")[0].getContent()
                    except:
                        anchor = "?"
                headings.append((lev, content, anchor))
        else:
            nodes = bodyXml.getNodes("//h1[a/@name] | //h2[a/@name] | //h3[a/@name] | //h4[a/@name]")
            for n in nodes:
                name = n.getName()
                headings.append( (int(name[-1]), n.getContent(),
                                    n.getNodes("a/@name")[0].getContent()) )
        def processHeadings(level):
            ul = None
            liNode = None
            if level>levels:
                return None
            while len(headings)>0:
                heading = headings[0]
                headingLevel = heading[0]
                if headingLevel==level:
                    headings.pop(0)
                    liNode = xml.createElement("li")
                    aNode = xml.createElement("a", elementContent=heading[1], href="#"+heading[2])
                    liNode.addChild(aNode)
                    if ul is None:
                        ul = xml.createElement("ul")
                    ul.addChild(liNode)
                elif headingLevel<level:
                    break   # return
                elif headingLevel==level+1 and level<levels and liNode is not None:
                    liNode.addChild(processHeadings(level+1))
                else:
                    headings.pop(0)     # just ignore it
            return ul
        try:
            ul = processHeadings(1)
        except Exception, e:
            print "Error in __generateToc(): %s" % str(e)
        
        bodyXml.close()
        toc = ""
        if ul!=None:
            toc = str(ul)
        xml.close()
        return toc
    
    
    def __getTitleFromHtml(self, absHtmlFile):
        title = None
        try:
            xml = self.iceContext.Xml(absHtmlFile)
            title = xml.getContent("//*[local-name()='title']")
            xml.close()
        except:
            if xml!=None:
                xml.close()
        return title
    
    
    









