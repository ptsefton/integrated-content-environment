
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

""" """

import sys
import os
import re

sys.path.append(os.getcwd())
if os.getcwd().endswith("/ooo2xhtml"):
    os.chdir("..")

##if sys.path.count("../ice")==0: sys.path.append("../ice")
##from ixe_globals import *
#from ice_common import IceCommon
#IceCommon.setup()

import ooo2xhtml

oOfficeNSList = [ \
            ("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"), \
            ("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0"), \
            ("xlink", "http://www.w3.org/1999/xlink"), \
            ("dc", "http://purl.org/dc/elements/1.1/"), \
            ("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"), \
            ("ooo", "http://openoffice.org/2004/office"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"), \
            ("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"), \
            ("table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"), \
            ("fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"), \
            ("number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"), \
            ("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"), \
            ("chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"), \
            ("dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"), \
            ("math", "http://www.w3.org/1998/Math/MathML"), \
            ("form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0"), \
            ("script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0"), \
            ("ooow", "http://openoffice.org/2004/writer"), \
            ("oooc", "http://openoffice.org/2004/calc"), \
            ("dom", "http://www.w3.org/2001/xml-events"), \
            ("xforms", "http://www.w3.org/2002/xforms"), \
            ("xsd", "http://www.w3.org/2001/XMLSchema"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
            # ("", "http://www.w3.org/1999/xhtml")
         ]

#xslt1 = "office2html.xsl"
#xslt1 = xslt_util.xslt(xslt1)
#xslt="./ooo2xhtml.xsl"
#xslt = xslt_util.xslt(xslt)
testData = "testData/"
#testData = "testData/"
testFiles = []
contents = []
testInfos = []


# Get a list of all *.odt files in the test directory
def getListOfTestFiles():
    tFiles = []
    for rootDir, dirs, files in os.walk(testData):
        files = [file for file in files if os.path.splitext(file)[1]==".odt"]
        for file in files:
            tFiles.append(os.path.join(rootDir, file))
    return tFiles


# Get the content.xml data from the zip file (.odt file)
def getContentsFrom(files):
    contents = []
    for file in files:
        content = getContentXmlFromFile(file)
        if content is None and file.endswith(".xml"):
            f = open(file, "rb")
            content = f.read()
            f.close()
        contents.append(content)
    return contents

def getContentXmlFromFile(file):
    return fs.readFromZipFile(file, "content.xml")


# convert the given content.xml using the xslt stylesheet
def xsltTransform(content):
    contentXml = IceCommon.Xml(content)
    newXml = contentXml.applyXslt(xslt)
    contentXml.close()
    xmlStr = str(newXml)
    newXml.close()
    return xmlStr

def pythonTransform(content):
    # not yet complete!!!!!!!
    o = ooo2xhtml.Ooo2xhtml(iceContext)
    o.process(content)
    result = o.serialize()
    return result


# apply the xslt stylesheet and optionaly save the results
def applyXslt(fileContents):
    """ fileContents is a list of tuples (sourceFileName, contentXml)
        returning a list of results
    """
    results = []
    for file, content in fileContents:
        print "Applying stylesheet to %s" % os.path.split(file)[1]
        st = time.time()
        xml = xsltTransform(content)
        results.append(xml)
        et = time.time() - st
        print "  Done in %s mS" % int(et * 1000)
        if False:
            fn = os.path.splitext(file)[0] + ".xhtml"
            f = open(fn, "wb")
            f.write(xml)
            f.close()
            fn = os.path.splitext(file)[0] + ".content.xml"
            f = open(fn, "wb")
            f.write(content)
            f.close()
    return results

def compare(fileContents):
    """ fileContents is a list of tuples (sourceFileName, contentXml)
        returning a list of timing results
    """
    results = []
    totalXsltTime = 0
    totalPythonTime = 0
    for file, content in fileContents:
        filename = os.path.split(file)[1]
        # XSLT
        st = time.time()
        xsltResult = xsltTransform(content)
        et = time.time() - st
        xsltTime = "XSLT processed %s in %s mS" % (filename, int(et * 1000))
        totalXsltTime += int(et * 1000)
        print xsltTime
        # Python
        st = time.time()
        pythonResult = pythonTransform(content)
        et = time.time() - st
        pythonTime = "Python processed %s in %s mS" % (filename, int(et * 1000))
        totalPythonTime += int(et * 1000)
        print pythonTime
        compareResults(xsltResult, pythonResult)
        print
        
        results.append( (xsltTime, pythonTime) )
    print "Total Xslt time = %s, total python time = %s" % (totalXsltTime/1000.0, totalPythonTime/1000.0)
    
    return results



def compareResults(result1, result2):
    ns = [("x", "http://www.w3.org/1999/xhtml")]
    xml1 = IceCommon.Xml(result1, ns)
    xml2 = IceCommon.Xml(result2, ns)
    
    node = xml1.getNode("//x:title")
    r1 = str(node)
    node = xml2.getNode("//x:title")
    r2 = str(node)
    print "Same Title", r1==r2
    if r1!=r2:
        print r1, r2
    
    node = xml1.getNode("//x:body")
    r1 = str(node)
    node = xml2.getNode("//x:body")
    r2 = str(node)
    print "Same body", r1==r2, len(r1)
    if len(r1)<1000:
        print r1
        print "----"
        print r2
    
    xml1.close()
    xml2.close()



if __name__=="__main__":
    print "\n--- Convertion Tests ---"
    testFiles = getListOfTestFiles()
    #print testFiles
    testFiles = ["ooo2xhtml/content.xml"]
    contents = getContentsFrom(testFiles)
    #print type(contents), len(contents)
    #testInfos = zip(testFiles, contents, applyXslt(zip(testFiles, contents)))
    compare(zip(testFiles, contents))
    


#######################################################################
from xml.dom.minidom import parseString


def getTestData(name="a1.content.xml"):
    file = testData + name
    f = open(file, "rb")
    xmlStr = f.read()
    f.close()
    return xmlStr

def xsltResult(xmlStr=None):
    if xmlStr is None:
        xmlStr = getTestData()
    newXmlStr = xsltConvert(xmlStr)
    return prettyPrint(newXmlStr)
    
def newResult(xmlStr=None):
    if xmlStr is None:
        xmlStr = getTestData()
    reload(ooo2xhtml)
    o = ooo2xhtml.Ooo2xhtml(iceContext)
    o.process(xmlStr)
    newXmlStr = str(o)
    return prettyPrint(newXmlStr)

def prettyPrint(xmlStr=None):
    if xmlStr is None:
        xmlStr = test()
    xmlStr = re.sub("\s+", " ", xmlStr)
    xmlStr = xmlStr.replace("> <", "><")
    dom = parseString(xmlStr)
    dom.normalize()
    # dom.toxml()
    try:
        r = dom.toprettyxml()
    except:
        print xmlStr
        print dom.toxml()
        raise
    dom.unlink()
    return r



