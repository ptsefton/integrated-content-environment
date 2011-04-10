
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

from ooo2xhtml_utils import *
import types



class _oooStyle(object):
    # sample names - 'p', 'bq1', 'li1b'
    def __init__(self, name, indirectName=None, properties={}):
        self.__types = {"b":"bullet", "n":"number"}
                        #, "p":"paragraph", "a":"lowercaseAlpha", \
                        #"A":"uppercaseAlpha", "i":"lowercaseRoman", "I":"uppercaseRoman"}
        self.__family = ""
        self.__level = 0
        self.__type = ""
        self.__indirectName = indirectName
        self.__properties = properties
        if name is not None:
            self.__name = name
            self.__family, self.__level, self.__type = self.__getFamilyLevelType(name)
        else:
            self.__name = ""
        #if self.__name=="p":
        #    print "name='%s'" % self.__name
        #    print " %s"  % str(self.__properties)
    
    @property
    def styleName(self):
        n = str(self.__properties)
        return n
        
    @property
    def name(self):
        return self.__name
    
    @property
    def family(self):
        return self.__family
    
    @property
    def level(self):
        return self.__level
    def setNumbered(self):
	self.__type = "number"
    @property
    def type(self):
        return self.__type
    
    @property 
    def indirectName(self):
        return self.__indirectName
    
    @property
    def isTitle(self):
        return self.__family=="Title"
    
    @property
    def isBold(self):
        return self.__properties.get("fo:font-weight", "")=="bold" or \
                self.__name=="i-b" or self.__name=="i-bi"
    
    @property
    def isItalic(self):
        return self.__properties.get("fo:font-style", "")=="italic" or \
                self.__name=="i-i" or self.__name=="i-bi"
    
    @property
    def isUnderline(self):
        return self.__properties.get("style:text-underline-style", None) is not None or \
                self.__name=="i-underline"
    
    @property
    def isDoubleUnderline(self):
        return self.__properties.get("style:text-underline-type", "")=="double" or \
                self.__name=="i-double-underline"
    
    @property
    def isSub(self):
        return self.__properties.get("style:text-position", "").startswith("sub ") or \
                self.__name=="i-sub"
    
    @property
    def isSuper(self):
        return self.__properties.get("style:text-position", "").startswith("super ") or \
                self.__name=="i-sup"
    
    @property
    def isOutline(self):
        return self.__properties.get("style:text-outline", "")=="true"
    
    @property
    def isShadow(self):
        return self.__properties.get("fo:text-shadow", "")!=""
    
    @property
    def isSmallCaps(self):
        return self.__properties.get("fo:font-variant", "")=="small-caps"   #css font-variant:small-caps;
    
    @property
    def isStrikeThrough(self):
        return self.__properties.get("style:text-line-through-style", "")!=""
    
    @property
    def isDoubleLine(self):
        return self.__properties.get("style:text-underline-type", "")=="double"
    
    @property
    def color(self):
        return self.__properties.get("fo:color", "")
        return 
    
    @property
    def tableAlign(self):
        tableAlign = self.__properties.get("table:align", "")
        if tableAlign=="right" or tableAlign=="center":
            return tableAlign
        else:
            return "left"
    
    @property
    def verticalAlign(self):
        verticalAlign = self.__properties.get("style:vertical-align", "")
        if verticalAlign == "":
            verticalAlign = self.__properties.get("style:vertical-pos", "")
        if verticalAlign=="middle" or verticalAlign=="center" or verticalAlign=="bottom":
            #return "center"
        #elif verticalAlign=="bottom":
            return verticalAlign
        else:
            return "top"
    
    @property
    def columnWidth(self):
        return self.__properties.get("style:column-width", "")
    
    @property       # Refactor this (should not be needed!)
    def styleName(self):
        name = self.__properties.get("style:name", None)
        if name == "Footnote_20_Text":
            name = "Footnote"
        return name
    @property
    def parentStyleName(self):
        return self.__properties.get("style:parent-style-name", None)
    
    
    @property
    def textDisplay(self):
        return self.__properties.get("text:display", None)
    
    
    def resetType(self):
        self.__type = ""
    
    
    def isEqual(self, other):
        return self.__family==other.family and \
            self.__level==other.level and \
            self.__type==other.type
    
    
    def __getFamilyLevelType(self, name):
        # (family)(#level)-(type)
        match = re.match(r"^([^-\d]*)(\d+|)-?(.*)$", name)
        family, level, type = match.groups(1)
        try:
            level = int(level)
        except:
            level = 0
        if family=="" or family=="Standard":
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
        
        if type in self.__types and family!="i":
            type = self.__types[type]
        if type.startswith("_"):
            type = ""
        
        if type=="module":
            level += 1      #
        return family, level, type
    
    
    def __str__(self):
        s = "[_oooStyle] family='%s', level=%s, type='%s', name='%s'" % (self.__family, self.__level, self.__type, self.__name)
        s += "\n\tpropeties='%s'" % str(self.__properties)
        return s



class styles(object):
    # used by ooo2xhtml as the main collection of styles
    """  """
    def __init__(self, o):
        self.__o = o
        
        self.__oooStyles = {}               # a collection of oooStyle objects keyed by styleName
        self.__cssSelectorsValueList = []   # a list of tuples (cssSelector(styleGroup), cssStyleData(styleValue))
        self.__cssStyles = {}                # a collection css style data keyed by a selector e.g. span.bold
        
        self.__outlineLevelStyles = {}      # Used externally
        # set a default style for tables
        self.__setCssStyle(["table"], "border-spacing: 0;empty-cells: show; ")
        self.__setCssStyle([".body .indent"], "margin-left: 25px;")    #Added to support p-indent style
        self.__setCssStyle([".body .hint"], "font-size: 1.4em; font-style: normal;font-weight:bolder;color: #00000;") #for hint
        self.__setCssStyle([".spCh"], "font-family: 'Lucida Grande','Arial Unicode MS', sans-serif; font-size: 1.2em;")
        #
#        self.__setCssStyle(["span.sub"], "vertical-align:sub; font-size:smaller; ")
#        self.__setCssStyle(["span.sup"], "vertical-align:super; font-size:smaller; ")
        self.__setCssStyle(["span.underline"], "text-decoration:underline; ")
        
        # Removed double-underline style re:Ticket #5396
        #self.__setCssStyle(["span.double-underline"], "border-bottom: 1px solid; text-decoration: underline; padding-bottom: .2em; ")
    
    
    @property
    def outlineLevelStyles(self):
        return self.__outlineLevelStyles
    
    
    # only called by styleStyleState.closingState() method
    def setOooStyle(self, properties):
        styleName = properties.get("style:name", "")
        parentStyleName = properties.get("style:parent-style-name", "")
        #print
        #print "setOooStyle, styleName='%s', parentStyleName='%s', properties='%s'" % (styleName, parentStyleName, properties)
        if parentStyleName=="Graphics":
            parentStyleName = "img"
        if styleName == "Footnote_20_Text":
            styleName = "Footnote"
        style = _oooStyle(parentStyleName, indirectName=styleName, properties=properties)
        self.__oooStyles[styleName] = style
        
        try:
##            ##
##            test = False
##            if styleName=="P2" or styleName=="P3":
##                test = True
##            if test: print "Testing %s Step1" % styleName
##            ##
            arr = []
            for k, v in properties.items():
                if k.startswith("fo:") and k!="fo:clip" and k!="fo:break-before":
                    arr.append(k[3:] + ":" + properties[k])
                if k=="style:width":
                    if properties.get("style:rel-width", "")!="":
                        arr.append("width:%s" % properties.get("style:rel-width"))
                    else:
                        arr.append("width:" + properties[k])
            if style.isUnderline:
                arr.append ("text-decoration: underline")
                if style.isDoubleUnderline:
                    arr.append("border-bottom: 1px solid")
                    arr.append("padding-bottom: .2em")
            if style.isSub:
                arr.append("vertical-align: sub")
                arr.append("font-size: smaller")
            if style.isSuper:
                arr.append("vertical-align: super")
                arr.append("font-size: smaller") 
            if style.isOutline:
                #arr.append("outline: solid black 1px")
                pass
            if style.isStrikeThrough:
                arr.append("text-decoration: line-through")
            wrap = properties.get("style:wrap", "")
            if wrap=="parallel" or wrap=="dynamic":
                hpos = properties.get("style:horizontal-pos", "")
                if hpos.find("left")!=-1:
                    arr.append("float: left")
                elif hpos.find("right")!=-1:
                    arr.append("float: right")
            
            if len(arr)>0:
                arr.sort()
                cssName = self.__nameTranslate(styleName)
                if parentStyleName!="":     # "style:parent-style-name"
                    #if not style.isTitle:   # and is not a Title
                    if True:
                        if style.family.startswith("Table"):
                            parentStyleName = "p"
                            #return  # 'Table' so do nothing
                        sGroups = ["%s.%s" % (parentStyleName, cssName)]
                        sValue = string.join(arr, "; ") + "; "
                        self.__setCssStyle(sGroups, sValue)
                else:
                    if properties.get("style:family", "")=="table":
                        sGroups = ["table.%s" % (cssName)]
                    elif properties.get("style:family", "")=="table-cell":
                        sGroups = ["th.%s" % cssName, "td.%s" % cssName]
                        #arr.insert(0, "vertical-align: top") 
                    else:
                        sGroups = ["span.%s" % cssName]
                    sValue = string.join(arr, "; ") + "; "
                    
                    self.__setCssStyle(sGroups, sValue)
                    if properties.get("style:family", "")=="table":
                        self.__setCssStyle(["div.%s" % cssName], "width: 100%; margin: 0px; padding: 0px; ")
        except Exception, e:
            print " Error: '%s'" % str(e)
##        ##
##        print "styleName='%s'" % styleName
##        print "  isBold=%s, isItalic=%s" % (style.isBold, style.isItalic)
##        if test: self.printCssData()
##        print
##        ##
    
    
    def getOooStyle(self, name):
        if self.__oooStyles.has_key(name):
            s = self.__oooStyles[name]
        else:
            s = _oooStyle(name)
        return s
    
    
    def printCssData(self):
        for s, v in self.__cssSelectorsValueList:
            print "s='%s', v='%s'" % (s, v)
    
    
    def outputCssStyles(self):
        for s, v in self.__cssSelectorsValueList:
            #if s[0].isupper():     # Not an element name so must be a class(style) name
            #    s = "." + s
            #print "@ %s - %s" % (s, v)
            self.__o.shtml.addStyle(s, v)
    
    
    def getCssStyle(self, selector):
        return self.__cssStyles.get(selector, "")
    
    def getBlockStyle(self, cssStyle):
        #Support only for bold, italic and underline
        otherStyle = ""
        isItalic = False
        isBold = False
        if cssStyle:
            styleList = cssStyle.split(";")
            for eachStyle in styleList:
                eachStyleVal = eachStyle.split(":")
                if len(eachStyleVal) > 1:
                    #for font-style and font-weight only
                    styleAttr = eachStyleVal[0]
                    styleVal  = eachStyleVal[1]
                    if styleAttr.strip() == "font-style" and styleVal.strip() == "italic":
                        isItalic = True
                    elif styleAttr.strip() == "font-weight" and styleVal.strip() == "bold":
                        isBold = True
                    elif styleAttr.strip() == "text-decoration" and styleVal.strip() == "underline":
                        otherStyle += "%s:%s; " % (styleAttr, styleVal)
#                elif eachStyle!=None or eachStyle.strip() != "":
#                    otherStyle += eachStyle
        return isItalic, isBold, otherStyle
    
    #def __isStyleTitle(self, styleName):
    #    #properties = self.__styleNames.get(styleName, None)
    #    style = self.__oooStyles.get(styleName, None)
    #    if style is None:
    #        return False
    #    return style.family=="Title"
    
    
    def __nameTranslate(self, name):
        return name.replace(" ", "_").replace(".", "_")
    
    
    def __setCssStyle(self, styleGroup, styleValue):
        """ 
            styleGroup is a list of style selectors 
            styleValue the css style data
        """
        t = type(styleGroup)
        if t is not types.ListType and t is not types.TupleType:
            raise Exception("styles.__setCssStyle expects styleGroup parameter to be a list type!")
        
        for sGroup in styleGroup:
            s = self.__cssStyles.get(sGroup, "")
            s += styleValue
            self.__cssStyles[sGroup] = s
        styleGroups = ", ".join(styleGroup)
        self.__cssSelectorsValueList.append((styleGroups, styleValue))
    
    
    def __str__(self):
        s = "[styles object]\n"
        for key in self.__oooStyles.keys():
            s += "  '%s'='%s'" % (key, self.__oooStyles[key]) #, self.__oooStyles[key].properties)
        return s


#  ====   Style States   ====

class styleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        #print "styleState"
    
    
    def characters(self, data):
        # ignore any text data
        pass



class styleStyleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__styleProperties = {}
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def processElement(self, name, attrs):
        self.__addAtt(attrs)
    
    
    def startElement(self, name, attrs):
        if name.startswith("style:"):
            self.__addAtt(attrs)
    
    
    def __addAtt(self, attrs):
        for key in attrs.keys():
            try:
                self.__styleProperties[str(key)] = str(attrs.get(key))
            except Exception, e:
                # Unicode attribute HACK
                x = attrs.get(key)
                if type(x) is types.UnicodeType:
                    self.__styleProperties[str(key)] = str(x.encode("utf-16"))
                else:
                    raise e
    
    
    def characters(self, data):
        # ignore any text data
        pass
    
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        # update the styles object
        self.o.styles.setOooStyle(self.__styleProperties)




class outlineStyleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.outlineLevelStyles = self.o.styles.outlineLevelStyles



class outlineLevelStyleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def processElement(self, name, attrs):
        self.outlineLevel = int(attrs.get("text:level", "0"))
        self.numPrefix = attrs.get("style:num-prefix", "")
        self.numSuffix = attrs.get("style:num-suffix", "")
        self.numFormat = attrs.get("style:num-format", "1")
        self.startValue = int(attrs.get("text:start-value", "1"))
        x = int(self.outlineLevel)
        self.o.setHeadingLevelStartValue(x, self.startValue)
        self.displayLevels = attrs.get("text:display-levels", "1")
        self.parentState.outlineLevelStyles[self.outlineLevel] = self
    
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        pass
    
    
    def __str__(self):
        s = "[outlineLevelStyle] level='%s', numPrefix='%s', numSuffix='%s',\n" + \
            "numFormat='%s', startValue='%s', displayLevels='%s'"
        s = s % (self.outlineLevel, self.numPrefix, self.numSuffix, self.numFormat,
                  self.startValue, self.displayLevels)
        return s


class listStyleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.outlineLevelStyles = self.o.styles.outlineLevelStyles


class listLevelStyleState(outlineLevelStyleState):
    def __str__(self):
        s = "[listLevelStyle] level='%s', numPrefix='%s', numSuffix='%s',\n" + \
            "numFormat='%s', startValue='%s', displayLevels='%s'"
        s = s % (self.outlineLevel, self.numPrefix, self.numSuffix, self.numFormat,
                  self.startValue, self.displayLevels)
        return s




### for testing
##class getFamilyState(stateObject):
##    def __init__(self, parentState, name, atts, style=None):
##        stateObject.__init__(self, parentState, name, atts, style=style)
##    
##    
##    def processElement(self, name, attrs):
##        self.stateElement = element("f")
##    
##    
##    def closingState(self):
##        """ do any state finalization/cleanup here """
##        family = oooStyle(self.data).family
##        self.stateElement.addChild(family)
##
##
### for testing
##class getLevelState(stateObject):
##    def __init__(self, parentState, name, atts, style=None):
##        stateObject.__init__(self, parentState, name, atts, style=style)
##
##    def processElement(self, name, attrs):
##        self.stateElement = element("l")
##    
##    def closingState(self):
##        """ do any state finalization/cleanup here """
##        s = oooStyle(self.data)
##        level = s.level
##        self.stateElement.addChild(level)
##
##
### for testing
##class getHeadingLevelState(stateObject):
##    def __init__(self, parentState, name, atts, style=None):
##        stateObject.__init__(self, parentState, name, atts, style=style)
##
##    def processElement(self, name, attrs):
##        self.stateElement = element("l")
##    
##    def closingState(self):
##        """ do any state finalization/cleanup here """
##        s = oooStyle(self.data)
##        level = s.level
##        self.stateElement.addChild(level)
##
##
### for testing
##class getTypeState(stateObject):
##    def __init__(self, parentState, name, atts, style=None):
##        stateObject.__init__(self, parentState, name, atts, style=style)
##
##    def processElement(self, name, attrs):
##        self.stateElement = element("t")
##    
##    def closingState(self):
##        """ do any state finalization/cleanup here """
##        type = oooStyle(self.data).type
##        self.stateElement.addChild(type)







