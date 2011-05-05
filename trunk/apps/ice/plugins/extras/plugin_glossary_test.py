#!/usr/bin/env python
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon

from plugin_glossary import *


class MockIceItem(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.meta = dict()
    
    @property
    def packageRootItem(self):
        return self
    
    def getMeta(self, name):
        fp = open(self.filename + "." + name)
        data = fp.read()
        fp.close()
        return data
    
    def setMeta(self, name, value):
        pass
    
    def flush(self):
        pass
    
    def close(self):
        pass
    
    def getIceItem(self, relPath):
        return MockIceItem(relPath)
    
    @property
    def relPath(self):
        return self.filename
    
class MockConvertedData(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.__renditions = dict()
    
    def getRendition(self, name):
        if self.__renditions.has_key(name):
            return self.__renditions.get(name)
        fp = open(self.filename + name)
        data = fp.read()
        fp.close()
        return data
    
    def addRenditionData(self, name, data):
        self.__renditions[name] = data
    
    def addMeta(self, name, data):
        pass

class GlossaryTest(IceCommon.TestCase):
    
    def setUp(self):
        self.iceContext = IceCommon.IceContext
        self.stdout = sys.stdout
        self.item = MockIceItem("plugins/extras/testData/glossary")
        self.glossary = Glossary(self.iceContext, self.item)
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testLoadTerms(self):
        self.assertEqual(3, len(self.glossary.terms))
        self.assertTrue(self.glossary.terms.has_key("url"))
    
    def testExtractTerms(self):
        convertedData = MockConvertedData("plugins/extras/testData/glossary")
        terms = self.glossary.extractTerms(self.item, convertedData)
        self.assertEqual(3, len(terms))
    
    def testAddTooltips(self):
        convertedData = MockConvertedData("plugins/extras/testData/document")
        self.glossary.addTooltips(convertedData)
        actual = convertedData.getRendition(".xhtml.body")
        fp = open("plugins/extras/testData/document.tooltips")
        expected = fp.read()
        fp.close()
        self.assertEqual(actual, expected)
    
    def __dump(self, terms):
        from cPickle import dump
        print terms
        fp = open("plugins/extras/testData/glossary.glossary-terms", "w")
        dump(terms, fp)
        fp.close()

if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






