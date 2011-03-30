#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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
    from pyPdf import PdfFileWriter, PdfFileReader
    from pyPdf.pdf import *
    from pyPdf.generic import *  
    from reportlab.lib.units import cm, mm, inch
    from reportlab.lib import pagesizes
    from reportlab.pdfgen import canvas
    
    PAGESIZE = pagesizes.A4    
except:
    PAGESIZE = None
    pass

pluginName = "ice.pdfUtils"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = PdfUtils
    #Mets.Helper = mets_helper
    pluginInitialized = True
    return pluginFunc

class PdfUtils(object):
    def __init__(self, fileSystem, outputFile=None, pageSize=None):
        self.__fs = fileSystem
        self.__standardPage = pageSize
        if self.__standardPage is None:
            self.__standardPage = PAGESIZE
        self.__outputFile = outputFile
    
    def fixPdf(self, pdfFile):
        try:
            fileOpen = file(pdfFile, "a")
            fileOpen.write("%%EOF")
            fileOpen.close()
            return "Fixed"
        except Exception, e:
            return "Unable to open file: %s with error: %s" % (pdfFile, str(e))
    
    def makeEmptyPagesPdf(self, nPages, pagesize=None):
        if pagesize is None:
            pagesize = self.__standardPage
        buffer = StringIO()
        c = canvas.Canvas(None)
        c.setPageSize(pagesize)
        #c.setPageCompression(0)
        #c.setPageCallBack(pageCallBack)
        #framePageForm(c) # define the frame form
        c.showOutline()
        for page in range(nPages):
            # page
            #framePage(c, "This is a title")
            c.showPage()
        buffer.write(c.getpdfdata())
        buffer.seek(0)
        
        pdfReader = self.pdfReader()
        reader = pdfReader.createPdfReader(buffer=buffer)
        return reader
    
    def imageMagickConverter(self, iceContext, outputDir, inputFile):
        return ImageMagickConverter(iceContext, outputDir, inputFile)

    def pdfReader(self):
        return PdfReader(self.__fs)
    
    def pdfWriter(self, outputFile=None):
        if outputFile is not None:
            self.__outputFile = outputFile
        return PdfWriter(self.__outputFile)

    def splitPdf(self, inputFile, outputFolder=None, removeSpace=False):
        #inputFile is absolutePath
        path, fileName, ext = self.__fs.splitPathFileExt(inputFile)
        if outputFolder is None:
            outputFolder = self.__fs.join(path, fileName)    
        self.__fs.makeDirectory(outputFolder)
        pdfReader = PdfReader(self.__fs)
        inputFileReader = pdfReader.createPdfReader(inputFile)
        if pdfReader.numOfPages:
            count = 1
            for page in range(pdfReader.numOfPages):
                try:
                    if removeSpace:
                        fileName = fileName.replace(" ", "_")
                    splitFileName = self.__fs.join(outputFolder, "%s%s.pdf" % (fileName, count))
                    pdfWriter = PdfWriter(outputFile=splitFileName)
                    pdfWriter.addPage(inputFileReader.getPage(page))
                    pdfWriter.savePdf()
                    count +=1
                except Exception, e:
                    print 'error in splitting file'
        pdfReader.close()

    def convertPdfToJpg(self, inputFile):
        pass
#        cmd = ("latex", "-halt-on-error",
#                        "-output-format=pdf",
#                        inputFile)
#        
#        stdout, _ = self.__execute3(cmd)
    
    def __execute3(self, cmd, *args):
        stdin, stdout, stderr = self.iceContext.system.execute3(cmd, *args)
        out = stdout.read()
        err = stderr.read()
        stdin.close()
        stdout.close()
        stderr.close()
        return out, err

class PdfReader(object):
    #Make sure the pdfFile is absolute path of the file
    def __init__(self, fileSystem):
        self.__fs = fileSystem
        self.errMsg = ""
        self.pdfFileReader = None
        self.__file = None
    
    def createPdfReader(self, pdfFile=None, buffer=None):
        if pdfFile is not None:
            if self.__fs.isFile(pdfFile):
                try:
                    self.__file = file(pdfFile, "rb")
                    self.pdfFileReader = PdfFileReader(self.__file)
                    return self.pdfFileReader
                except Exception, e:
                    self.errMsg = "Unable to open %s, error: %s" % (pdfFile, str(e))
                    return None
            else:
                self.errMsg = "File %s is not exist" % pdfFile
                return None
        elif buffer is not None:
            try:
                self.pdfFileReader = PdfFileReader(buffer)
                return self.pdfFileReader
            except Exception, e:
                self.errMsg = "%s" % str(e)
                return None
        return None
    
    def close(self):
        if self.__file is not None:
            self.__file.close()
    
    @property
    def isEncrypted(self):
        if self.pdfFileReader:
            return self.pdfFileReader.isEncrypted
        return None
    
    @property
    def numOfPages(self):
        if self.pdfFileReader:
            try:
                return self.pdfFileReader.getNumPages()
            except Exception, e:
                return str(e)
        return None
    
    def getPage(self, pageNumber):
        if self.pdfFileReader:
            return self.pdfFileReader.getPage(pageNumber)
        return None
    
    def getpageBox(self, page):
        return page.trimBox
    
    def rectangle2box(self, pdfPage):
        return {
            'width'   : pdfPage.upperRight[0],
            'height'  : pdfPage.upperRight[1],
            'offset_x': pdfPage.lowerLeft[0],
            'offset_y': pdfPage.lowerLeft[1],
            'unit'    : 'pt',
            'units_x' : pdfPage.upperRight[0],
            'units_y' : pdfPage.upperRight[1],
            }
    
    
class PdfWriter(object):
    def __init__(self, outputFile):
        self.outputWriter = PdfFileWriter()
        self.__outputFile = outputFile
        
    def savePdf(self):
        outputStream = file(self.__outputFile, "wb")
        self.outputWriter.write(outputStream)
        outputStream.close()
    
    def addPage(self, page):
        self.outputWriter.addPage(page)


class ImageMagickConverter(object):
    
    def __init__(self, iceContext, outputDir, inputFile):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs
        self.__outputDir = outputDir
        self.__inputFile = inputFile
        self._convertTool = ""
        self._pdftotextTool = ""
        self._exifTool = ""
        self.hasLocalImageMagick = self.__hasLocalImageMagick()
    
    def __extractFullText(self):
        try:
            for file in self.__fs.listFiles(self.__outputDir):
                filePath = self.__fs.join(self.__outputDir, file)
                if self.__fs.isFile(filePath):
                    stdout, stderr = self.__execute3(self._pdftotextTool, "%s" % filePath, "-enc", "UTF-8")
        except:
            print "Failed to extract full text for the pdf"
                
    def __execute3(self, cmd, *args):
        stdout, stderr = self.iceContext.system.executeNew(cmd, *args)
        return stdout, stderr
    
    def __getCommand(self, cmd):
        if self.iceContext.isWindows:
            return r"%s" % cmd
        return cmd
    
    def convertingPdfToImages(self):
        #Split pdfs using PdfUtils.split
        pdfUtils = PdfUtils(self.__fs)
        pdfUtils.splitPdf(self.__inputFile, self.__outputDir, removeSpace=True)
        
        #Extract each pdf full text using pdftotext
        self.__extractFullText()
        
        #Convert to jpg using imagemagick
        #convert -density 100 file.pdf file%02d.jpg
        count =0
        try:
            for file in self.__fs.listFiles(self.__outputDir): 
                _ , fileName, ext = self.__fs.splitPathFileExt(file)
                filePath = self.__fs.join(self.__outputDir, fileName + ext)
                if ext == ".pdf":
                    imageFileName = self.__fs.join(self.__outputDir, "%s.jpg" % (fileName))
                    stdout, stderr = self.__execute3(self._convertTool,"-density", "100", "%s" % filePath, "-scale", "2000x1000", "%s" % imageFileName)
            
                    count += 1
                    #Add fulltext to the images
                    fulltextFile = self.__fs.join(self.__outputDir, fileName + ".txt")
                    if self.__fs.isFile(fulltextFile):
                        data = self.__fs.read(fulltextFile)
                        if data:
                            data = data.replace('\\','\\\\').replace('"', '\\"')
                            try:
                                self.__execute3(self._exifTool, "-UserComment=%s" % data, "%s" % imageFileName)
                            except Exception, e:
                                print "Fail to add pdf page metadata to image file: ", str(e)
                            self.__fs.delete(fulltextFile)
                            if self.__fs.isFile(filePath):
                                self.__fs.delete(filePath)
                            if self.__fs.isFile(imageFileName + "_original"):
                                self.__fs.delete(imageFileName + "_original")
            return count, "ok"
        except Exception, e:
            print "error... in converting: ", str(e)
            return count, "error"
            #print 'error in converting pdf to jpg: ', str(e)
    
    def __hasLocalImageMagick(self):
        cmd = self.iceContext.settings.get("imageMagickPath","convert")
        cmd = self.__getCommand(cmd)
        _, stderr = self.__execute3(cmd)
        self._convertTool = cmd
        
        if self.iceContext.isWindows:
            keyword = "recognized"
        else:
            keyword = "found"
        hasLocal = stderr.find("not " + keyword) == -1
        
        #check exif
        if hasLocal:
            cmd = self.iceContext.settings.get("exiftoolPath","exiftool")
            cmd = self.__getCommand(cmd)
            self._exifTool = cmd
            _, stderr = self.__execute3(cmd)
            if self.iceContext.isWindows:
                keyword = "recognized"
            else:
                keyword = "found"
            hasLocal = stderr.find("not " + keyword) == -1
        
        #check pdftotext
        if hasLocal:
            cmd =self.iceContext.settings.get("pdftotextPath","pdftotext")
            cmd = self.__getCommand(cmd)
            self._pdftotextTool = cmd
            _, stderr = self.__execute3(cmd)
            if self.iceContext.isWindows:
                keyword = "recognized"
            else:
                keyword = "found"
            hasLocal = stderr.find("not " + keyword) == -1
        
        return hasLocal
        
        
