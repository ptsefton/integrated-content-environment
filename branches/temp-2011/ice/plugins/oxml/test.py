#!/usr/bin/env python

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
try:
    if sys.platform=="cli":
        import clr
        lib2Paths = [p.rsplit("/", 1)[0] + "/lib2" for p in sys.path if p.endswith("/Lib")]
        sys.path.extend(lib2Paths)
except Exception, e:
    pass
import os
import time
import types
from cStringIO import StringIO

#from unittest import TestCase

from oxml2xhtml import Oxml2xhtml


currentPluginPath = os.getcwd()
sys.path.append("../../../utils")
from file_system import FileSystem
fs = FileSystem()
class Context(object):
    def __init__(self):
        self.fs = fs

testFile = "test*.docx"              # "test*.docx" for all test*.docx files
testData = "testData/"
testOutput = "testData/testOutput/"
testExpectedResults = "testData/expected/"


def getListOfTestFiles():
    tFiles = []
    testDataFullPath = fs.join(fs.absolutePath(currentPluginPath), testData);

    for rootDir, dirs, files in os.walk(testDataFullPath):
        files = [file for file in files if os.path.splitext(file)[1]==".xml" and file.startswith("test_")]
        for file in files:
            tFiles.append(os.path.join(rootDir, file))
    return tFiles

def getListOfTestFiles(path, testFiles=["test*.docx"]):
    tFiles = []
    for testFile in testFiles:
        if testFile.find("*")!=-1:
            s, e = testFile.split("*", 1)
            for f in os.listdir(path):
                if f.startswith(s) and f.endswith(e):
                    tFiles.append(f)
    return tFiles


def test(testFiles=None):
    print "-- OXML Testing --"
    failedList = []
    if testFiles is None:
        testFiles = [testFile]
    #   readFromZipFile(zipFile, filename)
    context = Context()
    fs = context.fs
    fs.delete(testOutput)
    o = None
    testFiles = getListOfTestFiles(testData, testFiles)
    allStartTime = time.time()
    tmpFs = fs
    #tmpFs = fs.clone("temp")
    for tFile in testFiles:
        startTime = time.time()
        print ("\nTesting '%s'" % tFile),
        #o = Oxml2xhtml(context)        # ??? causing DeprecationWarning under IP2.6? Why? Something to with the SAX parser?
        o = Oxml2xhtml()
        o.context = context
        if True:
            o.outputFile = testOutput + fs.splitExt(tFile)[0] + ".htm"
            expectedOutputFile = testExpectedResults + fs.splitExt(tFile)[0] + ".htm"
            o.processFile(os.path.abspath(testData + tFile))

            o.getEmbeddedObjectImages(tmpFs)
            o.writeImagesTo()
            o.writeHtmlTo()
            finishTime = time.time()
            et = (finishTime - startTime) * 1000
            output = fs.read(o.outputFile)
            if True:    #
                expected = fs.read(expectedOutputFile)
                if expected is None:
                    failedList.append((tFile, "No expected output file found"))
                elif output is None:
                    failedList.append((tFile, "No output generated"))
                elif output!=expected:
                    msg = "output(%s)!=expected(%s)" % (len(output), len(expected))
                    failedList.append((tFile, msg))
            else:       # write out to testExpectedResults
                fs.write(expectedOutputFile, output)
            print "- done %s in %smS (incWriting=%smS)" % (tFile, o.processTime, int(et))
    print "-- completed all is %smS" % int((time.time()-allStartTime)*1000)
    if False and o is not None:
        try:
            html = o.html.formatted()
        except:
            html = "--no html--"
        o = None
        print html
    o = None
    context = None
    fs = None
    print "==  Results  =="
    if failedList==[]:
        print "All OK - Tested %s files" % (len(testFiles))
    else:
        print "Tested %s files - %s failed" % (len(testFiles), len(failedList))
        for failedFile, msg in failedList:
            print "'%s' - %s" % (failedFile, msg)






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
    

def main():
    #IceCommon.system.cls()
    display = 10            # display the first 10 diffs
    argv = sys.argv
    name = None
    if len(argv)>1:
        a = argv[1]
        try:
            display = int(a)
        except:
            name = a
    testAll(display, name)


if __name__=="__main__":
    #print "oxml2xhtml.MSWord.ErrorMessage='%s'" % (oxml2xhtml.MSWord.ErrorMessage)
    testFiles=["test*.docx"]
    test(testFiles)
    #runUnitTests(locals())
    time.sleep(.2)
    print "all done"
    sys.exit(0)

    






