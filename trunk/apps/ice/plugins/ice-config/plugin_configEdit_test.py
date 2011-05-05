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

import sys
if sys.path.count("../ice")==0: sys.path.append("../ice")

from config_edit import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
from file_system import *
from system import *
from cStringIO import StringIO


testRepUrl = "http://ice.usq.edu.au/svn-local/ice/trunk/sample-content"
testRepUsername = "icetest"
testRepPassword = "icetest"


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
class EditConfigXmlTests(TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO()        
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testInit(self):
        editConfigXml = EditConfigXml(config=config, fileSystem=fs, system=system)
    
    def testEdit(self):
        versionInfoSummary = "ICE Version information summary."
        versionInfoSummary = IceCommon.textToHtml(str(versionInfoSummary))
        mockRequestData = MockEditConfigXmlRequestData()
        editConfigXml = EditConfigXml(config=config, fileSystem=fs, \
                        system=system, xmlParser=IceCommon.Xml, \
                        versionInfoSummaryHtml=versionInfoSummary)
        html = editConfigXml.edit(requestData=mockRequestData, configFile=None)
    
    def debugWrite(self, msg):
        self.stdout.write(msg + "\n")



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






