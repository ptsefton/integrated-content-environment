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

from config_rep import IceRepConfig
    # Constructor:
    #   IceRepConfig(ElementTree, defaultSettings)
    # Properties:
    #   settings
    #   url
    #   path
    #   documentTemplatesPath
    #   name
    #   exportPath
    #   repName
    # Methods:
    #   processRepElement(repNode)      -> None
    #   getRepElement()                 -> element


testRepXmlStr = """<repository
        documentTemplatesPath="/templates"
        exportPath="/media/disk/ice/Exports"
        name="testRepName"
        path="/home/user/ice"
        url="http://localhost/svn">
  <settings>
    <var name="test" type="string" value="testing" desc="Test" />
  </settings>
</repository>"""

class IceRepConfigTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testProcessRepElement(self):
        e = ElementTree.XML(testRepXmlStr)
        repConfig = IceRepConfig(ElementTree, {})
        repConfig.processRepElement(e)
        #print repConfig.settings
        self.assertEquals(repConfig.settings["test"], "testing")
        self.assertEquals(repConfig.url, "http://localhost/svn")
        self.assertEquals(repConfig.path, "/home/user/ice")
        self.assertEquals(repConfig.documentTemplatesPath, "/templates")
        self.assertEquals(repConfig.name, "testRepName")
        self.assertEquals(repConfig.exportPath, "/media/disk/ice/Exports")
        self.assertEquals(repConfig.repName, "")

    def testGetRepElement(self):
        expected1 = '<repository documentTemplatesPath="templates" exportPath="" name="" path="" url=""><settings /></repository>'
        expected2 = '<repository documentTemplatesPath="TPath" exportPath="EPath" name="Name" path="Path" url="URL"><settings><var desc="desc" name="key" type="string" value="value" /></settings></repository>'
        repConfig = IceRepConfig(ElementTree, {})
        e = repConfig.getRepElement()
        s = ElementTree.tostring(e)
        self.assertEquals(s, expected1)
        repConfig.settings.set("key", "value", "desc")
        repConfig.url = "URL"
        repConfig.path = "Path"
        repConfig.documentTemplatesPath = "TPath"
        repConfig.name = "Name"
        repConfig.exportPath = "EPath"
        repConfig.repName = "RepName"
        e = repConfig.getRepElement()
        s = ElementTree.tostring(e)
        self.assertEquals(s, expected2)



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
