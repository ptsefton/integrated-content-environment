
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

""" """

from ooo2xhtml_utils import *
from ooo2xhtml_style import *
from ooo2xhtml_endfootnote_states import *


class officeDocumentContentState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts)
        #print "OfficeDocumentContentState"
    
    
    def characters(self, data):
        pass    # ignore any text data
    
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        #print "Finished officeDocumentContentState"
        pass
    


class bodyState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts)
    
    def characters(self, data):
        pass    # ignore any text data



class officeTextState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts)
    
    
    def characters(self, data):
        pass    # ignore any text data



class officeDocumentStylesState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts)
        #print "OfficeDocumentContentState"
    
    
    def characters(self, data):
        pass    # ignore any text data



class titleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        #print "=== titleState() ==="
        stateObject.__init__(self, parentState, name, atts)
    
    
    def processElement(self, name, attrs):
        #self.o.styles.printCssData()
        #print "=== titleState.processElement(name='%s')" % name
        p = element("p")
        self.stateElement = p        # Note: also set self.currentElement
        style = self.style
        if style is not None:
            p.setAttribute("class", style.name)
        a = element("a")
        id = self.getID()
        self.__id = id
        a.setAttribute("id", id)
        a.setAttribute("name", id)
        a.addChild(comment(id))
        p.addChild(a)

    #
    def createNewState(self, klass, name, attrs, style=None):
        #self.currentElement.addChild(self.data)
        #self.data = ""
        newState = klass(self, name, attrs, style=style)
        return newState
    #
    
    def endElement(self, name):
        self.currentElement.addChild(self.data)
        self.data = ""
    
    
    def closingState(self):
        if self.o.ignoreThisTitle(self):
            value = self.currentElement.value + self.data
            self.o.shtml.title = value
            self.rollback()
        else:
            self.currentElement.addChild(self.data)
            value = self.currentElement.value
        # set meta
        self.o.addMeta("title", value)

        #self.currentElement.addChild(self.data)
        #if self.__metaName is not None:
        #    value = self.currentElement.value
        #    self.o.addMeta(self.__metaName, value)
        #if self.style.textDisplay=="none":
        #    self.rollback()

pCount = 0

class paragraphState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        #print "=== paragraphState name='%s', style=%s" % (name, style)
        global pCount
        pCount += 1
        self.__pCount = pCount
        #print " pCount='%s'" % self.__pCount

        self.__metaName = None
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.maybeHidden = False


    def processElement(self, name, attrs):
		#print "para state"
        p = element("p")
        self.stateElement = p        # Note: also set self.currentElement
        style = self.style
        if style is not None:
            # check if this is a 'Caption'
            if (style.family=="Caption" or style.indirectName=="Caption" \
                or style.name=="Drawing" or style.name=="Illustration" \
                or style.name=="Table" or style.name=="Text"):
                print "**** Caption or Illustration found ***"
                #print style

                if style.styleName is not None:
                    styleName = style.styleName
                    ##print "  styleName='%s'" % styleName
                    parentStyleName = style.parentStyleName
                    if styleName!="Caption":                    
                        pStyle = self.o.styles.getOooStyle(parentStyleName)
                        ##print " pStyle='%s'" % pStyle
                        if pStyle.styleName is not None:
                            styleName = pStyle.styleName
                        if pStyle.parentStyleName is not None:
                            parentStyleName = pStyle.parentStyleName
                    cssClass = "%s.%s" % (parentStyleName, styleName)
                    ##print "   cssClass1='%s'" % cssClass
                    cssStyle = self.o.styles.getCssStyle(cssClass)
                    #print "   css=", cssStyle
                else:
                    cssClass = style.name
                    cssStyle = self.o.styles.getCssStyle(cssClass)
                if cssStyle is None:
                    cssStyle = ""
                #div = element("div")
                #div.setAttribute("style", cssStyle)
                #remove the div to get a valid xhtml output
                #div.addChild(p)
                #div.addChild(span)                
                p.setAttribute("class", cssClass)
                if cssStyle:
                    p.setAttribute("style", cssStyle)
                self.stateElement = p         # Note: also set self.currentElement
                self.currentElement = p
                
            elif style.type!="" and style.family!="bq":
               
                if style.name.startswith("p-meta"):
                    self.__metaName = style.name[len("p-meta-"):]
                p.setAttribute("class", style.type)
                
                elementStyle = ""
                if style.type=="nowrap":
                    elementStyle = "white-space: nowrap;"
                    #p.setAttribute("style", "white-space: nowrap;")
                styleName = style.styleName
                parentStyleName = style.parentStyleName
                cssClass = "%s.%s" % (parentStyleName, styleName)
                cssStyle = self.o.styles.getCssStyle(cssClass)
                
                if cssStyle:
                    elementStyle += cssStyle
                if elementStyle:
                    p.setAttribute("style", elementStyle)
            elif style.indirectName is not None and \
                    (style.family=="p" or style.family=="Table"):
                p.setAttribute("class", style.indirectName)
            else:
                pass
                #print "--NONE--"
        # Set the width of this 'frame' for captions
        if self.parentState.__class__.__name__=="frameState":
            width = self.convertUnits(self.parentState.attrs.get("svg:width", ""))
            #print "@ parent width='%s'" % width
            sattr = p.getAttribute("style")
            if sattr is None:
                p.setAttribute("style", "width:%spx;" % width)
            else:
                sattr.value += "width:%spx;" % width
    	
    def createNewState(self, klass, name, attrs, style=None):
        self.currentElement.addChild(self.data)
        self.data = ""
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        return newState
    
    
    def endElement(self, name):
        #print "+++endElement(%s) data='%s' %s" % (self.__pCount, self.data.strip(), self.depthCount)
        self.currentElement.addChild(self.data)
        self.data = ""
    
    
    def closingState(self):
        #print "++closingState(%s) data='%s'" % (self.__pCount, self.data.strip())
        self.currentElement.addChild(self.data)
        if self.__metaName is not None:
            value = self.currentElement.value
            self.o.addMeta(self.__metaName, value)
        if self.style.textDisplay=="none":
            self.rollback()
        if self.maybeHidden:
            def checkForNoContent(items):
                for item in items:
                    if item.value.isspace()==False and item.value != "":
                        return False
                    else:
                        return checkForNoContent(item.items)
                return True
            if checkForNoContent(self.currentElement.items):
                self.rollback()



class lineBreakState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def processElement(self, name, attrs):
        #self.stateElement = element("br")
        pass
    
    
    def closingState(self):
        self.currentElement.addChild(element("br"))



class tabState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def closingState(self):
        self.currentElement.addChild("    ")



class spanState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
	self.__metaName = None
        stateObject.__init__(self, parentState, name, atts, style=style)
    	
    
    def processElement(self, name, attrs):
        e2 = None
        style = self.style
        if name=="text:s":
            c = attrs.get("text:c", "1")
            try:
                c = int(c)
            except:
                c = 0
            #self.data = rawText("&#160;" * c)
            self.data = " " * c
        else:
            styleName = attrs.get("text:style-name", "")
            if style is not None:
                t = style.type
                name = style.name
                if name=="":
                    name = styleName
                if name.startswith("i-"):
                    
 		    if name.startswith("i-meta"):
                    	self.__metaName = name[len("i-meta-"):]
                    name = name[2:]
                css = self.o.styles.getCssStyle("span." + name)
                
                #if name=="T1":
                #    print
                #    self.o.styles.printCssData()
                #print
                ##print "span  %s t='%s'" % (str(props), t)
                #print "span type='%s' name='%s'" % (t, name)
                #print "  css='%s'" % css
                #print "  %s" % style.isItalic
                #print "  %s" % style
                
                stateElement = None
                currentElement = None
                if t=="code":
                    stateElement = element(t)
                    currentElement = stateElement
                if style.isBold:
                    css = css.replace("font-weight:bold; ", "")
                    e = element("b")
                    if stateElement is None:
                        stateElement = e
                    else:
                        currentElement.addChild(e)
                    currentElement = e
                if style.isItalic:
                    css = css.replace("font-style:italic; ", "")
                    e = element("i")
                    if stateElement is None:
                        stateElement = e
                    else:
                        currentElement.addChild(e)
                    currentElement = e
                
                if style.isSub:
                    css = css.replace("font-size: smaller; ", "")
                    css = css.replace("vertical-align: sub; ", "")
                    e = element ("sub")
                    if stateElement is None:
                        stateElement = e
                    else:
                        currentElement.addChild(e)
                    currentElement = e

                if style.isSuper:
                    css = css.replace("font-size: smaller; ", "")
                    css = css.replace("vertical-align: super; ", "")
                    e = element ("sup")
                    if stateElement is None:
                        stateElement = e
                    else:
                        currentElement.addChild(e)
                    currentElement = e
                
                if stateElement is None:    
                    stateElement = element("span")      # default
                    currentElement = stateElement       # default
                else:
                    pass
                
                if css!="" and name!="sub" and name!="sup":
                    stateElement.setAttribute("style", css)
                    s = element("span")
                    currentElement.addChild(s)
                    currentElement = s
                    
                if stateElement.name=="span" and name!="sub" and name!="sup":
                    if style.isDoubleLine:
                        #currentElement.setAttribute("class", name)
                        stateElement.setAttribute("class", name)
                    else:                 
                        currentElement.setAttribute("class", name)

                    
                self.stateElement = stateElement
                self.currentElement = currentElement

            else:
                self.stateElement = element("span")
	    name = style.name
	  
	 
	    
    	    if name.startswith("i-meta"):
	    	#self.stateElement.__metaName = name[len("i-meta-"):]
		#self.currentElement.__metaName = name[len("i-meta-"):]
		self.__metaName = name[len("i-meta-"):]
		
		
    
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if newState is not None:
            if self.data!="":
                self.currentElement.addChild(self.data)
                self.data = ""
        return newState
    
    
    def closingState(self):
	
	if self.__metaName is not None:
            value = self.data
	    print dir(self)
	    print value
            self.o.addMeta(self.__metaName, value)
	   
        if self.data!="":
            self.currentElement.addChild(self.data)
        if self.style.textDisplay=="none":
            parent = self.parentState
            while True:
                if parent.stateElement.name == "p":
                    parent.maybeHidden = True
                    break
                else:
                    parent =parent.parentState
            self.rollback()



class preState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
    
    
    def processElement(self, name, attrs):
        pre = element("pre")
        styleName = attrs.get("text:style-name", "")
        cssClass = "%s.%s" % (self.style.name, styleName)
        cssStyle = self.o.styles.getCssStyle(cssClass)
        
        isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
        if isItalic:
            i = element("i")
            if isBold:
                b = element("b")
                i.addChild(b)
                b.addChild(pre)
            else:
                i.addChild(pre)
            self.stateElement = i     
        elif isBold:
            b = element("b")
            if isItalic:
                i = element("i")
                b.addChild(i)
                i.addChild(pre)
            else:
                b.addChild(pre)
            self.stateElement = b
        else:
            self.stateElement = pre

        if otherStyle.strip() != "":
            pre.setAttribute("style", otherStyle)
            
        self.currentElement = pre    
        
        #self.stateElement =  element("pre")   # Note: also sets self.currentElement
    
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if isinstance(newState, preState):
            #self.data = ""
            #self.depthCount += 1
            #newState = self        # keep us as the new state
            newState.rollback()
            newState = None
        elif isinstance(newState, lineBreakState):
            newState.rollback()
            self.data += "\n"
            self.depthCount += 1
            newState = self        # keep us as the new state
        elif isinstance(newState, spanState) or \
            newState.__class__.__name__=="frameState" or \
            isinstance(newState, footnoteState) or \
            isinstance(newState, endnoteState):
            if self.data!="":
                self.currentElement.addChild(self.data)
                self.data = ""
            # child
            pass
        else:
            newState.rollback()
            newState = None
        return newState
    
    
    def startElement(self, name, attrs):
        #print "preState.startElement(%s)" % name
        if name=="text:tab":
            #print "adding tab"
            #self.currentElement.addChild(rawText("&#160;&#160;&#160;&#160;"))
            self.data += "    "
    
    
    def endElement(self, name):
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""
    
    
    def closingState(self):
        if self.currentElement.items==[]:
            c = comment("empty")
            self.currentElement.addChild(c)
        self.parentState.currentElement.addChild("\n")



class deletionState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__authorsName = ""
        self.__date = ""
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def processElement(self, name, attrs):
        div = element("div")
        div.setAttribute("class", "deletion")
        div.setAttribute("style", "color: red; text-decoration: line-through;")
        self.stateElement = div        # Note: also set self.currentElement
        
        div2 = element("div")
        div.addChild(div2)
        self.currentElement = div2
    
    
    def startElement(self, name, attrs):
        self.data = ""
    
    
    def endElement(self, name):
        if name=="dc:creator":
            self.__authorsName = self.data
        elif name=="dc:date":
            self.__date = self.data.replace("T", " ")
        elif name=="office:change-info":
            value = "Deletion: %s %s" % (self.__authorsName, self.__date)
            self.stateElement.setAttribute("title", value)



class annotationState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__authorsName = ""
        self.__date = ""
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    
    def processElement(self, name, attrs):
        div = element("div")
        div.setAttribute("class", "annotation")
        div.setAttribute("style", "color: black; border: 1px solid #C0C0C0; padding: 1px; margin: 1px; background: #F1F1F1; font-size: .9em;")
        self.stateElement = div        # Note: also set self.currentElement
        
        div2 = element("div")
        div.addChild(div2)
        self.currentElement = div2
    
    
    def startElement(self, name, attrs):
        self.data = ""
    
    
    def endElement(self, name):
        if name=="dc:creator":
            self.__authorsName = self.data
        elif name=="dc:date":
            self.__date = self.data.replace("T", " ")
            span = element("span")
            self.currentElement.addChild(span)
            span.setAttribute("class", "annotation-heading")
            span.setAttribute("style", "font-weight: bold;")
            span2 = element("span")
            span.addChild(span2)
            span2.addChild("Annotation: %s %s" % (self.__authorsName, self.__date))
    
    
    def closingState(self):
        s = self.currentElement.getFirstChild().getFirstChild()
        t = s.getFirstChild().value
        if t.startswith("Annotation: SciMarkup "):  # for oscar3 sci markup annotations
            self.rollback()

    
