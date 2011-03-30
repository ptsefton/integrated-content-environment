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


import re



class IceTemplateInfo(object):
    @staticmethod
    def getIceTemplateInfo(iceContext, xhtmlTemplate, isSlidePage, packagePath):
        templateData = IceTemplateInfo.__getTemplateData(iceContext, 
                                        xhtmlTemplate, isSlidePage, packagePath)
        iceTemplateInfo = IceTemplateInfo(iceContext, templateData)
        return iceTemplateInfo
    
    
    @staticmethod
    def __getTemplateData(iceContext, xhtmlTemplate, isSlidePage, packagePath):
        if isSlidePage:
            xhtmlTemplate = "slide/slide.xhtml"
        templateFile = iceContext.urlJoin(packagePath, "skin", xhtmlTemplate)        
        templateData = iceContext.rep.getItem(templateFile).read()
        if templateData==None:
            msg = "Failed to load the template. path='%s'" % templateFile
            raise Exception(msg)
        return templateData
    

    def __init__(self, iceContext, templateData):   # templatePath = 
        self.iceContext = iceContext
        self.__Xml = iceContext.Xml
        templateData = templateData.replace("%%", "%")  # support any already escaped '%' characters
        templateData = templateData.replace("%", "%%")  # escape any '%' characters
        self.__templateData = templateData
        self.__templateStr = None
        self.__templateHeader = ""
        self.__isXml = False
        self.__isSplashPage = False
        self.__splashTemplateStr = "*** SlashPage ***"
        self.__ins = {}
        self.__subs = {}
        self.__processTemplateData(templateData)
        if self.isXml==False:
            print "### Template is not well-formed XML ###"
    
    @property
    def templateString(self):
        return self.__templateStr
    
    @property
    def templateHeader(self):
        return self.__templateHeader
    
    @property
    def isXml(self):
        return self.__isXml
    
    @property
    def hasSplashData(self):
        return self.__isSplashPage
    
    @property
    def _replacementDict(self):
        keysDict = self.__subs.copy()
        keysDict.update(self.__ins)
        return keysDict
    
    
    def applyToTemplate(self, content):
        # Template -  Apply data to the template
        replacements = self._replacementDict
        replacements.update(content)
        title = self.iceContext.textToHtml(replacements.get("title", ""))
        replacements["title"] = title.replace("&#160;", " ")
        
        if content.isDefaultPage and self.hasSplashData:
            templateString = self.__splashTemplateStr
        else:
            templateString = self.__templateStr
        try:
            result = templateString % replacements
        except Exception, e:
            print "Error in applying content to the template. %s" % str(e)
            result = templateString
        return result
    
    
    def __processTemplateData(self, templateData):
        templateIsXml = True
        
        header = ""
        # remove any pre root element stuff including DOCTYPE (and PI's)
        headerRe = re.compile("^.*?(?=<\w)", re.DOTALL)
        class Sub(object):
            def __init__(self):
                self.header = ""
            def __call__(self, match):
                self.header = match.group()
                return ""
        sub = Sub()
        templateData = headerRe.sub(sub, templateData)
        self.__templateHeader = sub.header
        ## default value for docTypeStr
        #defaultDocTypeStr = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
        ## if no DOCTYPE then add the default DOCTYPE
        #docTypeRe = re.compile("<\!DOCTYPE\s[^>]*>")
        #if docTypeRe.search(header) is None:
        #    header += defaultDocTypeStr + "\n"
        
        #raise Exception("Testing")
        try:
            rawtemplate = self.__Xml(templateData)
        except Exception, e:
            errtmp = "<html><head><title>Error</title></head><body><div>%s</div></body></html>"
            tmp = "ERROR: load template failed - the given template or template file is not valid!"
            errtmp = errtmp % tmp
            rawtemplate = self.__Xml(errtmp)
        if rawtemplate.isHtml:
            self.__isXml = False
        else:
            self.__isXml = True
        
        insertions = rawtemplate.getNodes("//*[starts-with(@class,'ins ')]")
        for insert in insertions:
            classname = insert.getAttribute("class")[4:] # string after 'ins '
            # remove the 'ins '
            insert.setAttribute("class", classname)
            self.__ins[classname] = "<!--x-->"
            insert.setContent('%%(%s)s' % classname)
            
        # Splash page test
        splash = rawtemplate.getNode("//*[starts-with(@class, 'sub ice-splash')]")
        self.__isSplashPage = splash!=None
        if self.__isSplashPage:
            splash.setAttribute("class", splash.getAttribute("class")[4:])
            self.__splashData = str(splash)     # get the splash data
            splashParent = splash.getParent()
            splash.remove()
            
        substitutions = rawtemplate.getNodes("//*[starts-with(@class,'sub ')]")
        for sub in substitutions:
            attValue = sub.getAttribute("class")
            if attValue is not None:
                classname = attValue[4:] # string after 'sub '
                self.__subs[classname] = ""
                textNode = rawtemplate.createText("%(" + classname + ")s")
                sub.replace(textNode)
                sub.delete()
            else:
                try:
                    print "ERROR: failed to retrieve the 'class' attribute"
                    print "  for element '%s'" % sub.getName()
                except Exception, e:
                    pass
        
        # Remove the 'class' attribute from the title element to conform to xhtml - Ref#1876
        titleElem = rawtemplate.getNode("//head/title[@class]")
        if titleElem!=None:
            titleElem.removeAttribute("class")
        titleNode = rawtemplate.getNode("//head/title")
        if titleNode!=None:
            titleNode.setContent("%(title)s")
        
        self.__templateStr = str(rawtemplate.getRootNode())
        if self.__isSplashPage:
            for node in splashParent.getChildren():
                node.remove()
                node.delete()
            splashParent.addChild(splash)
            self.__splashTemplateStr = str(rawtemplate.getRootNode())
        rawtemplate.close()








