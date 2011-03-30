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

import os, sys
import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader

if sys.path.count("../utils")==0: sys.path.append("../utils")
import file_system
from cStringIO import StringIO


from ice_render import *



######### Test #########
class IceRenderTests(TestCase):
    def setUp(self):
        self.title = "TestTitle"
        self.xmlContent = "<body>Test body content.</body>"
    
    
    def tearDown(self):
        pass
    
    
    def dummyMethod(self, *args):
        return None
    
    
    def renderMethod(self, file, absFile, rep):         # method(file, absFile, self)
        from converted_data import ConvertedData
        #convertedData = method(file, absFile, self)
        convertedData = ConvertedData()
        convertedData.addMeta("title", self.title)
        convertedData.addMeta("testTwo", "Two")
        convertedData.addRenditionData(".xhtml.body", self.xmlContent)
        return convertedData
    
    
    def testRenderFile(self):
        self.title
        file = "testFile.odt"
        mockFile = MockFile()
        mockRep = MockIceRepository({file:mockFile})
        
        iceRender = IceRender(mockRep)
        renderMethods = {".odt": self.renderMethod}
        iceRender.setRenderMethods(renderMethods)
        iceRender.setIgnorePaths(["src", "templates"])
        
        output = StringIO()
        msg, renderedFiles = iceRender.render(file, forceConvert=False, \
                                                skipBooks=True, output=output)
        self.assertEqual(msg, "ok")
        self.assertEqual(renderedFiles, [file])
        self.assertEqual(output.getvalue(), "\nProcessing file: - '%s'\n" % file)
        cData = mockFile.property.ConvertedData
        self.assertEqual(cData.errorMessage, "")
        self.assertEqual(cData.getMeta("toc"), "")
        self.assertEqual(cData.getMeta("title"), self.title)
        self.assertEqual(cData.renditionNames, [".xhtml.body"])
        self.assertEqual(cData.getRendition(".xhtml.body"), self.xmlContent)
    
    
    def testRenderPath(self):
        self.title
        path = "testPath"
        files = ["testPath/one.odt", "testPath/src/two.odt", "testPath/three.odt", "four.odt", "testPath/five.txt"]
        mockFile = MockFile()
        #print mockFile.property.convertedData
        self.assertTrue(mockFile.property.convertedData==None)
        mockFile.isfile = False
        mockFile.walkerFiles = files
        # Note: the defaultMockFile will be used for all other files
        mockRep = MockIceRepository({path:mockFile})
        
        iceRender = IceRender(mockRep)
        renderMethods = {".odt": self.renderMethod}
        iceRender.setRenderMethods(renderMethods)
        iceRender.setIgnorePaths(["src", "templates"])
        
        output = StringIO()
        msg, renderedFiles = iceRender.render(path, forceConvert=False, \
                                                skipBooks=True, output=output)
        #print output.getvalue()
        self.assertEqual(msg, "ok")
        expectedFiles = ["testPath/one.odt", "testPath/three.odt", "four.odt"]
        self.assertEqual(renderedFiles, expectedFiles)
        #self.assertEqual(output.getvalue(), "\nProcessing file: - '%s'\n" % file)
        cData = mockFile.property.convertedData
        self.assertTrue(cData==None)
        cData = mockRep.getItem("testPath/one.odt").convertedData
        self.assertEqual(cData.errorMessage, "")
        self.assertEqual(cData.getMeta("toc"), "")
        self.assertEqual(cData.getMeta("title"), self.title)
        self.assertEqual(cData.renditionNames, [".xhtml.body"])
        self.assertEqual(cData.getRendition(".xhtml.body"), self.xmlContent)
        # Note: The same MockFile object has been used for all files
        cData = mockRep.getItem("testPath/src/two.odt").convertedData



########## MOCK CLASSES ##########
class MockIceRepository(object):
    def __init__(self, files={}):
        self.files = files      # dictionary of MockFiles keyed by relPath (filename)
        self.defaultMockFile = MockFile()
    
    def getAbsPath(self, relPath):
        return self.files.get(relPath, self.defaultMockFile).absPath
    
    def isfile(self, relPath):
        return self.files.get(relPath, self.defaultMockFile).isfile
    
    def walker(self, relPath, fileExts):
        return self.files.get(relPath, self.defaultMockFile).walkerFiles
    
    def add(self, relPath):
        pass
    
    def isHidden(self, relPath):
        return self.files.get(relPath, self.defaultMockFile).isHidden
    
    def isMyChangesFile(self, relPath):
        return self.files.get(relPath, self.defaultMockFile).isMyChangesFile

    def getProperty(self, relPath):
        return self.files.get(relPath, self.defaultMockFile).property

    @property
    def indexer(self):
        return self
    
    @property
    def metaIndexer(self):
        return self
        #metaIndexer.indexContent(file, prop.guid, {"path":file})
    def indexContent(self, *args, **kwargs):
        pass


class MockProperty(object):
    # needsUpdating
    # convertFlag
    # hasProperties                 # for indexing (if False no indexing is done!)
    # hasHtml                       # for indexing
    # guid                          # for indexing
    # close()
    # getMeta("documentType")       # for postRenderMethod
    # getMeta("title")              # for indexing
    # getRendition(".xhtml.body")   # for indexing
    # setConvertedData(convertedData)
    # flush()
    # 
    def __init__(self):
        self.convertedData = None
        self.needsUpdating = True
        self.convertFlag = True
        self.hasProperties = False
        self.hasHtml = False
        self.renditions = {}
        self.metas = {}
    
    def close(self):
        pass
    def flush(self):
        pass
    
    def getMeta(self, name):
        return self.metas.get(name, None)
    
    def getRendition(self, name):
        return self.renditions.get(name, None)
    
    def setConvertedData(self, convertedData):
        self.convertedData = convertedData


class MockFile(object):
    def __init__(self, property=None):
        self.absPath = "/absPath/test.txt"
        self.isfile = True
        self.isHidden = False
        self.isMyChangesFile = False
        self.walkerFiles = []
        if property is None:
            property = MockProperty()
        self.item = property




if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






