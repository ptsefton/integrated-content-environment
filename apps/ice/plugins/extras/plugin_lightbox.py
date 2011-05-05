
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
import urllib

from uuid import uuid4


pluginName = "ice.extra.lightbox"
pluginDesc = "Lightbox"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Lightbox
    pluginInitialized = True
    return pluginFunc


class Lightbox(object):
    
    JQUERY_JS = "package-root/skin/jquery.js"
    LIGHTBOX_JS = "package-root/skin/fancyzoom/fancyzoom.js"
    externalFiles = ["skin/jquery.js", "skin/fancyzoom"]
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def addScript(self, xml):
        bodyNode = xml.getNode("/*[local-name()='html']/*[local-name()='body']")
        scriptNode = bodyNode.getNode("/*[local-name()='script' and @src='%s']" % self.LIGHTBOX_JS)
        
        if bodyNode is not None and scriptNode is None:
            jqueryNode = xml.createElement("script", type="text/javascript", src=self.JQUERY_JS)
            jqueryNode.addChild(xml.createComment(" "))
            bodyNode.addChild(jqueryNode)
            fancyzoomNode = xml.createElement("script", id="ice_fancyzoom_script", type="text/javascript", src=self.LIGHTBOX_JS)
            fancyzoomNode.addChild(xml.createComment(" "))
            bodyNode.addChild(fancyzoomNode)
    
    def processLink(self, xml, linkNode, contentNode):
        id = uuid4().hex
        linkNode.setAttribute("class", "lightbox")
        
        name = linkNode.getAttribute("href")
        filePath = ""
        try :
            filePath = name.split("?")[0]
            name = name.split("&title=")[1]
            name = name.split("&")[0]
            name = urllib.unquote_plus(name)
        except:
            name = ""

        contentNode.setAttribute("title",name)
        linkNode.setAttribute("title",name)
        iconNode = xml.createElement("span", "     ")
        iconNode.setAttribute("class", "lightbox-link")
        iconNode.addChild(xml.createComment(" "))
        linkNode.addChild(iconNode)
        captionNode = xml.createElement("p",name)
        captionNode.setAttribute("class","lightbox-caption")
        if contentNode.getName() == "div":
            contentNode.setAttribute("id", id)
            contentNode.addChild(captionNode)
            linkNode.addChild(contentNode)
        else:
            newDivNode = xml.createElement("div", id=id)
            newDivNode.addChild(contentNode)
            newDivNode.addChild(captionNode)
            linkNode.addChild(newDivNode)
        imgNode = linkNode.getFirstChild()
        if imgNode.getName() == "img" :
            imgNode.setAttribute("title",name)
        linkNode.setAttribute("href", "#" + id)
        try:
            packagePath = self.iceContext.iceSite.packagePath
        except:
            #if ice-service
            packagePath= ""
        if packagePath!="":
            # Note: this is bad code, assumes that the document is in a package
            #   and what if the document is moved!
            fileSplit = filePath.split(packagePath)
            if len(fileSplit)>1:
                filePath = fileSplit[1]
            mediaName = self.iceContext.fs.join(packagePath, filePath)
            item = self.iceContext.rep.getItem(mediaName)
            if item.isFile:
                if mediaName not in self.externalFiles:
                    self.externalFiles.append(mediaName)
            else:
                cmlName = self.iceContext.fs.splitExt(mediaName)[0] + ".cml"
                cmlItem= self.iceContext.rep.getItem(cmlName)
                if self.iceContext.fs.isFile(self.iceContext.rep.getAbsPath(cmlItem.relPath)):
                    self.externalFiles.append(cmlName)
                    pngFileName = '%s/rendition.png' % (cmlItem._propAbsPath)
                    if self.iceContext.fs.isFile(pngFileName):
                        if pngFileName not in self.externalFiles:
                            self.externalFiles.append(pngFileName)
        return linkNode, self.externalFiles
    

        



