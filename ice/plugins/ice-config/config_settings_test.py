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


from config_settings import Settings
# Settings
# Constructor:
#   Settings(ElementTree, defaultSettings=None)
# Properties:
#   configEditorPluginName
#   ooo_port
#   ooo_host
#   ooo_python_path
#   [key]       # Read and Write
#   delete key
# Methods:
#   get(name, default=None)
#   getList()
#   keys()
#   getDescriptionFor(name)
#   setDescriptionFor(name, description)
#   set(name, value, description=None)
#   processSettingsElement(settingsNode)
#   getSettingsElement()

testSettingXmlStr = """<settings>
  <var desc="A string" name="tests" type="string" value="str" />
  <var desc="A boolean" name="testb" type="boolean" value="True" />
  <var desc="A integer" name="testi" type="integer" value="42" />
  <var desc="A list" name="testl" type="list"><var type="string" value="str" /><var type="integer" value="42" /></var>
  <var desc="A dict" name="testd" type="dict"><var name="key" type="string" value="value" /></var>
</settings>"""


class SettingsTest(TestCase):
    def setUp(self):
        self.settings = Settings(ElementTree)

    def tearDown(self):
        pass

    def testProperties(self):
        #   configEditorPluginName
        #   ooo_port
        #   ooo_host
        #   ooo_python_path
        #   [key]       # Read and Write
        settings = self.settings
        self.assertEquals(settings.configEditorPluginName, "ice.config2-editor")
        self.assertEquals(settings.ooo_port, None)
        self.assertEquals(settings.ooo_host, None)
        self.assertEquals(settings.ooo_python_path, None)
        settings._defaultSettings = {"oooPort":"8000",
                                    "oooHost": "localhost",
                                    "oooPythonPath":"/openoffice/org/"}
        self.assertEquals(settings.ooo_port, "8000")
        self.assertEquals(settings.ooo_host, "localhost")
        self.assertEquals(settings.ooo_python_path, "/openoffice/org/")

    def testGet(self):
        settings = self.settings
        self.assertEquals(settings.get("test", "default"), "default")
        settings._defaultSettings = {"test":"testing"}
        self.assertEquals(settings.get("test", "default"), "testing")

    def testGetList(self):
        expected = [('one', 'one', None, 'str', True),
                    ('three', 'False', None, 'bool', True),
                    ('two', '2', None, 'int', True)]
        settings = self.settings
        self.assertEquals(settings.getList(), [])
        settings._defaultSettings = {"one":"one", "two":2, "three":False}
        self.assertEquals(settings.getList(), expected)

    def testKeys(self):
        settings = self.settings
        self.assertEquals(settings.keys(), [])
        settings._defaultSettings = {"one":"one", "two":2, "three":False}
        self.assertEquals(settings.keys(), ["one", "three", "two"])

    def testGetDescriptionFor(self):
        settings = self.settings
        self.assertEquals(settings.getDescriptionFor("key"), None)
        settings.set("key", "value")
        self.assertEquals(settings.getDescriptionFor("key"), None)
        settings.set("key", "value", "desc")
        self.assertEquals(settings.getDescriptionFor("key"), "desc")

    def testSetDescriptionFor(self):
        settings = self.settings
        self.assertEquals(settings.getDescriptionFor("key"), None)
        settings.setDescriptionFor("key", "one")
        self.assertEquals(settings.getDescriptionFor("key"), "one")
        settings.setDescriptionFor("key", "two")
        self.assertEquals(settings.getDescriptionFor("key"), "two")

    def testSet(self):
        settings = self.settings
        self.assertEquals(settings["key"], None)
        settings.set("key", "value")
        self.assertEquals(settings["key"], "value")
        settings.set("key", "newvalue")
        self.assertEquals(settings["key"], "newvalue")

    def testProcessSettingsElement(self):
        settings = self.settings
        e = ElementTree.XML(testSettingXmlStr)
        settings.processSettingsElement(e)
        self.assertEquals(settings.keys(),
                            ['testb', 'testd', 'testi', 'testl', 'tests'])
        #print settings.getList()

    def testGetSettingsElement(self):
        settings = self.settings
        e = settings.getSettingsElement()
        self.assertEquals(ElementTree.tostring(e), "<settings />")

        settings._defaultSettings = {"one":"one", "two":2, "three":False}
        e = settings.getSettingsElement()
        self.assertEquals(ElementTree.tostring(e), "<settings />")

        settings.set("one", "str", "desc")
        e = settings.getSettingsElement()
        self.assertEquals(ElementTree.tostring(e),
            '<settings><var desc="desc" name="one" type="string" value="str" /></settings>')


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
