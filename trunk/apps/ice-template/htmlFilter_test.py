#!/usr/bin/env python
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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

from htmlFilter import HtmlFilter

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os


class HtmlFilterTests(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testFilterBasics(self):
        filter = HtmlFilter()
        self.assertEqual(filter.filter(None), "")
        self.assertEqual(filter.filter(""), "")
        self.assertEqual(filter.filter("one"), "one")
        self.assertEqual(filter.filter(True), "True")
        self.assertEqual(filter.filter(False), "False")
        self.assertEqual(filter.filter(1), "1")
        self.assertEqual(filter.filter([1, 2]), "[1, 2]")
    
    def testFilterUnicodeToUtf8(self):
        filter = HtmlFilter()
        self.assertEqual(filter.filter(u"\u2019"), "\xe2\x80\x99")
    
    def testHtmlEscaping(self):
        filter = HtmlFilter()
        self.assertEqual(filter.filter("< & ' \" > \t\n"), "&lt; &amp; &apos; &quot; &gt; \t\n")
    
    def testFilterOptions(self):
        filter = HtmlFilter()
        #   ${name, raw=True}       # no HTML escaping at all
        #   ${name, attr=True}      # (default) also escapes quotes and apos.
        #   ${name, text=True}      # does not escape quotes and apos.
        #   ${name, whiteText=True} # does not escape (" & ') but does also convert spaces, tabs and newlines
        self.assertEqual(filter.filter("< & ' \" > \t\n", raw=True, rawExpr="x"), "< & ' \" > \t\n")
        self.assertEqual(filter.filter("< & ' \" > \t\n", attr=True, rawExpr="x"),
                    "&lt; &amp; &apos; &quot; &gt; \t\n")
        self.assertEqual(filter.filter("< & ' \" > \t\n", text=True, rawExpr="x"), 
                    "&lt; &amp; ' \" &gt; \t\n")
        self.assertEqual(filter.filter("< & ' \" > \t\n", whiteText=True, rawExpr="x"), 
                    "&lt;&#160;&amp;&#160;'&#160;\"&#160;&gt;&#160;&#160;&#160;&#160;&#160;<br />")
    
    def testObjWithHtmlAttribute(self):
        filter = HtmlFilter()
        class Object(object): pass
        obj = Object()
        obj.html = "< & ' \" > \t\n"
        filter = HtmlFilter()
        self.assertEqual(filter.filter(obj), "< & ' \" > \t\n")



if __name__ == "__main__":
    import sys
    sys.path.append("../utils")
    from file_system import *
    from system import *
    system.cls()
    print "---- Testing ----"
    print
    
    # Run only the selected tests
    #  Test Attribute testXxxx.slowTest = True
    #  fastOnly (do not run any slow tests)
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = ["Add", "testAddGetRemoveImage"]
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and TestCase in i.__bases__]
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            testing = []
            for i in l:
                if i.lower() not in runTests:
                    #print "Removing '%s'" % i
                    delattr(x, i)
                else:
                    #print "Testing '%s'" % i
                    testing.append(i)
        x = None
        print "Running %s selected tests - %s" % (len(testing), str(testing)[1:-1])
    
    unittest.main()





