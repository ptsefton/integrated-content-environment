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

from shtml import Shtml

# Shtml
    # Constructor()
    # Properties:
    #   title
    #   head    (ReadOnly Element)
    #   body    (ReadOnly Element)
    # Methods:
    #   addStyle(s, value=None)
    #   formatted(includeXmlDec=False, includeDocType=True)
    #   toString(includeXmlDec=False, includeDocType=True)
    #   createStyle(name, value)
    #   createElement(*args, **kwargs)
    #   createAttribute(name, value, parent=None)
    #   createText(value, parent=None)
    #   createRawText(value, parent=None)
    #   createComment(value, parent=None)
    #   formatted(includeXmlDec=False, includeDocType=True)
    #   toString(includeXmlDec=False, includeDocType=True)
    #   __str__()

# Element
    # Constructor(*args, **kwargs)
    #   e.g. Element("div", "text contents", attName=2, {"name":"test", "class":"hi"})
    # Properties:
    #    name          (Read/Write)
    #    localName     (ReadOnly)
    #    atts          (ReadOnly)
    #    items         (ReadOnly)   children
    #    value         (ReadOnly)
    #    text          (ReadOnly)
    # Methods:
    #    addAttribute(name, value=None)
    #    setAttribute(name, value=None)
    #    getAttribute(name)
    #    remove(node=None)
    #    addChild(node)
    #    addChildElement(*args, **kwargs) - same argument options as this class
    #    getNextNode(node=None)
    #    prepend(n)
    #    getFirstChild()
    #    getChildren()
    #    getLastChild()
    #    __str__()


class ShtmlTest(TestCase):
    ExpectedEmpty = """<html xmlns="http://www.w3.org/1999/xhtml"><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type" /><title></title><style type="text/css">/*<![CDATA[*/

/*]]>*/
</style></head><body></body></html>"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        shtml = Shtml()
        str = shtml.toString(includeXmlDec=False, includeDocType=False)
        self.assertEquals(str, self.ExpectedEmpty)

    def testProperties(self):
        shtml = Shtml()
        self.assertEquals(shtml.title, "")
        shtml.title = "Test"
        self.assertEquals(shtml.title, "Test")
        self.assertEquals(shtml.head.items[1].value, "Test")
        self.assertEquals(shtml.head.__class__.__name__, "Element")
        self.assertEquals(shtml.body.__class__.__name__, "Element")
        self.assertEquals(str(shtml.body), "<body></body>")

    def testAddStyle(self):
        shtml = Shtml()
        s1 = "color:red;"
        s2 = "background-color:black;"
        shtml.addStyle("div", s1)
        shtml.addStyle("div", s2)
        shtml.toString()
        lines = str(shtml.head.getLastChild()).split("\n")
        self.assertEquals(lines[1], "div {%s}" % s1)
        self.assertEquals(lines[2], "div {%s}" % s2)

    def testCreateElement(self):
        shtml = Shtml()
        e = shtml.createElement("test", "text&", {"class":"CLS", "t":"'\""}, att1=1)
        self.assertEquals(str(e), '<test att1="1" class="CLS" t="&#39;&quot;">text&amp;</test>')

    def testToString(self):
        shtml = Shtml()
        str = shtml.toString(includeXmlDec=False, includeDocType=False)
        self.assertEquals(str, self.ExpectedEmpty)
        str = shtml.toString(includeXmlDec=True, includeDocType=False)
        self.assertEquals(str, '<?xml version="1.0" encoding="UTF-8"?>\n' + self.ExpectedEmpty)
        str = shtml.toString(includeXmlDec=False, includeDocType=True)
        self.assertEquals(str, '<!DOCTYPE html>\n' + self.ExpectedEmpty)

    def testHtml5VoidElement(self):
        HTML5VoidElements = ["area", "base", "br", "col", "command", "embed", "hr",
        "img", "input", "keygen", "link", "meta", "param", "source"]
        shtml = Shtml()
        for ename in HTML5VoidElements:
            e = shtml.createElement(ename)
            self.assertEquals(str(e), "<%s />" % ename)
        for ename in ["p", "div", "span"]:
            e = shtml.createElement(ename)
            self.assertNotEquals(str(e), "<%s />" % ename)




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
