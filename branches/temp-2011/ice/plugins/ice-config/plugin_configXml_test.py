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

from config_xml import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os
from cStringIO import StringIO

import sys
sys.path.append("../ice-utils")
sys.path.append("../utils")
from file_system import FileSystem
from system import system
fs = FileSystem()
import xml_util

class mockOooPath(object):
    def isOooPathOK(self, *args, **kwargs):
        return True
    
    def getBestOooPath(self):
        return "/bestOooPath"
    
    def getOooPythonPath(self, oooPath):
        return oooPath + "/program/python.sh"
    
oooPath = mockOooPath()
import config_xml as config
config.oooPath = oooPath
config._fs, config._system = fs, system



class ConfigTests(TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = self.stdout
        try:
            config = Config(None)
        except: pass
    
    def testInit(self):
        config = Config(configFile="teste_config.xml")


    def testLoad(self):
        config = Config(configFile="test_config.xml")
        config.load()
        self.assertFalse(config.using_defaults)
        self.assertEqual(config.get("icewebPort"), 8000)
        self.assertEqual(config.get("oooPath"), "/etc/openoffice.org-2.1")
        self.assertEqual(config.get("oooPythonPath"), "/etc/openoffice.org-2.1/program/python.sh")
        self.assertEqual(config.get("oooPort"), "2002")
        self.assertEqual(config.get("emailFromAddress"), "test@mailAddress")
        self.assertEqual(config.get("emailSmtpServer"), "smtp")
        self.assertEqual(config.get("emailUsername"), "username")
        self.assertEqual(config.get("defaultRepositoryName"), "Test")
        self.assertEqual(len(config.repositories), 4)
        # # repositories = { "Name" : [path, url, exportPath, documentTemplatesPath] }
        rep = config.repositories["TestSample"]
        self.assertEqual(rep[0], "../../testSample")
        self.assertEqual(rep[1], "file:///home/ward/work/ice/svnTestSampleRep")
        self.assertEqual(rep[2], "../../exports")
        self.assertEqual(rep[3], "/templates")

    def testDefaults(self):
        config = Config(configFile="invalid_config.xml")
        config.load()
        self.assertTrue(config.using_defaults)
        
        
    def testSerialize(self):
        config = Config(configFile="test_config.xml")
        config.load()
        s = config.serialize(True)
        self.assertTrue(len(s)>1024)
    
    
    def testSave(self):
        config = Config(configFile="invalid_config.xml")
        config.save(True, "tempTestConfig.xml")
        fs.delete("tempTestConfig.xml")

    
    def testSettings(self):
        config = Config(configFile="test_config.xml")
        config.load()
        self.assertEqual(config["strTest"], "value1")
        self.assertEqual(config["strTest2"], "value2")
        self.assertEqual(config["intTest"], 42)
        self.assertEqual(config["intTest2"], 33)
        self.assertEqual(config["boolTest"], False)
        self.assertEqual(config["boolTest2"], True)
        self.assertEqual(config["array1"], ["one", "two", "three", "4"])
        self.assertEqual(config["array2"], ["one", "two", "three", "four", 5, "five"])
        self.assertEqual(config["dict1"], {"key1":"v", "key2":"v2"})
        self.assertEqual(config["dict2"], {"key1":"value", "key2":"value2", "key":"value", "k":45})

    
    def testSettingConfigValues(self):
        config = Config(configFile="test_config.xml")
        config.load()
        config["test1"] = "newValue"
        self.assertEqual(config["test1"], "newValue")
        config["testStr"] = "string"
        config["testInt"] = 42
        config["testBool"] = True
        config["testArr"] = [1,2,3]
        config["testDict"] = {"key":"value", "int":42, "bool":False }
        s = config.serialize(True)
        
        config = Config(configFile = s)
        config.load()
        self.assertEqual(config["testStr"], "string")
        self.assertEqual(config["testInt"], 42)
        self.assertEqual(config["testBool"], True)
        self.assertEqual(config["testArr"], [1,2,3])
        self.assertEqual(config["testDict"], {"key":"value", "int":42, "bool":False })
    
    


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())





