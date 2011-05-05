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


from plugin_config2 import IceConfig

testConfig2XmlStr = """<iceConfig version="2.0">
	<iceWebHost>127.0.0.1</iceWebHost>
	<iceWebPort>8000</iceWebPort>
	<settings>
		<var name="asServiceOnly" type="boolean" value="False" />
        <var name="testDefault" type="string" value="Default" desc="TestDefaultDesc"/>
		<var name="defaultRepositoryName" type="string" value="TWO" />
	</settings>
	<repositories>
		<repository documentTemplatesPath="/templates" exportPath="/ice/export/ONE"
                name="ONE" path="/ice/ONE" url="IceOneUrl">
			<settings />
		</repository>
		<repository documentTemplatesPath="/templates" exportPath="/ice/export/TWO"
                name="TWO" path="/ice/TWO" url="IceTwoUrl">
			<settings>
                <var name="testDefault" type="string" value="OverriddenValue" />
                <var name="test" type="string" value="Testing" desc="TestDesc"/>
			</settings>
		</repository>
	</repositories>
</iceConfig>"""

    # Constructor:
    #   IceConfig(iceContext, **kwargs)
    #                   iceContext.ElementTree  # plug more if converting from old format
    # Properties:
    #   settings
    #   defaultRepositoryName
    #   repositories
    #   port
    #   hostAddress
    # Methods:
    #   setDefaultRepositoryName(name)
    #   serialize()
    #   process(xmlStr)
    #   save()
    #
    #   createNewRepository(name, url, path, documentTemplatesPath, exportPath) -> rep
    #   addRepository(rep)
    #   deleteRepository(name)
    #   getRepNames()
    #   getRep(name)

class IceConfigTest(TestCase):
    def setUp(self):
        class Object(object): pass
        self.context = Object()
        self.context.ElementTree = ElementTree

    def tearDown(self):
        pass

    def testProcessAndProperties(self):
        # Properties:
        #   settings
        #   defaultRepositoryName
        #   port
        #   hostAddress
        #   repositories
        config = IceConfig(self.context)
        config.process(testConfig2XmlStr)
        self.assertEquals(config.settings["testDefault"], "Default")
        self.assertEquals(config.defaultRepositoryName, "TWO")
        self.assertEquals(config.port, "8000")
        self.assertEquals(config.hostAddress, "127.0.0.1")
        reps = {}
        for r in config.repositories:
            reps[r.name] = r
            #print r.name, r.settings
        rep1 = reps["ONE"]
        rep2 = reps["TWO"]
        self.assertEquals(rep1.settings["testDefault"], "Default")
        self.assertEquals(rep1.settings.get("test", "not set"), "not set")
        self.assertEquals(rep2.settings["testDefault"], "OverriddenValue")
        self.assertEquals(rep2.settings.get("test", "not set"), "Testing")

    def testSetDefaultRepositoryName(self):
        config = IceConfig(self.context)
        self.assertEquals(config.defaultRepositoryName, None)
        config.setDefaultRepositoryName("ONE")
        self.assertEquals(config.defaultRepositoryName, "ONE")
        self.assertEquals(config.settings["defaultRepositoryName"], "ONE")

    def testSerialize(self):
        expected1 = """<iceConfig version="2.0">
	<iceWebHost>localhost</iceWebHost>
	<iceWebPort>8000</iceWebPort>
	<iceWebServer>Paste</iceWebServer>
	<settings />
	<repositories />
</iceConfig>"""
        config = IceConfig(self.context)
        self.assertEquals(config.serialize(), expected1)
        config.settings.set("key", "value")
        e = expected1
        e = e.replace("<settings />", '<settings>\n\t\t<var name="key" type="string" value="value" />\n\t</settings>')
        self.assertEquals(config.serialize(), e)

    def testSave(self):
        config = IceConfig(self.context)
        saveStr = [None]
        def saveMethod(xmlStr):
            saveStr[0] = xmlStr
        config.save(saveMethod)
        self.assertEquals(saveStr[0], config.serialize())

    def testCreateNewRepository(self):
        # createNewRepository(name, url, path, documentTemplatesPath, exportPath) -> rep
        self.testAddRepository()

    def testAddRepository(self):
        # addRepository(rep)
        config = IceConfig(self.context)
        rep = config.createNewRepository("Name", "Url", "Path",
                                        "DocTemplatesPath", "ExportPath")
        config.addRepository(rep)
        self.assertEquals(config.getRepNames(), ["Name"])
        #print config.serialize()

    def testDeleteRepository(self):
        # deleteRepository(name)
        config = IceConfig(self.context)
        config.process(testConfig2XmlStr)
        self.assertEquals(config.getRepNames(), ["ONE", "TWO"])
        config.deleteRepository("ONE")
        self.assertEquals(config.getRepNames(), ["TWO"])

    def testGetRepNames(self):
        # getRepNames()
        config = IceConfig(self.context)
        config.process(testConfig2XmlStr)
        self.assertEquals(config.getRepNames(), ["ONE", "TWO"])

    def testGetRep(self):
        # getRep(name)
        config = IceConfig(self.context)
        config.process(testConfig2XmlStr)
        rep = config.getRep("ONE")
        self.assertEquals(rep.name, "ONE")



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
