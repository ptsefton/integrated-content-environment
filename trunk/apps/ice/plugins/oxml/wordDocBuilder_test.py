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

from wordDocBuilder import WordDocBuilder
# Constructor:
#   WordDocBuilder()
# Properties:
# Methods:
#   addParagraph(contents)
#   createTextRun(text)         - returns a textRun string
#   toString()


class WordDocBuilderTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCreateTextRun(self):
        docBuilder = WordDocBuilder()
        textRun = docBuilder.createTextRun("testing")
        self.assertEquals(textRun, '<w:r><w:t xml:space="preserve">testing</w:t></w:r>')

    def testAddParagraph(self):
        docBuilder = WordDocBuilder()
        docBuilder.addParagraph("TestingText")
        expected = '<w:p><w:r><w:t xml:space="preserve">TestingText</w:t></w:r></w:p>'
        self.assertEquals(docBuilder._getBodyContents()[0], expected)
        docBuilder.addParagraph(["TestingText", "Two"])
        expected = '<w:p><w:r><w:t xml:space="preserve">TestingText</w:t></w:r><w:r><w:t xml:space="preserve">Two</w:t></w:r></w:p>'
        self.assertEquals(docBuilder._getBodyContents()[1], expected)

    def testToString(self):
        docBuilder = WordDocBuilder()
        docBuilder.addParagraph("TestingText")
        h = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        expected = """<w:p><w:r><w:t xml:space="preserve">TestingText</w:t></w:r></w:p>"""
        expected = docBuilder.DocBodyElement % expected
        self.assertEquals(docBuilder.toString(), h+expected)




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



