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

from odtConverter import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os
import sys
import re


sourceFilename = "/packages/ice-guide/study-modules/module02.htm"
testOdtFile = "testData/odt/test.odt"
testPdfFile = "testData/odt/temp.pdf"
testHtmlFile = "testData/odt/temp.html"
testHtmlImages = "testData/odt/temp_html_*"

testResizeOdtFile = "testData/resize/test.odt"
testLargeResizeOdtFile = "testData/largeResize/test.odt"
testTransResizeOdtFile = "testData/transResize/test.odt"
testAnimResizeOdtFile = "testData/animResize/test.odt"
testExcessImagesOdtFile = "testData/excessImages/test.odt"


import relative_linker
getRelativeLinkMethod = relative_linker.relativeLinker("http://localhost:8000/").getRelativeLink

sys.path.append("../utils")

from file_system import FileSystem
from system import system

fs = FileSystem(".")


class odtConverterTests(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    # Constructor
    #    __init__(getRelativeLinkMethod, oooConverterMethod, xslt="./ooo2xhtml.xsl")
    # Properties:
    #    
    # Methods:
    #    renderMethod(file, absFile, rep=None, oooConverterMethod=None) -> convertedData object
    #    renderPdfOnlyMethod(file, absFile, rep=None, oooConverterMethod=None) -> convertedData object
    
    def xtestBasic(self):
        output = StringIO()
        oooConverterMethod=mockOooConverter("testData/odt").convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod, output=output)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testOdtFile)
        #print "output='%s'" % output.getvalue()
        lines = output.getvalue().split("\n")
        #self.assertEqual(lines[0], "Transforming content using python")
        
        images = convertedData.imageNames
        images.sort()
        #print "images='%s'" % images
        self.assertEqual(images, \
            ['11167e99.png', '11167e99s57x57.jpg', '2fd541e5.gif', 'm236bb6e0.gif', \
            'm3b38cb36.gif', 'm43251e1f.gif', 'm7e526c9f.gif'])
        # convertedData.getImage(name)
        for name in images:
            self.assertTrue(len(convertedData.getImage(name))>0)
        
        renditionNames = convertedData.renditionNames
        renditionNames.sort()
        self.assertEqual(renditionNames, \
            ['.ALL.txt', '.pdf', '.xhtml.body'])
        # convertedData.getRendition(name)
        for name in renditionNames:
            self.assertTrue(len(convertedData.getRendition(name))>0)
        
        metaNames = convertedData.metaNames
        metaNames.sort()
        self.assertEqual(metaNames, \
            ['images', 'links', 'style.css', 'title'])
        # convertedData.metaNames
        for name in metaNames:
            self.assertTrue(len(convertedData.getMeta(name))>0)
        
        # Title
        unicodeDash = "\xe2\x80\x93"
        expectedTitle = "Module 2 - Word processing with OpenOffice.org (OOo) Writer"
        expectedTitle = expectedTitle.replace("-", unicodeDash)
        title = convertedData.getMeta("title")
        self.assertEqual(title, expectedTitle)
        
        self.assertEqual(len(convertedData.getMeta("style.css")), 3685)
        
        htmlBody = convertedData.getRendition(".xhtml.body")
        
        convertedData.close()
    
    
    def testResize(self):
        mockObject = mockOooConverter("testData/resize")
        mockObject.useOoo = False
        oooConverterMethod = mockObject.convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testResizeOdtFile)
        
        htmlBody = convertedData.getRendition(".xhtml.body")
        #print htmlBody
        
        xml = IceCommon.Xml(htmlBody)
        nodes = xml.getNodes("//img")
        try:
            for node in nodes:
                width = node.getAttribute("width")
                height = node.getAttribute("height")
                src = node.getAttribute("src")
                self.assertEqual(width, "321")
                self.assertEqual(height, "257")
                self.assertEqual(src, "module02_files/4c58561.gif")
        finally:
            xml.close()
        self.assertEqual(convertedData.imageNames, ["4c58561.gif"])
    
    
    def testLargeResize(self):
        mockObject = mockOooConverter("testData/largeResize")
        mockObject.useOoo = False
        oooConverterMethod = mockObject.convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testLargeResizeOdtFile)
        
        images = convertedData.imageNames
        images.sort()
        #print "images='%s'" % images
        self.assertEqual(images, \
            ['4c58561.gif', '4c58561s257x206.jpg', '4c58561s385x308.jpg'])
        metaImages = convertedData.getMeta("images")
        #print "metaImages='%s'" % metaImages
        self.assertEqual(metaImages, images)
        for name in images:
            self.assertTrue(len(convertedData.getImage(name))>0)
            imgData = convertedData.getImage(name)
            im = ice_image.iceImage(imgData)
            size = im.size
            m = re.search("(.*?)s(\d+)x(\d+)(\..*$)", name)
            if m is not None:
                peices = m.groups()
                requiredSize = (int(peices[1]), int(peices[2]))
                self.assertEqual(size, requiredSize)
        htmlBody = convertedData.getRendition(".xhtml.body")
        
        xml = IceCommon.Xml(htmlBody)
        nodes = xml.getNodes("//img")
        try:
            width = nodes[0].getAttribute("width")
            height = nodes[0].getAttribute("height")
            src = nodes[0].getAttribute("src")
            self.assertEqual(width, "321")
            self.assertEqual(height, "257")
            self.assertEqual(src, "module02_files/4c58561.gif")
            
            width = nodes[1].getAttribute("width")
            height = nodes[1].getAttribute("height")
            src = nodes[1].getAttribute("src")
            self.assertEqual(width, "257")
            self.assertEqual(height, "206")
            self.assertEqual(src, "module02_files/4c58561s257x206.jpg")
            
            width = nodes[2].getAttribute("width")
            height = nodes[2].getAttribute("height")
            src = nodes[2].getAttribute("src")
            self.assertEqual(width, "385")
            self.assertEqual(height, "308")
            self.assertEqual(src, "module02_files/4c58561s385x308.jpg")
            
        finally:
            xml.close()
    
    
    def testTransparency(self):
        #print "testTransparency"
        mockObject = mockOooConverter("testData/transResize")
        mockObject.useOoo = False
        oooConverterMethod = mockObject.convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testTransResizeOdtFile)
        
        images = convertedData.imageNames
        images.sort()
        self.assertEqual(images, ['22d8a8f7s79x60.jpg', 'a34efdd.gif', 'a34efdds186x259.jpg'])
        for name in images:
            imgData = convertedData.getImage(name)
            im = ice_image.iceImage(imgData)
            pxl=im.getPixel((5,5))
            if name.endswith(".gif"):
                transIndex = im.info['transparency']
                p = im.getpalette()
                colour = p[pxl:pxl+3]
                self.assertEqual(colour, [p[transIndex], p[transIndex+1], p[transIndex+2]])
            else:
                for a, b in zip(pxl, (255, 255, 255)):
                    self.assertTrue((a+5)>=b, "a='%s', b='%s'" % (a, b))
    
    
    def testAnimation(self):
        #print "testAnimation"
        mockObject = mockOooConverter("testData/animResize")
        mockObject.useOoo = False
        oooConverterMethod = mockObject.convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testAnimResizeOdtFile)
        
        images = convertedData.imageNames
        images.sort()
        self.assertEqual(images, \
            ['m32976176.gif']) #should be same as they went in
        htmlBody = convertedData.getRendition(".xhtml.body")
        
        xml = IceCommon.Xml(htmlBody)
        try:
            nodes = xml.getNodes("//img")
            for node in nodes:
                src = node.getAttribute("src")
                self.assertEqual(src, "module02_files/m32976176.gif")
            width = nodes[0].getAttribute("width")
            height = nodes[0].getAttribute("height")
            self.assertEqual(width, "109")
            self.assertEqual(height, "159")
            
            width = nodes[1].getAttribute("width")
            height = nodes[1].getAttribute("height")
            self.assertEqual(width, "104")
            self.assertEqual(height, "151")
            
            width = nodes[2].getAttribute("width")
            height = nodes[2].getAttribute("height")
            self.assertEqual(width, "87")
            self.assertEqual(height, "127")
        finally:
            xml.close()
    
    
    def testExcessImages(self):
        #print "testExcessImages"
        mockObject = mockOooConverter("testData/excessImages")
        mockObject.useOoo = False
        oooConverterMethod = mockObject.convertDocTo
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod)
        #absSrcFileName = os.path.abspath("." + sourceFilename)
        absSrcFileName = fs.absPath("." + sourceFilename)
        convertedData = converter.renderMethod(sourceFilename, testExcessImagesOdtFile)
        
        images = convertedData.imageNames
        images.sort()
        self.assertEqual(images, ['7a9d3b3s459x263.jpg', 'm6f1c4bbc.gif', 'm6f1c4bbcs276x319.jpg'])

    
def getOOoConverterMethod():
    import relative_linker
    from ooo_converter import oooConverter
    oooConverterMethod = oooConverter().convertDocTo
    return oooConverterMethod
    
    
#mockTestData = {sourceFilename:(testOdtFile, testPdfFile, testHtmlFile), }
class mockOooConverter:
    def __init__(self, basePath):
        basePath = basePath.replace("\\", "/")
        if not basePath.endswith("/"):
            basePath += "/"
        self.basePath = basePath
        self.testPdfFile = basePath + "temp.pdf"
        self.testHtmlFile = basePath + "temp.html"
        self.testOdtFile = basePath + "test.odt"
        self.useOoo = False
    
    
    def convertDocTo(self, sourceFilename, destFilename, reindex=False):
        #print "convertDocTo(%s, %s)" % (sourceFilename, destFilename)
        if self.useOoo:    # Use the oooConverter or use cached results of oooConverter
            import ooo_converter
            srcFilename = self.testOdtFile
            self.oooConverter = ooo_converter.oooConverter()
            self.oooConverter.convertDocumentTo(srcFilename, destFilename)
            # Cache the result
            #filename = os.path.split(destFilename)[1]
            filename = fs.split(destFilename)[1]
            #filename = os.path.abspath(self.basePath + filename)
            filename = fs.absPath(self.basePath + filename)
            self.oooConverter.convertDocumentTo(srcFilename, filename)
        else:
            #ext = os.path.splitext(destFilename)[1]
            ext = fs.splitExt(destFilename)[1]
            if ext==".pdf":
                self.__copy(self.testPdfFile, destFilename)
            elif ext==".html":
                self.__copy(self.testHtmlFile, destFilename)
                # also copy the associated images
                #toPath = os.path.split(destFilename)[0]
                toPath = fs.split(destFilename)[0]
                #files = [file for file in os.listdir(self.basePath) if file.startswith("temp_html_")]
                files = [file for file in fs.list(self.basePath) if file.startswith("temp_html_")]
                for file in files:
                    self.__copy(self.basePath + file, toPath + "/" + file)
            else:
                raise Exception("Unexcepted convert to document type!")
        result = True
        msg = ""
        return result, msg         
    
    
    def __copy(self, source, dest):
        #print "coping from %s to %s" % (source, dest)
        f = open(source, "rb")
        data = f.read()
        f.close()
        f = open(dest, "wb")
        f.write(data)
        f.close()


def copyToMethod(fromFilename, toFilename):
        if fromFilename!=sourceFilename:
            raise Exception("Unexcepted filename!")
        f = open(testOdtFile, "rb")
        data = f.read()
        f.close()
        f = open(toFilename, "wb")
        f.write(data)
        f.close()



if __name__ == "__main__":
    system.cls()
    print "---- Testing ----"
    print
    unittest.main()





