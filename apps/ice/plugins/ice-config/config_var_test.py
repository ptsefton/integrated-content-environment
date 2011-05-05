#!/usr/bin/env python
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

try:
    from xml.etree import ElementTree as ElementTree
except ImportError:
    try:
        import ElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree


from config_var import Var

# Var
# Constructor:
#   Var(ElementTree)
# Methods:
#   processVarElement(varNode)                      -> (name, value, desc)
#   getVarElement(name, value, description=None)    -> element


class VarTest(TestCase):
    testData = {
        "string":('<var desc="A string" name="tests" type="string" value="str" />',
                ("tests", "str", "A string")),
        "boolean":('<var desc="A boolean" name="testb" type="boolean" value="True" />',
                ("testb", True, "A boolean")),
        "integer":('<var desc="A integer" name="testi" type="integer" value="42" />',
                ("testi", 42, "A integer")),
        "list":('<var desc="A list" name="testl" type="list"><var type="string" value="str" /><var type="integer" value="42" /></var>',
                ("testl", ["str", 42], "A list")),
        "dict":('<var desc="A dict" name="testd" type="dict"><var name="key" type="string" value="value" /></var>',
                ("testd", {"key":"value"}, "A dict"))
    }

    def setUp(self):
        self.et = ElementTree
        self.var = Var(ElementTree)

    def tearDown(self):
        pass

    def toString(self, e):
        return self.et.tostring(e)

    def testGetVarElement(self):
        var = self.var
        testData = self.testData
        for key, value in testData.iteritems():
            elemStr, args = value
            e = var.getVarElement(*args)
            self.assertEquals(self.toString(e), elemStr)

    def testProcessVarElement(self):
        var = self.var
        testData = self.testData
        for key, value in testData.iteritems():
            elemStr, expected = value
            e = self.et.XML(elemStr)
            name, value, desc = var.processVarElement(e)
            #print "name='%s', value=%s, desc='%s'" % (name, repr(value), desc)
            self.assertEquals((name, value, desc), expected)




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
