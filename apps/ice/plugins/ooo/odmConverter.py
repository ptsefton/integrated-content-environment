
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

from baseConverter import *


class OdmConverter(BaseConverter):
    
    fromToExts = {".odt":[".htm", ".pdf"]}
    #render(file, rep, convertedData)
    
    def __init__(self, iceContext, getRelativeLinkMethod, oooConverterMethod, output=None):
        self.iceContext = iceContext
        BaseConverter.__init__(self, getRelativeLinkMethod, oooConverterMethod, \
                                output=output, IceContext=self.iceContext)
        self.convertToOdt = False
        self.__oooFileName = None    # odm
        self.__fs = self._fs
    

    def render(self, item, rep, convertedData, **kwargs):
        file = item.relPath
        return self.renderMethod(file, rep, convertedData)
    
    
    # override
    def renderMethod(self, file, rep, convertedData):
        self.convertedData = convertedData
        absFile = rep.getAbsPath(file)
        converter = self._oooConverterMethod
        
        self.__oooFileName = absFile
        if rep==None:
            def copy(src, dest):
                src = absFile
                self.__fs.copy(src, dest)
                pass
            self._setup(copy, file)
        else:
            item = rep.getItem(file)
            self._setup(item.export, file)
        
        # PDF
        result = self._convertToPdf()
        if result!="ok":
            self.convertedData.addErrorMessage(result)
        
        self._close()
        return self.convertedData
    
    
    # override
    def _setup(self, copyToMethod, sourceFileName, x=None, y=None):
        self._sourceFileName = sourceFileName

        self._tmpOooFileName = self.convertedData.abspath("temp.odm")
        self._tmpPdfFileName = self.convertedData.abspath("temp.pdf")
        
        content = self.__fs.readFromZipFile(self.__oooFileName, "content.xml")
        meta = self.__fs.readFromZipFile(self.__oooFileName, "meta.xml")
        try:
            self._contentXml = self.IceContext.Xml(content, oOfficeNSList)
        except Exception, e:
            msg = "ERROR: Failed to transformToDom! - " + str(e)
            msg += " Skipping sourceFile " + sourceFileName
            return False
        title = self._getTitle(meta)
        self.convertedData.addMeta("title", title)
        return True
    
    # override
    def _convertToPdf(self):
        #self.__removeLocalhostLinks(self.__tmpOooFileName)
        #result, msg = self.__convertFile(self.__tmpOooFileName, self.__tmpPdfFileName)
        result, msg = self._convertFile(self.__oooFileName, self._tmpPdfFileName)
        if result==False:
            return msg
        self.convertedData.addRenditionFile(".pdf", self._tmpPdfFileName)
        return "ok"

    
    



