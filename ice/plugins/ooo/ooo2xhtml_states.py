
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
from ooo2xhtml_basic_states import *
 
splitPathFileExt = None


class headingState(stateObject):
    def __init__(self, parentState, name, atts, style):
        self.__metaName = None
        stateObject.__init__(self, parentState, name, atts, style=style)
        #print "HeadingState style='%s'" % style

    def processElement(self, name, attrs):
        style = self.style
        if style is None:
            styleName = attrs.get("text:style-name", "")
            style = self.o.styles.getOooStyle(styleName)
            self.style = style
            
        level = style.level
        outlineLevel = attrs.get("text:outline-level", "")
        outlineLevelStyle = None
        
        styleName = attrs.get("text:style-name", "")
        cssClass = "%s.%s" % (self.style.name, styleName)
        cssStyle = self.o.styles.getCssStyle(cssClass)
        
        if outlineLevel!="":
            outlineLevelStyle = self.o.styles.outlineLevelStyles.get(int(outlineLevel))
            #print "* Heading outlineLevel=%s, %s" % (outlineLevel, outlineLevelStyle)
        
        #print "style=", str(style)
        if style.type!="":
            # HACK
            parent = self.parentState
            topTable = None
            while parent is not None:
                if hasattr(parent, "addClass"):
                    topTable = parent
                parent = parent.parentState
            if topTable is not None:
                topTable.addClass(style.type)
        #div = element("div")
        if style.level==0:
            h = element(style.family + "6")
        else:
            h = element(style.family + str(style.level))
                    
        a = element("a")
        id = self.getID()
        self.__id = id
        a.setAttribute("id", id)
        #a.setAttribute("name", id)
        a.addChild(comment(id))
        h.addChild(a)
        if style.type=="number":
            numSuffix = " "
            numPrefix = ""
            startValue = ""
            displayLevels = level
            if outlineLevelStyle is not None:
                numSuffix = outlineLevelStyle.numSuffix
                numPrefix = outlineLevelStyle.numPrefix
                displayLevels = int(outlineLevelStyle.displayLevels)
                level = outlineLevelStyle.outlineLevel
                #print "displayLevels=%s, level=%s" % (displayLevels, level)
                if outlineLevelStyle.numFormat=="":
                    displayLevels = 0
                    numSuffix = ""
                    numPrefix = ""
            
            self.__rb_level = level
            self.__rb_currentLevel = self.o.currentHeadingLevel
            self.__rb_headingNumber = self.o.currentHeadingNumber[level]
            if level > self.o.currentHeadingLevel:
                self.o.currentHeadingLevel = level
                self.o.getCurrentHeadingLevelStartValue()
            elif level < self.o.currentHeadingLevel:
                self.o.currentHeadingLevel = level
                self.o.currentHeadingNumber[level] += 1
            else:
                self.o.currentHeadingNumber[level] += 1
            
            numStr = ""
            for x in range(level-displayLevels, level):
                n = self.o.currentHeadingNumber[x+1]
                numStr += str(n) + "."
            h.addChild(numPrefix + numStr[:-1] + numSuffix)
            
        
        isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
        if isItalic:
            i = element("i")
            if isBold:
                b = element("b")
                i.addChild(b)
                b.addChild(h)
            else:
                i.addChild(h)
            self.stateElement = i     
        elif isBold:
            b = element("b")
            if isItalic:
                i = element("i")
                b.addChild(i)
                i.addChild(h)
            else:
                b.addChild(h)
            self.stateElement = b
        else:
            self.stateElement = h

        if otherStyle.strip() != "":
            h.setAttribute("style", otherStyle)
            
        
        self.currentElement = h    
    
    def rollback(self):
        #print "headingState.rollback() %s" % self.__id
        try:
            self.o.currentHeadingLevel = self.__rb_currentLevel
            self.o.currentHeadingNumber[self.__rb_level] = self.__rb_headingNumber
        except:
            pass
    
    def endElement(self, name):
        self.currentElement.addChild(self.data)
        self.data = ""
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        self.currentElement.addChild(self.data)
        if self.style.name.startswith("h-meta"):
            metaName = self.style.name[len("h-meta-"):]
            if metaName == "":
                metaName = "meta-heading"
            value = self.currentElement.value
            self.o.addMeta(metaName, value)

    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if newState is not None:
            self.currentElement.addChild(self.data)
            self.data = ""
        return newState
    

class testGetHeadingNumberMode(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        e = element("get-heading-number-mode")
        self.stateElement = e
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if isinstance(newState, headingState):
            self.stateElement.addChild(newState.level-1)
        newState = None
        return newState
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        pass



class linkState(stateObject):
    def __init__(self, parentState, name, atts, style):
        self.__href = ""
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
        
    def __getHref(self):
        return self.__href
    def __setHref(self, value):
        self.__href = value.replace("%0B", "")
    href = property(__getHref, __setHref)
        
    def processElement(self, name, attrs):
        a = element("a")
        type = attrs.get("xlink:type", "")
        self.href = attrs.get("xlink:href", "")
        a.setAttribute("href", self.href)

        target = attrs.get("office:target-frame-name", "")
        if target!="":
            #a.setAttribute("target", target)
            if target=="_blank":    # open in a new window
                a.setAttribute("onclick", "javascript:window.open(\"%s\");return false;" % (self.href))
            elif target=="_self":   # normal behaviour
                pass
            elif target=="_parent":
                a.setAttribute("onclick", "javascript:window.parent.open(\"%s\");return false;" % (self.href))
            elif target=="_top":
                a.setAttribute("onclick", "javascript:window.top.open(\"%s\");return false;" % (self.href))
            else:
                a.setAttribute("onclick", "javascript:window.open(\"%s\", \"%s\");return false;" % (self.href, target))
        self.stateElement = a
        
    def createNewState(self, klass, name, attrs, style=None):
        if name=="text:note":
            self.parentState.depthCount += 1    # so that the end text:a element will not cause the parentElement to close
            self.endState()
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if isinstance(newState, linkState):
            if newState.href.startswith(self.href):
                #self.stateElement = newState.stateElement
                self.href = newState.href
                self.stateElement.setAttribute("href", self.href)
                self.data = ""
                self.depthCount += 1
                newState = self        # keep us as the new state
            else:
                newState = None
        elif newState is not None:
            #print self.depthCount, isinstance(newState, lineBreakState), name
            #if isinstance(newState, lineBreakState):
            if self.depthCount>0 or isinstance(newState, lineBreakState) or \
                isinstance(newState, endnoteState):
                #isinstance(newState, footnoteState) or \  now this one can't be supported anymore
                # OK
                #print "Add child"
                self.currentElement.addChild(self.data)
                pass
            else:
                # no children
                #print " not a child but a sibling"
                newState = None
                self.parentState.data += self.data
            self.data = ""
        return newState
    
    def endElement(self, name):
        self.currentElement.addChild(self.data)
        self.data = ""
        
    def closingState(self):
        self.parentState.data += self.data


class blockquoteState(stateObject):
    def __init__(self, parentState, name, atts, style):        
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
        self.attrs = atts.copy()

    def processElement(self, name, attrs):
        #print "---- blockquoteState.processElement() ----"
        bq = element("blockquote")
        styleName = attrs.get("text:style-name", "")
        cssClass = "%s.%s" % (self.style.name, styleName)
        cssStyle = self.o.styles.getCssStyle(cssClass)
        
        if self.style is not None:
            bq.setAttribute("class", self.style.family + self.style.type[:1])
            
        self.stateElement = bq    # Note: also set self.currentElement
        p = element("p")
        
        isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
        if isItalic:
            i = element("i")
            if isBold:
                b = element("b")
                i.addChild(b)
                b.addChild(p)
            else:
                i.addChild(p)
            bq.addChild(i)        
        elif isBold:
            b = element("b")
            if isItalic:
                i = element("i")
                b.addChild(i)
                i.addChild(p)
            else:
                b.addChild(p)
            bq.addChild(b)
        else:
            bq.addChild(p)

        if otherStyle.strip() != "":
            p.setAttribute("style", otherStyle)
    
        self.stateElement = bq
        self.currentElement = p
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        #print "\n newState is a %s" % newState.__class__.__name__
        # Now if newState
        if newState.style.family==self.style.family and  \
            newState.level==self.level and newState.style.type==self.style.type:
            # is the same as me
            #print "same as me ***"
            styleName = attrs.get("text:style-name", "")
            cssClass = "%s.%s" % (self.style.name, styleName)
            cssStyle = self.o.styles.getCssStyle(cssClass)
            p = element("p")
            
            isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
            if isItalic:
                i = element("i")
                if isBold:
                    b = element("b")
                    i.addChild(b)
                    b.addChild(p)
                else:
                    i.addChild(p)
                self.stateElement.addChild(i)        
            elif isBold:
                b = element("b")
                if isItalic:
                    i = element("i")
                    b.addChild(i)
                    i.addChild(p)
                else:
                    b.addChild(p)
                self.stateElement.addChild(b)
            else:
                self.stateElement.addChild(p)
    
            if otherStyle.strip() != "":
                p.setAttribute("style", otherStyle)

            self.data = ""
            self.currentElement = p
            self.depthCount += 1
            newState = self        # keep us as the new state
        elif (newState.level > self.level) and not(isinstance(newState, headingState)):
            # OK is a child of me
            #print "is a child of me"
            if isinstance(newState, blockquoteState):
                self.currentElement = self.stateElement
            if self.data!="":
                self.currentElement.addChild(self.data)
                self.data = ""
        elif isinstance(newState, spanState) or \
                isinstance(newState, linkState) or \
                isinstance(newState, imageState) or \
                isinstance(newState, footnoteState) or \
                isinstance(newState, lineBreakState) or \
                isinstance(newState, endnoteState) or \
                isinstance(newState, linkImageState) or \
                isinstance(newState, bookmarkState) or \
                isinstance(newState, frameState):
            # OK is a child of me
            #print "OK is a child of me!"
            if self.data!="":
                self.currentElement.addChild(self.data)
                self.data = ""
        else:
            # else must be our sibling
            #print "is a sibling"
            newState.rollback()
            newState = None
        return newState
    
    def endElement(self, name):
        #print "\n endElement() name='%s'" % name
        if name=="text:p":
            self.currentElement.addChild(self.data)
            self.data = ""
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        #print "  closeState()"
        pass    

       
class listState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__li = None
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
        self.attrs = atts.copy()
    
    def processElement(self, name, attrs):
        style = self.style
#        print "listState name='%s', style.family='%s', .type='%s' .level='%s'" % (name, style.family, style.type, style.level)          

        cls = style.family + style.type[:1]        
        if style.type=="number":
            e = element("ol")
            e.setAttribute("class", cls)
            e.setAttribute("style", "list-style: decimal;")
        elif style.type=="i":
            e = element("ol")
            e.setAttribute("class", "li-lower-roman")
            e.setAttribute("style", "list-style: lower-roman;")
        elif style.type=="I":
            e = element("ol")
            e.setAttribute("class", "li-upper-roman")
            e.setAttribute("style", "list-style: upper-roman;")
        elif style.type=="a":
            e = element("ol")
            e.setAttribute("class", "li-lower-alpha")
            e.setAttribute("style", "list-style: lower-alpha;")
        elif style.type=="A":
            e = element("ol")
            e.setAttribute("class", "li-upper-alpha")
            e.setAttribute("style", "list-style: upper-alpha;")
        elif style.type=="bullet":
            e = element("ul")
            e.setAttribute("class", cls)
        elif style.type=="p":
            e = element("ul")
            prePreElement = self.o.previousOooElements[-3]
            if prePreElement!="text:list":
                e.setAttribute("style", "list-style-type: None")
            e.setAttribute("class", cls)
        else:
            raise Exception("Unkown style.type=='%s'" % style.type)
        
        #print "startValue: ", startValue
        if hasattr(self.parentState, "startValue"):
            startValue = self.parentState.startValue
            print "hasattr: ", startValue
            if startValue != "1":
                print "has attribute startValue=", startValue
                e.setAttribute("start", startValue)
            #pass

        self.stateElement = e        # Note: also sets self.currentState
        li = element("li")
        self.__li = li
        e.addChild(li)
        
        styleName = attrs.get("text:style-name", "")
        if style.family!="p":
            cssClass = "%s.%s" % (style.name, styleName)
        else:
            cssClass = "%s%s%s.%s" % (style.name, style.level, style.family, styleName)
        cssStyle = self.o.styles.getCssStyle(cssClass)
        
        p = element("p")
        
        isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
        if isItalic:
            i = element("i")
            if isBold:
                b = element("b")
                i.addChild(b)
                b.addChild(p)
            else:
                i.addChild(p)
            li.addChild(i)        
        elif isBold:
            b = element("b")
            if isItalic:
                i = element("i")
                b.addChild(i)
                i.addChild(p)
            else:
                b.addChild(p)
            li.addChild(b)
        else:
            li.addChild(p)

        if otherStyle.strip() != "":
            p.setAttribute("style", otherStyle)
        
        
        #li.addChild(p)
        self.currentElement = p       
        
#        print "li: ", li
        #print "list State currentElement: ", self.currentElement, "stateElement: ", self.stateElement
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)   
        # if is the same as me then it is just another listitem for me
        if  newState.style.family==self.style.family and  \
            newState.level==self.level and newState.style.type==self.style.type:
            #print "(Sameasme) newState.style.family:", newState.style.family, " newState.style.type", newState.style.type
            # is the same as me
            #print "same", newState.__class__.__name__
            li = element("li")
            self.__li = li
            self.data = ""
            self.stateElement.addChild(li)
            
            styleName = attrs.get("text:style-name", "")
            cssClass = "%s.%s" % (self.style.name, styleName)
            cssStyle = self.o.styles.getCssStyle(cssClass)
            p = element("p")
            
            isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)   
            if isItalic:
                i = element("i")
                if isBold:
                    b = element("b")
                    i.addChild(b)
                    b.addChild(p)
                else:
                    i.addChild(p)
                li.addChild(i)        
            elif isBold:
                b = element("b")
                if isItalic:
                    i = element("i")
                    b.addChild(i)
                    i.addChild(p)
                else:
                    b.addChild(p)
                li.addChild(b)
            else:
                li.addChild(p)
    
            if otherStyle.strip() != "":
                p.setAttribute("style", otherStyle)
            
#            if cssStyle:
#                cssClass = "%s_%s" % (self.style.name, styleName)
#                p.setAttribute("style", cssStyle)
#            li.addChild(p)
            self.currentElement = p
            self.depthCount += 1
            newState.rollback()
            newState = self        # keep us as the new state
        elif newState.style.family==self.style.family and newState.style.type=="p" and \
                newState.level>=self.level:
            #print "(Partofme) newState.style.family:", newState.style.family, " newState.style.type", newState.style.type
            # same (part of me)
            
            styleName = attrs.get("text:style-name", "")
            cssClass = "%s.%s" % (newState.style.parentStyleName, styleName)
            cssStyle = self.o.styles.getCssStyle(cssClass)
            
            self.data = ""
            p = element("p")
            
            isItalic, isBold, otherStyle = self.o.styles.getBlockStyle(cssStyle)
            if isItalic:
                i = element("i")
                if isBold:
                    b = element("b")
                    i.addChild(b)
                    b.addChild(p)
                else:
                    i.addChild(p)
                self.__li.addChild(i)        
            elif isBold:
                b = element("b")
                if isItalic:
                    i = element("i")
                    b.addChild(i)
                    i.addChild(p)
                else:
                    b.addChild(p)
                self.__li.addChild(b)
            else:
                self.__li.addChild(p)
    
            if otherStyle.strip() != "":
                p.setAttribute("style", otherStyle)
            
#            if cssStyle:
#                cssClass = "%s_%s" % (newState.style.parentStyleName, styleName)
#                p.setAttribute("style", cssStyle)
#            self.__li.addChild(p)
            self.currentElement = p
            self.depthCount += 1
            newState.rollback()
            newState = self        # keep us as the new state
        #elif (newState.level==0) or (newState.level > self.level):
        elif (((newState.level > self.level) or isinstance(newState, spanState) or \
                    isinstance(newState, frameState) or \
                    isinstance(newState, footnoteState) or \
                    isinstance(newState, endnoteState) or \
                    isinstance(newState, lineBreakState) or \
                    isinstance(newState, bookmarkState) or \
                    isinstance(newState, linkState)) and \
                    newState.style.family!="h") or \
                    (newState.__class__.__name__=="tableState"):
            #print "(childofme) newState.style.family:", newState.style.family, " newState.style.type", newState.style.type
            # OK is a child of me
            #print "is a child of me"
            self.currentElement.addChild(self.data)
            self.data = ""
        else:
            # else must be our sibling (or our parent's item)
            # let our parent create this state then
            #print "is our sibling (or our parent's item)"
            #print "level=%s, family='%s'" % (newState.level, newState.style.family)
            #print "(parentorsiblingitem) newState.style.family:", newState.style.family, " newState.style.type", newState.style.type
            newState.rollback()
            newState = None
        return newState
    
    
    def endElement(self, name):
        if name=="text:p" or name=="text:h":
            self.currentElement.addChild(self.data)
            self.data = ""
            self.currentElement = self.__li


class definitionListState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
        self.test = True
    
    
    def processElement(self, name, attrs):
        style = self.style
        dl = element("dl")
        self.stateElement = dl        # Note: also sets self.currentState
        e = element(style.family)
        dl.addChild(e)
        self.currentElement = e
    
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)        
        #print "createNewState", newState.style, self.style
        # Now if newState
        if (newState.style.family=="dd" or newState.style.family=="dt") and \
            newState.level==self.level and newState.style.type==self.style.type:
            # is the same as me
            #print "same"
            e = element(style.family)
            self.stateElement.addChild(e)
            self.currentElement = e
            self.data = ""
            self.depthCount += 1
            newState = self        # keep us as the new state
        #elif (newState.level==0) or (newState.level > self.level):
        elif ((newState.level > self.level) and not(isinstance(newState, headingState))) or \
                isinstance(newState, spanState) or isinstance(newState, linkState) or \
                isinstance(newState,lineBreakState) or\
                isinstance(newState, footnoteState) or isinstance(newState, endnoteState) or \
                isinstance(newState, bookmarkState) or isinstance(newState, frameState):
            # NOTE: If is a HeadingState then do not count the level (is a different type of level in this case)
            #print "child", newState.__class__.__name__, self.depthCount
            if self.depthCount:
                self.currentElement.addChild(self.data)
            self.data = ""
            if self.currentElement.name=="dt" and self.depthCount==0:
                # if self.depthCount==0 then we have finished with 'dt'
                e = element("dd")
                self.stateElement.addChild(e)
                self.currentElement = e
            # OK is a child of me
            if isinstance(newState, definitionListState):
                #self.currentElement = self.stateElement   ## orginal
                ##  new
                dd = element("dd")
                self.stateElement.addChild(dd)
                
                self.currentElement = dd
                ##
                
#                (((newState.level > self.level) or isinstance(newState, spanState) or \
#                    isinstance(newState, frameState) or \
#                    isinstance(newState, footnoteState) or \
#                    isinstance(newState, endnoteState) or \
#                    isinstance(newState, lineBreakState) or \
#                    isinstance(newState, bookmarkState) or \
#                    isinstance(newState, linkState)) and \
#                    newState.style.family!="h") or \
#                    (newState.__class__.__name__=="tableState"):
        else:
            #print "sibling or parent item (parent(same))"
            # else must be our sibling
            #newState.parentState = self.parentState
            newState.rollback()
            newState = None
        return newState
    
    
    def endElement(self, name):
        if name=="text:p":
            self.currentElement.addChild(self.data)
            self.data = ""



class linkImageState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        self.href = attrs.get("xlink:href", "")
        self.target = attrs.get("office:target-frame-name", "")

class imageAlternateState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def closingState(self):
        a = self.parentState.a
        img = a.getFirstChild()
        if img.type!="element":
            try:
                img = a.getNextElementNode()
            except:
                img = None
        if img is not None:
            img.setAttribute("longdesc", self.data)


class imageAltTitleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def closingState(self):
        a = self.parentState.a
        # get first img child
        img = None
        for child in a.getChildren():
            if child.name=="img":
                img = child
                break
        if img is None:
            span = self.currentElement.getLastChild()
            img = span.getLastChild()
        if img is not None:
            img.setAttribute ("title", self.data)


class frameState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.attrs = None
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        ##if not isinstance(self.parentState.parentState, frameState):
        ##    print "\n"
        self.attrs = attrs.copy()
        #print "=== frameState() -"
        a = element("a")
        if isinstance(self.parentState, linkImageState):
            href = self.parentState.href
            a.setAttribute("href", href)
            target = self.parentState.target
            if target!="":
                #a.setAttribute("target", target)
                if target=="_blank":    # open in a new window
                    a.setAttribute("onclick", "javascript:window.open(\"%s\");return false;" % (href))
                elif target=="_self":   # normal behaviour
                    pass
                elif target=="_parent":
                    a.setAttribute("onclick", "javascript:window.parent.open(\"%s\");return false;" % (href))
                elif target=="_top":
                    a.setAttribute("onclick", "javascript:window.top.open(\"%s\");return false;" % (href))
                else:
                    a.setAttribute("onclick", "javascript:window.open(\"%s\", \"%s\");return false;" % (href, target))
        self.a = a

    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        ##print " === newState is a %s" % newState.__class__.__name__
        return newState
    
    def endElement(self, name):
        ##print "=== endElement (frameState)"
        ##print self.currentElement
        pass
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        ##print "=== closingState() (frameState)"
        pass
        

class pluginState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        name = self.parentState.attrs.get("draw:name", "")
        nameNoSpace = name.replace(" ", "_")
        height = self.convertUnits(self.parentState.attrs.get("svg:height", ""))
        width = self.convertUnits(self.parentState.attrs.get("svg:width", ""))
        href = attrs.get("xlink:href", "")
        mtype = attrs.get("draw:mime-type", "")
        a = element("a")
        a.setAttribute("name", nameNoSpace)
        self.currentElement.addChild(a)
        e = element("embed")
        e.setAttribute("alt", name)
        e.setAttribute("name", nameNoSpace)
        e.setAttribute("title", name)
        e.setAttribute("src", href)
        e.setAttribute("type", mtype)
        e.setAttribute("height", height)
        e.setAttribute("width", width)
        self.currentElement.addChild(e)


        
class imageState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        
    
    def processElement(self, name, attrs):
        if hasattr(self.parentState, "attrs")==False:
            #print "*** Warning: ERROR in imageState expected parentState to have 'attrs' property"
            if self.parentState.__class__.__name__!="frameState" :
                pass
                #print " also excpected parentState to be a frameState!"
            self.parentState.attrs = {}
        
        drawStyleName = self.parentState.attrs.get("draw:style-name")
        name = self.parentState.attrs.get("draw:name", "")
        cls = self.parentState.attrs.get("draw:style-name", "")
        height = self.convertUnits(self.parentState.attrs.get("svg:height", ""))
        width = self.convertUnits(self.parentState.attrs.get("svg:width", ""))
        svgy = self.convertUnits(self.parentState.attrs.get("svg:y", "")) 
        if svgy != "":
            try:
                ratio = (float(height)/float(svgy))
                first = (float(height)*ratio)
                second = int(first/float(svgy))
                third = first/second
                if third > first:
                    #for those images height more than text but not more than 3.13pi or 50px
                    #if images more than 3.13pi or 50px, wrap the image to text
                    svgy = (float(svgy)/second)
                else:
                    #For those images smaller or equal size with the text
                    svgy = (float(svgy))/(second*4)
            except:
                svgy=""
        href = attrs.get("xlink:href", "")
        
        img = element("img")
        img.setAttribute("alt", name)
        img.setAttribute("class", cls)
        if svgy != "":
            img.setAttribute("style", "border:0px; vertical-align: baseline; margin-bottom: %spx;" % str(svgy))
        else:
            frameStyle = self.o.styles.getOooStyle(drawStyleName)
            verticalAlign = ""
            if frameStyle.verticalAlign:
                verticalAlign = "vertical-align: %s" % frameStyle.verticalAlign
            img.setAttribute("style", "border:0px; %s" % verticalAlign)
        img.setAttribute("src", href)
        img.setAttribute("height", height)
        img.setAttribute("width", width)
        #margin = self.convertUnits(attrs.get("svg:height", ""))
        a = None
        if isinstance(self.parentState, frameState):
            a = self.parentState.a
            nameNoSpace = name
            if (nameNoSpace.find("localhost")>-1 or nameNoSpace.find("LOCALHOST")>-1):
                nameNoSpace = splitPathFileExt(nameNoSpace)[1] + splitPathFileExt(nameNoSpace)[2]
            nameNoSpace = nameNoSpace.replace(" ", "_");
            nameNoSpace = nameNoSpace.replace("/", ":");
            #a.setAttribute("name", nameNoSpace)
            a.addChild(comment(" "))
            #try to add a new line after each image in case image and text are in same paragraph.
            #lineBR = element("br")
            
            if self.parentState.attrs.get("text:anchor-type", "") == "paragraph":
                #since div element can not existed inside p tag, use span with style to control the image padding
                span = element ("span")
                span.setAttribute("style", "display: block")
                span.addChild(a)
            
                #div = element("div")
                #div.addChild(a)
                # Have the image inside of the a element
                #a.addChild(img)
                #self.stateElement = div     # also sets the currentElement
                # or have the a element as a sibling
                if a.getAttribute("href") is None:
                    span.addChild(img)
                    #span.addChild(lineBR)
                else:
                    a.addChild(img)
                   # a.addChild(lineBR)
                self.currentElement.addChild(span)
            else:
                # Have the image inside of the a element
                #a.addChild(img)
                #self.stateElement = a     # also sets the currentElement
                # or have the a element as a sibling
                self.currentElement.addChild(a)
                if a.getAttribute("href") is None:
                    self.currentElement.addChild(img)
                    #self.currentElement.addChild(lineBR)
                else:
                    a.addChild(img)
                    #a.addChild(lineBR)
        else:
            pass
            #print "Warning: imageState expects a parentState of frameState. Not '%s'" % self.parentState.__class__.__name__


class slideState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        #print "*** Slide State ***"
        #print "parentState='%s'" % self.parentState.__class__.__name__
        h = element("h1")
        self.stateElement = h
        
        # Get parent table state object
        p = self.parentState
        while True:
            if p==None:
                return
            if p.__class__.__name__=="tableState":
                #print "Found parent table state"
                break
            p = p.parentState
        self.__parentTableState = p
        self.__old = self.__parentTableState.closingState
        self.__parentTableState.closingState = self.__parentTableStateClosingState
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if newState is not None:
            self.currentElement.addChild(self.data)
            self.data = ""
        return newState
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        self.currentElement.addChild(self.data)

    def __parentTableStateClosingState(self):
        #print "Closing parent table State"0
        table = self.__parentTableState
        table.stateElement = None
        self.__old()
        div = element("div")
        div.setAttribute("class", "slide")
        self.o.state.currentElement.addChild(div)
        for row in table.rows:
            for cell in row.cells:
                for e in list(cell.cellElement.items):
                    #print "what is e: ", e
                    div.addChild(e)


class bookmarkState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        name = ""
        if attrs.has_key("text:name"):
            name = attrs["text:name"]
            a = element("a")
            self.stateElement = a
            #a.setAttribute("name", name)
	    a.setAttribute("id", name)
            a.addChild(comment(name))

    def closingState(self):
        """ do any state finalization/cleanup here """
        pass


""" xrefState handling cross referencing
    e.g. Cross ref to list, heading, table, picture """
class xrefState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.endOnClosingOooElement = False
        
    def processElement(self, name, attrs):
        style = self.style
        styleName = attrs.get("text:style-name", "")
        
        if styleName == "xRef-ChapterText" or styleName =="xRef-RefText":
            e = element ("a")
            self.stateElement = e
            self.currentElement = e
        
        
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        
        if name=="text:bookmark-ref":
            if attrs.has_key("text:ref-name"):
                value = "#" + attrs["text:ref-name"]
                if self.currentElement.name == "a":
                    self.currentElement.setAttribute("href", value)
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""
        return newState
    
    def endElement(self, name):
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""
        pass
    
    def closingState(self):
        pass


class ignoreAllState(stateObject):
    # ignore all this element and all child elements
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def processElement(self, name, attrs):
        pass

    def createNewState(self, klass, name, attrs, style=None):
        #newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        newState = None
        return newState



class tableOfContentState(ignoreAllState):
    pass


class illustrationIndexState(ignoreAllState):
    pass









