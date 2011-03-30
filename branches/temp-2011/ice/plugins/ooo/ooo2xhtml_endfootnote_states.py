
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

import copy


# ===   footnotes / endnotes states   ===
class footnoteState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.__citation = None
        self.__body = None
    
    def processElement(self, name, attrs):
        id = attrs.get("text:id", "")
        
        a = element("a")
        a.setAttribute("name", id)
        a.setAttribute("href", "#%s-text" % id)
        self.__a = a
        
        span = element("span")
        span.setAttribute("class", "footnote")
        
        e = element("a")
        e.setAttribute("name", "%s-text" % id)
        e.setAttribute("href", "#%s" % id)
        e.setAttribute("class", "footnote")
        span.addChild(e)
        
        self.stateElement = span
        self.currentElement = e
        
        s2 = element("span")
        s2.setAttribute("class", "footnote-text")
        span.addChild(s2)
        self.footnoteTextElement = s2
        
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if isinstance(newState, noteCitationState):
            self.__citation = newState
        elif isinstance(newState, noteBodyState):
            self.__body = newState
        return newState
    
    def endElement(self, name):
        self.currentElement.addChild(self.data)
        self.data = ""
        
    def startElement(self, name, attrs):
        pass
        
    def endElement(self, name):
        #self.currentElement.addChild(self.data)
        self.data = ""
        
    def closingState(self):
        """ do any state finalization/cleanup here """
        if self.__citation is not None:
            self.currentElement.addChild(self.__citation.data)
            self.__a.addChild(self.__citation.data)
        span = element("span")
        span.setAttribute("class", "footnote-defined")
        #div.addChild(self.__a)
        if self.__body is not None:
            #print "has body", len(self.__body.currentElement.items)
            if len(self.__body.currentElement.items)>0 and self.__body.currentElement.items[0].name=="p":
                self.__body.currentElement.items[0].prepend(" ")
                self.__body.currentElement.items[0].prepend(self.__a)
            else:
                self.__body.currentElement.prepend(self.__a)
            
            skip = False
            ########################
            # skip = True
            # this is the original content. but because footnote does not go to the hover.
            # I have set it as false. Cynthia(17/6/2009)
            #######################
            for item in list(self.__body.currentElement.items):
                span.addChild(item)
                if skip:
                    skip = False
                else:
                    item2 = copy.deepcopy(item)
                    self.footnoteTextElement.addChild(item2)
        else:
            span.addChild(self.__a)
            
        #print "-----"
        #div.addChild(element("br"))
        self.o.addHtmlFooter(span)


class endnoteState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.__citation = None
        self.__body = None
    
    def processElement(self, name, attrs):
        a = element("a")
        a.setAttribute("name", "%s" % attrs.get("text:id", ""))
        a.setAttribute("href", "#%s-text" % attrs.get("text:id", ""))
        self.__a = a

        e = element("a")
        e.setAttribute("href", "#%s" % attrs.get("text:id", ""))
        e.setAttribute("name", "%s-text" % attrs.get("text:id", ""))
        self.stateElement = e        # Note: also sets self.currentState
        s1 = element("span")
        s1.setAttribute("style", "vertical-align: super;")
        e.addChild(s1)
        s2 = element("span")
        s2.setAttribute("class", "endnote")
        s1.addChild(s2)
        self.currentElement = s2
        
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if isinstance(newState, noteCitationState):
            #print "# has citation"
            self.__citation = newState
        elif isinstance(newState, noteBodyState):
            #print "# has note body"
            self.__body = newState
        return newState
    
    def endElement(self, name):
        self.currentElement.addChild(self.data)
        self.data = ""

    def closingState(self):
        """ do any state finalization/cleanup here """
        if self.__citation is not None:
            self.currentElement.addChild(self.__citation.data)
            self.__a.addChild(self.__citation.data)
        span = element("span")
        span.setAttribute("class", "endnote")
        #div.addChild(self.__a)
        if self.__body is not None:
            #print "has body", len(self.__body.currentElement.items)
            if len(self.__body.currentElement.items)>0 and self.__body.currentElement.items[0].name=="p":
                self.__body.currentElement.items[0].prepend(" ")
                self.__body.currentElement.items[0].prepend(self.__a)
            else:
                self.__body.currentElement.prepend(self.__a)
            for item in list(self.__body.currentElement.items):
                span.addChild(item)
        else:
            span.addChild(self.__a)
        #div.addChild(element("br"))
        self.o.addHtmlFooter(span)


class noteCitationState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)

    def closingState(self):
        """ do any state finalization/cleanup here """
        pass    


class noteBodyState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts, style=style)
        self.currentElement = element("noteBody")

    def createNewState(self, klass, name, attrs, style=None):
        if name=="text:p":
            # do not create a child paragraphState here if we are already the child
            #   of a paragraphState.
            p = self.parentState
            count = 0
            while p is not None:
                if p.__class__==klass:
                    self.depthCount += 1
                    return self
                p = p.parentState
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""
        return newState

    def endElement(self, name):
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""

    def closingState(self):
        """ do any state finalization/cleanup here """
        if self.data!="":
            self.currentElement.addChild(self.data)
            self.data = ""



#This style is created so there are no paragraph being created
#at the footnote and endnote (number and text are aligned in one line)
#Note: if the footnote or endnote uses style other than para,
#number and body of footnote/endnote will not in one line
#Need to be done: put the <a href> numbering tag into <p> tag of the body of
#footnote and endnote
class noStyleState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        #print "paragraphState name='%s', style=%s" % (name, style)
        stateObject.__init__(self, parentState, name, atts, style=style)
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        if self.data!="":
            self.data = " " + self.data
            self.currentElement.addChild(self.data)
            self.data = ""
        return newState

    def endElement(self, name):
        if self.data!="":
            self.data = " " + self.data
            self.currentElement.addChild(self.data)
            self.data = ""

    def closingState(self):
        """ do any state finalization/cleanup here """
        if self.data!="":
            self.data = " " + self.data
            self.currentElement.addChild(self.data)
            self.data = ""
