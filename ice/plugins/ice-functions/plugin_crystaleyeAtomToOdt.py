
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

pluginName = "ice.function.CrystaleyeAtomFeedToODT"
pluginDesc = "Crystaleye Atomfeed to ODT"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    pluginFunc = CrystaleyeAtomToOdt
    pluginClass = None
    pluginInitialized = True
    return pluginFunc

    
def CrystaleyeAtomToOdt(self):
    path = self["argPath"]
    item = self.iceContext.rep.getItem(path)
    url = "http://wwmm.ch.cam.ac.uk/crystaleye/feed/atom/feed.xml"
    ex = Ex1(self.iceContext)
    ex.test(url, item, self.rep)

#CrystaleyeAtomToOdt.options = {"toolBarGroup":"advanced", "position":12, "postRequired":False,
#            "label":"Create crystaleye document", 
#            "title":"Create a Writer document from the Crystaleye atom feed."}




class Ex1(object):
    atomFeedNS = [ \
                ("dc", "http://purl.org/dc/elements/1.1/"), \
                ("atom", "http://www.w3.org/2005/Atom"), \
                ("xhtml", "http://www.w3.org/1999/xhtml"), \
             ]
    mimeTypes = {".cml": "chemical/x-cml", ".png":"image/png", ".gif":"image/gif"}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__Http = self.iceContext.Http
        self.__Xml = self.iceContext.Xml
        self.__fs = self.iceContext.fs
        print "self.__Http='%s'" % self.__Http
    
    
    def test(self, url, item=None, rep=None):
        # Xml
        print "Ex1.test() url='%s'" % url
        print " item.relPath='%s', item._absPath='%s'" % (item.relPath, item._absPath)
        http = self.__Http()
        atomXmlStr = http.get(url)
        if atomXmlStr is None:
            raise Exception("atomXmlStr is None")
        atomXml = self.__Xml(atomXmlStr, self.atomFeedNS)
        subtitleNode = atomXml.getNode("//atom:feed/atom:subtitle")
        if subtitleNode is not None:
            subTitle = subtitleNode.getContent()
        else:
            subTitle = "Result from crystaleye atom feed"
    
        entryNodes = atomXml.getNodes("//atom:feed/atom:entry")
        #print len(entryNodes)        
        
        plugin = self.iceContext.getPlugin("ice.ooo.odtCreator")
        if plugin is None:
            raise Exception("ice.ooo.odtCreator plugin not found!")
        odtCreator = plugin.pluginClass(self.iceContext)        #
        odtCreator.setTitle(subTitle)
        for entryNode in entryNodes:
            atomEntry = AtomEntry(entryNode)
            title = atomEntry.title
            imageHref = atomEntry.getLinkHref(self.mimeTypes[".png"])
            cmlHref = atomEntry.getLinkHref(self.mimeTypes[".cml"])
            #print " --- %s --- " % atomEntry.id
            #print imageHref
            #print
            odtCreator.addParagraph("")
            odtCreator.addParagraph(title)
            if imageHref is not None:
                name = self.__fs.split(imageHref)[1]
                imageData = http.get(imageHref)
                odtCreator.addImage(name, imageName=name, \
                    imageData=imageData, linkHref=cmlHref + "?embed=1")
        atomXml.close()
        filename = self.__fs.join(item._absPath, "CmlAtomFeed.odt")
        odtCreator.saveTo(filename)
        odtCreator.close()



class AtomEntry(object):
    def __init__(self, entryNode):
        self.__title = ""
        self.__id = None
        self.__updated = None
        self.__summary = ""
        self.__links = dict()
        try:
            self.__title = entryNode.getContent("*[local-name()='title']")
            self.__id = entryNode.getContent("*[local-name()='id']")
            self.__updated = entryNode.getContent("*[local-name()='updated']")
            self.__summary = entryNode.getContent("*[local-name()='summary']")
            for linkNode in entryNode.getNodes("*[local-name()='link']"):
                mimeType = linkNode.getAttribute("type")
                href = linkNode.getAttribute("href")
                self.__links[mimeType] = href
        except Exception, e:
            print "Exception in AtomEntry - '%s'" % str(e)
    
    @property
    def title(self):
        return self.__title
    
    @property 
    def id(self):
        return self.__id
    
    @property
    def summary(self):
        return self.__summary
    
    def getLinkHref(self, mimeType):
        return self.__links.get(mimeType, None)

