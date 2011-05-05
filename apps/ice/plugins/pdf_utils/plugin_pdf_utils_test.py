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
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon
    sys.path.append("../utils")
    from system import System, system

#import os
#import sys
#sys.path.append("../ice")
#from ice_common import IceCommon
#from pdf_utils import *

fs = IceCommon.FileSystem(".")

from plugin_pdf_utils import *

basePath = "plugins/pdf_utils/"

class MockIceContext(object):
    def __init__(self, IceCommon):
        self.fs = IceCommon.FileSystem(".")
        self.system = system
        self.xmlUtils = IceCommon.xmlUtils
        self.rep = MockRep(self.fs)
        self.isWindows = system.isWindows
        self.isLinux = system.isLinux
        self.isMac = system.isMac

class MockRep(object):
    def __init__(self, fs):
        self.__fs = fs
    
    def getAbsPath(self, path):
        return self.__fs.join(self.__fs.absolutePath(), path)

class PDFUtilsTests(IceCommon.TestCase):    
    def setUp(self):
        self.iceContext = MockIceContext(IceCommon)
        self.pdfUtils = PdfUtils(self.iceContext.fs)
        #self.stdout = sys.stdout
        #sys.stdout = StringIO()
    
    def tearDown(self):
        pass
        #sys.stdout = self.stdout
    
    def testInit(self):
        pdfUtils = PdfUtils(self.iceContext.fs)
        
    def testPdfFileNotExist(self):
        testData = "%stestData/multipages1.pdf" % basePath
        testDataAbsPath = self.iceContext.fs.absPath(testData)
        pdfUtils = PdfUtils(self.iceContext.fs)
        pdfReaderUtil = pdfUtils.pdfReader()
        pdfReader = pdfReaderUtil.createPdfReader(testDataAbsPath)
        
        self.assertEquals(pdfReader, None)
        self.assertEquals(pdfReaderUtil.errMsg, \
                          'File /home/octalina/workspace/trunk/apps/ice/plugins/pdf_utils/testData/multipages1.pdf is not exist')
        
        
    def testOpeningNormalPdf(self):
        testData = "%stestData/multipages.pdf" % basePath
        testDataAbsPath = self.iceContext.fs.absPath(testData)
        pdfUtils = PdfUtils(self.iceContext.fs)
        pdfReaderUtil = pdfUtils.pdfReader()
        pdfReader = pdfReaderUtil.createPdfReader(testDataAbsPath)
        
        self.assertEqual(isinstance(pdfReader, PdfFileReader), True)
        self.assertEquals(pdfReaderUtil.numOfPages, 3)
        self.assertEquals(pdfReaderUtil.isEncrypted, False)
        self.assertEquals(pdfReaderUtil.errMsg, "")
        self.assertEqual(pdfReaderUtil.getpageBox(pdfReader.getPage(0)), RectangleObject([0, 0, 595, 842]))
        
        
    def testOpeningEncryptedPdf(self):
        testData = "%stestData/encrypted.pdf" % basePath
        testDataAbsPath = self.iceContext.fs.absPath(testData)
        pdfUtils = PdfUtils(self.iceContext.fs)
        pdfReaderUtil = pdfUtils.pdfReader()
        pdfReader = pdfReaderUtil.createPdfReader(testDataAbsPath)
        
        self.assertEqual(isinstance(pdfReader, PdfFileReader), True)
        self.assertEqual(pdfReaderUtil.numOfPages, 'file has not been decrypted')
    
    def testConvertingPdfToImages(self):
        testData = "%stestData/multipages.pdf" % basePath
        imageFolder = "%stestData/images" % basePath
        if self.iceContext.fs.isDirectory(imageFolder):
            self.iceContext.fs.delete(imageFolder)
        self.iceContext.fs.makeDirectory(imageFolder)
        
        imageMagickConverter = ImageMagickConverter(self.iceContext, imageFolder, self.iceContext.fs.absPath(testData))
        self.assertEqual(imageMagickConverter.hasLocalImageMagick, True)
        
        imageMagickConverter.convertingPdfToImages()
        self.assertEquals(len(self.iceContext.fs.listFiles(imageFolder)), 3)
    
    def xtestOpeningCorrupedPdf(self):
        testData = "%stestData/corrupted.pdf" % basePath
        testDataAbsPath = self.iceContext.fs.absPath(testData)
        pdfUtils = PdfUtils(self.iceContext.fs)
        pdfReaderUtil = pdfUtils.pdfReader()
        pdfReader = pdfReaderUtil.createPdfReader(testDataAbsPath)
        
        self.assertEqual(pdfReader, None)
        self.assertEqual(pdfReaderUtil.errMsg.find("EOF marker not found")!= -1, True)
        
        self.assertEqual(pdfUtils.fixPdf(testDataAbsPath), "Fixed")
        
        pdfReader = pdfReaderUtil.createPdfReader(testDataAbsPath)
        self.assertEqual(isinstance(pdfReader, PdfFileReader), True)
        self.assertEqual(pdfReaderUtil.numOfPages, '1')
        
        
    def xtestMergePdfWithEncryptedError(self):
        #Note: even corrupted pdfs have been fixed, this error must be reported to EPS in case the pdf is malformed
        #Note: only encrypted error sent to direct and stop merging
        corruptedPdfList = []
        encryptedPdfList = []
        fileList = [singlePagePdf, multiplePagesPdf, encryptedPdf, corruptedPdf]
        
        for file in fileList:
            print 'processing: ', file
            filePath = self.iceContext.fs.absolutePath(file)
            pdfReader = PdfReader(self.iceContext.fs)
            pdfReader.createPdfReader(filePath)
            if pdfReader.pdfFileReader is None:
                corruptedPdfList.append(file)
                self.pdfUtils.fixPdf(filePath)
                pdfReader.createPdfReader(filePath)
            else:
                if pdfReader.isEncrypted:
                    encryptedPdfList.append(file)
        
        self.assertEqual(corruptedPdfList, ['testData/corrupted.pdf'])
        self.assertEqual(encryptedPdfList, ['testData/encrypted.pdf'])
        
    def xtestMergePdfWithoutEncryptedError(self):
        #Note: even corrupted pdfs have been fixed, this error must be reported to EPS in case the pdf is malformed
        #Note: only encrypted error sent to direct and stop merging
        corruptedPdfList = []
        encryptedPdfList = []
        outputFile = "testData/merged.pdf"
        outputAbsPath = self.iceContext.fs.absolutePath(outputFile)
        fileList = [singlePagePdf, multiplePagesPdf, corruptedPdf]
        
        pdfWriter = PdfWriter(outputAbsPath)
        
        for file in fileList:
            print 'processing: ', file
            filePath = self.iceContext.fs.absolutePath(file)
            pdfReader = PdfReader(self.iceContext.fs)
            pdfReader.createPdfReader(filePath)
            if pdfReader.pdfFileReader is None:
                corruptedPdfList.append(file)
                self.pdfUtils.fixPdf(filePath)
                pdfReader.createPdfReader(filePath)
                for pageNum in range(pdfReader.numOfPages):
                    pdfWriter.outputWriter.addPage(pdfReader.getPage(pageNum))
            else:
                if pdfReader.isEncrypted:
                    encryptedPdfList.append(file)
                else:
                    pdfReader.createPdfReader(filePath)
                    for pageNum in range(pdfReader.numOfPages):
                        pdfWriter.outputWriter.addPage(pdfReader.getPage(pageNum))
                    
        
        self.assertEqual(corruptedPdfList, ['testData/corrupted.pdf'])
        self.assertEqual(encryptedPdfList, [])
        
        pdfWriter.savePdf()
        self.assertEqual(self.iceContext.fs.isFile(outputAbsPath), True)
        pdfReader = PdfReader(self.iceContext.fs)
        pdfReader.createPdfReader(outputAbsPath)
        self.assertEqual(pdfReader.numOfPages, 5)
    
#    def testNumPages(self):
#        pdfUtil = PDFUtils(fs, multiplePagesPdf)
#        pdfReader = pdfUtil.inputReader
#        self.assertEquals(pdfReader.numberOfPages, 3)
#        
#    def testPageDetail(self):
#        pdfUtil = PDFUtils(fs, singlePagePdf)
#        pdfReader = pdfUtil.inputReader
#        expectedResult = {'units_y': 842, 'units_x': 595, 'height': 842, 'width': 595, 'offset_x': 0, 
#                          'offset_y': 0, 'unit': 'pt'}
#        
#        #get page property for page 1
#        page = pdfReader.getPageBox(0)
#        result = pdfReader.rectangle2box(page)
#        self.assertEquals(result, expectedResult)
#    
#    def testMakeEmptyPage(self):
#        pdfUtil = PDFUtils(fs)
#        newPageReader = pdfUtil.makeEmptyPagesPdf(1)
#        
#        result = newPageReader.rectangle2box(newPageReader.getPage(0).trimBox)
#        expected = {'units_y': 841.8898, 'units_x': 595.2756, 'height': 841.8898, 'width': 595.2756, 'offset_x': 0, 'offset_y': 0, 'unit': 'pt'}
#        
#        for key in result:
#            resultVal = str(result[key])
#            expectVal = str(expected[key])
#            self.assertEquals(resultVal, expectVal)
#            
#        
#    
#    def testResize(self):
#        #only resize first page 
#        pdfFile = "testData/differentSize.pdf"
#        outputFile = "testData/outputFile.pdf"
#        pdfUtil = PDFUtils(fs, pdfFile)
#        pdfReader = pdfUtil.inputReader
#        outputWriter = pdfUtil.createPdfWriter()
#        
#        emptyReader = pdfUtil.makeEmptyPagesPdf(1)
#        emptyPage = emptyReader.getPage(0)
#        emptyRectangle = emptyReader.rectangle2box(emptyPage.trimBox)
#        emptyWidth = emptyRectangle['width']
#        emptyHeight = emptyRectangle['height']
#        
#        oriPage = pdfReader.getPage(1)
#        oriRectangle = pdfReader.rectangle2box(oriPage.trimBox)
#        oriWidth = oriRectangle['width']
#        oriHeight = oriRectangle['height']
#        outputWriter.addPage(emptyPage)
#        pdfUtil.scalePage(emptyPage, oriPage,
#              (0, emptyHeight/oriHeight), # offset x,y
#              (emptyWidth/oriWidth, emptyHeight/oriHeight)   # scaling x,y
#             )
#        
#        pdfUtil.savePdf(outputWriter, outputFile)
#        
#        outputUtil = PDFUtils(fs, outputFile)
#        outputReader = outputUtil.inputReader
#        outputRectangle = outputReader.rectangle2box(outputReader.getPage(0).trimBox)
#        #makesure the size is the same as emptyPage
#        self.assertEquals(emptyRectangle, outputRectangle)
#        
#        
#    
#    
#    def xtestExtractingPdfPages(self):
#        # Test on singlePage
#        pdfUtils = PDFUtils(fs)        
#        extractedFile = pdfUtils.extractPdfPages(singlePagePdf)
#        self.assertTrue(len(extractedFile), 1)
#        for file in extractedFile:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#        
#        
#        # Test on multiplePages
#        extractedFile = pdfUtils.extractPdfPages(multiplePagesPdf)
#        self.assertTrue(len(extractedFile), 3)
#        for file in extractedFile:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))                
#        
#    
#    def xtestConvertPdfToPs(self):
#        pdfUtils = PDFUtils(fs)        
#        extractedFile = pdfUtils.extractPdfPages(singlePagePdf)
#        psFiles = pdfUtils.convertPagesToPS(extractedFile)
#        self.assertTrue(len(extractedFile), 1)
#        for file in psFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#        
#        epsFiles = pdfUtils.convertPsToEps(psFiles)
#        self.assertTrue(len(extractedFile), 1)
#        for file in epsFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#            
#        for file in extractedFile:
#            fs.delete(fs.absolutePath(file))
##        for file in psFiles:
##            fs.delete(fs.absolutePath(file))
#            
#        
#        extractedFile = pdfUtils.extractPdfPages(multiplePagesPdf)
#        psFiles = pdfUtils.convertPagesToPS(extractedFile)
#        self.assertTrue(len(extractedFile), 3)
#        for file in psFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#
#        epsFiles = pdfUtils.convertPsToEps(psFiles)
#        self.assertTrue(len(extractedFile), 3)
#        for file in epsFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#
#        for file in extractedFile:
#            fs.delete(fs.absolutePath(file))            
##        for file in psFiles:
##            fs.delete(fs.absolutePath(file))
#            
#    def xtestConvertUseImageMagick(self):
#        pdfUtils = PDFUtils(fs)        
#        extractedFile = pdfUtils.extractPdfPages(singlePagePdf)
#        epsFiles = pdfUtils.convertUsesImageMagick(extractedFile)
#        self.assertTrue(len(epsFiles), 1)
#        for file in epsFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#
#        extractedFile = pdfUtils.extractPdfPages(imagePdf)
#        epsFiles = pdfUtils.convertUsesImageMagick(extractedFile)
#        self.assertTrue(len(epsFiles), 1)
#        for file in epsFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
#   
#        extractedFile = pdfUtils.extractPdfPages(multiplePagesPdf)
#        epsFiles = pdfUtils.convertUsesImageMagick(extractedFile)
#        self.assertTrue(len(epsFiles), 3)
#        for file in epsFiles:
#            self.assertTrue(fs.isFile(fs.absolutePath(file)))
   
   
if __name__ == "__main__":
    IceCommon.runUnitTests(locals())




