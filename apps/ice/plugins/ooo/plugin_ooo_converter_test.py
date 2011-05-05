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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append("../../ice")
    #os.chdir("..")
    from ice_common import IceCommon
# XmlTestCase        # self.assertSameXml


from plugin_ooo_converter import *



nsList = [ \
            ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"), \
            ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"), \
            ("xlink", "http://www.w3.org/1999/xlink"), \
            ("dc", "http://purl.org/dc/elements/1.1/"), \
            ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"), \
            ("ooo", "http://openoffice.org/2004/office"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"), \
            ("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"), \
         ]
introODT = "testData/introODT.odt"
htmlOutputTestFile = "temp/testTemp.htm"
testResult = "testData/testResult.odt"
sample_mathtype = "testData/sample_mathtype.odt"
noMathtype = "testData/noMathtype.odt"
sample_mathtypeAndNoMathType = "testData/sample_mathtypeAndNoMathType.odt"
linkfile = "testData/link.odt"



class OOoConverterTests(IceCommon.TestCase):
    def setUp(self):
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()
        pass
    
    
    def tearDown(self):
        #sys.stdout = self.stdout
        pass
    
    
    def testInit(self):
        converter = oooConverter()
    
    
    def xtestConvertDocumentTo(self):
        #def convertDocumentTo(self, absFilePath, toAbsFilePath=None, toExt=None):
        fs = FileSystem(".")
        converter = oooConverter()
        
        fs.delete(htmlOutputTestFile)
        tf, data = converter.convertDocumentTo(introODT, htmlOutputTestFile)
        self.assertTrue(tf)
        self.assertEqual(data, None)

    
    def testBuildBook(self):
        fs = FileSystem(".")
#        self.__tempDir = fs.createTempDirectory()
        testData = "testData/"
        baseBookfile = testData + "template_testing_Default.odt"    
        #mathType = testData + "sample_mathtype.odt"
        #mathType = testData + "sample_mathtypeAndNoMathType.odt"
        mathType = testData + "one.odt"
        #mathTypehtm = testData + "sample_mathtype.htm"
        mathTypehtm = testData + "one.htm"
        withBookMark = testData + "two.odt"
        third = testData + "three.odt"
        #fromBookFile = sample_mathtype
        fromBookFile = baseBookfile
        toBookFile = "testData/testBuildBookResult.odt"
        fs.delete(toBookFile)
        self.assertFalse(fs.isFile(toBookFile))
#        tmpDir = fs.createTempDirectory()
#        absToFile = tmpDir.absolutePath(baseBookfile)
#        absFromFile = fs.absPath(baseBookfile)
        
        #Add temporary paragraph to document
#        ext = fs.splitExt(mathType)
#        tempFileName = self.__tempDir.absolutePath("temp1%s" % (ext[1]))
#        fs.copy(mathType, tempFileName)
#        newDoc = tempFileName
#        
#        try:
#            tempFs = fs.unzipToTempDirectory(newDoc)
#            xml = IceCommon.Xml(tempFs.absolutePath("content.xml"), nsList)
#            node = xml.getNode("//office:text")
#            
#            #newNodeStr= """<text:p text:style-name="p"></text:p>"""        
#            newNode = xml.createElement("text:p")
#            newNode.setAttribute("text:style-name", "p")     
#            newNode.setContent("T")
#            node.addChild(newNode)
#            
#            xml.saveFile()
#            xml.close()
#            tempFs.zip(fs.absolutePath(newDoc))
#        
#            tempFs.delete()           
#            mathType = newDoc
#        except:
#            raise  "Invalid Open Office Document"      
        
        docs = []
        #docs = [ (linkfile, ""), (noMathtype, ""), (noMathtype, "") ]
        doc1 = [fs.absPath(mathType), mathTypehtm, {"InsertPageBreak":True, "Page":"Odd"}]
        docs.append(doc1)
        #doc2 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc2 = [fs.absPath(withBookMark), mathTypehtm, {"InsertPageBreak":True, "Page":"Odd"}]
        docs.append(doc2)
        #doc3 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc3 = [fs.absPath(third), mathTypehtm, {"InsertPageBreak":True, "Page":"Odd"}]
        docs.append(doc3)
        #doc4 = (os.path.abspath(m1file), "", {"InsertPageBreak":False})
        doc4 = [fs.absPath(third), mathTypehtm, {"InsertPageBreak":True, "Page":"Even"}]
        docs.append(doc4)
        
        converter = oooConverter()
        result=converter.buildBook(fromBookFile, docs, toBookFile, baseUrl="http://localhost:8000")
        self.assertTrue(fs.isFile(toBookFile))
        
#        print "TOBOOKFILE: ", toBookFile
        data = fs.readFile(toBookFile)
        self.assertTrue(len(data) > 100)
#        tmpDir.copy(baseBookfile, absFromFile)
#        self.__tempDir.delete()
#        tmpDir.delete()
        
    
    
    def xtestBuildBookPageStyle(self):
        testData = "bookTestData/"
        baseBookfile = testData + "template_testing_Default.odt"
        ch1file = testData + "chp1_with_headers.odt"
        ch2file = testData + "chp2_with_header.doc"
        ch3file = testData + "chp3_with_header.doc"
        tempOutput = testData + "tempBookOut1.odt"
        fs = FileSystem(".")
        fromBookFile = baseBookfile
        toBookFile = tempOutput
        
        docs = []
        #docs = [ (linkfile, ""), (noMathtype, ""), (noMathtype, "") ]
        doc1 = (fs.absPath(ch1file), "", {"InsertPageBreak":True, "Page":"Odd"})
        docs.append(doc1)
        #doc2 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc2 = (fs.absPath(ch2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        docs.append(doc2)
        #doc3 = (os.path.abspath(m2file), "", {"InsertPageBreak":True, "Page":"Odd"})
        doc3 = (fs.absPath(ch3file), "", {"InsertPageBreak":True, "Page":"Odd"})
        docs.append(doc3)
        #doc4 = (os.path.abspath(m1file), "", {"InsertPageBreak":False})
        doc4 = (fs.absPath(ch2file), "", {"InsertPageBreak":False})
        docs.append(doc4)
        
        converter = oooConverter()
        converter.buildBook(fromBookFile, docs, toBookFile, baseUrl="http://localhost:8000", title=None)
        self.assertTrue(fs.isFile(toBookFile))
        
        data = fs.readFile(toBookFile)
        self.assertTrue(len(data) > 100)        
        
    
    def xtestObjectReplacementHack(self):
        buildTestFile = True
        fs = FileSystem(".")
        converter = oooConverter()
        fromBookFile = noMathtype
        toBookFile = "testData/testObjectReplacementHackResult.odt"
        fs.delete(toBookFile)
        self.assertFalse(fs.isFile(toBookFile))
        
        docs = [ (sample_mathtype, ""), (noMathtype, ""), \
                (sample_mathtypeAndNoMathType, ""), (linkfile, "") ]
        
        try:
            # build test infomation
            converter.buildBook(fromBookFile, docs, toBookFile, baseUrl="http://localhost:8000", title=None)
            
            self.assertTrue(fs.isFile(toBookFile))
            
            xmlString="""<root 
                        xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' 
                        xmlns:xlink='http://www.w3.org/1999/xlink'
                        xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                        xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'>"""
            
            # now assert the the toBookFile contains all the orginal enbedded objects.
            tempFs = fs.unzipToTempDirectory(toBookFile)
            xml = IceCommon.Xml(tempFs.absolutePath("content.xml"), nsList)
            nodes = xml.getNodes("//draw:frame")
                
            if buildTestFile == True:    
                print "Building expectedxmlString.xml"   
                for node in nodes:
                    xmlString+=str(node)
                
                xmlString+="</root>"
                fs.writeFile("testData/expectedxmlString.xml", xmlString)
            else:           
                #Compare current Book xml with the expected xml result
                xmlExpected = IceCommon.Xml("testData/expectedxmlString.xml", nsList)
                expectedNodes =xmlExpected.getNodes("//draw:frame")
                
                for node, expectedNode in zip(nodes, expectedNodes):
                    #Hack: for now just remove namespaces for testing
                    nodeStr = str(node).replace(":", "_")
                    expectedNodeStr = str(expectedNode).replace(":", "_")
                    self.assertSameXml(nodeStr, expectedNodeStr, \
                                "Nodes are not the same!")
                
                xmlExpected.close()   
        finally:
            xml.close()
            tempFs.delete()
        
    
    def xtestImageObject(self):
        fs = FileSystem(".");
        fromBookFile = noMathtype
        
        tempFs = fs.unzipToTempDirectory(fromBookFile)
        xml = IceCommon.Xml(tempFs.absolutePath("content.xml"), nsList)
        nodes = xml.getNodes("//draw:frame")
        #nodes = xml.getNodes("//draw:frame[draw:object-ole]")        
        
        for node in nodes:
            objectOleNode = node.getNode("*[local-name()='object-ole']")        
            self.assertFalse(objectOleNode==None, "Only Image File not Object")
        
        xml.close()   


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())




