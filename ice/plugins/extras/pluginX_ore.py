
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

import socket
try:
    from foresite import *
except ImportError, e:
    print "ORE plugin requires the foresite toolkit"
    raise e

pluginName = 'ice.extra.ORE'
pluginDesc = ''
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OREResourceMap
    pluginInitialized = True
    return pluginFunc


class OREResourceMap(object):
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__rep = self.iceContext.rep
        self.__baseUri = self.getBaseUri()
        self.__skinFiles = ["default.css",
                            "pdf.gif",
                            "slideicon.gif",
                            "previous.gif",
                            "up.gif",
                            "next.gif",
                            "magnifier.png",
                            "inactive_previous.gif",
                            "inactive_up.gif",
                            "inactive_next.gif",
                            "jquery.js",
                            "fancyzoom/bl.gif",
                            "fancyzoom/bl.png",
                            "fancyzoom/bm.gif",
                            "fancyzoom/bm.png",
                            "fancyzoom/br.gif",
                            "fancyzoom/br.png",
                            "fancyzoom/closebox.gif",
                            "fancyzoom/closebox.png",
                            "fancyzoom/fancyzoom.js",
                            "fancyzoom/ml.gif",
                            "fancyzoom/ml.png",
                            "fancyzoom/mr.gif",
                            "fancyzoom/mr.png",
                            "fancyzoom/tl.gif",
                            "fancyzoom/tl.png",
                            "fancyzoom/tm.gif",
                            "fancyzoom/tm.png",
                            "fancyzoom/tr.gif",
                            "fancyzoom/tr.png",
                            ]
    
    
    def getBaseUri(self):
        host = self.iceContext.settings.get('host', 'localhost')
        port = self.iceContext.settings.get('port', '8000')
        baseUri = ""
        try:
            repName = self.__rep.name
            if port == '80':
                baseUri = 'http://%s/rep.%s' % (host, repName)
            else:
                baseUri = 'http://%s:%s/rep.%s' % (host, port, repName)
        except: 
            pass
        return baseUri
    
    
    def getPackageRdfXml(self, path, manifest):
        name = self.__baseUri + path
        packagePath, filename, ext = self.iceContext.fs.splitPathFileExt(name)
        agg = Aggregation(name + '#aggregation')
        agg.format = 'application/rdf+xml'
        
        # entry page
        htmRes = self.__addResource(agg, packagePath + "/toc.htm?exportVersion=1", title="Contents")
        
        # metadata
        dcRes = self.__addResource(agg, packagePath + "/toc.dc")
        dcRes.conformsTo = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
        
        items = manifest.defaultOrganization.items
        for item in items:
            if item.isVisible:
                fullUri = self.iceContext.fs.join(packagePath, item.resource.href)
                baseUri, itemExt = self.iceContext.fs.splitExt(fullUri)
                if itemExt==".htm":
                    itemExt = ".rdf#aggregation"
                resource = self.__addResource(agg, baseUri + itemExt)
                resource.title = item.title
                resource.isDescribedBy = baseUri + ".rdf"
            else:
                relPath, _, _ = self.iceContext.fs.splitPathFileExt(path)
                itemUri = self.iceContext.fs.join(relPath, item.resource.href)
                item2 = self.iceContext.rep.getItemForUri(itemUri)
                fullUri = self.__baseUri + item2.relPath
                resource = self.__addResource(agg, fullUri, title=item2.getMeta("title"))
        
        # add basic skin files
        self.__addBasicSkinResources(agg)
        
        serializer = RdfLibSerializer('rdf')
        rem = agg.register_serialization(serializer, name)
        return agg.get_serialization().data
    
    
    def getDocumentRdfXml(self, item, convertedData=None):
        name = self.__baseUri + item.relPath
        baseName, ext = self.iceContext.fs.splitExt(name)
        if item is not None:
            agg = Aggregation(baseName + '.rdf#aggregation')
            title = item.getMeta('title')
            if title is None or title == '':
                title = '[Untitled]'
            agg.title = title
            agg.format = 'application/rdf+xml'
            serializer = RdfLibSerializer('rdf')
            
            # source doc
            sourceDocRes = self.__addResource(agg, name, title="Original document")
            
            # metadata
            dcRes = self.__addResource(agg, baseName + ".dc", title="Dublin Core Metadata")
            dcRes.conformsTo = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
            
            # add image resources
            images = item.getMeta("images")
            if images is not None:
                for image in images:
                    self.__addResource(agg, baseName + '_files/' + image, title="[image]")
            
            # add embedded/lightboxed links
            xmlStr = None
            if convertedData is not None:
                try:                
                    xmlStr = convertedData.getRendition(".xhtml.body")
                except Exception,e:
                    #print "Failed to find xhtml file for RDF rendition"
                    xmlStr = None
            
            if xmlStr is None:
                try :
                    xmlStr = item.getHtmlRendition()[0]
                except:
                    print "Error in Exporting Document: Cannot get .xhtml.body. Lightbox/Embedded Links are skipped."

            if xmlStr is not None:
                xml = self.iceContext.Xml(xmlStr)
                basePath = self.iceContext.fs.splitPathFileExt(name)[0]
                cmlLinks = xml.getNodes("//span[@class='jmolapplet']/applet/param[@name='load']")
                for cmlLink in cmlLinks:
                    value = cmlLink.getAttribute("value")
                    uri = basePath + "/" + value
                    self.__addResource(agg, uri)
                    # add png version
                    self.__addResource(agg, uri.replace(".cml", ".png"))
                xml.close()
            
            # add other renditions: html, pdf
            self.__addResource(agg, baseName + '.htm?exportVersion=1', 'text/html', title=title)
            self.__addResource(agg, baseName + '.pdf', title="%s (PDF)" % title)
            
            # add basic skin files
            self.__addBasicSkinResources(agg)
            self.__addSlideResources(agg, item)
            
            rem = agg.register_serialization(serializer, baseName + ".rdf")
            return agg.get_serialization().data
        else:
            raise Exception("* Can not find itemName for path '%s'" % item.relPath)
    
    
    def __addResource(self, aggregation, uri, mimeType=None, title=None):
        resource = AggregatedResource(uri)
        path, name, ext = self.iceContext.fs.splitPathFileExt(uri)
        if mimeType is None:
            if '#' in ext:
                ext = ext[:ext.find('#')]
            if '?' in ext:
                ext = ext[:ext.find('?')]
            mimeType = self.iceContext.getMimeTypeForExt(ext)
        if title is None:
            title = name + ext
        resource.format = mimeType
        resource.title = title
        aggregation.add_resource(resource)
        return resource
    
    
    def __addSkinResource(self, aggregation, filename):
        title = "[ICE.skin] %s" % filename 
        resource = self.__addResource(aggregation, "%s/skin/%s" % (self.__baseUri, filename), title=title)
        return resource
    
    
    def __addBasicSkinResources(self, aggregation):
        for filename in self.__skinFiles:
            self.__addSkinResource(aggregation, filename)
    
    
    def __addSlideResources(self, aggregation, item):
        if item.hasSlide:
            name = self.__baseUri + item.relPath
            baseName = self.iceContext.fs.splitExt(name)[0]
            self.__addResource(aggregation, "%s.slide.htm" % baseName, "text/html", title="Slideshow")
            self.__addSkinResource(aggregation, "slide/slide.css")
            self.__addSkinResource(aggregation, "slide/slideous.js")
    
    
