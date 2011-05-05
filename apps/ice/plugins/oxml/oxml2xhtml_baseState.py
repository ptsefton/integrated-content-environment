#    Copyright (C) 2010  Distance and e-Learning Centre,
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



class BaseState(object):
    # Constructor:
    #   BaseState(parentState, name=None, attrs={})
    # Properties:
    #   html
    #   currentHtmlElement
    #   oxml
    #   parentState
    #   stateName
    #   propertyState
    #   parentParaState
    # Methods:
    #   createNewState(klass, name, attrs)
    #   endState()                          # return False if endState is canceled
    #   startElement(name, attrs)           # a virtual method that may be overriden
    #   endElment(name)                     # a virtual method that may be overriden
    #   characters(text)                    # a virtual method that may be overriden

    _stateTree = {}

    def __init__(self, parentState, name=None, attrs={}):
        self._parentState = parentState
        self._html = parentState.html
        self._currentHtmlElement = parentState.currentHtmlElement
        self._oxml = parentState.oxml      # the base/root Oxml2xhtml object
        self._eName = name
        self._attrs = attrs
        self._style = None
        self._text = ""
        #print "-%s-" % self.stateName


    @property
    def html(self):
        return self._html

    @property
    def currentHtmlElement(self):
        return self._currentHtmlElement

    @property
    def oxml(self):
        return self._oxml

    @property
    def parentState(self):
        return self._parentState

    @property
    def stateName(self):
        return self.__class__.__name__

    @property
    def propertyState(self):
        return None

    @property
    def parentParaState(self):
        p = self._parentState
        while p.stateName!="NullState":
            if p.stateName=="ParaState":
                return p
            p = p.parentState
        return None

    
    # Called to create new states
    #  can be overriden to prevent the creation of a new state
    def createNewState(self, klass, name, attrs):
        newState = klass(self, name, attrs)
        return newState


    # a virtual method that may be overriden
    def endState(self):
        # return False if endState is canceled
        return True


    # a virtual method that may be overriden
    #  called when a new element is parsed, that does not cause a new state object to be created
    def startElement(self, name, attrs):
        pass


    # a virtual method that may be overriden
    def characters(self, text):
        pass


    # a virtual method that may be overriden
    def endElement(self, name):
        pass

    
    ## SAX event handlers

    # A base method.  Note: must NOT be overriden
    #  called when a new element is parsed by the SAX parser
    def _startElement(self, name, attrs):
        states = self._stateTree.get(self.stateName, {})
        nextState = states.get(name)
        if nextState is not None:
            newState = self.createNewState(nextState, name, attrs)
            if newState is not None:
                self._oxml.currentState = newState
                return
        self.startElement(name, attrs)


    # A base method.  Note: must NOT be overriden
    def _characters(self, text):
        self.characters(text)


    # A base method.  Note: must NOT be overriden
    def _endElement(self, name):
        if name==self._eName:
            if self.endState():
                self._oxml.currentState = self._parentState
                return
        self.endElement(name)










