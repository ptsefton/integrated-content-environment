#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

from ice_common import IceCommon
IceCommon.setup()

from cStringIO import StringIO

sys.path.append("xhtml-export/convertionTests")
sys.path.append("../xhtml-export/convertionTests")


nsList = [
    ("utfx", "http://utfx.org/test-definition"), \
    ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"), \
    ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
    ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"), \
    ("table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"), \
    ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"), \
    ("fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"), \
    ("xlink", "http://www.w3.org/1999/xlink"), \
    ("dc", "http://purl.org/dc/elements/1.1/"), \
    ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"), \
    ("number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"), \
    ("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"), \
    ("chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"), \
    ("dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"), \
    ("math", "http://www.w3.org/1998/Math/MathML"), \
    ("form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0"), \
    ("script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0"), \
    ("ooo", "http://openoffice.org/2004/office"), \
    ("ooow", "http://openoffice.org/2004/writer"), \
    ("oooc", "http://openoffice.org/2004/calc"), \
    ("dom", "http://www.w3.org/2001/xml-events"), \
    ("xforms", "http://www.w3.org/2002/xforms"), \
    ("xsd", "http://www.w3.org/2001/XMLSchema"), \
    ("xsi", "http://www.w3.org/2001/XMLSchema-instance") ]



def main():
    testName = "P Styles"
    testName = "P"
    items = processFiles(testName=testName)

    print "Running %s test(s)\n" % len(items)
    for item in items:
        #processTest(item[3], item[0], item[1], item[2])
        domProcessTest(item[3], item[1], item[2])

def processTest(name, xsltSrc, xmlSrc, expectedXml):
    print "--- Test: '%s' ---" % name
    xslt = xslt_util.xslt(xsltSrc)
    
    r = "<root"
    for ns in nsList:
        r += "  xmlns:" + ns[0] + '="' + ns[1] + '"\n'
    r += ">\n"
    r += xmlSrc + "\n</root>"
    xml = IceCommon.Xml(r, nsList)
    newXml = xml.applyXslt(xslt)
    xslt.close()
    xml.close()
    expected = expectedXml.replace("utfx:expected", "body").replace(' validate="no"', "")
    html = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta content="text/html; charset=UTF-8" http-equiv="Content-Type"></meta>
  <title> Untitled </title>
  <style type="text/css" xml:space="preserve">table {border-spacing: 0;empty-cells: show;} </style>
</head>
<body>
</body>
</html>"""    
    xml = IceCommon.Xml(expected, nsList)
    import diff_util
    same = diff_util.sameXml(newXml.getNode("//body"), xml.getNode("//body"), False)
    print "Same=", same
    if same is False:
        for node in newXml.getNode("//body").getChildren():
            if node.getType()!="text":
                print node
        print 
        for node in xml.getNode("//body").getChildren():
            if node.getType()!="text":
                print node

    newXml.close()
    xml.close()
    print "--- Done ---\n"


def domProcessTest(name, xmlSrc, expectedXml):
    import ooo2xhtml
    
    print "--- Test: '%s' ---" % name
    o = ooo2xhtml.Ooo2xhtml(iceContext)
    r = "<root"
    for ns in nsList:
        r += "  xmlns:" + ns[0] + '="' + ns[1] + '"\n'
    r += ">\n"
    r += xmlSrc + "\n</root>"
    resultXmlStr = o.convert(r)
    print resultXmlStr
    print
    
    
def processFiles(testName):
    items = []
    files = getTestFiles()
    for file in files:
        #print "file = ", file
        xml = IceCommon.Xml(file, [("utfx", "http://utfx.org/test-definition")])
        nodes = xml.getNodes("//utfx:name")
        for node in nodes:
            name = node.getContent()
            if name.startswith(testName):
                #utfx:stylesheet src="ooo2xhtml.xsl"
                xsltSrc = xml.getNode("*/utfx:stylesheet").getAttribute("src")
                pNode = node.getParent()
                source = pNode.getNode("*/*[local-name()='source']")
                expected = pNode.getNode("*/*[local-name()='expected']")
                n = xml.createElement("office:body")
                n.addChildren(source.getChildren())
                source = str(n)
                n.delete()
                expected = str(expected)
                items.append((xsltSrc, source, expected, name))
        xml.close()
    return items


def getTestFiles():
    testFiles = []
    for root, dirs, files in os.walk("test"):
        while len(dirs): dirs.pop()
        testFiles = [os.path.join(root, file) for file in files if file.endswith("_test.xml")]
    return testFiles
        



def transform(xml):
    xslt = xslt_util.xslt("ooo2xhtml.xsl")
    newXml = xml.applyXslt(xslt)
    return newXml

    
main()






