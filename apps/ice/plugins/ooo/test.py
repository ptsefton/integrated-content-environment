#!/usr/bin/python

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

import os
import sys
import re
import types
from cStringIO import StringIO
#sysPath = sys.path
#sysPath.append("../../../ice")
#sysPath.append("../../../utils")
#sysPath.append("../../../ice-svn-rep")
#sysPath.append("../../../sitemap")
#sysPath.append("../../../ice-utils")
#sysPath.append("../../../ooo-utils")
#sysPath.append("../../../html")
#sysPath.append("../../../ice-template")
#sysPath.append("../../../index")
#from file_system import FileSystem
#from system import system


currentPluginPath = os.getcwd()
try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    sys.path.append("../..")
    from ice_common import IceCommon
    
#from ice_common import IceCommon
#IceCommon.setup(pluginsPath="../../ice/plugins")

import ooo2xhtml
from convertionTests import *

fs = IceCommon.FileSystem(".")

nsStr = \
""" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
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
"""

def test():
    xml = getTestData("a3.content.xml")
    print "---- XSLT Result ----"
    print xsltResult(xml)
    print 
    print "---- Python Result ----"
    print newResult(xml)
    print


def getListOfTestFiles():
    tFiles = []
    testDataFullPath = fs.join(fs.absolutePath(currentPluginPath), testData);
    
    for rootDir, dirs, files in os.walk(testDataFullPath):
        files = [file for file in files if os.path.splitext(file)[1]==".xml" and file.startswith("test_")]
        for file in files:
            tFiles.append(os.path.join(rootDir, file))
    return tFiles




def formatPart(xmlStr, match, format=True):
    xml = IceCommon.Xml(xmlStr, [("", "http://www.w3.org/1999/xhtml"), ("html", "http://www.w3.org/1999/xhtml")])
    matchContent = xml.getNode(match)
    s = str(matchContent)
    if format:
        pr = prettyPrint(s)
        pr = pr[pr.find("\n")+1:]
    else:
        pr = s
    xml.close()
    return pr


def testForDiff(name, resultStr, expectedStr, sout, display=True):
    displayChars = True
    if type(resultStr) is types.UnicodeType:
        resultStr = resultStr.encode("utf-8")
    if type(expectedStr) is types.UnicodeType:
        expectedStr = expectedStr.encode("utf-8")
    if resultStr==expectedStr:
        print "  Name = '%s'  --- OK ---" % name
        return True
    else:
        print "  Name = '%s'  --- Failed ---" % name
        sout.reset()
        s = sout.read()
        if display:
            if s is not None and s!="":
                print s
            rLines = resultStr.split("\n")
            eLines = expectedStr.split("\n")
            rLinesCount = len(rLines)
            eLinesCount = len(eLines)
            numberOfSameStartLines = 0
            numberOfSameEndLines = 0
            l = range(min(rLinesCount, eLinesCount))
            for x in l:
                if rLines[x] != eLines[x]:
                    break
                numberOfSameStartLines += 1
            for x in l:
                if rLines[rLinesCount-x-1] != eLines[eLinesCount-x-1]:
                    break
                numberOfSameEndLines += 1
            for x in range(numberOfSameStartLines):
                print "= ", eLines[x]
            print "----"
            for x in range(numberOfSameStartLines, eLinesCount-numberOfSameEndLines):
                if displayChars:
                    print "E ", repr(eLines[x])
                else:
                    print "E ", eLines[x]
                #e = eLines[x]
                #r = rLines[x]
                #for i in range(len(e)):
                #    if e[i] != r[i]:
                #        print "-- index %s --" % i
                #        print e[:i]
                #        break
            print "----"
            for x in range(numberOfSameStartLines, rLinesCount-numberOfSameEndLines):
                if displayChars:
                    print "R ", repr(rLines[x])
                else:
                    print "R ", rLines[x]
            #for x in range(numberOfSameStartLines, rLinesCount-numberOfSameEndLines):
            #        print rLines[x]
            print "----"
            for x in range(eLinesCount-numberOfSameEndLines, eLinesCount):
                print "= ", eLines[x]
            print
        return False


def testAll(display=10, testName=None):
    print
    testCount = 0
    failedCount = 0
    skipedCount = 0
    testFiles =  getListOfTestFiles()
    #print testFiles
    print testFiles;
    for testFile in testFiles:
        print "TestFile - '%s'" % testFile
        xml = IceCommon.Xml(testFile, [("x", "http://www.w3.org/1999/xhtml")])
        tests = xml.getNodes("/testData/tests/test")
        for test in tests:
            name = test.getAttribute("name")
            if testName!=None and not name.startswith(testName):
                continue
            skip = test.getAttribute("skip")
            format = test.getAttribute("normalize-white-spaces")
            format = format.lower()
            format = format=="true"
            if skip is not None and skip.lower()=="true":
                print "  Name = '%s' --- Skiped ---" % name
                skipedCount += 1
                testCount += 1
                continue
            testCount += 1
            source = test.getNode("source")
            expected = test.getNode("expected")
            match = expected.getAttribute("match")
            if match is None:
                match = "/"
            expected = test.getNode("expected/*")
            source = str(source)
            source = source.replace("<source>", "<source%s>" % nsStr)
            #print str(source)
            #print "  Name = '%s'  (match='%s')" % (name, match)
            sio = StringIO()
            stdout = sys.stdout
            sys.stdout = sio
            o = ooo2xhtml.Ooo2xhtml(IceCommon.IceContext)
            o.resetIDCount()
            o.process(source)
            #result = str(o)
            result = o.serialize()
            sys.stdout = stdout
            result = result[result.find("<html"):]

            result = formatPart(result, match, format)
            expected = formatPart(str(expected), "/*", format)
            
            r = testForDiff(name, result, expected, sio, display)
            if r==False:
                if display>0:
                    display -= 1
                failedCount += 1
                if False:
                    xsltR = xsltResult(source)
                    print xsltR
        xml.close()
    if failedCount==0 and skipedCount==0:
        print "Total: %s Tests and all passed OK (%s skipped)" % (testCount, skipedCount)
    else:
        print "Total: %s Tests, %s passed, %s failed, %s skipped" % (testCount, testCount-failedCount-skipedCount, failedCount, skipedCount)
    

display = 10
argv = sys.argv
name = None
if len(argv)>1:
    a = argv[1]
    try:
        display = int(a)
    except:
        name = a
IceCommon.system.cls()
testAll(display, name)

    






