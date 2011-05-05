
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

from odmConverter import *


sourceFilename = "/packages/ice-guide/ice_master.pdf"
testOdmFile = "testData/master/test.odm"
testPdfFile = "testData/master/temp.pdf"
testHtmlFile = "testData/master/temp.html"

import relative_linker
getRelativeLinkMethod = relative_linker.relativeLinker("http://localhost:8000/").getRelativeLink


class mockOooConverter:
    def __init__(self):
        pass
        
    def convertDocumentTo(self, sourceFilename, destFilename):
        #print "convert DocTo(%s, %s)" % (sourceFilename, destFilename)
        if False:
            import ooo_converter
            self.oooConverter = ooo_converter.oooConverter()
            self.oooConverter.convertDocumentTo(sourceFilename, destFilename)
            filename = os.path.split(destFilename)[1]
            filename = os.path.abspath("testData/master" + filename)
            self.oooConverter.convertDocumentTo(sourceFilename, filename)
        else:
            #if sourceFilename!=testOdmFile:
            #    raise Exception("Unexcepted filename!")
            toFilename = os.path.split(destFilename)[1]
            if toFilename=="temp.pdf":
                self.__copy(testPdfFile, destFilename)
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
        
        f = open(testOdmFile, "rb")
        data = f.read()
        f.close()
        
        f = open(toFilename, "wb")
        f.write(data)
        f.close()



def xtest_setup():
    if False:
        global converter
        converter = odmConverter(getRelativeLinkMethod, oooConverterMethod=mockOooConverter().convertDocumentTo)
        converter.setup(copyToMethod, sourceFilename)
        #converter.convertToHtml()    # No html version for master documents
        converter.convertToPdf()
        converter.close()
        convertedData = converter.convertedData
    else:
        convertedData = odmConverter(getRelativeLinkMethod).renderMethod(sourceFilename, os.path.abspath(testOdmFile), \
                    oooConverterMethod=mockOooConverter().convertDocumentTo)

    #print str(convertedData)
    metaNames = convertedData.metaNames
    imageNames = convertedData.imageNames
    renditionNames = convertedData.renditionNames
    metaNames.sort()
    imageNames.sort()
    renditionNames.sort()
    assert imageNames == []
    assert renditionNames == [".pdf"]
    assert metaNames == ["title"]
    
    assert convertedData.getMeta("title") == "Integrated Content Environment (ICE) user guide"
    #print "Title=" + convertedData.getMeta("title")
    
    pdf = convertedData.getRendition(".pdf")

    l = len(pdf)
    #assert l==474934    
    assert l>300000
#    
#    #convertedData.saveTo("testConvertedData")

#test_setup()

