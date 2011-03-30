
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


from types import *
import sys
import re
from shtml import *

errOutput = None


oOfficeNSList = [ \
            ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"), \
            ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"), \
            ("xlink", "http://www.w3.org/1999/xlink"), \
            ("dc", "http://purl.org/dc/elements/1.1/"), \
            ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"), \
            ("ooo", "http://openoffice.org/2004/office"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"), \
            ("fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"), \
            ("number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"), \
            ("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"), \
            ("chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"), \
            ("dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"), \
            ("math", "http://www.w3.org/1998/Math/MathML"), \
            ("form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0"), \
            ("script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0"), \
            ("ooow", "http://openoffice.org/2004/writer"), \
            ("oooc", "http://openoffice.org/2004/calc"), \
            ("dom", "http://www.w3.org/2001/xml-events"), \
            ("xforms", "http://www.w3.org/2002/xforms"), \
            ("xsd", "http://www.w3.org/2001/XMLSchema"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
            # xmlns="http://www.w3.org/1999/xhtml"
         ]


class stateObject(object):
    states = {}    # dictionary list of all states and when/what states it can go to next.
    idCount = 0
    
    
    # Called to create new states
    #  can be overriden to prevent the creation of a new state
    def createNewState(self, klass, name, attrs, style=None):
        if name=="text:p" and False:
            print "create para '%s'" % klass
            p = self.parentState
            count = 0
            while p is not None:
                if p.__class__==klass:
                    print " has para parent"
                    self.depthCount += 1
                    return self
                p = p.parentState
        newState = klass(self, name, attrs, style=style)
        return newState
    
    # called to check if a new state should be created or not
    def newState(self, name, attrs):
        s = None
        tests = self.states.get(self.__class__, None)
        if tests is not None:
            for state, stest, etest in tests:
                if type(stest) is StringType:
                    if name==stest or stest=="*":
                        s = self.createNewState(state, name, attrs)
                        break
                elif callable(stest):
                    s = stest(self, name, attrs, etest)
                    break
        if s is not None:
            self.o.state = s
        return s is not None
    
    
    def __init__(self, parentState, name=None, attrs=None, style=None):
        self.__o = parentState.o
        self.__parentState = parentState
        self.__currentElement = None
        self.__stateElement = None
        self.__data = ""
        self.__level = 0
        self.style = style
        if style is None:
            if attrs is not None:
                styleName = attrs.get("text:style-name", "")
                self.style = self.__o.styles.getOooStyle(styleName)
        self.__depthCount = 1
        self.test = False
        self.__endOnClosingOooElement = True
        if name is not None:
            self.__oooElementName = name
            self.processElement(name, attrs)
        self.__ignoreOooElements = ["text:list", "text:list-item", "text:changed-region"]
        #self.__ignoreOooElements = ["text:changed-region"]
        #print "ooo2html utils init"
    
    
    # the parent state
    def __getParentState(self):
        return self.__parentState
    def __setParentState(self, value):
        self.__parentState = value
    parentState = property(__getParentState, __setParentState)
    
    
    # The common output ooo2xhtml object
    def __getOoo2xhtml(self):
        return self.__o
    o = property(__getOoo2xhtml)
    
    
    # the current output element for this state
    def __getCurrentElement(self):
        if self.__currentElement is not None:
            return self.__currentElement
        else:
            return self.__parentState.currentElement
    def __setCurrentElement(self, value):
        self.__currentElement = value
    currentElement = property(__getCurrentElement, __setCurrentElement)
    
    
    # the base element for this state
    def __getStateElement(self):
        return self.__stateElement
    def __setStateElement(self, value):
        self.__currentElement = value
        self.__stateElement = value
    stateElement = property(__getStateElement, __setStateElement)
    
    
    # Get all text data that was processed/parsed in this state
    def __getData(self):
        return self.__data
    def __setData(self, value):
        self.__data = value
    data = property(__getData, __setData)
    
    
    # This states style (attribute)
    def __getStyle(self):
        return self.__style
    def __setStyle(self, value):
        if value is None:
            self.__level = 0
        else:
            self.__level = value.level
        self.__style = value
    style = property(__getStyle, __setStyle)
    
    
    #
    def __getLevel(self):
        return self.__level
    level = property(__getLevel)
    
    
    # 
    def __getEndOnClosingOooElement(self):
        return self.__endOnClosingOooElement
    def __setEndOnClosingOooElement(self, value):
        self.__endOnClosingOooElement = value
    endOnClosingOooElement = property(__getEndOnClosingOooElement, __setEndOnClosingOooElement)
    
    
    #
    def __getDepthCount(self):
        return self.__depthCount
    def __setDepthCount(self, value):
        self.__depthCount = value
        #if value==0:
        #    self.testEvent(value)
    depthCount = property(__getDepthCount, __setDepthCount)
    
    def testEvent(self, *args):
        ##
#        import traceback
#        print "a closingState"
#        for x in range(3):
#            # callerInfo = (file, line, method, code)
#            callerInfo = traceback.extract_stack(limit=3+x)[0]
#            print callerInfo
        ##
        pass

    def rollback(self):
        self.__stateElement = None
        self.__o.state = self.__parentState
    
    # A base method.  Note: must NOT be overriden
    #  called when a new element is parsed by the SAX parser
    def sElement(self, name, attrs):
        if name in self.__ignoreOooElements:
            return
        if self.newState(name, attrs):
            return
        if self.depthCount<1:        # End Test
            self.endState()
            self.__parentState.sElement(name, attrs)
            return
        self.depthCount += 1
        self.startElement(name, attrs)
    
    
    # a virtual method that may be overriden
    #  called when a new element is parsed, that does not cause a new state object to be created
    def startElement(self, name, attrs):
        pass
    
    
    # a virtual method that may be overriden (should not need to be thou)
    #  called on when processing closing elements
    #  Note: The default dehaviour is to end on the closing element (that created this state)
    def endTest(self, name):
        if self.__endOnClosingOooElement:
            return name==self.__oooElementName
    
    
    # A base method.  Note: must NOT be overriden
    #   called when ending/closing the current state(object)
    def endState(self):
        self.depthCount = -1
        self.closingState()
        #if self.currentElement.items==[]:
        #    c = comment("empty")
        #    self.currentElement.addChild(c)
        if self.__stateElement is not None:
            if self.__stateElement.items==[]:
                self.__stateElement.addChild(comment("empty"))
            self.__parentState.currentElement.addChild(self.__stateElement)
        self.__o.state = self.__parentState
    
    
    # Called to close an unwanted state object
    def close(self):
        self.closingState()
    
    
    # A base method.  Note: must NOT be overriden
    #  called when a end element is parsed by the SAX parser
    def eElement(self, name):
        if name in self.__ignoreOooElements:
            return
        self.depthCount -= 1
        if self.depthCount<0:
            self.endState()
            try:
                self.__parentState.eElement(name)
            except Exception, e:
                if errOutput is not None:
                    errOutput.write("error in eElement() - '%s'\n" % str(e))
                    errOutput.write("eElement name=%s %s\n" % (name, self))
                    if str(e).startswith("'myObj'"):
                        errOutput.write(" hint: error in closing elements in the correct order!\n")
            return
        if self.endTest(name):
            self.endState()
        else:
            self.endElement(name)
    
    
    # a virtual method that may be overriden
    def endElement(self, name):
        pass
    
    
    # a virtual method that may be overriden
    #  called when a new text data is parsed by the SAX parser
    def characters(self, data):
        if self.depthCount<1:
            if re.sub("\s*", "", data)!="":
                self.endState()
                self.__parentState.characters(data)
                return
        self.__data += data.encode("utf-8")
    
    # a virtual method to be overriden
    def processElement(self, name, attrs):
        pass
    
    
    # a virtual method to be overriden
    def closingState(self):
        """ do any state finalization/cleanup here """
        pass
    
    
    # Utility methods
    def nameTranslate(self, name):
        return name.replace(" ", "_").replace(".", "_")
    
    
    def convertUnits(self, value):
        if value.endswith("in"):
            value = value[:-2]
            value = float(value)
            value *= 96     #
            value = int(round(value))
        elif value.endswith("cm"):
            value = value[:-2]
            value = float(value)
            value *= 37.8   # 96 / 2.54
            value = int(round(value))
        elif value.endswith("mm"):
            value = value[:-2]
            value = float(value)
            value *= 3.78   # 96 / 25.4
            value = int(round(value))
        elif value.endswith("pt"):  # pica is same as point
            value = value[:-2]
            value = float(value)
            value *= 1.33   # 96 / 72
            value = int(round(value))
        return str(value)
    
    
    def getID(self):
        return "id" + str(self.__o.getIDCount())
    
    
    def resetIDCount(self):
        self.__o.resetIDCount()



class startState(stateObject):
    def __init__(self, parentState, name, attrs=None, o=None):
        class myObj(object):
            def __init__(self):
                self.parentState = None
        obj = myObj()
        obj.o = o
        obj.currentElement = o.shtml.body
        stateObject.__init__(self, obj, name, attrs)

    def startElement(self, name, attrs):
        pass
    
    def characters(self, data):
        pass


class ignoreState(stateObject):
    def __init__(self, parentState, name, attrs=None, style=None):
        stateObject.__init__(self, parentState, name, attrs)
    
    def startElement(self, name, attrs):
        pass
        
    def characters(self, data):
        pass




