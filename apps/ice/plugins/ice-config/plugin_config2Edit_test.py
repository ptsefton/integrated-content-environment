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
from plugin_config2Edit import ConfigEditor

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


class MockEditConfigXmlRequestData(object):
    def __init__(self):
        self.__dict = dict()
    def has_key(self, key):
        return self.__dict.has_key()
    def value(self, key, defaultValue=None):
        return self.__dict.get(key, defaultValue)
    def setValue(self, key, value):
        self.__dict[key] = value


class MockFileSystem(object):
    # fileSystem usage: split(), exists(), join()
    def __init__(self):
        pass
    def split(self, arg):
        return fs.split(arg)
    def exists(self, name):
        return fs.exists(name)
    def join(self, *args):
        return fs.join(*args)

    
class MockSystem(object):
    # system usage: getOsHomeDirectory(), isWindows
    def __init__(self, isWindows=False):
        self.__isWindows = isWindows
    
    @property
    def isWindows(self):
        return self.__isWindows
    
    def getOsHomeDirectory(self):
        return "/osHomeDir"


class MockConfig(object):
    # config usage: oooPath, settings, loadConfigValues()
    #       config.oooPath.isOooPathOK
    #       config.oooPath.getBestOooPath
    #       config.oooPath.getOooPythonPath
    #       config.settings.configFile
    def __init__(self):
        #self.oooPath = Object()
        #self.settings = Object()
        self.oooPath = config.oooPath
        self.settings = config.settings
    
    def loadConfigValues(self, configFile):
        return config.loadConfigValues(configFile)
    
    

## ===============================
##   TESTS  
## ===============================
class ConfigEditorTests(TestCase):
    def setUp(self):
        class Object(object): pass
        def getOsHomeDirectory():
            return "/home/user/"
        def readFile(file):
            return "[file: %s contents]" % file
        def textToHtml(s):
            return s
        self.context = Object()
        self.context.ElementTree = ElementTree
        self.context.system = Object()
        self.context.system.getOsHomeDirectory = getOsHomeDirectory
        self.context.fs = Object()
        self.context.fs.readFile    = readFile
        self.context.textToHtml = textToHtml
        self.context.versionInfoSummary = "ICE version info summary."
        self.context.config = IceConfig(self.context)
        self.context.config.process(testConfig2XmlStr)

    
    def tearDown(self):
        pass
    
    def testConstructor(self):
        editor = ConfigEditor(self.context)
        d = editor.getDisplayJson()
        #print d
        print d
    



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






