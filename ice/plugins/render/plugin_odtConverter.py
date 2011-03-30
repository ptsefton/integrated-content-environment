
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
from baseConverter import BaseConverter


pluginName = "ice.render.odtConverter"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = OdtConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc



class OdtConverter(BaseConverter):
    fromToExts = {".odt":[".htm", ".pdf"]}
    #render(file, rep, convertedData)
    
    # Constructor
    #    __init__(getRelativeLinkMethod, oooConverterMethod)
    # Properties:
    #    
    # Methods:
    #    render(file, absFile, rep=None, oooConverterMethod=None) -> ConvertedData object
    #    renderPdfOnlyMethod(file, absFile, rep=None, oooConverterMethod=None) -> ConvertedData object
    #    
    
    def __init__(self, iceContext):
        BaseConverter.__init__(self, iceContext)
        self.convertToOdt = False
        self.priority = True
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        if kwargs.get("pdfOnly", False):
            reindex = kwargs.get("reindex", False)
            return self.renderPdfOnlyMethod(file, convertedData, reindex=reindex)
        convertedData = self.renderMethod(file, convertedData, **kwargs)
        if file.find("/oscar/")!=-1:
            plugin = self.iceContext.getPlugin("ice.sci")
            if plugin is not None:
                xhtml = convertedData.getRendition(".xhtml.body")
                sciXml = plugin.pluginClass(self.iceContext)
                xhtml, cmls = sciXml.markupWithSci(xhtml)
                convertedData.addRenditionData(".xhtml.body", xhtml)
                for k, v in cmls.iteritems():
                    convertedData.addImageData(k+".cml", v)
                    convertedData.addRenditionData("." + k, v)
        return convertedData









