#!/usr/bin/env python
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

pluginName = "ice.ooo.odtAddLinkEndnotes"
pluginDesc = "Add endnote links to odt files"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = AddLinkEndnotes
    pluginInitialized = True
    return pluginFunc




class AddLinkEndnotes(object):
    def __init__ (self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
    
    
    def addEndnotes(self, path):
        tempFs = self.__fs.unzipToTempDirectory(path)
        try:
            xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), 
                        self.iceContext.OOoNS.items())
            try:
                #for text with link
                self.__createEndNotes(xml, "//text:a")
                
                #for image with link
                self.__createEndNotes(xml, "//draw:a")
                
                #updateNodes
                xml=self.__updateNoteId(xml)
            finally:
                xml.saveFile() 
                xml.close()        
            tempFs.zip(self.__fs.absolutePath(path))
        finally:
            tempFs.delete()
        return "ok"
    
    
    def __createEndNotes(self, xml, linkNode):
            baseUrl = self.iceContext.siteBaseUrl
            baseUrl = baseUrl.rstrip("/")
            if baseUrl.find("http://")>-1:
                baseUrl = baseUrl.lstrip("http://")
            if baseUrl.find(":")>-1:
                base, port = baseUrl.split(":")
            nodes = xml.getNodes(linkNode)
            if nodes!=[]:       #Need to do checking if nodes is empty == no links in the document
                for node in nodes:
                    #Ignore nodes if internal link e.g. http://localhost 
                    #Need to re-code this as now is hardcoded
                    #Future: check for where ice located
                    ahref=node.getAttribute("href")
                    if ahref.find(base)>-1 or ahref.find(baseUrl)>-1:  ## or ahref.find("#")>-1: # so what if has a anchor?
                        pass
                        ##if there is Endnote, remove it
                        ## Why remove the Endnote?, it may have been required
                        ##if self.__isNextSiblingAnEndnote(node, ahref):
                        ##    node.getNextSibling().delete()
                    else:                
                        #Check if the Endnote for that link is existed, if yes, ignore
                        ##hasEndnote=False
                        ##nextSibling = node.getNextSibling()
                        ###If there is Endnote for the link ignore
                        ##if nextSibling != None:
                        ##    if nextSibling.getName() == "note":
                        ##        nextSiblingChildren = nextSibling.getNode("*[name()='text:note-body']")
                        ##        if ahref.strip() == nextSiblingChildren.getContent().strip():
                        ##            hasEndnote=True                                
                        ###if hasEndnote==False:   # No Endnote so create and add it
                        #ignore if its bookmark or anchor
                        parentStyleName = ""
                        parent = node.getParent()
                        if parent is not None:
                            parentStyleName = parent.getAttribute("style-name")
                        
                        if not ahref.startswith("#") and parentStyleName != "Footnote" and parentStyleName != "Endnote":
                            if not self.__isNextSiblingAnEndnote(node, ahref):
                                linkName=node.getAttribute("href")
                                #create text:p for body
                                pBody = xml.createElement("text:p", linkName)
                                pBody.setAttribute("text:style-name", "Endnote")
                                #create text:note-body element
                                noteBody = xml.createElement("text:note-body")
                                noteBody.addChild(pBody)
                                #create text:note-citation element
                                noteCitation = xml.createElement("text:note-citation")
                                #create text:note element
                                noteNode = xml.createElement("text:note")
                                noteNode.setAttribute("text:note-class", "endnote")            
                                noteNode.addChild(noteCitation)
                                noteNode.addChild(noteBody)
                                #add it
                                node.addNextSibling(noteNode)
    
    
    def __isNextSiblingAnEndnote(self, node, href):
        nextSibling=node.getNextSibling()
        if nextSibling is not None:
            if nextSibling.getName()=="note":
                nextSiblingChildren = nextSibling.getNode("*[name()='text:note-body']")
                if href.strip()==nextSiblingChildren.getContent().strip():
                    return True                                
        return False
    
    
    def __updateNoteId(self, xml):
        #ResetAllNumber
        try:
            nodes = xml.getNodes("//text:note[@text:note-class='endnote']")
            count=1
            for node in nodes:
                strCount="ftn" + str(count)
                if node.getAttribute("id") == None:
                    node.setAttribute("text:id", strCount)
                else:
                    node.setAttribute("id", strCount)
                noteCitation= node.getNode("*[name()='text:note-citation']")
                noteCitation.setContent(str(count))
                count+=1            
            return xml
        except:
            return None






















