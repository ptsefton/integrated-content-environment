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

from plugins_odtAddLinkEndnotes import *
import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import sys

##sys.path.append("../utils")
##from file_system import *
##from xml_diff import *

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


linkDir = "testData/linkFootNote/"
linkFile = linkDir + "linkDocument.odt"
expectedLinkFile = linkDir + "expectedLinkDocument.odt"

class AddLinkEndnotesTests(XmlTestCase):
    def setUp(self):
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()
        pass
    
    
    def tearDown(self):
        #sys.stdout = self.stdout
        pass
    
    
    def testInit(self):
        addlinkEndnotes = AddLinkEndnotes()
        
    def testAddNewLinkEndnotes(self):
        self.__xmlString="""<root 
                    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                    xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' 
                    xmlns:xlink='http://www.w3.org/1999/xlink'
                    xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                    xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'
                    >%s</root>"""

        fs = FileSystem(".")
        addlinkEndnotes = AddLinkEndnotes()
        
        #call AddLinkFootnotes::addFootnotes function
        addlinkEndnotes.addEndnotes(linkFile)
                
        
        #Exctract link from the document (xml)
        tempFs = fs.unzipToTempDirectory(linkFile)
        xml = IceCommon.Xml(tempFs.absolutePath("content.xml"), nsList)
        nodes = xml.getNodes("//text:a")
        
        resultXML=""
        for node in nodes:            
            resultXML+=str(node)
            nextSibling = node.getNextSibling()
            while nextSibling != None:
                #If there is footnote for the link ignore
                if nextSibling.getName() == "note":           
                    resultXML+=str(node.getNextSibling())
                nextSibling = nextSibling.getNextSibling()
                    
        #resultXML=xml.xmlStringToElement(self.__xmlString % resultXML )
        
        #Expected result:
        expectedXML = """<text:a xlink:type="simple" xlink:href="http://www.google.com/">link</text:a>
                            <text:note text:id="1" text:note-class="footnote">
                                <text:note-citation>1</text:note-citation>
                                <text:note-body>
                                    <text:p text:style-name="Footnote">Link: http://www.google.com/</text:p>
                                </text:note-body>
                            </text:note>
                            <text:a xlink:type="simple" xlink:href="http://www.google.com/">link</text:a>
                            <text:note text:id="2" text:note-class="footnote">
                                <text:note-citation>2</text:note-citation>
                                <text:note-body>
                                    <text:p text:style-name="Footnote">Link: http://www.google.com/</text:p>
                                </text:note-body>
                            </text:note>
                            <text:a xlink:type="simple" xlink:href="http://www.usq.edu.au/" office:name="USQ link">link</text:a>
                            <text:note text:id="3" text:note-class="footnote">
                                <text:note-citation>3</text:note-citation>
                                    <text:note-body>
                                        <text:p text:style-name="Footnote">Link: http://www.usq.edu.au/</text:p>
                                    </text:note-body>
                            </text:note>"""
        expectedXML= expectedXML.replace("  ", "")
        expectedXML= expectedXML.replace("\n", "")
        #expectedXML=xml.xmlStringToElement(self.__xmlString % expectedXML )
        
        resultStr = str(resultXML).replace(":", "_")
        expectedStr = str(expectedXML).replace(":", "_")
            
        #self.assertEqual(resultStr, expectedStr)
            #print node
        xml.close()
        tempFs.delete()
        
        
        
        
        #compare with the expected result        
        
        pass
        
if __name__ == "__main__":
    system.cls()
    print "---- Testing ----"
    print
    unittest.main()        