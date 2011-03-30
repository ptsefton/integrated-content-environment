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

import sys
from oxml2xhtml_baseState import BaseState
from unittest import TestCase

# BaseState
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

class BaseStateTest(TestCase):
    def setUp(self):
        class ParentState(object):
            @property
            def html(self):
                return "HTML"
            @property
            def currentHtmlElement(self):
                return "CurrentHtmlElement"
            @property
            def oxml(self):
                return "OXML"
            @property
            def parentState(self):
                return None
            @property
            def stateName(self):
                return "NullState"
        self.ps = ParentState()

    def tearDown(self):
        pass

    def testConstructor(self):
        state = BaseState(self.ps)
        state = BaseState(self.ps, "test", {"att1":"1"})

    def testProperties(self):
        state = BaseState(self.ps, "test", {"att1":"1"})
        self.assertEquals(state.html, "HTML")
        self.assertEquals(state.currentHtmlElement, "CurrentHtmlElement")
        self.assertEquals(state.oxml, "OXML")
        self.assertEquals(state.stateName, "BaseState")
        self.assertEquals(state.propertyState, None)
        self.assertEquals(state.parentParaState, None)

#   createNewState(klass, name, attrs)
#   endState()                          # return False if endState is canceled
#   startElement(name, attrs)           # a virtual method that may be overriden
#   endElment(name)                     # a virtual method that may be overriden
#   characters(text)                    # a virtual method that may be overriden
    def testCreateNewState(self):
        BaseState._stateTree = {}
        state = BaseState(self.ps, "test", {"att1":"1"})


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
