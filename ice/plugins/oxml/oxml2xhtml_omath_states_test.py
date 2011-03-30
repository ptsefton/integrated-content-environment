#!/usr/bin/env python
#
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

from unittest import TestCase
import sys

from oxml2xhtml_omath_states import BaseState
from oxml2xhtml_omath_states import (OMathState)

# Note: this should be replaced by a mock object
from shtml import Shtml
from oxml2xhtml_utils import SaxContentHandler, saxParseString


stateTree = {
    "BaseState":{"m:oMath":OMathState},
    "OMathState": {}
}

testOMathSaxEvents = [("startElement", "m:oMath", {}), ("endElement", "m:oMath", None)]

class MockParentState(object):
    def __init__(self):
        self._html = Shtml()
        self._currentHtmlElement = self._html.body
        class Object(object): pass
        self._oxml = Object()
        self.startDataCapturingCalled = False
        self.stopDataCapturingCalled = False
        def startDataCapturing():
            self.startDataCapturingCalled = True
        def stopDataCapturing():
            self.stopDataCapturingCalled = True
        self._oxml.startDataCapturing = lambda s : startDataCapturing()
        self._oxml.stopDataCapturing = lambda s : stopDataCapturing()
    @property
    def html(self):
        return self._html
    @property
    def currentHtmlElement(self):
        return self._currentHtmlElement
    @property
    def oxml(self):
        return self._oxml



class OMathStateTest(TestCase):
    def setUp(self):
        BaseState._stateTree = stateTree
        self.parentState = MockParentState()
        self.baseState = BaseState(self.parentState, name=None, attrs={})

    def tearDown(self):
        pass

    def testDataCapture(self):
        # Note: Currently this the only functionality in OMathState
        e = testOMathSaxEvents
        eCall(self.baseState, e[0])
        state = self.baseState._oxml.currentState
        self.assertEquals(state.stateName, "OMathState")
        eCall(state, e[1])
        state = self.baseState._oxml.currentState
        self.assertEquals(state.stateName, "BaseState")
        self.assertTrue(self.parentState.startDataCapturingCalled)
        self.assertTrue(self.parentState.stopDataCapturingCalled)


def eCall(o, d):
    name, data, attr = d
    f = getattr(o, "_%s" % name)
    if name=="startElement":
        r = f(data, attr)
    else:
        r = f(data)
    return r


class XmlSaxParser(object, SaxContentHandler):
    @staticmethod
    def Process(xmlStr):
        s = XmlSaxParser()
        return s.process(xmlStr)

    def __init__(self):
        SaxContentHandler.__init__(self)
        self._events = []

    def process(self, xmlStr):
        saxParseString(xmlStr, self)
        return self._events

    #===========================
    # sax event handler methods
    #===========================
    def startElement(self, name, _attrs):
        attrs = {}
        for k in _attrs.keys():
            attrs[k]=_attrs.get(k)
        #self.__currentState._startElement(name, attrs)
        self._events.append(("startElement", name, attrs))

    def endElement(self, name):
        #self.__currentState._endElement(name)
        self._events.append(("endElement", name, None))

    def characters(self, data):
        #self.__currentState._characters(data)
        data = data.strip()
        if data=="":
            return
        self._events.append(("characters", data, None))
    #===========================
#testOMathSaxEvents = XmlSaxParser.Process(testTableXml)



def runUnitTests(locals):
    print "\n\n\n\n"
    if sys.platform=="cli":
        import clr
        import System.Console
        System.Console.Clear()
        print "---- Testing under IronPython ----"
    else:
        print "---- Testing ----"

    # Run only the selected tests
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals.values() \
                        if hasattr(i, "__bases__") and \
                            (TestCase in i.__bases__)]
        testing = []
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            for i in l:
                if i.lower() not in runTests:
                    delattr(x, i)
                else:
                    testing.append(i)
        x = None
        num = len(testing)
        if num<1:
            print "No selected tests found! - %s" % str(args)[1:-1]
        elif num==1:
            print "Running selected test - %s" % (str(testing)[1:-1])
        else:
            print "Running %s selected tests - %s" % (num, str(testing)[1:-1])
    from unittest import main
    main()


if __name__=="__main__":
    runUnitTests(locals())
    sys.exit(0)



