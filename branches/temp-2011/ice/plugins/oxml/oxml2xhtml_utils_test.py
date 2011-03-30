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
from time import sleep


# NOTE: oxml2xhtml_utils also fixes up the SAX parser when working under IronPython
from oxml2xhtml_utils import TimeIt, DataCapture, Image, ParseWordHtml
from oxml2xhtml_utils import SaxContentHandler, saxParseString


class DataCaptureTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAll(self):
        #startElement(name, attrs)
        #endElement(name)
        #characters(data)
        #toString()
        dc = DataCapture()
        dc.startElement("one", {"att":"a"})
        dc.characters("text")
        dc.endElement("one")
        self.assertEquals(dc.toString(), '<one att="a">text</one>')



class ParseWordHtmlTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testX(self):
        pass


class TimeItTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testMS(self):
        timeIt = TimeIt()
        sleep(.01)
        timeIt.stop()
        mS = timeIt.mS()
        s = str(timeIt)
        self.assertEquals(mS, 10)
        self.assertEquals(s, "10mS")





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



