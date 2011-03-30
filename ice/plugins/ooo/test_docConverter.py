
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

from docConverter import *

sourceFilename = "/packages/ice-guide/resources/test.htm"
testDocFile = "testData/word/word.doc"
testOdtFile = "testData/word/temp.odt"
testPdfFile = "testData/word/temp.pdf"
testHtmlFile = "testData/word/temp.html"

import relative_linker
getRelativeLinkMethod = relative_linker.relativeLinker("http://localhost:8000/").getRelativeLink


class mockOooConverter:
    def __init__(self):
        pass
        
    def convertDocumentTo(self, sourceFilename, destFilename):
        #print "convert DocTo(%s, %s)" % (sourceFilename, destFilename)
        if False:    # Use the oooConverter or use cached results of oooConverter
            import ooo_converter
            self.oooConverter = ooo_converter.oooConverter()
            self.oooConverter.convertDocumentTo(sourceFilename, destFilename)
            # Cache the result
            filename = os.path.split(destFilename)[1]
            filename = os.path.abspath("testData/word/" + filename)
            self.oooConverter.convertDocumentTo(sourceFilename, filename)
        else:
            #if sourceFilename!=testOdtFile:
            #    raise Exception("Unexcepted filename!")
            toFilename = os.path.split(destFilename)[1]
            if toFilename=="temp.odt":
                self.__copy(testOdtFile, destFilename)
            elif toFilename=="temp.pdf":
                self.__copy(testPdfFile, destFilename)
            elif toFilename=="temp.html":
                self.__copy(testHtmlFile, destFilename)
                # also copy the associated images
                toPath = os.path.split(destFilename)[0]
                files = [file for file in os.listdir("testData/word") if file.startswith("temp_html_")]
                for file in files:
                    self.__copy("testData/word/" + file, toPath + "/" + file)
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
    print "copyToMethod(%s, %s)" % (fromFilename, toFilename)
    if fromFilename!=sourceFilename:
        raise Exception("Unexcepted filename!")
    f = open(testDocFile, "rb")
    data = f.read()
    f.close()
    f = open(toFilename, "wb")
    f.write(data)
    f.close()




def xtest_setup():
    if False:
        global converter
        converter = docConverter(getRelativeLinkMethod, oooConverterMethod=mockOooConverter().convertDocumentTo)
        converter.setup(copyToMethod, sourceFilename)
        converter.convertToHtml()
        converter.convertToPdf()
        converter.close()
        convertedData = converter.convertedData
    else:
        convertedData = docConverter(getRelativeLinkMethod).renderMethod(sourceFilename, os.path.abspath(testDocFile), \
                    oooConverterMethod=mockOooConverter().convertDocumentTo)
    

    #print str(convertedData)
    metaNames = convertedData.metaNames
    imageNames = convertedData.imageNames
    renditionNames = convertedData.renditionNames
    metaNames.sort()
    imageNames.sort()
    renditionNames.sort()
    
    #print str(convertedData)
    
    expectedMetaNames = ['images', 'links', 'style.css', 'title']
    expectedImageNames = []
    expectedRenditionNames = ['.ALL.txt', '.pdf', '.xhtml.body']
    assert metaNames == expectedMetaNames
    assert imageNames == expectedImageNames
    assert renditionNames == expectedRenditionNames
    
    for name in renditionNames:
        assert len(convertedData.getRendition(name))>0
    
    expectedTitle = "Word Template Styles Test"
    title = convertedData.getMeta("title")
    assert expectedTitle == title
    
    l = len(convertedData.getMeta("style.css"))
    assert l == 4947
    l = len(convertedData.getRendition('.xhtml.body'))
    assert l > 31000
    
    #convertedData.saveTo("testConvertedData")

#test_setup()


