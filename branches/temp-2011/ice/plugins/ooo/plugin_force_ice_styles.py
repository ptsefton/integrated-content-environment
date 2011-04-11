
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

pluginName = "ice.ooo.cleanUpStyles"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = cleanUpStyles
    pluginInitialized = True
    return pluginFunc

class cleanUpStyles(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.xml  = None
        self.contentXml = None
        self.styleXml = None
        self.iceStylesList= []
        self.loadICEStyleXML()
    
    def __del__(self):
        self.xml.close()
        self.contentXml = None
        self.styleXml = None
        
    def loadICEStyleXML(self):
        #read from the file
        fileName = "iceStyles.xml"
        if self.iceContext.fs.isFile(fileName)==False:
            fileName = "plugins/ooo/"+fileName;
        if self.iceContext.fs.exists(fileName):
            absPath =self.iceContext.fs.absolutePath(fileName)
            self.xml = self.iceContext.Xml(absPath,self.iceContext.OOoNS.items())
            styleNodes = self.xml.getNodes("//style:style[@style:name]")
            if styleNodes != []:
                for styleNode in styleNodes:
                    styleName = styleNode.getAttribute("name")
                    self.iceStylesList.append(styleName)
                
            
                  
    def forceIceStyles(self,contentXml,styleXml):
#        print "in forceIceStyles"
        if contentXml is None:
            return contentXml,styleXml
        
        if self.iceStylesList == [] or self.xml is None:
            print "*** Cannot get ICE styles properties. Skipping..."
            return contentXml,styleXml

        self.contentXml = contentXml
        self.styleXml = styleXml
        
        outlineLists = []
        nodes = self.contentXml.getNodes("//*[@text:style-name!= '']")
        if nodes != []:
            for node in nodes:
                styleName = node.getAttribute("style-name")
                # can we get rid of this 
                paraType = "paragraph"
                if node.getName() == "h":
                    paraType = "heading"
                elif node.getParent().getName() == "list-item":
                    paraType = "list"
                # ----------------------------------
                if not self.isIceStyle(styleName):
                    #only if that is not ice style, then check whether base style is ICE Style
                    styleNode = self.contentXml.getNode("//style:style[@style:name='%s']" % styleName)
                    if styleNode is not None:
                        baseStyleName = styleNode.getAttribute("parent-style-name")
                        
                        if baseStyleName is not None:
                            if baseStyleName.find("Title")!=-1:
                                if node.getParent().getName() == "list-item":
                                    pass
#                                    #does not work yet.... Need to create something like Title-chapter so that we can copy
#                                    styleName = "Title-chapter"
#                                    self._copyICEStyle(styleName)
#                                    #node.setAttribute("style-name",styleName)
#                                    listNode = node.getParent().getParent()
#                                    if listNode.getName() == "list":
#                                        newNode =self.contentXml.createElement("text:h")
#                                        newNode.setAttribute("style-name",styleName)
#                                        newNode.setContent(node.getContent())
#                                        listNode.getParent().addChild(newNode)
#                                        listNode.remove()
#                                        print newNode.getParent()
#                                        
                                        
                         
                            elif not self.isIceStyle(baseStyleName):
				
                                styleName=self.checkInStyleXML(baseStyleName,paraType,styleNode)
				
                                family, _,_ =self.__getFamilyLevelType(styleName)
                                if family == "h" or family == "li":
                                    outlineLists.append(styleName)
#                                    style = self.fixupOutline(styleName,contentXml)
                                #set it directly to the paragraph
				    if family == "h":
					parentNode = self.styleXml.getNode("//style:style[@style:name='%s']" % baseStyleName)
					if parentNode:                       
						outlineLevel = parentNode.getAttribute("default-outline-level")
						if outlineLevel != None:
							outlineNode = self.styleXml.getNode("//text:outline-level-style[@text:level='%s']" % outlineLevel)
							if outlineNode!=None and outlineNode.getAttribute("num-format")!="": #TODO - other kinds of heading numbering?
								styleName = styleName + "n"

                                node.setAttribute("style-name",styleName)
                                       
                    else:
#                        print "style is not from content.xml"
                        styleName=self.checkInStyleXML(styleName,paraType,None)
                        family, _,_ =self.__getFamilyLevelType(styleName)
                        if family == "h" or family == "li" or family =="Title":
                            outlineLists.append(styleName)
                        node.setAttribute("style-name",styleName)
        if outlineLists != []:
            self.fixupOutline(outlineLists)
        self.contentXml.saveFile()
        self.styleXml.saveFile()
        return self.contentXml,self.styleXml

    def fixupOutline(self,styleNames):
        #todo this is not working
        # find out how to look up list and heading list
        # do i want to loop through everything or just the styles
        
        #in content.xml. outline list is defined as list within a list
#        <text:list xml:id="list29395025" text:style-name="WW8Num1">
#            <text:list-item>
#                <text:p text:style-name="P2">Outline level 1</text:p>
#                <text:list>
#                    <text:list-item>
#                        <text:p text:style-name="P1">Outline level 2</text:p>
#                        <text:list>
#                            <text:list-item>
#                                <text:p text:style-name="P1">Ouline Level 3</text:p>
#                            </text:list-item>
#                        </text:list>
#                    </text:list-item>
#                </text:list>
#            </text:list-item>
#        </text:list>
        for styleName in styleNames:
            nodes = self.contentXml.getNodes("//*[@text:style-name='%s']"%styleName)
            for node in nodes:
                count = 0
                parentNode = node.getParent()
                    
                if parentNode.getName()=="list-item":
                    family, _,type =self.__getFamilyLevelType(styleName)
                    if family == "Title":
                        count="-"
                        type="chapter"
                    else: 
                        def getLevel(n,curNode):
                            parentNode =curNode.getParent() 
                            if parentNode.getName() != "text":
                                n = getLevel(n,parentNode)
                            if parentNode.getName() == "list":
                                n = n + 1 
                            return n 
                        def getListName():
                            parentNode = node
                            listStyleName = None
                            while True:
                                parentNode = parentNode.getParent()
                                if parentNode.getName() == "list":
                                    listStyleName = parentNode.getAttribute("style-name")
                                if listStyleName is not None:
                                    break
                            return listStyleName
                        def getType():
                            styleNode = self.styleXml.getNode("//text:list-style[@style:name='%s']/*[@text:level='%s']"%(listStyleName,count))
                            if styleNode is not None:
                                type = styleNode.getAttribute("num-format")
                                if type =='1':
                                    type = "n"
                                if type is None:
                                    #check if this is bullet
                                    if styleNode.getAttribute("bullet-char") is not None:
                                        type = "b"
                                return type
                            else:
                                #check in content.xml
                                styleNode = self.contentXml.getNode("//text:list-style[@style:name='%s']/*[@text:level='%s']"%(listStyleName,count))
                                if styleNode is None:
                                    return "unknown"
                                else:
                                    type = styleNode.getAttribute("num-format")
                                    if type =='1':
                                        type = "n"
                                    if type is None:
                                        #check if this is bullet
                                        if styleNode.getAttribute("bullet-char") is not None:
                                            type = "b"
                                    return type





                        count= getLevel(count,node)
                        if count == 0:
                            count = 1
                        if count > 5:
                            count = 5
                        if family =="h":
                            type ="n"
                        else:
                            listStyleName = getListName()
                            listTypes = ['n','i','a','I','A','b']
                            
                            if family == "li" and type!="b":
                                #if numbering list
                                type = listTypes[count-1]
                            if listStyleName != None:
                                type = getType()
                            if not type in listTypes:
                                type = listTypes[count-1]
                    
                    styleName = "%s%s%s" %(family,count,type)
                    self._copyICEStyle(styleName)
                    ##print styleName
                    node.setAttribute("style-name",styleName)
                    #print node
        #        print "##################"
                
        self.contentXml.saveFile()
#        print 'done fixing up outline'
        
        
        
            
    def checkInStyleXML(self,styleName,paraType,contentStyleNode):
        ###print "checkIn STyleXML"
        node = self.styleXml.getNode("//style:style[@style:name='%s']" % styleName)
        if node is not None:
            styleDisplayName = node.getAttribute("display-name")
            if styleDisplayName is None:
                styleDisplayName = styleName
            if not self.isIceStyle(styleDisplayName):
                 #if not ice style Then add the relevant ice style
                 iceStyleName = self.getthisIceStyleName(styleDisplayName,paraType,contentStyleNode)
                 def getListType(listName):
                    list = self.styleXml.getNode("//text:list-style[@style:name='%s']" % listName)
                    listType= "n"
                    if list is not None:
                        firstChild = list.getFirstChild()
                        if firstChild.getName().lower().find("bullet")!= -1:
                            listType = "b"
                        else:
                            #if numbering 
                            listType = firstChild.getAttribute("num-format")
                            if listType == "1":
                                listType = "n"
                    return listType
                 
                 if contentStyleNode is not None and iceStyleName != "Title-chapter":
                     #for word list styles
                     listStyleName = contentStyleNode.getAttribute("list-style-name")
                     if listStyleName is not None:
                         parentStyleName = contentStyleNode.getAttribute("parent-style-name")
                         if parentStyleName.lower().find("heading")!= -1:
                             iceStyleName = iceStyleName+"n"
                         else:
                             #todo make the list
                             type = getListType(listStyleName)
                             iceStyleName = "li1"+type
                 elif iceStyleName[0]=="h":
                     #check if this is number or not.
                     outline = self.styleXml.getNode("//text:outline-style[@style:name='Outline']")
                     if outline is not None:
                         outlineStyleName = outline.getFirstChild().getAttribute("style-name")
                         if outlineStyleName is not None:
                             if outlineStyleName.lower().find("num")!=-1:
                                 iceStyleName =iceStyleName+"n"
                 styleName = iceStyleName
                 self._copyICEStyle(styleName)            
#                 iceStyleNode = self.styleXml.getNode("//style:style[@style:name='%s']" % iceStyleName)     
#                 if iceStyleNode is None:
#                     # if the node does not exist:
##                     styleNode =  self.xml.getNode("//style:style[@style:name='%s']" % iceStyleName)
##                     if styleNode is not None:
##                         node.getParent().addChild(styleNode)
##                         iceStyleNode = self.styleXml.getNode("//style:style[@style:name='%s']" % iceStyleName)
##                         
##                         styleName = iceStyleName
##                     else:
##                         #what is the icestyle doesnot exists????
##                         styleName = "standard"
#                 else:
#                    ##print "styleNode exits, so not addding"
#                    styleName = iceStyleName
        return styleName
    
    
    def _copyICEStyle(self, styleName):
        testNode = self.styleXml.getNode("//style:style[@style:name='%s']" % styleName)
        if testNode is None:
            # not exist in style.xml
            styleNode =  self.xml.getNode("//style:style[@style:name='%s']" % styleName)
            if styleNode is not None:
                stylesNode = self.styleXml.getNode("//office:styles")
                if stylesNode is not None and styleNode is not None:
                    stylesNode.addChild(styleNode)
            
#            node.getParent().addChild(styleNode)
#            iceStyleNode = styleXml.getNode("//style:style[@style:name='%s']" % styleName)

    
    def getthisIceStyleName(self,styleName,paraType,contentStyleNode):
        #todo see how openoffice define the outlinestyle
        iceStyleName = styleName
        #to do make makestylename function that is intelligent enough to create the style
        if paraType == "list" or  styleName.lower().find("list") != -1:
            if styleName.lower().find("title") != -1:
                iceStyleName = "Title-chapter"
            else:
                iceStyleName = "li1p"
            #todo catch if it is a list.
        elif styleName.lower().find("title") != -1:
            iceStyleName = "Title"
        elif paraType =="heading" or styleName.lower().find("heading") != -1:
            #TODO: find out if heading is numbered
            family = "h"
            try:
		#TODO - try with a regex to improve match
                level = int(styleName.split(" ")[1])
            except:
                level = 0
            if level > 5:
                level = 5
            if level < 1:
                level = 1
            iceStyleName = "%s%s" % (family,level) #Flag this as an unknown style	
	  
	  

	  
        elif styleName.lower().find("p-meta") != -1:
	    iceStyleName = styleName
        elif styleName.lower().find("quote") != -1:
            iceStyleName ="bq1"
        elif styleName.lower().find("title") != -1 and styleName.lower().find("subtitle")==-1:
            iceStyleName = styleName
	#TODO: ptsefton - why are para and char styles mixed up here?
        elif styleName.lower().find("emphasis") != -1 and styleName.lower().find("strong") != -1:
            iceStyleName="i-bi" 
  	elif styleName.lower().find("i-") != -1:
            iceStyleName = styleName
        elif styleName.lower().find("emphasis") != -1:
            iceStyleName = "i-i"
        elif styleName.lower().find("strong") != -1:
            iceStyleName = "i-b"
        elif styleName.lower().find("reference") != -1:
            iceStyleName = "xRef-RefText"
        else:
            iceStyleName = 'p'
            if contentStyleNode is not None:
                paraProps = contentStyleNode.getChildren()
                for child in paraProps:
                     if  child.getName() == "paragraph-properties": 
                        if child.getAttribute("text-align") == "center":
                            iceStyleName = "p-center"
                        elif child.getAttribute("text-align") == "end":
                            iceStyleName = "p-right"
                        elif child.getAttribute("margin-left") != "0cm":
                            iceStyleName = "p-indent"
        return iceStyleName
        
    
    def isIceStyle(self,styleName):
        #maybe i cann call this function from baseconverter to check the document
        if styleName in self.iceStylesList:
            return True
        else:
            return False

    def __getFamilyLevelType(self, name):
        
        # only work with ICE styles
        import re
        # (family)(#level)-(type)
        match = re.match(r"^([^-\d]*)(\d+|)-?(.*)$", name)
        family, level, type = match.groups(1)
        try:
            level = int(level)
        except:
            level = 0
        if family=="":
            family = "p"
        elif family=="Illustration":
            family = "p"
            type = "l"      # 'L'
        elif family=="Table_":
            family = "Table"
            level = 0
            type = type[1:]
        elif family == "Footnote_":
            family = "Footnote"
        elif family=="h" or family=="pre" or family=="bq":
            pass

        if type.startswith("_"):
            type = ""
        
        return family, level, type
    
    
    
