
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


pluginName = "ice.render.bookConverter"
pluginDesc = "odt book render"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    #getRelativeLinkMethod = iceContext.getRelativeLink
    #oooConverterMethod = iceContext.getOooConverter().convertDocumentTo
    pluginClass = BookConverter
    pluginFunc = None   #BookConverter(getRelativeLinkMethod, oooConverterMethod)
    pluginInitialized = True
    return pluginClass




class BookConverter(BaseConverter):
    fromToExts = {".book.odt":[".htm", ".pdf"]}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        BaseConverter.__init__(self, iceContext)
        self.convertToOdt = False
        self.BookInfo = iceContext.getPlugin("ice.book.bookInfo").pluginClass(self.iceContext)
        if self.BookInfo is not None:
            iceContext.odtBookRenderMethod = self.__render
        else:
            iceContext.output.write("* Failed to find 'ice.book.bookInfo' plugin!\n")
    
    
    def render(self, item, convertedData, **kwargs):
        #print "**** Book render ****"
        return self.BookInfo.renderMethod(self.iceContext, item, convertedData, **kwargs)
    

    def __render(self, file, convertedData, **kwargs):
        if kwargs.get("pdfOnly", False):
            reindex = kwargs.get("reindex", False)
            return self.renderPdfOnlyMethod(file, convertedData, reindex=reindex)
        return self.renderMethod(file, convertedData)







