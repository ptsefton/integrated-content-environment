
#    Copyright (C) 2006/2008  Distance and e-Learning Centre, 
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
import re
from odsbaseConverter import odsBaseConverter

pluginName = "ice.render.odsConverter"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = OdsConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc
    




class OdsConverter(odsBaseConverter):
    fromToExts = {".ods":[".htm", ".pdf"]}
    
    # Constructor
    #    __init__(getRelativeLinkMethod, oooConverterMethod)
    # Properties:
    #    
    # Methods:
    #    render(file, absFile, rep=None, oooConverterMethod=None) -> ConvertedData object
    #   
    
    def __init__(self, iceContext, oooConverterMethod=None):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs
        self._fs = self.__fs
        odsBaseConverter.__init__(self, iceContext)
        if oooConverterMethod is None:
            oooConverterMethod = iceContext.getOooConverter().convertDocumentTo
        self._oooConverterMethod = oooConverterMethod
  

    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        convertedData = self.renderMethod(file, convertedData, **kwargs)
        self.convertedData = convertedData
        return convertedData



