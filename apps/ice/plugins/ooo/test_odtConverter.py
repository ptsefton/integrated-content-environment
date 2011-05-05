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

from odtConverter import *


sourceFilename = "/packages/ice-guide/study-modules/module02.htm"
testOdtFile = "testData/odt/test.odt"
testPdfFile = "testData/odt/temp.pdf"
testHtmlFile = "testData/odt/temp.html"

import relative_linker
getRelativeLinkMethod = relative_linker.relativeLinker("http://localhost:8000/").getRelativeLink


def getOOoConverterMethod():
    import relative_linker
    from ooo_converter import oooConverter
    oooConverterMethod = oooConverter().convertDocTo
    return oooConverterMethod
    #xsltPath = "../xhtml-export/ooo2xhtml.xsl"
    #if not os.path.isfile(xslPath):
    #    xsltPath = "./ooo2xhtml.xsl"
    #xslt = xslt_util.xslt(xslPath)

    #getRelativeLinkMethod = relative_linker.relativeLinker("http://localhost:8000")

    #renderMethod = odtConverter(getRelativeLinkMethod, ooo.ConverterMethod, xslt).renderMethod
    #return renderMethod

if __name__=="__main__":
    print "Starting.."
    tempOdtFile = "temp/temp.odt"
    tempPdfFile = "temp/temp.pdf"
    tempHtmFile = "temp/temp.htm"
    oooConverterMethod = getOOoConverterMethod()
    #tmpDir = file_util.tempDir()
    #file_util.removeDir("temp")
    try:
        os.mkdir("temp")
    except:
        print "unable to make the temp directory"
    try:
        file_util.copyFile(testOdtFile, tempOdtFile)
    except:
        print "unable to copy temp.odt file"
    print os.path.abspath(tempPdfFile)
    r, msg = oooConverterMethod(tempOdtFile, os.path.abspath(tempPdfFile))
    print "r=%s, msg=%s" % (r, msg)
    print
    print os.path.abspath(tempHtmFile)
    r, msg = oooConverterMethod(tempOdtFile, os.path.abspath(tempHtmFile))
    print "r=%s, msg=%s" % (r, msg)
    print "OK"
    

class mockOooConverter:
    def __init__(self):
        pass
        
    def convertDocTo(self, sourceFilename, destFilename):
        #print "convertDocTo(%s, %s)" % (sourceFilename, destFilename)
        if False:    # Use the oooConverter or use cached results of oooConverter
            #import ooo_converter
            self.oooConverter = ooo_converter.oooConverter()
            self.oooConverter.convertDocumentTo(sourceFilename, destFilename)
            # Cache the result
            filename = os.path.split(destFilename)[1]
            filename = os.path.abspath("testData/odt/" + filename)
            self.oooConverter.convertDocumentTo(sourceFilename, filename)
        else:
            #if sourceFilename!=testOdtFile:
            #    raise Exception("Unexcepted filename!")
            toFilename = os.path.split(destFilename)[1]
            if toFilename=="temp.pdf":
                self.__copy(testPdfFile, destFilename)
            elif toFilename=="temp.html":
                self.__copy(testHtmlFile, destFilename)
                # also copy the associated images
                toPath = os.path.split(destFilename)[0]
                files = [file for file in os.listdir("testData/odt") if file.startswith("temp_html_")]
                for file in files:
                    self.__copy("testData/odt/" + file, toPath + "/" + file)
            else:
                raise Exception("Unexcepted convert to document type!")
        
        
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




def xtest_setup():
    if False:
        global converter
        converter = odtConverter(getRelativeLinkMethod, oooConverterMethod=mockOooConverter().convertDocTo)
        converter.setup(copyToMethod, sourceFilename)
        converter.convertToHtml()
        converter.convertToPdf()
        converter.close()
        convertedData = converter.convertedData
    else:
        convertedData = odtConverter(getRelativeLinkMethod).renderMethod(sourceFilename, os.path.abspath(testOdtFile), \
                    oooConverterMethod=mockOooConverter().convertDocTo)
    

    #print str(convertedData)
    metaNames = convertedData.metaNames
    imageNames = convertedData.imageNames
    renditionNames = convertedData.renditionNames
    metaNames.sort()
    imageNames.sort()
    renditionNames.sort()
    expectedMetaNames = ['images', 'links', 'style.css', 'title']
    expectedImageNames = ['11167e99.png', '2fd541e5.gif', 'm236bb6e0.gif', 'm3b38cb36.gif', 'm43251e1f.gif', 'm7e526c9f.gif']
    expectedRenditionNames = ['.ALL.txt', '.pdf', '.xhtml.body']
    assert metaNames == expectedMetaNames
    assert imageNames == expectedImageNames
    assert renditionNames == expectedRenditionNames
    
    for name in imageNames:
        assert len(convertedData.getImage(name))>0
    images = convertedData.getMeta("images")
    assert len(images)==len(imageNames)

    for name in renditionNames:
        assert len(convertedData.getRendition(name))>0
    
    unicodeDash = "\xe2\x80\x93"
    expectedTitle = "Module 2 - Word processing with OpenOffice.org (OOo) Writer"
    expectedTitle = expectedTitle.replace("-", unicodeDash)
    title = convertedData.getMeta("title")
    
    assert expectedTitle == title
    l = len(convertedData.getMeta("style.css"))
    assert l == 3564
    
    htmlBody = convertedData.getRendition(".xhtml.body")
    #f = open("temp.html", "wb")
    #f.write(htmlBody)
    #f.close()
    
    #convertedData.saveTo("testConvertedData")

#test_setup()


