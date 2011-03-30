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

from htmlTemplate import HtmlTemplate

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os


class HtmlTemplateTests(TestCase):
    strTemplate = "$one, $two, ${three, raw=True}"
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testStrHtmlTemplate(self):
        htmlTemplate = HtmlTemplate(templateString=self.strTemplate)
        d = {"one":1, "two":"'<two> &'", "three":"<b>'Bold' &amp;</b>"}
        result = htmlTemplate.transform(d)
        self.assertEqual(result, "1, &apos;&lt;two&gt; &amp;&apos;, <b>'Bold' &amp;</b>")
        
        class Object(object): pass
        obj = Object()
        obj.html = "<b>Testing &amp; </b>"
        d = {"one":obj, "two":None, "three":True}
        result = htmlTemplate.transform(d)
        self.assertEqual(result, "%s, %s, %s" % (obj.html, "", True))
    
    def testStrHtmlTemplateAllowMissing(self):
        htmlTemplate = HtmlTemplate(templateString=self.strTemplate)
        result = htmlTemplate.transform({}, allowMissing=True)
        missing = htmlTemplate.missing
        self.assertEqual(missing, ["one", "two", "three"])
        self.assertEqual(result, ", , ")



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





