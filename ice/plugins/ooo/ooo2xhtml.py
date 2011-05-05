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
import sys
import os
import xml.sax
import re
import types

from ooo2xhtml_utils import *
from ooo2xhtml_style import *
from ooo2xhtml_basic_states import *
from ooo2xhtml_states import *
from ooo2xhtml_table_states import *
from ooo2xhtml_endfootnote_states import *


import ooo2xhtml_states     # for ooo2xhtml_states.splitPathFileExt = context.fs.splitPathFileExt
import ooo2xhtml_utils      # for ooo2xhtml_utils.errOutput = sys.stderr




# States

def standardStates(currentState, name, attrs, etest):
    ##
    #attrsS = " - ".join(attrs.values())
    #print "=== standardStates(name='%s', attrs='%s')" % (name, attrsS)
    ##
    newState = None
    # text:
    if name=="text:a":
        newState = currentState.createNewState(linkState, name, attrs)
    elif name=="text:line-break":
        newState = currentState.createNewState(lineBreakState, name, attrs)
    elif name=="text:p" or name=="text:h":
        #<text:p text:style-name="p">
        #<text:p text:style-name="P1">
        #<text:h text:style-name="h1n">
        styleName = attrs.get("text:style-name", "")
	
        style = currentState.o.styles.getOooStyle(styleName)
        #print "name='%s', style=%s" % (name, style)
        if style.family=="p":
            newState = currentState.createNewState(paragraphState, name, attrs, style=style)
        elif style.isTitle:
            newState = currentState.createNewState(titleState, name, attrs)
        elif style.family=="h":
            #print "Heading"
	    outlineNumbered = attrs.get("text:outline-level", "")
	    if outlineNumbered!="" and style.type=="u":
		style.setNumbered()
            if style.type=="slide":
                newState = currentState.createNewState(slideState, name, attrs, style=style)
		
            else:
                newState = currentState.createNewState(headingState, name, attrs, style=style)
        elif style.family=="pre":
            newState = currentState.createNewState(preState, name, attrs, style=style)
        elif style.family=="bq":
            #print "BQ"
            newState = currentState.createNewState(blockquoteState, name, attrs, style=style)
        elif style.family=="li":
            newState = currentState.createNewState(listState, name, attrs, style=style)
        elif style.family=="dt" or style.family=="dd":
            #print "Definition"
            newState = currentState.createNewState(definitionListState, name, attrs, style=style)
        else:
            #style.type = ""
            state = paragraphState
            if styleName == "Footnote_20_Text":
                styleName = "Footnote"
            if styleName.lower() == "footnote" or styleName.lower() == "endnote":
                state = noStyleState 
            if style.type!="Heading":
                #style.type = ""
                style.resetType()   # sets style.type=""
            newState = currentState.createNewState(state, name, attrs, style=style)
    elif name=="text:span":
        styleName = attrs.get("text:style-name", "")
        style = currentState.o.styles.getOooStyle(styleName)
        if style.family != "xRef":
            newState = currentState.createNewState(spanState, name, attrs, style=style)
        else:
            newState = currentState.createNewState(xrefState, name, attrs, style=style)
    elif name=="text:bookmark-ref":
        newState = currentState.createNewState(xrefState, name, attrs)
    elif name=="text:s":
        newState = currentState.createNewState(spanState, name, attrs)
    elif name=="text:tab":
        newState = currentState.createNewState(tabState, name, attrs)
    elif name=="text:deletion":
        newState = currentState.createNewState(deletionState, name, attrs)
    elif name=="text:note":
        noteClass = attrs.get("text:note-class", "")
        if noteClass=="footnote":
            newState = currentState.createNewState(footnoteState, name, attrs)
        elif noteClass=="endnote":
            newState = currentState.createNewState(endnoteState, name, attrs)
    elif name=="text:note-citation":
        newState = currentState.createNewState(noteCitationState, name, attrs)
    elif name=="text:note-body":
        newState = currentState.createNewState(noteBodyState, name, attrs)
    elif name=="text:bookmark" or name=="text:bookmark-start":
        #print "Bookmark found..."
        newState = currentState.createNewState(bookmarkState, name, attrs)
    elif name=="text:table-of-content":
        newState = currentState.createNewState(tableOfContentState, name, attrs)
    elif name=="text:illustration-index":
        newState = currentState.createNewState(illustrationIndexState, name, attrs)
    # office:
    elif name=="office:annotation":
        newState = currentState.createNewState(annotationState, name, attrs)
    # draw:
    elif name=="draw:frame":
        newState = currentState.createNewState(frameState, name, attrs)
    elif name=="draw:image":
        newState = currentState.createNewState(imageState, name, attrs)
    elif name=="draw:plugin":
        newState = currentState.createNewState(pluginState, name, attrs)
    elif name=="draw:a":
        newState = currentState.createNewState(linkImageState, name, attrs)
##    elif name=="draw:rect":
##        newState = currentState.createNewState(ignoreState, name, attrs)
    elif name=="svg:desc":
        newState = currentState.createNewState(imageAlternateState, name, attrs)
    elif name=="svg:title":
        newState = currentState.createNewState(imageAltTitleState, name, attrs)
    # table:
    elif name=="table:table":
        if attrs.get("table:is-sub-table", "")=="true":
            newState = currentState.createNewState(subTableState, name, attrs)
        else:
            newState = currentState.createNewState(tableState, name, attrs)
    elif name=="table:table-header-rows":
        newState = currentState.createNewState(tableHeaderRowsState, name, attrs)
    elif name=="table:table-row":
        newState = currentState.createNewState(tableRowState, name, attrs)
    elif name=="table:table-cell":
        newState = currentState.createNewState(tableCellState, name, attrs)
    elif name=="table:table-column":
        newState = currentState.createNewState(tableColumnState, name, attrs)
    ## for testing only
    #elif name=="get-family":
    #    newState = currentState.createNewState(getFamilyState, name, attrs)
    #elif name=="get-level":
    #    newState = currentState.createNewState(getLevelState, name, attrs)
    #elif name=="get-heading-level":
    #    newState = currentState.createNewState(getHeadingLevelState, name, attrs)
    #elif name=="get-type":
    #    newState = currentState.createNewState(getTypeState, name, attrs)
    elif name=="test-get-heading-number-mode":
        newState = currentState.createNewState(testGetHeadingNumberMode, name, attrs)
    return newState


def titleStates(currentState, name, attrs, etest):
    newState = None
    if name=="text:span":
        newState = standardStates(currentState, name, attrs, etest)
    else:
        newState = currentState.createNewState(ignoreState, name, attrs)
    return newState

    
def ignoreAllStates(currentState, name, attrs, etest):
    newState = None
    return newState


commonStates = [ paragraphState, blockquoteState, spanState, preState, lineBreakState,\
                headingState, listState, noStyleState, definitionListState, linkState, tabState,\
                deletionState, annotationState, frameState, imageState, linkImageState, \
                imageAlternateState, tableOfContentState, \
                tableState, tableHeaderRowsState, tableRowState, tableCellState, \
                subTableState, tableColumnState, slideState, bookmarkState, \
                footnoteState, noteCitationState, noteBodyState, endnoteState, \
                testGetHeadingNumberMode, xrefState\
               ]
    
# dictionary of all valid states (keyed by the state classes)
#    value = a list of possible new states that can be entered from this state
#    value = [ (stateObjectClass, newStateString or callable, NotCurrentlyUsed), ]
#        test - new state
states = {
         startState:[
                        (officeDocumentContentState, "office:document-content", None),
                        (officeDocumentStylesState, "office:document-styles", None),
                    ],
         officeDocumentStylesState: [
                                (styleState, "office:automatic-styles", None),
                                (styleState, "office:styles", None),
                            ],
         officeDocumentContentState: [(styleState, "office:automatic-styles", None),
                                      (bodyState, "office:body", None)],
         styleState: [(styleStyleState, "style:style", None),
                      (outlineStyleState, "text:outline-style", None),
                      (listStyleState, "text:list-style", None),
                        ],
         outlineStyleState: [(outlineLevelStyleState, "text:outline-level-style", None)],
         listStyleState: [(listLevelStyleState, "text:list-level-style-number", None)],
         bodyState: [(officeTextState, "office:text", None)],
         officeTextState: [
                           (ignoreState, "office:forms", None),
                           (ignoreState, "text:sequence-decls", None),
                           (None, standardStates, None),
                          ],
         titleState: [  (ignoreState, "draw:rect", None),
                        (None, titleStates, None),
                        (ignoreState, "*", None),
                        ],
         #tableOfContentState: [(None, ignoreAllStates, None),],
#         paragraphState:[
#                           (None, standardStates, None),
#                        ]    
         }
# Plus all common States
for state in commonStates:
    states[state] = [(None, standardStates, None)]
stateObject.states = states
    

#===============================================
#===============================================
class Ooo2xhtml(object, xml.sax.ContentHandler):
    def __init__(self, context):
        self.__context = context
        # Hack
        ooo2xhtml_states.splitPathFileExt = context.fs.splitPathFileExt
        ooo2xhtml_utils.errOutput = context.output
        #
        s = shtml()
        self.__shtml = s
        self.__footer = element("footer")
        s.title = "Untitled"
        self.__styles = styles(self)
        self.__currentOooXPath = ""
        self.__oooDepth = 0
        
        xml.sax.ContentHandler.__init__(self)
        
        self.__setup()
        self.__state = startState(None, "?dummy?", None, o=self)
        self.__idCount = 0
        self.__ignoreFirstTitle = True
        self.__previousOooElements = []
#        self.__metaAuthor = {}
        self.__metaAuthor = []
        self.__currentMetaAuthor = None
#        self.__meta = {"authors":{}}
        self.__meta = {"authors": []}
    
    @property
    def meta(self):
        return self.__meta
    
    def addMeta(self, name, value):
        # title - first only
        # author - list of
        # abstract & keywords - append
        # all others - last only for now
        meta = self.__meta
        #print "Adding MetaName='%s', value='%s'" % (name, value)
#        print "meta: ", meta
        nameParts = name.split("-")
        name = nameParts.pop(0)
        if name=="title":
            if not meta.has_key(name):
                meta[name] = value
        elif name=="affiliation":
            if self.__currentMetaAuthor is not None and self.__metaAuthor!=[]:
                for list in self.__metaAuthor:
                    if list.has_key("name") and list["name"] == self.__currentMetaAuthor:
                        list[name] = value
        elif name=="author" or name=="authors":
            newName = name
            value = value.rstrip(",")
            if len(nameParts)>0:
                while len(nameParts)>0:
                    name = nameParts.pop(0)
                    newname = "%s-%s" % (newName, name)
                    if name== "name":
                        self.__metaAuthor.append({"name":value})
                        self.__currentMetaAuthor = value
                    if name=="affiliation" or name=="email":
                        if self.__currentMetaAuthor is not None and self.__metaAuthor!=[]:
                            for list in self.__metaAuthor:
                                if list.has_key("name") and list["name"] == self.__currentMetaAuthor:
                                    list[name] = value
            else:
                self.__metaAuthor.append({"name":value})
                self.__currentMetaAuthor = value
            
            meta["authors"] = self.__metaAuthor
        elif name=="issued" or name=="date":
	    print "Setting date"
            newName = name
            while len(nameParts)>0:
                name = nameParts.pop(0)
                newName = "%s-%s" % (newName, name)
                print "in loop" + newName
            if not meta.has_key(newName):
                meta[newName] = value
		print "setting now"
        elif name=="abstract" or name=="keywords":
            n = meta.get(name, "")
            if len(n)>0:
                n += " "
            meta[name] = n + value
        else:
            if name!= 'elementname' and name!='elementvalue':
                newName = name
                while len(nameParts)>0:
                    if meta.has_key(name):
                        meta = meta.get(name)
                    name = nameParts.pop(0)
                    newName = "%s-%s" % (newName, name)
                meta[newName] = value
    
    @property
    def previousOooElements(self):
        return self.__previousOooElements
    
    def getIDCount(self):
        self.__idCount += 1
        return self.__idCount
    
    def resetIDCount(self):
        self.__idCount = 0
    

    def process(self, contentXmlStr, stylesXmlStr=None):
        try:
            stylesXmlStr = None
            if stylesXmlStr is None or stylesXmlStr=="":
                stylesXmlStr = "<office:document-styles " + \
                            "xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0' " + \
                            "office:version='1.0'/>"
            try:
                xml.sax.parseString(stylesXmlStr, self)
                xml.sax.parseString(contentXmlStr, self)
            except Exception, e:
                raise         # output the css info
            self.styles.outputCssStyles()
            #only first item add horizontal bar
            count=1
            for item in list(self.__footer.items):
                if count==1:
                    self.__shtml.body.addChild(element("hr"))
                p = element("p")
                #div = element("div")
                #p.addChild(div)
                #div.setAttribute("style", "font-size: .9em;")
                p.addChild(item)
                self.__shtml.body.addChild(p)
                count+=1
            #print "shtml="
            #print self.shtml.formatted()
            #print
        except Exception, e:
            s = "Exception in ooo2xhtml.py - '%s'\n" % str(e)
            s += self.__context.formattedTraceback(5)
            s += "\n----\n"
            sys.stderr.write(s)
            raise e

    
    def __getState(self):
        return self.__state
    def __setState(self, value):
        #print "changing state to ", value
        self.__state = value
    state = property(__getState, __setState)
    
    
    def __getShtml(self):
        return self.__shtml
    shtml = property(__getShtml)
    
    def addHtmlFooter(self, elem):
        self.__footer.addChild(elem)
    
    
    def __getStyles(self):
        return self.__styles
    styles = property(__getStyles)
    
    
    def __getCurrentOooXPath(self):
        return self.__currentOooXPath
    currentOooXPath = property(__getCurrentOooXPath)
    
    
    def oooStepIntoElement(self, elementName):
        self.__currentOooXPath += "/" + elementName
        #print "CurrentOooXPath='%s'" % self.__currentOooXPath
    def oooStepOut(self):
        p = self.__currentOooXPath
        self.__currentOooXPath = p[:p.rfind("/")]
    
    
    def ignoreThisTitle(self, state=None):
        try:
            return self.__ignoreFirstTitle
        finally:
            self.__ignoreFirstTitle = False
    
    #def __getCurrentOutputElement(self):
    #    return self.__currentOutputElement
    #def __setCurrentOutputElement(self, element):
    #    self.__currentOutputElement = element
    #currentOutputElement = property(__getCurrentOutputElement, __setCurrentOutputElement)
    
    
    def startElement(self, name, attrs):
        ## attrs.get(name, default)
        ## attrs.keys()  attrs.has_key(name)
        self.__oooDepth += 1
        #print "\t" * self.__oooDepth + "start ", name
        #print "startElement %s %s  - %s" % (name, self.__oooDepth, attrs.keys())
        
        self.oooStepIntoElement(name)      
         
        self.__previousOooElements.append(name)
        
        if self.__state is not None:
            self.__state.sElement(name, attrs)
    
    
    def endElement(self, name):
        self.__oooDepth -= 1
        self.oooStepOut()
        if self.__state is not None:
            self.__state.eElement(name)
    
    
    def characters(self, data):
        if self.__state is not None:
            self.__state.characters(data)
    
    
    def serialize(self):
        s = str(self.__shtml)
        if type(s) is types.UnicodeType:
            s = s.encode("utf-8")
        return s
    
    def __str__(self):
        s = self.__shtml.formatted()
        if type(s) is types.UnicodeType:
            s = s.encode("utf-8")
        return s
        
    
    def __setup(self):
        self.currentHeadingLevel = 0
        self.currentHeadingNumber = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #self.currentHeadingNumber = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.__headingNumberStartValues = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    
    def getCurrentHeadingLevelStartValue(self):
        sv = self.__headingNumberStartValues[self.currentHeadingLevel]
        self.currentHeadingNumber[self.currentHeadingLevel] = sv
        # Reset headings start value or Not
        #self.__headingNumberStartValues = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        
    def setHeadingLevelStartValue(self, headingLevel, startValue):
        if startValue!=1:
            pass
            #print "# Heading startValue for level %s is %s" % (headingLevel, startValue)
        self.__headingNumberStartValues[headingLevel] = startValue
        self.currentHeadingNumber[headingLevel] = startValue

