#
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

import re


pluginName = "ice.ooo.odtCreator"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OdtCreator
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    OdtCreator._path = path
    OdtCreator.blankOdt = iceContext.fs.join(path, "blank.odt")
    return pluginFunc



class OdtCreator(object):
    blankOdt = "blank.odt"
    
    class Style(object):
        @staticmethod
        def getStyles(content):
            styleElems = content.findallns("office:automatic-styles/style:style")
            sfamily = content.makens("style:family")
            sname = content.makens("style:name")
            sparentStyleName = content.makens("style:parent-style-name")
            smasterPageName = content.makens("style:master-page-name")
            
            styles = {}
            for styleElem in styleElems:
                attributes = styleElem.attrib
                name = attributes.get(sname, "")
                family = attributes.get(sfamily, "")
                parentStyleName = attributes.get(sparentStyleName, "")
                masterPageName = attributes.get(smasterPageName, "")
                styles[name] = OdtCreator.Style(name, family, parentStyleName, masterPageName)
            if not styles.has_key("Standard"):
                styles["Standard"] = OdtCreator.Style("Standard", "paragraph")
            return styles
        
        def __init__(self, name="", family="", parentStyleName="", masterPageName=""):
            self.name = name
            self.family = family
            self.parentStyleName = parentStyleName
            self.masterPageName = masterPageName
        
        def addStyle(self, content):
            stylesElem = content.findns("office:automatic-styles")
            attributes = {}
            styleNs = content.makens("style:")
            attributes[styleNs + "name"] = self.name
            attributes[styleNs + "family"] = self.family
            attributes[styleNs + "parent-style-name"] = self.parentStyleName
            if self.masterPageName!="":
                attributes[styleNs + "master-page-name"] = self.masterPageName
            
            styleElem = content.makeelementns("style:style", attributes)
            stylesElem.append(styleElem)
            
            #   fr1 - Frame1
            #<style:graphic-properties 
            #       style:run-through="foreground" 
            #       style:wrap="none" 
            #       style:horizontal-pos="center" 
            #       style:horizontal-rel="paragraph" 
            #       style:mirror="none" 
            #       fo:clip="rect(0cm 0cm 0cm 0cm)" 
            #       draw:luminance="0%" 
            #       draw:contrast="0%" 
            #       draw:red="0%" 
            #       draw:green="0%" 
            #       draw:blue="0%" 
            #       draw:gamma="100%" 
            #       draw:color-inversion="false" 
            #       draw:image-opacity="100%" 
            #       draw:color-mode="standard"/>
            if self.name=="fr1":            ## Hack
                styleNs = content.makens("style:")
                drawNs = content.makens("draw:")
                attributes = {
                                styleNs + "run-through":"forground",
                                styleNs + "wrap":"none",
                                styleNs + "horizontal-pos":"center",
                                styleNs + "horizontal-rel":"paragraph",
                                styleNs + "mirror":"none",
                                content.makens("fo:clip"):"rect(0cm 0cm 0cm 0cm)",
                                drawNs + "luminance":"0%",
                                drawNs + "contrast":"0%",
                                drawNs + "red":"0%",
                                drawNs + "green":"0%",
                                drawNs + "blue":"0%",
                                drawNs + "gamma":"100%",
                                drawNs + "color-inversion":"false",
                                drawNs + "image-opacity":"100%",
                                drawNs + "color-mode":"standard",
                             }
                g = content.makeelementns("style:graphic-properties", attributes)
                styleElem.append(g)
            else:
                attributes = {content.makens("style:page-number"):"auto"}
                paraProps = content.makeelementns("style:paragraph-properties", attributes)
                styleElem.append(paraProps)
            return styleElem
        
        def __str__(self):
            extra = ""
            if self.masterPageName!="":
                extra += ", masterPageName='%s'" % self.masterPageName
            return "[Style] name='%s', family='%s', parentStyleName='%s'%s" % \
                    (self.name, self.family, self.parentStyleName, extra)
    
    
    def __init__(self, iceContext, templateOdt=None):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs
        self.__et = self.iceContext.pyElementTree
        #if self.__et is None:
        #    self.__et = self.iceContext.ElementTree
        self.__ooons = {}
        for key, value in self.iceContext.OOoNS.iteritems():
            self.__ooons[key] = "{%s}" % value
            self.__et._namespace_map[value] = key
        
        # templateOdt
        self.__tempOdt = self.__fs.unzipToTempDirectory(self.blankOdt)
        
        self.__metaEt = None
        # extent ElementTree
        def makens(self, str):
            def mReplace(m):
                m = m.group()
                return self.ns.get(m[:-1], m)
            return re.sub("\w+\:", mReplace, str)
        def findns(self, xpath):
            return self.find(self.makens(xpath))
        def findallns(self, xpath):
            return self.findall(self.makens(xpath))
        def makeelementns(self, elemName, attr={}):
            return self.makeelement(self.makens(elemName), attr)
        self.__et._ElementInterface.ns = self.__ooons
        self.__et._ElementInterface.makens = makens
        self.__et._ElementInterface.findns = findns
        self.__et._ElementInterface.findallns = findallns
        self.__et._ElementInterface.makeelementns = makeelementns
        
        data = self.__tempOdt.readFile("content.xml")
        self.__content = self.__et.XML(data)
        self.__styles = self.Style.getStyles(self.__content)
        #for style in self.__styles.values():
        #    print style
        self.__officeText = self.__content.findns(".//office:body/office:text")
    
    
    @property
    def __meta(self):
        if self.__metaEt is None:
            data = self.__tempOdt.readFile("meta.xml")
            self.__metaEt = self.__et.XML(data)
        return self.__metaEt
    
    
    def close(self):
        self.__flush()
        self.__tempOdt.delete();
    
    
    def setTitle(self, title):
        self.setPropertyTitle(title)
        self.setDocumentTitle(title)
    
    
    def addParagraph(self, text):
        pElem = self.__makeParagraph(text=text)
        self.__officeText.append(pElem)
    
    
    def addImage(self, imageFilename, imageName="", imageData=None, linkHref=None):
        if imageData is None:
            imageData = self.__fs.readFile(imageFilename)
        ext = self.__fs.splitExt(imageFilename)[1]
        hexStr = self.iceContext.md5Hex(imageData)
        pictName = "Pictures/%s%s" % (hexStr.upper(), ext)
        self.__tempOdt.writeFile(pictName, imageData)
        if imageName is None or imageName=="":
            imageName = self.__fs.split(imageFilename)[1]
        imgElem = self.__makeImage(imageHref=pictName, imageName=imageName)
        p = self.__makeParagraph()
        if linkHref is not None:
            linkElem = self.__makeLinkElement(href=linkHref)
            linkElem.append(imgElem)
            p.append(linkElem)
        else:
            p.append(imgElem)
        self.__officeText.append(p)
    
    
    def setPropertyTitle(self, title):
        ns = self.__ooons
        meta = self.__meta
        titleElem = meta.findns(".//office:meta/dc:title")
        if titleElem is not None:
            titleElem.text = self.__textToXml(title)
        else:
            # Ok we need to create a new dc:title element
            dcTitleElem = meta.makeelementns("dc:title", {})
            dcTitleElem.text = self.__textToXml(title)
            meta.findns(".//office:meta").append(dcTitleElem)
    
    
    def setDocumentTitle(self, title):
        content = self.__content
        # find a style with a parentStyleName of "Title
        if False:
            styles = [s for s in self.__styles.values() if s.parentStyleName=="Title"]
            if len(styles)>0:
                titleStyle = styles[0]
            else:
                count = 1
                while self.__styles.has_key("P%s" % count): count+=1
                name = "P%s" % count
                titleStyle = self.Style(name, family="paragraph", parentStyleName="Title", masterPageName="Standard")
                self.__styles[name] = titleStyle
                titleStyle.addStyle(content)
            titleStyleName = titleStyle.name
        else:
            titleStyleName = "Title"
        textP = content.makens("text:p")
        textStyleName = content.makens("text:style-name")
        # Find the <text:p text:style-name='Title'> element
        pElem = None
        for child in self.__officeText.getchildren():
            if child.tag==textP and child.attrib.get(textStyleName, "")==titleStyleName:
                pElem = child
                break
        if pElem is not None:
            print "Replacing the Document Title"
            pElem.text = title
        else:       # else if not found then add it
            # get the index of the first text:p
            print "Creating a new Document Title"
            index = 0
            for child in self.__officeText.getchildren():
                if child.tag==textP:
                    break;
                index += 1
            # make the text:p element
            pElem = self.__makeParagraph(text=title, styleName=titleStyleName)
            self.__officeText.insert(index, pElem)
    
    
    def saveTo(self, file):
        self.__flush()
        self.__tempOdt.zip(self.__fs.absolutePath(file))
    
    
    def __makeParagraph(self, text="", styleName="p"):
        content = self.__content
        pElem = content.makeelementns("text:p", {content.makens("text:style-name"):styleName})
        if text!="":
            pElem.text = text
        return pElem
    
    
    def __makeLinkElement(self, href):
        content = self.__content
        attributes = {  content.makens("xlink:type"):"simple", 
                        content.makens("xlink:href"):href
                     }
        return content.makeelementns("draw:a", attributes)
    
    
    def __makeImage(self, imageHref, imageName=""):
        content = self.__content
        if not self.__styles.has_key("fr1"):
            print "Adding style 'fr1'"
            style = self.Style(name="fr1", family="graphic", parentStyleName="Graphics")
            s = style.addStyle(content)
            self.__styles[style.name] = style
        #frame
        attributes = {  content.makens("draw:style-name"):"fr1", 
                        content.makens("draw:name"):imageName,
                        content.makens("text-anchor-type"):"paragraph",
                        content.makens("svg:width"):"10cm",     ## ?????
                        content.makens("svg:height"):"8cm",     ## ?????
                        content.makens("draw:z-index"):"0",
                     }
        frame = content.makeelementns("draw:frame", attributes)
        #image
        attributes = {  content.makens("xlink:href"):imageHref, 
                        content.makens("xlink:type"):"simple",
                        content.makens("xlink:show"):"embed",
                        content.makens("xlink:actuate"):"onLoad",
                     }
        image = content.makeelementns("draw:image", attributes)
        frame.append(image)
        return frame
    
    
    def __flush(self):
        if self.__metaEt is not None:
            data = self.__et.tostring(self.__metaEt)
            self.__tempOdt.writeFile("meta.xml", data)
        if self.__content is not None:
            data = self.__et.tostring(self.__content)
            self.__tempOdt.writeFile("content.xml", data)
    
    
    def __textToXml(self, text):
        return self.iceContext.xmlEscape(text)

    









