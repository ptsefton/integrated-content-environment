import os
import sys
import re
from cStringIO import StringIO

import ooo2xhtml
from convertionTests import *

ns = [("utfx", "http://utfx.org/test-definition"),
    ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"),
    ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"),
    ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"),
    ("table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"),
    ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"),
    ("fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"),
    ("xlink", "http://www.w3.org/1999/xlink" ),
    ("dc", "http://purl.org/dc/elements/1.1/"),
    ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"),
    ("number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"),
    ("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"),
    ("chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"),
    ("dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"),
    ("math", "http://www.w3.org/1998/Math/MathML"),
    ("form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0"),
    ("script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0"),
    ("ooo", "http://openoffice.org/2004/office"),
    ("ooow", "http://openoffice.org/2004/writer"),
    ("oooc", "http://openoffice.org/2004/calc" ),
    ("dom", "http://www.w3.org/2001/xml-events"),
    ("xforms", "http://www.w3.org/2002/xforms" ),
    ("xsd", "http://www.w3.org/2001/XMLSchema"),
    ("xsi", "http://www.w3.org/2001/XMLSchema-instance"),
            ]


sXml = """<?xml version="1.0"?>
<testData xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
    xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
    xmlns:math="http://www.w3.org/1998/Math/MathML"
    xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
    xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
    xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer"
    xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events"
    xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    office:version="1.0">
    <!-- xmlns="http://www.w3.org/1999/xhtml" -->
    
    <tests>
    </tests>
</testData>"""


print os.getcwd()
print testData


# links
# misc
# objects
# ole
# table
# style
utfxFile = "test/ooo2xhtml_style_test.xml"
outputFile = os.path.join(testData, "test_ooo2xhtml_temp.xml")

print "Converting '%s' to '%s'" % (utfxFile, outputFile)

xml = IceCommon.Xml(utfxFile, ns)
outputXml = IceCommon.Xml(sXml, ns)
oNode = outputXml.getNode("//tests")
testNodes = xml.getNodes("//utfx:test")
for testNode in testNodes:
    nameNode = testNode.getNode("*[local-name()='name']")
    name = nameNode.content
    sourceNodeI = testNode.getNode("*/*[local-name()='source']")
    expectedNodeI = testNode.getNode("*/*[local-name()='expected']")
    print "  Test name='%s'" % name
    #print sourceNode
    #print expectedNode
    testNode = outputXml.createElement("test", name=name)
    testNode.setAttribute("normalize-white-spaces", "true")
    oNode.addChild(testNode)
    oNode.addContent("\n")
    
    sourceNode = outputXml.createElement("source")
    docNode = outputXml.createElement("office:document-content")
    bodyNode = outputXml.createElement("office:body")
    textNode = outputXml.createElement("office:text")
    bodyNode.addChild(textNode)
    docNode.addChild(bodyNode)
    sourceNode.addChild(docNode)
    testNode.addContent("\n")
    testNode.addChild(sourceNode)
    textNode.addChild(sourceNodeI)
    sourceNodeI.replace(sourceNodeI.getChildren())
    
    testNode.addContent("\n")
    expectedNode = outputXml.createElement("expected", match="/html:html/html:body")
    bodyNode = outputXml.createElement("body")
    expectedNode.addChild(bodyNode)
    testNode.addChild(expectedNode)
    bodyNode.addChild(expectedNodeI)
    expectedNodeI.replace(expectedNodeI.getChildren())
    testNode.addContent("\n")

#print outputXml
outputXml.saveFile(outputFile)
print "Saved to '%s' ok. Done." % outputFile

xml.close()
outputXml.close()



