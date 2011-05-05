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

from oxml_docRels import DocRels

# word/_rels/document.xml.rels
testFile = "testData/document.xml.rels"

class DocRelsTest(TestCase):

    def setUp(self):
        f = open(testFile, "rb")
        self.docXmlRelsStr = f.read()
        f.close()

    def tearDown(self):
        pass

    #def getTarget(self, id):
    #def getType(self, id):
    #def getTargetMode(self, id):
    def testGetTarget(self):
        docRels = DocRels(self.docXmlRelsStr)
        id = "rId1"
        target = docRels.getTarget(id)
        expected = u'styles.xml'
        self.assertEquals(target, expected)

    def testGetType(self):
        docRels = DocRels(self.docXmlRelsStr)
        id = "rId1"
        type = docRels.getType(id)
        expected = u'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles'
        self.assertEquals(type, expected)

    def testGetTargetMode(self):
        docRels = DocRels(self.docXmlRelsStr)
        id = "rId1"
        targetMode = docRels.getTargetMode(id)
        self.assertEquals(targetMode, None)


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



